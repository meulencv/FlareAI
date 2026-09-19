import time
import unittest
import math
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

from autodispatch import BASELINE, LOCATION_REDIRECT_KM, WAVE_COOLDOWN, pick
from director import Director


def station(identifier, lon, kind='fire_engine', count=2):
    return [{'id': f'{identifier}:{kind}:{n + 1}', 'station_id': identifier, 'kind': kind, 'name': f'Sede {identifier}',
             'lat': 41, 'lon': lon} for n in range(count)]


class Atlas:
    """Atlas ficticio: cuatro parques con dos camiones, dos bases sanitarias y una comisaría."""
    def __init__(self):
        self.rows = [*station('p1', 1.01), *station('p2', 1.02), *station('p3', 1.03), *station('p4', 1.04),
                     *station('h1', 1.015, 'ambulance'), *station('h2', 1.025, 'ambulance'), *station('c1', 1.012, 'police', 1)]

    def nearby(self, lat, lon):
        return deepcopy(self.rows)


class AutoDispatchTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'incidents': [{'id': 'fire', 'name': 'Aviso', 'lat': 41, 'lon': 1, 'demo_report': {'summary': {}, 'run_id': 'call-1'}, 'weather': {}}], 'demo': {'field_reports': {}}}
        self.store = SimpleNamespace(db=Mock(), demo=SimpleNamespace(session_id='test'), payload=lambda: deepcopy(self.payload))
        self.router = Mock()
        self.router.route.side_effect = lambda start, end, **kwargs: {'coordinates': [list(start), list(end)], 'cumulative_km': [0, 1], 'duration_seconds': 90, 'distance_km': 1}
        self.director = Director(self.store, Mock(ready=False), self.router, Atlas())
        self.auto = self.director.auto

    def assignments(self, kind=None):
        return [a for a in self.director.state['assignments'].values() if kind is None or a['resource']['kind'] == kind]

    def test_pick_spreads_between_stations_before_repeating_one(self):
        free = [*station('p1', 1.01), *station('p2', 1.02), *station('p3', 1.03)]
        chosen = pick(free, 3, set())
        self.assertEqual([r['station_id'] for r in chosen], ['p1', 'p2', 'p3'])
        chosen = pick(free, 3, {'p1'})
        self.assertEqual([r['station_id'] for r in chosen], ['p2', 'p3', 'p1'])
        self.assertEqual(len(pick(free, 10, set())), 6)

    def test_baseline_leaves_immediately_without_planner_from_distinct_stations(self):
        self.director.step()
        engines = self.assignments('fire_engine')
        self.assertEqual(len(engines), BASELINE['fire_engine'])
        self.assertEqual(len({a['resource']['station_id'] for a in engines}), 3)
        self.assertEqual(len(self.assignments('ambulance')), 1)
        self.assertEqual(len(self.assignments('police')), 1)
        self.assertTrue(all(a['status'] == 'enroute' for a in self.assignments()))
        kinds = [e['kind'] for e in self.director.state['events']]
        self.assertIn('decision', kinds)
        self.assertEqual(kinds.count('dispatch'), 5)
        self.assertEqual(self.director.public_state()['auto']['fire']['phase'], 'active')
        # Sin cambios no se repite la oleada ni se duplican unidades.
        self.director.step()
        self.assertEqual(len(self.assignments()), 5)

    def test_units_removed_by_another_decision_are_replaced_while_the_fire_is_active(self):
        self.director.step()
        rid = next(iter(self.director.state['assignments']))
        del self.director.state['assignments'][rid]
        self.auto.records['fire']['wave_at'] = time.time() - WAVE_COOLDOWN - 1
        self.director.step()
        engines = self.assignments('fire_engine')
        self.assertEqual(len(engines), BASELINE['fire_engine'])
        self.assertEqual(len({a['resource']['station_id'] for a in engines}), 3)
        self.assertTrue(any('Refuerzo automático' in e['message'] for e in self.director.state['events'] if e['kind'] == 'decision'))

    def test_worsening_report_and_explicit_request_send_more_trucks(self):
        self.director.step()
        self.payload['demo']['field_reports']['fire'] = {'incident_id': 'fire', 'revision': 2, 'fields': {'incendio': 'confirmado', 'evolucion': 'empeora', 'refuerzos': 'solicitado', 'bomberos': '2'},
                                                         'field_versions': {'incendio': 1, 'evolucion': 2, 'refuerzos': 2, 'bomberos': 2}, 'field_sources': {}, 'run_id': 'call'}
        self.payload['incidents'][0]['responder_report'] = self.payload['demo']['field_reports']['fire']
        self.auto.records['fire']['wave_at'] = 0
        self.director.step()
        engines = self.assignments('fire_engine')
        self.assertGreaterEqual(len(engines), BASELINE['fire_engine'] + 2)
        self.assertEqual(len(self.assignments('ambulance')), 2)
        self.assertEqual(self.auto.records['fire']['requests']['fire_engine']['fulfilled'], 2)
        summaries = [e['message'] for e in self.director.state['events'] if e['kind'] == 'decision']
        self.assertTrue(any('Bomberos pide 2 camiones' in s for s in summaries))
        # La misma petición no se vuelve a ejecutar.
        count = len(self.assignments())
        self.auto.records['fire']['wave_at'] = 0
        self.director.step()
        self.assertEqual(len(self.assignments()), count)

    def test_sustained_work_contains_then_everyone_returns_and_frees(self):
        clock = [time.time()]
        with patch('autodispatch.time.time', side_effect=lambda: clock[0]), patch('director.time.time', side_effect=lambda: clock[0]):
            self.director.step()
            for assignment in self.assignments():
                assignment['started_at'] = clock[0] - 500
            clock[0] += 1
            self.director.step()
            self.assertTrue(all(a['status'] == 'onscene' for a in self.assignments()))
            record = self.auto.records['fire']
            self.assertEqual(record['phase'], 'active')
            for _ in range(4):  # tres camiones: 90 medios·s se alcanzan en 30 s, no en 45
                clock[0] += 5
                self.director.step()
            self.assertEqual(record['phase'], 'active')
            self.assertGreater(record['extinguished_pct'], 50)
            for _ in range(2):
                clock[0] += 5
                self.director.step()
            self.assertEqual(record['phase'], 'contained')
            clock[0] += 26
            self.director.step()
            self.assertEqual(record['phase'], 'watching')
            clock[0] += 46
            self.director.step()
            self.assertEqual(record['phase'], 'releasing')
            self.assertTrue(all(a['status'] == 'returning' for a in self.assignments()))
            self.assertEqual(len(self.assignments()), 5)
            for assignment in self.assignments():
                assignment['started_at'] = clock[0] - 500
            clock[0] += 1
            self.director.step()
            self.assertEqual(self.assignments(), [])
            clock[0] += 1
            self.director.step()
            self.assertEqual(record['phase'], 'closed')
            kinds = [e['kind'] for e in self.director.state['events']]
            for kind in ('contained', 'watch', 'release', 'return', 'available', 'closed'):
                self.assertIn(kind, kinds)
            # Cerrado: no vuelve a salir nadie hasta un parte de reactivación.
            clock[0] += WAVE_COOLDOWN + 1
            self.director.step()
            self.assertEqual(self.assignments(), [])
            self.assertEqual(self.director.public_state()['stations'][0]['available'], self.director.public_state()['stations'][0]['total'])

    def test_withdrawn_call_sends_units_home(self):
        self.director.step()
        self.payload['incidents'] = []
        self.director.step()
        self.assertTrue(all(a['status'] == 'returning' for a in self.assignments()))
        self.assertEqual(self.auto.records['fire']['phase'], 'releasing')

    def test_near_location_correction_redirects_existing_units_from_current_position(self):
        self.director.step()
        before = set(self.director.state['assignments'])
        for assignment in self.assignments():
            assignment['started_at'] = time.time() - 10
        self.payload['incidents'] = [{'id': 'demo:call-1', 'name': 'Sagrada Familia', 'lat': 41, 'lon': 1.05,
                                      'demo_report': {'summary': {}, 'run_id': 'call-1'}, 'weather': {}}]
        self.director.step()
        self.assertEqual(set(self.director.state['assignments']), before)
        self.assertTrue(all(a['incident_id'] == 'demo:call-1' for a in self.assignments()))
        self.assertTrue(all(a['target'] == [1.05, 41] for a in self.assignments()))
        self.assertTrue(all(a['report_run_id'] == 'call-1' for a in self.assignments()))
        self.assertEqual(sum(e['kind'] == 'location_correction' for e in self.director.state['events']), len(before))

    def test_far_location_correction_returns_old_units_and_dispatches_new_ones(self):
        self.director.step()
        old = set(self.director.state['assignments'])
        far_lon = 1 + (LOCATION_REDIRECT_KM + 5) / (111.32 * math.cos(math.radians(41)))
        self.payload['incidents'] = [{'id': 'demo:call-1', 'name': 'Punto corregido', 'lat': 41, 'lon': far_lon,
                                      'demo_report': {'summary': {}, 'run_id': 'call-1'}, 'weather': {}}]
        self.director.step()
        old_assignments = [self.director.state['assignments'][rid] for rid in old]
        self.assertTrue(all(a['status'] == 'returning' for a in old_assignments))
        replacements = [a for rid, a in self.director.state['assignments'].items() if rid not in old]
        self.assertTrue(replacements)
        self.assertTrue(all(a['incident_id'] == 'demo:call-1' for a in replacements))
        self.assertTrue(any(e['kind'] == 'location_correction' and 'nuevo' in e['message'] for e in self.director.state['events']))

    def test_scene_incident_follows_scene_phase_and_never_dispatches_in_release(self):
        self.payload['incidents'][0]['scenario'] = {'phase': 'releasing', 'radius_km': .3}
        self.director.step()
        self.assertEqual(self.assignments(), [])
        self.payload['incidents'][0]['scenario'] = {'phase': 'active', 'radius_km': .5}
        self.auto.records['fire']['wave_at'] = 0
        self.director.step()
        self.assertEqual(len(self.assignments('fire_engine')), BASELINE['fire_engine'] + 1)
        self.assertNotIn('contained', [e['kind'] for e in self.director.state['events']])  # la evolución la gobierna el escenario

    def test_disabled_layer_changes_nothing(self):
        self.auto.enabled = False
        self.director.step()
        self.assertEqual(self.assignments(), [])
        self.assertEqual(self.auto.records, {})

    def test_route_failure_still_mobilises_with_fallback(self):
        self.router.route.side_effect = ValueError('Sin red')
        self.director.step()
        self.assertEqual(len(self.assignments()), 5)
        self.assertTrue(all(a['route']['mode'] == 'ground_fallback' for a in self.assignments()))

    def test_reset_demo_clears_records(self):
        self.director.step()
        self.director.reset_demo()
        self.assertEqual(self.auto.records, {})
        self.assertEqual(self.director.state['assignments'], {})


class HeldTests(unittest.TestCase):
    def test_hold_releases_when_phone_is_disabled_or_after_limit(self):
        from operations import HOLD_LIMIT, Operations
        director = SimpleNamespace(state={'assignments': {}}, scene=None, db=Mock(), store=SimpleNamespace(allow_outbound=False))
        with patch('operations.OutboundCalls', create=True) as calls, patch.dict('sys.modules', {'outbound': SimpleNamespace(OutboundCalls=calls)}):
            operations = Operations(director)
        operations.outbound = SimpleNamespace(jobs={}, enabled=False)
        operations.records['fire'] = {'started_at': time.time(), 'requests': {}}
        self.assertTrue(operations.held('fire'))
        operations.outbound.jobs['fire'] = {'status': 'disabled'}
        self.assertFalse(operations.held('fire'))
        operations.outbound.jobs['fire'] = {'status': 'dialing'}
        self.assertTrue(operations.held('fire'))
        operations.records['fire']['started_at'] = time.time() - HOLD_LIMIT - 1
        self.assertFalse(operations.held('fire'))


if __name__ == '__main__':
    unittest.main()
