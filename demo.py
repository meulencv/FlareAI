from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import secrets
import threading
import time
import unicodedata
import uuid
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from shapely.affinity import scale, translate
from shapely.geometry import Point, mapping, shape

from gfs import Snapshot, point

ROOT = Path(__file__).resolve().parent
PHONE_ROOT = ROOT / 'happyrobot-112/static'
GEOCODER = 'https://www.cartociudad.es/geocoder/api/geocoder/'
MAX_ACTIVE_CALLS = 16
MAX_SESSION_CALLS = 256
REPORT_FIELDS = ('ubicacion', 'emergencia', 'personas', 'riesgos')
PART_CHOICES = {
    'llegada': ('confirmada', 'en_camino'), 'incendio': ('confirmado', 'descartado', 'extinguido'),
    'es_alert': ('solicitado', 'no_solicitado'), 'refuerzos': ('solicitado', 'no_solicitado'),
    'helicoptero': ('solicitado', 'no_solicitado'), 'evolucion': ('estable', 'empeora', 'critico'),
    'zona_urbana': ('si', 'no'), 'ambulancia': ('solicitado', 'no_solicitado'), 'policia': ('solicitado', 'no_solicitado'),
}
PART_FIELDS = (*PART_CHOICES, 'detalle', 'ubicacion', 'ambulancias', 'bomberos', 'helicopteros', 'policias', 'personas_asistidas')


def normalized(text: str) -> str:
    return ' '.join(re.sub(r'[^a-z0-9-]+', ' ', ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))).split())


def extract_report(messages: list[dict], tool: str = 'actualizar_ficha', fields: tuple = REPORT_FIELDS) -> dict:
    result: dict[str, str] = {}

    def visit(value: Any) -> None:
        if isinstance(value, str):
            try:
                visit(json.loads(value))
            except ValueError:
                pass
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            if value.get('name') == tool:
                args = value.get('arguments', value.get('args', value.get('parameters', {})))
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except ValueError:
                        return
                if isinstance(args, dict):
                    for key in fields:
                        if key in args and isinstance(args[key], str):
                            result[key] = ' '.join(args[key].split())[:240]
            for key in ('function', 'tool_call'):
                if key in value:
                    visit(value[key])

    for message in messages:
        if message.get('role') == 'assistant':
            visit(message.get('tool_calls'))
    return result


def extract_part(messages: list[dict]) -> dict:
    values = extract_report(messages, 'actualizar_parte', PART_FIELDS)
    counts = {'ambulancias', 'bomberos', 'helicopteros', 'policias', 'personas_asistidas'}
    return {key: value for key, value in values.items() if (key not in PART_CHOICES or value in PART_CHOICES[key])
            and (key not in counts or value.isascii() and value.isdigit() and 0 <= int(value) <= 100)}


def canonical_address(text: str) -> str:
    text = normalized(text)
    aliases = {'carrer': 'calle', 'c': 'calle', 'rua': 'calle', 'kalea': 'calle', 'av': 'avenida',
               'avda': 'avenida', 'avinguda': 'avenida', 'placa': 'plaza', 'passeig': 'paseo', 'basilica': 'iglesia', 'templo': 'iglesia'}
    return ' '.join(aliases.get(t, t) for t in text.split() if t not in {'de', 'del', 'la', 'el', 'las', 'los', 'les', 'l', 'd'})


def select_location_candidate(query: str, candidates: list[dict]) -> dict | None:
    target = canonical_address(query)
    tokens = set(target.split())
    ranked = []
    for candidate in candidates:
        address = canonical_address(candidate.get('address', ''))
        if not address:
            continue
        kind = candidate.get('type', '').lower()
        municipality = canonical_address(candidate.get('muni', ''))
        if kind in {'municipio', 'poblacion'} and target not in {address, municipality, canonical_address(candidate.get('muni', '') + ' ' + candidate.get('province', ''))}:
            continue
        variants = [address, canonical_address((candidate.get('tip_via') or '') + ' ' + candidate.get('address', ''))]
        score = max(1.0 if target == value else len(tokens) / len(set(value.split())) if tokens and tokens <= set(value.split()) else 0 for value in variants)
        if score >= .72 and (score == 1 or municipality and set(municipality.split()) <= tokens):
            ranked.append((score, candidate))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    if not ranked or len(ranked) > 1 and ranked[0][0] - ranked[1][0] < .15:
        return None
    return ranked[0][1]


def maritime_location(summary: dict) -> dict | None:
    text = normalized(' '.join(str(v) for v in summary.values()))
    if 'barcelona' not in text or not re.search(r'\b(barco|embarcacion|buque|velero|yate)\b', text) or not is_fire(summary):
        return None
    if re.search(r'\b(no es un barco|no hay barco|barco en tierra|dique seco)\b', text):
        return None
    return {'lat': 41.37, 'lon': 2.235, 'label': 'Mar de Barcelona · posición ilustrativa del barco comunicado',
            'precision': 'area', 'approximate': True, 'maritime': True, 'source': 'Llamada 112 · escenario marítimo',
            'reason': 'Aviso de barco comunicado; punto ilustrativo en el mar, no posición verificada del buque.'}


def is_fire(summary: dict) -> bool:
    text = normalized(summary.get('emergencia', ''))
    denied = re.search(r'\b(?:no (?:hay|es|existe|veo|vemos)(?: (?:un|ningun))? (?:incendio|fuego)|sin (?:incendio|fuego)|falsa alarma|(?:incendio|fuego) (?:ya )?(?:descartado|extinguido|apagado))\b', text)
    return bool(re.search(r'\b(incendio|fuego|arde|ardiendo)\b', text) and not denied)


def coordinates(lat: Any, lon: Any) -> bool:
    return isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and math.isfinite(lat + lon) and 27 <= lat <= 44.5 and -19 <= lon <= 5


def resolve_local(query: str, places: list[dict]) -> dict | None:
    pair = re.fullmatch(r'\s*(?:latitud\s*)?(-?\d{1,2}\.\d{3,})\s*[,; ]\s*(?:longitud\s*)?(-?\d{1,2}\.\d{3,})\s*', query, re.I)
    if pair:
        lat, lon = map(float, pair.groups())
        return {'lat': lat, 'lon': lon, 'label': query, 'precision': 'coordinates', 'source': 'caller'} if coordinates(lat, lon) else None
    text = normalized(query)
    if re.search(r'\b(calle|avenida|plaza|carretera|camino|paseo|km|kilometro|portal|poligono)\b|\d', text):
        return None
    matches = [place for place in places if text == normalized(place['name'])]
    if len(matches) == 1:
        return {**matches[0], 'label': matches[0]['name'], 'precision': 'locality', 'source': 'local_places'}
    return None


def clean_location(query: str) -> str:
    query = re.sub(r'^(?:(?:estoy|estamos|es|está|el incendio está|hay fuego|hay un incendio)\s+)?en\s+', '', query.strip(), flags=re.I)
    return re.sub(r'[,;]?\s+(?:\d+[ºª]?|primera|segunda|tercera|cuarta|quinta)\s+(?:planta|piso)\b.*$', '', query, flags=re.I).strip()


def select_osm_location(query: str, candidates: list[dict]) -> dict | None:
    tokens = set(canonical_address(query).split())
    ranked: list[tuple[int, dict]] = []
    for candidate in candidates:
        address = candidate.get('address', {})
        try:
            lat, lon = float(candidate['lat']), float(candidate['lon'])
        except (KeyError, ValueError, TypeError):
            continue
        if address.get('country_code') != 'es' or not coordinates(lat, lon):
            continue
        name = candidate.get('name', '')
        city = next((address[k] for k in ('city', 'town', 'village', 'municipality') if address.get(k)), '')
        road, number = address.get('road', ''), address.get('house_number', '')
        kind = candidate.get('addresstype', candidate.get('type', ''))
        locality = kind in {'city', 'town', 'village', 'municipality', 'hamlet'}
        label = ', '.join(filter(None, [road + (' ' + number if number else '') if road and not name else name, city]))
        available = set(canonical_address(candidate.get('display_name', '') + ' ' + name).split())
        if not tokens or not tokens <= available:
            continue
        if locality and tokens - set(canonical_address(name + ' ' + city).split()):
            continue
        numbers = set(re.findall(r'\b\d+\b', query))
        if numbers and not numbers <= set(re.findall(r'\b\d+\b', number + ' ' + address.get('postcode', ''))):
            continue
        precision = 'locality' if locality else 'address' if number and numbers else 'street' if candidate.get('category') == 'highway' else 'area' if kind in {'suburb', 'quarter', 'neighbourhood', 'state', 'county', 'province'} else 'poi'
        score = 2 if numbers and number and candidate.get('type') == 'house' else 1
        ranked.append((score, {'lat': lat, 'lon': lon, 'label': label or candidate.get('display_name', ''), 'precision': precision,
                              'source': 'OpenStreetMap / Nominatim', 'candidate_id': f'{candidate.get("osm_type", "")}/{candidate.get("osm_id", "")}',
                              'attribution': '© OpenStreetMap contributors · ODbL', 'query': query}))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    if not ranked:
        return None
    best = ranked[0][1]
    for score, other in ranked[1:]:
        distance = math.hypot((best['lat'] - other['lat']) * 111.32, (best['lon'] - other['lon']) * 111.32 * math.cos(math.radians(best['lat'])))
        if score == ranked[0][0] and distance > .2:
            return None
    return best


class LocationResolver:
    osm_lock = threading.Lock()
    osm_next_request = 0.0

    def __init__(self, database) -> None:
        self.db = database
        self.places = database.get_asset('map:places.json')['data']['places']
        self.country = shape(database.get_asset('map:spain.geojson')['data']['geometry']).buffer(.02)
        self.cache: dict[str, dict | None] = {}
        self.cache_lock = threading.Lock()
        self.osm_url = os.environ.get('FLAREAI_NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search')

    def __call__(self, query: str) -> dict | None:
        original, query = query, clean_location(query)
        key = normalized(query)
        with self.cache_lock:
            if key in self.cache:
                return deepcopy(self.cache[key])
        result = resolve_local(query, self.places)
        if not result and len(key) >= 4 and key not in {'pendiente', 'desconocido', 'no se donde estoy'}:
            result = self.osm(query) or self.remote(query)
            if not result:
                street = re.sub(r'\b\d+[a-zA-Z]?\b', '', query).strip(' ,')
                if street != query and re.search(r'\b(calle|avenida|plaza|paseo)\b', canonical_address(query)):
                    result = self.osm(street) or self.remote(street)
                    if result and result['precision'] == 'street':
                        result = {**result, 'reason': 'No se encontró el portal; punto representativo de la vía.'}
                    else:
                        result = None
            if not result:
                result = self.locality_fallback(query)
        if result and not self.country.covers(Point(result['lon'], result['lat'])):
            result = None
        if result:
            result = {**result, 'query': original, 'approximate': result['precision'] in {'locality', 'street', 'area'}}
            if result['approximate']:
                result.setdefault('reason', 'Punto representativo de la zona indicada, no ubicación exacta del incendio.')
        with self.cache_lock:
            if len(self.cache) >= 512:
                self.cache.pop(next(iter(self.cache)))
            self.cache[key] = result
        return deepcopy(result)

    def locality_fallback(self, query: str) -> dict | None:
        text = normalized(query)
        if re.search(r'\b(?:o|entre|no)\b', text):
            return None
        matches = [p for p in self.places if re.search(r'\b' + re.escape(normalized(p['name'])) + r'\b', text)]
        matches = [p for p in matches if not any(p != other and normalized(p['name']) in normalized(other['name']) for other in matches)]
        if len(matches) == 1 and not re.fullmatch(r'(?:calle|avenida|plaza|paseo) ' + re.escape(canonical_address(matches[0]['name'])) + r'(?: \d+)?', canonical_address(query)):
            return {**matches[0], 'label': matches[0]['name'], 'precision': 'locality', 'source': 'local_places',
                    'reason': 'Dirección no resuelta; se usa el municipio comunicado como aproximación de demo.'}
        parts = [p.strip() for p in query.split(',') if p.strip()]
        if len(parts) > 1 and not re.search(r'\d', parts[-1]):
            city = parts[-1]
            result = self.osm(city) or self.remote(city)
            if result and result['precision'] in {'locality', 'area'}:
                return {**result, 'reason': 'Dirección no resuelta; se usa la zona comunicada como aproximación de demo.'}
        return None

    def osm(self, query: str) -> dict | None:
        return select_osm_location(query, self.osm_fetch(query))

    def osm_fetch(self, query: str) -> list[dict]:
        if not self.osm_url:
            return []
        identifier = 'geocode:osm:' + hashlib.sha256((self.osm_url + normalized(query)).encode()).hexdigest()
        with self.osm_lock:
            cached = self.db.get_asset(identifier)
            if cached and time.time() - cached['data'].get('at', 0) < 86400:
                return cached['data']['results']
            time.sleep(max(0, LocationResolver.osm_next_request - time.monotonic()))
            LocationResolver.osm_next_request = time.monotonic() + 1.05
            try:
                args = {'q': query, 'format': 'jsonv2', 'addressdetails': 1, 'countrycodes': 'es', 'limit': 5}
                request = Request(self.osm_url + '?' + urlencode(args), headers={'User-Agent': 'FlareAI-Demo/1.0 (local fire-observatory demo)', 'Accept-Language': 'es'})
                with urlopen(request, timeout=5) as response:
                    body = response.read(1_000_001)
                results = json.loads(body) if len(body) <= 1_000_000 else []
                if not isinstance(results, list):
                    results = []
            except (OSError, ValueError):
                results = []
            self.db.asset(identifier, 'geocoding', {'at': time.time(), 'results': results})
            return results

    def remote(self, query: str) -> dict | None:
        def fetch(path: str, args: dict) -> Any:
            request = Request(GEOCODER + path + '?' + urlencode(args), headers={'User-Agent': 'FlareAI-Demo/1.0'})
            with urlopen(request, timeout=8) as response:
                body = response.read(1_000_001)
                if len(body) > 1_000_000:
                    raise ValueError('Geocodificación demasiado grande')
                return json.loads(body)

        try:
            query = re.sub(r'[,;]?\s+(?:\d+[ºª]?|primera|segunda|tercera|cuarta|quinta)\s+(?:planta|piso)\b.*$', '', query, flags=re.I)
            candidates = fetch('candidates', {'q': query, 'limit': 10})
            candidate = select_location_candidate(query, candidates)
            if candidate is None:
                shorter = re.sub(r'^(?:bas[ií]lica|iglesia|templo)\s+(?:de\s+)?(?:la\s+)?', '', query, flags=re.I)
                if shorter != query:
                    candidate = select_location_candidate(query, fetch('candidates', {'q': shorter, 'limit': 10}))
            if candidate is None:
                return None
            if not coordinates(candidate.get('lat'), candidate.get('lng')):
                candidate = fetch('find', {'q': candidate['address'], 'id': candidate['id'], 'type': candidate['type']})
            if not coordinates(candidate.get('lat'), candidate.get('lng')):
                return None
            return {'lat': candidate['lat'], 'lon': candidate['lng'], 'label': candidate['address'],
                    'precision': 'locality' if candidate['type'].lower() in {'municipio', 'poblacion'} else 'poi' if candidate['type'].lower() == 'toponimo' else 'street' if candidate['type'].lower() in {'callejero', 'via', 'vial'} else 'address',
                    'source': 'CartoCiudad / IGN', 'candidate_id': candidate.get('id'), 'query': query}
        except (OSError, ValueError, KeyError, TypeError):
            return None


def match_incident(location: dict, incidents: list[dict], radius_km: float = 3) -> str | None:
    xscale = 111.32 * math.cos(math.radians(location['lat']))
    ranked = []
    for incident in incidents:
        footprint = scale(translate(shape(incident['footprint']), -location['lon'], -location['lat']),
                          xfact=xscale, yfact=111.32, origin=(0, 0))
        ranked.append((footprint.distance(Point(0, 0)), incident['id']))
    nearest = min(ranked, default=(math.inf, None))
    return nearest[1] if nearest[0] <= radius_km else None


def call_incident(run_id: str, call: dict, weather: dict) -> dict:
    location = call['location']
    lat, lon = location['lat'], location['lon']
    support = translate(scale(Point(0, 0).buffer(.08, quad_segs=12), xfact=1 / (111.32 * math.cos(math.radians(lat))), yfact=1 / 111.32, origin=(0, 0)), lon, lat)
    return {'id': 'demo:' + run_id, 'source_kind': 'call', 'name': 'Aviso · ' + location['label'],
            'province': 'Demo · ubicación ' + ('aproximada' if location.get('approximate') or location['precision'] == 'locality' else 'comunicada'),
            'lat': lat, 'lon': lon, 'first_seen': call['reported_at'], 'last_seen': call['reported_at'],
            'observations': 0, 'passes': 0, 'satellites': [], 'frp_peak_mw': None,
            'brightness_i4_k': None, 'brightness_i4_c': None, 'brightness_at_utc': None,
            'low_confidence': 0, 'documented': False, 'documentation_url': None, 'burned_area_ha': None,
            'footprint_ha': None, 'footprint': mapping(support), 'geometry_role': 'illustrative_report_location',
            'detections': [], 'weather': point(cast(Snapshot, weather), lat, lon)}


class HappyRobotProvider:
    def __init__(self, database=None) -> None:
        spec = importlib.util.spec_from_file_location('flareai_happyrobot112', ROOT / 'happyrobot-112/server.py')
        if spec is None or spec.loader is None:
            raise RuntimeError('No se encontró happyrobot-112')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.load_env()
        self.client = self.module.HappyRobotClient()
        try:
            self.workflow_id = self.module.workflow_id()
        except RuntimeError:
            self.workflow_id = ''
        self.ready = bool(self.client.key and self.workflow_id)
        self.sessions: dict[str, str] = {}
        config = database.responder_setting() if database else {}
        self.responder_workflow_id = config.get('workflow_id', '') if config.get('published') else ''
        self.responder_ready = bool(self.client.key and self.responder_workflow_id)

    def create(self, session_id: str, role: str = 'citizen', context: dict | None = None) -> dict:
        identifier = self.responder_workflow_id if role == 'firefighter' else self.workflow_id
        if not identifier:
            raise RuntimeError('El workflow de voz no está publicado')
        return self.client.request('POST', '/voice/tokens/', {'workflow_id': identifier, 'env': 'production',
                                   'ttl_seconds': 1800, 'data': {'source': 'flareai-demo-webcall', 'demo_session': session_id,
                                                               'role': role, 'incident': context or {}}})

    def messages(self, run_id: str) -> list[dict]:
        session = self.sessions.get(run_id)
        if not session:
            try:
                rows = self.module.list_data(self.client.request('GET', f'/runs/{run_id}/sessions?page=1&page_size=10&sort=desc'))
            except self.module.HappyRobotError as error:
                if error.status == 404:
                    return []
                raise
            rows = [row for row in rows if row.get('run_id') == run_id]
            if not rows:
                return []
            session = str(uuid.UUID(rows[0]['id']))
            self.sessions[run_id] = session
        payload = self.client.request('GET', f'/sessions/{session}/messages?page=1&page_size=100&sort=desc')
        return list(reversed(self.module.list_data(payload)))


class DemoBridge:
    def __init__(self, database, provider=None, resolver: Callable | None = None) -> None:
        self.db = database
        self.provider = provider if provider is not None else HappyRobotProvider(database)
        self.resolver = resolver if resolver is not None else LocationResolver(database)
        self.session_id = str(uuid.uuid4())
        self.lock = threading.RLock()
        self.calls: dict[str, dict] = {}
        self.owners: dict[str, str] = {}
        self.browsers: dict[str, float] = {}
        self.version = 0
        self.latest_id: str | None = None
        self.public_url: str | None = None
        self.starting = 0
        self.polling: set[str] = set()
        self.call_locks: dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=MAX_ACTIVE_CALLS, thread_name_prefix='demo-call')
        self.closed = threading.Event()
        self.field_reports: dict[str, dict] = {}
        self.sensor_incidents: dict[str, dict] = {}
        self.db.start_demo(self.session_id)
        self.cloud_polled_at = 0.0
        self.cloud_error: str | None = None

    def open_browser(self) -> str:
        with self.lock:
            now = time.monotonic()
            self.browsers = {key: expires for key, expires in self.browsers.items() if expires > now}
            if len(self.browsers) >= 64:
                raise PermissionError('La demo ha alcanzado el límite de navegadores de esta sesión')
            token = secrets.token_urlsafe(32)
            self.browsers[hashlib.sha256(token.encode()).hexdigest()] = now + 21600
            return token

    def authorized(self, token: str) -> bool:
        with self.lock:
            return self.browsers.get(hashlib.sha256(token.encode()).hexdigest(), 0) > time.monotonic()

    def register(self, run_id: str, owner: str = '', role: str = 'citizen', binding: dict | None = None) -> None:
        run_id = str(uuid.UUID(run_id))
        with self.lock:
            self.calls[run_id] = {'summary': {}, 'state': 'waiting', 'location': None, 'reported_at': datetime.now(timezone.utc).isoformat(),
                                  'poll_until': time.monotonic() + 900, 'last_poll': 0, 'target_id': None,
                                  'role': role, 'binding': deepcopy(binding or {}), 'part': {}, 'part_updates': {}}
            self.owners[run_id] = owner
            self.call_locks[run_id] = threading.Lock()
            self.persist(run_id)

    def create_call(self, owner: str, role: str = 'citizen', binding: dict | None = None) -> dict:
        with self.lock:
            if not self.authorized(owner):
                raise PermissionError('Abre primero el marcador de la demo')
            if role not in {'citizen', 'firefighter'}:
                raise ValueError('Tipo de llamada no válido')
            if role == 'firefighter':
                citizen = binding and self.calls.get(str(binding.get('run_id', '')), {}).get('role') == 'citizen'
                sensor = binding and self.sensor_incidents.get(str(binding.get('sensor_id', '')))
                if not citizen and not sensor:
                    raise ValueError('Selecciona un aviso activo para informar')
            if not self.provider.ready or role == 'firefighter' and not self.provider.responder_ready:
                raise RuntimeError('HappyRobot no está configurado para este número')
            active = sum(not c.get('ended') and c['poll_until'] > time.monotonic() for c in self.calls.values())
            if len(self.calls) + self.starting >= MAX_SESSION_CALLS or active + self.starting >= MAX_ACTIVE_CALLS:
                raise RuntimeError('La demo ha alcanzado su capacidad de llamadas; reintenta al quedar una plaza libre.')
            self.starting += 1
        reserved = True
        try:
            payload = self.provider.create(self.session_id, role, binding) if role == 'firefighter' else self.provider.create(self.session_id)
            run_id = str(uuid.UUID(payload['run_id']))
            result = {key: payload[key] for key in ('url', 'token', 'room_name', 'run_id')}
            with self.lock:
                self.starting -= 1
                reserved = False
                self.register(run_id, owner, role, binding)
            return result
        finally:
            if reserved:
                with self.lock:
                    self.starting -= 1

    def persist(self, run_id: str, value: dict | None = None) -> None:
        data = {key: item for key, item in (value if value is not None else self.calls[run_id]).items() if key not in {'poll_until', 'last_poll', 'location_retry'}}
        self.db.save_demo_call(self.session_id, run_id, data)

    def accept_part(self, run_id: str, messages: list[dict]) -> None:
        incoming = extract_part(messages)
        with self.lock:
            call = self.calls[run_id]
            changes = {k: v for k, v in incoming.items() if call['part'].get(k) != v}
            if not changes:
                return
            at = datetime.now(timezone.utc).isoformat()
            updated = deepcopy(call)
            updated['part'].update(changes)
            updated['part_updates'].update({k: {'value': v, 'revision': self.version + 1, 'at': at} for k, v in changes.items()})
            updated.update(state='field_report', updated_at=at, revision=self.version + 1)
            updated['summary'] = {'ubicacion': call['binding'].get('label', ''), 'emergencia': updated['part'].get('incendio', 'pendiente'),
                                  'riesgos': updated['part'].get('detalle', '')}
            updated.pop('error', None)
            self.persist(run_id, updated)
            self.calls[run_id] = updated
            self.version += 1

    def accept(self, run_id: str, messages: list[dict]) -> None:
        with self.lock:
            call_lock = self.call_locks[run_id]
        with call_lock:
            self.accept_update(run_id, messages)

    def accept_update(self, run_id: str, messages: list[dict]) -> None:
        with self.lock:
            role = self.calls[run_id].get('role', 'citizen')
        if role == 'firefighter':
            self.accept_part(run_id, messages)
            return
        incoming = extract_report(messages)
        with self.lock:
            call = self.calls[run_id]
            summary = {**call['summary'], **incoming}
            if summary == call['summary']:
                return
            old_location = call['summary'].get('ubicacion')
        location = maritime_location(summary)
        if location is None:
            location = call['location'] if old_location == summary.get('ubicacion') and not (call['location'] or {}).get('maritime') else self.resolver(summary.get('ubicacion', ''))
        state = 'not_fire' if not is_fire(summary) else 'located' if location else 'needs_location'
        with self.lock:
            call = self.calls[run_id]
            if summary == call['summary'] and location == call['location'] and state == call['state']:
                return
            updated = {**call, 'summary': summary, 'location': location, 'state': state, 'revision': self.version + 1,
                       'updated_at': datetime.now(timezone.utc).isoformat()}
            updated.pop('error', None)
            self.persist(run_id, updated)
            self.calls[run_id] = updated
            self.version += 1

    def poll_call(self, run_id: str) -> None:
        try:
            self.accept(run_id, self.provider.messages(run_id))
            with self.lock:
                self.calls[run_id].pop('error', None)
        except Exception:
            with self.lock:
                self.calls[run_id]['error'] = 'No se pudo actualizar desde HappyRobot; reintentando'
        finally:
            with self.lock:
                self.calls[run_id]['last_poll'] = time.monotonic()
                self.polling.discard(run_id)

    def discover_cloud_calls(self) -> None:
        now = time.monotonic()
        if getattr(self.db, 'dynamic_cloud', False) is not True or now - self.cloud_polled_at < 2:
            return
        self.cloud_polled_at = now
        try:
            rows = self.db.demo_calls(self.session_id)
            with self.lock:
                for row in rows:
                    identifier = str(uuid.UUID(row['id']))
                    if identifier not in self.calls:
                        if len(self.calls) >= MAX_SESSION_CALLS:
                            raise RuntimeError('Capacidad de sesión alcanzada')
                        self.register(identifier, owner='cloud', role='citizen')
                    if row.get('ended_at') and not self.calls[identifier].get('ended'):
                        self.calls[identifier].update(ended=True, poll_until=now + 20)
                self.cloud_error = None
        except Exception:
            self.cloud_error = 'No se pudieron sincronizar las llamadas de Twin; reintentando sin duplicarlas'

    def poll_once(self, wait: bool = True) -> None:
        self.discover_cloud_calls()
        with self.lock:
            if self.closed.is_set():
                return
            now = time.monotonic()
            runs = [key for key, call in sorted(self.calls.items(), key=lambda pair: pair[1]['last_poll'])
                    if call['poll_until'] > now and key not in self.polling and now - call['last_poll'] >= 2]
            if not wait:
                runs = runs[:max(0, MAX_ACTIVE_CALLS - len(self.polling))]
            self.polling.update(runs)
            futures = [self.executor.submit(self.poll_call, run_id) for run_id in runs]
        if wait:
            for future in futures:
                future.result()

    def loop(self) -> None:
        while not self.closed.is_set():
            self.poll_once(wait=False)
            self.closed.wait(.25)

    def close(self) -> None:
        with self.lock:
            self.closed.set()
        self.executor.shutdown(wait=True)

    def brief(self, run_id: str, owner: str) -> dict:
        with self.lock:
            if not self.authorized(owner) or self.owners.get(run_id) != owner:
                raise PermissionError('Esta llamada no pertenece a este navegador')
            call = self.calls[run_id]
            return {'status': call['state'], 'summary': dict(call['summary']), 'map_status': call['state'],
                    'updated_at': call.get('updated_at', call['reported_at']), 'error': call.get('error'), 'location': deepcopy(call['location']),
                    'role': call.get('role', 'citizen'), 'part': deepcopy(call.get('part', {})), 'binding': deepcopy(call.get('binding', {}))}

    def stop(self, run_id: str, owner: str) -> None:
        self.brief(run_id, owner)
        with self.lock:
            self.calls[run_id]['poll_until'] = time.monotonic() + 20
            self.calls[run_id]['ended'] = True
            self.persist(run_id)

    def public_state(self) -> dict:
        with self.lock:
            return {'session_id': self.session_id, 'version': self.version, 'latest_id': self.latest_id, 'cloud_error': self.cloud_error,
                    'field_reports': deepcopy(self.field_reports),
                    'last_update_role': max(self.calls.values(), key=lambda c: c.get('revision', 0), default={}).get('role'),
                    'calls': [{'id': key, 'role': c.get('role', 'citizen'), 'state': c['state'], 'location': (c['location'] or {}).get('label'), 'error': c.get('error'), 'ended': c.get('ended', False)}
                              for key, c in self.calls.items()]}

    def overlay(self, incidents: list[dict], weather: dict, now: datetime) -> list[dict]:
        with self.lock:
            calls = deepcopy(self.calls)
            self.sensor_incidents = {i['id']: {'lat': i['lat'], 'lon': i['lon']} for i in incidents
                                     if (i.get('sensor_report') or i.get('scene_report')) and i.get('scenario', {}).get('phase') not in {'closed', 'releasing'}}
        result = [deepcopy(i) for i in incidents]
        latest_revision = -1
        latest_id = None
        targets = {}
        for run_id, call in calls.items():
            if call['state'] != 'located' or (now - datetime.fromisoformat(call['reported_at'])).total_seconds() > 86400:
                continue
            target = match_incident(call['location'], [i for i in result if i.get('source_kind') != 'call']) if call['location']['precision'] == 'locality' and not call['location'].get('reason') else None
            if target is None:
                item = call_incident(run_id, call, weather)
                result.append(item)
            else:
                item = next(i for i in result if i['id'] == target)
            targets[run_id] = item
            if item.get('confirmation', {}).get('status') != 'confirmed':
                item['confirmation'] = {'status': 'confirmed', 'demo': True, 'source_name': 'Llamada web · demo',
                                        'source_url': '/api/demo/report/' + run_id, 'confirmed_at': call['reported_at'],
                                        'valid_until': (datetime.fromisoformat(call['reported_at']) + timedelta(hours=24)).isoformat()}
            item['demo_report'] = {'location': call['location'], 'summary': call['summary'], 'run_id': run_id,
                                   'reported_at': call['reported_at'], 'session_id': self.session_id}
            if call.get('revision', 0) > latest_revision:
                latest_revision, latest_id = call.get('revision', 0), item['id']
        reports: dict[str, dict] = {}
        for run_id, call in calls.items():
            binding = call.get('binding', {})
            sensor_id = binding.get('sensor_id')
            target_item = next((i for i in result if i['id'] == sensor_id), None) if sensor_id else targets.get(binding.get('run_id'))
            if call.get('role') != 'firefighter' or not target_item or not call.get('part_updates'):
                continue
            item = target_item
            origin = item if sensor_id else calls[binding['run_id']]['location']
            if any(binding.get(k) != origin.get(k) for k in ('lat', 'lon')):
                continue
            report = reports.setdefault(item['id'], {'incident_id': item['id'], 'fields': {}, 'field_versions': {}, 'field_sources': {}, 'revision': 0})
            for key, update in call['part_updates'].items():
                if update['revision'] > report['field_versions'].get(key, 0):
                    report['fields'][key] = update['value']
                    report['field_versions'][key] = update['revision']
                    report['field_sources'][key] = {'run_id': run_id, 'resource_id': binding.get('resource_id')}
                if update['revision'] > report['revision']:
                    report.update(revision=update['revision'], at=update['at'], run_id=run_id, resource_id=binding.get('resource_id'))
        for item in result:
            report = reports.get(item['id'], {})
            if not report:
                continue
            item['responder_report'] = report
            status = report['fields'].get('incendio')
            if status in {'descartado', 'extinguido'}:
                if item.get('demo_report'):
                    item['demo_report']['cancelled'] = True
                if item.get('confirmation', {}).get('demo'):
                    item['confirmation'] = {'status': 'unconfirmed', 'demo': True, 'reason': 'Parte de bomberos · ' + status}
            elif status == 'confirmado' and item.get('confirmation', {}).get('demo'):
                item['confirmation'] = {**item['confirmation'], 'source_name': 'Bomberos · confirmado en demo', 'confirmed_at': report['at'], 'source_url': '/api/demo/report/' + report['run_id']}
        with self.lock:
            self.latest_id = latest_id
            self.field_reports = reports
        return sorted([i for i in result if not (i.get('source_kind') == 'call' and i.get('demo_report', {}).get('cancelled'))],
                      key=lambda i: bool(i.get('demo_report')), reverse=True)


def publish(port: int = 8112) -> None:
    import os
    import signal
    import subprocess
    from urllib.error import HTTPError

    origin = f'http://127.0.0.1:{port}'
    with urlopen(origin + '/112/api/status', timeout=5) as response:
        status = json.load(response)
    if not status.get('integrated') or not status.get('configured'):
        raise RuntimeError('Arranca app.py con la demo integrada antes de publicar')
    try:
        urlopen(origin + '/api/data', timeout=5).close()
    except HTTPError as error:
        if error.code != 404:
            raise RuntimeError('El puerto móvil no está aislado') from error
        error.close()
    else:
        raise RuntimeError('No se publicará un puerto que exponga el mapa')
    binary = ROOT / '.local/cloudflared/cloudflared'
    if not binary.is_file():
        raise RuntimeError('Instala cloudflared en .local/cloudflared/')
    runtime = ROOT / '.local/demo-public.json'
    process = subprocess.Popen([str(binary), 'tunnel', '--config', '/dev/null', '--no-autoupdate', '--protocol', 'http2', '--url', origin],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               env={**{key: value for key, value in os.environ.items() if not key.startswith(('TUNNEL_', 'CLOUDFLARE_', 'HAPPYROBOT_'))}, 'HOME': str(binary.parent)})

    def stop(signum, frame) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        if process.stdout is None:
            raise RuntimeError('No se pudo leer la dirección pública')
        for line in process.stdout:
            match = re.search(r'https://(?!api\.)[a-z0-9]+(?:-[a-z0-9]+)+\.trycloudflare\.com', line)
            if match:
                data = {'url': match.group(0), 'pid': process.pid, 'port': port}
                temporary = runtime.with_suffix('.tmp')
                temporary.write_text(json.dumps(data))
                temporary.replace(runtime)
                print(f"Webcall pública: {data['url']}/112/", flush=True)
                print('Abre el marcador desde el móvil, sin código. Mantén este proceso abierto.', flush=True)
            elif 'ERR' in line:
                print('El túnel está reintentando la conexión con Cloudflare.', flush=True)
        if process.wait() != 0:
            raise RuntimeError('Cloudflare no pudo mantener el túnel; vuelve a ejecutar publish')
    except KeyboardInterrupt:
        pass
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        if runtime.exists() and json.loads(runtime.read_text()).get('pid') == process.pid:
            runtime.unlink()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['publish'])
    parser.add_argument('--port', type=int, default=8112)
    options = parser.parse_args()
    publish(options.port)
