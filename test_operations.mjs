import test from 'node:test';
import assert from 'node:assert/strict';
import process from 'node:process';
import { testimonyRows } from './static/operations.js';
import { GET, POST } from './happyrobot-112/cloud/route.js';

const { Request, Response } = globalThis;
const room = '00000000-0000-4000-8000-000000000001';

test('el feed distingue webcall de testimonios sintéticos y conserva sus evaluaciones', () => {
  const rows = testimonyRows([{ citizen: { id: 'real', at: 1, source: 'webcall' }, testimonies: [{ id: 'demo', at: 2, source: 'synthetic_demo' }], assessment: { testimonies: [{ id: 'demo', status: 'uncertain' }] } }]);
  assert.equal(rows[0].id, 'demo');
  assert.equal(rows[0].assessment.status, 'uncertain');
  assert.equal(rows[1].source, 'webcall');
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
