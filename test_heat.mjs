import { test } from "node:test";
import assert from "node:assert/strict";
import {
  colorize, createHeatLayer, heatPalette, heatRadiusPixels, hoverSummary, nearestSample, sampleAlpha,
} from "./static/heat.js";

test("la paleta es un degradado continuo y creciente, transparente en el origen", () => {
  const palette = heatPalette();
  assert.equal(palette.length, 1024);
  assert.equal(palette[3], 0);
  let previous = -1;
  for (let i = 0; i < 256; i++) {
    const alpha = palette[i * 4 + 3];
    assert.ok(alpha >= previous, "la opacidad nunca retrocede");
    previous = alpha;
  }
  const hot = palette[255 * 4] - palette[255 * 4 + 2], cold = palette[0] - palette[2];
  assert.ok(hot > cold, "el extremo denso es más cálido que el origen");
  assert.ok(palette[255 * 4 + 1] < palette[1], "y pierde verde al intensificarse");
});

test("la densidad se traduce a color y el ruido de fondo no se pinta", () => {
  const palette = heatPalette();
  const pixels = new Uint8ClampedArray([0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 140, 0, 0, 0, 255]);
  colorize(pixels, palette, .8);
  assert.equal(pixels[3], 0);
  assert.equal(pixels[7], 0, "por debajo del umbral queda invisible");
  assert.ok(pixels[11] > 0 && pixels[11] < pixels[15], "más densidad, más presencia");
  assert.equal(pixels[15], Math.round(palette[255 * 4 + 3] * .8));
});

test("el radio sigue una distancia real acotada y la intensidad respeta la puntuación", () => {
  assert.ok(heatRadiusPixels(10) > heatRadiusPixels(60), "al acercar, el radio crece");
  assert.equal(heatRadiusPixels(30), 450 / 30);
  assert.equal(heatRadiusPixels(1), 75);
  assert.equal(heatRadiusPixels(1000000), 10);
  assert.equal(heatRadiusPixels(0), 10);
  assert.equal(sampleAlpha(null), 0);
  assert.equal(sampleAlpha(0), 0);
  assert.ok(sampleAlpha(100) > sampleAlpha(40));
  assert.ok(sampleAlpha(100) <= .55);
});

test("el rótulo dice qué hay, sin inventar viento ni datos ausentes", () => {
  const facilities = [
    { id: "way:1", name: "Gasolinera Río", category_label: "Gasolinera" },
    { id: "way:2", name: "", category_label: "Área industrial" },
    { id: "way:3", name: "Tercera", category_label: "Fábrica" },
  ];
  const sample = {
    id: "cell:1", distance_km: 1.24, downwind: true,
    evidence: { population: 1200, vegetation_pct: 62.4, facility_ids: ["way:1", "way:2", "way:3"] },
  };
  const text = hoverSummary(sample, facilities, { status: "current" });
  assert.match(text, /Gasolinera Río/);
  assert.match(text, /Área industrial/);
  assert.match(text, /\+1 instalaciones/);
  assert.match(text, /1200 residentes/, "el español no separa los millares de cuatro cifras");
  assert.match(hoverSummary({ ...sample, evidence: { ...sample.evidence, population: 24509 } }, facilities, {}), /24\.509 residentes/);
  assert.match(text, /62 % vegetación/);
  assert.match(text, /a favor del viento/);
  assert.match(text, /a 1,2 km/);
  const stale = hoverSummary(sample, facilities, { status: "stale" });
  assert.ok(!stale.includes("a favor del viento"));
  const empty = hoverSummary({ id: "x", distance_km: 0.05, evidence: { facility_ids: [] } }, facilities, {});
  assert.match(empty, /Sin elementos registrados · en la huella/);
  assert.equal(hoverSummary(null), null);
  const unknown = hoverSummary({ id: "y", evidence: { population: null, vegetation_pct: null, facility_ids: ["way:9"] } }, facilities, {});
  assert.equal(unknown, "Sin elementos registrados");
});

test("el punto más cercano se limita a un radio y no adivina fuera de él", () => {
  const samples = [{ id: "a", lat: 40, lon: -3 }, { id: "b", lat: 41, lon: -3 }];
  const project = (lat, lon) => ({ x: lon * 10, y: lat * 10 });
  assert.equal(nearestSample(samples, project, -30, 408, 20).id, "b");
  assert.equal(nearestSample(samples, project, -30, 395, 20).id, "a");
  assert.equal(nearestSample(samples, project, -30, 500, 20), null);
  assert.equal(nearestSample([], project, 0, 0, 50), null);
});

function fixture() {
  const events = new Map(), gradients = [], reads = [];
  let frame = 0, hovered;
  const canvas = { width: 0, height: 0, style: {}, getContext: () => ctx };
  const ctx = {
    setTransform() {}, clearRect() { gradients.length = 0; }, beginPath() {}, arc() {}, fill() {},
    createRadialGradient(x0, y0, r0, x1, y1, radius) {
      const stops = [];
      gradients.push({ x: x1, y: y1, radius, stops });
      return { addColorStop: (offset, color) => stops.push([offset, color]) };
    },
    getImageData(x, y, width, height) {
      reads.push({ width, height });
      return { data: new Uint8ClampedArray(width * height * 4) };
    },
    putImageData() {},
  };
  const map = {
    zoom: 12,
    getZoom() { return this.zoom; }, getCenter() { return { lat: 40 }; }, getSize() { return { x: 800, y: 600 }; },
    getPixelOrigin() { const p = this.project([40, -3], this.zoom); return { x: p.x - 400, y: p.y - 300 }; },
    containerPointToLayerPoint() { return { x: 0, y: 0 }; },
    project([lat, lon], zoom) { const scale = 256 * 2 ** zoom / 360; return { x: (lon + 180) * scale, y: (90 - lat) * scale }; },
    on(names, handler) { for (const name of names.split(" ")) events.set(name, handler); },
  };
  const original = globalThis.requestAnimationFrame;
  globalThis.requestAnimationFrame = callback => { frame = callback; return 1; };
  const layer = createHeatLayer({ map, canvas, document: null, onHover: value => { hovered = value; }, resolution: .5 });
  return {
    layer, map, canvas, gradients, reads, events,
    flush() { const callback = frame; frame = 0; if (callback) callback(); },
    get hovered() { return hovered; },
    restore() { globalThis.requestAnimationFrame = original; },
  };
}

test("el calor se dibuja como degradados continuos y se recolorea una sola vez por fotograma", t => {
  const f = fixture(); t.after(f.restore);
  f.layer.set([
    { id: "a", lat: 40, lon: -3, score: 80, evidence: { population: 500, facility_ids: [] } },
    { id: "b", lat: 40, lon: -3.001, score: 20, evidence: { facility_ids: [] } },
    { id: "c", lat: 40, lon: -3, score: null, evidence: { facility_ids: [] } },
    { id: "d", lat: 40, lon: 40, score: 90, evidence: { facility_ids: [] } },
  ], { wind: { status: "current" }, potential: { facilities: [] } });
  f.flush();
  assert.equal(f.canvas.width, 400);
  assert.equal(f.canvas.height, 300);
  assert.equal(f.gradients.length, 2, "sin puntuación no se pinta; fuera de la vista tampoco");
  assert.equal(f.reads.length, 1);
  assert.deepEqual(f.reads[0], { width: 400, height: 300 });
  const [strong, weak] = f.gradients;
  assert.ok(strong.stops[0][1] !== weak.stops[0][1], "la intensidad depende de la puntuación");
  assert.match(strong.stops.at(-1)[1], /rgba\(0,0,0,0\)/);
  assert.ok(strong.radius > 0 && strong.radius < 200);
  assert.ok(Math.abs(strong.x - 200) < 1e-6 && Math.abs(strong.y - 150) < 1e-6, "se proyecta en la escala del canvas");
});

test("acercarse amplía el radio del calor sin pedir otro recoloreado por evento", t => {
  const f = fixture(); t.after(f.restore);
  f.layer.set([{ id: "a", lat: 40, lon: -3, score: 70, evidence: { facility_ids: [] } }], { wind: {}, potential: {} });
  f.flush();
  const before = f.gradients[0].radius;
  f.map.zoom = 14;
  f.events.get("zoom")(); f.events.get("move")();
  f.flush();
  assert.ok(f.gradients[0].radius > before, "al acercar cubre más pantalla");
  assert.equal(f.reads.length, 2, "un recoloreado por fotograma, no por evento");
});

test("al pasar el ratón informa del punto y se oculta al salir, arrastrar o vaciar", t => {
  const f = fixture(); t.after(f.restore);
  const sample = { id: "a", lat: 40, lon: -3, score: 70, distance_km: .4, evidence: { population: 90, facility_ids: [] } };
  f.layer.set([sample], { wind: { status: "current" }, potential: { facilities: [] } });
  f.flush();
  const point = { x: 400, y: 300 };
  f.events.get("mousemove")({ containerPoint: { x: point.x, y: point.y } });
  assert.equal(f.hovered.id, "a");
  assert.match(f.hovered.text, /90 residentes/);
  f.events.get("mousemove")({ containerPoint: { x: point.x + 4000, y: point.y } });
  assert.equal(f.hovered, null);
  f.events.get("mousemove")({ containerPoint: { x: point.x, y: point.y } });
  assert.equal(f.hovered.id, "a");
  f.events.get("dragstart")();
  assert.equal(f.hovered, null);
  f.layer.clear(); f.flush();
  assert.equal(f.gradients.length, 0);
  f.events.get("mousemove")({ containerPoint: { x: point.x, y: point.y } });
  assert.equal(f.hovered, null);
});
