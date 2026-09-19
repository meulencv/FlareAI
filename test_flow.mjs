import { test } from "node:test";
import assert from "node:assert/strict";
import {
  budget, detailedOutline, emberBudget, expired, flameOutline, flicker, heatRadius, indexRings, inside,
  pointInPolygon, polygonArea, rings, spawn, stepParticle, visualSpeed, windStroke,
} from "./static/flow.js";

const bounds = { west: -3, east: -1, south: 41, north: 43 };
const square = [[[-3, 41], [-1, 41], [-1, 43], [-3, 43], [-3, 41]]];
const westerly = { u: 5, v: 0, speed: 20, from: 270 };

test("la partícula viaja hacia donde sopla el viento, no hacia su procedencia", () => {
  const start = { lon: -2, lat: 42, age: 0, life: 4, seed: 0, trail: [] };
  const moved = stepParticle(start, westerly, 1, 120);
  assert.ok(moved.lon > start.lon);
  assert.ok(Math.abs(moved.lat - start.lat) < 1e-6);
  assert.ok(Math.abs(moved.bearing - 90) < 1e-6);
  const north = stepParticle(start, { u: 0, v: 4, speed: 14, from: 180 }, 1, 120);
  assert.ok(north.lat > start.lat);
});

test("el índice geográfico conserva huecos e islas al otro lado de una celda", () => {
  const hole = [[-2.5, 41.5], [-1.5, 41.5], [-1.5, 42.5], [-2.5, 42.5], [-2.5, 41.5]];
  const shapes = [...square, hole, [[2, 41], [3, 41], [3, 42], [2, 42], [2, 41]]];
  const indexed = indexRings(shapes);
  for (const [lon, lat] of [[-2, 42], [-2.8, 42], [2.5, 41.5], [4, 40], [-3.01, 42]]) {
    assert.equal(indexed(lon, lat), pointInPolygon(shapes, lon, lat));
  }
  assert.equal(indexed(-2, 42), false);
  assert.equal(indexed(2.5, 41.5), true);
});

test("el detalle del borde está acotado y los trazos nacen con dirección sin historial de pantalla", () => {
  const points = [{ x: 0, y: 0 }, { x: 3000, y: 0 }, { x: 3000, y: 3000 }, { x: 0, y: 3000 }];
  const detail = detailedOutline(points);
  assert.equal(detail.length, 180);
  assert.ok(Math.abs(polygonArea(points) - polygonArea(detail)) < 1e-6);
  const stroke = windStroke({ lon: -2, lat: 42 }, westerly, 10);
  assert.equal(stroke.length, 2);
  assert.ok(stroke[0].lon < stroke[1].lon);
  assert.deepEqual(windStroke({ lon: -2, lat: 42 }, null, 10), []);
});
test("sin viento o en calma la partícula solo envejece", () => {
  const start = { lon: -2, lat: 42, age: 0, life: 4, seed: 0, trail: [] };
  for (const wind of [null, { u: 0, v: 0, speed: 0, from: null }, { u: 0, v: 0, speed: 0, from: 0 }]) {
    const moved = stepParticle(start, wind, 1, 120);
    assert.equal(moved.lon, start.lon);
    assert.equal(moved.lat, start.lat);
    assert.equal(moved.age, 1);
  }
});
test("la velocidad visual se acota y nunca es negativa", () => {
  assert.equal(visualSpeed(0, 10, .5), 10);
  assert.equal(visualSpeed(-40, 10, .5), 10);
  assert.equal(visualSpeed(NaN, 10, .5), 10);
  assert.equal(visualSpeed(500, 10, .5, 70), 45);
});
test("las partículas caducan por edad o al salir de la vista", () => {
  assert.ok(expired({ lon: -2, lat: 42, age: 5, life: 4 }, bounds));
  assert.ok(!expired({ lon: -2, lat: 42, age: 1, life: 4 }, bounds));
  assert.ok(expired({ lon: 6, lat: 42, age: 1, life: 4 }, bounds));
  assert.ok(inside({ lon: -1.1, lat: 41.2 }, bounds));
});
test("las semillas solo aparecen donde se aceptan y el presupuesto depende del área", () => {
  const random = () => .5;
  assert.equal(spawn(bounds, random, 4, () => false), null);
  const seed = spawn(bounds, random, 4, (lon, lat) => pointInPolygon(square, lon, lat));
  assert.ok(pointInPolygon(square, seed.lon, seed.lat));
  assert.ok(seed.age < seed.life);
  assert.ok(budget(1200, 800) > budget(600, 400));
  assert.equal(budget(9000, 9000), 520);
  assert.ok(emberBudget(9, true, 12) > emberBudget(9, false, 6));
  assert.ok(!pointInPolygon(square, 0, 42));
});
test("el fuego se dibuja sobre la huella real y se inclina con el viento", () => {
  const points = [{ x: -10, y: -10 }, { x: 10, y: -10 }, { x: 10, y: 10 }, { x: -10, y: 10 }];
  const calm = flameOutline(points, 0, null, 4);
  const leaning = flameOutline(points, 0, 90, 4);
  assert.equal(leaning.length, points.length);
  assert.ok(polygonArea(leaning) > polygonArea(points));
  assert.ok(Math.max(...leaning.map(p => p.x)) > Math.max(...calm.map(p => p.x)));
  assert.equal(polygonArea(flameOutline(points, 0, 90, 4)), polygonArea(leaning));
  assert.ok(Math.abs(flicker(1, 2)) <= 2);
  assert.ok(heatRadius(1, 1) >= 9 && heatRadius(1e9, 400) <= 150);
  assert.equal(rings({ type: "Polygon", coordinates: square }).length, 1);
  assert.equal(rings(null).length, 0);
});
