"""Polígono ilustrativo con forma de fuego: frentes irregulares orientados por el viento.

Solo para geometrías de escenario o de aviso (``illustrative``). Nunca sustituye la huella
térmica NASA ni interviene en cálculos de superficie o distancia.
"""
from __future__ import annotations

import math
import random

MIN_RADIUS_FACTOR = .35
MAX_RADIUS_FACTOR = 1.9


def fire_polygon(lon: float, lat: float, radius_km: float, wind_to: float, seed: str, points: int = 72) -> dict:
    """Devuelve un GeoJSON ``Polygon`` cerrado con lóbulos (frentes) estables por ``seed``.

    El contorno se alarga a favor de ``wind_to`` (grados, hacia dónde sopla), incorpora entre tres
    y cinco frentes gaussianos y varios armónicos de baja amplitud para que no parezca un óvalo.
    Cambiar ``radius_km`` escala la misma forma, así que el crecimiento no hace saltar los frentes.
    El radio medio del contorno coincide con ``radius_km``.
    """
    rng = random.Random(seed)
    fronts = [(rng.uniform(-2.3, 2.3), rng.uniform(.14, .32), rng.uniform(.45, 1.1)) for _ in range(rng.randint(3, 5))]
    fronts += [(rng.uniform(-math.pi, math.pi), rng.uniform(.05, .1), rng.uniform(.25, .55)) for _ in range(rng.randint(2, 4))]
    harmonics = [(k, rng.uniform(0, math.tau), amp) for k, amp in ((2, .1), (3, .12), (5, .09), (9, .05), (13, .03))]
    direction = math.radians(wind_to)
    east_km = 111.32 * max(.05, math.cos(math.radians(lat)))
    factors = []
    for n in range(points):
        theta = math.tau * n / points - math.pi  # 0 = a favor del viento
        downwind = (math.cos(theta) + 1) / 2
        factor = .5 + .9 * downwind ** 1.5
        for centre, width, strength in fronts:
            delta = (theta - centre + math.pi) % math.tau - math.pi
            factor += strength * math.exp(-(delta / width) ** 2) * (.5 + .5 * downwind)
        for order, phase, amp in harmonics:
            factor += amp * math.sin(order * theta + phase)
        factors.append(factor)
    mean = sum(factors) / len(factors)
    coordinates = []
    for n, factor in enumerate(factors):
        theta = math.tau * n / points - math.pi
        distance = min(MAX_RADIUS_FACTOR, max(MIN_RADIUS_FACTOR, factor / mean)) * radius_km
        along, across = math.cos(theta) * distance, math.sin(theta) * distance
        x = along * math.sin(direction) + across * math.cos(direction)
        y = along * math.cos(direction) - across * math.sin(direction)
        coordinates.append([lon + x / east_km, lat + y / 111.32])
    coordinates.append(list(coordinates[0]))
    return {'type': 'Polygon', 'coordinates': [coordinates]}
