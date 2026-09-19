from __future__ import annotations

import argparse
import base64
import json
import threading
import time
import uuid
from copy import deepcopy
from http.server import ThreadingHTTPServer

from playwright.sync_api import expect, sync_playwright

from app import ROOT, Handler, Store
from database import Database
from demo import DemoBridge
from director import Director
from local_routes import LocalRouter


class PlannerFixture:
    ready = True

    def start(self, context):
        self.context = context
        return str(uuid.uuid4())

    def poll(self, run_id):
        context = self.context
        incident = context['incidents'][0]
        resource = next(r for r in context['resources'] if r['kind'] == 'fire_engine')
        return {'revision': context['revision'], 'summary': 'Asignando recursos al aviso', 'actions': [
            {'type': 'focus', 'incident_id': incident['id'], 'reason': 'Aviso localizado'},
            {'type': 'context', 'incident_id': incident['id'], 'reason': 'Consultando el entorno territorial'},
            {'type': 'dispatch', 'incident_id': incident['id'], 'resource_id': resource['id'], 'reason': 'Recurso de prueba disponible'},
            {'type': 'alert', 'incident_id': incident['id'], 'reason': 'Vista previa de aviso en prueba visual'},
        ]}


def instrument_map(route):
    response = route.fetch()
    route.fulfill(response=response, body=response.text() + '''
window.__directorMap = map;
window.__directorFrames = [];
map.on("move", () => {
  window.__directorFrames.push({zoom: map.getZoom(), lat: map.getCenter().lat, lon: map.getCenter().lng});
  if (window.__directorFrames.length > 2000) window.__directorFrames.shift();
});
''')


def verify_evidence(browser, url, store):
    payload = deepcopy(store.payload())
    thermal = next(i for i in payload['incidents'] if i['name'] == 'Igea')
    thermal['demo_report'] = {'location': {'lat': thermal['lat'], 'lon': thermal['lon'], 'label': 'Igea · prueba visual', 'precision': 'locality'}}
    other = next(i for i in payload['incidents'] if i.get('source_kind') == 'call')
    director = {'session_id': 'visual-evidence-fixture', 'status': 'watching', 'sequence': 0, 'events': [], 'assignments': {}, 'alerts': {}}
    camera = {'id': 'camera-fixture', 'lat': thermal['lat'], 'lon': thermal['lon'], 'kind': 'snapshot', 'name': 'Captura fixture', 'source': 'prueba'}
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda error: errors.append(error.stack))
    page.route('**/app.js', instrument_map)
    page.route('**/api/data', lambda route: route.fulfill(json=payload))
    page.route('**/api/director', lambda route: route.fulfill(json=director | {'server_time': time.time()}))
    page.route('**/api/webcams', lambda route: route.fulfill(json={'cameras': [camera], 'sources': []}))
    page.route('**/api/webcam?*', lambda route: route.fulfill(json={'kind': 'snapshot', 'url': '/territorial/' + '0' * 24 + '.img', 'offline': True, 'fetched_at': '2026-09-19T10:00:00Z'}))
    page.route('**/territorial/' + '0' * 24 + '.img', lambda route: route.fulfill(content_type='image/png', body=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a/a0AAAAASUVORK5CYII=')))
    page.goto(url)
    page.wait_for_function('window.__directorMap && document.querySelector("#zone-count").textContent !== "—"')

    def event(incident):
        director['sequence'] += 1
        director['events'].append({'sequence': director['sequence'], 'at': time.time(), 'kind': 'report', 'incident_id': incident['id'], 'message': 'Aviso fixture para revisión de evidencias'})

    event(thermal)
    page.locator('#evidence-satellite img').wait_for(state='visible', timeout=30000)
    page.locator('#evidence-camera img').wait_for(state='visible')
    assert 'Brillo I4' in page.locator('#evidence-facts').inner_text()
    assert 'MUESTRA HISTÓRICA' in page.locator('#evidence-status').inner_text()
    assert page.locator('#evidence-satellite circle').count() > 0
    page.wait_for_timeout(4000)
    page.screenshot(path=str(ROOT / '.local/director-evidence.png'))
    first_zoom = page.evaluate('window.__directorMap.getZoom()')
    page.evaluate('window.__directorFrames = []')
    event(other)
    page.wait_for_function('(name) => document.querySelector("#evidence-title").textContent === name', arg=other['demo_report']['location']['label'])
    page.wait_for_timeout(4200)
    frames = page.evaluate('window.__directorFrames')
    assert min(f['zoom'] for f in frames) < first_zoom - 1, 'Debe alejarse antes de cambiar de localidad'
    assert frames[-1]['zoom'] > min(f['zoom'] for f in frames) + 1, 'Debe acercarse al llegar'
    assert abs(frames[-1]['lat'] - other['lat']) < .05
    assert page.locator('#evidence-satellite img').count() == 0, 'No reutilizar imágenes de otra zona sin detecciones'
    page.mouse.move(500, 650)
    page.mouse.wheel(0, 120)
    page.wait_for_timeout(500)
    assert page.locator('#follow-toggle').get_attribute('aria-pressed') == 'false'
    assert not page.locator('#agent-evidence').is_visible()
    before = page.evaluate('[window.__directorMap.getZoom(), window.__directorMap.getCenter()]')
    page.wait_for_timeout(17000)
    assert page.evaluate('[window.__directorMap.getZoom(), window.__directorMap.getCenter()]') == before
    page.locator('#follow-toggle').click()
    page.wait_for_function('document.querySelector("#evidence-title").textContent === "Igea · prueba visual"')
    page.locator('#evidence-satellite img').wait_for(state='visible')
    page.locator('#evidence-satellite button').click()
    page.locator('#evidence-satellite img').wait_for(state='visible')
    assert 'color natural' in page.locator('#evidence-satellite h3').inner_text()
    page.locator('#evidence-close').click()
    assert not page.locator('#agent-evidence').is_visible()
    page.set_viewport_size({'width': 390, 'height': 844})
    page.emulate_media(reduced_motion='reduce')
    page.wait_for_timeout(300)
    page.evaluate('window.__directorFrames = []')
    event(other)
    page.wait_for_function('(name) => document.querySelector("#evidence-title").textContent === name', arg=other['demo_report']['location']['label'])
    panel = page.locator('#agent-evidence').bounding_box()
    assert panel and panel['x'] >= 0 and panel['x'] + panel['width'] <= 390
    assert panel['y'] + panel['height'] < 422, 'En móvil el panel debe dejar visible el centro del mapa'
    assert len(page.evaluate('window.__directorFrames')) <= 2, 'Movimiento reducido: sin vuelo animado'
    assert not errors, errors
    page.close()
    print('Evidencias: GIBS offline real, FIRMS/GFS fechados, cámara fixture, dos zonas, zoom out/in, control manual y reanudación: OK')


def verify_responder_ui(browser, url, store):
    from test_demo import message, part

    class VoiceFixture:
        ready = responder_ready = True

        def __init__(self):
            self.created = []
            self.transcripts = {}

        def create(self, session_id, role='citizen', context=None):
            run_id = str(uuid.uuid4())
            self.created.append((run_id, role, context))
            return {'run_id': run_id, 'url': 'wss://example.invalid', 'token': 'fixture', 'room_name': 'fixture'}

        def messages(self, run_id):
            return self.transcripts.get(run_id, [])

    provider = VoiceFixture()
    store.demo.provider = provider
    store.director.planner.ready = False
    incident = next(i for i in store.payload()['incidents'] if i.get('source_kind') == 'call')
    resource = next(a['resource'] for a in store.director.state['assignments'].values() if a['incident_id'] == incident['id'])
    phone = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    receiver = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    errors = []
    for page in (phone, receiver):
        page.on('pageerror', lambda error: errors.append(error.stack))
    phone.route('https://cdn.jsdelivr.net/**', lambda route: route.fulfill(content_type='text/javascript', body='''
window.LivekitClient = {RoomEvent: {TrackSubscribed: 'track', Disconnected: 'disconnected'}, Track: {Kind: {Audio: 'audio'}},
Room: class { constructor(){ this.localParticipant = {setMicrophoneEnabled: async () => {}}; } on(){ } async connect(){ } disconnect(){ }} };
'''))
    receiver.add_init_script('''
window.__alarmStarts = 0;
const original = AudioContext.prototype.createOscillator;
AudioContext.prototype.createOscillator = function() {
 const oscillator = original.call(this), start = oscillator.start.bind(oscillator);
 oscillator.start = (...args) => { window.__alarmStarts++; return start(...args); };
 return oscillator;
};
''')
    receiver.goto(url + '/112/alerts/')
    receiver.locator('#activate-alerts').click()
    expect(receiver.locator('body')).to_have_attribute('data-armed', 'true')
    expect(receiver.locator('#receiver-status')).to_contain_text('conectado')
    phone.goto(url + '/112/')
    phone.locator('[data-number="123"]').click()
    phone.locator('#incident-choice').select_option(incident['id'])
    phone.locator('#resource-choice').select_option(resource['id'])
    phone.locator('#call-button').click()
    expect(phone.locator('#status')).to_have_text('En llamada', timeout=30000)
    expect(phone.locator('#speaker-button')).to_be_enabled()
    phone.locator('#speaker-button').click()
    expect(phone.locator('#audio-note')).not_to_be_empty()
    expect(phone.locator('#status')).to_have_text('En llamada')
    run_id, role, binding = provider.created[-1]
    assert role == 'firefighter' and binding['incident_id'] == incident['id']
    provider.transcripts[run_id] = [part(llegada='confirmada', incendio='confirmado', es_alert='solicitado', refuerzos='solicitado', helicoptero='solicitado', evolucion='empeora', zona_urbana='si', detalle='Prueba de refuerzos y alerta móvil')]
    store.demo.poll_once()
    store.director.step()
    expect(receiver.locator('body')).to_have_attribute('data-sounding', 'true')
    assert receiver.evaluate('window.__alarmStarts') == 1
    assert store.director.state['assignments'][resource['id']]['arrival_confirmed']
    phone.locator('#details-toggle').click()
    expect(phone.locator('#part-details')).to_contain_text('solicitado')
    receiver.locator('#ack-alert').click()
    assert receiver.locator('#received-alert').is_hidden()
    store.director.step()
    receiver.wait_for_timeout(1800)
    assert receiver.evaluate('window.__alarmStarts') == 1, 'No duplicar una petición ya emitida'
    context = store.director.context(store.payload())
    helicopter = next(r for r in context['resources'] if r['kind'] == 'helicopter' and not r['assignment'])
    reinforcement = next(r for r in context['resources'] if r['kind'] == 'fire_engine' and not r['assignment'])
    plan = {'revision': context['revision'], 'summary': 'Plan fixture: refuerzo terrestre y aéreo', 'actions': [
        {'type': 'dispatch', 'incident_id': incident['id'], 'resource_id': r['id'], 'reason': 'Solicitud de apoyo en parte de bomberos'} for r in (helicopter, reinforcement)]}
    actions = store.director.prepare(plan, context)
    assert all(not action.get('route_error') for action in actions)
    store.director.apply(plan, actions, 'response-ui-fixture')
    map_page = browser.new_page(viewport={'width': 1440, 'height': 900})
    map_page.on('pageerror', lambda error: errors.append(error.stack))
    map_page.goto(url)
    map_page.locator('.response-vehicle.helicopter').wait_for(state='attached')
    assert map_page.locator('.response-vehicle.fire-engine').count() >= 2
    second_run = str(uuid.uuid4())
    store.demo.register(second_run)
    previous_resolver = store.demo.resolver
    store.demo.resolver = lambda query: {'lat': 41.13, 'lon': 1.26, 'label': 'Segundo aviso de prueba', 'precision': 'coordinates', 'source': 'test_fixture'}
    store.demo.accept(second_run, [message('Segundo aviso de prueba')])
    store.demo.resolver = previous_resolver
    second_incident = next(i for i in store.payload()['incidents'] if i.get('demo_report', {}).get('run_id') == second_run)
    context = store.director.context(store.payload())
    context['incidents'] = [dict(i, responder_report={'fields': {'helicoptero': 'solicitado'}}) if i['id'] == second_incident['id'] else i for i in context['incidents']]
    reassignment = {'revision': context['revision'], 'summary': 'Plan fixture: redistribución', 'actions': [{'type': 'reassign', 'incident_id': second_incident['id'], 'resource_id': helicopter['id'], 'reason': 'Apoyo aéreo a segundo aviso en la prueba'}]}
    store.director.apply(reassignment, store.director.prepare(reassignment, context), 'reassign-ui-fixture')
    assert store.director.state['assignments'][helicopter['id']]['incident_id'] == second_incident['id']
    provider.transcripts[run_id].append(part(incendio='descartado', es_alert='no_solicitado'))
    store.demo.poll_once()
    store.director.step()
    assert incident['id'] not in [i['id'] for i in store.payload()['incidents']]
    assert incident['id'] not in store.director.state['alerts']
    phone.locator('#details-close').click()
    phone.locator('#hangup-button').click()
    receiver.reload()
    receiver.locator('#activate-alerts').click()
    receiver.wait_for_timeout(1800)
    assert receiver.evaluate('window.__alarmStarts') == 0, 'Recargar no reproduce alertas anteriores'
    assert not errors, errors
    for page in (phone, receiver, map_page):
        page.close()
    print('123 + receptor: selección de incidente/unidad, parte, llegada, ES-Alert con AudioContext, idempotencia, refuerzo/camión/helicóptero, reasignación y cancelación: OK (voz y plan fixtures).')


def main(cloud: bool = False) -> None:
    database = Database()
    store = Store(offline=True, database=database)
    store.demo = DemoBridge(database, provider=type('IntakeFixture', (), {'ready': True})(),
                            resolver=lambda query: {'lat': 41.1189, 'lon': 1.2445, 'label': 'Tarragona', 'precision': 'locality', 'source': 'test_fixture'})
    store.director = Director(store, planner=None if cloud else PlannerFixture(), router=LocalRouter(database, offline=not cloud))

    class TestHandler(Handler):
        def log_message(self, *args):
            pass
    TestHandler.store = store
    server = ThreadingHTTPServer(('127.0.0.1', 0), TestHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(error.stack))

            page.route('**/app.js', instrument_map)
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.wait_for_timeout(1500)
            assert not page.locator('#details').is_visible()
            assert not page.locator('#sidebar').is_visible()
            assert not page.locator('#agent-aura').is_visible()
            bounds = page.locator('#map').bounding_box()
            assert bounds and bounds['width'] == 1440
            run = str(uuid.uuid4())
            store.demo.register(run)
            store.demo.accept(run, [{'role': 'assistant', 'tool_calls': [{'function': {'name': 'actualizar_ficha', 'arguments': json.dumps({
                'ubicacion': 'Tarragona', 'emergencia': 'Incendio', 'riesgos': 'Humo', 'personas': 'Sin heridos conocidos'})}}]}])
            store.director.step()
            page.locator('#agent-evidence').wait_for(state='visible')
            assert 'NOAA GFS' in page.locator('#evidence-facts').inner_text()
            assert 'La llamada se mantiene' in page.locator('.evidence-caveat').inner_text()
            page.locator('#agent-aura').wait_for(state='visible')
            store.director.step()
            deadline = time.monotonic() + 160
            while store.director.state['pending'] and time.monotonic() < deadline:
                page.wait_for_timeout(2000)
                store.director.step()
            assert store.director.state['history'], 'No llegó un plan válido'
            if cloud:
                print('Plan real HappyRobot recibido:', store.director.state['history'][-1]['run_id'], flush=True)
            assert store.director.state['assignments'], 'No se pudo asignar un recurso con ruta válida'
            page.locator('.response-vehicle').wait_for(state='visible')
            first = page.locator('.response-vehicle').first.get_attribute('style')
            page.wait_for_timeout(1300)
            second = page.locator('.response-vehicle').first.get_attribute('style')
            assert first != second, 'El vehículo debe avanzar por la geometría de la ruta'
            assert page.locator('.response-station').count() >= 1
            assert page.locator('.place-marker.facility').count() == 0
            assert not page.locator('#details').is_visible()
            page.wait_for_timeout(3500)
            frames = page.evaluate('window.__directorFrames')
            assert len(frames) > 20, 'El mapa debe recorrer vistas intermedias, no teletransportarse'
            jumps = [(a, b) for a, b in zip(frames, frames[1:]) if abs(a['zoom'] - b['zoom']) >= .8]
            assert not jumps, jumps[:4]
            page.locator('#motion-toggle').click()
            frozen = page.locator('.response-vehicle').first.get_attribute('style')
            page.wait_for_timeout(500)
            assert page.locator('.response-vehicle').first.get_attribute('style') == frozen
            for event in store.director.state['events']:
                event['at'] = time.time() - 200
            store.director.state['status'] = 'watching'
            page.reload()
            page.wait_for_timeout(2000)
            assert not page.locator('#agent-aura').is_visible(), 'No reproducir decisiones antiguas'
            assert not page.locator('#details').is_visible()
            assert not errors, errors
            print('UI escritorio: mapa limpio, llamada fixture, borde de actividad, estación y camión animado, pausa y reconexión: OK')
            mobile = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, reduced_motion='reduce')
            mobile.goto(f'http://127.0.0.1:{server.server_port}')
            mobile.wait_for_timeout(2000)
            assert not mobile.locator('#details').is_visible()
            bounds = mobile.locator('#map').bounding_box()
            assert bounds and bounds['height'] == 844
            print(f'UI móvil y movimiento reducido: OK. Planner {"HappyRobot real" if cloud else "fixture"}; entrada de llamada fixture; rutas y consultas SQL reales.')
            mobile.close()
            page.close()
            verify_evidence(browser, f'http://127.0.0.1:{server.server_port}', store)
            verify_responder_ui(browser, f'http://127.0.0.1:{server.server_port}', store)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true', help='Usa el LLM de HappyRobot con cuota en lugar del planner fixture')
    main(parser.parse_args().cloud)
