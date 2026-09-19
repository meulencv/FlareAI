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

    def test_voice_prompt_replacement_preserves_voice_tools_and_requires_consent(self):
        from director_workflow import replace_voice_prompt
        client = Mock()
        with self.assertRaises(ValueError):
            replace_voice_prompt(client, 'voice', 'Voice', 'live', 'Short prompt')
        client.request.assert_not_called()
        prompt = {'id': 'prompt', 'type': 'prompt', 'name': 'Voice', 'configuration': {'keep': True}, 'model': {'original': True}, 'initial_message': 'Hola'}
        client.request.side_effect = [
            {'name': 'Voice', 'latest_version': {'id': 'live', 'is_live': True}}, {'data': []},
            {'id': 'draft'}, [{'id': 'prompt', 'type': 'prompt'}, {'id': 'tool', 'type': 'tool'}],
            prompt, {}, {**prompt, 'prompt_md': 'Short prompt'}, {'data': []}, {'is_live': True, 'is_published': True},
        ]
        result = replace_voice_prompt(client, 'voice', 'Voice', 'live', 'Short prompt', replace_live=True)
        self.assertEqual(result['previous_version_id'], 'live')
        writes = [call for call in client.request.call_args_list if call.args[0] == 'PUT']
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0].args[2]['configuration'], prompt['configuration'])
        self.assertEqual(writes[0].args[2]['model'], prompt['model'])
        self.assertEqual(client.request.call_args_list[-1].args, ('POST', '/versions/draft/publish', {'environment': 'production', 'unpublish_version_id': 'live'}))

    def test_active_voice_call_prevents_fork_and_publication(self):
        from director_workflow import replace_voice_prompt
        client = Mock()
        client.request.side_effect = [{'name': 'Voice', 'latest_version': {'id': 'live', 'is_live': True}}, {'data': [{'id': 'active'}]}]
        with self.assertRaises(RuntimeError):
            replace_voice_prompt(client, 'voice', 'Voice', 'live', 'Short prompt', replace_live=True)
        self.assertTrue(all(call.args[0] == 'GET' for call in client.request.call_args_list))

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

    def test_transport_hospitals_require_emergency_ward_and_drop_other_centres(self):
        hospitals = EmergencyAtlas().hospitals(41.41, 2.15)
        self.assertTrue(hospitals)
        names = [(h['name'] or '').lower() for h in hospitals]
        self.assertTrue(any('sant pau' in name for name in names))
        self.assertTrue(any("vall d'hebron" in name for name in names))
        for rejected in ('atenció primària', 'salut mental', 'residència', 'sociosanitari'):
            self.assertFalse([name for name in names if rejected in name], rejected)
        self.assertTrue(all(h['emergency_ward'] in {'own', 'nearby'} for h in hospitals))
        self.assertTrue(all(h['capacity'] == 8 and h['occupied'] == 0 and h['simulated_capacity'] for h in hospitals))
        self.assertTrue(all('phone' not in h for h in hospitals))

    def test_hospitals_on_the_same_site_are_unified_without_merging_neighbours(self):
        from director import same_site
        campus = {'name': "HOSPITAL UNIVERSITARI VALL D'HEBRON", 'lat': 41.42803, 'lon': 2.14077}
        pavilion = {'name': "1- Hospital General Vall d'Hebron", 'lat': 41.42770, 'lon': 2.14175}
        neighbour = {'name': 'FUNDACIO PUIGVERT - IUNA', 'lat': 41.41293, 'lon': 2.17278}
        sant_pau = {'name': 'HOSPITAL DE LA SANTA CREU I SANT PAU', 'lat': 41.41398, 'lon': 2.17422}
        duplicate = {'name': None, 'lat': 41.42805, 'lon': 2.14079}
        self.assertTrue(same_site(campus, pavilion))
        self.assertTrue(same_site(campus, duplicate))
        self.assertFalse(same_site(sant_pau, neighbour))
        self.assertFalse(same_site(campus, sant_pau))
        hospitals = EmergencyAtlas().hospitals(41.41, 2.15)
        merged = next(h for h in hospitals if "vall d'hebron" in (h['name'] or '').lower())
        self.assertTrue(merged['merged_ids'])
        self.assertEqual(len({h['id'] for h in hospitals}), len(hospitals))
        self.assertFalse({m for h in hospitals for m in h['merged_ids']} & {h['id'] for h in hospitals})


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'incidents': [{'id': 'fire', 'lat': 41, 'lon': 1, 'demo_report': {'summary': {}}, 'weather': {}}]}
        self.store = SimpleNamespace(db=Mock(), demo=SimpleNamespace(session_id='test'), payload=lambda: deepcopy(self.payload))
        self.planner = Mock(ready=True)
        self.router = Mock()
        self.route = {'coordinates': [[1, 41], [1.01, 41]], 'cumulative_km': [0, 1], 'duration_seconds': 90, 'distance_km': 1}
        self.router.route.return_value = self.route
        self.director = Director(self.store, self.planner, self.router, Mock())
        self.director.auto.enabled = False  # estas pruebas cubren el camino del planner LLM; el dispositivo automático tiene las suyas
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
        # Una unidad ya movilizada no se roba ni se duplica: sin alternativa libre queda bloqueada, no lanza.
        repeated = self.director.prepare(self.plan, self.context)
        self.assertTrue(repeated[0]['route_error'])
        self.assertIn('ya está movilizada', repeated[0]['blocked_reason'])

    def test_stale_plan_does_not_execute(self):
        self.payload['incidents'][0]['lat'] = 42
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})
        self.router.route.assert_not_called()
        self.assertEqual(self.director.state['events'][-1]['kind'], 'superseded')

    def test_growing_call_summary_dispatches_and_reviews_afterwards(self):
        from director import anchor
        self.director.state['pending']['anchor'] = anchor(self.payload)
        self.payload['incidents'][0]['demo_report']['summary'] = {'riesgos': 'el llamante sigue describiendo el humo'}
        self.director.step()
        self.assertIn('truck', self.director.state['assignments'])
        self.assertNotEqual(self.director.state['events'][-1]['kind'], 'superseded')
        self.payload['incidents'][0]['demo_report']['summary'] = {'riesgos': 'ahora informa de personas atrapadas'}
        self.assertNotEqual(self.director.state['last_fingerprint'], fingerprint(self.payload))

    def test_location_correction_still_supersedes_an_in_flight_plan(self):
        from director import anchor
        self.director.state['pending']['anchor'] = anchor(self.payload)
        self.payload['incidents'][0]['demo_report']['location'] = {'lat': 41.5, 'lon': 2.1, 'precision': 'address'}
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})
        self.assertEqual(self.director.state['events'][-1]['kind'], 'superseded')

    def test_correction_while_computing_route_does_not_execute(self):
        def change(*args):
            self.payload['incidents'] = []
            return self.route
        self.router.route.side_effect = change
        self.director.step()
        self.assertEqual(self.director.state['assignments'], {})

    def test_unreachable_station_uses_available_alternative_without_taking_busy_units(self):
        alternative = {**self.resource, 'id': 'alternative', 'station_id': 'other-base', 'lon': 1.02}
        busy = {**self.resource, 'id': 'busy', 'station_id': 'busy-base', 'lon': 1.001}
        self.context['resources'].extend([alternative, busy])
        self.director.state['resources'].update({r['id']: r for r in [alternative, busy]})
        self.director.state['assignments']['busy'] = {'incident_id': 'other-fire'}
        self.router.route.side_effect = [ValueError('Sin conexión'), self.route]
        actions = self.director.prepare(self.plan, self.context)
        self.assertEqual(actions[0]['resource_id'], 'alternative')
        self.assertEqual(actions[0]['requested_resource_id'], 'truck')
        self.director.apply(self.plan, actions, 'replacement-run')
        self.assertIn('alternative', self.director.state['assignments'])
        self.assertEqual(self.director.state['assignments']['busy']['incident_id'], 'other-fire')
        self.assertTrue(any(e['kind'] == 'alternative' for e in self.director.state['events']))

    def test_alternative_does_not_steal_another_action_resource(self):
        second = {**self.resource, 'id': 'second', 'station_id': 'other-base', 'lon': 1.02}
        self.context['resources'].append(second)
        self.director.state['resources']['second'] = second
        plan = deepcopy(self.plan)
        plan['actions'].append({**plan['actions'][0], 'resource_id': 'second'})
        self.router.route.side_effect = [ValueError('Sin conexión'), ValueError('Sin conexión relajada'), self.route]
        actions = self.director.prepare(plan, self.context)
        self.assertEqual(actions[0]['resource_id'], 'truck')
        self.assertEqual(actions[0]['route']['mode'], 'ground_fallback')
        self.assertTrue(actions[0]['route_fallback'])
        self.assertEqual(actions[1]['resource_id'], 'second')
        self.assertFalse(actions[1]['route'].get('approximate'))

    def test_station_inventory_counts_busy_and_available_resources(self):
        second = {**self.resource, 'id': 'second'}
        self.director.state['resources']['second'] = second
        self.director.step()
        station = self.director.public_state()['stations'][0]
        self.assertEqual((station['total'], station['available'], station['busy']), (2, 1, 1))
        self.assertTrue(station['simulated_capacity'])

    def test_no_road_route_still_dispatches_with_labelled_fallback(self):
        self.router.route.side_effect = ValueError('Sin carretera')
        self.director.step()
        assignment = self.director.state['assignments']['truck']
        self.assertEqual(assignment['status'], 'enroute')
        self.assertEqual(assignment['route']['mode'], 'ground_fallback')
        self.assertTrue(assignment['route']['approximate'])
        self.assertEqual(assignment['route']['coordinates'], [[1, 41], [1, 41]])
        kinds = [e['kind'] for e in self.director.state['events']]
        self.assertIn('approximate', kinds)
        self.assertIn('dispatch', kinds)
        self.assertNotIn('blocked', kinds)
        self.assertFalse(self.director.state.get('route_retry_at'))

    def test_relaxed_road_route_is_preferred_over_straight_fallback(self):
        relaxed = {**self.route, 'approximate': True, 'source': 'OpenStreetMap · A* local (sin sentidos)'}
        self.router.route.side_effect = lambda *args, **kwargs: relaxed if kwargs.get('relaxed') else (_ for _ in ()).throw(ValueError('Sentido único'))
        actions = self.director.prepare(self.plan, self.context)
        self.assertIs(actions[0]['route'], relaxed)
        self.assertNotEqual(actions[0]['route'].get('mode'), 'ground_fallback')
        self.assertTrue(actions[0]['route_fallback'])

    def test_new_call_dispatches_after_thirty_or_more_runs_without_reset(self):
        for count in (30, 100):
            with self.subTest(count=count):
                self.setUp()
                self.director.state['pending'] = None
                self.director.state['runs'] = [time.time() - 5] * count
                with patch.object(self.director, 'context', return_value=self.context):
                    self.planner.start.return_value = 'new-run'
                    self.director.step()
                self.planner.start.assert_called_once()
                self.assertEqual(self.director.public_state()['status'], 'thinking')
                self.director.step()
                self.assertIn('truck', self.director.state['assignments'])
                self.assertEqual(self.director.public_state()['status'], 'watching')

    def test_pending_run_prevents_duplicate_starts(self):
        self.planner.poll.return_value = None
        for _ in range(5):
            self.director.step()
        self.planner.start.assert_not_called()
        self.assertEqual(self.director.state['pending']['run_id'], 'run')
        self.assertFalse(self.director.state['assignments'])

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

    def test_helicopter_requires_part_and_uses_air_path_not_road_router(self):
        helicopter = {**self.resource, 'id': 'heli', 'kind': 'helicopter'}
        self.director.state['resources']['heli'] = helicopter
        self.context['resources'].append(helicopter)
        plan = deepcopy(self.plan)
        plan['actions'][0]['resource_id'] = 'heli'
        self.assertTrue(self.director.prepare(plan, self.context)[0]['route_error'])
        self.context['incidents'][0]['responder_report'] = {'fields': {'helicoptero': 'solicitado'}}
        self.context['incidents'][0]['lon'] = 1.1
        action = self.director.prepare(plan, self.context)[0]
        self.assertEqual(action['route']['mode'], 'air_demo')
        self.router.route.assert_not_called()
        self.director.apply(plan, [action], 'air-run')
        self.assertEqual(self.director.state['assignments']['heli']['resource']['kind'], 'helicopter')

    def test_explicit_alert_request_is_idempotent_even_without_planner(self):
        self.planner.ready = False
        report = {'revision': 2, 'fields': {'es_alert': 'solicitado'}, 'field_versions': {'es_alert': 2}}
        self.payload['demo'] = {'field_reports': {'fire': report}}
        self.director.step()
        self.assertEqual(self.director.alert_feed(0)['events'][0]['source'], 'firefighter_request')
        self.assertEqual(self.director.alert_feed()['events'], [])
        self.assertEqual(self.director.alert_feed(1)['events'], [])
        self.director.step()
        report.update(revision=3)
        report['fields']['detalle'] = 'Humo'
        report['field_versions']['detalle'] = 3
        self.director.step()
        self.assertEqual(self.director.alert_feed(0)['sequence'], 1)
        report.update(revision=4)
        report['fields']['incendio'] = 'descartado'
        report['field_versions']['incendio'] = 4
        self.director.step()
        self.assertEqual(self.director.alert_feed(1)['events'][0]['kind'], 'cancel')
        self.assertFalse(self.director.state['alerts'])

    def test_director_alert_requires_explicit_request_or_extreme_part(self):
        plan = {**self.plan, 'actions': [{'type': 'alert', 'incident_id': 'fire', 'reason': 'Humo cerca de viviendas'}]}
        action = self.director.prepare(plan, self.context)[0]
        self.assertFalse(action['mobile_alert'])
        self.director.apply(plan, [action], 'preview')
        self.assertEqual(self.director.alert_feed(0)['events'], [])
        self.context['incidents'][0]['responder_report'] = {'fields': {'incendio': 'confirmado'}}
        self.context['incidents'][0]['environment'] = {'population': {'residents': 20}, 'landcover': {'percentages': {'urbano': 0}}}
        self.assertFalse(self.director.prepare(plan, self.context)[0]['mobile_alert'])
        self.context['incidents'][0]['responder_report'] = {'fields': {'incendio': 'confirmado', 'zona_urbana': 'si'}}
        self.assertFalse(self.director.prepare(plan, self.context)[0]['mobile_alert'])
        self.context['incidents'][0]['responder_report']['fields']['evolucion'] = 'critico'
        action = self.director.prepare(plan, self.context)[0]
        self.assertTrue(action['mobile_alert'])
        self.director.apply(plan, [action], 'notify')
        self.assertEqual(len(self.director.alert_feed(0)['events']), 1)
        self.director.apply(plan, [action], 'duplicate')
        self.assertEqual(len(self.director.alert_feed(0)['events']), 1)

    def test_report_marks_only_the_reporting_resource_arrived(self):
        self.director.step()
        self.planner.ready = False
        report = {'revision': 2, 'fields': {'llegada': 'confirmada'}, 'field_versions': {'llegada': 2}, 'field_sources': {'llegada': {'resource_id': 'truck'}}}
        self.payload['demo'] = {'field_reports': {'fire': report}}
        self.director.step()
        self.assertTrue(self.director.state['assignments']['truck']['arrival_confirmed'])
        self.assertEqual(self.director.state['assignments']['truck']['status'], 'onscene')
        self.assertNotIn('incendio', report['fields'])

    def test_sql_failure_does_not_publish_uncommitted_actions(self):
        self.store.db.save_director.side_effect = RuntimeError('SQL no disponible')
        with self.assertRaises(RuntimeError):
            self.director.step()
        self.assertEqual(self.director.state['assignments'], {})


if __name__ == '__main__':
    unittest.main()
