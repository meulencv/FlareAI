from __future__ import annotations

import hashlib
import random
import time
from copy import deepcopy

from local_routes import km


COHERENT = (
    'Veo humo en {place}; estoy mirando desde una calle cercana.',
    'También estoy en {place}. Se ve una columna de humo, no sé cuántas personas hay.',
    'Aviso desde las inmediaciones de {place}. Parece el mismo incendio del que están avisando otros vecinos.',
    'Hay gente alejándose de {place}. No puedo confirmar heridos.',
    'Desde mi ventana veo humo hacia {place}; no tengo visión completa del foco.',
    'Llamo por el aviso de fuego en {place}. No estoy dentro y no conozco su extensión.',
)
DOUBTFUL = (
    'Me lo han contado: hay cientos de heridos en {place}, pero yo no estoy allí.',
    'No estoy seguro de la calle; quizá el humo de {place} esté dos barrios más lejos.',
    'Dicen en un grupo que ha explotado todo {place}; no tengo ninguna imagen ni lo he visto.',
    'Creo que lo de {place} ya está apagado porque ahora no veo humo desde donde estoy.',
)
JOKES = (
    'En {place} hay un dragón echando fuego. Era una broma, quería probar el teléfono.',
    'Mandad todos los helicópteros a {place} para grabar mi vídeo. No he visto ningún incendio.',
)


# Cinco testigos por aviso (petición expresa 19/09/2026): tres coherentes, uno dudoso y una broma,
# mezclados en orden aleatorio estable por incidente. Antes eran 24 y saturaban el mapa.
WAVE_SIZE = 5


def build_wave(incident: dict, started_at: float) -> list[dict]:
    randomizer = random.Random(incident['id'])
    place = str(incident.get('demo_report', {}).get('location', {}).get('label') or incident['name'])[:160]
    texts = [t.format(place=place) for t in randomizer.sample(COHERENT, 3)]
    texts += [randomizer.choice(DOUBTFUL).format(place=place), randomizer.choice(JOKES).format(place=place)]
    randomizer.shuffle(texts)
    clock, rows = started_at, []
    for index, text in enumerate(texts):
        clock += randomizer.randint(500, 2000) / 1000
        identifier = hashlib.sha256(f'{incident["id"]}:{index}'.encode()).hexdigest()[:20]
        rows.append({'id': identifier, 'at': round(clock, 3), 'speaker': f'Testigo {index + 1:02}',
                     'text': text, 'source': 'synthetic_demo', 'incident_id': incident['id']})
    return rows


FIRST_PLAN_DELAY = 3.0
# La contención del escenario espera al parte telefónico y a los refuerzos pedidos, pero no indefinidamente:
# pasado este plazo desde el aviso, el fuego se extingue en la simulación aunque el teléfono no se haya atendido.
HOLD_LIMIT = 300.0


def visible_testimonies(wave: list[dict], now: float) -> list[dict]:
    return [item for item in wave if item['at'] <= now]


def alert_allowed(fields: dict) -> bool:
    return fields.get('incendio') not in {'descartado', 'extinguido'} and fields.get('es_alert') != 'no_solicitado' and (
        fields.get('es_alert') == 'solicitado' or fields.get('evolucion') == 'critico')


def requested_resources(fields: dict, versions: dict | None = None) -> dict[str, int]:
    if fields.get('incendio') in {'descartado', 'extinguido'}:
        return {}
    result = {}
    for field, kind, flag, default in [('ambulancias', 'ambulance', 'ambulancia', 1),
                                     ('bomberos', 'fire_engine', 'refuerzos', 2),
                                     ('helicopteros', 'helicopter', 'helicoptero', 1),
                                     ('policias', 'police', 'policia', 1)]:
        value = str(fields.get(field, ''))
        count = min(100, int(value)) if value.isascii() and value.isdigit() else default if fields.get(flag) == 'solicitado' else 0
        if fields.get(flag) == 'no_solicitado' and (versions or {}).get(flag, 0) >= (versions or {}).get(field, 0):
            count = 0
        if count:
            result[kind] = count
    return result


class Operations:
    def __init__(self, director) -> None:
        from outbound import OutboundCalls
        self.director, self.db = director, director.db
        self.waves: dict[str, list[dict]] = {}
        self.outbound = OutboundCalls(director)
        self.last_heartbeat = 0.0
        director.state['operations'] = {}
        if director.scene:
            director.scene.data['automatic'] = False

    @property
    def records(self) -> dict:
        return self.director.state['operations']

    def tick(self, payload: dict) -> None:
        now = time.time()
        if now - self.last_heartbeat >= 10:
            self.db.heartbeat(self.director.session_id)
            self.last_heartbeat = now
        for incident in payload.get('incidents', []):
            if not incident.get('demo_report') or incident['id'] in self.records:
                continue
            wave = build_wave(incident, now)
            identifier = incident['id']
            self.db.document('testimonies:' + identifier, 'testimonies', {'items': wave}, self.director.session_id)
            self.waves[identifier] = wave
            self.records[identifier] = {'id': identifier, 'name': incident['name'], 'started_at': now,
                'ready_at': wave[-1]['at'], 'assessment': None, 'requests': {}, 'reported': False,
                'source_call': incident['demo_report']['run_id'],
                'citizen': {'id': 'citizen:' + incident['demo_report']['run_id'], 'speaker': 'Llamada 112', 'at': now,
                    'source': 'webcall', 'text': ' · '.join(str(v) for v in incident['demo_report'].get('summary', {}).values())}}
            self.director.event('testimonies', 'Entran avisos relacionados con el 112', f'{WAVE_SIZE} testimonios sintéticos de demo, algunos falsos; se contrastan sin confundir repetición con credibilidad.', incident_id=identifier)
        self.outbound.tick(payload)
        self.reinforce(payload)
        for identifier, record in self.records.items():
            scene = (self.director.scene.data['incidents'].get(identifier) if self.director.scene else None) or {}
            if scene.get('phase') == 'closed' and not record['reported']:
                from reports import finish_operation
                finish_operation(self.director, record)
                record['reported'] = True
                self.director.event('report_ready', 'Informe y memoria disponibles', 'PDF, estimaciones del escenario y aprendizajes verificables; sin créditos de carbono emitidos.', incident_id=identifier)
                self.director.save()

    def ready(self) -> bool:
        return all(time.time() >= record['started_at'] + FIRST_PLAN_DELAY for record in self.records.values())

    def wave(self, identifier: str) -> list[dict]:
        if identifier not in self.waves:
            stored = self.db.document('testimonies:' + identifier) or {}
            self.waves[identifier] = stored.get('items', []) if isinstance(stored, dict) else []
        return self.waves[identifier]

    def context(self, identifier: str) -> dict:
        record = self.records.get(identifier)
        if not record:
            return {}
        return {'testimonies': deepcopy(self.wave(identifier)),
                'assessment': record['assessment'], 'mandatory_requests': deepcopy(record['requests'])}

    def public_state(self) -> dict:
        now = time.time()
        return {'incidents': [deepcopy(record) | {'testimonies': visible_testimonies(self.wave(identifier), now),
                    'outbound': self.outbound.public_state(identifier)} for identifier, record in self.records.items()],
                'outbound_enabled': self.outbound.enabled}

    def accept_assessments(self, plan: dict) -> None:
        for assessment in plan.get('assessments', []):
            if not isinstance(assessment, dict) or assessment.get('incident_id') not in self.records:
                continue
            identifier = assessment['incident_id']
            known = {item['id'] for item in self.waves.get(identifier, [])}
            items = []
            for item in assessment.get('testimonies', [])[:WAVE_SIZE]:
                if isinstance(item, dict) and item.get('id') in known and item.get('status') in {'supported', 'uncertain', 'unlikely', 'prank'}:
                    items.append({'id': item['id'], 'status': item['status'], 'reason': str(item.get('reason', ''))[:240]})
            accepted = {'summary': str(assessment.get('summary', ''))[:1200], 'testimonies': items, 'at': time.time()}
            self.records[identifier]['assessment'] = accepted
            self.director.event('assessment', 'Conclusión de los testimonios', accepted['summary'], incident_id=identifier)

    def held(self, identifier: str) -> bool:
        record = self.records.get(identifier)
        if not record:
            return False
        if time.time() - record['started_at'] >= HOLD_LIMIT:
            return False
        call = self.outbound.jobs.get(identifier, {})
        requests = [r for r in record['requests'].values() if r.get('status') != 'cancelled']
        traveling = any(self.director.state['assignments'].get(rid, {}).get('status') in {'enroute', 'blocked'}
                        for r in requests for rid in r['resource_ids'])
        # Telefonía desactivada, contacto inalcanzable o conversación sin parte no retienen la extinción simulada.
        waiting_call = call.get('status') not in {'completed', 'needs_report', 'disabled', 'unreachable'}
        return waiting_call or traveling or any(r['fulfilled'] < r['quantity'] for r in requests)

    def reinforce(self, payload: dict) -> None:
        for identifier, report in payload.get('demo', {}).get('field_reports', {}).items():
            record = self.records.get(identifier)
            if not record:
                continue
            fields = report['fields']
            if fields.get('incendio') in {'descartado', 'extinguido'}:
                for request in record['requests'].values():
                    if request['fulfilled'] < request['quantity']:
                        request['status'] = 'cancelled'
                continue
            mapping = {'ambulance': ('ambulancias', 'ambulancia'), 'fire_engine': ('bomberos', 'refuerzos'),
                       'helicopter': ('helicopteros', 'helicoptero'), 'police': ('policias', 'policia')}
            versions = report.get('field_versions', {})
            for kind, (quantity_field, flag) in mapping.items():
                cancelled = (fields.get(flag) == 'no_solicitado' and versions.get(flag, 0) >= versions.get(quantity_field, 0)
                             or fields.get(quantity_field) == '0' and versions.get(quantity_field, 0) >= versions.get(flag, 0))
                if cancelled:
                    for request in record['requests'].values():
                        if request['kind'] == kind and request['fulfilled'] < request['quantity']:
                            request['status'] = 'cancelled'
            for kind, count in requested_resources(fields, versions).items():
                field = max(mapping[kind], key=lambda k: report.get('field_versions', {}).get(k, 0))
                revision = report.get('field_versions', {}).get(field, 0)
                source = report.get('field_sources', {}).get(field, {}).get('run_id', report.get('run_id', 'field'))
                key = f'{kind}:{source}'
                request = record['requests'].setdefault(key, {'kind': kind, 'quantity': count, 'fulfilled': 0, 'resource_ids': [], 'status': 'pending', 'retry_at': 0, 'revision': -1})
                if revision > request['revision']:
                    request.update(quantity=count, revision=revision, retry_at=0)
                    request['status'] = 'fulfilled' if request['fulfilled'] >= count else 'pending'
            for key, request in record['requests'].items():
                if request['fulfilled'] >= request['quantity'] or request.get('status') == 'cancelled' or request['retry_at'] > time.time():
                    continue
                context = self.director.context(payload)
                incident = next((i for i in context['incidents'] if i['id'] == identifier), None)
                if not incident:
                    continue
                remaining = request['quantity'] - request['fulfilled']
                available = sorted((r for r in context['resources'] if r['kind'] == request['kind'] and not r.get('assignment')),
                                   key=lambda r: km([r['lon'], r['lat']], [incident['lon'], incident['lat']]))
                actions = [{'type': 'dispatch', 'incident_id': identifier, 'resource_id': r['id'],
                            'reason': 'Solicitud explícita de bomberos; ejecución obligatoria en el simulador.'} for r in available[:min(remaining, 8)]]
                previous = deepcopy(self.director.state)
                try:
                    if actions:
                        plan = {'revision': context['revision'], 'summary': 'Ejecutando la solicitud de bomberos', 'actions': actions}
                        prepared = self.director.prepare(plan, {**context, 'presentation': False})
                        fresh = self.director.store.payload()
                        current = next((i for i in fresh.get('incidents', []) if i['id'] == identifier), None)
                        latest = fresh.get('demo', {}).get('field_reports', {}).get(identifier, {})
                        if not current or (current['lat'], current['lon']) != (incident['lat'], incident['lon']) or latest.get('revision') != report.get('revision'):
                            request['retry_at'] = time.time() + 2
                            self.director.save()
                            continue
                        executed = [a for a in prepared if not a.get('route_error')]
                        if executed:
                            self.director.apply(plan, prepared, f'field:{identifier}:{key}:{request["fulfilled"]}')
                            request['resource_ids'].extend(a['resource_id'] for a in executed)
                            request['fulfilled'] += len(executed)
                    request['status'] = 'fulfilled' if request['fulfilled'] >= request['quantity'] else 'blocked'
                    request['retry_at'] = time.time() + 15
                    if request['status'] == 'blocked':
                        self.director.event('request_blocked', 'Refuerzo pendiente; no se descarta la petición', 'Se buscarán unidades libres con acceso utilizable.', incident_id=identifier)
                    self.director.save()
                except Exception:
                    self.director.state = previous
                    raise
