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

    def test_arrival_does_not_close_and_suppression_requires_work_then_watch(self):
        self.scene.observe({'incidents': [incident()]}, 1789812000)
        self.scene.observe({'incidents': [incident()]}, 1789812009)
        record = self.scene.data['incidents']['sensor']
        self.scene.evolve(1789812040)
        self.assertEqual(record['phase'], 'active')
        self.director.state['assignments'] = {
            str(n): {'incident_id': 'sensor', 'status': 'onscene', 'resource': {'kind': 'fire_engine'}} for n in range(2)}
        self.scene.evolve(1789812041)
        self.assertEqual(record['phase'], 'active')
        self.scene.evolve(1789812090)
        self.assertEqual(record['phase'], 'contained')
        self.scene.evolve(1789812115)
        self.assertEqual(record['phase'], 'watching')
        self.scene.evolve(1789812165)
        self.assertEqual(record['phase'], 'releasing')
        self.director.state['assignments'] = {}
        self.scene.evolve(1789812170)
        self.assertEqual(record['phase'], 'closed')

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

    def test_no_automatic_maritime_incident(self):
        self.scene.observe({'incidents': []}, 1789812000)
        self.assertEqual(self.scene.overlay({'incidents': []})['incidents'], [])
