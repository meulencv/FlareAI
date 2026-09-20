import { test } from "node:test";
import assert from "node:assert/strict";
import { routePosition, freshEvents, directorWarning, cinematicFrame, nearbyEvidence, patrolTargets, createCameraTour, createEvidenceView, createRouteRehearsal } from "./static/director.js";

import { notificationBatch, createAlertReceiver } from './happyrobot-112/static/alerts.js';
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

test('el director no anuncia informes aunque el backend los siga generando', () => {
  const events = [{ sequence: 1, at: 100, kind: 'return' }, { sequence: 2, at: 101, kind: 'report_ready' }];
  assert.deepEqual(freshEvents(events, 0, 102), [events[0]]);
  assert.equal(events.length, 2);
});

test('los bloqueos del director tienen explicación persistente y no aparentan despacho', () => {
  for (const status of ['error', 'auth_required', 'unconfigured', 'standby', 'disconnected']) assert.ok(directorWarning(status));
  for (const status of ['idle', 'thinking', 'watching', 'disabled']) assert.equal(directorWarning(status), '');
  assert.match(directorWarning('error'), /Sin nuevos despachos/);
});

const rehearsalAssignment = (id = 'truck') => ({ id: `assignment-${id}`, resource: { id, kind: 'fire_engine', name: `Unidad ${id}` },
  incident_id: 'fire', status: 'enroute', started_at: 0, travel_seconds: 1000, route_revision: 1,
  route: { coordinates: [[2, 41], [2.01, 41.01]], cumulative_km: [0, 1] } });

function rehearsalHarness(random = () => 0) {
  const rehearsal = createRouteRehearsal({ random }), assignment = rehearsalAssignment();
  const input = { assignments: { truck: assignment }, enabled: true, busy: false, visible: () => true };
  return { rehearsal, assignment, input, step: (now, extra = {}) => rehearsal.step({ ...input, now, ...extra }) };
}

test('el recálculo visual es esporádico, selecciona una unidad y no modifica rutas ni tiempos', () => {
  const h = rehearsalHarness(); h.assignment.travel_seconds = 45;
  const original = JSON.stringify(h.input.assignments);
  assert.equal(h.step(0), null);
  assert.equal(h.step(11), null);
  const start = h.step(12);
  assert.equal(start.kind, 'route_rehearsal');
  assert.equal(start.resource_id, 'truck');
  assert.match(start.message, /Viento cambiado.*simulación.*recalculando/i);
  assert.match(start.reason, /no modifica/i);
  assert.equal(h.rehearsal.active.resource_id, 'truck');
  assert.equal(h.step(17), null);
  assert.match(h.step(18).message, /Ruta revisada.*simulación/);
  assert.equal(h.rehearsal.active, null);
  assert.equal(JSON.stringify(h.input.assignments), original);
  h.assignment.travel_seconds = 1000;
  assert.equal(h.step(62), null);
  assert.ok(h.step(63));
});

test('el ensayo de acceso no crea coches decorativos ni modifica la ruta', () => {
  const h = rehearsalHarness(() => .5), original = JSON.stringify(h.assignment.route);
  h.step(0);
  const event = h.step(18);
  assert.match(event.message, /Revisión de acceso.*simulación/);
  assert.equal(h.rehearsal.active.obstruction, undefined);
  assert.equal(JSON.stringify(h.assignment.route), original);
  h.step(24);
  assert.equal(h.rehearsal.active, null);
});

test('varía la cadencia, el motivo y la unidad sin encadenar ráfagas', () => {
  const h = rehearsalHarness(() => .999);
  h.input.assignments.other = rehearsalAssignment('other');
  h.step(0);
  assert.equal(h.step(23), null);
  const event = h.step(24);
  assert.equal(event.resource_id, 'other');
  assert.match(event.message, /Acceso alternativo/);
  assert.ok(h.step(30));
  assert.equal(h.step(119), null);
  assert.ok(h.step(120));
});

test('no simula en vacío, fuera de pantalla, al llegar, en vuelo o con ruta aproximada', () => {
  for (const change of [a => a.status = 'onscene', a => a.status = 'blocked', a => a.status = 'returning',
    a => a.started_at = 100, a => a.travel_seconds = 40, a => a.resource.kind = 'helicopter',
    a => a.route.approximate = true, a => a.route.coordinates = []]) {
    const h = rehearsalHarness(); change(h.assignment); h.step(0);
    assert.equal(h.step(35), null);
    assert.equal(h.rehearsal.active, null);
  }
  const h = rehearsalHarness(); h.step(0);
  assert.equal(h.step(35, { visible: () => false }), null);
  assert.equal(h.step(100, { assignments: {} }), null);
});

test('pausa, desconexión y decisiones reales cancelan el efecto sin publicar un éxito ficticio', () => {
  for (const extra of [{ enabled: false }, { busy: true }, { assignments: {} }]) {
    const h = rehearsalHarness(); h.step(0); assert.ok(h.step(35));
    assert.equal(h.step(36, extra), null);
    assert.equal(h.rehearsal.active, null);
    assert.equal(h.step(41), null);
  }
  const h = rehearsalHarness(); h.step(0); h.step(35);
  h.assignment.route_revision++;
  assert.equal(h.step(41), null);
  assert.equal(h.rehearsal.active, null);
  h.rehearsal.reset();
  assert.equal(h.step(200), null);
});

function receiverHarness() {
  const elements = new Map(), oscillators = [], gains = [], requests = [];
  const $ = id => {
    if (!elements.has(id)) elements.set(id, { textContent: '', hidden: true, disabled: false, focus() {} });
    return elements.get(id);
  };
  const document = { getElementById: $, body: { dataset: {} }, addEventListener() {} };
  const param = () => ({ values: [], setValueAtTime(value, at) { this.values.push([value, at]); },
    linearRampToValueAtTime(value, at) { this.values.push([value, at]); } });
  const audio = { state: 'suspended', currentTime: 10, destination: {},
    async resume() { this.state = 'running'; this.onstatechange?.(); },
    createOscillator() {
      const node = { frequency: param(), connect() {}, disconnect() { this.disconnected = true; },
        start(at) { this.started = at; }, stop(at) { this.stopped = at; } };
      oscillators.push(node); return node;
    },
    createGain() {
      const node = { gain: param(), connect() {}, disconnect() { this.disconnected = true; } };
      gains.push(node); return node;
    },
  };
  let payload = { session_id: 'test', sequence: 0, events: [] };
  const window = { AudioContext: function() { return audio; }, navigator: { audioSession: {} },
    addEventListener() {}, setInterval() { return 1; }, clearInterval() {} };
  const receiver = createAlertReceiver({ document, window, fetch: async url => {
    requests.push({ url, tones: oscillators.length });
    return { ok: true, json: async () => payload };
  } });
  const deliver = async (kind = 'alert') => {
    payload = { session_id: 'test', sequence: payload.sequence + 1, events: [{ sequence: payload.sequence + 1,
      kind, incident_id: 'fire', message: 'Alerta de prueba', at: Date.now() / 1000, expires_at: Date.now() / 1000 + 60 }] };
    await receiver.poll();
  };
  return { $, document, window, audio, oscillators, gains, requests, receiver, deliver };
}

test('el receptor prueba el sonido fuerte antes de la red y permite repetir la prueba', async () => {
  const h = receiverHarness();
  await h.$('activate-alerts').onclick();
  assert.equal(h.requests[0].tones, 1, 'la activación debe reproducir un tono, no solo reanudar un contexto vacío');
  assert.equal(h.window.navigator.audioSession.type, 'playback');
  assert.equal(h.$('activate-alerts').disabled, false);
  assert.ok(Math.abs(h.oscillators[0].stopped - h.oscillators[0].started - .8) < 1e-9);
  assert.ok(h.gains[0].gain.values.some(([value]) => value >= .8));
  assert.ok(h.gains[0].gain.values.every(([value]) => value <= 1));
  await h.$('activate-alerts').onclick();
  assert.equal(h.oscillators.length, 2);
  assert.equal(h.requests.filter(r => r.url === '/112/api/session').length, 1);
  h.receiver.stop();
});

test('el receptor conserva el aviso de audio suspendido y lo recupera desde la alerta', async () => {
  const h = receiverHarness();
  await h.$('activate-alerts').onclick();
  h.audio.state = 'interrupted'; h.audio.onstatechange?.();
  await h.deliver(); await h.receiver.poll();
  assert.equal(h.$('received-alert').hidden, false);
  assert.equal(h.$('retry-alert-sound').hidden, false);
  assert.match(h.$('alert-sound-status').textContent, /suspendido/i);
  await h.$('retry-alert-sound').onclick();
  assert.equal(h.audio.state, 'running');
  assert.equal(h.document.body.dataset.sounding, 'true');
  assert.equal(h.$('retry-alert-sound').hidden, true);
  const tone = h.oscillators.at(-1);
  assert.equal(tone.stopped - tone.started, 8);
  const count = h.oscillators.length;
  await h.receiver.poll();
  assert.equal(h.oscillators.length, count, 'un refresco no vuelve a sonar');
  h.$('ack-alert').onclick();
  assert.equal(tone.disconnected, true);
  assert.equal(h.document.body.dataset.sounding, 'false');
  h.receiver.stop();
});

test('la cancelación y el final natural liberan el sonido de la alerta', async () => {
  const h = receiverHarness();
  await h.$('activate-alerts').onclick(); await h.deliver();
  const tone = h.oscillators.at(-1), gain = h.gains.at(-1);
  tone.onended();
  assert.ok(tone.disconnected && gain.disconnected);
  assert.equal(h.document.body.dataset.sounding, 'false');
  await h.deliver('cancel');
  assert.equal(h.$('received-alert').hidden, true);
  await h.deliver();
  const next = h.oscillators.at(-1);
  await h.deliver('cancel');
  assert.equal(next.disconnected, true);
  h.receiver.stop();
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

test('la cámara se acerca a las calles junto al camión y respeta detención y movimiento reducido', async () => {
  const { vehicleCameraView } = await import('./static/director.js');
  const assignment = rehearsalAssignment();
  const view = vehicleCameraView(assignment, 500);
  assert.equal(view.zoom, 15.5);
  assert.ok(Math.abs(view.center[0] - 41.005) < 1e-9 && Math.abs(view.center[1] - 2.005) < 1e-9);
  assert.deepEqual(vehicleCameraView(assignment, 500, true).center, [41, 2]);
  assignment.held_position = [2.003, 41.002];
  assert.deepEqual(vehicleCameraView(assignment, 500).center, [41.002, 2.003]);
  assignment.resource.kind = 'helicopter';
  assert.equal(vehicleCameraView(assignment, 500).zoom, 14);
});

test("la ronda visita avisos y vehículos activos, nunca detecciones sin llamada ni retornos antiguos", () => {
  const report = { id: "a", demo_report: {}, lat: 41, lon: 1 };
  const assignments = { truck: { resource: { id: "truck" }, incident_id: "a", status: "enroute" }, done: { resource: { id: "done" }, status: "onscene" } };
  assert.deepEqual(patrolTargets([report, { id: "b" }], assignments).map(t => t.key), ["incident:a", "vehicle:truck"]);
  assert.deepEqual(patrolTargets([], {}), []);
});

test('la ronda sigue ambulancias en traslado y regresos, pero no unidades ya en destino', () => {
  const assignments = Object.fromEntries(['enroute', 'transporting', 'returning', 'onscene', 'blocked'].map(status =>
    [status, { ...rehearsalAssignment(status), status }]));
  assert.deepEqual(patrolTargets([], assignments).map(t => t.key), ['vehicle:enroute', 'vehicle:transporting', 'vehicle:returning']);
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
