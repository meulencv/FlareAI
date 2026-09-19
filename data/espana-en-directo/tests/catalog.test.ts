import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdir, mkdtemp, readFile, rm } from 'node:fs/promises';
import { resolve } from 'node:path';
import { CatalogStore } from '../server/catalog.ts';
import { type Camera, catalogSchema, type Source } from '../src/model.ts';

const camera: Camera = {
  id: 'fixture-1', source: 'fixture', name: 'Example', place: 'Madrid',
  lat: 40.4, lon: -3.7, category: 'traffic', kind: 'snapshot', refreshSeconds: 300,
  pageUrl: 'https://informo.madrid.es/', imageUrl: 'https://informo.madrid.es/cameras/Camara06303.jpg',
};
const info: Source = {
  id: 'fixture', name: 'Fixture', url: 'https://example.com', license: 'Test',
  licenseUrl: 'https://example.com', note: 'Test', status: 'pending', count: 0, excluded: 0,
};

test('failed sync preserves catalog and last successful timestamp across restart', async t => {
  await mkdir(resolve('data'), { recursive: true });
  const dir = await mkdtemp(resolve('data/test-'));
  t.after(() => rm(dir, { recursive: true }));
  let fail = false;
  let calls = 0;
  const adapter = { info, interval: 3600000, run: async () => {
    calls++;
    if (fail) throw new Error('Provider unavailable');
    return { cameras: [camera], excluded: 1 };
  } };
  const path = resolve(dir, 'catalog.json');
  const store = new CatalogStore([adapter], path);
  await store.refresh(true);
  const updatedAt = store.data.sources[0].updatedAt;
  assert.equal(store.data.sources[0].status, 'ok');
  await store.refresh();
  assert.equal(calls, 1, 'successful sources respect their refresh interval');
  fail = true;
  await store.refresh(true);
  assert.deepEqual(store.data.cameras, [camera]);
  assert.equal(store.data.sources[0].status, 'error');
  assert.equal(store.data.sources[0].updatedAt, updatedAt);
  const restored = new CatalogStore([adapter], path);
  await restored.restore();
  assert.deepEqual(restored.data, store.data);
  catalogSchema.parse(JSON.parse(await readFile(path, 'utf8')));
});

test('concurrent refreshes are coalesced and empty responses cannot erase cameras', async t => {
  await mkdir(resolve('data'), { recursive: true });
  const dir = await mkdtemp(resolve('data/test-'));
  t.after(() => rm(dir, { recursive: true }));
  let calls = 0;
  let empty = false;
  const adapter = { info, interval: 1, run: async () => {
    calls++;
    return { cameras: empty ? [] : [camera], excluded: 0 };
  } };
  const store = new CatalogStore([adapter], resolve(dir, 'catalog.json'));
  await Promise.all([store.refresh(true), store.refresh(true)]);
  assert.equal(calls, 1);
  empty = true;
  await store.refresh(true);
  assert.deepEqual(store.data.cameras, [camera]);
  assert.equal(store.data.sources[0].status, 'error');
});
