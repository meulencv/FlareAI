import test from 'node:test';
import assert from 'node:assert/strict';
import process from 'node:process';
import { createOperationView, createScenarioEditor, mergeBrainNotes, testimonyRows, witnessPosition, hashSeed } from './static/operations.js';
import { GET, POST } from './happyrobot-112/cloud/route.js';

const { Request, Response } = globalThis;
const room = '00000000-0000-4000-8000-000000000001';

test('el cerebro muestra cuatro notas base sin API y conecta respuestas antiguas sin duplicar notas', () => {
  const base = mergeBrainNotes();
  assert.equal(base.length, 4);
  assert.ok(base.every(note => note.links.every(id => base.some(target => target.id === id))));
  const old = [{ id: 'memory-1', kind: 'memory', title: 'Aprendizaje' }];
  assert.equal(mergeBrainNotes(old).length, 5);
  assert.deepEqual(mergeBrainNotes(old).at(-1).links, ['base-learning']);
  assert.deepEqual(old, [{ id: 'memory-1', kind: 'memory', title: 'Aprendizaje' }]);
  const remote = base.map(note => ({ ...note, text: 'Versión del servidor' }));
  assert.equal(mergeBrainNotes(remote).length, 4);
  assert.ok(mergeBrainNotes(remote).every(note => note.text === 'Versión del servidor'));
});

test('el cerebro excluye informes y sus enlaces sin perder aprendizajes ni mutar la API', () => {
  const notes = [
    { id: 'report-1', kind: 'report', title: 'Informe final', markdown: 'Contenido del PDF' },
    { id: 'memory-1', kind: 'memory', title: 'Aprendizaje', links: ['base-learning', 'report-1'], reports: ['report-1'] },
  ];
  const snapshot = globalThis.structuredClone(notes), merged = mergeBrainNotes(notes);
  assert.equal(merged.length, 5);
  assert.ok(merged.every(note => note.kind !== 'report'));
  assert.deepEqual(merged.at(-1).links, ['base-learning']);
  assert.deepEqual(merged.at(-1).reports, []);
  assert.deepEqual(notes, snapshot);
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
  const element = () => ({ setAttribute() {}, append() {}, prepend() {}, replaceChildren() {}, addEventListener() {}, classList: { add() {} } });
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
  const snapshot = globalThis.structuredClone(records);
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

function editorFixture(fetch) {
  const elements = [], document = {};
  const element = () => {
    const item = { children: [], attributes: {}, handlers: {}, value: '',
      setAttribute(key, value) { this.attributes[key] = value; },
      append(...children) { this.children.push(...children); },
      replaceChildren(...children) { this.children = children; },
      addEventListener(type, handler) { this.handlers[type] = handler; },
      focus() { document.activeElement = this; },
    };
    elements.push(item); return item;
  };
  Object.assign(document, { createElement: element, createElementNS: element, body: element() });
  const editor = createScenarioEditor({ document, fetch });
  const get = id => elements.find(item => item.id === id);
  const state = { session_id: 'test', scenario: { incidents: {
    first: { id: 'first', name: 'Primero', phase: 'active', wind_to: 90 },
    second: { id: 'second', name: 'Segundo', phase: 'watching', wind_to: 180, fire_power: -50 },
    closed: { id: 'closed', name: 'Cerrado', phase: 'closed' },
    linked: { id: 'linked', name: 'Vinculado', phase: 'active', linked_call_id: 'first' },
  } } };
  return { editor, document, get, state };
}

test('el lápiz abre un panel accesible y envía corte, viento y potencia al escenario seleccionado', async () => {
  const requests = [];
  const { editor, get, state, document } = editorFixture(async (url, options) => {
    requests.push({ url, body: JSON.parse(options.body) }); return { ok: true, json: async () => ({ ok: true }) };
  });
  const snapshot = globalThis.structuredClone(state);
  editor.update(state);
  const button = get('scenario-edit-toggle'), panel = get('scenario-edit-panel'), select = get('scenario-edit-incident');
  assert.equal(button.hidden, false); assert.equal(panel.hidden, true);
  button.onclick(); assert.equal(panel.hidden, false); assert.equal(button.attributes['aria-expanded'], 'true');
  assert.equal(select.children.length, 2);
  await get('scenario-random-cut').onclick();
  assert.equal(requests[0].body.action, 'random_closure');
  select.value = 'second'; select.onchange();
  const wind = get('scenario-edit-wind'), power = get('scenario-edit-power');
  assert.equal(wind.value, '180'); assert.equal(power.value, '-50');
  wind.value = '270'; wind.focus(); wind.oninput();
  editor.update(state);
  assert.equal(wind.value, '270', 'el polling no interrumpe el deslizador enfocado');
  await wind.onchange();
  power.value = '75'; power.oninput(); await power.onchange();
  await get('scenario-edit-normal').onclick();
  assert.deepEqual(requests.slice(1).map(request => request.body), [
    { action: 'wind', incident_id: 'second', value: 270 },
    { action: 'fire_power', incident_id: 'second', value: 75 },
    { action: 'fire_power', incident_id: 'second', value: 0 },
  ]);
  assert.ok(requests.every(request => request.url === '/api/scenario'));
  assert.deepEqual(state, snapshot, 'no cambia el estado recibido del servidor');
  panel.handlers.keydown({ key: 'Escape', preventDefault() {} });
  assert.equal(panel.hidden, true); assert.equal(document.activeElement, button);
  editor.update({ session_id: 'other', operations: {} });
  assert.equal(get('scenario-random-cut').disabled, true); assert.equal(power.disabled, true);
  assert.match(get('scenario-edit-notice').textContent, /no disponible/);
  editor.update({ session_id: 'other' }); assert.equal(button.hidden, true);
});

test('el editor serializa órdenes, muestra errores y descarta respuestas de otra sesión', async () => {
  let resolve, count = 0;
  const { editor, get, state } = editorFixture(() => { count++; return new Promise(done => { resolve = done; }); });
  editor.update(state);
  const cut = get('scenario-random-cut'), status = get('scenario-edit-status');
  const pending = cut.onclick();
  assert.equal(cut.disabled, true); await cut.onclick(); assert.equal(count, 1);
  resolve({ ok: false, json: async () => ({ error: 'Hace falta una unidad de carretera en ruta' }) });
  await pending; assert.match(status.textContent, /Hace falta/); assert.equal(cut.disabled, false);
  const old = cut.onclick(); editor.update({ ...state, session_id: 'new' });
  resolve({ ok: true, json: async () => ({ ok: true }) }); await old;
  assert.equal(status.textContent, ''); assert.equal(cut.disabled, false);
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
