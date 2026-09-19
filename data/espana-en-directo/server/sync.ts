import { CatalogStore } from './catalog.ts';

const store = new CatalogStore();
await store.restore();
await store.refresh(true);
console.log(`${store.data.cameras.length} cámaras en el catálogo.`);
if (store.data.sources.some(s => s.status !== 'ok')) process.exitCode = 1;
