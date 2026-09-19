import { test } from "node:test";
import assert from "node:assert/strict";
import { createContextView, potentialLabel, selectionBounds } from "./static/context.js";

const footprint = { type: "Polygon", coordinates: [[[-3.001, 39.999], [-2.999, 39.999], [-2.999, 40.001], [-3.001, 40.001], [-3.001, 39.999]]] };
const incident = id => ({ id, lat: 40, lon: -3, footprint });
function context(id = "a") {
  return {
    incident_id: id, wind: { status: "current" },
    potential: {
      status: "available", facilities: [],
      samples: [{ id: "cell:1", lat: 40, lon: -3, score: 48, distance_km: .4, evidence: { population: 120, facility_ids: [] } }],
    },
  };
}

test("encuadre automático incluye la huella y cinco kilómetros, también multipolígonos", () => {
  const bounds = selectionBounds(incident("a"));
  assert.ok(bounds[0][0] < 39.96 && bounds[1][0] > 40.04);
  assert.ok(bounds[0][1] < -3.05 && bounds[1][1] > -2.95);
  const multi = { ...incident("a"), footprint: { type: "MultiPolygon", coordinates: [footprint.coordinates] } };
  assert.deepEqual(selectionBounds(multi), bounds);
});

test("la leyenda diferencia ausencia de datos, señal insuficiente y viento antiguo", () => {
  const data = context();
  assert.equal(potentialLabel(data), "Riesgo inmediato alrededor");
  data.wind.status = "historical"; assert.match(potentialLabel(data), /histórico/);
  data.wind.status = "calm"; assert.match(potentialLabel(data), /sin viento actual/);
  data.wind.status = "stale"; assert.match(potentialLabel(data), /sin viento actual/);
  data.potential.samples[0].score = null; assert.match(potentialLabel(data), /sin señal suficiente/);
  data.potential.status = "unavailable"; assert.match(potentialLabel(data), /sin cobertura/);
});

function harness(fetch) {
  const elements = new Map(), fits = [], painted = [], contexts = [];
  const document = { getElementById(id) {
    if (!elements.has(id)) {
      elements.set(id, { textContent: "", hidden: false, title: "", style: {},
        classList: { toggle() {}, remove() {}, add() {} } });
    }
    return elements.get(id);
  }, addEventListener() {} };
  let focuses = 0;
  const canvas = { width: 0, height: 0, style: {}, getContext: () => ({
    setTransform() {}, clearRect() { painted.length = 0; }, beginPath() {}, arc() {}, fill() {},
    createRadialGradient: (x0, y0, r0, x, y, radius) => { painted.push({ x, y, radius }); return { addColorStop() {} }; },
    getImageData: (x, y, width, height) => ({ data: new Uint8ClampedArray(width * height * 4) }),
    putImageData() {},
  }) };
  let frame = null;
  const original = globalThis.requestAnimationFrame;
  globalThis.requestAnimationFrame = callback => { frame = callback; return 1; };
  const map = {
    handlers: new Map(), zoom: 12,
    getZoom() { return this.zoom; }, getCenter() { return { lat: 40 }; }, getSize() { return { x: 800, y: 600 }; },
    getPixelOrigin() { const p = this.project([40, -3], this.zoom); return { x: p.x - 400, y: p.y - 300 }; },
    containerPointToLayerPoint() { return { x: 0, y: 0 }; },
    project([lat, lon], zoom) { const scale = 256 * 2 ** zoom / 360; return { x: (lon + 180) * scale, y: (90 - lat) * scale }; },
    on(names, handler) { for (const name of names.split(" ")) this.handlers.set(name, handler); },
    fitBounds(bounds) { fits.push(bounds); },
    attributionControl: { added: new Set(), addAttribution(text) { this.added.add(text); }, removeAttribution(text) { this.added.delete(text); } },
  };
  const view = createContextView({ map, document, fetch, canvas, onFocus: () => focuses++, onContext: value => contexts.push(value) });
  return {
    view, elements, fits, map, painted, contexts,
    flush() { const callback = frame; frame = null; if (callback) callback(); },
    hover(x, y) { map.handlers.get("mousemove")({ containerPoint: { x, y } }); },
    get focuses() { return focuses; },
    get attributions() { return map.attributionControl.added.size; },
    restore() { globalThis.requestAnimationFrame = original; },
  };
}

test("seleccionar pinta el calor y centra una vez; actualizar no mueve el mapa", async t => {
  const h = harness(async () => ({ ok: true, json: async () => context() })); t.after(h.restore);
  await h.view.load(incident("a"), { focus: true });
  h.flush();
  assert.equal(h.fits.length, 1); assert.equal(h.focuses, 1);
  assert.equal(h.painted.length, 1, "un degradado por muestra con puntuación");
  assert.equal(h.elements.get("potential-key").hidden, false);
  assert.match(h.elements.get("potential-status").textContent, /Riesgo inmediato/);
  assert.equal(h.attributions, 1);
  assert.equal(h.elements.has("context-focus"), false, "sin controles manuales");
  await h.view.load(incident("a"));
  h.flush();
  assert.equal(h.fits.length, 1);
  assert.equal(h.contexts.at(-1).incident_id, "a");
  h.view.setVisible(false); h.flush();
  assert.equal(h.contexts.at(-1), null);
  assert.equal(h.painted.length, 0);
  assert.equal(h.attributions, 0);
  h.view.setVisible(true); h.flush();
  assert.equal(h.painted.length, 1);
  h.view.clear(); h.flush();
  assert.equal(h.painted.length, 0);
  assert.equal(h.elements.get("potential-key").hidden, true);
});

test("el rótulo aparece sobre el calor y desaparece al vaciar la selección", async t => {
  const h = harness(async () => ({ ok: true, json: async () => context() })); t.after(h.restore);
  await h.view.load(incident("a"));
  h.flush();
  h.hover(400, 300);
  const tip = h.elements.get("heat-tip");
  assert.equal(tip.hidden, false);
  assert.match(tip.textContent, /120 residentes/);
  assert.match(tip.style.transform, /translate\(400px, 300px\)/);
  h.hover(4000, 300);
  assert.equal(tip.hidden, true);
  h.hover(400, 300); assert.equal(tip.hidden, false);
  h.view.clear();
  assert.equal(tip.hidden, true);
});

test("una respuesta tardía no sustituye la zona seleccionada ni mueve la cámara", async t => {
  const pending = [];
  const h = harness(() => new Promise(resolve => pending.push(resolve))); t.after(h.restore);
  const a = h.view.load(incident("a"), { focus: true });
  const b = h.view.load(incident("b"), { focus: true });
  const current = context("b"); current.potential.samples[0].id = "cell:b";
  pending[1]({ ok: true, json: async () => current }); await b;
  pending[0]({ ok: true, json: async () => context("a") }); await a;
  assert.equal(h.contexts.at(-1).incident_id, "b", "los iconos reciben solo el contexto vigente");
  h.flush(); h.hover(400, 300);
  assert.match(h.elements.get("heat-tip").textContent, /120 residentes/);
  assert.equal(h.fits.length, 2);
});

test("fallo de API retira el calor anterior y no pide activación manual", async t => {
  let fail = false;
  const h = harness(async () => ({ ok: !fail, json: async () => context() })); t.after(h.restore);
  await h.view.load(incident("a")); h.flush();
  assert.equal(h.painted.length, 1);
  fail = true;
  await h.view.load(incident("b"), { focus: true }); h.flush();
  assert.equal(h.painted.length, 0);
  assert.equal(h.attributions, 0);
  assert.match(h.elements.get("potential-status").textContent, /no disponible/);
  assert.equal(h.elements.has("context-retry"), false);
});

test("cerrar invalida respuestas pendientes; sin cobertura no se pinta calor", async t => {
  let resolve;
  const h = harness(() => new Promise(done => { resolve = done; })); t.after(h.restore);
  const pending = h.view.load(incident("a")); h.view.clear();
  resolve({ ok: true, json: async () => context() }); await pending;
  h.flush();
  assert.equal(h.painted.length, 0);
  assert.equal(h.elements.get("potential-key").hidden, true);
  const empty = context();
  empty.potential.status = "unavailable"; empty.potential.samples[0].score = null;
  const blank = harness(async () => ({ ok: true, json: async () => empty })); t.after(blank.restore);
  await blank.view.load(incident("a")); blank.flush();
  assert.equal(blank.painted.length, 0);
  assert.equal(blank.attributions, 0);
  assert.match(blank.elements.get("potential-status").textContent, /sin cobertura/);
});
