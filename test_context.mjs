import { test } from "node:test";
import assert from "node:assert/strict";
import { contextSummary, createContextView, pointsVisible, safeSourceUrl } from "./static/context.js";

function context(id = "a") {
  return {
    incident_id: id, level: "attention", coverage: "grid_centres_in_radius", radius_km: 5,
    population: { residents: 42, inhabited_cells: 2, downwind_residents: 12, children_under_15: 4, adults_65_plus: 9 },
    facilities: { count: 3, high_priority: 2, downwind_high_priority: 1 },
    wind: { status: "current", usable: true },
    landcover: { percentages: { bosque: 60, urbano: 40 }, missing_cells: 0 },
    sources: { population: "Censo 2021", details_url: "/atlas/sources" },
    points: [{ id: "cell:1", kind: "population", name: "Celda habitada", residents: 42, lat: 40, lon: -3, distance_km: 1.2, downwind: true }],
    method: "No es una predicción.", points_truncated: false,
  };
}

test("los datos históricos, nulos y los ceros tienen explicaciones distintas", () => {
  const data = context();
  assert.match(contextSummary(data).headline, /Atención/);
  data.wind.status = "historical";
  assert.match(contextSummary(data).directional, /no aviso actual/);
  data.wind.status = "stale";
  assert.match(contextSummary(data).directional, /desactualizada/);
  data.population.residents = null;
  assert.match(contextSummary(data).population, /sin datos/);
  data.population.residents = 0;
  assert.match(contextSummary(data).population, /^0 residentes/);
  data.coverage = "no_grid_cells";
  assert.match(contextSummary(data).headline, /Sin cobertura/);
});

test("puntos solo en detalle local y enlaces OSM restringidos", () => {
  assert.equal(pointsVisible(context(), 8, true), false);
  assert.equal(pointsVisible(context(), 10, true), true);
  assert.equal(pointsVisible(context(), 12, false), false);
  assert.equal(pointsVisible(null, 12, true), false);
  assert.equal(safeSourceUrl("https://www.openstreetmap.org/way/123"), "https://www.openstreetmap.org/way/123");
  for (const url of ["javascript:alert(1)", "https://www.openstreetmap.org.evil/way/1", "//evil", null]) assert.equal(safeSourceUrl(url), null);
});

function harness(fetch) {
  const elements = new Map(), layers = [], events = {};
  function element() {
    return { textContent: "", checked: true, hidden: false, children: [],
      classList: { toggle() {}, remove() {} },
      append(...children) { this.children.push(...children); }, replaceChildren() { this.children = []; } };
  }
  const document = { getElementById(id) { if (!elements.has(id)) elements.set(id, element()); return elements.get(id); }, createElement: element };
  const layer = { addTo() { return this; }, clearLayers() { layers.length = 0; } };
  const L = { layerGroup: () => layer, circleMarker() { return { bindPopup() { return this; }, addTo() { layers.push(this); return this; }, openPopup() {} }; } };
  let zoom = 12;
  const map = { getZoom: () => zoom, on(name, handler) { events[name] = handler; } };
  const view = createContextView({ map, L, document, fetch });
  return { view, elements, layers, setZoom(value) { zoom = value; events.zoomend(); } };
}

test("una respuesta tardía no sustituye la zona seleccionada", async () => {
  const pending = [];
  const h = harness(() => new Promise(resolve => pending.push(resolve)));
  const a = h.view.load({ id: "a" });
  const b = h.view.load({ id: "b" });
  const current = context("b"); current.population.residents = 99;
  pending[1]({ ok: true, json: async () => current }); await b;
  pending[0]({ ok: true, json: async () => context("a") }); await a;
  assert.match(h.elements.get("context-population").textContent, /^99 residentes/);
  assert.equal(h.layers.length, 1);
  h.setZoom(7); assert.equal(h.layers.length, 0);
  h.setZoom(12); assert.equal(h.layers.length, 1);
  h.view.setVisible(false); assert.equal(h.layers.length, 0);
  h.view.clear(); assert.equal(h.elements.get("context-data").hidden, true);
});

test("fallo de API elimina puntos anteriores y ofrece reintento", async () => {
  let fail = false;
  const h = harness(async () => ({ ok: !fail, json: async () => context() }));
  await h.view.load({ id: "a" }); assert.equal(h.layers.length, 1);
  fail = true;
  await h.view.load({ id: "b" });
  assert.equal(h.layers.length, 0);
  assert.equal(h.elements.get("context-data").hidden, true);
  assert.equal(h.elements.get("context-retry").hidden, false);
  assert.match(h.elements.get("context-summary").textContent, /no disponible/);
});

test("cerrar el detalle invalida la consulta pendiente y escapa nombres", async () => {
  let resolve;
  const h = harness(() => new Promise(done => { resolve = done; }));
  const pending = h.view.load({ id: "a" }); h.view.clear();
  resolve({ ok: true, json: async () => context() }); await pending;
  assert.equal(h.layers.length, 0);
  const malicious = context(); malicious.points[0].name = '<img src=x onerror="alert(1)">';
  const safe = harness(async () => ({ ok: true, json: async () => malicious }));
  await safe.view.load({ id: "a" });
  const html = safe.elements.get("context-points").children[0].children[0].innerHTML;
  assert.ok(!html.includes("<img")); assert.ok(html.includes("&lt;img"));
});
