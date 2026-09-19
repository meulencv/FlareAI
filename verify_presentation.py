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
    for elapsed in (0, 46, 72, 118):
        director.scene.evolve(now + elapsed)
    assert director.scene.data['incidents'][identifier]['phase'] == 'releasing'
    director.scene.maintenance()
    assert all(a['status'] == 'returning' for a in director.state['assignments'].values())
    for assignment in director.state['assignments'].values():
        assignment['started_at'] -= assignment['travel_seconds'] + 1
    director.advance()
    director.scene.evolve(now + 120)
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
                expect(page.locator('.witness-marker')).to_have_count(25)
                expect(page.locator('.witness-marker.real-call')).to_have_count(1)
                expect(page.locator('.witness-marker.credibility-uncertain')).to_have_count(24)
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
                expect(page.locator('.witness-marker.has-report')).to_have_count(1, timeout=15000)
                page.locator('#brain-toggle').click()
                expect(page.locator('#brain-view')).to_be_visible()
                expect(page.locator('.brain-notes button')).to_have_count(1)
                page.locator('.brain-notes button').click()
                expect(page.locator('.brain-article')).to_contain_text('Créditos de carbono')
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
            print('Presentación verificada: 25 avisos, refuerzos, hospital, cierre, PDF, cerebro y 112 sin 123. Voz y LLM fixtures; rutas reales cacheadas; sin llamadas reales.')
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
    args = parser.parse_args()
    if args.phone:
        phone_check()
    elif args.cloud:
        cloud_check()
    else:
        for _ in range(args.cycles):
            main()
