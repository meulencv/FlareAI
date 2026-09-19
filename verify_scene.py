from __future__ import annotations

import argparse
import json
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from unittest.mock import Mock

from playwright.sync_api import expect, sync_playwright

from app import Handler, ROOT, Store
from database import Database
from demo import DemoBridge
from director import Director
from local_routes import LocalRouter
from verify_director_ui import instrument_map


class ScenePlannerFixture:
    ready = True

    def start(self, context):
        self.context = context
        return str(uuid.uuid4())

    def poll(self, run_id):
        context = self.context
        incident = context['incidents'][0]
        resources = []
        for kind, count in [('fire_engine', 2), ('ambulance', 1), ('police', 1), ('helicopter', 1)]:
            resources.extend([r for r in context['resources'] if r['kind'] == kind and not r.get('assignment')][:count])
        return {'revision': context['revision'], 'summary': 'Riesgo vital: dispositivo combinado de ejercicio',
                'assumption': 'La vía de acceso permanece abierta y el viento estable.', 'actions': [
                    {'type': 'dispatch', 'incident_id': incident['id'], 'resource_id': r['id'], 'reason': 'Medio ficticio del atlas para prueba integrada'} for r in resources]}


def main(cloud=False, response=False):
    database = Database()
    store = Store(offline=True, database=database, hackathon=True)
    store.fires = json.loads((ROOT / 'examples/firms.geojson').read_text())
    store.weather = json.loads((ROOT / 'examples/weather.json').read_text())
    store.incidents = json.loads((ROOT / 'examples/combined.json').read_text())['incidents']
    provider = Mock(ready=True, responder_ready=True)
    store.demo = DemoBridge(database, provider=provider, resolver=lambda _: {
        'lat': 41.4035, 'lon': 2.1744, 'label': 'Sagrada Familia, Barcelona · entrada fixture', 'precision': 'poi', 'source': 'fixture de prueba'})
    director = store.director = Director(store, planner=None if cloud else ScenePlannerFixture(), router=LocalRouter(database, offline=True))
    director.scene.data['automatic'] = False
    run = str(uuid.uuid4())
    store.demo.register(run)
    store.demo.accept(run, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_ficha', 'args': {
        'ubicacion': 'Sagrada Familia, Barcelona', 'emergencia': 'Incendio', 'riesgos': 'Humo sobre barrio y personas atrapadas', 'personas': 'Dos heridos'}}]}])
    if response:
        incident = next(i for i in store.payload()['incidents'] if i.get('demo_report'))
        field_run = str(uuid.uuid4())
        store.demo.register(field_run, role='firefighter', binding={**incident['demo_report']['location'], 'run_id': run, 'incident_id': incident['id']})
        store.demo.accept(field_run, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_parte', 'args': {
            'llegada': 'confirmada', 'incendio': 'confirmado', 'evolucion': 'critico', 'zona_urbana': 'si',
            'refuerzos': 'solicitado', 'helicoptero': 'solicitado', 'es_alert': 'solicitado',
            'detalle': 'Parte ficticio: personas atrapadas, propagación rápida y solicitud de apoyo terrestre y aéreo.'}}]}])
    director.scene.observe(store.payload())
    context = director.context(store.payload())
    run_id = director.planner.start(context)
    deadline = time.monotonic() + 150
    plan = None
    while plan is None and time.monotonic() < deadline:
        plan = director.planner.poll(run_id)
        if plan is None:
            time.sleep(2)
    assert plan is not None, 'El director no entregó plan'
    director.apply(plan, director.prepare(plan, context), run_id)
    director.save()
    kinds = {a['resource']['kind'] for a in director.state['assignments'].values()}
    assert {'fire_engine', 'ambulance'} <= kinds, (kinds, [e['message'] for e in director.state['events']])
    print('Plan', 'HappyRobot real' if cloud else 'fixture', run_id, plan['summary'], 'medios:', sorted(kinds), flush=True)
    if cloud:
        if response:
            assert 'helicopter' in kinds, 'El plan real no asignó el apoyo aéreo solicitado'
        assert not any(e['kind'] == 'blocked' for e in director.state['events']), 'Hay rutas pendientes en el plan real'
        store.demo.close()
        return

    class TestHandler(Handler):
        def log_message(self, *args):
            pass
    TestHandler.store = store
    server = ThreadingHTTPServer(('127.0.0.1', 0), TestHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}'
    identifier = context['incidents'][0]['id']
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda error: errors.append(error.stack))
            page.route('**/app.js', instrument_map)
            page.goto(url)
            expect(page.locator('#zone-count')).not_to_have_text('—')
            expect(page.locator('#decision-panel')).to_be_hidden()
            assert int(page.locator('#zone-count').inner_text()) >= len(store.incidents), 'Se conserva España'
            page.locator('#follow-toggle').click()
            page.locator('#history-toggle').click()
            expect(page.locator('#decision-history')).to_contain_text('Supuesto clave')
            page.locator('#scene-controls summary').click()
            page.locator('#scene-barcelona').click()
            page.evaluate('window.__directorMap.setView([41.4035,2.1744],14,{animate:false})')
            expect(page.locator('.traffic-canvas')).to_have_attribute('data-status', 'ready', timeout=30000)
            page.wait_for_function('Number(document.querySelector(".traffic-canvas").dataset.cars) > 0')
            assert int(page.locator('.traffic-canvas').get_attribute('data-cars')) <= 48, 'Tráfico local escaso, no toda la ciudad'
            atlas_hospitals = director.scene.data['hospitals']
            open_records = [r for r in director.scene.data['incidents'].values() if r['phase'] != 'closed']
            reserved = [h for h in atlas_hospitals if h['occupied']]
            threatened = [h for h in atlas_hospitals if not h['occupied']
                          and any(h['name'] in r.get('hospital_threats', []) for r in open_records)]
            expected = len(reserved) + min(1, len(threatened))
            assert expected < len(atlas_hospitals), 'El mapa ya no debe dibujar todos los hospitales del atlas'
            expect(page.locator('.hospital-marker')).to_have_count(expected)
            expect(page.locator('.hospital-marker.transfer')).to_have_count(0)
            expect(page.locator('.response-vehicle.ambulance').first).to_be_visible()
            for assignment in director.state['assignments'].values():
                assignment['started_at'] = time.time()
            before = {rid: a['route']['coordinates'] for rid, a in director.state['assignments'].items()}
            page.locator('[data-scene-action="closure"]').click()
            expect(page.locator('#scene-feedback')).to_contain_text('Cambio aplicado', timeout=30000)
            expect(page.locator('#plan-invalidated')).to_be_visible()
            expect(page.locator('.closure-marker').first).to_be_visible()
            changed = [a for rid, a in director.state['assignments'].items() if a['route']['coordinates'] != before[rid]]
            assert changed, 'El desvío debe cambiar la geometría, no solo el texto'
            assert all(not set(a['route'].get('edge_ids', [])) & set(director.scene.data['closures']) for a in changed)
            expect(page.locator('#decision-history')).to_contain_text('Ruta recalculada')
            page.locator('[data-scene-action="wind"]').click()
            expect(page.locator('#scene-feedback')).to_contain_text('Cambio aplicado')
            page.locator('#scene-role').select_option(label='sanitarios')
            page.locator('#scene-report').select_option(label='heridos')
            page.locator('#scene-field').click()
            expect(page.locator('#decision-history')).to_contain_text('Parte de sanitarios')
            count = page.locator('.history-event').count()
            page.screenshot(path=str(ROOT / '.local/scene-barcelona.png'))
            page.reload()
            expect(page.locator('#decision-panel')).to_be_hidden()
            page.locator('#history-toggle').click()
            expect(page.locator('.history-event')).to_have_count(count)
            expect(page.locator('#decision-history')).to_contain_text('Ruta recalculada')
            director.propose_alert(identifier, 'Humo sobre zona urbana · simulación de prueba', 'test_fixture')
            expect(page.locator('#alert-countdown')).to_be_visible()
            page.locator('#cancel-alert').click()
            expect(page.locator('#alert-countdown')).to_be_hidden()
            page.wait_for_timeout(3200)
            assert not director.alert_feed(0)['events']
            director.state['alert_cooldowns'] = {}
            director.propose_alert(identifier, 'Segundo aviso simulado', 'test_fixture')
            expect(page.locator('#alert-countdown')).to_be_visible()
            page.wait_for_timeout(3500)
            expect(page.locator('#alert-countdown')).to_be_hidden()
            assert len(director.alert_feed(0)['events']) == 1
            record = director.scene.data['incidents'][identifier]
            now = time.time()
            for a in director.state['assignments'].values():
                a.update(status='onscene', started_at=now - a['travel_seconds'], arrived_at=now - 20)
            director.scene.maintenance()
            ambulance = next(a for a in director.state['assignments'].values() if a['resource']['kind'] == 'ambulance')
            assert ambulance['status'] == 'transporting', ambulance['status']
            assert any(h['occupied'] for h in director.scene.data['hospitals'])
            if page.locator('#follow-toggle').get_attribute('aria-pressed') == 'true':
                page.locator('#follow-toggle').click()
            page.evaluate('window.__directorMap.setView([41.4035,2.1744],13,{animate:false})')
            expect(page.locator('.hospital-marker.transfer')).to_have_count(1)
            expect(page.locator('.hospital-marker.transfer').first).to_be_visible()
            assert ambulance['avoided_hospital_ids'], 'El traslado debe descartar los hospitales pegados al fuego'
            expect(page.locator('.hospital-marker.avoided').first).to_be_visible()
            expect(page.locator('#decision-history')).to_contain_text('cambiado por seguridad')
            director.scene.evolve(now)
            assert record['phase'] == 'active'
            director.scene.evolve(now + 46)
            assert record['phase'] == 'contained'
            director.scene.evolve(now + 72)
            assert record['phase'] == 'watching'
            director.scene.evolve(now + 118)
            assert record['phase'] == 'releasing'
            ambulance['started_at'] = time.time() - ambulance['travel_seconds'] - 1
            director.advance()
            director.scene.maintenance()
            assert all(a['status'] == 'returning' for a in director.state['assignments'].values())
            for a in director.state['assignments'].values():
                a['started_at'] = time.time() - a['travel_seconds'] - 1
            director.advance()
            director.scene.evolve(now + 120)
            assert record['phase'] == 'closed'
            director.save()
            expect(page.locator('#decision-history')).to_contain_text('Cerrado')
            boat_run = str(uuid.uuid4())
            store.demo.register(boat_run)
            store.demo.accept(boat_run, [{'role': 'assistant', 'tool_calls': [{'name': 'actualizar_ficha', 'args': {
                'ubicacion': 'Mar de Barcelona', 'emergencia': 'Incendio en un barco', 'personas': 'Tres personas en peligro'}}]}])
            director.scene.observe(store.payload())
            maritime_context = director.context(store.payload())
            maritime = next(i for i in maritime_context['incidents'] if i.get('scenario', {}).get('maritime'))
            resources = [next(r for r in maritime_context['resources'] if r['kind'] == kind and not r['assignment']) for kind in ('helicopter', 'ambulance', 'fire_engine')]
            maritime_plan = {'revision': maritime_context['revision'], 'summary': 'Ejercicio marítimo, no llamada real', 'actions': [
                {'type': 'dispatch', 'incident_id': maritime['id'], 'resource_id': r['id'], 'reason': 'Aire al barco comunicado, apoyo terrestre en la costa'} for r in resources]}
            actions = director.prepare(maritime_plan, maritime_context)
            assert all('route' in a for a in actions)
            from scene import SHORE
            for action, resource in zip(actions, resources):
                assert action['target'] == ([maritime['lon'], maritime['lat']] if resource['kind'] == 'helicopter' else SHORE)
            director.apply(maritime_plan, actions, 'maritime-fixture')
            director.save()
            expect(page.locator('.maritime-marker')).to_have_count(1)
            phone = browser.new_page(viewport={'width': 390, 'height': 844})
            phone.goto(url + '/112/')
            phone.locator('[data-number="123"]').click()
            phone.locator('#incident-choice').select_option(maritime['id'])
            expect(phone.locator('#resource-choice')).to_contain_text('Ambulancia')
            phone.close()
            page.set_viewport_size({'width': 390, 'height': 844})
            panel = page.locator('#decision-panel').bounding_box()
            assert panel and panel['x'] >= 0 and panel['x'] + panel['width'] <= 390
            page.screenshot(path=str(ROOT / '.local/scene-mobile.png'))
            director.state['status'] = 'error'
            expect(page.locator('#director-warning')).to_be_visible()
            expect(page.locator('#director-warning')).to_contain_text('Sin nuevos despachos')
            director.state['status'] = 'watching'
            expect(page.locator('#director-warning')).to_be_hidden()
            assert not errors, errors
            browser.close()
        print('UI: España, hospitales implicados, ambulancias, coches, corte/desvío, partes, memoria tras recarga, veto/envío ES-Alert, traslado, vigilancia/retorno/cierre y móvil: OK')
    finally:
        server.shutdown()
        server.server_close()
        store.demo.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true')
    parser.add_argument('--response', action='store_true')
    args = parser.parse_args()
    if args.response and not args.cloud:
        parser.error('--response requiere --cloud; la suite UI ya cubre partes con fixtures')
    main(args.cloud, args.response)
