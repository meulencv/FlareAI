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
from local_routes import LocalRouter, km, valid_point

ROOT = Path(__file__).resolve().parent
ACTION_TYPES = {'focus', 'context', 'dispatch', 'reassign', 'return', 'alert', 'watch'}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()[:24]


def reported(payload: dict) -> list[dict]:
    return sorted((i for i in payload.get('incidents', []) if i.get('demo_report') and not i['demo_report'].get('cancelled')), key=lambda i: i['id'])


def fingerprint(payload: dict) -> str:
    return digest({'status': payload.get('status'), 'field_reports': payload.get('demo', {}).get('field_reports', {}), 'incidents': [
        {k: i.get(k) for k in ('id', 'lat', 'lon', 'demo_report', 'responder_report', 'weather', 'footprint')} for i in reported(payload)]})


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
            for category, kind, count in [('fire_station', 'fire_engine', 2), ('police', 'police', 1), ('helipad', 'helicopter', 1)]:
                for row in proximity(db, lat, lon, 60, category, 6 if kind == 'fire_engine' else 3):
                    for index in range(count):
                        stations.append({'id': f'{row["id"]}:{kind}:{index + 1}', 'station_id': row['id'],
                                         'name': row['name'] or {'fire_engine': 'Parque de bomberos', 'police': 'Policía', 'helicopter': 'Helipuerto · sede para recurso simulado'}[kind],
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


def air_route(start: list[float], end: list[float]) -> dict:
    if not valid_point(start) or not valid_point(end) or km(start, end) > 180:
        raise ValueError('Vuelo fuera del alcance ilustrativo de 180 km')
    distance = km(start, end)
    return {'coordinates': [start, end], 'cumulative_km': [0, distance], 'distance_km': round(distance, 3),
            'duration_seconds': max(1, distance / 180 * 3600), 'mode': 'air_demo',
            'limitations': 'Trayectoria aérea recta ilustrativa. No valida espacio aéreo, meteorología, capacidad ni disponibilidad real.'}


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
                                      'last_fingerprint': '', 'last_review': 0, 'pending': None, 'history': [], 'runs': [],
                                      'field_revisions': {}, 'field_actions': {}, 'alert_requests': {}, 'notifications': [], 'delivery_sequence': 0}
        self.retry_at = 0.0
        self.failure_count = 0

    def station_inventory(self) -> list[dict]:
        stations: dict[str, dict] = {}
        for resource in self.state['resources'].values():
            station = stations.setdefault(resource['station_id'], {k: resource[k] for k in ('station_id', 'name', 'lat', 'lon', 'kind')} | {
                'total': 0, 'available': 0, 'busy': 0, 'simulated_capacity': True})
            station['total'] += 1
            station['busy' if resource['id'] in self.state['assignments'] else 'available'] += 1
        return list(stations.values())

    def public_state(self) -> dict:
        with self.lock:
            return deepcopy({k: self.state[k] for k in ('session_id', 'mode', 'status', 'sequence', 'events', 'assignments', 'alerts')}) | {'server_time': time.time(), 'stations': self.station_inventory()}

    def alert_feed(self, after: int | None = None) -> dict:
        with self.lock:
            return {'session_id': self.session_id, 'sequence': self.state['delivery_sequence'], 'mode': 'simulation_only',
                    'events': deepcopy([e for e in self.state['notifications'] if after is not None and e['sequence'] > after and e['expires_at'] > time.time()])}

    def notify(self, incident_id: str, message: str, source: str, kind: str = 'alert') -> None:
        self.state['delivery_sequence'] += 1
        at = time.time()
        notification = {'id': f'{self.session_id}:{self.state["delivery_sequence"]}', 'sequence': self.state['delivery_sequence'],
                        'incident_id': incident_id, 'kind': kind, 'message': message[:240], 'at': at, 'expires_at': at + 300,
                        'source': source, 'mode': 'simulation_only'}
        self.state['notifications'] = (self.state['notifications'] + [notification])[-50:]
        if kind == 'alert':
            self.state['alerts'][incident_id] = {**notification, 'mode': 'mobile_simulation'}
        else:
            self.state['alerts'].pop(incident_id, None)
        self.event('alert' if kind == 'alert' else 'cancelled', 'ES-Alert enviado al simulador móvil' if kind == 'alert' else 'Aviso retirado por bomberos · demo', message, incident_id=incident_id)

    def ingest_field_reports(self, payload: dict) -> bool:
        changed = False
        for identifier, report in payload.get('demo', {}).get('field_reports', {}).items():
            if report['revision'] <= self.state['field_revisions'].get(identifier, 0):
                continue
            changed = True
            self.state['field_revisions'][identifier] = report['revision']
            fields = report['fields']
            previous_versions = self.state['field_actions'].get(identifier, {})
            self.state['field_actions'][identifier] = dict(report['field_versions'])
            self.event('field_report', 'Parte de bomberos recibido', fields.get('detalle', fields.get('incendio', 'Actualización de situación')), incident_id=identifier)
            arrival_resource = report.get('field_sources', {}).get('llegada', {}).get('resource_id', report.get('resource_id'))
            assignment = self.state['assignments'].get(arrival_resource)
            if report['field_versions'].get('llegada', 0) > previous_versions.get('llegada', 0) and fields.get('llegada') == 'confirmada' and assignment and assignment['incident_id'] == identifier and assignment['status'] != 'returning':
                assignment.update(status='onscene', arrival_confirmed=True, started_at=time.time() - assignment['travel_seconds'])
                self.event('arrived', 'Llegada confirmada por bomberos · demo', incident_id=identifier)
            if fields.get('incendio') in {'descartado', 'extinguido'}:
                if report['field_versions'].get('incendio', 0) > previous_versions.get('incendio', 0):
                    self.notify(identifier, 'Bomberos informa: ' + fields['incendio'] + '. Se retira el aviso de demostración.', 'firefighter_demo', 'cancel')
                continue
            request_id = report['field_versions'].get('es_alert', 0)
            if fields.get('es_alert') == 'solicitado' and self.state['alert_requests'].get(identifier) != request_id:
                self.state['alert_requests'][identifier] = request_id
                self.notify(identifier, fields.get('detalle') or 'Solicitud expresa de bomberos. Aviso de emergencia simulado; no es una alerta real.', 'firefighter_request')
        return changed

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
            incidents.append({k: incident.get(k) for k in ('id', 'name', 'lat', 'lon', 'weather', 'demo_report', 'source_kind', 'responder_report')} | {
                'environment': {k: environment.get(k) for k in ('population', 'landcover', 'wind', 'coverage', 'method')},
                'attention_samples': samples[:6], 'attention_model': environment['potential'].get('model'),
                'facilities': environment['potential'].get('facilities', [])[:12]})
        relevant.update(self.state['assignments'])
        resources = [r | {'assignment': self.state['assignments'].get(r['id'])} for r in self.state['resources'].values() if r['id'] in relevant]
        for r in resources:
            if r['assignment']:
                r['assignment'] = {k: v for k, v in r['assignment'].items() if k not in ('route', 'resource')}
        context = {'mode': 'simulation_only', 'incidents': incidents, 'resources': resources, 'stations': self.station_inventory(),
                   'dispatch_policy': 'Si falla la ruta de una unidad propuesta para dispatch, el ejecutor intentará hasta tres sedes alternativas con unidades libres del mismo tipo. Nunca tomará unidades ocupadas ni reservadas para otra acción del plan. Si todas fallan, revisa otra sede en el siguiente plan.',
                   'alerts': self.state['alerts'], 'history': self.state['history'][-8:],
                   'source_status': payload.get('status'), 'at': time.time(), 'incident_limit': 8,
                   'field_reports': payload.get('demo', {}).get('field_reports', {}),
                   'capabilities': {'alert': 'Vista ES-Alert en móviles de la demo: solo confirmación de bomberos en entorno urbano o petición expresa. Nunca Cell Broadcast real.',
                                    'helicopter': 'Recurso ficticio en helipuerto real; disponible para solicitud aérea explícita o incendio confirmado que empeora. Vuelo ilustrativo, no protocolo español.',
                                    'reinforcements': 'Solicitudes de bomberos en responder_report.fields.refuerzos; valorar recursos libres y reassign entre incidentes con motivo y cobertura restante.'},
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
        reserved = {a['resource_id'] for a in plan['actions'] if a.get('resource_id')}
        failed_stations: set[tuple] = set()
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
                fields = (incidents.get(item.get('incident_id'), {}).get('responder_report') or {}).get('fields', {})
                if resource['kind'] == 'helicopter' and kind != 'return' and not (fields.get('helicoptero') == 'solicitado' or fields.get('incendio') == 'confirmado' and fields.get('evolucion') in {'empeora', 'critico'}):
                    item['route_error'] = True
                    item['blocked_reason'] = 'Apoyo aéreo pendiente de solicitud explícita o empeoramiento confirmado en un parte de bomberos.'
                    prepared.append(item)
                    continue
                alternatives = sorted((r for r in context['resources'] if kind == 'dispatch' and resource['kind'] != 'helicopter'
                    and r['kind'] == resource['kind'] and r['id'] not in reserved and r['id'] not in self.state['assignments']
                    and km([r['lon'], r['lat']], item['target']) <= 60), key=lambda r: km([r['lon'], r['lat']], item['target']))
                attempted: set[str] = set()
                for candidate in [resource, *alternatives]:
                    station = candidate['station_id']
                    if station in attempted or len(attempted) >= 4:
                        continue
                    attempted.add(station)
                    failure_key = (station, *item['target'])
                    if kind == 'dispatch' and failure_key in failed_stations:
                        continue
                    try:
                        item['route'] = air_route(self.vehicle_origin(candidate), item['target']) if candidate['kind'] == 'helicopter' else self.router.route(self.vehicle_origin(candidate), item['target'])
                        if candidate['id'] != rid:
                            item.update(resource_id=candidate['id'], requested_resource_id=rid)
                            reserved.add(candidate['id'])
                        break
                    except (OSError, ValueError, RuntimeError) as error:
                        item['blocked_reason'] = 'No se pudo calcular una ruta utilizable; se revisarán alternativas. ' + str(error)[:160]
                        if kind == 'dispatch':
                            failed_stations.add(failure_key)
                if 'route' not in item:
                    item['route_error'] = True
            if kind == 'alert':
                incident = incidents[item['incident_id']]
                fields = (incident.get('responder_report') or {}).get('fields', {})
                population = incident.get('environment', {}).get('population', {}).get('residents') or 0
                urban_pct = incident.get('environment', {}).get('landcover', {}).get('percentages', {}).get('urbano') or 0
                urban = fields.get('zona_urbana') == 'si' or fields.get('zona_urbana') != 'no' and population > 0 and urban_pct >= 5
                item['mobile_alert'] = fields.get('incendio') not in {'descartado', 'extinguido'} and (fields.get('es_alert') == 'solicitado' or fields.get('incendio') == 'confirmado' and urban)
            prepared.append(item)
        return prepared

    def apply(self, plan: dict, actions: list[dict], run_id: str) -> None:
        blocked = any(action.get('route_error') for action in actions)
        self.event('decision', 'Plan con rutas pendientes; revisando alternativas' if blocked else plan['summary'], plan['summary'] if blocked else '', run_id=run_id)
        departures: dict[str, int] = {}
        for action in actions:
            kind, incident_id = action['type'], action.get('incident_id')
            data = {'incident_id': incident_id, 'run_id': run_id}
            if action.get('route_error'):
                self.event('blocked', 'No se ha movilizado el recurso', action.get('blocked_reason', 'Ruta no disponible. ' + action['reason']), **data)
                continue
            if kind in {'dispatch', 'reassign', 'return'}:
                rid = action['resource_id']
                resource = self.state['resources'][rid]
                if action.get('requested_resource_id'):
                    self.event('alternative', 'Recurso alternativo disponible · ' + resource['name'], 'Sustituye una unidad sin ruta utilizable; mismo tipo y sin retirar recursos de otros avisos.', resource_id=rid, requested_resource_id=action['requested_resource_id'], **data)
                route = action['route']
                delay = departures.get(resource['station_id'], 0) * 4 if kind == 'dispatch' else 0
                departures[resource['station_id']] = departures.get(resource['station_id'], 0) + 1
                self.state['assignments'][rid] = {'id': f'{run_id}:{rid}', 'resource': resource, 'incident_id': incident_id,
                    'route': route, 'target': action['target'], 'started_at': time.time() + delay, 'travel_seconds': max(45, min(150, route['duration_seconds'] / 30)),
                    'status': 'returning' if kind == 'return' else 'enroute', 'time_scale': 'accelerated_demo', 'reason': action['reason']}
                noun = {'fire_engine': 'camión de bomberos', 'police': 'patrulla', 'helicopter': 'helicóptero de demo'}[resource['kind']]
                message = f'{"Regresa" if kind == "return" else "Reasignando" if kind == "reassign" else "Movilizando"} 1 {noun} · {resource["name"]}'
                self.event(kind, message, action['reason'], resource_id=rid, **data)
            elif kind == 'alert':
                current_alert = self.state['alerts'].get(incident_id, {})
                if current_alert.get('mode') == 'mobile_simulation' and current_alert.get('expires_at', 0) > time.time():
                    continue
                if action.get('mobile_alert'):
                    self.notify(str(incident_id), action['reason'], 'director_decision')
                else:
                    self.state['alerts'][incident_id] = {'message': action['reason'], 'at': time.time(), 'expires_at': time.time() + 120, 'mode': 'preview_only'}
                    self.event('alert', 'Preparando ES-Alert · vista previa, sin parte habilitante', action['reason'], **data)
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
        payload = self.store.payload()
        with self.lock:
            previous = deepcopy(self.state)
            try:
                if self.ingest_field_reports(payload):
                    self.save()
            except Exception:
                self.state = previous
                raise
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
                        route_failed = any(a.get('route_error') and not a.get('blocked_reason', '').startswith('Apoyo aéreo pendiente') for a in actions)
                        self.state['route_retry_count'] = self.state.get('route_retry_count', 0) + 1 if route_failed else 0
                        self.state['route_retry_at'] = time.time() + min(180, 15 * 2 ** min(4, self.state['route_retry_count'] - 1)) if route_failed else 0
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
            retry_route = self.state.get('route_retry_at', 0) and time.time() >= self.state['route_retry_at']
            if current == self.state['last_fingerprint'] and time.time() - self.state['last_review'] < 180 and not moved and not retry_route:
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
