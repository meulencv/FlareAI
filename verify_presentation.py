from __future__ import annotations

import json
import tempfile
import threading
import time
import uuid
from copy import deepcopy
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock, patch

from playwright.sync_api import expect, sync_playwright

from app import Handler, ROOT, Store
from database import Database
from demo import DemoBridge
from director import Director
from local_routes import LocalRouter
from verify_director_ui import instrument_map


class PresentationFixtureDB(Database):
    dynamic_cloud = True

    def __init__(self):
        super().__init__()
        self.docs = {}
        self.states = {}
        self.calls = {}

    def setting(self, key, value=None):
        return {}

    def start_demo(self, identifier):
        return None

    def save_demo_call(self, session_id, run_id, data):
        self.calls[run_id] = deepcopy(data)

    def save_director(self, session_id, state):
        self.states[session_id] = deepcopy(state)

    def director_history(self, session_id):
        return {'session_id': session_id, 'events': deepcopy(self.states.get(session_id, {}).get('events', []))}

    def document(self, identifier, kind='', value=None, session_id=None):
        if value is not None:
            self.docs[identifier] = {'id': identifier, 'kind': kind, 'session_id': session_id, 'data': deepcopy(value)}
        return deepcopy(self.docs.get(identifier, {}).get('data'))

    def documents(self, kind, session_id=None):
        return [deepcopy(v) for v in self.docs.values() if v['kind'] == kind and (session_id is None or v['session_id'] == session_id)]

    def cached(self, key, ttl, load):
        return load()

    def heartbeat(self, session_id):
        return None


def fixture_store():
    db = PresentationFixtureDB()
    store = Store(offline=True, database=db, presentation=True)
    store.fires = json.loads((ROOT / 'examples/firms.geojson').read_text())
    store.weather = json.loads((ROOT / 'examples/weather.json').read_text())
    store.incidents = json.loads((ROOT / 'examples/combined.json').read_text())['incidents']
    provider = Mock(ready=True, responder_ready=False)
    store.demo = DemoBridge(db, provider=provider, resolver=lambda _: {
        'lat': 41.4035, 'lon': 2.1744, 'label': 'Sagrada Familia, Barcelona · fixture', 'precision': 'poi', 'source': 'fixture'})
    director = store.director = Director(store, planner=Mock(ready=False), router=LocalRouter(db, offline=True))
    director.scene.data['automatic'] = False
    run = str(uuid.uuid4())
    store.demo.register(run)
    store.demo.accept(run, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_ficha', 'args': {
        'ubicacion': 'Sagrada Familia, Barcelona', 'emergencia': 'Incendio', 'riesgos': 'Humo y dos heridos', 'personas': 'Dos heridos'}}]}])
    director.scene.observe(store.payload())
    director.operations.tick(store.payload())
    identifier = next(iter(director.operations.records))
    for testimony in director.operations.waves[identifier]:
        testimony['at'] -= 120
    director.operations.records[identifier]['ready_at'] -= 120
    context = director.context(store.payload())
    trucks = [r for r in context['resources'] if r['kind'] == 'fire_engine'][:2]
    plan = {'revision': context['revision'], 'summary': 'Plan fixture: dos bomberos tras contraste',
            'assessments': [{'incident_id': identifier, 'summary': 'Evaluación fixture; los testimonios no son evidencia independiente.',
                            'testimonies': [{'id': t['id'], 'status': 'uncertain', 'reason': 'Clasificación fixture, no salida de LLM'} for t in director.operations.waves[identifier]]}],
            'actions': [{'type': 'dispatch', 'incident_id': identifier, 'resource_id': r['id'], 'reason': 'Prueba con ruta real cacheada'} for r in trucks]}
    actions = director.prepare(plan, context)
    assert not any(a.get('route_error') for a in actions)
    director.apply(plan, actions, 'fixture-director')
    director.save()
    return store, identifier, run


def complete_fixture(store, identifier, run):
    director = store.director
    for assignment in director.state['assignments'].values():
        assignment['started_at'] -= assignment['travel_seconds'] + 1
    director.advance()
    director.operations.outbound.last_poll = 0
    director.operations.outbound.tick(store.payload())
    assert director.operations.outbound.jobs[identifier]['status'] == 'disabled'
    incident = next(i for i in store.payload()['incidents'] if i['id'] == identifier)
    responder = str(uuid.uuid4())
    store.demo.register(responder, role='firefighter', binding={**incident['demo_report']['location'], 'run_id': run, 'incident_id': identifier})
    store.demo.accept(responder, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_parte', 'args': {
        'incendio': 'confirmado', 'evolucion': 'estable', 'ambulancias': '1', 'bomberos': '1', 'helicoptero': 'solicitado',
        'personas_asistidas': '2', 'es_alert': 'no_solicitado', 'detalle': 'Parte fixture, sin llamada telefónica real'}}]}])
    director.operations.outbound.jobs[identifier]['status'] = 'completed'
    director.scene.observe(store.payload())
    director.operations.reinforce(store.payload())
    requests = director.operations.records[identifier]['requests']
    assert requests and all(r['fulfilled'] == r['quantity'] for r in requests.values()), requests
    for assignment in director.state['assignments'].values():
        assignment['started_at'] -= assignment['travel_seconds'] + 1
    director.advance()
    for assignment in director.state['assignments'].values():
        assignment['arrived_at'] = time.time() - 20
    director.scene.maintenance()
    ambulance = next(a for a in director.state['assignments'].values() if a['resource']['kind'] == 'ambulance')
    assert ambulance['status'] == 'transporting'
    ambulance['started_at'] -= ambulance['travel_seconds'] + 1
    director.advance()
    assert ambulance.get('patient_delivered')
    now = time.time()
    for elapsed in range(1, 181):
        director.scene.evolve(now + elapsed)
        if director.scene.data['incidents'][identifier]['phase'] == 'releasing':
            break
    assert director.scene.data['incidents'][identifier]['phase'] == 'releasing'
    director.scene.maintenance()
    assert all(a['status'] == 'returning' for a in director.state['assignments'].values())
    assert all(5 <= a['travel_seconds'] <= 15 for a in director.state['assignments'].values())
    director.operations.tick(store.payload())
    assert director.operations.records[identifier]['reported']
    assert director.state['assignments'], 'El informe debe estar disponible antes de llegar a base'
    for assignment in director.state['assignments'].values():
        assignment['started_at'] -= assignment['travel_seconds'] + 1
    director.advance()
    director.scene.evolve(now + elapsed + 1)
    assert director.scene.data['incidents'][identifier]['phase'] == 'closed'
    director.save()
    director.operations.tick(store.payload())
    assert director.operations.records[identifier]['reported']
    assert not director.state['notifications']


def main():
    store, identifier, run = fixture_store()
    server = None
    try:
        with tempfile.TemporaryDirectory() as temporary, patch('reports.MEMORY_ROOT', Path(temporary) / 'vault'), patch('reports.REPORT_ROOT', Path(temporary) / 'pdf'):
            class FixtureHandler(Handler):
                pass
            FixtureHandler.store = store
            server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            url = f'http://127.0.0.1:{server.server_port}'
            errors = []
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/app.js', instrument_map)
                page.goto(url)
                assert page.locator('#calls-panel').count() == 0, 'El panel izquierdo de voces se retiró'
                expect(page.locator('.witness-marker')).to_have_count(6)
                expect(page.locator('.witness-marker.real-call')).to_have_count(1)
                expect(page.locator('.witness-marker.simulated.credibility-uncertain')).to_have_count(5)
                expect(page.locator('.threat-surface')).to_have_count(1)
                page.locator('#follow-toggle').click()
                page.evaluate('window.__directorMap.setView([41.4035,2.1744],15,{animate:false})')
                page.wait_for_timeout(600)
                page.locator('.witness-marker.simulated').first.hover()
                expect(page.locator('.witness-tooltip')).to_be_visible()
                expect(page.locator('.witness-tooltip')).to_contain_text('Testigo')
                page.mouse.move(5, 5)
                expect(page.locator('#brain-toggle')).to_be_visible()
                page.screenshot(path=str(ROOT / '.local/presentation-calls.png'))
                complete_fixture(store, identifier, run)
                expect(page.locator('.witness-marker')).to_have_count(0, timeout=15000)
                page.locator('#brain-toggle').click()
                expect(page.locator('#brain-view')).to_be_visible()
                page.locator('.brain-notes button', has_text='Operación ·').click()
                expect(page.locator('.brain-article')).to_contain_text('sin esperar al regreso a base')
                pdf = page.request.get(url + page.locator('.report-download').get_attribute('href'))
                assert pdf.ok and pdf.body().startswith(b'%PDF-1.4')
                assert list((Path(temporary) / 'vault').glob('*.md'))
                page.screenshot(path=str(ROOT / '.local/presentation-brain.png'))
                phone = browser.new_page(viewport={'width': 390, 'height': 844})
                phone.goto(url + '/112/')
                expect(phone.locator('[data-number="123"]')).to_have_count(0)
                expect(phone.locator('[data-number="112"]')).to_be_visible()
                assert not errors, errors
                browser.close()
            print('Presentación verificada: 6 avisos, refuerzos, hospital, retirada inmediata, PDF antes de llegar a base, cerebro y 112 sin 123. Voz y LLM fixtures; rutas reales cacheadas; sin llamadas reales.')
    finally:
        if server:
            server.shutdown()
            server.server_close()
        store.demo.close()


def camera_check():
    from verify_director_ui import verify_evidence

    store, identifier, _ = fixture_store()
    server = None
    try:
        class CameraHandler(Handler):
            pass
        CameraHandler.store = store
        server = ThreadingHTTPServer(('127.0.0.1', 0), CameraHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            verify_evidence(browser, url, store)
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
            errors, requests = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: requests.append(request.url))
            state = {'session_id': 'camera-fixture', 'status': 'watching', 'sequence': 0, 'events': [], 'assignments': {}, 'alerts': {}}
            base = deepcopy(next(iter(store.director.state['assignments'].values())))
            for index, kind in enumerate(['fire_engine', 'ambulance', 'police', 'helicopter']):
                assignment = deepcopy(base)
                lat, lon = 41.40 + index * .01, 2.12 + index * .01
                assignment.update(id=kind, status='transporting' if kind == 'ambulance' else 'enroute',
                                  started_at=time.time(), travel_seconds=1000, route_revision=1)
                assignment['resource'].update(id=kind, kind=kind, lat=lat, lon=lon)
                assignment['route'].update(coordinates=[[lon, lat], [lon + .01, lat + .01]], cumulative_km=[0, 1], distance_km=1)
                state['assignments'][kind] = assignment
            page.route('**/app.js', instrument_map)
            page.route('**/api/director', lambda route: route.fulfill(json=state | {'server_time': time.time()}))
            page.goto(url)
            expect(page.locator('.response-vehicle')).to_have_count(4)

            def event(kind, resource=None):
                state['sequence'] += 1
                message = f'Cámara fixture {state["sequence"]}'
                state['events'].append({'sequence': state['sequence'], 'at': time.time(), 'kind': kind,
                                        'incident_id': identifier, 'resource_id': resource, 'message': message})
                expect(page.locator('#agent-message')).to_have_text(message, timeout=15000)

            for kind in ['fire_engine', 'ambulance', 'police', 'helicopter']:
                event('dispatch' if kind == 'fire_engine' else 'vehicle', kind)
                assignment = state['assignments'][kind]
                expected = [assignment['resource']['lat'], assignment['resource']['lon'], 14 if kind == 'helicopter' else 15.5]
                page.wait_for_function('([lat,lon,zoom]) => { const m=window.__directorMap, c=m.getCenter(); return Math.abs(c.lat-lat)<.00001 && Math.abs(c.lng-lon)<.00001 && m.getZoom()===zoom; }', arg=expected)
            state['assignments']['fire_engine']['status'] = 'returning'
            event('return', 'fire_engine')
            page.wait_for_function('window.__directorMap.getZoom() === 15.5')
            page.locator('#follow-toggle').click()
            before = page.evaluate('[window.__directorMap.getZoom(), window.__directorMap.getCenter()]')
            event('arrived')
            assert page.evaluate('[window.__directorMap.getZoom(), window.__directorMap.getCenter()]') == before
            page.locator('#follow-toggle').click()
            event('arrived')
            page.wait_for_function('Math.abs(window.__directorMap.getCenter().lng - 2.1744) < .01')
            page.set_viewport_size({'width': 390, 'height': 844})
            event('vehicle', 'ambulance')
            expect(page.locator('.response-vehicle.ambulance')).to_have_count(1)
            expect(page.locator('.traffic-canvas, .traffic-breakdown')).to_have_count(0)
            assert not any('/traffic.js' in request or '/api/scenario/roads' in request for request in requests), requests
            assert not errors, errors
            browser.close()
        print('Cámara verificada: avisos, viaje alejar/acercar, cuatro tipos de vehículo, traslado, regreso, llegada, control manual, reanudación y móvil. Sin capa ni consultas de coches; voz/LLM fixtures.')
    finally:
        if server:
            server.shutdown()
            server.server_close()
        store.demo.close()


def editor_check():
    with tempfile.TemporaryDirectory() as temporary, patch('reports.MEMORY_ROOT', Path(temporary) / 'vault'), patch('reports.REPORT_ROOT', Path(temporary) / 'pdf'):
        store, identifier, _ = fixture_store()
        server = None
        try:
            class EditorHandler(Handler):
                pass
            EditorHandler.store = store
            server = ThreadingHTTPServer(('127.0.0.1', 0), EditorHandler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            url = f'http://127.0.0.1:{server.server_port}'
            errors = []
            scene = store.director.scene
            record = scene.data['incidents'][identifier]
            observations = deepcopy(store.incidents)
            routes = {key: deepcopy(a['route']) for key, a in store.director.state['assignments'].items()}
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(url + '/') else route.abort())
                page.goto(url)
                pencil = page.locator('#scenario-edit-toggle')
                expect(pencil).to_be_visible()
                settings = page.locator('#settings-toggle')
                left, right = pencil.bounding_box(), settings.bounding_box()
                assert left['x'] + left['width'] < right['x']
                await_box = page.locator('#scenario-edit-status')
                pencil.click()
                expect(page.locator('#scenario-edit-panel')).to_be_visible()
                page.locator('#scenario-random-cut').click()
                expect(await_box).to_contain_text('Corte creado', timeout=30000)
                assert scene.data['closures']
                changed = [a for key, a in store.director.state['assignments'].items() if a.get('previous_route') == routes[key]]
                assert changed
                for assignment in changed:
                    assert assignment['status'] == 'blocked' or not set(assignment['route']['edge_ids']) & set(scene.data['closures'])
                page.locator('#scenario-edit-wind').focus()
                page.keyboard.press('End')
                expect(await_box).to_contain_text('Cambio aplicado')
                assert record['wind_to'] == 359
                page.locator('#scenario-edit-power').focus()
                page.keyboard.press('Home')
                expect(page.locator('#scenario-edit-power-value')).to_contain_text('Apagar · 100 %')
                expect(page.locator('#scenario-edit-power')).to_be_enabled()
                assert record['fire_power'] == -100
                before = record['radius_km']
                scene.evolve(record['last_tick'] + 10)
                assert record['radius_km'] < before
                page.keyboard.press('End')
                expect(page.locator('#scenario-edit-power-value')).to_contain_text('Avivar · 100 %')
                expect(page.locator('#scenario-edit-power')).to_be_enabled()
                assert record['fire_power'] == 100
                before = record['radius_km']
                scene.evolve(record['last_tick'] + 10)
                assert record['radius_km'] > before
                page.locator('#scenario-edit-normal').click()
                expect(page.locator('#scenario-edit-power-value')).to_contain_text('Evolución normal')
                assert record['fire_power'] == 0
                assert store.incidents == observations
                page.screenshot(path=str(ROOT / '.local/scenario-editor-desktop.png'))
                page.keyboard.press('Escape')
                expect(page.locator('#scenario-edit-panel')).to_be_hidden()
                expect(pencil).to_be_focused()
                settings.click()
                expect(page.locator('#settings-panel')).to_be_visible()
                pencil.click()
                expect(page.locator('#settings-panel')).to_be_hidden()
                settings.click()
                expect(page.locator('#scenario-edit-panel')).to_be_hidden()
                page.set_viewport_size({'width': 390, 'height': 844})
                pencil.click()
                box = page.locator('#scenario-edit-panel').bounding_box()
                assert box['x'] >= 0 and box['x'] + box['width'] <= 390 and box['y'] >= 0
                page.screenshot(path=str(ROOT / '.local/scenario-editor-mobile.png'))
                page.locator('#scenario-edit-close').click()
                expect(page.locator('#scenario-edit-panel')).to_be_hidden()
                with store.director.lock:
                    store.director.state['assignments'] = {}
                pencil.click()
                page.locator('#scenario-random-cut').click()
                expect(await_box).to_contain_text('Hace falta una unidad')
                assert not errors, errors
                browser.close()
            print('Editor verificado: escritorio/móvil, corte con A* local, viento, potencia progresiva, teclado, errores y datos originales intactos. Voz/LLM fixtures, sin llamadas reales.')
        finally:
            if server:
                server.shutdown()
                server.server_close()
            store.demo.close()


def cloud_check():
    from director import Planner, validate_plan
    from twin import TwinDatabase
    store, identifier, _ = fixture_store()
    try:
        director = store.director
        director.state['assignments'] = {}
        director.state['history'] = []
        director.state['events'] = []
        director.operations.records[identifier]['assessment'] = None
        planner = Planner(TwinDatabase())
        context = director.context(store.payload())
        run = planner.start(context)
        deadline = time.monotonic() + 150
        plan = None
        while plan is None and time.monotonic() < deadline:
            plan = planner.poll(run)
            if plan is None:
                time.sleep(2)
        assert plan is not None, 'El agente no entregó plan'
        validate_plan(plan, context)
        assessment = next(a for a in plan.get('assessments', []) if a.get('incident_id') == identifier)
        expected = {t['id'] for t in director.operations.waves[identifier]}
        assert {t['id'] for t in assessment['testimonies']} == expected, 'El agente debe evaluar los cinco testimonios'
        actions = director.prepare(plan, context)
        assert not any(a.get('route_error') for a in actions), actions
        trucks = [a for a in actions if a['type'] == 'dispatch' and director.state['resources'][a['resource_id']]['kind'] == 'fire_engine']
        assert len(trucks) >= 2, 'La operación necesita medios de extinción suficientes'
        assert not any(a['type'] == 'alert' and a.get('mobile_alert') for a in actions), 'Sin parte no hay ES-Alert'
        print(json.dumps({'run_id': run, 'testimonies_evaluated': len(expected), 'fire_engines': len(trucks),
                          'summary': plan['summary'], 'voice': 'fixture; no se ha llamado a ningún teléfono'}, ensure_ascii=False))
    finally:
        store.demo.close()


def phone_check():
    from demo import HappyRobotProvider
    from outbound import OutboundCalls
    from twin import TwinDatabase
    store, identifier, citizen_run = fixture_store()
    cloud = TwinDatabase()
    cloud.start_demo(store.demo.session_id)
    cloud.save_demo_call(store.demo.session_id, citizen_run, store.demo.calls[citizen_run])
    store.db = store.demo.db = store.director.db = store.director.operations.db = cloud
    store.demo.provider = HappyRobotProvider(cloud)
    store.demo.calls[citizen_run]['poll_until'] = 0
    store.allow_outbound = True
    director = store.director
    director.operations.outbound = OutboundCalls(director)
    for assignment in director.state['assignments'].values():
        assignment['started_at'] -= assignment['travel_seconds'] + 10
    director.advance()
    director.save()
    deadline = time.monotonic() + 300
    try:
        while time.monotonic() < deadline:
            director.operations.outbound.tick(store.payload())
            job = director.operations.outbound.jobs.get(identifier, {})
            store.demo.poll_once(wait=True)
            director.operations.reinforce(store.payload())
            if job.get('status') == 'completed':
                fields = store.demo.field_reports.get(identifier, {}).get('fields', {})
                requests = director.operations.records[identifier]['requests']
                print(json.dumps({'run_id': job['run_id'], 'phone': 'real_authorized', 'attempt': job['attempt'],
                    'recorded_fields': sorted(fields), 'requests': requests, 'simulation': True}, ensure_ascii=False), flush=True)
                return
            if job.get('status') in {'uncertain', 'unreachable', 'needs_report', 'disabled'}:
                raise RuntimeError('Prueba detenida sin repetir llamadas: ' + job['status'])
            time.sleep(2)
        raise RuntimeError('Prueba pendiente; no se iniciarán llamadas adicionales')
    finally:
        store.demo.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true', help='Consume una ejecución real del director, nunca llama a un teléfono')
    parser.add_argument('--phone', action='store_true', help='Llama a los contactos reales: requiere autorización específica del usuario')
    parser.add_argument('--cycles', type=int, default=1, choices=range(1, 6), help='Repite solo los ciclos de fixtures, nunca llamadas reales')
    parser.add_argument('--editor', action='store_true', help='Verifica el editor con fixtures y rutas locales, sin llamadas reales')
    parser.add_argument('--camera', action='store_true', help='Verifica seguimiento y ausencia de tráfico con fixtures, sin llamadas reales')
    args = parser.parse_args()
    if args.camera:
        camera_check()
    elif args.editor:
        editor_check()
    elif args.phone:
        phone_check()
    elif args.cloud:
        cloud_check()
    else:
        for _ in range(args.cycles):
            main()
