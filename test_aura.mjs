import test from "node:test";
import assert from "node:assert/strict";
import { createAura, frameMetrics, perimeterLength, perimeterPoint, wavyFrame } from "./static/aura.js";

test("frameMetrics follows the Apple Intelligence frame bounds", () => {
  assert.deepEqual(frameMetrics(320, 568), { inset: 7, radius: 18 });
  assert.deepEqual(frameMetrics(2560, 1440), { inset: 11, radius: 30 });
});

test("perimeterPoint walks the rounded frame clockwise and wraps", () => {
  const at = t => perimeterPoint(t, 1000, 600, 10, 20);
  assert.deepEqual(at(0), { x: 30, y: 10 });
  assert.deepEqual(at(1), at(0));
  assert.deepEqual(at(-.25), at(.75));
  for (const t of [.1, .3, .6, .9]) { const p = at(t); assert.ok(p.x >= 10 && p.x <= 990 && p.y >= 10 && p.y <= 590); }
  assert.ok(Math.abs(perimeterLength(1000, 600, 10, 20) - (940 * 2 + 540 * 2 + Math.PI * 40)) < 1e-9);
});

test("wavyFrame stays within the amplitude of the straight frame and is almost straight", () => {
  const straight = wavyFrame(1000, 600, 10, 20, 0, 360, 0), wavy = wavyFrame(1000, 600, 10, 20, 2.5, 360, 100);
  assert.equal(straight.length, wavy.length);
  let maxOffset = 0;
  straight.forEach((p, i) => { maxOffset = Math.max(maxOffset, Math.hypot(p.x - wavy[i].x, p.y - wavy[i].y)); });
  assert.ok(maxOffset > 2 && maxOffset <= 2.5 + 1e-6, `ondulación de ${maxOffset}px`);
});

function fakeContainer() {
  const calls = [];
  const ctx = new Proxy({}, { get: (_, name) => (...args) => { calls.push([name, args]); } });
  const canvases = [0, 1, 2].map(() => ({ width: 0, height: 0, style: {}, getContext: () => ctx }));
  const classes = new Set();
  return { calls, classes, canvases, container: { querySelectorAll: () => canvases, classList: { toggle: (name, on) => classes[on ? "add" : "delete"](name) } } };
}

test("createAura blurs each layer with CSS (Safari has no canvas filter) and stops rendering when inactive, reduced or paused", () => {
  globalThis.window = { innerWidth: 800, innerHeight: 600, devicePixelRatio: 1, addEventListener() {} };
  globalThis.performance ??= { now: () => 0 };
  const { container, canvases, classes, calls } = fakeContainer();
  const reduced = { matches: false, addEventListener() {} };
  let pending = null, cancelled = 0;
  const aura = createAura(container, { reduced, requestFrame: fn => { pending = fn; return 1; }, cancelFrame: () => { cancelled++; pending = null; } });
  const run = t => { const fn = pending; pending = null; fn(t); };
  assert.deepEqual(canvases.map(c => c.style.filter), ["blur(45px)", "blur(30px)", "blur(24px)"]);
  assert.equal(aura.active, false);
  aura.set(true);
  assert.ok(classes.has("ai-active"));
  assert.equal(canvases[0].width, 800);
  run(16); assert.ok(pending, "keeps animating while active");
  assert.equal(calls.filter(([name]) => name === "stroke").length, 3, "glow + two waves per frame");
  assert.ok(!calls.some(([name]) => name === "filter"), "never relies on ctx.filter");
  reduced.matches = true; run(32); assert.equal(pending, null, "reduced motion renders a single still frame");
  reduced.matches = false; aura.set(false);
  assert.ok(!classes.has("ai-active"));
  aura.setPaused(true); aura.set(true); run(48); assert.equal(pending, null, "paused keeps a still frame");
  aura.set(false); assert.equal(cancelled, 0, "no frame pending to cancel");
});
