import { test } from "node:test";
import assert from "node:assert/strict";
import { groupPlaces, facilityDetails, safeLink, camerasVisible, roadEvents, roadLayerMixin, frozenLevelChange, facilitiesVisible, fireExclusionBoxes, obscuresFire, relevantFacilities, FACILITY_LIMIT, FACILITY_TOTAL } from "./static/infrastructure.js";

test("las instalaciones solo aparecen de cerca y nunca encima de una huella ampliada", () => {
  assert.equal(facilitiesVisible(12.99), false);
  assert.equal(facilitiesVisible(13), true);
  const fire = { lat: 0, lon: 0, footprint: { type: "Polygon", coordinates: [[[-.01, -.01], [.01, -.01], [.01, .01], [-.01, -.01]]] } };
  const boxes = fireExclusionBoxes([fire], ([lat, lon]) => ({ x: lon, y: lat }));
  assert.equal(obscuresFire({ x: 25, y: 0 }, boxes), true);
  assert.equal(obscuresFire({ x: 80, y: 0 }, boxes), false);
  assert.equal(obscuresFire({ x: 0, y: 0 }, []), false);
});

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

test("congelada durante el zoom continuo, la rejilla de carreteras solo se recalcula al cruzar un zoom entero", () => {
  const calls = [];
  const base = {
    getEvents() { return { viewprereset() {}, zoom() {} }; },
    _setView(center, zoom, noPrune, noUpdate) { calls.push(["setView", zoom, noPrune, noUpdate]); this._tileZoom = Math.round(zoom); },
    _onMoveEnd() { calls.push(["moveend"]); },
  };
  const layer = Object.assign(Object.create(roadLayerMixin(base)), {
    _map: { getCenter: () => [0, 0], getZoom: () => 8.4 }, _tileZoom: 8,
    _setZoomTransforms(center, zoom) { calls.push(["transform", zoom]); },
    _resetView() { calls.push(["reset"]); this._setView([0, 0], this._map.getZoom()); },
  });
  assert.deepEqual(Object.keys(layer.getEvents()), ["zoom"]);
  assert.equal(frozenLevelChange(8.4, 8), false); assert.equal(frozenLevelChange(8.6, 8), true);
  layer._setView([0, 0], 8.2); layer._onMoveEnd();
  assert.deepEqual(calls, [["setView", 8.2, undefined, undefined], ["moveend"]], "sin congelar se comporta como Leaflet");
  calls.length = 0; layer.freeze();
  layer._setView([0, 0], 8.3); layer._onMoveEnd(); layer._setView([0, 0], 8.45);
  assert.deepEqual(calls, [["transform", 8.3], ["transform", 8.45]], "misma tesela: solo transformación CSS, sin pedir ni podar");
  calls.length = 0;
  layer._setView([0, 0], 8.7);
  assert.deepEqual(calls, [["setView", 8.7, true, undefined]], "al cruzar un zoom entero pide teselas sin podar el nivel anterior");
  assert.equal(layer._tileZoom, 9);
  calls.length = 0; layer.thaw(); layer.thaw();
  assert.deepEqual(calls, [["reset"], ["setView", 8.4, undefined, undefined]], "descongelar recoloca y poda una sola vez");
  calls.length = 0; layer._onMoveEnd();
  assert.deepEqual(calls, [["moveend"]]);
  const fresh = Object.assign(Object.create(roadLayerMixin(base)), { _map: { getZoom: () => 5 } });
  fresh.freeze(); fresh._setView([0, 0], 5.5);
  assert.deepEqual(calls.at(-1), ["setView", 5.5, undefined, undefined], "sin nivel inicial, la primera vista carga teselas aunque esté congelada");
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

test("los puntos de residuos salen del mapa salvo los pocos con prioridad alta", () => {
  const facilities = [
    { id: "n:1", category: "gestion_residuos", priority: "revisar", distance_km: .2 },
    { id: "n:2", category: "vertedero", priority: "alta_orientativa", distance_km: 3 },
    { id: "n:3", category: "vertedero", priority: "alta_orientativa", distance_km: 1 },
    { id: "n:4", category: "gestion_residuos", priority: "alta_orientativa", distance_km: 2 },
    { id: "n:5", category: "gasolinera", priority: "revisar", distance_km: 4 },
  ];
  assert.equal(FACILITY_LIMIT, 2);
  assert.deepEqual(relevantFacilities(facilities).map(poi => poi.id), ["n:3", "n:4", "n:5"]);
  assert.deepEqual(relevantFacilities([facilities[0]]), []);
  assert.deepEqual(relevantFacilities([facilities[4]]), [facilities[4]]);
});

test("las instalaciones se reducen a una muestra: dos por familia de icono y un total acotado", () => {
  const fuel = Array.from({ length: 6 }, (_, i) => ({ id: `f:${i}`, category: "gasolinera", priority: i === 5 ? "alta_orientativa" : "revisar", distance_km: i }));
  const factory = Array.from({ length: 5 }, (_, i) => ({ id: `i:${i}`, category: i % 2 ? "fabrica" : "area_industrial", priority: "revisar", distance_km: 4 - i }));
  const rest = [
    { id: "p", category: "puerto", priority: "revisar", distance_km: 3 },
    { id: "h", category: "helipuerto", priority: "revisar", distance_km: 4.5 },
    { id: "a", category: "aeropuerto_aerodromo", priority: "revisar", distance_km: 1 },
    { id: "c", category: "central_combustion", priority: "revisar", distance_km: 2 },
    { id: "t", category: "combustibles_quimica", priority: "revisar", distance_km: 2 },
  ];
  const ids = relevantFacilities([...fuel, ...factory, ...rest]).map(poi => poi.id);
  assert.equal(FACILITY_TOTAL, 8);
  assert.equal(ids.length, FACILITY_TOTAL);
  assert.ok(ids.includes("f:5") && ids.includes("f:0"), "prioridad alta y la más cercana de cada familia");
  assert.ok(!ids.includes("f:1"), "no más de dos por familia");
  assert.ok(["p", "a", "c", "t", "i:4"].every(id => ids.includes(id)), "cada familia conserva su primer representante antes de repetir");
  assert.ok(!ids.includes("h"), "el segundo de una familia lejana cede ante los primeros de otras");
  assert.deepEqual(relevantFacilities([]), []);
});

test("enlaces rechazan scripts, credenciales y protocolos no web", () => {
  for (const value of ["javascript:alert(1)", "data:text/html,test", "https://user:pass@example.org", "/local", null]) assert.equal(safeLink(value), null);
  assert.equal(safeLink("https://www.openstreetmap.org/way/12"), "https://www.openstreetmap.org/way/12");
});
