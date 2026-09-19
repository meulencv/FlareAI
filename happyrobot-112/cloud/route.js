import { createHash, createHmac, randomUUID, timingSafeEqual } from 'node:crypto';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const COOKIE = 'flare_cloud';
const API = 'https://platform.eu.happyrobot.ai/api/v2';
const quote = value => "'" + String(value).replaceAll("'", "''") + "'";
const jsonSql = value => quote(JSON.stringify(value)) + '::jsonb';
const idValid = value => typeof value === 'string' && /^[0-9a-f-]{36}$/i.test(value);

function response(value, status = 200, headers = {}) {
  return Response.json(value, { status, headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', ...headers } });
}
function equal(a, b) {
  const first = createHash('sha256').update(String(a)).digest(), second = createHash('sha256').update(String(b)).digest();
  return timingSafeEqual(first, second);
}
function encodeSession(data) {
  const body = Buffer.from(JSON.stringify(data)).toString('base64url');
  return body + '.' + createHmac('sha256', process.env.DEMO_COOKIE_SECRET).update(body).digest('base64url');
}
function session(request) {
  const value = (request.headers.get('cookie') || '').split(';').map(s => s.trim()).find(s => s.startsWith(COOKIE + '='))?.slice(COOKIE.length + 1);
  if (!value || value.length > 2048 || !process.env.DEMO_COOKIE_SECRET) return null;
  try {
    const [body, signature] = value.split('.');
    if (!equal(signature, createHmac('sha256', process.env.DEMO_COOKIE_SECRET).update(body).digest('base64url'))) return null;
    const data = JSON.parse(Buffer.from(body, 'base64url').toString());
    return idValid(data.owner) && data.expires > Date.now() ? data : null;
  } catch { return null; }
}
async function happyrobot(path, method = 'GET', body = undefined, twin = false) {
  const key = twin ? process.env.TWIN_API_KEY : process.env.HAPPYROBOT_API_KEY;
  if (!key) throw new Error('CONFIGURATION');
  const result = await fetch(API + path, { method, headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(20000), cache: 'no-store' });
  if (!result.ok) throw new Error('PROVIDER');
  return result.json();
}
async function sql(statement) {
  const result = await happyrobot('/twin/sql', 'POST', { sql: statement }, true);
  if (result.truncated || !Array.isArray(result.rows)) throw new Error('PARTIAL');
  return result.rows;
}
async function room() {
  const rows = await sql("SELECT data FROM flare_live_documents WHERE id='active-room'");
  const value = rows[0]?.data;
  return value && idValid(value.session_id) && Date.now() / 1000 - value.heartbeat_at < 45 ? value : null;
}
function ownerHash(owner) { return createHash('sha256').update(owner).digest('hex'); }
async function ownedCall(run, active, auth) {
  if (!idValid(run)) return null;
  const rows = await sql(`SELECT data FROM flare_live_calls WHERE id=${quote(run)} AND session_id=${quote(active.session_id)} AND owner_hash=${quote(ownerHash(auth.owner))}`);
  return rows[0]?.data || null;
}

export async function GET(request) {
  try {
    const url = new URL(request.url), route = url.pathname.split('/').filter(Boolean).at(-1);
    const configured = Boolean(process.env.HAPPYROBOT_API_KEY && process.env.TWIN_API_KEY && process.env.HAPPYROBOT_WORKFLOW_ID && process.env.DEMO_ACCESS_CODE && process.env.DEMO_COOKIE_SECRET?.length >= 32);
    if (!configured) return response({ configured: false, browser_ready: false }, route === 'status' ? 200 : 503);
    const active = await room(), auth = session(request);
    if (route === 'status') return response({ configured: Boolean(active), browser_ready: Boolean(active && auth?.session === active.session_id), integrated: true, cloud: true });
    if (!active) return response({ error: 'El centro local no está conectado. Abre FlareAI en el ordenador.' }, 503);
    if (!auth || auth.session !== active.session_id) return response({ error: 'Abre el marcador desde el enlace de la sala.' }, 403);
    if (route === 'brief') {
      const call = await ownedCall(url.searchParams.get('run_id'), active, auth);
      if (!call) return response({ error: 'Llamada no disponible' }, 404);
      return response({ status: call.state || 'waiting', summary: call.summary || {}, map_status: call.state || 'waiting',
        location: call.location || null, role: 'citizen', updated_at: call.updated_at || call.reported_at });
    }
    if (route === 'alerts') {
      const after = url.searchParams.has('after') ? Number(url.searchParams.get('after')) : null;
      if (after !== null && (!Number.isInteger(after) || after < 0 || after > 1000000)) return response({ error: 'Secuencia no válida' }, 400);
      const rows = await sql(`SELECT data->'notifications' AS events,data->'delivery_sequence' AS sequence FROM flare_live_state WHERE session_id=${quote(active.session_id)}`);
      return response({ session_id: active.session_id, sequence: rows[0]?.sequence || 0, mode: 'simulation_only',
        events: (rows[0]?.events || []).filter(e => after !== null && e.sequence > after && e.expires_at > Date.now() / 1000) });
    }
    return response({ error: 'Ruta no disponible' }, 404);
  } catch { return response({ error: 'HappyRobot o Twin no están disponibles. Reintenta sin iniciar otra llamada.' }, 503); }
}

export async function POST(request) {
  try {
    const url = new URL(request.url), route = url.pathname.split('/').filter(Boolean).at(-1);
    if (request.headers.get('origin') !== url.origin) return response({ error: 'Origen no permitido' }, 403);
    const raw = await request.text();
    if (Buffer.byteLength(raw) > 4096) return response({ error: 'Solicitud demasiado grande' }, 413);
    const body = JSON.parse(raw || '{}'), active = await room(), auth = session(request);
    if (!active) return response({ error: 'El centro local no está conectado.' }, 503);
    if (route === 'session') {
      if (!process.env.DEMO_COOKIE_SECRET || process.env.DEMO_COOKIE_SECRET.length < 32 || !process.env.DEMO_ACCESS_CODE) return response({ error: 'Configuración incompleta' }, 503);
      if (!auth && !equal(body.access_code || '', process.env.DEMO_ACCESS_CODE)) return response({ error: 'Abre este marcador desde el enlace privado del centro.' }, 403);
      const value = encodeSession({ owner: auth?.owner || randomUUID(), session: active.session_id, expires: Date.now() + 21600000 });
      return response({ ready: true }, 200, { 'Set-Cookie': `${COOKIE}=${value}; Path=/112/; HttpOnly; Secure; SameSite=Strict; Max-Age=21600` });
    }
    if (!auth || auth.session !== active.session_id) return response({ error: 'Sesión no válida; recarga el marcador.' }, 403);
    if (route === 'stop') {
      if (!await ownedCall(body.run_id, active, auth)) return response({ error: 'Llamada no disponible' }, 404);
      await sql(`UPDATE flare_live_calls SET ended_at=(now() AT TIME ZONE 'UTC') WHERE id=${quote(body.run_id)} AND owner_hash=${quote(ownerHash(auth.owner))}`);
      return response({ ok: true });
    }
    if (route !== 'call' || body.number !== '112' || !idValid(body.request_id)) return response({ error: 'Solo se admite la webcall 112.' }, 400);
    const owner = ownerHash(auth.owner), reservation = (await sql(`SELECT flare_live_reserve_web_v1(${quote(active.session_id)},${quote(owner)},${quote(body.request_id)}) AS result`))[0]?.result;
    if (!reservation?.created) return reservation?.status === 'ready' ? response(reservation.data) : response({ error: 'Hay un inicio pendiente. No se repite para evitar llamadas duplicadas.' }, 409);
    let token;
    try {
      token = await happyrobot('/voice/tokens/', 'POST', { workflow_id: process.env.HAPPYROBOT_WORKFLOW_ID, env: 'production', ttl_seconds: 1800,
        data: { source: 'flareai-cloud-112', demo_session: active.session_id, role: 'citizen' } });
      if (!idValid(token.run_id) || typeof token.token !== 'string' || typeof token.url !== 'string') throw new Error('INVALID_TOKEN');
    } catch {
      await sql(`UPDATE flare_live_web_requests SET status='uncertain' WHERE id=${quote(body.request_id)} AND owner_hash=${quote(owner)}`);
      return response({ error: 'No se pudo confirmar el inicio; revisa la sala antes de repetir.' }, 503);
    }
    const result = { run_id: token.run_id, url: token.url, token: token.token, room_name: token.room_name };
    const call = { role: 'citizen', state: 'waiting', summary: {}, location: null, reported_at: new Date().toISOString(), source: 'cloud_webcall' };
    await sql(`INSERT INTO flare_live_calls(id,session_id,owner_hash,data) VALUES(${quote(token.run_id)},${quote(active.session_id)},${quote(owner)},${jsonSql(call)}) ON CONFLICT(id) DO NOTHING`);
    await sql(`UPDATE flare_live_web_requests SET status='ready',run_id=${quote(token.run_id)},data=${jsonSql(result)} WHERE id=${quote(body.request_id)} AND owner_hash=${quote(owner)}`);
    return response(result);
  } catch { return response({ error: 'No se pudo completar la solicitud. Puede haber otra llamada activa; comprueba la sala antes de repetir.' }, 503); }
}
