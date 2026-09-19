import unittest

from operations import alert_allowed, build_wave, requested_resources, visible_testimonies


class OperationTests(unittest.TestCase):
    def test_wave_is_reproducible_and_cadence_is_bounded(self):
        incident = {'id': 'fire', 'name': 'Barcelona', 'demo_report': {'summary': {'ubicacion': 'Barcelona', 'emergencia': 'incendio'}}}
        first = build_wave(incident, 100)
        self.assertEqual(first, build_wave(incident, 100))
        self.assertEqual(len(first), 24)
        times = [100, *[item['at'] for item in first]]
        self.assertTrue(all(.5 <= b - a <= 2.001 for a, b in zip(times, times[1:])))
        self.assertEqual(len({item['id'] for item in first}), 24)
        self.assertTrue(all('truth' not in item and 'classification' not in item for item in first))
        self.assertEqual(visible_testimonies(first, 100), [])
        self.assertEqual(visible_testimonies(first, 200), first)

    def test_alert_requires_explicit_request_or_extreme_field_report(self):
        self.assertFalse(alert_allowed({}))
        self.assertFalse(alert_allowed({'incendio': 'confirmado', 'zona_urbana': 'si'}))
        self.assertFalse(alert_allowed({'evolucion': 'empeora'}))
        self.assertTrue(alert_allowed({'evolucion': 'critico'}))
        self.assertTrue(alert_allowed({'es_alert': 'solicitado'}))
        self.assertFalse(alert_allowed({'incendio': 'descartado', 'es_alert': 'solicitado'}))
        self.assertFalse(alert_allowed({'evolucion': 'critico', 'es_alert': 'no_solicitado'}))

    def test_requests_preserve_types_and_quantities(self):
        self.assertEqual(requested_resources({'ambulancias': '2', 'helicoptero': 'solicitado', 'refuerzos': 'solicitado'}),
                         {'ambulance': 2, 'fire_engine': 2, 'helicopter': 1})
        self.assertEqual(requested_resources({'bomberos': '3', 'refuerzos': 'solicitado', 'helicopteros': '2'}),
                         {'fire_engine': 3, 'helicopter': 2})
        self.assertEqual(requested_resources({'ambulancias': '-1', 'bomberos': 'muchos', 'policias': '0'}), {})

    def test_newer_cancellation_overrides_old_quantity(self):
        fields = {'ambulancias': '2', 'ambulancia': 'no_solicitado'}
        self.assertEqual(requested_resources(fields, {'ambulancias': 2, 'ambulancia': 3}), {})
        self.assertEqual(requested_resources(fields, {'ambulancias': 4, 'ambulancia': 3}), {'ambulance': 2})
        self.assertEqual(requested_resources({'bomberos': '100'}), {'fire_engine': 100})

    def test_first_dispatch_requires_complete_evidence_assessment(self):
        from director import validate_plan
        context = {'revision': 'v', 'presentation': True, 'resources': [],
                   'incidents': [{'id': 'fire', 'testimonies': [{'id': 'a'}, {'id': 'b'}]}]}
        plan = {'revision': 'v', 'summary': 'Revisión', 'actions': []}
        with self.assertRaises(ValueError):
            validate_plan(plan, context)
        plan['assessments'] = [{'incident_id': 'fire', 'summary': 'No hay certeza', 'testimonies': [
            {'id': 'a', 'status': 'uncertain'}, {'id': 'b', 'status': 'uncertain'}]}]
        self.assertEqual(validate_plan(plan, context), plan)
        plan['assessments'][0]['testimonies'][1]['id'] = 'a'
        with self.assertRaises(ValueError):
            validate_plan(plan, context)


if __name__ == '__main__':
    unittest.main()
