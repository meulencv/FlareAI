from __future__ import annotations

import argparse
import json
import threading
import time
import uuid
from http.server import ThreadingHTTPServer

from playwright.sync_api import sync_playwright

from app import Handler, Store
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
            page.on('pageerror', lambda error: errors.append(str(error)))
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
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true', help='Usa el LLM de HappyRobot con cuota en lugar del planner fixture')
    main(parser.parse_args().cloud)
