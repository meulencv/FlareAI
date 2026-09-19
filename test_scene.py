from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from scene import Scene, sensor_candidate, satellite_contrast


def incident(identifier='sensor'):
    return {'id': identifier, 'lat': 41.43, 'lon': 2.12, 'name': 'Collserola', 'observations': 2,
            'frp_peak_mw': 30, 'last_seen': '2026-09-19T10:00:00+00:00',
            'detections': [{'lat': 41.43, 'lon': 2.12, 'confidence': 'high', 'at': '2026-09-19T10:00:00+00:00'}],
            'weather': {'wind_from_degrees': 90}, 'footprint': {'type': 'Polygon', 'coordinates': []}}


class SceneTests(TestCase):
    def setUp(self):
        self.director = SimpleNamespace(state={'resources': {}, 'assignments': {}, 'sequence': 0}, event=Mock(),
                                        store=SimpleNamespace(context=lambda _: {'potential': {'samples': []}}))
        self.scene = Scene(self.director)

    def test_sensor_threshold_region_and_age(self):
        item = incident()
        now = 1789812000
        self.assertTrue(sensor_candidate(item, now))
        self.assertFalse(sensor_candidate({**item, 'lon': -3}, now))
        self.assertFalse(sensor_candidate({**item, 'frp_peak_mw': 2}, now))
        self.assertFalse(sensor_candidate(item, now + 90000))

    def test_sensor_debounce_and_no_mutation_or_fake_confirmation(self):
        item = incident()
        original = deepcopy(item)
        payload = {'incidents': [item]}
        self.scene.observe(payload, 1789812000)
        self.assertFalse(self.scene.data['incidents'])
        self.scene.observe(payload, 1789812009)
        overlay = self.scene.overlay(payload)['incidents'][0]
        self.assertEqual(overlay['source_kind'], 'sensor')
        self.assertNotIn('demo_report', overlay)
        self.assertNotIn('confirmation', overlay)
        self.assertEqual(item, original)
        self.assertEqual(len(self.scene.data['incidents']), 1)
        self.scene.observe(payload, 1789812012)
        self.assertEqual(len(self.scene.data['incidents']), 1)

    def test_contrast_uses_detection_not_centroid_and_labels_simulated(self):
        target = {'lat': 41.43, 'lon': 2.12}
        thermal = {**incident(), 'lat': 40, 'lon': -3}
        self.assertEqual(satellite_contrast(target, [thermal])['mode'], 'observed')
        missing = satellite_contrast(target, [])
        self.assertEqual(missing['mode'], 'simulated')
        self.assertIn('simulado', missing['label'])

    def contain_seconds(self, engines):
        self.setUp()
        self.scene.observe({'incidents': [incident()]}, 1789812000)
        self.scene.observe({'incidents': [incident()]}, 1789812009)
        record = self.scene.data['incidents']['sensor']
        for second in range(10, 100):
            self.scene.evolve(1789812000 + second)
        self.assertEqual(record['phase'], 'active')
        grown = record['radius_km']
        self.assertGreater(grown, .3)
        self.director.state['assignments'] = {
            str(n): {'incident_id': 'sensor', 'status': 'onscene', 'resource': {'kind': 'fire_engine'}} for n in range(engines)}
        for second in range(100, 700):
            self.scene.evolve(1789812000 + second)
            if record['phase'] != 'active':
                return second - 100, record, grown
        return None, record, grown

    def test_arrival_does_not_close_and_more_resources_extinguish_sooner(self):
        one, record, grown = self.contain_seconds(1)
        self.assertIsNone(one, 'Un solo camión apenas frena el fuego')
        self.assertLess(record['radius_km'], grown + .2)  # 600 s más: sin medios habría crecido hasta el tope de 1,2 km
        three, record, _ = self.contain_seconds(3)
        self.assertEqual(record['phase'], 'releasing')
        self.assertGreater(three, 30, 'Llegar no basta: la extinción es progresiva')
        self.assertEqual(record['extinguished_pct'], 100)
        five, _, _ = self.contain_seconds(5)
        self.assertLess(five, three)
        kinds = [c.args[0] for c in self.director.event.call_args_list]
        self.assertIn('suppression', kinds)
        record = self.scene.data['incidents']['sensor']
        at = 1789812000 + 100 + five
        self.assertEqual(record['phase'], 'releasing')
        self.director.state['assignments'] = {}
        self.scene.evolve(at + 1)
        self.assertEqual(record['phase'], 'closed')

    def test_extinction_returns_units_immediately_without_interrupting_transport(self):
        import time
        from unittest.mock import patch
        self.scene.observe({'incidents': [{**incident(), 'scene_report': {'source': 'fixture'}}]}, 1000)
        self.scene.data['automatic'] = False
        record = self.scene.data['incidents']['sensor']
        record.update(radius_km=.061, medical=True)
        self.director.state['assignments'] = {
            key: {'incident_id': 'sensor', 'status': status, 'resource': {'kind': kind, 'name': key, 'lat': 41.4, 'lon': 2.1},
                  'route': {'coordinates': [[2.1, 41.4], [2.12, 41.43]], 'cumulative_km': [0, 4], 'distance_km': 4},
                  'target': [2.12, 41.43], 'started_at': time.time() - 100, 'arrived_at': time.time() - 30, 'travel_seconds': 30}
            for key, kind, status in [('truck1', 'fire_engine', 'onscene'), ('truck2', 'fire_engine', 'onscene'),
                                      ('police', 'police', 'enroute'), ('ambulance', 'ambulance', 'onscene'),
                                      ('patient', 'ambulance', 'transporting'), ('air', 'helicopter', 'onscene')]}
        self.scene.evolve(1001)
        self.assertEqual(record['phase'], 'releasing')
        self.assertEqual(record['extinguished_pct'], 100)
        with patch.object(self.scene, 'route', return_value={'coordinates': [[2.12, 41.43], [2.1, 41.4]], 'duration_seconds': 900}):
            self.scene.maintenance()
        for key, assignment in self.director.state['assignments'].items():
            self.assertEqual(assignment['status'], 'transporting' if key == 'patient' else 'returning')
            if key != 'patient':
                self.assertLessEqual(assignment['travel_seconds'], 15)
        self.assertNotEqual(record['phase'], 'closed')

    def test_phone_and_requested_firefighters_delay_shrinking_until_arrival(self):
        from operations import Operations, HOLD_LIMIT
        from unittest.mock import patch
        now = 1789812000
        item = {**incident(), 'demo_report': {'summary': {}}}
        self.scene.observe({'incidents': [item]}, now)
        operations = Operations.__new__(Operations)
        operations.director = self.director
        operations.outbound = SimpleNamespace(jobs={'sensor': {'status': 'dialing'}})
        self.director.operations = operations
        request = {'kind': 'fire_engine', 'quantity': 2, 'fulfilled': 2, 'resource_ids': ['r1', 'r2'], 'status': 'fulfilled'}
        self.director.state['operations'] = {'sensor': {'started_at': now, 'requests': {'reinforcement': request}}}
        self.director.state['assignments'] = {
            key: {'incident_id': 'sensor', 'status': 'enroute' if key.startswith('r') else 'onscene',
                  'resource': {'kind': 'fire_engine'}} for key in ['base1', 'base2', 'base3', 'r1', 'r2']}
        record = self.scene.data['incidents']['sensor']
        with patch('operations.time.time', return_value=now + 10):
            self.scene.evolve(now + 10)
        self.assertGreater(record['radius_km'], .18)
        self.assertEqual(record['suppression_power'], 0)
        operations.outbound.jobs['sensor']['status'] = 'completed'
        self.director.state['assignments']['r1']['status'] = 'onscene'
        before = record['radius_km']
        with patch('operations.time.time', return_value=now + HOLD_LIMIT + 10):
            self.scene.evolve(now + HOLD_LIMIT + 10)
        self.assertGreaterEqual(record['radius_km'], before, 'No consume extinción mientras falta un refuerzo, incluso tras 300 s')
        self.director.state['assignments']['r2']['status'] = 'onscene'
        before = record['radius_km']
        for second in range(1, 61):
            with patch('operations.time.time', return_value=now + HOLD_LIMIT + 10 + second):
                self.scene.evolve(now + HOLD_LIMIT + 10 + second)
            if second == 1:
                self.assertLess(record['radius_km'], before)
                self.assertEqual(record['phase'], 'active', 'La llegada inicia trabajo progresivo, no apaga de golpe')
                self.assertGreater(record['extinguished_pct'], 0)
            if record['phase'] == 'releasing':
                break
        self.assertEqual(record['phase'], 'releasing')

    def test_happyrobot_template_normalization_does_not_weaken_prompt_check(self):
        from director_workflow import canonical_prompt
        self.assertEqual(canonical_prompt('{{ index . "abc-123.data.context_json" }}'), '{{abc-123.data.context_json}}')
        self.assertNotEqual(canonical_prompt('Texto cambiado {{ index . "abc-123.data.context_json" }}'), '{{abc-123.data.context_json}}')

    def test_sensor_accepts_bound_123_part_without_inventing_a_citizen_call(self):
        from demo import DemoBridge
        import uuid
        bridge = DemoBridge(Mock(), provider=Mock(ready=True, responder_ready=True), resolver=Mock())
        item = {**incident(), 'sensor_report': {'source': 'FIRMS'}, 'confirmation': {'status': 'unconfirmed'}}
        bridge.overlay([item], {}, datetime.now(timezone.utc))
        run = str(uuid.uuid4())
        bridge.register(run, role='firefighter', binding={'sensor_id': item['id'], 'lat': item['lat'], 'lon': item['lon'], 'label': item['name']})
        bridge.accept(run, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_parte', 'args': {'incendio': 'confirmado'}}]}])
        overlay = bridge.overlay([item], {}, datetime.now(timezone.utc))[0]
        self.assertEqual(overlay['responder_report']['fields']['incendio'], 'confirmado')
        self.assertNotIn('demo_report', overlay)
        bridge.close()

    def test_ship_requires_explicit_call_and_is_labelled_illustrative(self):
        from demo import maritime_location
        self.assertIsNone(maritime_location({'emergencia': 'Incendio', 'ubicacion': 'Barcelona'}))
        self.assertIsNone(maritime_location({'emergencia': 'No hay incendio en el barco', 'ubicacion': 'Barcelona'}))
        location = maritime_location({'emergencia': 'Incendio en un barco', 'ubicacion': 'Mar de Barcelona'})
        self.assertTrue(location['maritime'])
        self.assertTrue(location['approximate'])
        self.assertGreater(location['lon'], 2.22)

    def test_alert_cancel_and_timeout_are_mutually_exclusive(self):
        from director import Director
        from unittest.mock import patch
        director = Director(SimpleNamespace(db=Mock(), demo=SimpleNamespace(session_id='test')), planner=Mock(ready=False), router=Mock(), atlas=Mock())
        director.scene = Scene(director)
        with patch('director.threading.Timer'):
            director.propose_alert('a', 'Aviso simulado', 'director')
            proposal = director.state['pending_alerts']['a']
            director.cancel_alert(proposal['id'])
            director.deliver_alert('a', proposal['id'])
            self.assertEqual(director.alert_feed(0)['events'], [])
            director.propose_alert('b', 'Otro aviso simulado', 'director')
            proposal = director.state['pending_alerts']['b']
            director.deliver_alert('b', proposal['id'])
            director.deliver_alert('b', proposal['id'])
            self.assertEqual(len(director.alert_feed(0)['events']), 1)
            with self.assertRaises(ValueError):
                director.cancel_alert(proposal['id'])
            director.propose_alert('c', 'Plazo vencido', 'director')
            late = director.state['pending_alerts']['c']
            late['due_at'] = 0
            with self.assertRaises(ValueError):
                director.cancel_alert(late['id'])
            self.assertEqual(len(director.alert_feed(0)['events']), 2)

    def test_transport_prefers_a_hospital_outside_the_fire_and_explains_the_change(self):
        import time
        from scene import hospital_options
        near = {'id': 'near', 'name': 'Hospital junto al fuego', 'lat': 41.433, 'lon': 2.123, 'capacity': 8, 'occupied': 0}
        far = {'id': 'far', 'name': 'Hospital alejado', 'lat': 41.46, 'lon': 2.16, 'capacity': 8, 'occupied': 0}
        full = {'id': 'full', 'name': 'Hospital sin plazas', 'lat': 41.47, 'lon': 2.17, 'capacity': 8, 'occupied': 8}
        ordered, avoided, margin = hospital_options([near, far, full], {'lat': 41.43, 'lon': 2.12, 'radius_km': .5})
        self.assertEqual([h['id'] for h in ordered], ['far', 'near'])
        self.assertEqual([h['id'] for h in avoided], ['near'])
        self.assertAlmostEqual(margin, 2)
        alone, none_avoided, _ = hospital_options([near], {'lat': 41.43, 'lon': 2.12, 'radius_km': .5})
        self.assertEqual([h['id'] for h in alone], ['near'])
        self.assertEqual(none_avoided, [])

        self.scene.data['hospitals'] = [near, far]
        self.scene.observe({'incidents': [incident()]}, 1789812000)
        self.scene.observe({'incidents': [incident()]}, 1789812009)
        self.scene.data['incidents']['sensor'].update(medical=True, radius_km=.5)
        self.scene.route = lambda start, end: {'coordinates': [start, end], 'cumulative_km': [0, 3.3],
                                               'distance_km': 3.3, 'duration_seconds': 600, 'edge_ids': []}
        assignment = {'incident_id': 'sensor', 'status': 'onscene', 'arrived_at': time.time() - 20,
                      'started_at': time.time() - 60, 'travel_seconds': 60, 'target': [2.12, 41.43],
                      'resource': {'id': 'amb', 'kind': 'ambulance', 'name': 'Ambulancia', 'lat': 41.44, 'lon': 2.13},
                      'route': {'coordinates': [[2.13, 41.44], [2.12, 41.43]], 'cumulative_km': [0, 1], 'distance_km': 1, 'edge_ids': []}}
        self.director.state['assignments'] = {'amb': assignment}
        self.scene.maintenance()
        self.assertEqual(assignment['status'], 'transporting')
        self.assertEqual(assignment['hospital_id'], 'far')
        self.assertEqual(assignment['avoided_hospital_ids'], ['near'])
        self.assertEqual(far['occupied'], 1)
        self.assertEqual(near['occupied'], 0)
        kind, message, reason = self.director.event.call_args[0]
        self.assertEqual(kind, 'transport')
        self.assertIn('seguridad', message)
        self.assertIn('Hospital junto al fuego', reason)
        self.assertIn('no es protocolo sanitario', reason)

    def test_manual_wind_and_fire_power_preserve_observations(self):
        item = {**incident(), 'scene_report': {'source': 'fixture'}}
        original = deepcopy(item)
        self.scene.observe({'incidents': [item]}, 1000)
        self.scene.data['automatic'] = False
        record = self.scene.data['incidents']['sensor']
        self.scene.command({'action': 'wind', 'incident_id': 'sensor', 'value': 45})
        self.assertEqual(record['wind_to'], 45)
        self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': -1})
        before = record['radius_km']
        self.scene.evolve(record['last_tick'] + 1)
        self.assertLess(record['radius_km'], before)
        self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': 100})
        self.assertEqual(record['phase'], 'active')
        before = record['radius_km']
        self.scene.evolve(record['last_tick'] + 10)
        self.assertGreater(record['radius_km'], before)
        self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': 0})
        self.assertEqual(record['fire_power'], 0)
        self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': -100})
        before = record['radius_km']
        now = record['last_tick']
        self.scene.evolve(now + 10)
        self.assertLess(record['radius_km'], before)
        for elapsed in range(20, 100, 10):
            self.scene.evolve(now + elapsed)
            if record['phase'] == 'releasing':
                break
        self.assertEqual(record['phase'], 'releasing')
        with self.assertRaises(ValueError):
            self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': 100})
        self.assertEqual(item, original)
        self.assertEqual(self.scene.overlay({'incidents': [item]})['incidents'][0]['weather'], original['weather'])

    def test_manual_controls_validate_values_and_terminal_phases(self):
        self.scene.observe({'incidents': [{**incident(), 'scene_report': {"source": "fixture"}}]}, 1000)
        for action, invalid in [('wind', [-1, 360, '90', None, True, float('nan'), float('inf')]),
                                ('fire_power', [-101, 101, '0', None, False, float('nan')])]:
            for value in invalid:
                with self.subTest(action=action, value=value), self.assertRaises(ValueError):
                    self.scene.command({'action': action, 'incident_id': 'sensor', 'value': value})
        record = self.scene.data['incidents']['sensor']
        for phase in ('releasing', 'closed'):
            record['phase'] = phase
            with self.assertRaises(ValueError):
                self.scene.command({'action': 'fire_power', 'incident_id': 'sensor', 'value': 100})
        self.assertNotIn('fire_power', record)

    def test_random_closure_reroutes_locally_or_stops_without_a_detour(self):
        from local_routes import RoadGraph
        from test_local_routes import way
        from unittest.mock import patch
        import time
        for detour in (True, False):
            with self.subTest(detour=detour):
                self.setUp()
                elements = [way(1, [1, 2, 3], [(2.1, 41.4), (2.101, 41.4), (2.102, 41.4)])]
                if detour:
                    elements.append(way(2, [1, 4, 3], [(2.1, 41.4), (2.101, 41.401), (2.102, 41.4)]))
                graph = RoadGraph({'elements': elements})
                start, end = [2.1, 41.4], [2.102, 41.4]
                route = graph.route(start, end)
                self.director.router = Mock()
                self.director.router.route.side_effect = lambda a, b, **kw: graph.route(a, b, blocked=kw['blocked'], congestion=kw['congestion'])
                assignment = {'incident_id': 'sensor', 'status': 'enroute', 'route': route,
                              'started_at': time.time(), 'travel_seconds': 100, 'target': end,
                              'resource': {'kind': 'fire_engine'}}
                self.director.state['assignments'] = {'truck': assignment}
                with patch('scene.random.choice', side_effect=lambda candidates: candidates[-1]) as choose:
                    self.scene.command({'action': 'random_closure'})
                choose.assert_called_once()
                self.assertEqual(len(self.scene.data['closures']), 1)
                self.assertEqual(assignment['previous_route'], route)
                self.assertTrue(self.director.router.route.call_args.kwargs['scenario'])
                if detour:
                    self.assertEqual(assignment['status'], 'enroute')
                    self.assertNotEqual(assignment['route']['coordinates'], route['coordinates'])
                    self.assertFalse(set(assignment['route']['edge_ids']) & set(self.scene.data['closures']))
                else:
                    self.assertEqual(assignment['status'], 'blocked')
                    self.assertIn('held_position', assignment)

    def test_random_closure_rejects_missing_or_finished_routes(self):
        with self.assertRaises(ValueError):
            self.scene.command({'action': 'random_closure'})
        self.assertFalse(self.scene.data['closures'])

    def test_no_automatic_maritime_incident(self):
        self.scene.observe({'incidents': []}, 1789812000)
        self.assertEqual(self.scene.overlay({'incidents': []})['incidents'], [])


class FireShapeTests(TestCase):
    def test_fire_polygon_has_fronts_and_keeps_mean_radius(self):
        import math
        from fireshape import fire_polygon, MAX_RADIUS_FACTOR, MIN_RADIUS_FACTOR
        polygon = fire_polygon(2.17, 41.4, .5, 90, 'demo:x')
        ring = polygon['coordinates'][0]
        self.assertEqual(ring[0], ring[-1])
        east = 111.32 * math.cos(math.radians(41.4))
        reach = [math.hypot((lon - 2.17) * east, (lat - 41.4) * 111.32) for lon, lat in ring[:-1]]
        self.assertAlmostEqual(sum(reach) / len(reach), .5, delta=.03)
        self.assertLessEqual(max(reach), .5 * MAX_RADIUS_FACTOR + 1e-9)
        self.assertGreaterEqual(min(reach), .5 * MIN_RADIUS_FACTOR - 1e-9)
        self.assertGreater(max(reach) / min(reach), 2, 'frentes marcados, no un óvalo')
        eastmost = max(ring, key=lambda p: p[0])
        westmost = min(ring, key=lambda p: p[0])
        self.assertGreater(eastmost[0] - 2.17, 2.17 - westmost[0], 'alargado a favor del viento')
        self.assertEqual(polygon, fire_polygon(2.17, 41.4, .5, 90, 'demo:x'), 'estable por semilla')
        self.assertNotEqual(polygon, fire_polygon(2.17, 41.4, .5, 90, 'demo:y'))
        grown = fire_polygon(2.17, 41.4, 1.0, 90, 'demo:x')['coordinates'][0]
        ratios = [math.hypot((g[0] - 2.17) * east, (g[1] - 41.4) * 111.32) / r for g, r in zip(grown[:-1], reach)]
        self.assertAlmostEqual(min(ratios), 2, delta=.01)
        self.assertAlmostEqual(max(ratios), 2, delta=.01)
