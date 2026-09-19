from copy import deepcopy
import unittest

from director import fingerprint, extract_plan, validate_plan, route_position, EmergencyAtlas, Director
from types import SimpleNamespace
from unittest.mock import Mock, patch
import time


class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.context = {'revision': 'abc', 'incidents': [{'id': 'fire', 'lat': 41, 'lon': 1}],
                        'resources': [{'id': 'truck', 'kind': 'fire_engine'}]}
        self.plan = {'revision': 'abc', 'summary': 'Prioridad al aviso', 'actions': [
            {'type': 'dispatch', 'incident_id': 'fire', 'resource_id': 'truck', 'reason': 'Recurso próximo'}]}

    def test_valid_and_no_mutation(self):
        original = deepcopy(self.plan)
        self.assertEqual(validate_plan(self.plan, self.context), original)
        self.assertEqual(self.plan, original)

    def test_rejects_unknown_stale_and_duplicate(self):
        for key, value in [('revision', 'old'), ('actions', [{'type': 'send_sms', 'reason': 'test'}])]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_plan({**self.plan, key: value}, self.context)
        for changes in ({'resource_id': 'invented'}, {'incident_id': 'invented'}, {'reason': ''}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_plan({**self.plan, 'actions': [{**self.plan['actions'][0], **changes}]}, self.context)
        with self.assertRaises(ValueError):
            validate_plan({**self.plan, 'actions': self.plan['actions'] * 2}, self.context)

    def test_plan_only_from_assistant_tool(self):
        import json
        call = {'function': {'name': 'publicar_plan', 'arguments': json.dumps({'plan_json': json.dumps(self.plan)})}}
        self.assertIsNone(extract_plan([{'role': 'user', 'tool_calls': [call]}]))
        self.assertEqual(extract_plan([{'role': 'assistant', 'tool_calls': [call]}]), self.plan)

    def test_real_happyrobot_tool_envelope_and_nested_fallback(self):
        import json
        args = {'plan_json': json.dumps(self.plan)}
        for call in [
            {'name': 'publicar_plan', 'args': args, 'type': 'function', 'function': {'name': 'publicar_plan', 'arguments': json.dumps(args)}},
            {'name': 'publicar_plan', 'function': {'name': 'publicar_plan', 'arguments': json.dumps(args)}},
            {'name': 'publicar_plan', 'args': args},
        ]:
            with self.subTest(call=call):
                self.assertEqual(extract_plan([{'role': 'assistant', 'tool_calls': [call]}]), self.plan)

    def test_prompt_references_runtime_hook_data_envelope(self):
        from director_workflow import context_prompt
        prompt = context_prompt('trigger-test')
        self.assertIn('{{trigger-test.data.context_json}}', prompt)
        self.assertNotIn('{{trigger-test.context_json}}', prompt)

    def test_sync_keeps_literal_hook_key_and_updates_all_node_ids(self):
        from director_workflow import sync, NAME
        database = Mock()
        database.director_setting.return_value = {'workflow_id': 'workflow', 'hook_key': 'literal-test-key'}
        provider = Mock()
        provider.module.list_data.side_effect = lambda value: value['data']
        provider.client.request.side_effect = [
            {'data': {'name': NAME, 'latest_version': {'id': 'v2', 'is_published': True}}},
            {'data': [{'id': 'hook2', 'name': 'Cambio del entorno'}, {'id': 'prompt2', 'type': 'prompt'}, {'id': 'tool2', 'name': 'publicar_plan'}]},
            {'data': {'configuration': {'enhanced_security': True, 'auth_type': 'api_key', 'api_key': 'transformed-server-value'},
                      'webhook_urls': {'production': 'https://workflows.platform.eu.happyrobot.ai/hooks/test'}}},
        ]
        with patch('director_workflow.HappyRobotProvider', return_value=provider):
            config = sync(database)
        self.assertEqual(config['hook_key'], 'literal-test-key')
        self.assertEqual(config['prompt_id'], 'prompt2')
        self.assertEqual(config['tool_id'], 'tool2')
        self.assertEqual(config['trigger_id'], 'hook2')

    def test_fingerprint_ignores_poll_clock_but_tracks_corrections_and_weather(self):
        payload = {'generated_at': '1', 'status': 'ready', 'incidents': [{'id': 'a', 'lat': 41, 'lon': 1,
                   'demo_report': {'run_id': 'call', 'summary': {'riesgos': 'humo'}}, 'weather': {'wind_speed_kmh': 10}}]}
        self.assertEqual(fingerprint(payload), fingerprint({**payload, 'generated_at': '2'}))
        changed = deepcopy(payload)
        changed['incidents'][0]['demo_report']['summary']['riesgos'] = 'personas atrapadas'
        self.assertNotEqual(fingerprint(payload), fingerprint(changed))
        changed = deepcopy(payload)
        changed['incidents'][0]['weather']['wind_speed_kmh'] = 25
        self.assertNotEqual(fingerprint(payload), fingerprint(changed))
        self.assertNotEqual(fingerprint(payload), fingerprint({**payload, 'incidents': []}))

    def test_route_progress_uses_distance_not_vertices(self):
        route = {'coordinates': [[0, 40], [0.001, 40], [0.1, 40]], 'cumulative_km': [0, 1, 100]}
        self.assertEqual(route_position(route, 0), [0, 40])
        self.assertEqual(route_position(route, 1), [.1, 40])
        self.assertAlmostEqual(route_position(route, .5)[0], .05)

    def test_real_atlas_is_read_only_and_does_not_invent_contacts(self):
        stations = EmergencyAtlas().nearby(41.1189, 1.2445)
        self.assertTrue(stations)
        self.assertTrue(any(s['kind'] == 'fire_engine' for s in stations))
        self.assertTrue(all(s['simulated_capacity'] for s in stations))
        self.assertTrue(all('phone' not in s for s in stations))


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'incidents': [{'id': 'fire', 'lat': 41, 'lon': 1, 'demo_report': {'summary': {}}, 'weather': {}}]}
        self.store = SimpleNamespace(db=Mock(), demo=SimpleNamespace(session_id='test'), payload=lambda: deepcopy(self.payload))
        self.planner = Mock(ready=True)
        self.router = Mock()
        self.route = {'coordinates': [[1, 41], [1.01, 41]], 'cumulative_km': [0, 1], 'duration_seconds': 90, 'distance_km': 1}
        self.router.route.return_value = self.route
        self.director = Director(self.store, self.planner, self.router, Mock())
        self.resource = {'id': 'truck', 'station_id': 'base', 'kind': 'fire_engine', 'name': 'Parque', 'lat': 41, 'lon': 1}
        self.director.state['resources']['truck'] = self.resource
        self.context = {'revision': 'r', 'incidents': self.payload['incidents'], 'resources': [self.resource]}
        self.plan = {'revision': 'r', 'summary': 'Atender aviso', 'actions': [
            {'type': 'dispatch', 'resource_id': 'truck', 'incident_id': 'fire', 'reason': 'Disponible y próximo'}]}
        self.director.state['pending'] = {'run_id': 'run', 'context': self.context, 'fingerprint': fingerprint(self.payload), 'started_at': time.time()}
        self.planner.poll.return_value = self.plan

    def test_applies_once_and_reserves_vehicle(self):
        self.director.step()
        self.assertIn('truck', self.director.state['assignments'])
        sequence = self.director.state['sequence']
        self.director.step()
        self.assertEqual(self.director.state['sequence'], sequence)
        self.assertEqual(self.planner.poll.call_count, 1)
        with self.assertRaises(ValueError):
            self.director.prepare(self.plan, self.context)

    def test_stale_plan_does_not_execute(self):
        self.payload['incidents'][0]['lat'] = 42
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})
        self.router.route.assert_not_called()
        self.assertEqual(self.director.state['events'][-1]['kind'], 'superseded')

    def test_correction_while_computing_route_does_not_execute(self):
        def change(*args):
            self.payload['incidents'] = []
            return self.route
        self.router.route.side_effect = change
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})

    def test_no_route_no_dispatch(self):
        self.router.route.side_effect = ValueError('Sin carretera')
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})
        self.assertEqual(self.director.state['events'][-1]['kind'], 'blocked')

    def test_arrival_is_not_availability_and_return_frees_only_on_arrival(self):
        self.director.step()
        assignment = self.director.state['assignments']['truck']
        assignment['started_at'] = 0
        self.director.advance()
        self.assertEqual(assignment['status'], 'onscene')
        returning = {'revision': 'r', 'summary': 'Regreso', 'actions': [{'type': 'return', 'resource_id': 'truck', 'reason': 'Aviso retirado'}]}
        actions = self.director.prepare(returning, self.context)
        self.director.apply(returning, actions, 'return-run')
        self.assertIn('truck', self.director.state['assignments'])
        self.director.state['assignments']['truck']['started_at'] = 0
        self.director.advance()
        self.assertNotIn('truck', self.director.state['assignments'])

    def test_two_incidents_share_inventory_and_reassign_from_current_position(self):
        self.director.step()
        second = {'id': 'second', 'lat': 41.02, 'lon': 1.02}
        self.context['incidents'].append(second)
        replacement = {'revision': 'r', 'summary': 'Mayor prioridad', 'actions': [{
            'type': 'reassign', 'incident_id': 'second', 'resource_id': 'truck', 'reason': 'Peligro vital comunicado'}]}
        self.director.state['assignments']['truck']['started_at'] = time.time() - 10
        actions = self.director.prepare(replacement, self.context)
        origin = self.router.route.call_args.args[0]
        self.assertGreater(origin[0], 1)
        self.assertLess(origin[0], 1.01)
        self.director.apply(replacement, actions, 'reassign-run')
        self.assertEqual(len(self.director.state['assignments']), 1)
        self.assertEqual(self.director.state['assignments']['truck']['incident_id'], 'second')

    def test_location_correction_can_redirect_same_incident(self):
        self.director.step()
        self.context['incidents'][0]['lon'] = 1.02
        correction = deepcopy(self.plan)
        correction['actions'][0]['type'] = 'reassign'
        actions = self.director.prepare(correction, self.context)
        self.assertEqual(actions[0]['target'], [1.02, 41])

    def test_auth_outage_still_advances_existing_simulation(self):
        self.director.step()
        self.director.state['assignments']['truck']['started_at'] = 0
        self.planner.ready = False
        self.director.step()
        self.assertEqual(self.director.state['assignments']['truck']['status'], 'onscene')

    def test_sql_failure_does_not_publish_uncommitted_actions(self):
        self.store.db.save_director.side_effect = RuntimeError('SQL no disponible')
        with self.assertRaises(RuntimeError):
            self.director.step()
        self.assertEqual(self.director.state['assignments'], {})


if __name__ == '__main__':
    unittest.main()
