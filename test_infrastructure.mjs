import { test } from "node:test";
import assert from "node:assert/strict";
import { groupPlaces, facilityDetails, safeLink, camerasVisible, roadEvents } from "./static/infrastructure.js";

test("las cámaras son invisibles en panorama y aparecen solo a escala local", () => {
  assert.equal(camerasVisible(6), false);
  assert.equal(camerasVisible(9.99), false);
  assert.equal(camerasVisible(10), true);
  assert.equal(camerasVisible(14), true);
});

test("las carreteras conservan teselas durante resets de zoom sin perder reproyección", () => {
  const handlers = { viewprereset() {}, viewreset() {}, zoom() {}, moveend() {} };
  const events = roadEvents(handlers);
  assert.equal(events.viewprereset, undefined);
  assert.equal(events.viewreset, handlers.viewreset);
  assert.equal(events.zoom, handlers.zoom);
  assert.equal(events.moveend, handlers.moveend);
  assert.ok(handlers.viewprereset, "no altera otras capas");
});

const project = ([lat, lon]) => ({ x: lon * 100, y: lat * 100 });
test("agrupa sin perder instalaciones y separa al acercar; coincidentes siguen accesibles", () => {
  const points = [{ id: "a", lat: 40, lon: -3 }, { id: "b", lat: 40.01, lon: -3 }, { id: "c", lat: 41, lon: -2 }];
  assert.equal(groupPlaces(points, project, 64).length, 2);
  assert.equal(groupPlaces(points, project, 0).length, 3);
  const same = [...points, { ...points[0], id: "d" }];
  const groups = groupPlaces(same, project, 0);
  assert.equal(groups.length, 3);
  assert.equal(groups.reduce((sum, group) => sum + group.items.length, 0), 4);
});

test("la ficha distingue prioridad orientativa, distancia y viento histórico", () => {
  const poi = { category: "gasolinera", name: "<img onerror=alert(1)>", distance_km: 0, priority: "alta_orientativa", downwind: true };
  const current = facilityDetails(poi, { status: "current" });
  assert.equal(current.name, poi.name);
  assert.equal(current.icon, "fuel");
  assert.match(current.distance, /0 km/);
  assert.match(current.wind, /actual/);
  assert.match(facilityDetails(poi, { status: "historical" }).wind, /histórica/);
  assert.match(facilityDetails(poi, { status: "stale" }).wind, /Sin viento actual/);
  assert.match(current.priority, /orientativa/);
  assert.match(facilityDetails({ category: "unknown" }, {}).distance, /no disponible/);
});

test("enlaces rechazan scripts, credenciales y protocolos no web", () => {
  for (const value of ["javascript:alert(1)", "data:text/html,test", "https://user:pass@example.org", "/local", null]) assert.equal(safeLink(value), null);
  assert.equal(safeLink("https://www.openstreetmap.org/way/12"), "https://www.openstreetmap.org/way/12");
});
