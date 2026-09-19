import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from outbound import OutboundCalls
from reports import impact, pdf_bytes, report_markdown


class OutboundTests(unittest.TestCase):
    def setUp(self):
        self.provider = Mock()
        self.provider.module.list_data.side_effect = lambda response: response['data']
        self.db = Mock()
        self.db.setting.return_value = {'published': True, 'workflow_id': 'workflow'}
        self.demo = SimpleNamespace(provider=self.provider, calls={}, register=Mock(), poll_call=Mock())
        self.director = SimpleNamespace(db=self.db, store=SimpleNamespace(demo=self.demo, allow_outbound=False),
            state={'assignments': {'truck': {'resource': {'kind': 'fire_engine'}, 'status': 'onscene', 'incident_id': 'fire'}}},
            operations=SimpleNamespace(records={'fire': {}}), event=Mock(), save=Mock())
        self.calls = OutboundCalls(self.director)
        self.incident = {'id': 'fire', 'name': 'Barcelona', 'lat': 41.4, 'lon': 2.1}
        self.db.contacts.side_effect = lambda role='firefighter': ([{'id': 'origin', 'phone': '+34900000003'}] if role == 'caller' else
            [{'id': 'primary', 'phone': '+34900000001'}, {'id': 'backup', 'phone': '+34900000002'}])

    def test_phone_is_disabled_without_explicit_enable(self):
        self.calls.tick({'incidents': [self.incident]})
        self.provider.client.request.assert_not_called()
        self.assertEqual(self.calls.jobs['fire']['status'], 'disabled')

    def test_numbers_come_from_database_and_attempt_is_persisted_before_call(self):
        seen = []
        self.director.save.side_effect = lambda: seen.append(self.calls.jobs['fire']['status'])
        run = '00000000-0000-4000-8000-000000000001'
        self.provider.client.request.side_effect = lambda *args: (seen.append('network') or {'run_id': run})
        self.calls.start(self.incident, 'truck', 1)
        self.assertEqual(seen[:2], ['starting', 'network'])
        payload = self.provider.client.request.call_args.args[2]['payload']
        self.assertEqual(payload['phone_number'], '+34900000002')
        self.assertEqual(payload['from_number'], '+34900000003')
        self.assertEqual(self.calls.jobs['fire']['run_id'], run)

    def test_uncertain_start_is_not_redialed(self):
        self.calls.enabled = True
        self.provider.client.request.side_effect = TimeoutError()
        self.calls.start(self.incident, 'truck', 0)
        self.assertEqual(self.calls.jobs['fire']['status'], 'uncertain')
        self.calls.last_poll = 0
        self.calls.tick({'incidents': [self.incident]})
        self.assertEqual(self.provider.client.request.call_count, 1)

    def test_only_a_terminal_failed_result_enables_backup(self):
        job = {'run_id': 'run', 'status': 'dialing', 'attempt': 1}
        self.provider.client.request.return_value = {'data': [{'run_id': 'run', 'type': 'outbound', 'status': 'busy'}]}
        self.calls.poll('fire', job)
        self.assertEqual(job['status'], 'retry_backup')
        job.update(status='dialing', attempt=2)
        self.calls.poll('fire', job)
        self.assertEqual(job['status'], 'unreachable')


class ReportTests(unittest.TestCase):
    def test_impact_uses_peak_area_not_extinguished_animation(self):
        scene = {'started_at': 100, 'peak_radius_km': .5, 'radius_km': .02}
        metrics = impact(scene, {'personas_asistidas': '2'}, 500)
        self.assertGreater(metrics['scenario_area_ha'], 40)
        self.assertGreaterEqual(metrics['avoided_area_ha'], 0)
        self.assertEqual(metrics['assisted_people'], 2)
        self.assertEqual(metrics['issued_credits'], 0)
        self.assertEqual(len(metrics['carbon_value_eur']), 3)

    def test_missing_people_and_maritime_carbon_are_not_invented(self):
        metrics = impact({'maritime': True, 'started_at': 0}, {}, 100)
        self.assertIsNone(metrics['potential_lives_saved'])
        self.assertIsNone(metrics['avoided_co2_t'])

    def test_pdf_has_pages_xref_and_carbon_disclaimer(self):
        report = {'title': 'Prueba España', 'summary': 'Simulacro', 'metrics': impact({'started_at': 0}, {}, 100),
                  'field_report': {}, 'requests': [], 'events': [], 'closed_at': 100}
        markdown = report_markdown(report)
        self.assertIn('no un crédito certificado', markdown)
        pdf = pdf_bytes(markdown)
        self.assertTrue(pdf.startswith(b'%PDF-1.4'))
        self.assertTrue(pdf.endswith(b'%%EOF\n'))
        self.assertIn(b'/Type /Page ', pdf)
        self.assertIn(b'xref\n', pdf)


if __name__ == '__main__':
    unittest.main()
