from __future__ import annotations

import hashlib
import heapq
import json
import math
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from build_emergency_db import OVERPASS, distance_km

SPEEDS = {'motorway': 90, 'trunk': 70, 'primary': 60, 'secondary': 50, 'tertiary': 45,
          'unclassified': 35, 'residential': 25, 'living_street': 10, 'service': 15, 'track': 10}
HIGHWAYS = set(SPEEDS) | {name + '_link' for name in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary')}
LIMITATIONS = 'Ruta ilustrativa OSM; cortes y demoras del escenario, no tráfico real. Sin gálibos ni restricciones de giro completas. No es itinerario operativo.'
DEMO_BOUNDS = (41.28, 2.00, 41.54, 2.32)
DEMO_GRAPH = 'barcelona-demo-road-v1'


def edge_id(a: int, b: int) -> str:
    return f'{min(a, b)}:{max(a, b)}'


def in_demo(point) -> bool:
    return DEMO_BOUNDS[1] <= point[0] <= DEMO_BOUNDS[3] and DEMO_BOUNDS[0] <= point[1] <= DEMO_BOUNDS[2]


def valid_point(point) -> bool:
    return len(point) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in point) and -19 <= point[0] <= 5 and 27 <= point[1] <= 44.5


def km(a, b) -> float:
    return distance_km(a[1], a[0], b[1], b[0])


def route_bounds(start, end) -> tuple[float, float, float, float]:
    if not valid_point(start) or not valid_point(end) or km(start, end) > 60:
        raise ValueError('Fuera del ámbito local de rutas (60 km)')
    west = math.floor((min(start[0], end[0]) - .015) * 100) / 100
    east = math.ceil((max(start[0], end[0]) + .015) * 100) / 100
    south = math.floor((min(start[1], end[1]) - .015) * 100) / 100
    north = math.ceil((max(start[1], end[1]) + .015) * 100) / 100
    if (east - west) * (north - south) > .7:
        raise ValueError('Área viaria demasiado grande para consulta bajo demanda')
    return south, west, north, east


class RoadGraph:
    def __init__(self, payload: dict) -> None:
        self.points: dict[int, list[float]] = {}
        self.edges: dict[int, list[tuple[int, float, float]]] = {}
        self.cells: dict[tuple[int, int], list[int]] = {}
        for way in payload.get('elements', []):
            if way.get('type') != 'way':
                continue
            tags = way.get('tags', {})
            highway = tags.get('highway')
            if highway not in HIGHWAYS or tags.get('area') == 'yes':
                continue
            access = next((tags[key] for key in ('motorcar', 'motor_vehicle', 'vehicle', 'access') if key in tags), 'yes')
            if access in {'no', 'private', 'agricultural', 'forestry', 'customers', 'delivery'}:
                continue
            if tags.get('construction') or tags.get('access:conditional') or tags.get('motor_vehicle:conditional'):
                continue
            nodes, geometry = way.get('nodes', []), way.get('geometry', [])
            if len(nodes) != len(geometry):
                continue
            coords = [[p.get('lon'), p.get('lat')] for p in geometry]
            if any(not valid_point(p) for p in coords):
                continue
            speed = float(SPEEDS.get(highway.removesuffix('_link'), 25))
            try:
                speed = min(speed, max(5, float(tags.get('maxspeed', speed))))
            except (ValueError, TypeError):
                pass
            oneway = tags.get('oneway', 'yes' if tags.get('junction') == 'roundabout' or highway == 'motorway' else 'no')
            for identifier, point in zip(nodes, coords):
                self.points[identifier] = point
            for a, b in zip(nodes, nodes[1:]):
                distance = km(self.points[a], self.points[b])
                if not distance:
                    continue
                cost = distance / speed * 3600
                if oneway != '-1':
                    self.edges.setdefault(a, []).append((b, cost, distance))
                if oneway not in {'yes', 'true', '1'}:
                    self.edges.setdefault(b, []).append((a, cost, distance))
        for identifier, point in self.points.items():
            self.cells.setdefault((math.floor(point[0] * 100), math.floor(point[1] * 100)), []).append(identifier)

    def nearest(self, point) -> int:
        x, y = math.floor(point[0] * 100), math.floor(point[1] * 100)
        candidates = [n for dx in range(-2, 3) for dy in range(-2, 3) for n in self.cells.get((x + dx, y + dy), [])]
        if not candidates:
            raise ValueError('No hay carretera cerca del punto')
        node = min(candidates, key=lambda n: km(point, self.points[n]))
        if km(point, self.points[node]) > .75:
            raise ValueError('Punto a más de 750 m de la red viaria')
        return node

    def route(self, start: list[float], end: list[float], blocked: set[str] | None = None, congestion: dict[str, float] | None = None) -> dict:
        blocked, congestion = blocked or set(), congestion or {}
        source, target = self.nearest(start), self.nearest(end)
        if source == target:
            raise ValueError('No hay desplazamiento viario representable')
        costs, previous = {source: 0.0}, {}
        queue = [(0.0, 0.0, source)]
        visited = 0
        while queue:
            _, cost, node = heapq.heappop(queue)
            if cost > costs[node]:
                continue
            if node == target:
                break
            visited += 1
            if visited > 300000:
                raise ValueError('Límite del cálculo local alcanzado')
            for neighbor, duration, _ in self.edges.get(node, []):
                edge = edge_id(node, neighbor)
                if edge in blocked:
                    continue
                candidate = cost + duration * max(1, min(10, congestion.get(edge, 1)))
                if candidate < costs.get(neighbor, math.inf):
                    costs[neighbor], previous[neighbor] = candidate, node
                    heuristic = km(self.points[neighbor], self.points[target]) / 90 * 3600
                    heapq.heappush(queue, (candidate + heuristic, candidate, neighbor))
        if target not in previous:
            raise ValueError('Sin conexión viaria dentro de la zona descargada')
        path = [target]
        while path[-1] != source:
            path.append(previous[path[-1]])
        points = [self.points[n] for n in reversed(path)]
        cumulative = [0.0]
        for a, b in zip(points, points[1:]):
            cumulative.append(cumulative[-1] + km(a, b))
        return {'coordinates': points, 'cumulative_km': cumulative, 'distance_km': cumulative[-1],
                'duration_seconds': costs[target], 'source': 'OpenStreetMap · A* local',
                'edge_ids': [edge_id(a, b) for a, b in zip(reversed(path), list(reversed(path))[1:])],
                'fetched_at': time.time(), 'limitations': LIMITATIONS,
                'start_gap_m': round(km(start, points[0]) * 1000), 'end_gap_m': round(km(end, points[-1]) * 1000)}


class LocalRouter:
    route_lock = threading.Lock()
    route_next_request = 0.0
    route_unavailable: dict[str, float] = {}

    def __init__(self, database, offline: bool = False) -> None:
        self.db, self.offline = database, offline
        self.graphs: dict[str, RoadGraph] = {}
        self.graph_bounds: dict[str, tuple] = {}
        self.lock = threading.Lock()
        self.last_download = 0.0
        self.failures: dict[tuple, float] = {}

    def demo_graph(self) -> RoadGraph:
        if DEMO_GRAPH not in self.graphs:
            stored = self.db.get_asset(DEMO_GRAPH)
            if not stored or not isinstance(stored, dict):
                raise RuntimeError('Falta precargar Barcelona: python local_routes.py --prepare-demo')
            self.graphs[DEMO_GRAPH] = RoadGraph(stored['data'])
        return self.graphs[DEMO_GRAPH]

    def demo_roads(self, bounds: list[float]) -> list[dict]:
        graph = self.demo_graph()
        west, south, east, north = bounds
        roads, seen = [], set()
        for a, edges in graph.edges.items():
            point = graph.points[a]
            if not west <= point[0] <= east or not south <= point[1] <= north:
                continue
            for b, _, distance in edges:
                identifier = edge_id(a, b)
                if identifier not in seen and distance > .025:
                    seen.add(identifier)
                    roads.append({'id': identifier, 'coordinates': [point, graph.points[b]], 'length_km': distance})
                if len(roads) >= 4000:
                    return roads
        return roads

    def route(self, start: list[float], end: list[float], *, scenario: bool = False, blocked: set[str] | None = None, congestion: dict[str, float] | None = None) -> dict:
        bounds = route_bounds(start, end)
        if scenario and in_demo(start) and in_demo(end):
            with self.lock:
                return self.demo_graph().route(start, end, blocked, congestion)
        if blocked:
            raise ValueError('No se permite usar un proveedor que desconozca los cortes del escenario')
        key = 'local-route-v1:' + hashlib.sha256(json.dumps([start, end]).encode()).hexdigest()[:24]
        with self.lock:
            cached = self.db.get_asset(key)
            if cached and time.time() - cached['data']['fetched_at'] < 604800:
                return cached['data']
            if not self.offline:
                try:
                    route = self.remote_route(start, end)
                except RuntimeError:
                    pass
                else:
                    self.db.asset(key, 'director_route', route)
                    return route
            graph_id = next((identifier for identifier, box in self.graph_bounds.items()
                             if box[0] <= bounds[0] and box[1] <= bounds[1] and box[2] >= bounds[2] and box[3] >= bounds[3]),
                            'local-road-graph-v1:' + ':'.join(map(str, bounds)))
            if graph_id not in self.graphs:
                stored = self.db.get_asset(graph_id)
                if stored and (self.offline or time.time() - stored['data']['fetched_at'] < 604800):
                    payload = stored['data']
                else:
                    raise RuntimeError('Proveedores de rutas no disponibles y sin red local cacheada; buscando otra sede')
                if len(self.graphs) >= 6:
                    expired = next(iter(self.graphs))
                    if expired != DEMO_GRAPH:
                        self.graphs.pop(expired)
                        self.graph_bounds.pop(expired, None)
                self.graphs[graph_id] = RoadGraph(payload)
                self.graph_bounds[graph_id] = bounds
            route = self.graphs[graph_id].route(start, end)
            self.db.asset(key, 'director_route', route)
            return route

    def remote_route(self, start: list[float], end: list[float]) -> dict:
        route_bounds(start, end)
        points = ';'.join(','.join(map(str, p)) for p in (start, end))
        providers = ('https://router.project-osrm.org', 'https://routing.openstreetmap.de/routed-car')
        with self.route_lock:
            for provider in providers:
                if self.route_unavailable.get(provider, 0) > time.monotonic():
                    continue
                time.sleep(max(0, LocalRouter.route_next_request - time.monotonic()))
                LocalRouter.route_next_request = time.monotonic() + 1.05
                request = Request(provider + '/route/v1/driving/' + points + '?overview=full&geometries=geojson&steps=false',
                                  headers={'User-Agent': 'FlareAI-Hackathon/1.0 (simulated response map)'})
                try:
                    with urlopen(request, timeout=6) as response:
                        raw = response.read(4_000_001)
                    if len(raw) > 4_000_000:
                        raise ValueError('Ruta demasiado grande')
                    payload = json.loads(raw)
                    if payload.get('code') != 'Ok' or not payload.get('routes'):
                        continue
                    result = payload['routes'][0]
                    coords = result['geometry']['coordinates']
                    duration = float(result['duration'])
                    if result['geometry'].get('type') != 'LineString' or not 2 <= len(coords) <= 20000 or any(not valid_point(p) for p in coords) or not math.isfinite(duration) or duration <= 0:
                        raise ValueError('Geometría de ruta inválida')
                    start_gap, end_gap = km(start, coords[0]), km(end, coords[-1])
                    if max(start_gap, end_gap) > .75:
                        raise ValueError('La ruta termina lejos de la ubicación comunicada')
                    cumulative = [0.0]
                    for a, b in zip(coords, coords[1:]):
                        cumulative.append(cumulative[-1] + km(a, b))
                    if not 0 < cumulative[-1] <= 400:
                        raise ValueError('Distancia de ruta inválida')
                    return {'coordinates': coords, 'cumulative_km': cumulative, 'distance_km': cumulative[-1],
                            'duration_seconds': duration, 'source': 'OpenStreetMap · OSRM', 'provider': provider,
                            'mode': 'road_api', 'fetched_at': time.time(), 'start_gap_m': round(start_gap * 1000), 'end_gap_m': round(end_gap * 1000),
                            'limitations': 'Ruta de conducción sobre OSM para demo, sin tráfico ni validación operativa para vehículos de emergencia. Tiempo visual acelerado.'}
                except OSError as error:
                    if isinstance(error, HTTPError):
                        error.close()
                    self.route_unavailable[provider] = time.monotonic() + 30
                except (ValueError, KeyError, TypeError):
                    continue
        raise RuntimeError('No hay ruta utilizable en los proveedores OSM; se intentarán otras unidades')

    def download(self, bounds, allow_empty: bool = False) -> dict:
        if self.offline:
            raise RuntimeError('Grafo viario no disponible offline')
        if self.failures.get(bounds, 0) > time.monotonic():
            raise RuntimeError('Servicio de calles temporalmente no disponible; reintento pendiente')
        bbox = ','.join(map(str, bounds))
        highway = '|'.join(sorted(HIGHWAYS))
        query = f'[out:json][timeout:{60 if allow_empty else 20}];way["highway"~"^({highway})$"]({bbox});out geom;'
        error: Exception | None = None
        for endpoint in OVERPASS:
            time.sleep(max(0, 5 - (time.monotonic() - self.last_download)))
            self.last_download = time.monotonic()
            request = Request(endpoint, data=urlencode({'data': query}).encode(),
                              headers={'User-Agent': 'FlareAI-Hackathon/1.0 local road graph', 'Content-Type': 'application/x-www-form-urlencoded'})
            try:
                with urlopen(request, timeout=75 if allow_empty else 25) as response:
                    raw = response.read(24_000_001)
                if len(raw) > 24_000_000:
                    raise ValueError('Grafo demasiado grande')
                payload = json.loads(raw)
                if payload.get('remark') or not isinstance(payload.get('elements'), list) or not payload['elements'] and not allow_empty:
                    raise ValueError('Descarga viaria incompleta o sin datos')
                payload.update(fetched_at=time.time(), bounds=bounds)
                self.failures.pop(bounds, None)
                return payload
            except HTTPError as caught:
                caught.close()
                if caught.code not in {429, 500, 502, 503, 504}:
                    raise
                error = caught
            except (OSError, ValueError) as caught:
                error = caught
        self.failures = {key: until for key, until in self.failures.items() if until > time.monotonic()}
        self.failures[bounds] = time.monotonic() + 30
        raise RuntimeError('No se pudo descargar la red viaria desde los proveedores OSM; se reintentará') from error


def prepare_demo(database) -> dict:
    router = LocalRouter(database)
    elements = {}
    south, west, north, east = DEMO_BOUNDS
    with database.verification_lock(804031) as acquired:
        if not acquired:
            raise RuntimeError('Ya hay una preparación viaria en curso')
        for y in range(4):
            for x in range(4):
                box = tuple(round(v, 5) for v in (south + (north - south) * y / 4, west + (east - west) * x / 4,
                                                 south + (north - south) * (y + 1) / 4, west + (east - west) * (x + 1) / 4))
                key = DEMO_GRAPH + f':tile:{y}:{x}'
                cached = database.get_asset(key)
                if cached:
                    payload = cached['data']
                else:
                    try:
                        payload = router.download(box, allow_empty=True)
                    except RuntimeError:
                        parts = []
                        for sy in range(2):
                            for sx in range(2):
                                subkey = key + f':{sy}:{sx}'
                                subcache = database.get_asset(subkey)
                                subbox = (box[0] + (box[2] - box[0]) * sy / 2, box[1] + (box[3] - box[1]) * sx / 2,
                                          box[0] + (box[2] - box[0]) * (sy + 1) / 2, box[1] + (box[3] - box[1]) * (sx + 1) / 2)
                                part = subcache['data'] if subcache else router.download(tuple(round(v, 5) for v in subbox), allow_empty=True)
                                if not subcache:
                                    database.asset(subkey, 'demo_road_tile', part)
                                parts.extend(part['elements'])
                        payload = {'elements': parts, 'bounds': box, 'fetched_at': time.time()}
                    database.asset(key, 'demo_road_tile', payload)
                elements.update({w['id']: w for w in payload['elements'] if w.get('type') == 'way'})
                print(f'Barcelona: tesela {y * 4 + x + 1}/16 · {len(elements)} vías acumuladas', flush=True)
        payload = {'elements': list(elements.values()), 'bounds': DEMO_BOUNDS, 'fetched_at': time.time(), 'attribution': '© OpenStreetMap contributors · ODbL'}
        graph = RoadGraph(payload)
        if len(graph.points) < 1000:
            raise RuntimeError('Red de Barcelona incompleta')
        database.asset(DEMO_GRAPH, 'demo_road_graph', payload)
        return {'nodes': len(graph.points), 'ways': len(elements), 'bounds': DEMO_BOUNDS, 'fetched_at': payload['fetched_at']}


if __name__ == '__main__':
    import argparse
    from database import Database
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-demo', action='store_true', required=True)
    parser.parse_args()
    print(json.dumps(prepare_demo(Database()), ensure_ascii=False))
