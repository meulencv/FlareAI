import { test } from "node:test";
import assert from "node:assert/strict";
import { scenario, destination, imagePoints } from "./static/simulation.js";
import { sample } from "./static/wind.js";

const incident = { lon: -2, lat: 42, footprint_ha: 100, weather: { wind_from_degrees: 270 } };

test("la procedencia y el desplazamiento son opuestos", () => {
  assert.equal(destination(270), 90);
  assert.equal(destination(0), 180);
  assert.equal(destination(null), null);
});
test("el escenario avanza al este si el viento viene del oeste", () => {
  const shape = scenario(incident, 3, .3);
  const xs = shape.coordinates[0].map(p => p[0]);
  assert.ok((Math.max(...xs) + Math.min(...xs)) / 2 > incident.lon);
  assert.equal(shape.coordinates[0].length, 81);
  assert.equal(incident.footprint_ha, 100);
});
test("sin horizonte o sin dirección no se inventa una proyección", () => {
  assert.equal(scenario(incident, 0, .3), null);
  assert.equal(scenario({ ...incident, weather: { wind_from_degrees: null } }, 2, .3), null);
  assert.throws(() => scenario(incident, 7, .3));
  assert.throws(() => scenario(incident, 2, NaN));
});
test("las detecciones se sitúan en la imagen con el norte arriba", () => {
  assert.deepEqual(imagePoints([{ lon: 0, lat: 1 }, { lon: 1, lat: 0 }, { lon: 5, lat: 0 }], [0, 0, 1, 1]),
    [{ x: 0, y: 0 }, { x: 900, y: 600 }]);
});
test("la interpolación de componentes evita saltos 0/360", () => {
  const grid = { west: 0, south: 0, step: 1, nx: 2, ny: 2,
    u: [-1, 1, -1, 1], v: [-10, -10, -10, -10], gust: [12, 12, 12, 12] };
  const result = sample([grid], .5, .5);
  assert.equal(result.from, 0);
  assert.equal(result.speed, 36);
});
