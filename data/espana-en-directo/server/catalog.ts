import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { type Catalog, catalogSchema } from '../src/model.ts';
import { adapters } from './sources.ts';

export class CatalogStore {
  data: Catalog;
  private refreshing = false;

  constructor(private readonly sources = adapters, private readonly path = resolve('data/catalog.json')) {
    this.data = { cameras: [], sources: sources.map(a => ({ ...a.info })) };
  }

  async restore(): Promise<void> {
    try {
      const raw: unknown = JSON.parse(await readFile(this.path, 'utf8'));
      const saved = catalogSchema.parse(raw);
      this.data = {
        cameras: saved.cameras.filter(c => this.sources.some(a => a.info.id === c.source)),
        sources: this.sources.map(a => ({ ...a.info, ...saved.sources.find(s => s.id === a.info.id) })),
      };
    } catch {
      console.log('Sin catálogo previo. Sincronizando fuentes públicas…');
    }
  }

  async refresh(force = false): Promise<void> {
    if (this.refreshing) return;
    this.refreshing = true;
    try {
      await Promise.all(this.sources.map(async adapter => {
        const previous = this.data.sources.find(s => s.id === adapter.info.id) || adapter.info;
        const interval = previous.status === 'error' ? 300000 : adapter.interval;
        if (!force && previous.checkedAt && Date.now() - Date.parse(previous.checkedAt) < interval) return;
        try {
          const result = await adapter.run();
          if (!result.cameras.length) throw new Error('El catálogo no contiene cámaras válidas');
          this.data.cameras = this.data.cameras.filter(c => c.source !== adapter.info.id).concat(result.cameras);
          this.data.sources = this.data.sources.map(s => s.id === adapter.info.id ? {
            ...adapter.info, status: 'ok', count: result.cameras.length, excluded: result.excluded,
            checkedAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
          } : s);
          console.log(`${adapter.info.name}: ${result.cameras.length} cámaras, ${result.excluded} excluidas`);
        } catch (error) {
          const detail = error instanceof Error ? error.message : 'Error de conexión';
          this.data.sources = this.data.sources.map(s => s.id === adapter.info.id ? {
            ...s, status: 'error', error: detail.slice(0, 220), checkedAt: new Date().toISOString(),
          } : s);
          console.error(`${adapter.info.name}: ${detail}`);
        }
      }));
      await mkdir(dirname(this.path), { recursive: true });
      await writeFile(`${this.path}.tmp`, JSON.stringify(this.data));
      await rename(`${this.path}.tmp`, this.path);
    } finally {
      this.refreshing = false;
    }
  }
}
