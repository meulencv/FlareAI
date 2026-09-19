import express from 'express';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';
import { CatalogStore } from './catalog.ts';
import { allowedImage, fetchImage, getText, readLimited } from './network.ts';
import { parsePublicPlayer } from './sources.ts';

const app = express();
app.disable('x-powered-by');
const store = new CatalogStore();
await store.restore();

app.use((_req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});
app.get('/api/catalog', (_req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.json(store.data);
});
app.get('/api/health', (_req, res) => res.json({ cameras: store.data.cameras.length }));

interface ImageResult { bytes: Buffer; type: string; modified: string | null; fetched: string; expires: number }
const images = new Map<string, ImageResult>();
const pending = new Map<string, Promise<ImageResult>>();
const failures = new Map<string, number>();
let activeImages = 0;

async function getImage(id: string, url: string, seconds: number): Promise<ImageResult> {
  const saved = images.get(id);
  if (saved && saved.expires > Date.now()) return saved;
  const inProgress = pending.get(id);
  if (inProgress) return inProgress;
  if ((failures.get(id) || 0) > Date.now()) throw new Error('La cámara no responde. Reintenta en un minuto.');
  if (activeImages >= 8) throw new Error('Demasiadas imágenes en curso. Inténtalo de nuevo.');
  const job = (async () => {
    activeImages++;
    try {
      const response = await fetchImage(url);
      const type = response.headers.get('content-type')?.split(';')[0] || '';
      if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(type)) {
        await response.body?.cancel();
        throw new Error('El proveedor no ha devuelto una imagen');
      }
      const bytes = await readLimited(response, 5 * 1024 * 1024);
      const result: ImageResult = {
        bytes, type, modified: response.headers.get('last-modified'),
        fetched: new Date().toISOString(), expires: Date.now() + Math.max(30, seconds) * 1000,
      };
      if (images.size >= 40) images.delete(images.keys().next().value || '');
      images.set(id, result);
      return result;
    } catch (error) {
      if (failures.size >= 1000) failures.clear();
      failures.set(id, Date.now() + 60000);
      throw error;
    } finally {
      activeImages--;
      pending.delete(id);
    }
  })();
  pending.set(id, job);
  return job;
}

app.get('/api/cameras/:id/image', async (req, res) => {
  const camera = store.data.cameras.find(c => c.id === req.params.id);
  if (!camera?.imageUrl || !allowedImage(camera.imageUrl)) {
    res.status(404).json({ error: 'Imagen no disponible' }); return;
  }
  try {
    const image = await getImage(camera.id, camera.imageUrl, camera.refreshSeconds);
    res.setHeader('Cache-Control', 'private, max-age=30');
    res.setHeader('X-Fetched-At', image.fetched);
    if (image.modified) res.setHeader('X-Source-Last-Modified', image.modified);
    res.type(image.type).send(image.bytes);
  } catch {
    res.status(502).json({ error: 'La cámara no responde o no publica una imagen válida. Puedes abrir su fuente original.' });
  }
});

const players = new Map<string, { url: string | null; expires: number }>();
const pendingPlayers = new Map<string, Promise<string | null>>();
async function resolvePlayer(id: string, page: string): Promise<string | null> {
  const cached = players.get(id);
  if (cached && cached.expires > Date.now()) return cached.url;
  const pendingPlayer = pendingPlayers.get(id);
  if (pendingPlayer) return pendingPlayer;
  if (pendingPlayers.size >= 4) throw new Error('Demasiados reproductores en curso');
  const job = (async () => {
    try {
      const url = parsePublicPlayer(await getText(page));
      players.set(id, { url, expires: Date.now() + 3600000 });
      return url;
    } finally {
      pendingPlayers.delete(id);
    }
  })();
  pendingPlayers.set(id, job);
  return job;
}
app.get('/api/cameras/:id/player', async (req, res) => {
  const camera = store.data.cameras.find(c => c.id === req.params.id && c.source === 'hispa');
  if (!camera || !camera.pageUrl.startsWith('https://www.hispacams.com/webcams/')) {
    res.status(404).json({ error: 'Reproductor no encontrado' }); return;
  }
  try {
    res.json({ url: await resolvePlayer(camera.id, camera.pageUrl), pageUrl: camera.pageUrl });
  } catch {
    res.status(502).json({ error: 'No se pudo cargar el reproductor. Abre la página del proveedor.' });
  }
});

if (existsSync(resolve('dist/index.html'))) {
  app.use(express.static(resolve('dist')));
  app.get('/', (_req, res) => res.sendFile(resolve('dist/index.html')));
} else {
  app.get('/', (_req, res) => res.status(503).send('Ejecuta npm run build antes de iniciar Faro.'));
}
const port = Number(process.env.PORT || 3000);
app.listen(port, '0.0.0.0', () => console.log(`Faro listo en puerto ${port}`));
void store.refresh().catch(console.error);
setInterval(() => { void store.refresh().catch(console.error); }, 60000).unref();
