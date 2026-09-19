import test from 'node:test';
import assert from 'node:assert/strict';
import { createTraffic, trafficProgress, trafficOpacity, localTrafficRoads, trafficRouteRoads, TRAFFIC_LIMIT } from './static/traffic.js';
import { createSceneView, priorityLine, extinctionLine, engagedHospitals, HOSPITAL_THREAT_LIMIT, sessionImpact } from './static/scene.js';

const impactRecord = (id, metrics = {}) => ({ id, report_id: `report-${id}`, reported: true,
  metrics: { avoided_area_ha: 12, avoided_co2_t: 50, carbon_value_eur: [500, 1500, 3000], ...metrics } });

test('impacto acumula informes únicos de la sesión, no avisos activos ni duplicados', () => {
  const first = impactRecord('first'), second = impactRecord('second');
  const state = { operations: { incidents: [first, second, { ...first }, { id: 'active' }] } };
  const before = JSON.stringify(state);
  assert.deepEqual(sessionImpact(state), { reports: 2, area: 24, co2: 100, carbon: [1000, 6000], areaCount: 2, co2Count: 2, carbonCount: 2 });
  assert.equal(JSON.stringify(state), before);
  assert.equal(sessionImpact({}).co2, null);
  assert.equal(sessionImpact({ operations: { incidents: [] } }).reports, 0);
});

test('impacto distingue cero, cobertura parcial y datos desconocidos o no válidos', () => {
  const sea = impactRecord('sea', { avoided_co2_t: null, carbon_value_eur: null });
  const land = impactRecord('land');
  const partial = sessionImpact({ operations: { incidents: [sea, land] } });
  assert.equal(partial.reports, 2);
  assert.equal(partial.co2Count, 1);
  assert.equal(partial.carbonCount, 1);
  assert.equal(partial.co2, 50);
  assert.equal(sessionImpact({ operations: { incidents: [sea] } }).co2, null);
  const zero = impactRecord('zero', { avoided_area_ha: 0, avoided_co2_t: 0, carbon_value_eur: [0, 0, 0] });
  assert.equal(sessionImpact({ operations: { incidents: [zero] } }).co2, 0);
  const invalid = impactRecord('invalid', { avoided_area_ha: -1, avoided_co2_t: NaN, carbon_value_eur: [0, Infinity] });
  assert.equal(sessionImpact({ operations: { incidents: [invalid] } }).carbon, null);
  assert.equal(sessionImpact({ operations: { incidents: [invalid] } }).area, null);
});
import { patrolTargets, engagedStations } from './static/director.js';

test('la sala no crea canvas de tráfico ni solicita carreteras para coches', () => {
  const elements = new Map(), requests = [];
  const node = () => ({ hidden: true, dataset: {}, style: {}, append() {}, replaceChildren() {}, setAttribute() {} });
  const document = { getElementById(id) {
    assert.ok(!['scene-controls', 'scene-barcelona', 'scene-field', 'scene-incident'].includes(id));
    if (!elements.has(id)) elements.set(id, node()); return elements.get(id);
  }, createElement(tag) { assert.notEqual(tag, 'canvas'); return node(); }, querySelectorAll: () => [] };
  const group = () => ({ addTo() { return this; }, clearLayers() {}, remove() {} });
  const map = { on() {}, getZoom: () => 16 };
  const view = createSceneView({ map, L: { layerGroup: group }, document, fetch: url => requests.push(url), focus() {} });
  view.update({ session_id: 'no-traffic', status: 'watching', events: [], assignments: {} });
  view.tick();
  assert.equal(elements.get('impact-co2').textContent, '—');
  const completed = { session_id: 'no-traffic', operations: { incidents: [impactRecord('done')] } };
  view.update(completed);
  view.update(completed);
  assert.equal(elements.get('impact-co2').textContent, '50 t');
  assert.equal(elements.get('impact-area').textContent, '12 ha');
  assert.equal(elements.get('impact-operations').textContent, '1');
  assert.match(elements.get('impact-carbon').textContent, /500–3000 €/);
  view.update({ session_id: 'new-session' });
  assert.equal(elements.get('impact-co2').textContent, '—');
  assert.equal(elements.get('impact-operations').textContent, '0');
  assert.deepEqual(requests, []);
});

test('el historial oculta informes tanto en directo como al recuperar la sesión', async () => {
  const elements = new Map();
  const node = () => ({ hidden: true, dataset: {}, style: {}, children: [],
    append(...children) { this.children.push(...children); }, replaceChildren() { this.children = []; }, setAttribute() {} });
  const document = { getElementById(id) { if (!elements.has(id)) elements.set(id, node()); return elements.get(id); },
    createElement: node, querySelectorAll: () => [] };
  const group = () => ({ addTo() { return this; }, clearLayers() {}, remove() {} });
  const events = [{ sequence: 1, at: 100, kind: 'return', message: 'Regreso a base' },
    { sequence: 2, at: 101, kind: 'report_ready', message: 'Informe disponible' }];
  const view = createSceneView({ map: { on() {}, getZoom: () => 16 }, L: { layerGroup: group }, document,
    fetch: async () => ({ ok: true, json: async () => ({ session_id: 'reports-hidden', events }) }), focus() {} });
  view.update({ session_id: 'reports-hidden', events, assignments: {} });
  const check = () => {
    assert.equal(elements.get('decision-history').children.length, 1);
    assert.match(elements.get('history-count').textContent, /^1 pasos/);
  };
  check();
  await elements.get('history-toggle').onclick();
  check();
  assert.equal(events.length, 2);
});

test('los coches desaparecen lejos y entran progresivamente al acercarse', () => {
  assert.equal(trafficOpacity(10), 0);
  assert.equal(trafficOpacity(12.5), 0);
  assert.equal(trafficOpacity(13), 0);
  assert.ok(trafficOpacity(13.5) > 0 && trafficOpacity(13.5) < 1);
  assert.equal(trafficOpacity(14), 1);
});

test('tráfico escaso solo en carreteras próximas a las unidades, no por todo el mapa', () => {
  const road = (id, lat) => ({ id, coordinates: [[2.17, lat], [2.175, lat]] });
  const near = road('near', 41.4), distant = road('far', 41.43);
  const vehicles = [{ lon: 2.172, lat: 41.4 }];
  assert.deepEqual(localTrafficRoads([distant, near], vehicles), [near]);
  assert.deepEqual(localTrafficRoads([near], []), []);
  assert.deepEqual(localTrafficRoads([near], [{ lon: 2.25, lat: 41.4 }]), []);
  const many = Array.from({ length: 1000 }, (_, i) => road(String(i), 41.4 + i / 1000000));
  assert.ok(localTrafficRoads(many, vehicles).length <= TRAFFIC_LIMIT / 2);
  assert.deepEqual(localTrafficRoads(many, vehicles), localTrafficRoads([...many].reverse(), vehicles));
});

test('fuera de la red preparada reutiliza geometrías de rutas, nunca rectas aproximadas ni vuelos', () => {
  const route = { coordinates: [[-3.7, 40.4], [-3.701, 40.401], [-3.702, 40.401]], edge_ids: ['a', 'b'] };
  const vehicles = [{ route }, { route }, { route: { ...route, approximate: true } }, { route: { ...route, mode: 'air' } }];
  assert.deepEqual(trafficRouteRoads(vehicles).map(r => r.id), ['a', 'b']);
  assert.deepEqual(trafficRouteRoads([{ route: { ...route, approximate: true } }]), []);
  assert.deepEqual(trafficRouteRoads([{ route: { ...route, mode: 'air' } }]), []);
});

test('el canvas limpia tráfico lejano, pausa el movimiento y descarta descargas tardías', async t => {
  const frames = new Map(), draws = [], requests = [];
  let serial = 0, zoom = 14, vehicles = [{ lat: 41.4, lon: 2.17,
    route: { coordinates: [[2.168, 41.4], [2.172, 41.4]] } }];
  const ctx = { setTransform() {}, clearRect() { draws.length = 0; }, save() {}, restore() {}, rotate() {}, fillRect() {},
    translate(x, y) { draws.push([x, y]); } };
  const canvas = { style: {}, dataset: {}, setAttribute() {}, getContext: () => ctx };
  const document = { hidden: false, createElement: () => canvas, addEventListener() {} };
  const globals = {
    window: { devicePixelRatio: 2 }, matchMedia: () => ({ matches: false, addEventListener() {} }),
    requestAnimationFrame: callback => { frames.set(++serial, callback); return serial; }, cancelAnimationFrame: id => frames.delete(id),
  };
  for (const [key, value] of Object.entries(globals)) {
    const descriptor = Object.getOwnPropertyDescriptor(globalThis, key);
    Object.defineProperty(globalThis, key, { value, configurable: true, writable: true });
    t.after(() => { if (descriptor) Object.defineProperty(globalThis, key, descriptor); else Reflect.deleteProperty(globalThis, key); });
  }
  const map = {
    getZoom: () => zoom, getSize: () => ({ x: 800, y: 600 }), getPane: () => ({ append() {} }), on() {},
    getBounds: () => ({ contains: ([lat, lon]) => Math.abs(lat - 41.4) < .003 && Math.abs(lon - 2.17) < .004 }),
    containerPointToLayerPoint: () => ({ x: 0, y: 0 }),
    latLngToContainerPoint: ([lat, lon]) => ({ x: 400 + (lon - 2.17) * 100000, y: 300 - (lat - 41.4) * 100000 }),
  };
  const traffic = createTraffic({ map, L: { DomUtil: { setPosition() {} } }, document, getVehicles: () => vehicles,
    fetch: (url, options) => new Promise(resolve => requests.push({ url, options, resolve })) });
  const tick = time => { const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(callback => callback(time)); };
  traffic.update({ enabled: true }, 'one'); tick(100);
  assert.equal(requests.length, 1);
  assert.ok(Number(canvas.dataset.cars) > 0 && Number(canvas.dataset.cars) <= TRAFFIC_LIMIT);
  assert.ok(draws.every(([x, y]) => Math.hypot(x - 400, y - 300) <= 220));
  const moving = JSON.stringify(draws); tick(150);
  assert.notEqual(JSON.stringify(draws), moving);
  traffic.setPaused(true); tick(200);
  const frozen = JSON.stringify(draws); traffic.update({ enabled: true }, 'one'); tick(400);
  assert.equal(JSON.stringify(draws), frozen);
  assert.equal(requests.length, 1, 'no duplica la petición pendiente');
  zoom = 12; traffic.update({ enabled: true }, 'one'); tick(500);
  assert.equal(canvas.dataset.cars, '0'); assert.equal(canvas.style.opacity, '0');
  assert.equal(requests[0].options.signal.aborted, true);
  requests[0].resolve({ ok: true, json: async () => ({ roads: [{ id: 'stale', coordinates: [[2.168, 41.4], [2.172, 41.4]] }] }) });
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(canvas.dataset.roads, '0'); assert.equal(canvas.dataset.cars, '0');
  zoom = 14; vehicles = []; traffic.update({ enabled: true }, 'two'); tick(600);
  assert.equal(canvas.dataset.cars, '0'); assert.equal(requests.length, 1);
  vehicles = [{ lat: 41.43, lon: 2.17 }]; traffic.update({ enabled: true }, 'two'); tick(700);
  assert.equal(canvas.dataset.cars, '0'); assert.equal(requests.length, 1);
});

test('ningún coche cruza la barrera y el tapón queda aguas arriba', () => {
  for (let time = 0; time < 300; time++) for (let n = 0; n < 7; n++) {
    const value = trafficProgress(time, n, 7, true);
    assert.ok(value >= 0 && value < .44);
  }
  assert.ok(trafficProgress(3, 0, 1, false, 6) < trafficProgress(3, 0, 1, false, 1));
});

test('prioridad en una sola línea y ronda incluye sensores sin fabricar llamadas', () => {
  assert.equal(priorityLine({ priority: 9.2, priority_reason: 'riesgo vital y cerca de zona urbana' }), 'Prioridad 9.2/10 · riesgo vital y cerca de zona urbana');
  assert.equal(extinctionLine({ phase: 'active', suppression_power: 0, extinguished_pct: 0 }), 'Fuego creciendo · medios en camino');
  assert.match(extinctionLine({ phase: 'active', fire_power: -1 }), /Potencia manual · apagar 1 %/);
  assert.match(extinctionLine({ phase: 'active', fire_power: 80 }), /Potencia manual · avivar 80 %/);
  assert.equal(extinctionLine({ phase: 'active', suppression_power: 4, extinguished_pct: 37 }), 'Extinción simulada 37 % · 4 medios trabajando · más medios, antes');
  assert.equal(extinctionLine({ phase: 'watching', suppression_power: 4, extinguished_pct: 90 }), '');
  assert.match(extinctionLine({ phase: 'active', waiting_suppression: true, suppression_power: 3 }), /esperando llamada o refuerzos/);
  const sensor = { id: 'sensor', sensor_report: { source: 'FIRMS' } };
  assert.equal(patrolTargets([sensor], {}).length, 1);
  assert.equal(patrolTargets([{ ...sensor, scenario: { phase: 'closed' } }], {}).length, 0);
});

test('solo se encienden el hospital del traslado y la sede que moviliza', () => {
  const scene = {
    hospitals: [{ id: 'h1', name: 'Sant Pau', lat: 41.41, lon: 2.18, capacity: 8, occupied: 0 },
      { id: 'h2', name: 'Mar', lat: 41.403, lon: 2.175, capacity: 8, occupied: 0 },
      { id: 'h3', name: 'Clínic', lat: 41.39, lon: 2.15, capacity: 8, occupied: 1 },
      { id: 'h4', name: 'Vall d\'Hebron', lat: 41.42, lon: 2.14, capacity: 8, occupied: 0 },
      { id: 'h5', name: 'Dos de Maig', lat: 41.409, lon: 2.178, capacity: 8, occupied: 0 }],
    incidents: { a: { phase: 'active', lat: 41.4035, lon: 2.1744, hospital_threats: ['Mar', 'Dos de Maig'] },
      b: { phase: 'closed', lat: 41.42, lon: 2.14, hospital_threats: ['Vall d\'Hebron'] } },
  };
  const assignments = { v1: { hospital_id: 'h1', avoided_hospital_ids: ['h5'], resource: { station_id: 's1', kind: 'ambulance' } } };
  assert.deepEqual(engagedHospitals(scene, assignments).map(h => [h.id, h.role]),
    [['h1', 'transfer'], ['h2', 'threatened'], ['h3', 'reserved'], ['h5', 'avoided']]);
  assert.deepEqual(engagedHospitals(scene, {}).map(h => h.id), ['h2', 'h3']);
  assert.deepEqual(engagedHospitals({ hospitals: [{ id: 'h1', name: 'Sant Pau' }], incidents: {} }, {}), []);
  assert.equal(HOSPITAL_THREAT_LIMIT, 1);
  const stations = [{ station_id: 's1', kind: 'ambulance' }, { station_id: 's1', kind: 'fire_engine' }, { station_id: 's2', kind: 'ambulance' }];
  assert.deepEqual(engagedStations(stations, assignments), [stations[0]]);
  assert.deepEqual(engagedStations(stations, {}), []);
  assert.deepEqual(engagedStations(undefined, assignments), []);
});

test('la superficie de riesgo sigue la huella del fuego con margen reducido y sesgo a favor del viento', async () => {
  const { threatOutline, THREAT_MARGIN_KM } = await import('./static/scene.js');
  assert.ok(THREAT_MARGIN_KM <= .08, 'halo pegado al fuego: como mucho 80 metros de margen base');
  const record = { lat: 41.4, lon: 2.17, radius_km: .5, wind_to: 90 };
  const east = 111.32 * Math.cos(record.lat * Math.PI / 180);
  const ring = Array.from({ length: 33 }, (_, i) => {
    const angle = i / 32 * 2 * Math.PI;
    return [record.lon + Math.sin(angle) * .5 / east, record.lat + Math.cos(angle) * .5 / 111.32];
  });
  const outline = threatOutline(record, { type: 'Polygon', coordinates: [ring] });
  assert.equal(outline.length, 32);
  const reach = outline.map(([lat, lon]) => Math.hypot((lat - record.lat) * 111.32, (lon - record.lon) * east));
  assert.ok(Math.max(...reach) < .5 + THREAT_MARGIN_KM * 1.7, 'margen acotado, mucho menor que los 0,8 km anteriores');
  assert.ok(Math.min(...reach) > .5 + THREAT_MARGIN_KM * .6);
  const eastmost = outline.reduce((a, b) => (b[1] > a[1] ? b : a)), westmost = outline.reduce((a, b) => (b[1] < a[1] ? b : a));
  assert.ok((eastmost[1] - record.lon) > (record.lon - westmost[1]), 'más margen a favor del viento');
  assert.equal(threatOutline(record, null).length, 48, 'sin huella recae en un círculo pequeño');
});
