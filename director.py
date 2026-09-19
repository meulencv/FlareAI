from __future__ import annotations

import bisect
import hashlib
import http.client
import json
import re
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from build_emergency_db import proximity
from demo import HappyRobotProvider
from local_routes import LocalRouter

ROOT = Path(__file__).resolve().parent
ACTION_TYPES = {'focus', 'context', 'dispatch', 'reassign', 'return', 'alert', 'watch'}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()[:24]


def reported(payload: dict) -> list[dict]:
    return sorted((i for i in payload.get('incidents', []) if i.get('demo_report')), key=lambda i: i['id'])


def fingerprint(payload: dict) -> str:
    return digest({'status': payload.get('status'), 'incidents': [
        {k: i.get(k) for k in ('id', 'lat', 'lon', 'demo_report', 'weather', 'footprint')} for i in reported(payload)]})


def extract_plan(messages: list[dict]) -> dict | None:
    def visit(value):
        if isinstance(value, str):
            try:
                return visit(json.loads(value))
            except ValueError:
                return None
        if isinstance(value, list):
            for item in value:
                result = visit(item)
                if result is not None:
                    return result
        if isinstance(value, dict):
            if value.get('name') == 'publicar_plan':
                args = value.get('arguments', value.get('args', {}))
                if isinstance(args, str):
                    args = json.loads(args)
                plan = args.get('plan_json') if isinstance(args, dict) else None
                if plan is not None:
                    return json.loads(plan) if isinstance(plan, str) else plan
            for key in ('function', 'tool_call'):
                if key in value:
                    result = visit(value[key])
                    if result is not None:
                        return result
        return None
    for message in messages:
        if message.get('role') == 'assistant':
            result = visit(message.get('tool_calls'))
            if result is not None:
                return result
    return None


def validate_plan(plan: dict, context: dict) -> dict:
    if not isinstance(plan, dict) or plan.get('revision') != context['revision']:
        raise ValueError('Plan obsoleto o inválido')
    if not isinstance(plan.get('summary'), str) or not 1 <= len(plan['summary']) <= 240:
        raise ValueError('Resumen inválido')
    actions = plan.get('actions')
    if not isinstance(actions, list) or len(actions) > 8:
        raise ValueError('Máximo ocho acciones')
    incidents = {i['id'] for i in context['incidents']}
    resources = {r['id'] for r in context['resources']}
    used = set()
    for action in actions:
        if not isinstance(action, dict) or action.get('type') not in ACTION_TYPES:
            raise ValueError('Acción no permitida')
        if not isinstance(action.get('reason'), str) or not 1 <= len(action['reason']) <= 240:
            raise ValueError('Motivo requerido')
        if action['type'] != 'return' and action.get('incident_id') not in incidents:
            raise ValueError('Incidente desconocido')
        if action['type'] in {'dispatch', 'reassign', 'return'}:
            rid = action.get('resource_id')
            if rid not in resources or rid in used:
                raise ValueError('Recurso inventado o duplicado')
            used.add(rid)
    return deepcopy(plan)


class EmergencyAtlas:
    def nearby(self, lat: float, lon: float) -> list[dict]:
        with closing(sqlite3.connect(f'file:{ROOT / "emergencias_espana.db"}?mode=ro', uri=True)) as db:
            stations = []
            for category, kind, count in [('fire_station', 'fire_engine', 2), ('police', 'police', 1)]:
                for row in proximity(db, lat, lon, 60, category, 3):
                    for index in range(count):
                        stations.append({'id': f'{row["id"]}:{kind}:{index + 1}', 'station_id': row['id'],
                                         'name': row['name'] or ('Parque de bomberos' if kind == 'fire_engine' else 'Policía'),
                                         'lat': row['lat'], 'lon': row['lon'], 'kind': kind,
                                         'distance_km': round(row['distance_km'], 2), 'simulated_capacity': True,
                                         'coordinate_method': row['coordinate_method']})
            return stations


def route_position(route: dict, progress: float) -> list[float]:
    points, distances = route['coordinates'], route['cumulative_km']
    target = max(0, min(1, progress)) * distances[-1]
    index = min(len(points) - 1, max(1, bisect.bisect_left(distances, target)))
    span = distances[index] - distances[index - 1]
    fraction = (target - distances[index - 1]) / span if span else 1
    return [points[index - 1][axis] + (points[index][axis] - points[index - 1][axis]) * fraction for axis in (0, 1)]


class Planner:
    def __init__(self, database) -> None:
        self.provider = HappyRobotProvider()
        self.config = database.director_setting()
        self.ready = bool(self.provider.client.key and self.config.get('published'))

    def start(self, context: dict) -> str:
        url = urlsplit(self.config.get('hook_url', ''))
        if url.scheme != 'https' or url.netloc != 'workflows.platform.eu.happyrobot.ai' or not re.fullmatch(r'/hooks/[a-zA-Z0-9_-]+', url.path) or url.query or url.fragment or not self.config.get('hook_key'):
            raise ValueError('Webhook del director no válido')
        connection = http.client.HTTPSConnection(url.netloc, timeout=20)
        try:
            connection.request('POST', url.path, json.dumps({'context_json': json.dumps(context, ensure_ascii=False)}).encode(),
                               {'X-API-Key': self.config['hook_key'], 'Content-Type': 'application/json'})
            response = connection.getresponse()
            body = response.read(100001)
            if response.status in {401, 403}:
                raise PermissionError('HappyRobot requiere revisar la autenticación del director')
            if response.status != 200 or len(body) > 100000:
                raise RuntimeError(f'No se pudo iniciar el director (HTTP {response.status})')
            result = json.loads(body)
        finally:
            connection.close()
        if isinstance(result.get('data'), dict):
            result = result['data']
        return str(uuid.UUID(result['run_id']))

    def poll(self, run_id: str) -> dict | None:
        return extract_plan(self.provider.messages(run_id))


class Director:
    def __init__(self, store, planner=None, router=None, atlas=None) -> None:
        self.store, self.db = store, store.db
        self.session_id = store.demo.session_id
        self.planner = planner if planner is not None else Planner(self.db)
        self.router = router if router is not None else LocalRouter(self.db)
        self.atlas = atlas if atlas is not None else EmergencyAtlas()
        self.lock = threading.RLock()
        self.state: dict[str, Any] = {'session_id': self.session_id, 'mode': 'demo', 'status': 'idle' if self.planner.ready else 'unconfigured',
                                      'sequence': 0, 'events': [], 'resources': {}, 'assignments': {}, 'alerts': {},
                                      'last_fingerprint': '', 'last_review': 0, 'pending': None, 'history': [], 'runs': []}
        self.retry_at = 0.0
        self.failure_count = 0

    def public_state(self) -> dict:
        with self.lock:
            return deepcopy({k: self.state[k] for k in ('session_id', 'mode', 'status', 'sequence', 'events', 'assignments', 'alerts')}) | {'server_time': time.time()}

    def event(self, kind: str, message: str, reason: str = '', **data) -> None:
        self.state['sequence'] += 1
        self.state['events'].append({'sequence': self.state['sequence'], 'kind': kind, 'message': message,
                                     'reason': reason, 'at': time.time(), **data})
        self.state['events'] = self.state['events'][-100:]

    def save(self) -> None:
        self.db.save_director(self.session_id, self.state)

    def context(self, payload: dict) -> dict:
        incidents = []
        relevant = set()
        for incident in reported(payload)[:8]:
            for resource in self.atlas.nearby(incident['lat'], incident['lon']):
                self.state['resources'].setdefault(resource['id'], resource)
                relevant.add(resource['id'])
            environment = self.store.context(incident['id'])
            samples = sorted(environment['potential']['samples'], key=lambda s: s.get('score') or 0, reverse=True)
            incidents.append({k: incident.get(k) for k in ('id', 'name', 'lat', 'lon', 'weather', 'demo_report', 'source_kind')} | {
                'environment': {k: environment.get(k) for k in ('population', 'landcover', 'wind', 'coverage', 'method')},
                'attention_samples': samples[:6], 'attention_model': environment['potential'].get('model'),
                'facilities': environment['potential'].get('facilities', [])[:12]})
        relevant.update(self.state['assignments'])
        resources = [r | {'assignment': self.state['assignments'].get(r['id'])} for r in self.state['resources'].values() if r['id'] in relevant]
        for r in resources:
            if r['assignment']:
                r['assignment'] = {k: v for k, v in r['assignment'].items() if k not in ('route', 'resource')}
        context = {'mode': 'simulation_only', 'incidents': incidents, 'resources': resources,
                   'alerts': self.state['alerts'], 'history': self.state['history'][-8:],
                   'source_status': payload.get('status'), 'at': time.time(), 'incident_limit': 8,
                   'omitted_incidents': max(0, len(reported(payload)) - 8),
                   'limits': 'Capacidades ficticias. Atlas no exhaustivo. Sin tráfico ni rutas de emergencia. Potencial no es probabilidad. No confirmar extinción por llegada de vehículos.'}
        context['revision'] = digest(context)
        return context

    def vehicle_origin(self, resource: dict) -> list[float]:
        assignment = self.state['assignments'].get(resource['id'])
        if not assignment:
            return [resource['lon'], resource['lat']]
        return route_position(assignment['route'], (time.time() - assignment['started_at']) / assignment['travel_seconds'])

    def prepare(self, plan: dict, context: dict) -> list[dict]:
        plan = validate_plan(plan, context)
        incidents = {i['id']: i for i in context['incidents']}
        prepared = []
        for action in plan['actions']:
            item = dict(action)
            kind, rid = item['type'], item.get('resource_id')
            if kind in {'dispatch', 'reassign', 'return'}:
                current = self.state['assignments'].get(rid)
                if kind == 'dispatch' and current or kind in {'reassign', 'return'} and not current:
                    raise ValueError('Disponibilidad incompatible con el plan')
                resource = self.state['resources'][rid]
                destination = resource if kind == 'return' else incidents[item['incident_id']]
                item['target'] = [destination['lon'], destination['lat']]
                if kind == 'reassign' and current['incident_id'] == item['incident_id'] and current.get('target') == item['target']:
                    raise ValueError('El recurso ya está asignado a ese destino')
                try:
                    item['route'] = self.router.route(self.vehicle_origin(resource), item['target'])
                except (OSError, ValueError, RuntimeError):
                    item['route_error'] = True
            prepared.append(item)
        return prepared

    def apply(self, plan: dict, actions: list[dict], run_id: str) -> None:
        self.event('decision', plan['summary'], run_id=run_id)
        departures: dict[str, int] = {}
        for action in actions:
            kind, incident_id = action['type'], action.get('incident_id')
            data = {'incident_id': incident_id, 'run_id': run_id}
            if action.get('route_error'):
                self.event('blocked', 'No se ha movilizado el recurso: ruta no disponible', action['reason'], **data)
                continue
            if kind in {'dispatch', 'reassign', 'return'}:
                rid = action['resource_id']
                resource = self.state['resources'][rid]
                route = action['route']
                delay = departures.get(resource['station_id'], 0) * 4 if kind == 'dispatch' else 0
                departures[resource['station_id']] = departures.get(resource['station_id'], 0) + 1
                self.state['assignments'][rid] = {'id': f'{run_id}:{rid}', 'resource': resource, 'incident_id': incident_id,
                    'route': route, 'target': action['target'], 'started_at': time.time() + delay, 'travel_seconds': max(45, min(150, route['duration_seconds'] / 30)),
                    'status': 'returning' if kind == 'return' else 'enroute', 'time_scale': 'accelerated_demo', 'reason': action['reason']}
                noun = 'camión de bomberos' if resource['kind'] == 'fire_engine' else 'patrulla'
                message = f'{"Regresa" if kind == "return" else "Reasignando" if kind == "reassign" else "Movilizando"} 1 {noun} · {resource["name"]}'
                self.event(kind, message, action['reason'], resource_id=rid, **data)
            elif kind == 'alert':
                self.state['alerts'][incident_id] = {'message': action['reason'], 'at': time.time(), 'expires_at': time.time() + 120, 'mode': 'preview_only'}
                self.event('alert', 'Preparando ES-Alert · vista previa', action['reason'], **data)
            else:
                self.event(kind, {'focus': 'Revisando el aviso', 'context': 'Evaluando el entorno', 'watch': 'Manteniendo vigilancia'}[kind], action['reason'], **data)
        self.state['history'].append({'run_id': run_id, 'at': time.time(), 'plan': plan,
                                      'outcomes': [e for e in self.state['events'] if e.get('run_id') == run_id]})
        self.state['history'] = self.state['history'][-20:]

    def advance(self) -> bool:
        changed = False
        for rid, assignment in list(self.state['assignments'].items()):
            if assignment['status'] == 'onscene' or time.time() < assignment['started_at'] + assignment['travel_seconds']:
                continue
            if assignment['status'] == 'returning':
                del self.state['assignments'][rid]
                self.event('available', 'Recurso de nuevo disponible', assignment['resource']['name'])
            else:
                assignment['status'] = 'onscene'
                self.event('arrived', 'Recurso en el punto de encuentro', assignment['resource']['name'], incident_id=assignment['incident_id'])
            changed = True
        for identifier, alert in list(self.state['alerts'].items()):
            if time.time() >= alert['expires_at']:
                del self.state['alerts'][identifier]
                changed = True
        return changed

    def step(self) -> None:
        with self.lock:
            moved = self.advance()
            if moved:
                self.save()
            pending = self.state['pending']
        if not self.planner.ready or time.monotonic() < self.retry_at:
            return
        payload = self.store.payload()
        current = fingerprint(payload)
        if pending:
            plan = self.planner.poll(pending['run_id'])
            if plan is None and time.time() - pending['started_at'] < 150:
                if moved:
                    with self.lock:
                        self.save()
                return
            if plan is None:
                raise RuntimeError('El agente no entregó un plan a tiempo')
            actions = self.prepare(plan, pending['context']) if current == pending['fingerprint'] else []
            fresh = fingerprint(self.store.payload())
            with self.lock:
                if fresh != pending['fingerprint'] or current != pending['fingerprint']:
                    self.event('superseded', 'El aviso ha cambiado; revisando el plan')
                    self.state['last_fingerprint'] = ''
                else:
                    previous = deepcopy(self.state)
                    try:
                        self.apply(plan, actions, pending['run_id'])
                        self.state['last_fingerprint'] = current
                        self.state['last_review'] = time.time()
                        self.state['status'], self.state['pending'] = 'watching', None
                        self.save()
                    except Exception:
                        self.state = previous
                        raise
                self.state['status'], self.state['pending'] = 'watching', None
                self.failure_count = 0
                self.save()
            return
        active = reported(payload)
        with self.lock:
            needs_review = active or self.state['assignments']
            if not needs_review:
                self.state['status'] = 'idle'
                if moved:
                    self.save()
                return
            if current == self.state['last_fingerprint'] and time.time() - self.state['last_review'] < 180 and not moved:
                return
            self.state['runs'] = [at for at in self.state['runs'] if time.time() - at < 3600]
            if len(self.state['runs']) >= 30:
                self.state['status'] = 'limited'
                return
            self.state['status'] = 'thinking'
            self.event('thinking', 'Analizando cambios y recursos disponibles')
            self.save()
        context = self.context(payload)
        run_id = self.planner.start(context)
        with self.lock:
            self.state['runs'].append(time.time())
            self.state['pending'] = {'run_id': run_id, 'context': context, 'fingerprint': current, 'started_at': time.time()}
            self.save()

    def loop(self) -> None:
        with self.db.verification_lock(804030) as acquired:
            if not acquired:
                with self.lock:
                    self.state['status'] = 'standby'
                return
            while True:
                try:
                    self.step()
                except Exception as error:
                    with self.lock:
                        authentication = isinstance(error, PermissionError) or getattr(error, 'status', None) in {401, 403}
                        if authentication:
                            self.planner.ready = False
                        self.failure_count += 1
                        self.state['status'], self.state['pending'] = 'auth_required' if authentication else 'error', None
                        self.event('error', 'Director pendiente de autenticación' if authentication else 'Director temporalmente no disponible', 'Sin nuevas movilizaciones. Se conservan las asignaciones existentes.')
                        self.retry_at = time.monotonic() + min(300, 15 * 2 ** min(self.failure_count, 5))
                        try:
                            self.save()
                        except Exception:
                            pass
                threading.Event().wait(2)
