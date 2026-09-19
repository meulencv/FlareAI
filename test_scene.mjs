import test from 'node:test';
import assert from 'node:assert/strict';
import { trafficProgress, trafficOpacity } from './static/traffic.js';
import { priorityLine, extinctionLine, engagedHospitals, HOSPITAL_THREAT_LIMIT } from './static/scene.js';
import { patrolTargets, engagedStations } from './static/director.js';

test('los coches desaparecen lejos y entran progresivamente al acercarse', () => {
  assert.equal(trafficOpacity(10), 0);
  assert.ok(trafficOpacity(12) > 0 && trafficOpacity(12) < 1);
  assert.equal(trafficOpacity(14), 1);
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
  assert.equal(extinctionLine({ phase: 'active', suppression_power: 4, extinguished_pct: 37 }), 'Extinción simulada 37 % · 4 medios trabajando · más medios, antes');
  assert.equal(extinctionLine({ phase: 'watching', suppression_power: 4, extinguished_pct: 90 }), '');
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
