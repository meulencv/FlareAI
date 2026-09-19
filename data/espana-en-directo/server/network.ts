import { setTimeout } from 'node:timers/promises';

const USER_AGENT = 'FaroWebcams/1.0 (public webcam directory; source attribution in /api/catalog)';
const MAX_BYTES = 12 * 1024 * 1024;

export async function readLimited(response: Response, maxBytes = MAX_BYTES): Promise<Buffer> {
  if (!response.ok) {
    await response.body?.cancel();
    throw new Error(`HTTP ${response.status}`);
  }
  if (Number(response.headers.get('content-length') || 0) > maxBytes) {
    await response.body?.cancel();
    throw new Error('Respuesta demasiado grande');
  }
  const parts: Uint8Array[] = [];
  let size = 0;
  if (!response.body) throw new Error('Respuesta vacía');
  const reader = response.body.getReader();
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.length;
      if (size > maxBytes) throw new Error('Respuesta demasiado grande');
      parts.push(value);
    }
  } finally {
    await reader.cancel();
  }
  return Buffer.concat(parts);
}

export async function getText(url: string): Promise<string> {
  for (let attempt = 0; ; attempt++) {
    try {
      const response = await fetch(url, {
        headers: { 'User-Agent': USER_AGENT },
        signal: AbortSignal.timeout(25000),
      });
      return (await readLimited(response)).toString('utf8');
    } catch (error) {
      if (attempt >= 1) throw error;
      await setTimeout(1500);
    }
  }
}

export async function getJson(url: string): Promise<unknown> {
  return JSON.parse(await getText(url)) as unknown;
}

const imageRules: Record<string, RegExp> = {
  'etraffic.dgt.es': /^\/camarasEtraffic\/[\w-]+\.jpg$/,
  'informo.madrid.es': /^\/cameras\/Camara\d+\.jpg$/,
  'www.meteogalicia.gal': /^\/datosred\/camaras\/[\w/.-]+\.(jpg|jpeg|png)$/,
  'www.trafikoa.eus': /^\/static\/files\/tr\/camaras\/\d+\.jpg$/,
  'www.trafikoa.net': /^\/static\/files\/tr\/camaras\/\d+\.jpg$/,
  'www.bilbao.eus': /^\/camarastrafico\/[\w/-]+\.jpg$/,
  'mct.gencat.cat': /^\/mct2bo\/(RenderService|TransitCamera)$/,
  'emap.terrassa.cat': /^\/it_terrassa\/cam\d+\.jpeg$/,
  'www.bcn.cat': /^\/transit\/imatges\/[\w-]+\.gif$/,
};

export function allowedImage(url: string): boolean {
  try {
    const u = new URL(url);
    return !u.username && !u.password && !u.port
      && (u.protocol === 'https:' || (u.protocol === 'http:' && ['mct.gencat.cat', 'www.bcn.cat'].includes(u.hostname)))
      && Boolean(imageRules[u.hostname]?.test(u.pathname));
  } catch {
    return false;
  }
}

export async function fetchImage(url: string): Promise<Response> {
  const signal = AbortSignal.timeout(14000);
  let target = url;
  for (let redirects = 0; redirects <= 3; redirects++) {
    if (!allowedImage(target)) throw new Error('URL de imagen no permitida');
    const response = await fetch(target, { redirect: 'manual', signal, headers: { 'User-Agent': USER_AGENT } });
    if (![301, 302, 303, 307, 308].includes(response.status)) return response;
    const location = response.headers.get('location');
    await response.body?.cancel();
    if (!location) throw new Error('Redirección sin destino');
    target = new URL(location, target).href;
  }
  throw new Error('Demasiadas redirecciones');
}

export function allowedPlayer(url: string): boolean {
  try {
    const u = new URL(url);
    return u.protocol === 'https:' && !u.username && !u.password && !u.port
      && (
        (u.hostname === 'rtsp.me' && /^\/embed\/[a-zA-Z0-9]+\/?$/.test(u.pathname))
        || (['www.youtube.com', 'www.youtube-nocookie.com'].includes(u.hostname)
          && /^\/embed\/[a-zA-Z0-9_-]{11}$/.test(u.pathname))
      );
  } catch {
    return false;
  }
}
