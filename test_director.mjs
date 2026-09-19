import { test } from "node:test";
import assert from "node:assert/strict";
import { routePosition, freshEvents, directorWarning, cinematicFrame, nearbyEvidence, patrolTargets, createCameraTour, createEvidenceView } from "./static/director.js";

import { notificationBatch } from './happyrobot-112/static/alerts.js';
import { preferredSpeaker, createSpeakerOutput } from './happyrobot-112/static/audio.js';

test('manos libres elige altavoz explícito, nunca inventa que el dispositivo default sea altavoz', () => {
  const device = (id, label) => ({ kind: 'audiooutput', deviceId: id, label });
  assert.equal(preferredSpeaker([device('default', 'Default - Speaker')]), null);
  assert.equal(preferredSpeaker([device('a', 'Headphones'), device('b', 'Earpiece Receiver')]), null);
  const speaker = device('speaker', 'Altavoz integrado');
  assert.equal(preferredSpeaker([device('default', 'Default - Speaker'), speaker]), speaker);
  assert.equal(preferredSpeaker([{ ...speaker, kind: 'audioinput' }]), null);
});

test('la voz usa una sola salida mezclada, selecciona altavoz y libera audio sin tocar el micrófono', async () => {
  const elements = [], statuses = [];
  let connections = 0, disconnected = 0, closed = 0, stopped = 0;
  function element() {
    return { dataset: {}, muted: false, setAttribute() {}, play: async () => {}, pause() {},
      setSinkId: async function(id) { this.sinkId = id; }, remove() { this.removed = true; } };
  }
  const document = { createElement: element, body: { append: node => elements.push(node) } };
  const window = {
    AudioContext: class {
      state = 'suspended';
      async resume() { this.state = 'running'; }
      createMediaStreamDestination() { return { stream: { getTracks: () => [{ stop: () => stopped++ }] } }; }
      createMediaStreamSource() { return { connect: () => connections++, disconnect: () => disconnected++ }; }
      async close() { closed++; }
    },
    MediaStream: class {},
    navigator: { mediaDevices: { enumerateDevices: async () => [{ kind: 'audiooutput', deviceId: 'speaker', label: 'Altavoz integrado' }],
      getUserMedia() { throw new Error('No debe tocar la captura del micrófono'); } } },
  };
  const output = createSpeakerOutput({ window, document, onStatus: (...args) => statuses.push(args), onDevices() {} });
  await output.prepare();
  const native = element(), track = { mediaStreamTrack: {}, attach: () => native, detach() {} };
  output.attach(track); await new Promise(resolve => setTimeout(resolve, 0));
  output.attach(track);
  assert.equal(connections, 1);
  assert.equal(native.muted, true, 'sin doble reproducción nativa y mezcla');
  await output.activate();
  assert.equal(elements[0].sinkId, 'speaker');
  assert.equal(statuses.at(-1)[1], true);
  output.close();
  assert.equal(closed, 1); assert.equal(stopped, 1); assert.equal(disconnected, 1);
  assert.ok(elements.every(e => e.removed));
});

test('los bloqueos del director tienen explicación persistente y no aparentan despacho', () => {
  for (const status of ['error', 'auth_required', 'unconfigured', 'standby', 'disconnected']) assert.ok(directorWarning(status));
  for (const status of ['idle', 'thinking', 'watching', 'disabled']) assert.equal(directorWarning(status), '');
  assert.match(directorWarning('error'), /Sin nuevos despachos/);
});

const point = (x, y) => ({ x, y });

test('el receptor no reproduce alertas antiguas, duplicadas, caducadas ni de otra sesión', () => {
  const payload = { session_id: 'a', sequence: 3, events: [
    { sequence: 1, kind: 'alert', expires_at: 110 },
    { sequence: 2, kind: 'alert', expires_at: 90 },
    { sequence: 3, kind: 'cancel', expires_at: 120 },
  ] };
  assert.deepEqual(notificationBatch(payload, null, 0, 100).events, []);
  assert.deepEqual(notificationBatch(payload, 'a', 1, 100).events, [payload.events[2]]);
  assert.deepEqual(notificationBatch(payload, 'a', 3, 100).events, []);
  assert.deepEqual(notificationBatch(payload, 'previous', 0, 100).events, []);
});

test("el viaje aleja, recorre y acerca de forma continua sin saltar al destino", () => {
  const start = { center: point(0, 0), zoom: 13 }, end = { center: point(100, 50), zoom: 12 };
  assert.deepEqual(cinematicFrame(start, end, 6, 0), start);
  assert.deepEqual(cinematicFrame(start, end, 6, 1), end);
  assert.equal(cinematicFrame(start, end, 6, .25).zoom, 6);
  assert.equal(cinematicFrame(start, end, 6, .5).center.x, 50);
  assert.equal(cinematicFrame(start, end, 6, .75).zoom, 6);
  for (const boundary of [.25, .75]) {
    const before = cinematicFrame(start, end, 6, boundary - .00001);
    const after = cinematicFrame(start, end, 6, boundary + .00001);
    assert.ok(Math.abs(before.zoom - after.zoom) < .001);
    assert.ok(Math.abs(before.center.x - after.center.x) < .001);
  }
});

test("las evidencias usan detecciones cercanas, no centroides ni llamadas como NASA", () => {
  const report = { id: "call", lat: 41, lon: 1, source_kind: "call", observations: 0 };
  const nasa = { id: "nasa", lat: 43, lon: 3, observations: 2, detections: [{ lat: 41.01, lon: 1 }] };
  const remote = { ...nasa, id: "far", lat: 41, lon: 1, detections: [{ lat: 43, lon: 3 }] };
  const camera = { id: "camera", lat: 41.02, lon: 1, kind: "snapshot" };
  const original = JSON.stringify([report, nasa, remote, camera]);
  const result = nearbyEvidence(report, [report, remote, nasa], [camera, { ...camera, id: "external", kind: "link" }]);
  assert.equal(result.thermal.incident.id, "nasa");
  assert.ok(result.thermal.distance_km < 2);
  assert.equal(result.camera.item.id, "camera");
  assert.deepEqual(nearbyEvidence(report, [report, remote], [{ ...camera, lat: 50 }]), { thermal: null, camera: null });
  assert.equal(JSON.stringify([report, nasa, remote, camera]), original);
});

test("la ronda visita avisos y vehículos activos, nunca detecciones sin llamada ni retornos antiguos", () => {
  const report = { id: "a", demo_report: {}, lat: 41, lon: 1 };
  const assignments = { truck: { resource: { id: "truck" }, incident_id: "a", status: "enroute" }, done: { resource: { id: "done" }, status: "onscene" } };
  assert.deepEqual(patrolTargets([report, { id: "b" }], assignments).map(t => t.key), ["incident:a", "vehicle:truck"]);
  assert.deepEqual(patrolTargets([], {}), []);
});

test("interrumpir un viaje cancela el siguiente fotograma; movimiento reducido no anima", () => {
  let callback, views = [], canceled = 0;
  const map = { getCenter: () => ({ lat: 41, lng: 1 }), getZoom: () => 13, getMinZoom: () => 4,
    getMaxZoom: () => 16, getSize: () => point(1000, 800), stop() {},
    getBoundsZoom: () => 8, project: p => point(p.lng, p.lat), unproject: p => [p.y, p.x],
    setView: (center, zoom) => views.push({ center, zoom }) };
  const L = { latLngBounds: () => ({}), point, latLng: p => Array.isArray(p) ? { lat: p[0], lng: p[1] } : p };
  const tour = createCameraTour({ map, L, now: () => 0, requestFrame: fn => { callback = fn; return 1; }, cancelFrame: () => canceled++ });
  tour.go([42, 2], 12);
  callback(500);
  assert.ok(views[0].zoom < 13);
  const stale = callback;
  tour.cancel(); stale(5000);
  assert.equal(views.length, 1, "un fotograma ya cancelado no recupera el control");
  assert.equal(canceled, 1);
  assert.equal(tour.moving(), false);
  views = [];
  tour.go([42, 2], 12, true);
  assert.deepEqual(views, [{ center: [42, 2], zoom: 12 }]);
  assert.equal(tour.moving(), false);
});

function evidenceHarness(fetch, incidents = [], cameras = []) {
  function node(tag = "div") {
    return { tag, children: [], text: "", className: "", hidden: false,
      get textContent() { return this.text + this.children.map(c => c.textContent).join(" "); },
      set textContent(value) { this.text = value; this.children = []; },
      set src(value) { this.url = value; this.onload?.(); },
      append(...children) { children.forEach(c => { c.parent = this; this.children.push(c); }); },
      replaceChildren(...children) { this.children = []; this.text = ""; this.append(...children); },
      remove() { if (this.parent) this.parent.children = this.parent.children.filter(c => c !== this); },
      setAttribute() {},
      querySelector(selector) { return this.children.find(c => c.className === selector.slice(1)) || this.children.map(c => c.querySelector(selector)).find(Boolean); },
    };
  }
  const elements = new Map();
  const document = { getElementById(id) { if (!elements.has(id)) elements.set(id, node()); return elements.get(id); }, createElement: node, createElementNS: (_, tag) => node(tag) };
  const payload = { status: "offline", incidents };
  const view = createEvidenceView({ document, fetch, getData: () => payload, getCameras: () => cameras, openCamera() {} });
  return { view, get: document.getElementById, payload };
}
const settle = () => new Promise(resolve => setTimeout(resolve, 0));
const report = { id: "report", name: "Aviso", lat: 41, lon: 1, source_kind: "call", weather: { air_temperature_c: 0 } };
const thermal = { id: "thermal", name: "Señal", observations: 2, lat: 41, lon: 1, detections: [{ lat: 41, lon: 1 }], brightness_i4_c: 80, brightness_i4_k: 353.15, brightness_at_utc: "2026-09-18T10:00:00Z" };

test("sin coincidencias se omite GIBS y no se convierte falta de cobertura en rechazo", async () => {
  const urls = [], h = evidenceHarness(async url => { urls.push(url); });
  const original = JSON.stringify(report);
  h.view.show(report); await settle();
  assert.deepEqual(urls, []);
  assert.match(h.get("evidence-facts").textContent, /0 °C/);
  assert.match(h.get("evidence-satellite").textContent, /no se descarta/);
  assert.match(h.get("evidence-camera").textContent, /Sin cámaras verificadas/);
  assert.equal(JSON.stringify(report), original);
  h.view.hide();
});

test("evidencias fechadas, fallo de cámara tolerado y cierre invalida respuestas tardías", async () => {
  const pending = [], camera = { id: "cam", name: "Cámara", lat: 41, lon: 1, kind: "snapshot" };
  const h = evidenceHarness((url, options) => new Promise(resolve => pending.push({ url, options, resolve })), [thermal], [camera]);
  h.view.show(report);
  assert.equal(pending.length, 2);
  assert.match(h.get("evidence-facts").textContent, /80 °C eq/);
  assert.match(h.get("evidence-status").textContent, /HISTÓRICA/);
  pending[1].resolve({ ok: false }); await settle();
  assert.match(h.get("evidence-camera").textContent, /La llamada sigue activa/);
  h.view.hide();
  assert.equal(pending[0].options.signal.aborted, true);
  pending[0].resolve({ ok: true, json: async () => ({ url: `/satellite/${"a".repeat(24)}.png`, date: "2026-09-18" }) });
  await settle();
  assert.equal(h.get("agent-evidence").hidden, true);
  assert.equal(h.get("evidence-satellite").children.length, 0);
});

test("un cambio de zona descarta respuestas antiguas y mantiene ambas llamadas intactas", async () => {
  let resolve;
  const h = evidenceHarness(() => new Promise(done => { resolve = done; }), [thermal]);
  h.view.show(report);
  const next = { ...report, id: "other", name: "Otro aviso", lat: 43, lon: -3 };
  h.view.show(next);
  resolve({ ok: true, json: async () => ({ url: `/satellite/${"a".repeat(24)}.png`, date: "2026-09-18" }) }); await settle();
  assert.equal(h.get("evidence-title").textContent, next.name);
  assert.match(h.get("evidence-satellite").textContent, /Sin detecciones FIRMS/);
  assert.equal(h.payload.incidents[0], thermal);
  h.view.hide();
});

test("una corrección de ubicación con el mismo ID no reutiliza el mosaico anterior", async () => {
  const urls = [], otherThermal = { ...thermal, id: "other", lat: 42, detections: [{ lat: 42, lon: 1 }] };
  const h = evidenceHarness(async url => { urls.push(url); return { ok: true, json: async () => ({ url: `/satellite/${"a".repeat(24)}.png`, date: "2026-09-18" }) }; }, [thermal, otherThermal]);
  h.view.show(report); await settle();
  h.view.show(report); await settle();
  assert.equal(urls.length, 1, "revisar la misma ubicación utiliza la caché breve");
  h.view.show({ ...report, lat: 42 }); await settle();
  assert.equal(urls.length, 2, "una corrección obliga a consultar la imagen de la nueva ubicación");
  h.view.hide();
});

test("rechaza URLs de medios ajenas a los proxies locales y no inventa confirmación", async () => {
  const h = evidenceHarness(async () => ({ ok: true, json: async () => ({ url: "https://example.org/incorrect.png" }) }), [thermal]);
  h.view.show(report); await settle();
  assert.match(h.get("evidence-satellite").textContent, /sin validación por imagen/);
  h.view.hide();
});

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
