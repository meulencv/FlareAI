import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('./app.js', import.meta.url), 'utf8');

function page(ageSeconds, calibration = 'aligned', count = 2) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {textContent: '', disabled: false, addEventListener() {}, append() {}, replaceChildren() {}});
    return elements.get(id);
  };
  const now = Date.parse('2026-09-19T11:00:00Z');
  const context = vm.createContext({
    document: {getElementById: element}, setInterval() {}, setTimeout() {},
    fetch: async () => ({ok: true, json: async () => ({cameras: [], cloud_ready: true})}),
    TEST_NOW: now,
    EVIDENCE: {source: {mode: 'live', source_updated_at: new Date(now - ageSeconds * 1000).toISOString()},
      analyzed_at: new Date(now).toISOString(), captured_at: null, capture_time_verified: false,
      calibration: {status: calibration}, zones: [{vehicle_count: count}]},
  });
  vm.runInContext(source + '\nDate.now = () => TEST_NOW; cloudReady = true; observation = {evidence: EVIDENCE}; updateTime();', context);
  return {context, element};
}

test('unmatched view disables road-summary action', () => {
  const {element} = page(20, 'unverified');
  assert.equal(element('cloud').disabled, true);
  assert.match(element('captured').textContent, /NO VERIFICADA/);
  assert.doesNotMatch(element('source-badge').textContent, /IMAGEN RECIENTE/);
});

test('provider age above ten minutes expires without another request', () => {
  const {context, element} = page(599);
  assert.equal(element('cloud').disabled, false);
  vm.runInContext('TEST_NOW += 2000; updateTime();', context);
  assert.equal(element('cloud').disabled, true);
  assert.match(element('age').textContent, /CADUCADA/);
  assert.equal(vm.runInContext('observation.evidence.freshness', context), 'stale');
});

test('no vehicles detected is not sufficient to run road summary', () => {
  assert.equal(page(20, 'aligned', 0).element('cloud').disabled, true);
});

test('timestamp without timezone is not treated as recent', () => {
  const {context, element} = page(20);
  vm.runInContext("observation.evidence.source.source_updated_at = '2026-09-19T11:00:00'; updateTime();", context);
  assert.equal(element('cloud').disabled, true);
  assert.equal(element('updated').textContent, 'No verificada');
});

test('reset clears previous count and analysis timestamp', () => {
  const {context, element} = page(20);
  element('scene-count').textContent = '99';
  vm.runInContext('resetReadout()', context);
  assert.equal(element('scene-count').textContent, '—');
  assert.equal(element('analyzed').textContent, '—');
});
