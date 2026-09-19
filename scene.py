from __future__ import annotations

import math
import random
import re
import time
from copy import deepcopy
from datetime import datetime

from fireshape import fire_polygon
from local_routes import in_demo, km

PHASES = {'active': 'En intervención', 'contained': 'Fuego contenido', 'watching': 'En vigilancia',
          'releasing': 'Retirada escalonada', 'closed': 'Cerrado · seguro en el escenario'}
SHORE = [2.1964, 41.388]
SAFE_HOSPITAL_KM = 1.5
# Extinción progresiva (petición expresa 19/09/2026): el fuego crece a ritmo fijo y cada medio trabajando en el
# lugar (camión 1, helicóptero 2) lo reduce; más recursos, extinción antes. Con un solo camión apenas se frena.
GROWTH_KM_PER_S = .0025
SUPPRESSION_KM_PER_S = .0022
MANUAL_GROWTH_KM_PER_S = .0125
CONTAINED_RADIUS_KM = .06


def hospital_options(hospitals: list[dict], record: dict) -> tuple[list[dict], list[dict], float]:
    """Hospitales con plaza ficticia libre, primero los que quedan fuera del entorno de amenaza del
    escenario. Margen ilustrativo del simulador: no es un criterio sanitario ni una evacuación real."""
    origin = [record['lon'], record['lat']]
    margin = record['radius_km'] + SAFE_HOSPITAL_KM
    distances = {h['id']: km(origin, [h['lon'], h['lat']]) for h in hospitals}
    free = sorted((h for h in hospitals if h['occupied'] < h['capacity']), key=lambda h: distances[h['id']])
    safe = [h for h in free if distances[h['id']] >= margin]
    near = [h for h in free if distances[h['id']] < margin]
    return (safe + near, near, margin) if safe else (near, [], margin)


def sensor_candidate(item: dict, now: float) -> bool:
    try:
        age = now - datetime.fromisoformat(item['last_seen'].replace('Z', '+00:00')).timestamp()
    except (ValueError, KeyError):
        return False
    return (item.get('source_kind') not in {'call', 'scenario'} and in_demo([item['lon'], item['lat']])
            and 0 <= age <= 86400 and (item.get('frp_peak_mw') or 0) >= 15
            and any(d.get('confidence') == 'high' for d in item.get('detections', [])))


def satellite_contrast(item: dict, incidents: list[dict]) -> dict:
    matches = [(km([item['lon'], item['lat']], [d['lon'], d['lat']]), i, d)
               for i in incidents if i.get('observations', 0) > 0 for d in i.get('detections', [])]
    nearest = min(matches, key=lambda match: match[0], default=None)
    if nearest and nearest[0] <= 10:
        distance, source, detection = nearest
        return {'mode': 'observed', 'label': 'Contrastado con detección FIRMS cercana · no confirma fuego',
                'distance_km': round(distance, 2), 'incident_id': source['id'], 'at': detection.get('at')}
    return {'mode': 'simulated', 'label': 'Contraste satelital simulado · sin coincidencia FIRMS real'}


def visual_geometry(record: dict) -> dict:
    return fire_polygon(record['lon'], record['lat'], record['radius_km'], record['wind_to'], str(record['id']))


class Scene:
    def __init__(self, director) -> None:
        self.director = director
        director.state['scenario'] = {'enabled': True, 'revision': 0, 'plan_revision': 0, 'incidents': {}, 'candidates': {},
                                      'closures': {}, 'congestion': {}, 'hospitals': [], 'automatic': True,
                                      'label': 'SIMULACIÓN DE SALA · no moviliza servicios reales'}
        self.samples: dict[str, list] = {}

    @property
    def data(self) -> dict:
        return self.director.state['scenario']

    def change(self, kind: str, message: str, reason: str, identifier: str | None = None) -> None:
        self.data['revision'] += 1
        self.director.event(kind, message, reason, incident_id=identifier, simulation=True)

    def observe(self, payload: dict, now: float | None = None) -> None:
        now = time.time() if now is None else now
        valid = set()
        present = {i['id'] for i in payload.get('incidents', [])}
        for identifier, record in self.data['incidents'].items():
            if identifier in present or record['phase'] in {'releasing', 'closed'}:
                continue
            if record['source'] == 'call':
                record.update(phase='releasing', phase_at=now, radius_km=.02)
                self.change('cancelled', 'Aviso retirado de la sesión', 'El 112 o un parte de campo retira el aviso. Se retira el dispositivo sin borrar las observaciones satélite.', identifier)
        for item in payload.get('incidents', []):
            identifier = item['id']
            if not in_demo([item['lon'], item['lat']]):
                continue
            call = item.get('demo_report')
            if call and call.get('cancelled'):
                record = self.data['incidents'].get(identifier)
                if record and record['phase'] not in {'releasing', 'closed'}:
                    record.update(phase='releasing', phase_at=now, radius_km=.02)
                    self.change('contained', 'Parte de campo: se retira el aviso', 'No se borran las observaciones NASA. Regresan las unidades de demo.', identifier)
                continue
            if not call and not item.get('scene_report'):
                if getattr(self.director, 'operations', None) or not sensor_candidate(item, now):
                    continue
                valid.add(identifier)
                if identifier not in self.data['candidates']:
                    self.data['candidates'][identifier] = now
                    self.change('detected', 'Detectado · señal FIRMS fuerte', 'FRP ≥15 MW y confianza alta. Comprobación de persistencia durante 8 s; no es confirmación oficial.', identifier)
                if now - self.data['candidates'][identifier] < 8:
                    continue
            record = self.data['incidents'].get(identifier)
            if record:
                field = item.get('responder_report') or {}
                revision = field.get('revision', 0)
                if revision > record.get('field_revision', 0):
                    record['field_revision'] = revision
                    fields = field.get('fields', {})
                    if fields.get('incendio') in {'extinguido', 'descartado'}:
                        record.update(phase='contained', phase_at=now)
                    elif fields.get('evolucion') in {'empeora', 'critico'} or fields.get('refuerzos') == 'solicitado':
                        record.update(phase='active', medical=True, suppression_since=None)
                    from operations import requested_resources
                    requests = requested_resources(fields, field.get('field_versions'))
                    if requests and record['phase'] not in {'releasing', 'closed'}:
                        record.update(phase='active', suppression_since=None)
                    if requests.get('ambulance'):
                        record['medical'] = True
                    self.invalidate(identifier, 'Un parte de campo modifica la situación del aviso')
                summary = (call or {}).get('summary', {})
                signature = repr(sorted(summary.items()))
                if signature != record.get('summary_signature'):
                    text = ' '.join(str(v) for v in summary.values()).lower()
                    text = re.sub(r'\b(?:sin|no hay) (?:heridos|personas atrapadas)\b', '', text)
                    record['medical'] = bool(re.search(r'herid|atrapad|no respira|humo|personas en peligro', text)) or record['medical']
                    record['summary_signature'] = signature
                    record['contrast'] = satellite_contrast(item, payload['incidents'])
                    self.invalidate(identifier, 'La ficha del 112 aporta una corrección de riesgos o ubicación')
                if (record['lat'], record['lon']) != (item['lat'], item['lon']):
                    record.update(lat=item['lat'], lon=item['lon'])
                    self.samples.pop(identifier, None)
                    self.invalidate(identifier, 'El equipo o el 112 ha corregido la ubicación')
                continue
            if len(self.data['incidents']) >= 32:
                continue
            contrast = satellite_contrast(item, payload['incidents'])
            summary = (call or {}).get('summary', {})
            text = ' '.join(str(v) for v in summary.values()).lower()
            text = re.sub(r'\b(?:sin|no hay) (?:heridos|personas atrapadas)\b', '', text)
            medical = bool(re.search(r'herid|atrapad|no respira|humo|personas en peligro', text))
            maritime = bool((call or {}).get('location', {}).get('maritime'))
            record = {'id': identifier, 'name': item['name'], 'lat': item['lat'], 'lon': item['lon'],
                      'source': 'call' if call else 'scenario' if item.get('scene_report') else 'sensor',
                      'phase': 'active', 'phase_at': now, 'started_at': now, 'last_tick': now,
                      'radius_km': .08 if maritime else .18, 'wind_to': ((item.get('weather', {}).get('wind_from_degrees') or 0) + 180) % 360,
                      'wind_changed': False, 'medical': medical, 'maritime': maritime, 'contrast': contrast,
                      'summary_signature': repr(sorted(summary.items())), 'priority': 8.8 if medical else 6.5, 'priority_reason': 'riesgo vital comunicado' if medical else 'señal térmica y entorno por revisar',
                      'exposed_population': 0, 'hospital_threats': [], 'suppression_since': None,
                      'assumption': 'Accesos transitables y viento estable; recursos y capacidad exclusivamente ficticios.'}
            self.data['incidents'][identifier] = record
            if call and contrast['mode'] == 'observed' and contrast.get('distance_km', 11) <= 3:
                sensor = self.data['incidents'].get(contrast.get('incident_id'))
                if sensor and sensor['source'] == 'sensor':
                    sensor['linked_call_id'] = identifier
                    record['sensor_id'] = sensor['id']
                    for assignment in self.director.state['assignments'].values():
                        if assignment.get('incident_id') == sensor['id']:
                            assignment['incident_id'] = identifier
                    self.change('contrasted', 'Llamada y sensor vinculados', 'Detección individual a ≤3 km; se conserva el punto comunicado y no se duplica el dispositivo.', identifier)
            self.change('detected', 'Detectado · ' + ('llamada 112' if call else 'aviso de escenario' if item.get('scene_report') else 'aviso sensor'), item['name'], identifier)
            self.change('contrasted', contrast['label'], 'Se conserva la fecha y distancia de la observación; no se analiza la imagen por IA.' if contrast['mode'] == 'observed' else 'Gesto del escenario separado de los datos reales NASA.', identifier)
            self.change('report', 'Entra al director · ' + item['name'], 'Certeza: aviso de llamada' if call else 'Certeza: anomalía térmica persistente; incendio no confirmado oficialmente', identifier)
        self.data['candidates'] = {k: v for k, v in self.data['candidates'].items() if k in valid or k in self.data['incidents']}

    def invalidate(self, identifier: str | None, cause: str) -> None:
        self.data['plan_revision'] = self.data.get('plan_revision', 0) + 1
        self.change('invalidated', 'Plan anterior invalidado · recalculando', cause, identifier)
        self.director.state['last_fingerprint'] = ''

    def enrich(self, item: dict, environment: dict) -> None:
        record = self.data['incidents'].get(item['id'])
        if not record:
            return
        self.samples[item['id']] = environment.get('potential', {}).get('samples', [])
        self.risk(record)

    def risk(self, record: dict) -> None:
        origin = [record['lon'], record['lat']]
        radius = record['radius_km'] + .8
        def threatened_sample(sample):
            point = [sample['lon'], sample['lat']]
            angle = math.degrees(math.atan2((point[0] - origin[0]) * math.cos(math.radians(origin[1])), point[1] - origin[1])) % 360
            downwind = abs((angle - record['wind_to'] + 180) % 360 - 180) <= 45
            return km(origin, point) <= radius + (record['radius_km'] if downwind else 0)
        population = sum(s.get('evidence', {}).get('population') or 0 for s in self.samples.get(record['id'], []) if threatened_sample(s))
        hospitals = [h['name'] for h in self.data['hospitals'] if km(origin, [h['lon'], h['lat']]) <= radius + .5]
        record.update(exposed_population=round(population), hospital_threats=hospitals)
        threatened = population > 0 or bool(hospitals)
        if record['radius_km'] > .4 and threatened:
            record['medical'] = True
        score = min(10, 6 + (1.8 if record['medical'] else 0) + (1 if threatened else 0) + (.6 if hospitals else 0) + record['radius_km'])
        if record['phase'] != 'active':
            score = {'contained': 4, 'watching': 2, 'releasing': 1, 'closed': 0}[record['phase']]
        record['priority'] = round(score, 1)
        record['priority_reason'] = ' y '.join(filter(None, ['riesgo vital' if record['medical'] else 'señal térmica',
            'hospital próximo' if hospitals else 'población próxima' if population else ''])) if record['phase'] == 'active' else PHASES[record['phase']].lower()

    def evolve(self, now: float | None = None) -> None:
        now = time.time() if now is None else now
        for record in self.data['incidents'].values():
            identifier, phase = record['id'], record['phase']
            if record.get('linked_call_id'):
                linked = self.data['incidents'].get(record['linked_call_id'])
                if linked:
                    record['phase'] = linked['phase']
                    record['priority'] = linked['priority']
                continue
            elapsed = max(0, now - record['last_tick'])
            record['last_tick'] = now
            operations = getattr(self.director, 'operations', None)
            held = bool(operations and operations.held(identifier))
            record['waiting_field_report'] = held
            record['peak_radius_km'] = max(record.get('peak_radius_km', 0), record['radius_km'])
            record['waiting_suppression'] = bool(operations and operations.held(identifier, suppression=True))
            record['peak_exposed_population'] = max(record.get('peak_exposed_population', 0), record.get('exposed_population', 0))
            assignments = [a for a in self.director.state['assignments'].values() if a.get('incident_id') == identifier]
            suppression = sum(1 if a['resource']['kind'] == 'fire_engine' else 2 if a['resource']['kind'] == 'helicopter' else 0
                              for a in assignments if a['status'] == 'onscene')
            if record['waiting_suppression']:
                suppression = 0
            old_band = int(record['radius_km'] * 4)
            if phase == 'active':
                step = min(elapsed, 10)
                floor = .04 if record['maritime'] else CONTAINED_RADIUS_KM
                cap = .15 if record['maritime'] else 1.2
                power = record.get('fire_power', 0)
                growth = (GROWTH_KM_PER_S if power >= 0 else 0) + power / 100 * MANUAL_GROWTH_KM_PER_S
                record['radius_km'] = max(floor, min(cap, record['radius_km'] + step * (growth - suppression * SUPPRESSION_KM_PER_S)))
                record['suppression_power'] = suppression
                if suppression >= 1:
                    record['suppression_since'] = record['suppression_since'] if record['suppression_since'] is not None else now
                else:
                    record['suppression_since'] = None
                if (suppression >= 1 or power < 0) and record['radius_km'] <= floor and not held:
                    record.update(phase='contained', phase_at=now)
                    reason = 'Control manual de potencia: reducción progresiva del fuego simulado.' if power < 0 else f'{suppression} medios trabajando redujeron el frente hasta el mínimo; no es extinción medida.'
                    self.change('contained', 'Fuego contenido · escenario', reason, identifier)
                if not record['wind_changed'] and now - record['started_at'] > 35 and self.data['automatic']:
                    record.update(wind_to=(record['wind_to'] + 70) % 360, wind_changed=True)
                    self.invalidate(identifier, 'El viento del escenario gira 70°; deja de cumplirse el supuesto de dirección estable')
                band = int(record['radius_km'] * 4)
                if band > old_band:
                    self.risk(record)
                    self.change('growth', 'El fuego amplía su entorno de amenaza', f"Prioridad {record['priority']}/10 · {record['priority_reason']}. Población censal próxima: {record['exposed_population']}; no afectados medidos.", identifier)
                elif band < old_band:
                    self.risk(record)
                    message = 'El fuego retrocede · potencia manual' if power < 0 else f'El fuego retrocede · {suppression} medios trabajando'
                    self.change('suppression', message, f"Radio ilustrativo {record['radius_km']:.2f} km; reducción simulada, no extinción medida.", identifier)
            if record['phase'] in {'contained', 'watching'}:
                record.update(phase='releasing', phase_at=now, radius_km=.02)
                self.change('release', 'Fuego apagado · regreso inmediato', 'Sin espera de vigilancia en la demo. Regresan las unidades; los traslados en curso terminan antes de volver a base.', identifier)
            elif phase == 'releasing' and not assignments:
                record.update(phase='closed', phase_at=now, radius_km=.02)
                self.change('closed', 'Cerrado · seguro en el escenario', 'Medios de regreso en base. Relato conservado; datos NASA intactos.', identifier)
            record['peak_radius_km'] = max(record['peak_radius_km'], record['radius_km'])
            record['extinguished_pct'] = (100 if record['phase'] in {'releasing', 'closed'} else
                                         round(100 * max(0, 1 - record['radius_km'] / record['peak_radius_km'])) if record['peak_radius_km'] else 0)
            self.risk(record)

    def overlay(self, payload: dict) -> dict:
        result = dict(payload)
        result['incidents'] = []
        originals = payload.get('incidents', [])
        identifiers = {i['id'] for i in originals}
        for original in [*originals, *(i for i in self.data.get('fixtures', []) if i['id'] not in identifiers)]:
            record = self.data['incidents'].get(original['id'])
            item = dict(original)
            if record:
                item['scenario'] = deepcopy(record)
                item['scenario']['label'] = PHASES[record['phase']]
                item['scenario']['footprint'] = visual_geometry(record)
                if record['source'] == 'sensor':
                    item['source_kind'] = 'sensor'
                    item['sensor_report'] = {'certainty': 'thermal_anomaly', 'severity': record['priority'], 'source': 'NASA FIRMS', 'demo': True}
            result['incidents'].append(item)
        result['scenario_revision'] = self.data['revision']
        result['scenario_plan_revision'] = self.data.get('plan_revision', 0)
        return result

    def command(self, body: dict) -> None:
        action = body.get('action')
        if action in {'closure', 'random_closure', 'congestion'}:
            self.disrupt(action != 'congestion', randomize=action == 'random_closure')
            return
        if action == 'automatic':
            self.data['automatic'] = not self.data['automatic']
            return
        if action == 'exercise':
            from demo import call_incident
            from datetime import timezone
            import uuid
            identifier = str(uuid.uuid4())
            call = {'location': {'lat': 41.425, 'lon': 2.115, 'label': 'Collserola · ejercicio de sala', 'precision': 'area'},
                    'reported_at': datetime.now(timezone.utc).isoformat()}
            item = call_incident(identifier, call, self.director.store.weather)
            item.update(source_kind='scenario', scene_report={'source': 'Ejercicio manual de sala, NO FIRMS ni llamada'})
            fixtures = self.data.setdefault('fixtures', [])
            if len(fixtures) >= 8:
                raise ValueError('Máximo ocho ejercicios por sesión')
            fixtures.append(item)
            return
        identifier = str(body.get('incident_id', ''))
        record = self.data['incidents'].get(identifier)
        if not record or record['phase'] == 'closed':
            raise ValueError('Selecciona un aviso activo')
        if action in {'wind', 'fire_power'}:
            if record['phase'] == 'releasing' or record.get('linked_call_id'):
                raise ValueError('Selecciona un incendio en intervención o vigilancia')
            value = body.get('value', (record['wind_to'] + 70) % 360 if action == 'wind' else None)
            low, high = (0, 359) if action == 'wind' else (-100, 100)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f'Valor de {action} fuera de rango: {low} a {high}')
            if action == 'wind':
                record.update(wind_to=value, wind_changed=True)
                cause = 'Viento ajustado manualmente en el escenario: cambia el sector de población expuesta'
            else:
                record['fire_power'] = value
                record['last_tick'] = time.time()
                if value > 0 and record['phase'] in {'contained', 'watching'}:
                    record.update(phase='active', phase_at=time.time(), suppression_since=None)
                cause = f'Potencia manual del incendio: {value:+g} · evolución ilustrativa, no medición'
            self.risk(record)
            self.invalidate(identifier, cause)
        elif action == 'field':
            role, report = body.get('role'), body.get('report')
            if role not in {'bomberos', 'sanitarios', 'policía'} or report not in {'empeora', 'heridos', 'contenido', 'reactivación'}:
                raise ValueError('Parte de ejercicio no válido')
            if report in {'empeora', 'heridos', 'reactivación'}:
                record.update(phase='active', phase_at=time.time(), medical=True, suppression_since=None)
                if report == 'reactivación':
                    record['radius_km'] = max(.25, record['radius_km'])
            else:
                record.update(phase='contained', phase_at=time.time())
            self.risk(record)
            self.change('field_report', f'Parte de {role} · {report}', 'Parte manual del escenario; no acredita personal real. Corrige el supuesto del plan.', identifier)
            self.invalidate(identifier, f'{role.capitalize()} informa: {report}')
        else:
            raise ValueError('Acción del escenario no disponible')

    def route(self, start: list, end: list, relaxed: bool = False) -> dict:
        return self.director.router.route(start, end, scenario=True, blocked=set(self.data['closures']), congestion=self.data['congestion'], relaxed=relaxed)

    def disrupt(self, closure: bool = True, randomize: bool = False) -> None:
        from director import route_position
        assignments = [a for a in self.director.state['assignments'].values()
                       if a['status'] in {'enroute', 'returning', 'transporting'} and a['route'].get('edge_ids')
                       and not a['route'].get('approximate') and a['resource']['kind'] != 'helicopter']
        if randomize:
            random.shuffle(assignments)
        for assignment in assignments:
            route = assignment['route']
            progress = max(0, (time.time() - assignment['started_at']) / assignment['travel_seconds'])
            if progress > .75:
                continue
            edges = route['edge_ids']
            candidates = [n for n, d in enumerate(route['cumulative_km'][:-1])
                          if d >= route['distance_km'] * max(.4, progress + .15)
                          and route['cumulative_km'][n + 1] - d >= .04 and edges[n] not in self.data['closures']]
            if not candidates:
                continue
            index = random.choice(candidates) if randomize else candidates[0]
            edge = edges[index]
            coordinates = route['coordinates'][index:index + 2]
            if closure:
                self.data['closures'][edge] = {'id': edge, 'coordinates': coordinates, 'label': 'Corte de vía · escenario', 'at': time.time()}
            else:
                self.data['congestion'][edge] = 6
            self.invalidate(assignment['incident_id'], 'Vía cortada en el escenario' if closure else 'Congestión dibujada: el tiempo de acceso ya no es válido')
            for active in self.director.state['assignments'].values():
                if active['status'] not in {'enroute', 'returning', 'transporting', 'blocked'} or edge not in active['route'].get('edge_ids', []):
                    continue
                origin = active.get('held_position') or route_position(active['route'], (time.time() - active['started_at']) / active['travel_seconds'])
                active['previous_route'] = active['route']
                try:
                    new = self.route(origin, active['target'])
                except (ValueError, RuntimeError):
                    active.setdefault('resume_status', active['status'])
                    active.update(status='blocked', held_position=origin)
                    self.change('blocked', 'Unidad detenida antes del corte', 'No hay desvío utilizable; nunca se atraviesa una vía cerrada. Pendiente de nueva decisión.', active['incident_id'])
                    continue
                active.update(route=new, started_at=time.time(), travel_seconds=max(30, min(150, new['duration_seconds'] / 20)), route_revision=self.data['revision'], status=active.pop('resume_status', active['status']))
                active.pop('held_position', None)
                self.change('reroute', 'Ruta recalculada · desvío visible', f"{new['distance_km']:.1f} km · {new['duration_seconds'] / 60:.1f} min estimados de escenario. Trazo gris: plan anterior; color: nuevo.", active['incident_id'])
            return
        raise ValueError('Hace falta una unidad de carretera en ruta, con recorrido por delante')

    def maintenance(self) -> None:
        from director import route_position
        now = time.time()
        for rid, assignment in list(self.director.state['assignments'].items()):
            record = self.data['incidents'].get(assignment.get('incident_id'))
            if not record:
                continue
            if record['phase'] not in {'releasing', 'closed'} and assignment['status'] == 'onscene' and assignment['resource']['kind'] == 'ambulance' and record['medical'] and not assignment.get('patient_delivered') and now - assignment.get('arrived_at', now) >= 15:
                ordered, avoided, margin = hospital_options(self.data['hospitals'], record)
                origin = [record['lon'], record['lat']]
                for hospital in ordered:
                    try:
                        target = [hospital['lon'], hospital['lat']]
                        route = self.route(assignment['route']['coordinates'][-1], target)
                    except (ValueError, RuntimeError):
                        continue
                    hospital['occupied'] += 1
                    distance = km(origin, target)
                    skipped = [h for h in avoided if h['id'] != hospital['id']] if distance >= margin else []
                    assignment.update(route=route, target=target, status='transporting', hospital_id=hospital['id'],
                                      avoided_hospital_ids=[h['id'] for h in skipped], started_at=now,
                                      travel_seconds=max(30, min(120, route['duration_seconds'] / 20)), route_revision=self.data['revision'] + 1)
                    if skipped:
                        self.change('transport', f'Ambulancia hacia {hospital["name"]} · hospital cambiado por seguridad',
                                    f'{skipped[0]["name"]} queda a {km(origin, [skipped[0]["lon"], skipped[0]["lat"]]):.1f} km del fuego, dentro del entorno de amenaza del escenario '
                                    f'({margin:.1f} km). Se traslada a {hospital["name"]}, a {distance:.1f} km. Criterio del simulador y plaza ficticia: '
                                    'no es protocolo sanitario, disponibilidad hospitalaria real ni alta médica.', record['id'])
                    elif distance < margin:
                        self.change('transport', 'Ambulancia hacia ' + hospital['name'],
                                    f'No hay hospital con ruta utilizable fuera del entorno de amenaza ({margin:.1f} km); el destino queda a {distance:.1f} km del fuego. '
                                    'Traslado ficticio: se reserva una plaza de demo. No es disponibilidad hospitalaria real ni alta médica.', record['id'])
                    else:
                        self.change('transport', 'Ambulancia hacia ' + hospital['name'], 'Traslado ficticio: se reserva una plaza de demo. No es disponibilidad hospitalaria real ni alta médica.', record['id'])
                    break
            if record['phase'] == 'releasing' and assignment['status'] not in {'returning', 'transporting'} and now >= assignment.get('return_retry_at', 0):
                resource = assignment['resource']
                origin = assignment.get('held_position') or route_position(assignment['route'], (now - assignment['started_at']) / assignment['travel_seconds'])
                target = [resource['lon'], resource['lat']]
                at_base = km(origin, target) < .03
                if not at_base and resource['kind'] != 'helicopter' and km(origin, target) < .75 and in_demo(origin) and in_demo(target):
                    graph = self.director.router.demo_graph()
                    at_base = graph.nearest(origin) == graph.nearest(target)
                if at_base:
                    del self.director.state['assignments'][rid]
                    self.change('available', 'Unidad ya en su sede · disponible', 'Finaliza la reserva tras la vigilancia; no implica alta del paciente ficticio.', record['id'])
                    continue
                try:
                    from director import air_route
                    route = air_route(origin, target) if resource['kind'] == 'helicopter' else self.route(origin, target)
                except (ValueError, RuntimeError):
                    assignment['return_retry_at'] = now + 30
                    self.change('blocked', 'Regreso pendiente de acceso', 'Se conserva la unidad ocupada; reintento en 30 s. No se inventa un trayecto a base.', record['id'])
                    continue
                assignment.pop('held_position', None)
                assignment.update(route=route, target=target, status='returning', started_at=now, travel_seconds=max(5, min(15, route['duration_seconds'] / 60)), route_revision=self.data['revision'] + 1)
                self.change('return', 'Regresa · ' + resource['name'], 'Fin de la intervención; regreso acelerado de demo. La unidad sigue ocupada hasta llegar a sede.', record['id'])
        if self.data['automatic'] and not self.data.get('auto_cut'):
            traveling = [a for a in self.director.state['assignments'].values() if a['status'] == 'enroute' and a['route'].get('edge_ids') and now - a['started_at'] > 12]
            if traveling:
                try:
                    self.disrupt()
                    self.data['auto_cut'] = True
                except ValueError:
                    pass
