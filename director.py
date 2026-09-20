from __future__ import annotations

import bisect
import hashlib
import http.client
import json
import re
import sqlite3
import threading
import time
import unicodedata
import uuid
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from build_emergency_db import proximity
from demo import HappyRobotProvider
from local_routes import LocalRouter, km, valid_point

if TYPE_CHECKING:
    from operations import Operations
    from scene import Scene

ROOT = Path(__file__).resolve().parent
ACTION_TYPES = {'focus', 'context', 'dispatch', 'reassign', 'return', 'alert', 'watch'}
PUBLIC_EVENTS = 200


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()[:24]


def reported(payload: dict) -> list[dict]:
    return sorted((i for i in payload.get('incidents', []) if (i.get('demo_report') and not i['demo_report'].get('cancelled') or i.get('sensor_report') or i.get('scene_report'))
                   and i.get('scenario', {}).get('phase') != 'closed' and not i.get('scenario', {}).get('linked_call_id')), key=lambda i: -(i.get('scenario', {}).get('priority') or 0))


def fingerprint(payload: dict) -> str:
    return digest({'scenario_revision': payload.get('scenario_revision'), 'status': payload.get('status'), 'field_reports': payload.get('demo', {}).get('field_reports', {}), 'incidents': [
        {k: i.get(k) for k in ('id', 'lat', 'lon', 'demo_report', 'responder_report', 'weather', 'footprint')} for i in reported(payload)]})


def anchor(payload: dict) -> str:
    """Condiciones que un plan en vuelo necesita para seguir siendo ejecutable.

    Cambia con una corrección de ubicación, una retirada o una invalidación del escenario
    (corte de vía, giro de viento, parte de campo), no con el relato creciente de la llamada.
    """
    return digest({'revision': payload.get('scenario_plan_revision', payload.get('scenario_revision')),
                   'status': payload.get('status'),
                   'incidents': [{'id': i['id'], 'lat': i.get('lat'), 'lon': i.get('lon'),
                                  'location': (i.get('demo_report') or {}).get('location'),
                                  'cancelled': (i.get('demo_report') or {}).get('cancelled'),
                                  'responder_report': i.get('responder_report')} for i in reported(payload)],
                   'field_reports': payload.get('demo', {}).get('field_reports', {})})


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
    if context.get('presentation'):
        assessments = plan.get('assessments', [])
        if not isinstance(assessments, list):
            raise ValueError('Evaluaciones no válidas')
        for incident in context['incidents']:
            if not incident.get('testimonies') or incident.get('assessment'):
                continue
            assessment = next((a for a in assessments if isinstance(a, dict) and a.get('incident_id') == incident['id']), None)
            if not assessment or not isinstance(assessment.get('summary'), str) or not assessment['summary'].strip():
                raise ValueError('Falta la conclusión de los testimonios')
            verdicts = assessment.get('testimonies', [])
            expected = {t['id'] for t in incident['testimonies']}
            if not isinstance(verdicts, list) or len(verdicts) != len(expected) or any(not isinstance(v, dict) for v in verdicts):
                raise ValueError('Falta evaluar todos los testimonios')
            if {v.get('id') for v in verdicts} != expected or any(v.get('status') not in {'supported', 'uncertain', 'unlikely', 'prank'} for v in verdicts):
                raise ValueError('Evaluación de testimonios incompleta o inválida')
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


EMERGENCY_WARD_METRES = 300
HOSPITAL_MERGE_METRES = 250
HOSPITAL_SAME_POINT_METRES = 60
HOSPITAL_MIN_BEDS = 40
HOSPITAL_TYPES_ACCEPTED = ('generales', 'especializados', 'hospital')
HOSPITAL_TYPES_REJECTED = ('larga estancia', 'salud mental', 'toxicoman', 'otros centros')
HOSPITAL_NAMES_REJECTED = ('atencio primaria', 'atencion primaria', 'salut mental', 'salud mental', 'residencia',
                           'consultori', 'sociosanitari', 'llarga estada', 'larga estancia', 'geriatric',
                           'salut laboral', 'salud laboral', 'oftalmolog')
HOSPITAL_NAME_NOISE = {'hospital', 'hospitals', 'clinica', 'clinic', 'universitari', 'universitario', 'universitaria',
                       'general', 'generales', 'fundacio', 'fundacion', 'centre', 'centro', 'complex', 'consorci',
                       'de', 'del', 'la', 'el', 'los', 'las', 'i', 'y', 'sa', 'sl', 'urgencies', 'urgencias', 'seu'}


def plain(value: str | None) -> str:
    text = unicodedata.normalize('NFKD', (value or '').lower())
    return re.sub(r'[^a-z0-9 ]+', ' ', ''.join(c for c in text if not unicodedata.combining(c)))


def name_tokens(value: str | None) -> set[str]:
    return {word for word in plain(value).split() if len(word) > 2 and word not in HOSPITAL_NAME_NOISE}


def same_site(a: dict, b: dict) -> bool:
    metres = km([a['lon'], a['lat']], [b['lon'], b['lat']]) * 1000
    if metres <= HOSPITAL_SAME_POINT_METRES:
        return True
    return metres <= HOSPITAL_MERGE_METRES and bool(name_tokens(a['name']) & name_tokens(b['name']))


class EmergencyAtlas:
    def nearby(self, lat: float, lon: float) -> list[dict]:
        with closing(sqlite3.connect(f'file:{ROOT / "emergencias_espana.db"}?mode=ro', uri=True)) as db:
            stations = []
            sources: list[tuple[list[dict], str, int]] = [
                (self.hospitals(lat, lon, 60, 3), 'ambulance', 2),
            ]
            for category, kind, count in [('fire_station', 'fire_engine', 2), ('police', 'police', 1), ('helipad', 'helicopter', 1), ('ambulance_station', 'ambulance', 2)]:
                sources.append((proximity(db, lat, lon, 60, category, 6 if kind == 'fire_engine' else 3), kind, count))
            for rows, kind, count in sources:
                for row in rows:
                    for index in range(count):
                        stations.append({'id': f'{row["id"]}:{kind}:{index + 1}', 'station_id': row['id'],
                                         'name': row['name'] or {'fire_engine': 'Parque de bomberos', 'police': 'Policía', 'ambulance': 'Base sanitaria del atlas', 'helicopter': 'Helipuerto · sede para recurso simulado'}[kind],
                                         'lat': row['lat'], 'lon': row['lon'], 'kind': kind,
                                         'distance_km': round(row['distance_km'], 2), 'simulated_capacity': True,
                                         'coordinate_method': row['coordinate_method']})
            return list({r['id']: r for r in stations}.values())

    def registry(self, db: sqlite3.Connection, facility_id: str) -> dict | None:
        for row in db.execute("SELECT raw_json FROM source_records WHERE facility_id=? AND source_id IN ('sanidad_hospitals','dera_hospitals')", (facility_id,)):
            raw = json.loads(row[0])
            beds = str(raw.get('Camas', ''))
            return {'type': plain(raw.get('dependenciaTipoCentro') or raw.get('tipo')),
                    'beds': int(beds) if beds.isdigit() else None}
        return None

    def transport_ready(self, db: sqlite3.Connection, row: dict, wards: list[dict]) -> dict | None:
        """Hospital del atlas que puede recibir un traslado: urgencias publicadas y tipo asistencial
        compatible. Heurística documental sobre datos estáticos; no acredita urgencias abiertas ni
        ambulancias disponibles."""
        if not row['name'] or any(bad in plain(row['name']) for bad in HOSPITAL_NAMES_REJECTED):
            return None
        categories = {value for value, in db.execute('SELECT category_id FROM facility_categories WHERE facility_id=?', (row['id'],))}
        ward = ('own' if 'emergency_department' in categories else
                'nearby' if any(km([row['lon'], row['lat']], [w['lon'], w['lat']]) * 1000 <= EMERGENCY_WARD_METRES for w in wards) else None)
        if ward is None:
            return None
        registry = self.registry(db, row['id'])
        if registry and (any(bad in registry['type'] for bad in HOSPITAL_TYPES_REJECTED)
                         or not any(good in registry['type'] for good in HOSPITAL_TYPES_ACCEPTED)
                         or (registry['beds'] is not None and registry['beds'] < HOSPITAL_MIN_BEDS)):
            return None
        return {'emergency_ward': ward, 'official_registry': bool(registry),
                'registered_beds': (registry or {}).get('beds')}

    def hospitals(self, lat: float, lon: float, radius_km: float = 22, limit: int = 30) -> list[dict]:
        with closing(sqlite3.connect(f'file:{ROOT / "emergencias_espana.db"}?mode=ro', uri=True)) as db:
            wards = [row for row in proximity(db, lat, lon, radius_km + 2, 'emergency_department', 600)
                     if not db.execute("SELECT 1 FROM facility_categories WHERE facility_id=? AND category_id='health_centre'", (row['id'],)).fetchone()]
            candidates = []
            for row in proximity(db, lat, lon, radius_km, 'hospital', max(limit * 6, 60)):
                evidence = self.transport_ready(db, row, wards)
                if evidence:
                    candidates.append({k: row[k] for k in ('id', 'name', 'lat', 'lon', 'coordinate_method', 'distance_km')} | evidence)
        merged: list[dict] = []
        for row in sorted(candidates, key=lambda r: (not r['official_registry'], -(r['registered_beds'] or 0), r['distance_km'])):
            twin = next((m for m in merged if same_site(m, row)), None)
            if twin:
                twin['merged_ids'].append(row['id'])
                continue
            merged.append(row | {'capacity': 8, 'occupied': 0, 'simulated_capacity': True, 'merged_ids': []})
        return sorted(merged, key=lambda r: r['distance_km'])[:limit]


def route_position(route: dict, progress: float) -> list[float]:
    points, distances = route['coordinates'], route['cumulative_km']
    target = max(0, min(1, progress)) * distances[-1]
    index = min(len(points) - 1, max(1, bisect.bisect_left(distances, target)))
    span = distances[index] - distances[index - 1]
    fraction = (target - distances[index - 1]) / span if span else 1
    return [points[index - 1][axis] + (points[index][axis] - points[index - 1][axis]) * fraction for axis in (0, 1)]


def ground_fallback(start: list[float], end: list[float]) -> dict:
    # Último recurso cuando ninguna red viaria conectada ni proveedor OSM ofrece trayectoria: línea ilustrativa
    # para que la unidad siempre salga en el mapa. No es geometría de carretera ni itinerario operativo.
    if not valid_point(start) or not valid_point(end):
        raise ValueError('Coordenadas no válidas para la trayectoria ilustrativa')
    distance = km(start, end)
    return {'coordinates': [list(start), list(end)], 'cumulative_km': [0, distance], 'distance_km': round(distance, 3),
            'duration_seconds': max(60, distance / 40 * 3600), 'mode': 'ground_fallback', 'approximate': True,
            'source': 'Trayectoria ilustrativa sin geometría viaria', 'fetched_at': time.time(),
            'limitations': 'Sin ruta viaria calculable: trayectoria recta ilustrativa para no dejar el aviso sin recursos. No representa carreteras ni tiempos reales.'}


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
        self.planner: Any
        if getattr(store, 'visual_demo', False) is True:
            from visual_demo import SilentProvider
            self.planner = SilentProvider()
        else:
            self.planner = planner if planner is not None else Planner(self.db)
        self.router = router if router is not None else LocalRouter(self.db)
        self.atlas = atlas if atlas is not None else EmergencyAtlas()
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.state: dict[str, Any] = {'session_id': self.session_id, 'mode': 'demo', 'status': 'idle' if self.planner.ready else 'unconfigured',
                                      'sequence': 0, 'events': [], 'resources': {}, 'assignments': {}, 'alerts': {},
                                      'last_fingerprint': '', 'last_review': 0, 'pending': None, 'history': [], 'runs': [],
                                      'field_revisions': {}, 'field_actions': {}, 'alert_requests': {}, 'notifications': [], 'delivery_sequence': 0}
        self.retry_at = 0.0
        self.failure_count = 0
        self.scene: Scene | None = None
        self.operations: Operations | None = None
        self.scene_saved_at = 0.0
        if getattr(store, 'hackathon', False) is True:
            self._setup_scenario()
        from autodispatch import AutoDispatch
        # Garantía de movilización (petición expresa 19/09/2026): bomberos de parques distintos, ambulancia y patrulla
        # salen sin esperar al planner LLM y el dispositivo se mantiene mientras el aviso siga activo.
        self.auto = AutoDispatch(self)

        if getattr(store, 'presentation', False) is True:
            from operations import Operations
            self.operations = Operations(self)

        self.visual = None
        if getattr(store, 'visual_demo', False) is True:
            from visual_demo import VisualDemo
            self.visual = VisualDemo(self)

    def _setup_scenario(self) -> None:
        from scene import Scene
        from local_routes import in_demo
        graph = self.router.demo_graph()
        self.scene = Scene(self)
        self.scene.data['network'] = {'nodes': len(graph.points), 'bounds': [41.28, 2.00, 41.54, 2.32], 'source': 'OpenStreetMap · red precargada local'}
        self.scene.data['hospitals'] = [h for h in self.atlas.hospitals(41.41, 2.15) if in_demo([h['lon'], h['lat']])]
        self.state['resources'] = {}
        for lat, lon in [(41.39, 2.17), (41.44, 2.10), (41.40, 2.23)]:
            for resource in self.atlas.nearby(lat, lon):
                if in_demo([resource['lon'], resource['lat']]):
                    self.state['resources'][resource['id']] = resource
        self.event('watch', 'Vigilancia de Barcelona, Collserola y costa', 'FIRMS, 112, NOAA y atlas reales; evolución, tráfico y recursos simulados. España permanece completa.')

    def reset_demo(self) -> None:
        """Vacía incidentes, avisos y despachos de simulaciones anteriores para empezar una demo desde cero.
        No toca `flare_contacts` (teléfonos de bomberos) ni credenciales/ajustes."""
        with self.lock:
            self.state.update(sequence=0, events=[], assignments={}, alerts={}, last_fingerprint='', last_review=0,
                              pending=None, history=[], runs=[], field_revisions={}, field_actions={},
                              alert_requests={}, notifications=[], delivery_sequence=0, auto={})
            self.state.pop('pending_alerts', None)
            self.state.pop('alert_cooldowns', None)
            self.retry_at = 0.0
            self.failure_count = 0
            if self.scene is not None:
                self._setup_scenario()
            if self.operations is not None:
                from operations import Operations
                self.operations = Operations(self)
            if self.visual is not None:
                from visual_demo import VisualDemo
                self.visual = VisualDemo(self)
            self.save()

    def station_inventory(self) -> list[dict]:
        stations: dict[str, dict] = {}
        for resource in self.state['resources'].values():
            station = stations.setdefault(resource['station_id'] + ':' + resource['kind'], {k: resource[k] for k in ('station_id', 'name', 'lat', 'lon', 'kind')} | {
                'total': 0, 'available': 0, 'busy': 0, 'simulated_capacity': True})
            station['total'] += 1
            station['busy' if resource['id'] in self.state['assignments'] else 'available'] += 1
        return list(stations.values())

    def public_state(self) -> dict:
        with self.lock:
            # El sondeo del mapa llega cada 500 ms: solo viajan los últimos eventos; el historial completo
            # sigue en /api/director/history (SQL) y el panel lo carga al abrirse.
            return deepcopy({k: self.state[k] for k in ('session_id', 'mode', 'status', 'sequence', 'assignments', 'alerts')}) | {
                'events': deepcopy(self.state['events'][-PUBLIC_EVENTS:]), 'server_time': time.time(), 'stations': self.station_inventory(),
                'scenario': deepcopy(self.scene.data) if self.scene else None, 'pending_alerts': deepcopy(self.state.get('pending_alerts', {})),
                'operations': self.operations.public_state() if self.operations else None, 'auto': self.auto.public_state()}

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
            self.state.get('pending_alerts', {}).pop(incident_id, None)
        self.event('alert' if kind == 'alert' else 'cancelled', 'ES-Alert enviado al simulador móvil' if kind == 'alert' else 'Aviso retirado por bomberos · demo', message, incident_id=incident_id)

    def propose_alert(self, incident_id: str, message: str, source: str) -> None:
        if not self.scene:
            self.notify(incident_id, message, source)
            return
        pending = self.state.setdefault('pending_alerts', {})
        if incident_id in pending or self.state.get('alert_cooldowns', {}).get(incident_id, 0) > time.time():
            return
        pending[incident_id] = {'id': str(uuid.uuid4()), 'incident_id': incident_id, 'message': message[:240],
                                'source': source, 'due_at': time.time() + 3, 'mode': 'simulation_only'}
        self.event('alert_proposed', 'ES-Alert propuesto · envío automático en 3 s', message, incident_id=incident_id)
        timer = threading.Timer(3, self.deliver_alert, args=(incident_id, pending[incident_id]['id']))
        timer.daemon = True
        timer.start()

    def deliver_alert(self, incident_id: str, proposal_id: str) -> None:
        with self.lock:
            proposal = self.state.get('pending_alerts', {}).get(incident_id)
            if not proposal or proposal['id'] != proposal_id:
                return
            self.notify(incident_id, proposal['message'], proposal['source'])
            self.state['pending_alerts'].pop(incident_id)
            self.state.setdefault('alert_cooldowns', {})[incident_id] = time.time() + 120
            self.save()

    def cancel_alert(self, identifier: str) -> None:
        with self.lock:
            key = next((k for k, a in self.state.get('pending_alerts', {}).items() if a['id'] == identifier), None)
            if key is None:
                raise ValueError('La propuesta ya no está pendiente')
            if self.state['pending_alerts'][key]['due_at'] <= time.time():
                self.deliver_alert(key, identifier)
                raise ValueError('El plazo de cancelación ha terminado')
            self.state['pending_alerts'].pop(key)
            self.state.setdefault('alert_cooldowns', {})[key] = time.time() + 120
            self.event('alert_cancelled', 'ES-Alert cancelado por el operador', 'El freno humano evitó el envío al simulador.', incident_id=key)
            self.save()

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
            team = {'ambulance': 'sanitarios', 'police': 'policía'}.get(self.state['resources'].get(report.get('resource_id'), {}).get('kind'), 'bomberos')
            self.event('field_report', f'Parte de {team} recibido', fields.get('detalle', fields.get('incendio', 'Actualización de situación')), incident_id=identifier)
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
                self.propose_alert(identifier, fields.get('detalle') or 'Solicitud expresa de bomberos. Aviso de emergencia simulado; no es una alerta real.', 'firefighter_request')
        return changed

    def event(self, kind: str, message: str, reason: str = '', **data) -> None:
        self.state['sequence'] += 1
        self.state['events'].append({'sequence': self.state['sequence'], 'kind': kind, 'message': message,
                                     'reason': reason, 'at': time.time(), **data})
        self.state['events'] = self.state['events'][-2000:]

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
            if self.scene:
                self.scene.enrich(incident, environment)
            samples = sorted(environment['potential']['samples'], key=lambda s: s.get('score') or 0, reverse=True)
            incidents.append({k: incident.get(k) for k in ('id', 'name', 'lat', 'lon', 'weather', 'demo_report', 'source_kind', 'sensor_report', 'scene_report', 'scenario', 'responder_report')} | {
                'environment': {k: environment.get(k) for k in ('population', 'landcover', 'wind', 'coverage', 'method')},
                'attention_samples': samples[:6], 'attention_model': environment['potential'].get('model'),
                'facilities': environment['potential'].get('facilities', [])[:12]})
        relevant.update(self.state['assignments'])
        resources = [r | {'assignment': self.state['assignments'].get(r['id'])} for r in self.state['resources'].values() if r['id'] in relevant]
        for r in resources:
            if r['assignment']:
                r['assignment'] = {k: v for k, v in r['assignment'].items() if k not in ('route', 'resource')}
        context = {'mode': 'simulation_only', 'incidents': incidents, 'resources': resources, 'stations': self.station_inventory(),
                   'dispatch_policy': 'Un dispositivo automático mínimo (camiones de parques distintos, ambulancia y patrulla) sale sin esperar tu plan y ya figura en resources[].assignment: no lo dupliques; añade, reasigna o retira según la situación. Si falla la ruta de una unidad propuesta para dispatch, el ejecutor intentará hasta tres sedes alternativas con unidades libres del mismo tipo. Nunca tomará unidades ocupadas ni reservadas para otra acción del plan. Si todas fallan, revisa otra sede en el siguiente plan.',
                   'alerts': self.state['alerts'], 'history': self.state['history'][-8:],
                   'source_status': payload.get('status'), 'at': time.time(), 'incident_limit': 8,
                   'field_reports': payload.get('demo', {}).get('field_reports', {}),
                   'capabilities': {'alert': 'ES-Alert simulado: petición expresa, parte crítico o decisión del agente por peligro para la población fundamentada en el parte actual (population_risk=true y report_evidence=copia íntegra de fields.detalle). No requiere que el bombero lo solicite; no_solicitado no es un veto. Humo genérico o entorno urbano no bastan. Nunca Cell Broadcast real.',
                                    'helicopter': 'Recurso ficticio en helipuerto real; disponible para solicitud aérea explícita o incendio confirmado que empeora. Vuelo ilustrativo, no protocolo español.',
                                    'reinforcements': 'Solicitudes de bomberos en responder_report.fields.refuerzos; valorar recursos libres y reassign entre incidentes con motivo y cobertura restante.'},
                   'omitted_incidents': max(0, len(reported(payload)) - 8),
                   'limits': 'Capacidades ficticias. Atlas no exhaustivo. Sin tráfico ni rutas de emergencia. Potencial no es probabilidad. No confirmar extinción por llegada de vehículos.'}
        if self.operations:
            for incident in incidents:
                incident.update(self.operations.context(incident['id']))
            context['presentation'] = True
            from reports import decision_memories
            context['memories'] = self.db.cached('memories', 30, lambda: decision_memories(self.db))
            context['memory_guidance'] = 'Consulta estas notas como contexto para tus decisiones y cita su título cuando resulten relevantes. curated_base es conocimiento inicial; simulation_observation son lecciones de operaciones anteriores. No sustituyen el parte actual, las restricciones ni la validación de recursos y rutas.'
        if self.scene:
            context['scenario'] = deepcopy(self.scene.data)
            context['capabilities'].update(ambulance='Ambulancias ficticias desde hospitales/bases del atlas. Riesgo vital, humo sobre barrio o población amenazada requieren valorar sanitario y policía, no solo camiones.',
                alert=context['capabilities']['alert'] + ' Toda propuesta habilitada se envía al receptor de simulación tras 3 segundos salvo cancelación humana.',
                helicopter='Apoyo aéreo ilustrativo admisible en aviso marítimo por llamada o riesgo alto del escenario.',
                lifecycle='active → contained → watching → releasing → closed. Contener requiere trabajo sostenido, no solo llegada. En releasing se ejecuta retirada; no movilices recursos nuevos.')
        context['revision'] = digest(context)
        return context

    def vehicle_origin(self, resource: dict) -> list[float]:
        assignment = self.state['assignments'].get(resource['id'])
        if not assignment:
            return [resource['lon'], resource['lat']]
        return assignment.get('held_position') or route_position(assignment['route'], (time.time() - assignment['started_at']) / assignment['travel_seconds'])

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
                if kind in {'reassign', 'return'} and not current:
                    raise ValueError('Disponibilidad incompatible con el plan')
                # Una unidad ya movilizada (p. ej. por el dispositivo automático) no se roba: se busca otra libre del mismo tipo.
                occupied = kind == 'dispatch' and current is not None
                resource = self.state['resources'][rid]
                destination = resource if kind == 'return' else incidents[item['incident_id']]
                report_run_id = (destination.get('demo_report') or {}).get('run_id') if kind != 'return' else None
                if report_run_id:
                    # A call can move from a coarse locality (or a nearby FIRMS group) to a
                    # precise address while keeping the same run.  Keep that stable identity
                    # on the vehicle so AutoDispatch can reconcile the assignment.
                    item['report_run_id'] = report_run_id
                scene = destination.get('scenario') or {}
                if self.scene and kind != 'return' and scene.get('phase') in {'releasing', 'closed'}:
                    item.update(route_error=True, blocked_reason='Aviso en retirada; no admite nuevas movilizaciones.')
                    prepared.append(item)
                    continue
                item['target'] = [destination['lon'], destination['lat']]
                if scene.get('maritime') and resource['kind'] != 'helicopter':
                    from scene import SHORE
                    item['target'] = list(SHORE)
                    item['reason'] += ' Apoyo terrestre en punto de encuentro costero; no circula por el mar.'
                if kind == 'reassign' and current['status'] != 'blocked' and current['incident_id'] == item['incident_id'] and current.get('target') == item['target']:
                    raise ValueError('El recurso ya está asignado a ese destino')
                fields = (incidents.get(item.get('incident_id'), {}).get('responder_report') or {}).get('fields', {})
                from operations import requested_resources
                field_versions = (incidents.get(item.get('incident_id'), {}).get('responder_report') or {}).get('field_versions', {})
                requested_air = requested_resources(fields, field_versions).get('helicopter', 0) > 0
                if resource['kind'] == 'helicopter' and kind != 'return' and not (self.scene and (scene.get('maritime') or scene.get('medical') or scene.get('priority', 0) >= 7) or requested_air or fields.get('incendio') == 'confirmado' and fields.get('evolucion') in {'empeora', 'critico'}):
                    item['route_error'] = True
                    item['blocked_reason'] = 'Apoyo aéreo pendiente de solicitud explícita o empeoramiento confirmado en un parte de bomberos.'
                    prepared.append(item)
                    continue
                alternatives = sorted((r for r in context['resources'] if kind == 'dispatch' and resource['kind'] != 'helicopter'
                    and r['kind'] == resource['kind'] and r['id'] not in reserved and r['id'] not in self.state['assignments']
                    and km([r['lon'], r['lat']], item['target']) <= 60), key=lambda r: km([r['lon'], r['lat']], item['target']))
                attempted: set[str] = set()
                for candidate in [*([] if occupied else [resource]), *alternatives]:
                    station = candidate['station_id']
                    if station in attempted or len(attempted) >= 4:
                        continue
                    attempted.add(station)
                    failure_key = (station, *item['target'])
                    if kind == 'dispatch' and failure_key in failed_stations:
                        continue
                    try:
                        routing = self.scene.route if self.scene else self.router.route
                        item['route'] = air_route(self.vehicle_origin(candidate), item['target']) if candidate['kind'] == 'helicopter' else routing(self.vehicle_origin(candidate), item['target'])
                        if candidate['id'] != rid:
                            item.update(resource_id=candidate['id'], requested_resource_id=rid)
                            reserved.add(candidate['id'])
                        break
                    except (OSError, ValueError, RuntimeError) as error:
                        item['blocked_reason'] = 'No se pudo calcular una ruta utilizable; se revisarán alternativas. ' + str(error)[:160]
                        if kind == 'dispatch':
                            failed_stations.add(failure_key)
                if 'route' not in item and occupied:
                    item.update(route_error=True, blocked_reason='La unidad pedida ya está movilizada por otra decisión y no queda otra libre del mismo tipo con ruta.')
                    prepared.append(item)
                    continue
                if 'route' not in item:
                    # Garantía de movilización: red viaria sin sentidos desde la unidad pedida y, si tampoco, trayectoria ilustrativa.
                    origin = self.vehicle_origin(resource)
                    try:
                        item['route'] = routing(origin, item['target'], relaxed=True)
                    except (OSError, ValueError, RuntimeError):
                        item['route'] = ground_fallback(origin, item['target'])
                    item['route_fallback'] = item.pop('blocked_reason', 'Ruta estricta no disponible')
            if kind == 'alert':
                incident = incidents[item['incident_id']]
                fields = (incident.get('responder_report') or {}).get('fields', {})
                from operations import alert_allowed
                item['mobile_alert'] = alert_allowed(fields, item)
            prepared.append(item)
        return prepared

    def apply(self, plan: dict, actions: list[dict], run_id: str) -> None:
        if self.operations:
            self.operations.accept_assessments(plan)
        blocked = any(action.get('route_error') for action in actions)
        self.event('decision', 'Plan con rutas pendientes; revisando alternativas' if blocked else plan['summary'], plan['summary'] if blocked else '', run_id=run_id)
        if self.scene:
            assumption = str(plan.get('assumption') or 'Accesos transitables, viento estable y capacidad ficticia disponible.')[:240]
            self.event('assumption', 'Supuesto clave del plan', assumption, run_id=run_id)
            for record in self.scene.data['incidents'].values():
                record['assumption'] = assumption
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
                previous_assignment = self.state['assignments'].get(rid, {})
                if kind == 'return' and self.scene:
                    incident_id = self.state['assignments'][rid]['incident_id']
                    data['incident_id'] = incident_id
                if action.get('requested_resource_id'):
                    self.event('alternative', 'Recurso alternativo disponible · ' + resource['name'], 'Sustituye una unidad sin ruta utilizable; mismo tipo y sin retirar recursos de otros avisos.', resource_id=rid, requested_resource_id=action['requested_resource_id'], **data)
                route = action['route']
                if action.get('route_fallback'):
                    self.event('approximate', 'Trayectoria aproximada · ' + resource['name'], route.get('limitations', '') + ' ' + str(action['route_fallback'])[:160], resource_id=rid, **data)
                delay = departures.get(resource['station_id'], 0) * 4 if kind == 'dispatch' else 0
                departures[resource['station_id']] = departures.get(resource['station_id'], 0) + 1
                self.state['assignments'][rid] = {'id': f'{run_id}:{rid}', 'resource': resource, 'incident_id': incident_id,
                    'route': route, 'target': action['target'], 'started_at': time.time() + delay, 'travel_seconds': max(45, min(150, route['duration_seconds'] / 30)),
                    'status': 'returning' if kind == 'return' else 'enroute', 'time_scale': 'accelerated_demo', 'reason': action['reason'],
                    'report_run_id': action.get('report_run_id') or previous_assignment.get('report_run_id')}
                noun = {'fire_engine': 'camión de bomberos', 'police': 'patrulla', 'ambulance': 'ambulancia', 'helicopter': 'helicóptero de demo'}[resource['kind']]
                message = f'{"Regresa" if kind == "return" else "Reasignando" if kind == "reassign" else "Movilizando"} 1 {noun} · {resource["name"]}'
                self.event(kind, message, action['reason'], resource_id=rid, **data)
            elif kind == 'alert':
                current_alert = self.state['alerts'].get(incident_id, {})
                if current_alert.get('mode') == 'mobile_simulation' and current_alert.get('expires_at', 0) > time.time():
                    continue
                if action.get('mobile_alert'):
                    self.propose_alert(str(incident_id), action['reason'], 'director_decision')
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
            if assignment['status'] in {'onscene', 'blocked'} or time.time() < assignment['started_at'] + assignment['travel_seconds']:
                continue
            if assignment['status'] == 'returning':
                del self.state['assignments'][rid]
                self.event('available', 'Recurso de nuevo disponible', assignment['resource']['name'])
            else:
                transported = assignment['status'] == 'transporting'
                assignment.update(status='onscene', arrived_at=time.time())
                if transported:
                    assignment['patient_delivered'] = True
                self.event('hospital' if transported else 'arrived', 'Paciente ficticio recibido en hospital' if transported else 'Recurso en el punto de encuentro', 'No implica alta médica ni extinción. ' + assignment['resource']['name'], incident_id=assignment['incident_id'])
            changed = True
        for identifier, proposal in list(self.state.get('pending_alerts', {}).items()):
            if time.time() >= proposal['due_at']:
                self.notify(identifier, proposal['message'], proposal['source'])
                del self.state['pending_alerts'][identifier]
                self.state.setdefault('alert_cooldowns', {})[identifier] = time.time() + 120
                changed = True
        for identifier, alert in list(self.state['alerts'].items()):
            if time.time() >= alert['expires_at']:
                del self.state['alerts'][identifier]
                changed = True
        return changed

    def step(self) -> None:
        if self.visual is not None:
            self.visual.step()
            return
        payload = self.store.payload()
        with self.lock:
            previous = deepcopy(self.state)
            try:
                if self.scene:
                    sequence = self.state['sequence']
                    self.scene.observe(payload)
                    self.scene.evolve()
                    self.scene.maintenance()
                    if sequence != self.state['sequence'] or time.monotonic() - self.scene_saved_at >= 5:
                        self.save()
                        self.scene_saved_at = time.monotonic()
                if self.ingest_field_reports(payload):
                    self.save()
            except Exception:
                self.state = previous
                raise
            moved = self.advance()
            if moved:
                self.save()
        # Dispositivo automático: usa la carga con el escenario ya observado; calcula rutas fuera del cerrojo.
        if self.auto.tick(self.store.payload()):
            moved = True
        with self.lock:
            if self.operations:
                self.operations.tick(payload)
                if not self.operations.ready():
                    self.state['status'] = 'collecting'
                    return
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
            key = anchor if pending.get('anchor') else fingerprint
            expected = pending.get('anchor') or pending['fingerprint']
            executable = key(payload) == expected
            actions = self.prepare(plan, pending['context']) if executable else []
            with self.lock:
                if not executable or key(self.store.payload()) != expected:
                    self.event('superseded', 'El aviso ha cambiado de ubicación o de condiciones; revisando el plan')
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
            self.state['status'] = 'thinking'
            self.event('thinking', 'Analizando cambios y recursos disponibles')
            self.save()
        context = self.context(payload)
        run_id = self.planner.start(context)
        with self.lock:
            self.state['runs'].append(time.time())
            self.state['pending'] = {'run_id': run_id, 'context': context, 'fingerprint': current,
                                     'anchor': anchor(payload), 'started_at': time.time()}
            self.save()

    def loop(self) -> None:
        while not self.stop_event.is_set():
            with self.db.verification_lock(804030) as acquired:
                with self.lock:
                    self.state['status'] = ('idle' if self.planner.ready else 'unconfigured') if acquired else 'standby'
                while acquired and not self.stop_event.is_set():
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
                    self.stop_event.wait(.5 if self.scene else 2)
            self.stop_event.wait(2)
