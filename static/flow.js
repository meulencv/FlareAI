const RADIANS = Math.PI / 180;

export function metersPerDegree(lat) {
  return { east: 111320 * Math.cos(lat * RADIANS), north: 111320 };
}

export function visualSpeed(kmh, base = 10, gain = .85, cap = 70) {
  if (!Number.isFinite(kmh)) return base;
  return base + Math.min(Math.max(kmh, 0), cap) * gain;
}

export function flicker(seed, time, rate = 1) {
  const t = time * rate;
  return (Math.sin(t * 2.3 + seed) + Math.sin(t * 3.7 + seed * 1.7) * .6 + Math.sin(t * 6.1 + seed * .5) * .3) / 1.9;
}

export function budget(width, height, area = 13000, cap = 520) {
  return Math.max(0, Math.min(cap, Math.round(width * height / area)));
}

export function inside(point, bounds, margin = 0) {
  return point.lon >= bounds.west - margin && point.lon <= bounds.east + margin
    && point.lat >= bounds.south - margin && point.lat <= bounds.north + margin;
}

export function pointInPolygon(rings, lon, lat) {
  let contained = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > lat) !== (yj > lat) && lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) contained = !contained;
    }
  }
  return contained;
}

export function indexRings(shapes, cell = 2) {
  const bins = new Map();
  for (const ring of shapes) {
    const bounds = ring.reduce((b, [lon, lat]) => ({
      west: Math.min(b.west, lon), east: Math.max(b.east, lon),
      south: Math.min(b.south, lat), north: Math.max(b.north, lat),
    }), { west: Infinity, east: -Infinity, south: Infinity, north: -Infinity });
    for (let x = Math.floor(bounds.west / cell); x <= Math.floor(bounds.east / cell); x++) {
      for (let y = Math.floor(bounds.south / cell); y <= Math.floor(bounds.north / cell); y++) {
        const key = `${x},${y}`;
        if (!bins.has(key)) bins.set(key, []);
        bins.get(key).push({ ring, bounds });
      }
    }
  }
  return (lon, lat) => {
    const candidates = bins.get(`${Math.floor(lon / cell)},${Math.floor(lat / cell)}`) || [];
    return pointInPolygon(candidates.filter(entry => inside({ lon, lat }, entry.bounds)).map(entry => entry.ring), lon, lat);
  };
}

export function rings(geometry) {
  if (!geometry) return [];
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
  return polygons.flat();
}

export function displace(point, bearingDegrees, meters) {
  const angle = bearingDegrees * RADIANS, scale = metersPerDegree(point.lat);
  return {
    lon: point.lon + Math.sin(angle) * meters / scale.east,
    lat: point.lat + Math.cos(angle) * meters / scale.north,
  };
}

export function stepParticle(particle, wind, seconds, metersPerPixel, options = {}) {
  const next = { ...particle, age: particle.age + seconds };
  if (!wind || wind.from === null) return next;
  const speed = Math.hypot(wind.u, wind.v);
  if (!(speed > 0)) return next;
  const { base, gain, drift = 0 } = options;
  const meters = visualSpeed(wind.speed, base, gain) * seconds * metersPerPixel;
  const scale = metersPerDegree(particle.lat);
  const sway = drift ? Math.sin(next.age * 2.6 + (particle.seed || 0)) * drift * seconds * metersPerPixel : 0;
  return {
    ...next,
    lon: particle.lon + (wind.u * meters + -wind.v * sway) / speed / scale.east,
    lat: particle.lat + (wind.v * meters + wind.u * sway) / speed / scale.north,
    speed: wind.speed,
    bearing: (Math.atan2(wind.u, wind.v) / RADIANS + 360) % 360,
  };
}

export function expired(particle, bounds, margin = .35) {
  return particle.age >= particle.life || !inside(particle, bounds, margin);
}

export function spawn(bounds, random, life, accepts = () => true, attempts = 12) {
  for (let i = 0; i < attempts; i++) {
    const lon = bounds.west + random() * (bounds.east - bounds.west);
    const lat = bounds.south + random() * (bounds.north - bounds.south);
    if (!accepts(lon, lat)) continue;
    return { lon, lat, age: random() * life * .8, life, seed: random() * 6.28, speed: 0, bearing: 0, trail: [] };
  }
  return null;
}

export function emberBudget(observations, selected, zoom) {
  const detail = Math.max(0, Math.min(1, (zoom - 5.5) / 5.5));
  return Math.round((selected ? 13 : 4) * (.45 + detail) * Math.min(3.2, Math.sqrt(observations)));
}

export function heatRadius(pixelArea, observations) {
  return Math.max(9, Math.min(150, Math.sqrt(Math.max(pixelArea, 1) / Math.PI) * 1.25 + Math.sqrt(observations) * 2.4));
}

export function detailedOutline(points, spacing = 7, cap = 180) {
  const lengths = points.map((p, i) => {
    const next = points[(i + 1) % points.length];
    return Math.hypot(next.x - p.x, next.y - p.y);
  });
  const perimeter = lengths.reduce((sum, length) => sum + length, 0);
  const count = Math.min(cap, Math.max(12, Math.ceil(perimeter / spacing)));
  if (!perimeter) return points;
  const result = [];
  let edge = 0, offset = 0;
  for (let i = 0; i < count; i++) {
    const distance = i / count * perimeter;
    while (edge < lengths.length - 1 && offset + lengths[edge] < distance) offset += lengths[edge++];
    const fraction = lengths[edge] ? (distance - offset) / lengths[edge] : 0;
    const p = points[edge], next = points[(edge + 1) % points.length];
    result.push({ x: p.x + (next.x - p.x) * fraction, y: p.y + (next.y - p.y) * fraction });
  }
  return result;
}

export function windStroke(particle, wind, metersPerPixel, pixels = 20) {
  if (!wind || wind.from === null || !Math.hypot(wind.u, wind.v)) return [];
  const tail = displace(particle, Math.atan2(-wind.u, -wind.v) / RADIANS, pixels * metersPerPixel);
  return [tail, { lon: particle.lon, lat: particle.lat }];
}

export function polygonArea(points) {
  let total = 0;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    total += (points[j].x + points[i].x) * (points[j].y - points[i].y);
  }
  return Math.abs(total / 2);
}

export function flameOutline(points, time, bearing, amplitude) {
  const centre = points.reduce((acc, p) => ({ x: acc.x + p.x / points.length, y: acc.y + p.y / points.length }), { x: 0, y: 0 });
  const lean = bearing === null ? null : { x: Math.sin(bearing * RADIANS), y: -Math.cos(bearing * RADIANS) };
  return points.map((point, index) => {
    const dx = point.x - centre.x, dy = point.y - centre.y;
    const length = Math.hypot(dx, dy) || 1;
    const normal = { x: dx / length, y: dy / length };
    const downwind = lean ? Math.max(0, normal.x * lean.x + normal.y * lean.y) : .5;
    const pulse = (flicker(index / points.length * 11, time, 1.1) + 1) / 2;
    const push = amplitude * (.35 + pulse * .65) * (.55 + downwind * 1.15);
    return { x: point.x + normal.x * push, y: point.y + normal.y * push };
  });
}
