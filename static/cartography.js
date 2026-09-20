// Cartografía base (países vecinos, España y provincias) dibujada en un solo canvas.
//
// Antes se añadían como capas GeoJSON de Leaflet (SVG): cada fotograma de zoom continuo
// reproyectaba y recortaba ~111.000 vértices en JavaScript, más de la mitad del tiempo de
// CPU durante un zoom. Aquí las geometrías se proyectan UNA vez a coordenadas de mundo
// (zoom 0, relativas a un origen para conservar precisión en float32) y se guardan como
// Path2D; cada fotograma solo aplica una transformación afín y rellena/traza los trazados.
// Se preparan varios niveles de detalle (Douglas-Peucker) y en escala local solo se dibujan
// las entidades cuya caja intersecta la vista. Nunca modifica los GeoJSON originales.

export const LEVELS = [
  // [tolerancia en px de mundo a zoom 0, zoom máximo que la usa]
  { tolerance: .006, maxZoom: 7 },
  { tolerance: .0008, maxZoom: 10 },
  { tolerance: 0, maxZoom: Infinity },
];

export function detailLevel(zoom, levels = LEVELS) {
  return Math.max(0, levels.findIndex(level => zoom <= level.maxZoom));
}

// Douglas-Peucker iterativo sobre puntos {x, y}; conserva extremos y nunca deja menos de 4 puntos.
export function simplify(points, tolerance) {
  if (!(tolerance > 0) || points.length <= 4) return points;
  const keep = new Uint8Array(points.length);
  keep[0] = keep[points.length - 1] = 1;
  const stack = [[0, points.length - 1]];
  const limit = tolerance * tolerance;
  while (stack.length) {
    const [first, last] = stack.pop();
    if (last - first < 2) continue;
    const a = points[first], b = points[last];
    const dx = b.x - a.x, dy = b.y - a.y, length = dx * dx + dy * dy;
    let index = -1, worst = limit;
    for (let i = first + 1; i < last; i++) {
      const p = points[i];
      let distance;
      if (length === 0) distance = (p.x - a.x) ** 2 + (p.y - a.y) ** 2;
      else {
        const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / length));
        distance = (p.x - a.x - t * dx) ** 2 + (p.y - a.y - t * dy) ** 2;
      }
      if (distance > worst) { worst = distance; index = i; }
    }
    if (index > 0) { keep[index] = 1; stack.push([first, index], [index, last]); }
  }
  const result = [];
  for (let i = 0; i < points.length; i++) if (keep[i]) result.push(points[i]);
  return result.length < 4 ? points : result;
}

export function projectRings(geometry, project) {
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.type === "MultiPolygon" ? geometry.coordinates : [];
  return polygons.map(polygon => polygon.map(ring => ring.map(([lon, lat]) => project(lat, lon))));
}

export function boundsOf(polygons) {
  const box = { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity };
  for (const polygon of polygons) for (const ring of polygon) for (const p of ring) {
    if (p.x < box.left) box.left = p.x; if (p.x > box.right) box.right = p.x;
    if (p.y < box.top) box.top = p.y; if (p.y > box.bottom) box.bottom = p.y;
  }
  return box;
}

export function intersects(a, b) {
  return a.left <= b.right && a.right >= b.left && a.top <= b.bottom && a.bottom >= b.top;
}

// Anillos cuya caja no llega a dos veces la tolerancia son motas subpíxel a esa escala
// (islotes, rocas): se omiten en ese nivel. España tiene ~4.900 anillos así.
export function visibleRing(ring, tolerance) {
  if (!(tolerance > 0)) return true;
  const box = boundsOf([[ring]]);
  return box.right - box.left >= tolerance * 2 || box.bottom - box.top >= tolerance * 2;
}

function toPath(polygons, tolerance, Path2D) {
  const path = new Path2D();
  for (const polygon of polygons) for (const ring of polygon) {
    if (ring.length < 3 || !visibleRing(ring, tolerance)) continue;
    const points = simplify(ring, tolerance);
    path.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) path.lineTo(points[i].x, points[i].y);
    path.closePath();
  }
  return path;
}

// Prepara una colección: por entidad, caja y un Path2D por nivel de detalle.
export function buildLayer(features, project, { Path2D = globalThis.Path2D, levels = LEVELS } = {}) {
  const items = [];
  let vertices = 0;
  for (const feature of features) {
    const polygons = projectRings(feature.geometry, project);
    if (!polygons.length) continue;
    vertices += polygons.reduce((sum, polygon) => sum + polygon.reduce((s, ring) => s + ring.length, 0), 0);
    items.push({ bounds: boundsOf(polygons), paths: levels.map(level => toPath(polygons, level.tolerance, Path2D)) });
  }
  return { items, bounds: boundsOf(items.map(item => [[{ x: item.bounds.left, y: item.bounds.top }, { x: item.bounds.right, y: item.bounds.bottom }]])), vertices };
}

export const STYLES = {
  neighbors: { fill: "#f2f4f7", stroke: "#e5e9ee", weight: .8 },
  country: { fill: "#ffffff", stroke: "#cfd6df", weight: 1 },
  provinces: { fill: null, stroke: "#e7ebf0", weight: .6 },
};

export function createCartography({ map, canvas, L, window: view = globalThis, Path2D = globalThis.Path2D }) {
  const ctx = canvas.getContext("2d");
  const origin = L.latLng(40, -3);
  const anchor = map.project(origin, 0);
  const project = (lat, lon) => { const p = map.project(L.latLng(lat, lon), 0); return { x: p.x - anchor.x, y: p.y - anchor.y }; };
  const layers = new Map();
  const order = ["neighbors", "country", "provinces"];
  let frame = 0;

  function paint() {
    frame = 0;
    if (!Number.isFinite(map.getZoom())) return;
    const size = map.getSize(), ratio = Math.min(2, view.devicePixelRatio || 1);
    const offset = map.containerPointToLayerPoint([0, 0]);
    canvas.style.transform = `translate(${offset.x}px, ${offset.y}px)`;
    if (canvas.width !== Math.round(size.x * ratio) || canvas.height !== Math.round(size.y * ratio)) {
      canvas.width = Math.round(size.x * ratio); canvas.height = Math.round(size.y * ratio);
      canvas.style.width = `${size.x}px`; canvas.style.height = `${size.y}px`;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const zoom = map.getZoom(), scale = map.getZoomScale(zoom, 0), base = map.latLngToContainerPoint(origin);
    // Vista en coordenadas de mundo relativas al origen, con margen para los trazos.
    const viewBox = { left: -base.x / scale - 2, top: -base.y / scale - 2, right: (size.x - base.x) / scale + 2, bottom: (size.y - base.y) / scale + 2 };
    const level = detailLevel(zoom);
    ctx.setTransform(ratio * scale, 0, 0, ratio * scale, ratio * base.x, ratio * base.y);
    ctx.lineJoin = "round";
    for (const name of order) {
      const layer = layers.get(name);
      if (!layer || !intersects(layer.bounds, viewBox)) continue;
      const style = STYLES[name];
      ctx.lineWidth = style.weight / scale;
      for (const item of layer.items) {
        if (!intersects(item.bounds, viewBox)) continue;
        const path = item.paths[Math.min(level, item.paths.length - 1)];
        if (style.fill) { ctx.fillStyle = style.fill; ctx.fill(path); }
        if (style.stroke) { ctx.strokeStyle = style.stroke; ctx.stroke(path); }
      }
    }
  }
  function schedule() { if (!frame) frame = view.requestAnimationFrame(paint); }
  map.on("move zoom resize viewreset", schedule);
  return {
    set(name, geojson) {
      const features = geojson.type === "FeatureCollection" ? geojson.features : [geojson];
      layers.set(name, buildLayer(features, project, { Path2D }));
      schedule();
    },
    paint, schedule,
    has: name => layers.has(name),
  };
}
