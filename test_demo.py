import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from demo import DemoBridge, extract_report, is_fire, match_incident, resolve_local


def message(location='Igea', emergency='Incendio forestal'):
    return {'role': 'assistant', 'tool_calls': [{'function': {'name': 'actualizar_ficha', 'arguments': {'ubicacion': location, 'emergencia': emergency}}}]}


class DemoTests(unittest.TestCase):
    def test_only_structured_tool_evidence_can_confirm(self):
        self.assertEqual(extract_report([{'role': 'user', 'content': 'Hay fuego en Igea'}]), {})
        self.assertEqual(extract_report([message()])['ubicacion'], 'Igea')
        fake = message()
        fake['tool_calls'][0]['function']['name'] = 'otra_tool'
        self.assertEqual(extract_report([fake]), {})
        fake = message()
        fake['role'] = 'user'
        self.assertEqual(extract_report([fake]), {})

    def test_locality_and_explicit_coordinates_without_inventing_street_positions(self):
        places = [{'name': 'Igea', 'lat': 42.0677, 'lon': -2.0117}, {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038}]
        self.assertEqual(resolve_local('Igea, La Rioja', places)['precision'], 'locality')
        self.assertIsNone(resolve_local('Calle Mayor 4, Madrid', places))
        self.assertIsNone(resolve_local('Igea o Madrid', places))
        self.assertEqual(resolve_local('42.0750, -2.0240', places)['lat'], 42.075)
        self.assertIsNone(resolve_local('90.000, 180.000', places))

    def test_negations_do_not_confuse_uncontrolled_fire_with_false_alarm(self):
        self.assertTrue(is_fire({'emergencia': 'Incendio no controlado'}))
        self.assertTrue(is_fire({'emergencia': 'Fuego sin control'}))
        self.assertFalse(is_fire({'emergencia': 'No hay incendio'}))
        self.assertFalse(is_fire({'emergencia': 'Incendio descartado'}))

    def test_match_uses_footprint_not_only_centroid(self):
        incident = {'id': 'a', 'lat': 40, 'lon': -3, 'footprint': {'type': 'Polygon', 'coordinates': [[[-3,40],[-2.9,40],[-2.9,40.01],[-3,40.01],[-3,40]]]}}
        self.assertEqual(match_incident({'lat': 40.005, 'lon': -2.89}, [incident]), 'a')
        self.assertIsNone(match_incident({'lat': 42, 'lon': -2.89}, [incident]))

    def test_new_demo_is_empty_and_old_browser_credentials_do_not_work(self):
        db = Mock()
        bridge = DemoBridge(db, provider=Mock(), resolver=Mock())
        token = bridge.open_browser()
        self.assertTrue(bridge.authorized(token))
        other = DemoBridge(db, provider=Mock(), resolver=Mock())
        self.assertNotEqual(bridge.session_id, other.session_id)
        self.assertFalse(other.authorized(token))
        self.assertEqual(other.public_state()['calls'], [])

    def test_automatic_browser_sessions_are_bounded(self):
        bridge = DemoBridge(Mock(), provider=Mock(), resolver=Mock())
        for _ in range(64):
            self.assertTrue(bridge.authorized(bridge.open_browser()))
        with self.assertRaises(PermissionError):
            bridge.open_browser()

    def test_report_updates_are_idempotent_and_corrections_replace_evidence(self):
        resolver = Mock(return_value={'lat':42.0677,'lon':-2.0117,'label':'Igea','precision':'locality','source':'local'})
        bridge = DemoBridge(Mock(), provider=Mock(), resolver=resolver)
        bridge.register('00000000-0000-4000-8000-000000000001')
        run = next(iter(bridge.calls))
        bridge.accept(run, [message()])
        version = bridge.version
        bridge.accept(run, [message()])
        self.assertEqual(bridge.version, version)
        self.assertEqual(resolver.call_count, 1)
        self.assertEqual(bridge.calls[run]['state'], 'located')
        bridge.accept(run, [message(), message(emergency='No hay fuego, falsa alarma')])
        self.assertEqual(bridge.calls[run]['state'], 'not_fire')
        self.assertGreater(bridge.version, version)

    def test_ambiguous_location_waits_and_foreign_runs_are_rejected(self):
        bridge = DemoBridge(Mock(), provider=Mock(), resolver=Mock(return_value=None))
        run = '00000000-0000-4000-8000-000000000001'
        bridge.register(run)
        bridge.accept(run, [message('Calle Mayor 4')])
        self.assertEqual(bridge.calls[run]['state'], 'needs_location')
        with self.assertRaises(KeyError):
            bridge.accept('otro-run', [message()])

    def test_demo_confirmation_does_not_mutate_nasa_records(self):
        from app import Store
        original = Store(offline=True)
        item = dict(original.incidents[0])
        resolver = Mock(return_value={'lat':item['lat'],'lon':item['lon'],'label':'Igea','precision':'locality','source':'local'})
        bridge = DemoBridge(Mock(), provider=Mock(), resolver=resolver)
        run = '00000000-0000-4000-8000-000000000001'
        bridge.register(run)
        bridge.accept(run, [message()])
        rendered = bridge.overlay([item], dict(original.weather), datetime.now(timezone.utc))
        self.assertEqual(rendered[0]['confirmation']['status'], 'confirmed')
        self.assertTrue(rendered[0]['confirmation']['demo'])
        self.assertNotIn('confirmation', item)
        self.assertEqual(len(rendered), 1)
        fresh = DemoBridge(Mock(), provider=Mock(), resolver=resolver)
        self.assertNotIn('confirmation', fresh.overlay([item], dict(original.weather), datetime.now(timezone.utc))[0])


class PublishTests(unittest.TestCase):
    def test_tunnel_environment_excludes_provider_and_cloudflare_credentials(self):
        import io
        import os
        from unittest.mock import patch
        from urllib.error import HTTPError
        from demo import ROOT, publish
        process = Mock(stdout=[], pid=12345)
        process.wait.return_value = 0
        responses = [io.BytesIO(b'{"integrated":true,"configured":true}'), HTTPError('http://127.0.0.1:8112/api/data', 404, 'Not Found', {}, None)]
        environment = {'PATH': '/usr/bin', 'HAPPYROBOT_API_KEY': 'fixture', 'TUNNEL_TOKEN': 'fixture', 'CLOUDFLARE_API_TOKEN': 'fixture'}
        with patch.dict(os.environ, environment, clear=True), patch('demo.urlopen', side_effect=responses), patch('pathlib.Path.is_file', return_value=True), patch('pathlib.Path.exists', return_value=False), patch('signal.signal'), patch('subprocess.Popen', return_value=process) as popen:
            publish()
        self.assertEqual(popen.call_args.kwargs['env'], {'PATH': '/usr/bin', 'HOME': str(ROOT / '.local/cloudflared')})
        self.assertEqual(popen.call_args.args[0][-1], 'http://127.0.0.1:8112')
        process.terminate.assert_called_once()


class DemoHTTPTests(unittest.TestCase):
    def test_mobile_isolation_ownership_and_map_update(self):
        import json
        import threading
        from http.server import ThreadingHTTPServer
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        from app import Handler, MobileHandler, Store

        store = Store(offline=True)
        provider = Mock(ready=True)
        run = '00000000-0000-4000-8000-000000000099'
        provider.create.return_value = {'run_id': run, 'token': 'fixture', 'url': 'wss://example.invalid', 'room_name': 'fixture'}
        provider.messages.return_value = [message()]
        resolver = Mock(return_value={'lat':42.0677,'lon':-2.0117,'label':'Igea','precision':'locality','source':'local'})
        store.demo = DemoBridge(Mock(), provider=provider, resolver=resolver)
        class Operator(Handler):
            pass
        class Phone(MobileHandler):
            pass
        Operator.store = Phone.store = store
        with ThreadingHTTPServer(('127.0.0.1', 0), Operator) as operator, ThreadingHTTPServer(('127.0.0.1', 0), Phone) as phone:
            threads = [threading.Thread(target=server.serve_forever) for server in (operator, phone)]
            for thread in threads:
                thread.start()
            base = f'http://127.0.0.1:{phone.server_port}'
            desktop = f'http://127.0.0.1:{operator.server_port}'
            def request(path, body=None, cookie='', origin=None):
                headers = {'Cookie': cookie}
                if body is not None:
                    headers['Content-Type'] = 'application/json'
                if origin:
                    headers['Origin'] = origin
                return urlopen(Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers), timeout=5)
            try:
                for path in ['/api/data', '/api/demo/setup', '/schema.sql', '/112/../demo.py']:
                    with self.assertRaises(HTTPError) as error:
                        request(path)
                    self.assertEqual(error.exception.code, 404)
                    error.exception.close()
                with self.assertRaises(HTTPError) as error:
                    request('/112/api/call', {})
                self.assertEqual(error.exception.code, 403)
                error.exception.close()
                provider.create.assert_not_called()
                with self.assertRaises(HTTPError) as error:
                    request('/112/api/session', {}, origin='https://elsewhere.invalid')
                self.assertEqual(error.exception.code, 403)
                error.exception.close()
                with request('/112/api/session', {}, origin=base) as response:
                    self.assertTrue(json.load(response)['ready'])
                    cookie = response.headers['Set-Cookie'].split(';', 1)[0]
                    self.assertIn('HttpOnly', response.headers['Set-Cookie'])
                with request('/112/api/call', {}, cookie) as response:
                    self.assertEqual(json.load(response)['run_id'], run)
                with request('/112/api/brief?run_id=' + run, cookie=cookie) as response:
                    self.assertEqual(json.load(response)['status'], 'waiting')
                with self.assertRaises(HTTPError) as error:
                    request('/112/api/brief?run_id=' + run)
                self.assertEqual(error.exception.code, 403)
                error.exception.close()
                store.demo.poll_once()
                with urlopen(desktop + '/api/data') as response:
                    incidents = json.load(response)['incidents']
                confirmed = [i for i in incidents if i.get('demo_report')]
                self.assertEqual(len(confirmed), 1)
                self.assertEqual(confirmed[0]['name'], 'Igea')
                self.assertTrue(confirmed[0]['confirmation']['demo'])
                resolver.return_value = {'lat':40.4168,'lon':-3.7038,'label':'Madrid','precision':'locality','source':'local'}
                store.demo.accept(run, [message('Madrid')])
                with urlopen(desktop + '/api/data') as response:
                    incidents = json.load(response)['incidents']
                new = [i for i in incidents if i.get('source_kind') == 'call']
                self.assertEqual(len(new), 1)
                self.assertEqual(new[0]['observations'], 0)
                self.assertIsNone(new[0]['footprint_ha'])
                self.assertFalse(next(i for i in incidents if i['name'] == 'Igea')['confirmation'].get('demo', False))
            finally:
                for server in (operator, phone):
                    server.shutdown()
                for thread in threads:
                    thread.join()


if __name__ == '__main__':
    unittest.main()
