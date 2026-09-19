import test from 'node:test';
import assert from 'node:assert/strict';
import process from 'node:process';
import { createOperationView, mergeBrainNotes, testimonyRows, witnessPosition, hashSeed } from './static/operations.js';
import { GET, POST } from './happyrobot-112/cloud/route.js';

const { Request, Response } = globalThis;
const room = '00000000-0000-4000-8000-000000000001';

test('el cerebro muestra cuatro notas base sin API y conecta respuestas antiguas sin duplicar notas', () => {
  const base = mergeBrainNotes();
  assert.equal(base.length, 4);
  assert.ok(base.every(note => note.links.every(id => base.some(target => target.id === id))));
  const old = [{ id: 'report-1', kind: 'report', title: 'Informe' }];
  assert.equal(mergeBrainNotes(old).length, 5);
  assert.deepEqual(mergeBrainNotes(old).at(-1).links, ['base-learning']);
  assert.deepEqual(old, [{ id: 'report-1', kind: 'report', title: 'Informe' }]);
  const remote = base.map(note => ({ ...note, text: 'Versión del servidor' }));
  assert.equal(mergeBrainNotes(remote).length, 4);
  assert.ok(mergeBrainNotes(remote).every(note => note.text === 'Versión del servidor'));
});

test('el feed distingue webcall de testimonios sintéticos y conserva sus evaluaciones', () => {
  const rows = testimonyRows([{ citizen: { id: 'real', at: 1, source: 'webcall' }, testimonies: [{ id: 'demo', at: 2, source: 'synthetic_demo' }], assessment: { testimonies: [{ id: 'demo', status: 'uncertain' }] } }]);
  assert.equal(rows[0].id, 'demo');
  assert.equal(rows[0].assessment.status, 'uncertain');
  assert.equal(rows[1].source, 'webcall');
});

test('las personitas se reparten de forma estable alrededor del aviso y la llamada 112 queda junto al foco', () => {
  const incident = { lat: 41.4, lon: 2.17 };
  const east = 111320 * Math.cos(incident.lat * Math.PI / 180);
  const meters = ([lat, lon]) => Math.hypot((lat - incident.lat) * 111320, (lon - incident.lon) * east);
  const call = witnessPosition({ id: 'citizen:run', source: 'webcall' }, incident, .2);
  assert.deepEqual(call, witnessPosition({ id: 'citizen:run', source: 'webcall' }, incident, .2));
  assert.ok(Math.abs(meters(call) - 430) < 1);
  const spots = Array.from({ length: 24 }, (_, i) => witnessPosition({ id: `t${i}`, speaker: `Testigo ${String(i + 1).padStart(2, '0')}`, source: 'synthetic_demo' }, incident, .2));
  for (const spot of spots) { assert.ok(meters(spot) >= 500 && meters(spot) <= 1060); }
  assert.ok(new Set(spots.map(s => s.join(','))).size === 24, 'sin posiciones repetidas');
  assert.notEqual(hashSeed('a'), hashSeed('b'));
});

test('las llamadas y testigos desaparecen al cerrar el incendio sin perder el historial ni otros avisos', () => {
  const element = () => ({ setAttribute() {}, append() {}, prepend() {}, addEventListener() {}, classList: { add() {} } });
  const document = { createElement: element, createElementNS: element, body: element() };
  const visible = new Set();
  const layer = { addTo() { return this; }, removeLayer(marker) { visible.delete(marker); } };
  const L = {
    layerGroup: () => layer,
    divIcon: options => options,
    marker: (position, options) => ({
      options,
      bindTooltip() { return this; },
      addTo() { visible.add(this); return this; },
      setIcon() {}, setTooltipContent() {}, setLatLng() {},
    }),
  };
  const incidents = new Map(['resolved', 'active'].map(id => [id, { id, lat: 41.4, lon: 2.17, scenario: { phase: 'active' } }]));
  const records = [...incidents.keys()].map(id => ({ id,
    citizen: { id: `${id}:call`, speaker: 'Llamada 112', source: 'webcall', at: 1, text: id },
    testimonies: [{ id: `${id}:witness`, speaker: 'Testigo 1', source: 'synthetic_demo', at: 2, text: id }],
    outbound: { status: 'completed' },
  }));
  const view = createOperationView({ document, L, map: { getPane: () => ({}) }, findIncident: id => incidents.get(id) });
  const state = { operations: { incidents: records } };
  const snapshot = structuredClone(records);
  const assertResolvedHidden = () => {
    assert.equal(visible.size, 2);
    assert.ok([...visible].every(marker => marker.options.alt.endsWith(': active')));
  };
  view.update(state);
  assert.equal(visible.size, 4, 'colgar no retira los avisos de incendios activos');
  for (const phase of ['contained', 'watching', 'releasing']) {
    view.update({ ...state, scenario: { incidents: { resolved: { phase } } } });
    assert.equal(visible.size, 4, 'se conservan durante la intervención y el regreso');
  }
  const closed = { ...state, scenario: { incidents: { resolved: { phase: 'closed' } } } };
  view.update(closed);
  assertResolvedHidden();
  view.update(closed);
  assertResolvedHidden();
  assert.deepEqual(records, snapshot, 'el historial sigue intacto');
  view.update(state);
  view.update({ ...state, auto: { resolved: { phase: 'closed' } } });
  assertResolvedHidden();
  view.update(state);
  incidents.get('resolved').scenario.phase = 'closed';
  view.update(state);
  assertResolvedHidden();
  incidents.get('resolved').scenario.phase = 'active';
  for (const completion of [{ reported: true }, { report_id: 'report:resolved' }]) {
    view.update(state);
    view.update({ operations: { incidents: [{ ...records[0], ...completion }, records[1]] } });
    assertResolvedHidden();
  }
  view.update(state);
  incidents.get('resolved').demo_report = { cancelled: true };
  view.update(state);
  assertResolvedHidden();
  view.update({});
  assert.equal(visible.size, 0);
});

test('112 cloud protege la sesión, rechaza 123 y no revela credenciales', async () => {
  const keys = ['HAPPYROBOT_API_KEY', 'TWIN_API_KEY', 'HAPPYROBOT_WORKFLOW_ID', 'DEMO_ACCESS_CODE', 'DEMO_COOKIE_SECRET'];
  const before = Object.fromEntries(keys.map(key => [key, process.env[key]]));
  Object.assign(process.env, { HAPPYROBOT_API_KEY: 'voice-private-fixture', TWIN_API_KEY: 'twin-private-fixture', HAPPYROBOT_WORKFLOW_ID: 'fixture', DEMO_ACCESS_CODE: 'access-fixture', DEMO_COOKIE_SECRET: 'cookie-fixture-secret-that-is-long-enough' });
  const previousFetch = globalThis.fetch, requests = [];
  globalThis.fetch = async (url, options) => {
    requests.push({ url, options });
    assert.ok(url.endsWith('/twin/sql'), 'No debe iniciarse voz real en estas pruebas');
    const query = JSON.parse(options.body).sql;
    return Response.json({ rows: query.includes('active-room') ? [{ data: { session_id: room, heartbeat_at: Date.now() / 1000 } }] : [], truncated: false });
  };
  const post = (route, body, cookie = '', origin = 'https://demo.example') => POST(new Request(`https://demo.example/112/api/${route}`, { method: 'POST', headers: { origin, cookie, 'content-type': 'application/json' }, body: JSON.stringify(body) }));
  try {
    assert.equal((await post('session', { access_code: 'wrong' })).status, 403);
    assert.equal((await post('session', { access_code: 'access-fixture' }, '', 'https://other.example')).status, 403);
    const result = await post('session', { access_code: 'access-fixture' });
    assert.equal(result.status, 200);
    const header = result.headers.get('set-cookie');
    assert.match(header, /HttpOnly; Secure; SameSite=Strict/);
    const cookie = header.split(';')[0];
    const ready = await GET(new Request('https://demo.example/112/api/status', { headers: { cookie } }));
    assert.equal((await ready.json()).browser_ready, true);
    assert.equal((await post('call', { number: '123', request_id: room }, cookie)).status, 400);
    assert.equal((await GET(new Request(`https://demo.example/112/api/brief?run_id=${room}`))).status, 403);
    const status = JSON.stringify(await (await GET(new Request('https://demo.example/112/api/status'))).json());
    assert.ok(!status.includes('private-fixture'));
    assert.ok(requests.length > 0);
  } finally {
    globalThis.fetch = previousFetch;
    for (const key of keys) if (before[key] === undefined) delete process.env[key]; else process.env[key] = before[key];
  }
});
