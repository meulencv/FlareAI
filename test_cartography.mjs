import { test } from "node:test";
import assert from "node:assert/strict";
import { LEVELS, boundsOf, buildLayer, createCartography, detailLevel, intersects, projectRings, simplify, visibleRing } from "./static/cartography.js";

class FakePath2D {
  constructor() { this.ops = []; this.vertices = 0; }
  moveTo(x, y) { this.ops.push(["M", x, y]); this.vertices++; }
  lineTo(x, y) { this.ops.push(["L", x, y]); this.vertices++; }
  closePath() { this.ops.push(["Z"]); }
}

const mercator = (lat, lon) => ({ x: (lon + 180) / 360 * 256, y: (1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * 256 });

test("Douglas-Peucker conserva extremos, elimina puntos casi colineales y respeta la tolerancia", () => {
  const points = Array.from({ length: 101 }, (_, i) => ({ x: i * .001, y: Math.sin(i / 10) * .0005 }));
  assert.equal(simplify(points, 0), points, "sin tolerancia no se toca la geometría");
  const coarse = simplify(points, .0001);
  assert.ok(coarse.length < 20 && coarse.length >= 4);
  assert.deepEqual([coarse[0], coarse.at(-1)], [points[0], points.at(-1)]);
  const flat = Array.from({ length: 50 }, (_, i) => ({ x: i, y: 0 }));
  assert.equal(simplify(flat, .1), flat, "un anillo que se reduciría a menos de cuatro puntos conserva el original");
  assert.equal(simplify([{ x: 0, y: 0 }, { x: 1, y: 1 }, { x: 0, y: 0 }], 5).length, 3);
});

test("los niveles de detalle se eligen por zoom y las motas subpíxel se omiten", () => {
  assert.equal(detailLevel(4), 0); assert.equal(detailLevel(7), 0);
  assert.equal(detailLevel(7.1), 1); assert.equal(detailLevel(10), 1);
  assert.equal(detailLevel(14), 2); assert.equal(detailLevel(16), 2);
  assert.equal(LEVELS.at(-1).tolerance, 0, "la escala local usa la geometría completa");
  const speck = [{ x: 0, y: 0 }, { x: .001, y: 0 }, { x: .001, y: .001 }, { x: 0, y: 0 }];
  assert.equal(visibleRing(speck, .006), false);
  assert.equal(visibleRing(speck, 0), true, "sin simplificación se dibuja todo");
  assert.equal(visibleRing([{ x: 0, y: 0 }, { x: .05, y: 0 }, { x: .05, y: .001 }, { x: 0, y: 0 }], .006), true);
});

test("buildLayer proyecta una vez, calcula cajas y crea un Path2D por nivel", () => {
  const square = (lon, lat, size) => [[lon, lat], [lon + size, lat], [lon + size, lat + size], [lon, lat + size], [lon, lat]];
  const features = [
    { geometry: { type: "Polygon", coordinates: [square(-3, 40, 1)] } },
    { geometry: { type: "MultiPolygon", coordinates: [[square(2, 41, .5)], [square(2.9, 41.9, .0005)]] } },
    { geometry: { type: "Point", coordinates: [0, 0] } },
  ];
  const layer = buildLayer(features, mercator, { Path2D: FakePath2D });
  assert.equal(layer.items.length, 2, "solo se dibujan polígonos");
  assert.equal(layer.vertices, 15);
  assert.equal(layer.items[0].paths.length, LEVELS.length);
  assert.ok(layer.items[0].bounds.left < layer.items[0].bounds.right && layer.items[0].bounds.top < layer.items[0].bounds.bottom);
  assert.ok(intersects(layer.bounds, layer.items[1].bounds));
  assert.equal(layer.items[1].paths[0].ops.filter(op => op[0] === "M").length, 1, "el islote subpíxel desaparece en el nivel grueso");
  assert.equal(layer.items[1].paths[2].ops.filter(op => op[0] === "M").length, 2, "y se conserva a escala local");
  const rings = projectRings(features[1].geometry, mercator);
  assert.equal(rings.length, 2);
  assert.deepEqual(boundsOf([[[{ x: 1, y: 2 }, { x: -1, y: 5 }]]]), { left: -1, top: 2, right: 1, bottom: 5 });
  assert.equal(intersects({ left: 0, top: 0, right: 1, bottom: 1 }, { left: 2, top: 0, right: 3, bottom: 1 }), false);
});

test("la capa pinta con una transformación afín por fotograma y omite lo que queda fuera de la vista", () => {
  const calls = [];
  const ctx = {
    lineWidth: 0, fillStyle: "", strokeStyle: "", lineJoin: "",
    setTransform(...args) { calls.push(["transform", ...args]); },
    clearRect() { calls.push(["clear"]); },
    fill(path) { calls.push(["fill", path]); },
    stroke(path) { calls.push(["stroke", path]); },
  };
  const canvas = { width: 0, height: 0, style: {}, getContext: () => ctx };
  const listeners = {};
  let zoom = 6, center = { lat: 40, lon: -3 };
  const map = {
    on: (names, fn) => names.split(" ").forEach(name => { listeners[name] = fn; }),
    getZoom: () => zoom, getSize: () => ({ x: 1000, y: 800 }), getZoomScale: (to, from) => 2 ** (to - from),
    containerPointToLayerPoint: () => ({ x: 0, y: 0 }),
    project: (latlng, z) => { const p = mercator(latlng.lat, latlng.lng); return { x: p.x * 2 ** z, y: p.y * 2 ** z }; },
    latLngToContainerPoint(latlng) {
      const p = this.project(latlng, zoom), c = this.project({ lat: center.lat, lng: center.lon }, zoom);
      return { x: 500 + p.x - c.x, y: 400 + p.y - c.y };
    },
  };
  const L = { latLng: (lat, lng) => ({ lat, lng }) };
  const pending = [];
  const view = { devicePixelRatio: 2, requestAnimationFrame: fn => pending.push(fn) };
  const flush = () => { const batch = pending.splice(0); batch.forEach(fn => fn()); return batch.length; };
  const layer = createCartography({ map, canvas, L, window: view, Path2D: FakePath2D });
  const square = (lon, lat, size) => [[lon, lat], [lon + size, lat], [lon + size, lat + size], [lon, lat + size], [lon, lat]];
  layer.set("country", { type: "Feature", geometry: { type: "Polygon", coordinates: [square(-4, 39, 2)] } });
  layer.set("provinces", { type: "FeatureCollection", features: [
    { geometry: { type: "Polygon", coordinates: [square(-4, 39, 1)] } },
    { geometry: { type: "Polygon", coordinates: [square(60, 10, 1)] } },
  ] });
  assert.equal(flush(), 1, "dos capas cargadas seguidas solo programan una pintura");
  assert.equal(canvas.width, 2000, "canvas a la densidad de píxeles del dispositivo");
  const fills = calls.filter(c => c[0] === "fill"), strokes = calls.filter(c => c[0] === "stroke");
  assert.equal(fills.length, 1, "España se rellena; las provincias solo se trazan");
  assert.equal(strokes.length, 2, "la provincia fuera de la vista no se dibuja");
  const transform = calls.filter(c => c[0] === "transform").at(-1);
  assert.equal(transform[1], 2 * 2 ** 6, "escala = ratio × 2^zoom");
  assert.ok(Math.abs(ctx.lineWidth - .6 / 2 ** 6) < 1e-9, "el grosor se compensa con la escala");
  calls.length = 0;
  listeners.zoom(); listeners.move();
  assert.equal(flush(), 1, "varios eventos en el mismo fotograma solo programan una pintura");
  zoom = 12; center = { lat: 39.5, lon: -3.5 };
  calls.length = 0;
  listeners.zoom(); flush();
  const local = calls.filter(c => c[0] === "stroke");
  assert.equal(local.length, 2);
  assert.ok(layer.has("provinces"));
  assert.equal(local[1][1].vertices, 5, "a escala local se usa la geometría completa");
  zoom = NaN;
  calls.length = 0;
  listeners.zoom(); flush();
  assert.equal(calls.length, 0, "sin zoom inicial no se pinta nada");
});
