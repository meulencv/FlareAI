import threading
import time
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from demo import DemoBridge, LocationResolver, extract_report, extract_part, is_fire, match_incident, resolve_local, select_location_candidate


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
        self.assertEqual(resolve_local('Igea', places)['precision'], 'locality')
        self.assertIsNone(resolve_local('Calle Mayor 4, Madrid', places))
        self.assertIsNone(resolve_local('Igea o Madrid', places))
        self.assertEqual(resolve_local('42.0750, -2.0240', places)['lat'], 42.075)
        self.assertIsNone(resolve_local('90.000, 180.000', places))

    def test_specific_places_are_not_reduced_to_the_city(self):
        places = [{'name': 'Barcelona', 'lat': 41.38, 'lon': 2.17}]
        for query in ['Carrer Mallorca 401, Barcelona', 'Sagrada Familia, Barcelona', 'Parc de la Ciutadella Barcelona', 'Barcelona calle Balmes 10']:
            self.assertIsNone(resolve_local(query, places))
        good = {'id': 'a', 'type': 'portal', 'address': 'CALLE MALLORCA 401, Barcelona', 'muni': 'Barcelona', 'lat': 41.403, 'lng': 2.174}
        bad = {**good, 'id': 'b', 'address': 'CALLE MALLORCA 404, Barcelona'}
        self.assertEqual(select_location_candidate('Carrer de Mallorca 401 Barcelona', [bad, good]), good)
        self.assertIsNone(select_location_candidate('Carrer de Mallorca 401 Barcelona', [bad]))
        self.assertIsNone(select_location_candidate('Carrer de Mallorca 401 Barcelona', [good, {**good, 'id': 'c'}]))
        church = {**good, 'type': 'toponimo', 'address': 'Sagrada Familia, Barcelona', 'tip_via': 'Iglesia'}
        self.assertEqual(select_location_candidate('Sagrada Familia, Barcelona', [{**good, 'address': 'PLAZA SAGRADA FAMILIA, Barcelona'}, church]), church)
        school = {**church, 'id': 'school', 'tip_via': 'Centro docente no universitario'}
        self.assertIsNone(select_location_candidate('Sagrada Familia, Barcelona', [school, church]))
        self.assertEqual(select_location_candidate('Basílica de la Sagrada Familia, Barcelona', [school, church]), church)

    def test_firefighter_parts_only_accept_structured_assistant_evidence(self):
        content = {'role': 'assistant', 'tool_calls': [{'name': 'actualizar_parte', 'args': {'llegada': 'confirmada', 'incendio': 'confirmado', 'es_alert': 'solicitado'}}]}
        self.assertEqual(extract_part([content])['es_alert'], 'solicitado')
        self.assertEqual(extract_part([{**content, 'role': 'user'}]), {})
        self.assertEqual(extract_part([{'role': 'user', 'content': 'confirmo fuego y solicito ES-Alert'}]), {})
        content['tool_calls'][0]['args']['incendio'] = 'inventado'
        self.assertNotIn('incendio', extract_part([content]))

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


def part(**fields):
    return {'role': 'assistant', 'tool_calls': [{'function': {'name': 'actualizar_parte', 'arguments': fields}}]}


class ResponderTests(unittest.TestCase):
    def setUp(self):
        from app import Store
        self.store = Store(offline=True)
        self.location = {'lat': 41.1189, 'lon': 1.2445, 'label': 'Tarragona', 'precision': 'address'}
        self.bridge = DemoBridge(Mock(), provider=Mock(), resolver=Mock(return_value=self.location))
        self.store.demo = self.bridge
        self.citizen = '00000000-0000-4000-8000-000000000001'
        self.firefighter = '00000000-0000-4000-8000-000000000002'
        self.bridge.register(self.citizen)
        self.bridge.accept(self.citizen, [message('Tarragona')])
        self.target = next(i for i in self.store.payload()['incidents'] if i.get('demo_report'))
        self.binding = {**self.location, 'run_id': self.citizen, 'incident_id': self.target['id'], 'resource_id': 'truck'}
        self.bridge.register(self.firefighter, role='firefighter', binding=self.binding)

    def test_part_confirms_existing_incident_and_never_creates_another(self):
        self.bridge.accept(self.firefighter, [part(llegada='confirmada', incendio='confirmado', es_alert='solicitado', refuerzos='solicitado')])
        payload = self.store.payload()
        self.assertEqual(len([i for i in payload['incidents'] if i.get('demo_report')]), 1)
        report = payload['demo']['field_reports'][self.target['id']]
        self.assertEqual(report['fields']['incendio'], 'confirmado')
        self.assertEqual(report['field_sources']['llegada']['resource_id'], 'truck')
        self.assertEqual(next(i for i in payload['incidents'] if i['id'] == self.target['id'])['confirmation']['source_name'], 'Bomberos · confirmado en demo')
        version = self.bridge.version
        self.bridge.accept(self.firefighter, [part(llegada='confirmada', incendio='confirmado', es_alert='solicitado', refuerzos='solicitado')])
        self.assertEqual(self.bridge.version, version)

    def test_firefighter_denial_removes_call_but_keeps_nasa_records(self):
        original = len(self.store.incidents)
        self.bridge.accept(self.firefighter, [part(incendio='descartado')])
        payload = self.store.payload()
        self.assertFalse(any(i.get('source_kind') == 'call' for i in payload['incidents']))
        self.assertEqual(len(payload['incidents']), original)
        self.assertEqual(payload['demo']['field_reports'][self.target['id']]['fields']['incendio'], 'descartado')

    def test_old_confirmation_is_not_resurrected_by_notes_from_another_unit(self):
        self.bridge.accept(self.firefighter, [part(incendio='confirmado')])
        second = '00000000-0000-4000-8000-000000000003'
        self.bridge.register(second, role='firefighter', binding={**self.binding, 'resource_id': 'other'})
        self.bridge.accept(second, [part(incendio='descartado')])
        self.bridge.accept(self.firefighter, [part(incendio='confirmado'), part(detalle='Estamos regresando')])
        payload = self.store.payload()
        self.assertEqual(payload['demo']['field_reports'][self.target['id']]['fields']['incendio'], 'descartado')
        self.assertFalse(any(i.get('source_kind') == 'call' for i in payload['incidents']))

    def test_correction_of_civilian_location_invalidates_previous_site_part(self):
        self.bridge.accept(self.firefighter, [part(incendio='descartado')])
        self.bridge.resolver.return_value = {**self.location, 'lat': 42, 'label': 'Otra ubicación'}
        self.bridge.accept(self.citizen, [message('Otra ubicación')])
        payload = self.store.payload()
        self.assertEqual(payload['demo']['field_reports'], {})
        self.assertTrue(any(i.get('source_kind') == 'call' for i in payload['incidents']))

    def test_citizen_cannot_submit_a_firefighter_part_or_bind_an_invented_incident(self):
        self.bridge.accept(self.citizen, [part(incendio='descartado', es_alert='solicitado')])
        self.assertEqual(self.store.payload()['demo']['field_reports'], {})
        owner = self.bridge.open_browser()
        with self.assertRaises(ValueError):
            self.bridge.create_call(owner, 'firefighter', {'run_id': 'invented'})
        self.bridge.provider.create.assert_not_called()

    def test_precise_address_is_not_replaced_by_the_nearest_nasa_centroid(self):
        self.assertEqual(self.target['lat'], self.location['lat'])
        self.assertEqual(self.target['lon'], self.location['lon'])
        self.assertEqual(self.target['source_kind'], 'call')
        self.assertEqual(self.target['observations'], 0)


class ConcurrentCallTests(unittest.TestCase):
    def setUp(self):
        self.provider = Mock(ready=True, responder_ready=True)
        self.bridge = DemoBridge(Mock(), provider=self.provider, resolver=Mock(return_value={'lat': 41.38, 'lon': 2.17, 'label': 'Barcelona', 'precision': 'address'}))
        self.addCleanup(self.bridge.close)

    def test_four_citizens_and_four_firefighters_can_start_together(self):
        citizen = str(uuid.uuid4())
        self.bridge.register(citizen)
        self.bridge.accept(citizen, [message('Barcelona')])
        barrier = threading.Barrier(8)
        def create(*args):
            barrier.wait(timeout=3)
            run = str(uuid.uuid4())
            return {'run_id': run, 'token': 'fixture', 'url': 'wss://example.invalid', 'room_name': run}
        self.provider.create.side_effect = create
        owners = [self.bridge.open_browser() for _ in range(8)]
        def start(index):
            role = 'citizen' if index < 4 else 'firefighter'
            return self.bridge.create_call(owners[index], role, {'run_id': citizen})['run_id']
        with ThreadPoolExecutor(max_workers=8) as executor:
            runs = list(executor.map(start, range(8)))
        self.assertEqual(len(set(runs)), 8)
        self.assertEqual(self.bridge.starting, 0)
        for index, run in enumerate(runs):
            self.assertEqual(self.bridge.brief(run, owners[index])['role'], 'citizen' if index < 4 else 'firefighter')
            with self.assertRaises(PermissionError):
                self.bridge.brief(run, owners[(index + 1) % 8])

    def test_slow_poll_does_not_block_other_updates_or_overlap_same_run(self):
        slow, fast = str(uuid.uuid4()), str(uuid.uuid4())
        started, release, updated = threading.Event(), threading.Event(), threading.Event()
        self.bridge.register(slow)
        self.bridge.register(fast)
        def messages(run):
            if run == slow:
                started.set()
                release.wait(timeout=4)
            return [message(run)]
        self.provider.messages.side_effect = messages
        original = self.bridge.accept
        def accept(run, messages):
            original(run, messages)
            if run == fast:
                updated.set()
        with patch.object(self.bridge, 'accept', side_effect=accept):
            try:
                self.bridge.poll_once(wait=False)
                self.assertTrue(started.wait(1))
                self.assertTrue(updated.wait(1))
                self.assertEqual(self.bridge.calls[fast]['state'], 'located')
                self.bridge.poll_once(wait=False)
                self.assertEqual(sum(c.args[0] == slow for c in self.provider.messages.call_args_list), 1)
            finally:
                release.set()

    def test_hangup_during_geocoding_is_not_undone_by_late_result(self):
        owner = self.bridge.open_browser()
        run = str(uuid.uuid4())
        self.bridge.register(run, owner)
        started, release = threading.Event(), threading.Event()
        location = self.bridge.resolver.return_value
        def resolve(query):
            started.set()
            release.wait(timeout=3)
            return location
        self.bridge.resolver.side_effect = resolve
        with ThreadPoolExecutor(max_workers=1) as executor:
            task = executor.submit(self.bridge.accept, run, [message()])
            try:
                self.assertTrue(started.wait(1))
                self.bridge.stop(run, owner)
            finally:
                release.set()
            task.result()
        self.assertTrue(self.bridge.calls[run]['ended'])
        self.assertLess(self.bridge.calls[run]['poll_until'] - time.monotonic(), 21)

    def test_poll_failure_is_isolated_and_finished_calls_release_capacity(self):
        self.provider.create.side_effect = lambda *args: {'run_id': str(uuid.uuid4()), 'token': 'fixture', 'url': 'wss://example.invalid', 'room_name': 'fixture'}
        owner = self.bridge.open_browser()
        for _ in range(24):
            run = self.bridge.create_call(owner)['run_id']
            self.bridge.stop(run, owner)
        good = self.bridge.create_call(owner)['run_id']
        def messages(run):
            if run != good:
                raise OSError('fixture')
            return [message()]
        self.provider.messages.side_effect = messages
        self.bridge.poll_once()
        self.assertEqual(self.bridge.calls[good]['state'], 'located')
        self.assertTrue(self.bridge.calls[run]['error'])

    def test_reservations_enforce_capacity_and_failures_release_them(self):
        from demo import MAX_ACTIVE_CALLS
        owner = self.bridge.open_browser()
        self.bridge.starting = MAX_ACTIVE_CALLS
        with self.assertRaises(RuntimeError):
            self.bridge.create_call(owner)
        self.provider.create.assert_not_called()
        self.bridge.starting = 0
        self.provider.create.side_effect = OSError('fixture')
        with self.assertRaises(OSError):
            self.bridge.create_call(owner)
        self.assertEqual(self.bridge.starting, 0)


class GeocodingTests(unittest.TestCase):
    def setUp(self):
        db = Mock()
        self.places = [{'name': 'Barcelona', 'lat': 41.3874, 'lon': 2.1686}, {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038}]
        db.get_asset.side_effect = lambda name: {'data': {'places': self.places} if name.endswith('places.json') else {'geometry': {'type': 'Polygon', 'coordinates': [[[-19,27],[5,27],[5,44.5],[-19,44.5],[-19,27]]]}}}
        self.resolver = LocationResolver(db)

    def test_osm_address_wins_over_municipality_and_is_cached(self):
        candidate = {'lat': '41.4031876', 'lon': '2.1748235', 'osm_type': 'node', 'osm_id': 1, 'category': 'place', 'type': 'house', 'name': '',
                     'display_name': '401, Carrer de Mallorca, Barcelona, España', 'address': {'house_number': '401', 'road': 'Carrer de Mallorca', 'city': 'Barcelona', 'country_code': 'es'}}
        with patch.object(self.resolver, 'osm_fetch', return_value=[candidate]) as osm, patch.object(self.resolver, 'remote') as ign:
            result = self.resolver('Carrer de Mallorca 401 Barcelona')
            self.assertEqual(result['precision'], 'address')
            self.assertEqual(result['lat'], 41.4031876)
            self.assertEqual(result['source'], 'OpenStreetMap / Nominatim')
            self.assertEqual(self.resolver('Carrer de Mallorca 401 Barcelona'), result)
            self.assertEqual(osm.call_count, 1)
            ign.assert_not_called()

    def test_failed_address_falls_back_to_explicit_city_not_another_house_number(self):
        candidate = {'lat': '41.40', 'lon': '2.17', 'category': 'place', 'type': 'house', 'display_name': '404, Carrer de Mallorca, Barcelona',
                     'address': {'house_number': '404', 'road': 'Carrer de Mallorca', 'city': 'Barcelona', 'country_code': 'es'}}
        with patch.object(self.resolver, 'osm_fetch', return_value=[candidate]), patch.object(self.resolver, 'remote', return_value=None):
            result = self.resolver('Carrer de Mallorca 99999 Barcelona')
        self.assertEqual(result['precision'], 'locality')
        self.assertTrue(result['approximate'])
        self.assertEqual(result['lat'], self.places[0]['lat'])
        self.assertEqual(result['query'], 'Carrer de Mallorca 99999 Barcelona')
        self.assertIn('reason', result)

    def test_ign_is_used_if_osm_cannot_resolve_precise_address(self):
        precise = {'lat': 41.403, 'lon': 2.174, 'label': 'Mallorca 401 Barcelona', 'precision': 'address', 'source': 'CartoCiudad / IGN'}
        with patch.object(self.resolver, 'osm_fetch', return_value=[]), patch.object(self.resolver, 'remote', return_value=precise):
            self.assertEqual(self.resolver('Carrer Mallorca 401 Barcelona')['precision'], 'address')

    def test_unknown_city_can_be_resolved_by_osm_and_missing_location_is_not_invented(self):
        candidate = {'lat': '41.1189', 'lon': '1.2445', 'category': 'boundary', 'type': 'administrative', 'addresstype': 'city',
                     'name': 'Tarragona', 'display_name': 'Tarragona, Cataluña, España', 'address': {'city': 'Tarragona', 'country_code': 'es'}}
        with patch.object(self.resolver, 'osm_fetch', side_effect=lambda query: [candidate] if query == 'Tarragona' else []), patch.object(self.resolver, 'remote', return_value=None):
            self.assertEqual(self.resolver('Calle inventada 9, Tarragona')['precision'], 'locality')
            self.assertIsNone(self.resolver('No sé dónde estoy'))
            self.assertIsNone(self.resolver('Calle Barcelona'))

    def test_osm_requests_are_throttled_and_persistently_cached(self):
        import io
        assets = {}
        self.resolver.db.get_asset.side_effect = lambda key: assets.get(key)
        self.resolver.db.asset.side_effect = lambda key, kind, data: assets.update({key: {'data': data}})
        with patch('demo.urlopen', side_effect=lambda *a, **k: io.BytesIO(b'[]')) as network, patch('demo.time.sleep') as sleep, patch('demo.time.monotonic', return_value=10), patch.object(LocationResolver, 'osm_next_request', 0):
            self.resolver.osm_fetch('Barcelona')
            self.resolver.osm_fetch('Madrid')
            self.resolver.osm_fetch('Barcelona')
        self.assertEqual(network.call_count, 2)
        self.assertAlmostEqual(sleep.call_args_list[1].args[0], 1.05)
        self.assertEqual(len(assets), 2)

    def test_ambiguous_pois_do_not_invent_an_exact_point(self):
        from demo import select_osm_location
        candidate = {'lat': '41.4', 'lon': '2.17', 'category': 'amenity', 'type': 'school', 'name': 'Sagrada Familia',
                     'display_name': 'Sagrada Familia, Barcelona', 'address': {'city': 'Barcelona', 'country_code': 'es'}}
        self.assertIsNone(select_osm_location('Sagrada Familia Barcelona', [candidate, {**candidate, 'lat': '41.45'}]))
        self.assertIsNone(select_osm_location('Sagrada Familia Barcelona', [{**candidate, 'address': {'country_code': 'fr'}}]))

    def test_plain_city_does_not_need_network(self):
        with patch.object(self.resolver, 'osm_fetch') as osm:
            self.assertEqual(self.resolver('Estoy en Barcelona')['label'], 'Barcelona')
            osm.assert_not_called()


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
    def test_public_url_ignores_cloudflare_service_hosts(self):
        import re
        pattern = re.compile(r'https://(?!api\.)[a-z0-9]+(?:-[a-z0-9]+)+\.trycloudflare\.com')
        for noise in ['Requesting new quick Tunnel on trycloudflare.com...',
                      'ERR Request failed error="lookup api.trycloudflare.com" url=https://api.trycloudflare.com/tunnel']:
            self.assertIsNone(pattern.search(noise), noise)
        assigned = '|  https://skills-islands-plastic-changelog.trycloudflare.com   |'
        self.assertEqual(pattern.search(assigned).group(0), 'https://skills-islands-plastic-changelog.trycloudflare.com')

    def test_mobile_isolation_ownership_and_map_update(self):
        import json
        import threading
        from http.server import ThreadingHTTPServer
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        from app import Handler, MobileHandler, Store

        store = Store(offline=True)
        from app import ROOT
        store.fires = json.loads((ROOT / 'examples/firms.geojson').read_text())
        store.weather = json.loads((ROOT / 'examples/weather.json').read_text())
        store.incidents = json.loads((ROOT / 'examples/combined.json').read_text())['incidents']
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
                for path in ['/api/data', '/api/demo/setup', '/api/director', '/director.py', '/schema.sql', '/112/../demo.py']:
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
                for path in ['/112/api/incidents', '/112/api/alerts']:
                    with self.assertRaises(HTTPError) as unauthorized:
                        request(path)
                    self.assertEqual(unauthorized.exception.code, 403)
                    unauthorized.exception.close()
                with request('/112/alerts/') as response:
                    self.assertIn(b'SIMULACRO', response.read())
                with request('/112/api/session', {}, origin=base) as response:
                    self.assertTrue(json.load(response)['ready'])
                    cookie = response.headers['Set-Cookie'].split(';', 1)[0]
                    self.assertIn('HttpOnly', response.headers['Set-Cookie'])
                with request('/112/api/alerts', cookie=cookie) as response:
                    self.assertEqual(json.load(response)['events'], [])
                for invalid in [{'number': '999'}, {'number': '123', 'incident_id': 'invented'}]:
                    with self.assertRaises(HTTPError) as rejected:
                        request('/112/api/call', invalid, cookie)
                    self.assertEqual(rejected.exception.code, 400)
                    rejected.exception.close()
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
