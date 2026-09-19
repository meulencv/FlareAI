from __future__ import annotations

import hashlib
import heapq
import json
import math
import threading
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from build_emergency_db import distance_km

SPEEDS = {'motorway': 90, 'trunk': 70, 'primary': 60, 'secondary': 50, 'tertiary': 45,
          'unclassified': 35, 'residential': 25, 'living_street': 10, 'service': 15, 'track': 10}
HIGHWAYS = set(SPEEDS) | {name + '_link' for name in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary')}
LIMITATIONS = 'Ruta local sobre OSM para demo; sin tráfico, cortes, gálibos ni restricciones de giro completas. No es itinerario operativo para emergencias.'


def valid_point(point) -> bool:
    return len(point) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in point) and -19 <= point[0] <= 5 and 27 <= point[1] <= 44.5


def km(a, b) -> float:
    return distance_km(a[1], a[0], b[1], b[0])


def route_bounds(start, end) -> tuple[float, float, float, float]:
    if not valid_point(start) or not valid_point(end) or km(start, end) > 60:
        raise ValueError('Fuera del ámbito local de rutas (60 km)')
    west = math.floor((min(start[0], end[0]) - .03) * 10) / 10
    east = math.ceil((max(start[0], end[0]) + .03) * 10) / 10
    south = math.floor((min(start[1], end[1]) - .025) * 10) / 10
    north = math.ceil((max(start[1], end[1]) + .025) * 10) / 10
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

    def route(self, start: list[float], end: list[float]) -> dict:
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
                candidate = cost + duration
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
                'fetched_at': time.time(), 'limitations': LIMITATIONS,
                'start_gap_m': round(km(start, points[0]) * 1000), 'end_gap_m': round(km(end, points[-1]) * 1000)}


class LocalRouter:
    def __init__(self, database, offline: bool = False) -> None:
        self.db, self.offline = database, offline
        self.graphs: dict[str, RoadGraph] = {}
        self.lock = threading.Lock()
        self.last_download = 0.0

    def route(self, start: list[float], end: list[float]) -> dict:
        bounds = route_bounds(start, end)
        key = 'local-route-v1:' + hashlib.sha256(json.dumps([start, end]).encode()).hexdigest()[:24]
        with self.lock:
            cached = self.db.get_asset(key)
            if cached and time.time() - cached['data']['fetched_at'] < 604800:
                return cached['data']
            graph_id = 'local-road-graph-v1:' + ':'.join(map(str, bounds))
            if graph_id not in self.graphs:
                stored = self.db.get_asset(graph_id)
                if stored and (self.offline or time.time() - stored['data']['fetched_at'] < 604800):
                    payload = stored['data']
                else:
                    payload = self.download(bounds)
                    self.db.asset(graph_id, 'local_road_graph', payload)
                if len(self.graphs) >= 6:
                    self.graphs.pop(next(iter(self.graphs)))
                self.graphs[graph_id] = RoadGraph(payload)
            route = self.graphs[graph_id].route(start, end)
            self.db.asset(key, 'director_route', route)
            return route

    def download(self, bounds) -> dict:
        if self.offline:
            raise RuntimeError('Grafo viario no disponible offline')
        time.sleep(max(0, 5 - (time.monotonic() - self.last_download)))
        self.last_download = time.monotonic()
        bbox = ','.join(map(str, bounds))
        highway = '|'.join(sorted(HIGHWAYS))
        query = f'[out:json][timeout:25];way["highway"~"^({highway})$"]({bbox});out geom;'
        request = Request('https://overpass-api.de/api/interpreter', data=urlencode({'data': query}).encode(),
                          headers={'User-Agent': 'FlareAI-Hackathon/1.0 local road graph', 'Content-Type': 'application/x-www-form-urlencoded'})
        with urlopen(request, timeout=35) as response:
            raw = response.read(24_000_001)
        if len(raw) > 24_000_000:
            raise ValueError('Grafo demasiado grande')
        payload = json.loads(raw)
        if payload.get('remark') or not payload.get('elements'):
            raise ValueError('Descarga viaria incompleta o sin datos')
        payload['fetched_at'] = time.time()
        payload['bounds'] = bounds
        return payload
