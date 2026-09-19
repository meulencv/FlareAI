import assert from 'node:assert/strict';
import test from 'node:test';
import { fetchImage } from '../server/network.ts';

test('image redirects are revalidated before the destination is requested', async t => {
  const destinations: string[] = [];
  const mock = t.mock.method(globalThis, 'fetch', async (url: string) => {
    destinations.push(url);
    return new Response(null, { status: 302, headers: { location: 'http://127.0.0.1/private' } });
  });
  await assert.rejects(fetchImage('http://mct.gencat.cat/mct2bo/RenderService?sctidcam=nc87.gif'), /no permitida/);
  assert.equal(mock.mock.callCount(), 1);
  assert.equal(destinations.length, 1);
});

test('SCT RenderService can redirect to its public TransitCamera endpoint', async t => {
  let count = 0;
  t.mock.method(globalThis, 'fetch', async (url: string) => {
    count++;
    if (count === 1) return new Response(null, { status: 302, headers: { location: '/mct2bo/TransitCamera?nom=nc87.gif' } });
    assert.equal(url, 'http://mct.gencat.cat/mct2bo/TransitCamera?nom=nc87.gif');
    return new Response('image', { headers: { 'content-type': 'image/gif' } });
  });
  const response = await fetchImage('http://mct.gencat.cat/mct2bo/RenderService?sctidcam=nc87.gif');
  assert.equal(await response.text(), 'image');
  assert.equal(count, 2);
});

test('redirect loops have a finite request budget', async t => {
  const mock = t.mock.method(globalThis, 'fetch', async () =>
    new Response(null, { status: 302, headers: { location: '/mct2bo/RenderService' } }));
  await assert.rejects(fetchImage('http://mct.gencat.cat/mct2bo/RenderService'), /Demasiadas/);
  assert.equal(mock.mock.callCount(), 4);
});
