import { test } from "node:test";
import assert from "node:assert/strict";
import { createStage, confirmedFire, fireTint, locatorSize } from "./static/flames.js";

test("los fuegos tienen un localizador legible al alejar, sin ampliar la huella", () => {
  assert.equal(locatorSize(.01), 32);
  assert.equal(locatorSize(100), 32);
  assert.equal(locatorSize(10000), 0);
});

test("ni FIRMS de alta confianza ni una noticia antigua confirman actividad actual", () => {
  const item = { documented: true, confidence: "high" };
  assert.equal(confirmedFire(item), false);
  assert.match(fireTint(item, 255, 120, 30), /^rgba\((\d+),\1,\1,/);
  const now = Date.now();
  item.confirmation = { status: "confirmed", source_name: "Fuente contrastada", source_url: "https://example.org/fire", confirmed_at: new Date(now - 1000).toISOString(), valid_until: new Date(now + 60000).toISOString() };
  assert.equal(confirmedFire(item, now), true);
  assert.equal(fireTint(item, 255, 120, 30), "rgba(255,120,30,1)");
  assert.equal(confirmedFire(item, now + 61000), false);
  item.confirmation.status = "withdrawn";
  assert.equal(confirmedFire(item, now), false);
});

const land = [[[-9, 36], [4, 36], [4, 44], [-9, 44], [-9, 36]]];
const incident = {
  id: "fixture", lat: 42, lon: -2, observations: 8,
  weather: { wind_from_degrees: 270 },
  footprint: { type: "Polygon", coordinates: [
    [[-2.01, 41.99], [-1.99, 41.99], [-1.99, 42.01], [-2.01, 42.01], [-2.01, 41.99]],
  ] },
};

function fixture(t, reduced = false) {
  let frameId = 0, path = [];
  const frames = new Map(), mapEvents = new Map(), documentEvents = new Map(), motionEvents = new Map();
  const strokes = [], fills = [];
  const ctx = {
    strokeStyle: "", fillStyle: "", globalAlpha: 1,
    setTransform() {}, clearRect() { strokes.length = 0; fills.length = 0; },
    beginPath() { path = []; }, moveTo(x, y) { path.push([x, y]); },
    lineTo(x, y) { path.push([x, y]); },
    quadraticCurveTo(x1, y1, x, y) { path.push([x, y]); },
    arc(x, y, radius) { assert.ok(Number.isFinite(x + y + radius)); },
    closePath() {}, fill() { fills.push(path.slice()); }, clip() {}, save() {}, restore() {},
    stroke() { strokes.push({ color: this.strokeStyle, points: path.slice() }); },
    createRadialGradient() { return { addColorStop() {} }; },
    createLinearGradient() { return { addColorStop() {} }; },
  };
  const canvas = { width: 0, height: 0, style: {}, getContext: () => ctx };
  const map = {
    zoom: 11, pan: { x: 0, y: 0 },
    getZoom() { return this.zoom; }, getCenter() { return { lat: 42 }; },
    getSize() { return { x: 800, y: 600 }; },
    getBounds() { return { getWest: () => -2.1, getEast: () => -1.9, getSouth: () => 41.9, getNorth: () => 42.1 }; },
    project([lat, lon], zoom) { const scale = 256 * 2 ** zoom / 360; return { x: lon * scale, y: -lat * scale }; },
    getPixelOrigin() { const p = this.project([42, -2], this.zoom); return { x: p.x - 400, y: p.y - 300 }; },
    containerPointToLayerPoint() { return { x: -this.pan.x, y: -this.pan.y }; },
    on(names, callback) { for (const name of names.split(" ")) mapEvents.set(name, callback); },
  };
  const motion = { matches: reduced, addEventListener(name, callback) { motionEvents.set(name, callback); } };
  const doc = { hidden: false, addEventListener(name, callback) { documentEvents.set(name, callback); } };
  const globals = {
    window: { devicePixelRatio: 3 }, document: doc, matchMedia: () => motion,
    requestAnimationFrame: callback => { frames.set(++frameId, callback); return frameId; },
    cancelAnimationFrame: id => frames.delete(id),
  };
  for (const [key, value] of Object.entries(globals)) {
    const descriptor = Object.getOwnPropertyDescriptor(globalThis, key);
    Object.defineProperty(globalThis, key, { value, configurable: true, writable: true });
    t.after(() => {
      if (descriptor) Object.defineProperty(globalThis, key, descriptor);
      else Reflect.deleteProperty(globalThis, key);
    });
  }
  const stage = createStage({
    map, canvas, random: () => .5,
    sampleWind: () => ({ u: 5, v: 0, speed: 18, from: 270 }),
  });
  stage.update([incident], incident.id); stage.start(land);
  const tick = time => {
    assert.ok(frames.size > 0, "hay un dibujo solicitado");
    const callbacks = [...frames.values()]; frames.clear();
    for (const callback of callbacks) callback(time);
  };
  const wind = () => strokes.find(s => s.color === "#93a6b6")?.points;
  return { stage, map, canvas, frames, tick, wind, fills, strokes, mapEvents, motionEvents, documentEvents, doc, motion };
}

test("el canvas usa DPR acotado y dibuja viento inmediatamente, incluso con movimiento reducido", t => {
  const f = fixture(t, true);
  f.tick(100);
  assert.equal(f.canvas.width, 1600);
  assert.equal(f.canvas.height, 1200);
  assert.ok(f.wind()?.length >= 2);
  assert.ok(f.fills.length > 0);
  assert.equal(f.frames.size, 0, "no consume fotogramas en reposo");
});

test("al arrastrar se reproyectan cabeza y cola juntas, sin estelas en la posición anterior", t => {
  const f = fixture(t, true);
  f.tick(100);
  const before = f.wind().map(p => p.slice());
  f.map.pan = { x: 120, y: -45 };
  f.mapEvents.get("move")(); f.tick(116);
  const after = f.wind();
  before.forEach(([x, y], i) => {
    assert.ok(Math.abs(after[i][0] - x - 120) < 1e-6);
    assert.ok(Math.abs(after[i][1] - y + 45) < 1e-6);
  });
});

test("un salto de zoom mantiene la longitud visual del viento y no espera a moveend", t => {
  const f = fixture(t, true);
  f.tick(100);
  const length = points => Math.hypot(points[0][0] - points[1][0], points[0][1] - points[1][1]);
  const before = length(f.wind());
  f.map.zoom = 13;
  f.mapEvents.get("zoom")(); f.tick(116);
  assert.ok(Math.abs(length(f.wind()) - before) < .01);
  assert.equal(f.frames.size, 0);
});

test("la huella del incendio queda anclada al terreno y no se deforma al hacer zoom", t => {
  const f = fixture(t, true);
  const outline = () => {
    const scale = 256 * 2 ** f.map.zoom / 360;
    const path = f.fills.reduce((largest, points) => (points.length > largest.length ? points : largest), []);
    const lons = path.map(([x]) => -2 + (x - 400) / scale);
    const lats = path.map(([, y]) => 42 - (y - 300) / scale);
    return { west: Math.min(...lons), east: Math.max(...lons), south: Math.min(...lats), north: Math.max(...lats) };
  };
  f.tick(100);
  const before = outline();
  assert.ok(before.east - before.west > .019 && before.east - before.west < .05, "la huella dibujada parte de la geometría real");
  f.map.zoom = 14;
  f.mapEvents.get("zoom")(); f.tick(116);
  const after = outline();
  for (const edge of ["west", "east", "south", "north"]) {
    assert.ok(Math.abs(after[edge] - before[edge]) < .002, `${edge} se mantiene al hacer zoom`);
  }
});

test("pausa, pestaña oculta, cambio de preferencia y reanudación controlan el bucle", t => {
  const f = fixture(t);
  f.tick(100); assert.equal(f.frames.size, 1);
  f.stage.setPaused(true); f.tick(116); assert.equal(f.frames.size, 0);
  f.stage.setPaused(false); f.tick(200); assert.equal(f.frames.size, 1);
  f.doc.hidden = true; f.documentEvents.get("visibilitychange")(); assert.equal(f.frames.size, 0);
  f.doc.hidden = false; f.documentEvents.get("visibilitychange")(); f.tick(2000);
  f.motion.matches = true; f.motionEvents.get("change")(); f.tick(2016);
  assert.equal(f.frames.size, 0);
  f.motion.matches = false; f.motionEvents.get("change")(); f.tick(2100);
  assert.equal(f.frames.size, 1);
  f.stage.stop(); assert.equal(f.frames.size, 0);
});

test("los filtros y el interruptor del viento retiran sus capas", t => {
  const f = fixture(t, true);
  f.tick(100);
  assert.ok(f.wind());
  f.stage.setWind(false); f.stage.update([], null); f.tick(116);
  assert.equal(f.wind(), undefined);
  assert.equal(f.fills.length, 0);
});
