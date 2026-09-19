from __future__ import annotations

import argparse
import json
import time
import uuid
from copy import deepcopy

from app import Store
from database import Database
from demo import DemoBridge
from director import Director


def cloud_check() -> None:
    database = Database()
    store = Store(offline=True, database=database)
    store.demo = DemoBridge(database, provider=type('IntakeFixture', (), {'ready': True})(),
                            resolver=lambda query: {'lat': 41.1189, 'lon': 1.2445, 'label': 'Tarragona', 'precision': 'locality', 'source': 'test_fixture'})
    run = str(uuid.uuid4())
    store.demo.register(run)
    store.demo.accept(run, [{'role': 'assistant', 'tool_calls': [{'function': {'name': 'actualizar_ficha',
        'arguments': json.dumps({'ubicacion': 'Tarragona', 'emergencia': 'Incendio de vegetación', 'riesgos': 'Humo cerca de viviendas', 'personas': 'Sin heridos conocidos'})}}]}])
    director = Director(store)
    if not director.planner.ready:
        raise RuntimeError('Publica primero el workflow independiente')
    director.step()
    pending = director.state['pending']
    if pending is None:
        raise RuntimeError('No se inició el razonamiento')
    print('Run real de razonamiento:', pending['run_id'], flush=True)
    deadline = time.monotonic() + 160
    while director.state['pending'] and time.monotonic() < deadline:
        time.sleep(2)
        director.step()
    if not director.state['history']:
        raise RuntimeError('El agente no produjo un plan válido')
    state = director.public_state()
    print('Decisión:', director.state['history'][-1]['plan']['summary'], flush=True)
    print('Acciones:', [e['kind'] for e in state['events']], flush=True)
    print('Vehículos:', len(state['assignments']), flush=True)
    for assignment in state['assignments'].values():
        print(assignment['resource']['name'], round(assignment['route']['distance_km'], 2), 'km; ruta A* local', flush=True)
    database.asset('director-verification', 'test_evidence', {'state': deepcopy(state), 'payload': store.payload(),
                   'plan': director.state['history'][-1]['plan'], 'intake': 'fixture, not a real voice call', 'reasoning': 'real HappyRobot run'})
    print('Evidencia local en SQL: director-verification. Entrada de llamada ficticia, razonamiento HappyRobot real.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true', help='Ejecuta un razonamiento real con cuota; no llama ni envía mensajes')
    args = parser.parse_args()
    if not args.cloud:
        parser.error('Se requiere --cloud explícito; para pruebas sin cuota usa unittest test_director test_local_routes')
    cloud_check()
