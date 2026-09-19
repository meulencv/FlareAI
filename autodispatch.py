"""Dispositivo automático garantizado del simulador.

Petición expresa (19/09/2026): cuando hay un aviso activo tienen que salir bomberos de parques distintos,
una ambulancia y una patrulla sin esperar al planner LLM, escalar con el crecimiento del escenario y con
los partes de bomberos, extinguir el fuego con trabajo sostenido y volver a base. Es determinista y ficticio:
unidades y capacidades del atlas simuladas, tiempos acelerados, sin protocolo real. El planner LLM sigue
pudiendo añadir, reasignar o retirar recursos; esta capa solo garantiza el mínimo mientras el fuego siga activo.
"""
from __future__ import annotations

import time
import uuid
from copy import deepcopy

from local_routes import km

BASELINE = {'fire_engine': 3, 'ambulance': 1, 'police': 1}
MAX_ENGINES = 6
MAX_RANGE_KM = 60
LOCATION_REDIRECT_KM = 20   # cerca del punto corregido: continúa desde su posición; lejos: vuelve y sale otro dispositivo
LOCATION_EPSILON_KM = .15   # evita recalcular por redondeos de geocodificación
WAVE_COOLDOWN = 20          # segundos entre oleadas automáticas por aviso
CONTAIN_WORK = 90           # medios × segundos de trabajo en el lugar para contener: 2 camiones 45 s, 3 en 30 s, 5 en 18 s
STRUGGLE_SECONDS = 120      # activo con medios en el lugar sin contener: un camión más
PHASES = {'active': 'En intervención', 'contained': 'Fuego contenido', 'watching': 'En vigilancia',
          'releasing': 'Retirada escalonada', 'closed': 'Cerrado · simulación'}


def pick(free: list[dict], count: int, engaged: set[str]) -> list[dict]:
    """Reparte entre sedes distintas: primero una unidad por sede aún no movilizada en el aviso,
    después una por sede restante y, si hace falta, el resto por cercanía."""
    chosen: list[dict] = []
    taken: set[str] = set()
    used: set[str] = set()
    for stage in range(3):
        for resource in free:
            if len(chosen) >= count:
                return chosen
            station = resource['station_id']
            if resource['id'] in taken or stage == 0 and (station in engaged or station in used) or stage == 1 and station in used:
                continue
            chosen.append(resource)
            taken.add(resource['id'])
            used.add(station)
    return chosen


class AutoDispatch:
    def __init__(self, director) -> None:
        self.director = director
        self.enabled = getattr(director.store, 'auto_dispatch', True) is not False
        director.state.setdefault('auto', {})

    @property
    def records(self) -> dict:
        return self.director.state['auto']

    def assigned(self, identifier: str) -> list[dict]:
        return [a for a in self.director.state['assignments'].values() if a.get('incident_id') == identifier]

    def resources(self, incident: dict) -> list[dict]:
        record = self.records[incident['id']]
        point = [incident['lon'], incident['lat']]
        if not record.get('atlas_loaded'):
            for resource in self.director.atlas.nearby(incident['lat'], incident['lon']):
                self.director.state['resources'].setdefault(resource['id'], resource)
            record['atlas_loaded'] = True
        return sorted((r for r in self.director.state['resources'].values() if km([r['lon'], r['lat']], point) <= MAX_RANGE_KM),
                      key=lambda r: km([r['lon'], r['lat']], point))

    def required(self, incident: dict, record: dict, fields: dict, now: float) -> dict[str, int]:
        scene = incident.get('scenario') or {}
        if (scene.get('phase') or record['phase']) != 'active':
            return {}
        radius = scene.get('radius_km') or 0
        engines = BASELINE['fire_engine'] + (radius >= .45) + (radius >= .8)
        medical = bool(scene.get('medical') or record.get('medical'))
        if fields.get('evolucion') in {'empeora', 'critico'}:
            engines += 2
            medical = True
        if record.get('first_arrival') and now - record['first_arrival'] >= STRUGGLE_SECONDS:
            engines += 1
        if scene.get('maritime'):
            engines = min(engines, 2)
        return {'fire_engine': min(MAX_ENGINES, engines), 'ambulance': 2 if medical else 1, 'police': 1}

    def dispatch(self, incident: dict, wanted: dict[str, int], summary: str, reason: str) -> int:
        identifier = incident['id']
        director = self.director
        with director.lock:
            assignments = director.state['assignments']
            resources = self.resources(incident)
            engaged = {a['resource']['station_id'] for a in self.assigned(identifier)}
            actions, reserved = [], set()
            for kind, count in wanted.items():
                free = [r for r in resources if r['kind'] == kind and r['id'] not in assignments and r['id'] not in reserved]
                for resource in pick(free, count, engaged):
                    reserved.add(resource['id'])
                    actions.append({'type': 'dispatch', 'incident_id': identifier, 'resource_id': resource['id'], 'reason': reason})
            if not actions:
                return 0
            plan = {'revision': 'auto', 'summary': summary[:240], 'actions': actions[:8]}
            context = {'revision': 'auto', 'incidents': [deepcopy(incident)], 'resources': deepcopy(resources)}
        # Las rutas pueden consultar proveedores OSM: se calculan fuera del cerrojo para no congelar la API.
        prepared = director.prepare(plan, context)
        with director.lock:
            # Solo se aplican unidades que sigan libres: otra decisión pudo adelantarse mientras se calculaban rutas.
            prepared = [a for a in prepared if a.get('route_error') or a['resource_id'] not in director.state['assignments']]
            if not any(not a.get('route_error') for a in prepared):
                return 0
            director.apply(plan, prepared, f'auto:{uuid.uuid4().hex[:8]}')
            director.save()
        return sum(1 for a in prepared if not a.get('route_error'))

    def ensure(self, incident: dict, record: dict, fields: dict, now: float) -> bool:
        """Mantiene el nivel mínimo de medios mientras el aviso siga activo, aunque el planner LLM
        haya retirado unidades o una ruta haya fallado."""
        if now - record['wave_at'] < WAVE_COOLDOWN:
            return False
        required = self.required(incident, record, fields, now)
        if not required:
            return False
        present: dict[str, int] = {}
        for assignment in self.assigned(incident['id']):
            if assignment['status'] != 'returning':
                present[assignment['resource']['kind']] = present.get(assignment['resource']['kind'], 0) + 1
        wanted = {kind: count - present.get(kind, 0) for kind, count in required.items() if count > present.get(kind, 0)}
        if not wanted:
            return False
        record['wave_at'] = now
        first = not record.get('baseline_at')
        stations = len({r['station_id'] for r in self.resources(incident) if r['kind'] == 'fire_engine'})
        summary = ('Dispositivo automático: salen bomberos de parques distintos, ambulancia y patrulla' if first
                   else 'Refuerzo automático: el fuego sigue activo y se amplía el dispositivo')
        reason = ('Salida inmediata del simulador al recibir el aviso; no espera al planner. Unidades y tiempos ficticios.' if first
                  else 'Nivel mínimo de medios mientras el aviso siga activo; se reparte entre sedes disponibles.')
        sent = self.dispatch(incident, wanted, summary, reason)
        if first and sent:
            record['baseline_at'] = now
        elif not sent:
            self.director.event('auto_pending', 'Sin unidades libres a menos de 60 km', f'Se reintenta en {WAVE_COOLDOWN} s. Parques ficticios considerados: {stations}.', incident_id=incident['id'])
        return True

    def requests(self, incident: dict, record: dict, report: dict, now: float) -> bool:
        """Solicitudes explícitas de un parte de bomberos (refuerzos, ambulancias, helicópteros, policía).
        En presentación las tramita `Operations.reinforce`; aquí el resto de modos."""
        if self.director.operations is not None or not report or record['phase'] in {'releasing', 'closed'}:
            return False
        from operations import requested_resources
        fields, versions = report.get('fields', {}), report.get('field_versions', {})
        changed = False
        for kind, count in requested_resources(fields, versions).items():
            revision = max(versions.get(k, 0) for k in {'fire_engine': ('bomberos', 'refuerzos'), 'ambulance': ('ambulancias', 'ambulancia'),
                                                        'helicopter': ('helicopteros', 'helicoptero'), 'police': ('policias', 'policia')}[kind])
            request = record['requests'].setdefault(kind, {'revision': -1, 'quantity': 0, 'fulfilled': 0, 'retry_at': 0})
            if revision > request['revision']:
                request.update(revision=revision, quantity=count, fulfilled=0, retry_at=0)
            if request['fulfilled'] >= request['quantity'] or now < request['retry_at']:
                continue
            remaining = request['quantity'] - request['fulfilled']
            noun = {'fire_engine': 'camiones', 'ambulance': 'ambulancias', 'helicopter': 'helicópteros', 'police': 'patrullas'}[kind]
            sent = self.dispatch(incident, {kind: remaining}, f'Bomberos pide {remaining} {noun}: se envían desde otras sedes',
                                 'Solicitud explícita en el parte de bomberos; ejecución obligatoria en el simulador.')
            request['fulfilled'] += sent
            request['retry_at'] = now + 15
            if record['phase'] != 'active' and not incident.get('scenario'):
                record.update(phase='active', phase_at=now, suppression_since=None)
            changed = True
        return changed

    def go_home(self, rid: str, assignment: dict, now: float) -> None:
        from director import air_route, ground_fallback
        resource = assignment['resource']
        origin = self.director.vehicle_origin(resource)
        target = [resource['lon'], resource['lat']]
        try:
            route = air_route(origin, target) if resource['kind'] == 'helicopter' else self.director.router.route(origin, target)
        except (OSError, ValueError, RuntimeError):
            try:
                route = self.director.router.route(origin, target, relaxed=True)
            except (OSError, ValueError, RuntimeError, TypeError):
                route = ground_fallback(origin, target)
        assignment.pop('held_position', None)
        assignment.update(route=route, target=target, status='returning', started_at=now,
                          travel_seconds=max(5, min(15, route['duration_seconds'] / 60)), route_revision=int(now))
        self.director.event('return', 'Regresa · ' + resource['name'], 'Fin de la intervención; regreso acelerado de demo. La unidad sigue ocupada hasta llegar a sede.',
                            incident_id=assignment['incident_id'], resource_id=rid)

    @staticmethod
    def report_run_id(incident: dict) -> str | None:
        return (incident.get('demo_report') or {}).get('run_id')

    def reconcile_locations(self, incidents: list[dict], now: float) -> bool:
        """Reconcilia una corrección de ubicación de la misma llamada.

        El overlay puede cambiar de un grupo FIRMS/localidad a un aviso puntual y, con ello,
        cambiar también el id visible. La identidad estable es el run de la llamada. Las
        unidades próximas se enrutan desde su posición actual; las lejanas regresan y quedan
        disponibles solo al alcanzar su sede. `ensure` completará después el mínimo en el
        destino nuevo con unidades libres.
        """
        current = {run_id: incident for incident in incidents if (run_id := self.report_run_id(incident))}
        candidates: list[tuple[str, dict, dict, float]] = []
        with self.director.lock:
            for rid, assignment in self.director.state['assignments'].items():
                if assignment.get('status') in {'returning', 'transporting'}:
                    continue
                run_id = assignment.get('report_run_id')
                # Compatibility for call-only assignments saved before report_run_id existed.
                if not run_id and str(assignment.get('incident_id', '')).startswith('demo:'):
                    run_id = str(assignment['incident_id'])[5:]
                    assignment['report_run_id'] = run_id
                incident = current.get(run_id)
                if not incident:
                    continue
                target = [incident['lon'], incident['lat']]
                if assignment.get('incident_id') == incident['id'] and km(assignment.get('target', target), target) <= LOCATION_EPSILON_KM:
                    continue
                origin = self.director.vehicle_origin(assignment['resource'])
                candidates.append((rid, deepcopy(assignment), deepcopy(incident), km(origin, target)))

        changed = False
        for rid, snapshot, incident, distance in candidates:
            if distance > LOCATION_REDIRECT_KM:
                with self.director.lock:
                    assignment = self.director.state['assignments'].get(rid)
                    if not assignment or assignment.get('id') != snapshot.get('id'):
                        continue
                    self.go_home(rid, assignment, now)
                    self.director.event('location_correction', 'Ubicación corregida · sale un dispositivo nuevo',
                                        f'{assignment["resource"]["name"]} estaba a {distance:.1f} km del punto corregido y regresa a base.',
                                        incident_id=incident['id'], resource_id=rid)
                    self.director.save()
                    changed = True
                continue

            plan = {'revision': 'auto-location', 'summary': 'Ubicación corregida: se redirigen los medios próximos', 'actions': [{
                'type': 'reassign', 'incident_id': incident['id'], 'resource_id': rid,
                'reason': 'Corrección de la misma llamada; continúa desde su posición actual por proximidad al nuevo punto.'}]}
            context = {'revision': 'auto-location', 'incidents': [incident],
                       'resources': deepcopy(list(self.director.state['resources'].values()))}
            prepared = self.director.prepare(plan, context)
            with self.director.lock:
                assignment = self.director.state['assignments'].get(rid)
                if not assignment or assignment.get('id') != snapshot.get('id'):
                    continue
                self.director.apply(plan, prepared, f'location:{uuid.uuid4().hex[:8]}')
                self.director.event('location_correction', 'Medio redirigido al punto corregido',
                                    f'{assignment["resource"]["name"]} estaba a {distance:.1f} km y continúa sin volver a su sede.',
                                    incident_id=incident['id'], resource_id=rid)
                self.director.save()
                changed = True
        return changed

    def lifecycle(self, incident: dict, record: dict, fields: dict, report: dict, now: float) -> bool:
        """Evolución ilustrativa para avisos sin escenario de sala: contención con trabajo sostenido,
        vigilancia, retirada y cierre. Nunca modifica las observaciones NASA ni confirma extinción real."""
        if incident.get('scenario'):
            return False
        identifier = incident['id']
        assignments = self.assigned(identifier)
        arrived = [a for a in assignments if a['status'] == 'onscene']
        revision = report.get('revision', 0) if report else 0
        if revision > record['field_revision']:
            record['field_revision'] = revision
            if fields.get('incendio') in {'descartado', 'extinguido'} and record['phase'] in {'active', 'contained', 'watching'}:
                record.update(phase='releasing', phase_at=now)
                self.director.event('release', 'Bomberos informa: ' + str(fields['incendio']) + ' · retirada', 'Regresan las unidades de la simulación.', incident_id=identifier)
            elif fields.get('evolucion') in {'empeora', 'critico'} or fields.get('refuerzos') == 'solicitado':
                if record['phase'] != 'active':
                    self.director.event('field_report', 'Reactivación comunicada por bomberos', 'El dispositivo vuelve a intervención.', incident_id=identifier)
                record.update(phase='active', phase_at=now, suppression_since=None, medical=True, work=min(record.get('work', 0), CONTAIN_WORK * .5))
        phase = record['phase']
        changed = False
        elapsed = min(10, max(0, now - record.get('last_tick', now)))
        record['last_tick'] = now
        if phase == 'active':
            # Extinción progresiva: cada medio en el lugar suma trabajo; más recursos, contención antes.
            suppression = sum(1 if a['resource']['kind'] == 'fire_engine' else 2 if a['resource']['kind'] == 'helicopter' else 0 for a in arrived)
            operations = self.director.operations
            record['waiting_suppression'] = bool(operations and operations.held(identifier, suppression=True))
            if record['waiting_suppression']:
                suppression = 0
            record['suppression_power'] = suppression
            if suppression >= 1:
                record['suppression_since'] = record['suppression_since'] if record['suppression_since'] is not None else now
                record['work'] = record.get('work', 0) + elapsed * suppression
                record['extinguished_pct'] = min(100, round(100 * record['work'] / CONTAIN_WORK))
                if record['work'] >= CONTAIN_WORK:
                    record.update(phase='contained', phase_at=now)
                    self.director.event('contained', 'Fuego contenido · simulación', f'{suppression} medios trabajando en el lugar. Llegar no bastaba; no es extinción medida.', incident_id=identifier)
                    changed = True
            else:
                record['suppression_since'] = None
        if record['phase'] in {'contained', 'watching'}:
            record.update(phase='releasing', phase_at=now, extinguished_pct=100)
            self.director.event('release', 'Fuego apagado · regreso inmediato', 'Sin espera de vigilancia en la demo. Las unidades siguen ocupadas hasta llegar a base.', incident_id=identifier)
            changed = True
        if record['phase'] == 'releasing':
            for rid, assignment in self.director.state['assignments'].items():
                if assignment.get('incident_id') == identifier and assignment['status'] not in {'returning', 'transporting'}:
                    self.go_home(rid, assignment, now)
                    changed = True
            if not assignments:
                record.update(phase='closed', phase_at=now)
                self.director.event('closed', 'Cerrado · simulación', 'Medios de regreso en base. Datos NASA intactos.', incident_id=identifier)
                changed = True
        return changed

    def orphans(self, present: set[str], now: float) -> bool:
        """Avisos que desaparecen de la sesión (112 retira la llamada) sin escenario que los gobierne:
        sus unidades regresan y el registro se cierra."""
        changed = False
        for identifier, record in self.records.items():
            if identifier in present or record['phase'] == 'closed':
                continue
            for rid, assignment in self.director.state['assignments'].items():
                if assignment.get('incident_id') == identifier and assignment['status'] not in {'returning', 'transporting'}:
                    self.go_home(rid, assignment, now)
                    changed = True
            if record['phase'] != 'releasing':
                record.update(phase='releasing', phase_at=now)
                changed = True
            if not self.assigned(identifier):
                record.update(phase='closed', phase_at=now)
                changed = True
        return changed

    def tick(self, payload: dict) -> bool:
        from director import reported
        if not self.enabled:
            return False
        now = time.time()
        changed = False
        reports = payload.get('demo', {}).get('field_reports', {})
        incidents = reported(payload)
        changed |= self.reconcile_locations(incidents, now)
        with self.director.lock:
            for incident in incidents:
                identifier = incident['id']
                record = self.records.setdefault(identifier, {'phase': 'active', 'phase_at': now, 'since': now, 'suppression_since': None,
                                                              'wave_at': 0, 'requests': {}, 'medical': False, 'field_revision': 0})
                report = incident.get('responder_report') or reports.get(identifier) or {}
                if incident.get('scenario'):
                    record['phase'] = incident['scenario'].get('phase') or 'active'
                if not record.get('first_arrival') and any(a['status'] == 'onscene' for a in self.assigned(identifier)):
                    record['first_arrival'] = now
                changed |= self.lifecycle(incident, record, report.get('fields', {}), report, now)
            changed |= self.orphans({i['id'] for i in incidents} | {i['id'] for i in payload.get('incidents', [])}, now)
            if changed:
                self.director.save()
        for incident in incidents:
            record = self.records[incident['id']]
            report = incident.get('responder_report') or reports.get(incident['id']) or {}
            changed |= self.ensure(incident, record, report.get('fields', {}), now)
            changed |= self.requests(incident, record, report, now)
        return changed

    def public_state(self) -> dict:
        return {identifier: {'phase': record['phase'], 'label': PHASES[record['phase']], 'baseline_at': record.get('baseline_at'),
                             'suppression_power': record.get('suppression_power', 0), 'extinguished_pct': record.get('extinguished_pct', 0),
                             'requests': deepcopy(record['requests'])} for identifier, record in self.records.items()}
