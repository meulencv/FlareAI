import { test } from "node:test";
import assert from "node:assert/strict";
import { routePosition, freshEvents } from "./static/director.js";

test("los vehículos recorren distancias y no saltan por densidad de vértices", () => {
  const route = { coordinates: [[0, 40], [.001, 40], [.1, 40]], cumulative_km: [0, 1, 100] };
  assert.deepEqual(routePosition(route, 0), [0, 40]);
  assert.deepEqual(routePosition(route, 1), [.1, 40]);
  assert.deepEqual(routePosition(route, -1), [0, 40]);
  assert.deepEqual(routePosition(route, 2), [.1, 40]);
  assert.ok(Math.abs(routePosition(route, .5)[0] - .05) < .00001);
});

test("el feed no repite acciones ni reproduce decisiones antiguas tras reconectar", () => {
  const events = [{ sequence: 1, at: 1 }, { sequence: 2, at: 100 }, { sequence: 3, at: 110 }];
  assert.deepEqual(freshEvents(events, 1, 120), events.slice(1));
  assert.deepEqual(freshEvents(events, 3, 120), []);
  assert.deepEqual(freshEvents(events, 0, 500), []);
});
