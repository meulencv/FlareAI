import { selectionBounds } from "./context.js";
import { imagePoints } from "./simulation.js";
import { safeLink } from "./infrastructure.js";
import { createSceneView } from './scene.js';
import { createOperationView } from './operations.js';
import { createAura } from "./aura.js";

const smooth = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };

export function cinematicFrame(start, end, overview, progress) {
  const travel = smooth((progress - .25) / .5);
  return { center: { x: start.center.x + (end.center.x - start.center.x) * travel,
    y: start.center.y + (end.center.y - start.center.y) * travel },
  zoom: progress < .25 ? start.zoom + (overview - start.zoom) * smooth(progress / .25)
    : overview + (end.zoom - overview) * smooth((progress - .75) / .25) };
}

export function createCameraTour({ map, L, now = () => performance.now(), requestFrame = requestAnimationFrame, cancelFrame = cancelAnimationFrame }) {
  let frame = 0, generation = 0;
  function cancel() { generation++; if (frame) cancelFrame(frame); frame = 0; if (Number.isFinite(map.getZoom())) map.stop(); }
  function go(center, zoom, reduced = false) {
    cancel();
    const target = L.latLng(center), origin = map.getCenter();
    zoom = Math.max(map.getMinZoom(), Math.min(map.getMaxZoom(), zoom));
    if (reduced) { map.setView(center, zoom, { animate: false }); return; }
    const start = { center: map.project(origin, 0), zoom: map.getZoom() }, end = { center: map.project(target, 0), zoom };
    const distance = Math.hypot(start.center.x - end.center.x, start.center.y - end.center.y) * 2 ** Math.min(start.zoom, zoom);
    if (distance < 16 && Math.abs(start.zoom - zoom) < .15) return;
    const overview = distance < 80 ? Math.min(start.zoom, zoom)
      : Math.max(map.getMinZoom(), Math.min(start.zoom, zoom, map.getBoundsZoom(L.latLngBounds([origin, target]), false, L.point(160, 180))) - .7);
    const duration = distance < 80 ? 900 : 2400, token = generation;
    let previous = now(), elapsed = 0, lastPaint = -Infinity;
    function tick(timestamp) {
      if (token !== generation) return;
      elapsed += Math.max(0, Math.min(50, timestamp - previous)); previous = timestamp;
      const progress = Math.min(1, elapsed / duration);
      // setView dispara la reproyección de todas las capas Leaflet. A 60 Hz saturaba
      // especialmente pantallas Retina; 30 Hz mantiene el viaje suave y deja tiempo
      // de CPU a los canvas y a la interacción.
      if (progress === 1 || timestamp - lastPaint >= 32) {
        const view = cinematicFrame(start, end, overview, progress);
        map.setView(map.unproject(L.point(view.center.x, view.center.y), 0), view.zoom, { animate: false });
        lastPaint = timestamp;
      }
      frame = progress < 1 ? requestFrame(tick) : 0;
    }
    frame = requestFrame(tick);
  }
  function bounds(points, maxZoom = 12.5, reduced = false) {
    const bounds = L.latLngBounds(points), size = map.getSize();
    go(bounds.getCenter(), Math.min(maxZoom, map.getBoundsZoom(bounds, false, L.point(Math.min(180, size.x * .3), Math.min(220, size.y * .3)))), reduced);
  }
  return { go, bounds, cancel, moving: () => Boolean(frame) };
}

function distanceKm(a, b) {
  if (![a.lat, a.lon, b.lat, b.lon].every(Number.isFinite)) return Infinity;
  const rad = Math.PI / 180, dlat = (b.lat - a.lat) * rad, dlon = (b.lon - a.lon) * rad;
  const h = Math.sin(dlat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dlon / 2) ** 2;
  return 12742 * Math.asin(Math.min(1, Math.sqrt(h)));
}

export function nearbyEvidence(incident, incidents, cameras) {
  const origin = incident.demo_report?.location || incident;
  const thermal = incidents.filter(i => i.source_kind !== "call" && i.observations > 0)
    .map(i => ({ incident: i, distance_km: Math.min(...(i.detections || []).map(d => distanceKm(origin, d))) }))
    .filter(i => i.distance_km <= 10).sort((a, b) => a.distance_km - b.distance_km)[0] || null;
  const camera = cameras.filter(c => ["snapshot", "player"].includes(c.kind))
    .map(item => ({ item, distance_km: distanceKm(origin, item) }))
    .filter(c => c.distance_km <= 10).sort((a, b) => a.distance_km - b.distance_km)[0] || null;
  return { thermal, camera };
}

export function patrolTargets(incidents, assignments) {
  return [...incidents.filter(i => (i.demo_report && !i.demo_report.cancelled || i.sensor_report || i.scene_report) && i.scenario?.phase !== 'closed' && !i.scenario?.linked_call_id).map(i => ({ key: `incident:${i.id}`, incident: i })),
    ...Object.values(assignments).filter(a => ["enroute", "transporting", "returning"].includes(a.status))
      .map(a => ({ key: `vehicle:${a.resource.id}`, assignment: a }))];
}

export function routePosition(route, progress) {
  const points = route.coordinates, distances = route.cumulative_km;
  const target = Math.max(0, Math.min(1, progress)) * distances.at(-1);
  let low = 1, high = distances.length - 1;
  while (low < high) {
    const mid = Math.floor((low + high) / 2);
    if (distances[mid] < target) low = mid + 1; else high = mid;
  }
  const span = distances[low] - distances[low - 1];
  const fraction = span ? (target - distances[low - 1]) / span : 1;
  return points[low].map((value, axis) => points[low - 1][axis] + (value - points[low - 1][axis]) * fraction);
}

export function vehicleCameraView(assignment, now, reduced = false) {
  const progress = reduced ? (assignment.status === 'onscene' ? 1 : 0) : (now - assignment.started_at) / assignment.travel_seconds;
  const [lon, lat] = assignment.held_position || routePosition(assignment.route, progress);
  return { center: [lat, lon], zoom: assignment.resource.kind === 'helicopter' ? 14 : 15.5 };
}

export function engagedStations(stations, assignments) {
  const engaged = new Set(Object.values(assignments || {}).map(a => `${a.resource?.station_id}:${a.resource?.kind}`));
  return (stations || []).filter(station => engaged.has(`${station.station_id}:${station.kind}`));
}

export function freshEvents(events, sequence, now) {
  return events.filter(event => event.kind !== 'report_ready' && event.sequence > sequence && now - event.at < 90);
}

export function createRouteRehearsal({ random = Math.random } = {}) {
  let active = null, nextAt = null;
  const delay = (minimum, spread) => minimum + random() * spread;
  function eligible(a, now) {
    return a?.status === 'enroute' && a.resource.kind !== 'helicopter' && !a.route.approximate
      && a.route.coordinates.length > 1 && now >= a.started_at && a.started_at + a.travel_seconds - now > 10;
  }
  function step({ assignments, now, enabled, busy, visible }) {
    if (!enabled) { active = null; nextAt = null; return null; }
    if (busy) {
      if (active) { active = null; nextAt = now + delay(45, 45); }
      return null;
    }
    if (active) {
      const a = assignments[active.resource_id];
      if (!eligible(a, now) || a.id !== active.assignment_id || a.route_revision !== active.revision) {
        active = null; nextAt = now + delay(45, 45); return null;
      }
      if (now < active.until) return null;
      const event = { ...active.event, at: now, message: 'Ruta revisada · simulación',
        reason: `${a.resource.name} · ensayo visual completado; se conserva el itinerario asignado, sin cambiar la ETA ni enviar órdenes.` };
      active = null; nextAt = now + delay(45, 45);
      return event;
    }
    if (!Object.values(assignments).some(a => eligible(a, now))) { nextAt = null; return null; }
    if (nextAt === null) { nextAt = now + delay(12, 12); return null; }
    if (now < nextAt) return null;
    const candidates = Object.values(assignments).filter(a => eligible(a, now) && visible(a));
    nextAt = now + delay(45, 45);
    if (!candidates.length) return null;
    const a = candidates[Math.floor(random() * candidates.length)];
    const reason = ['Viento cambiado', 'Revisión de acceso', 'Acceso alternativo'][Math.floor(random() * 3)];
    const event = { kind: 'route_rehearsal', visual: true, at: now, resource_id: a.resource.id, incident_id: a.incident_id,
      message: `${reason} · simulación · recalculando ruta`,
      reason: `${a.resource.name} · ensayo visual aleatorio, no una observación ni una decisión del LLM. No modifica el viento, la ruta ni los tiempos del servidor.` };
    active = { resource_id: a.resource.id, assignment_id: a.id, revision: a.route_revision, until: now + 6, event };
    return event;
  }
  return { step, get active() { return active; }, reset() { active = null; nextAt = null; } };
}

export function directorWarning(status) {
  return {
    error: 'Director temporalmente no disponible · reintento automático. Sin nuevos despachos hasta recuperar la conexión.',
    auth_required: 'Director sin autenticación · revisa la conexión con HappyRobot. No se están generando nuevos despachos.',
    unconfigured: 'Director no configurado · las llamadas no pueden movilizar recursos.',
    standby: 'Director esperando el control de la sala · otro servidor o un reinicio reciente conserva el turno. Reintento automático.',
    disconnected: 'Sin conexión con el servidor · el mapa conserva el último estado recibido.',
  }[status] || '';
}

export function createEvidenceView({ document, fetch, getData, getCameras, openCamera }) {
  const $ = id => document.getElementById(id), cache = new Map();
  const number = value => Number.isFinite(value) ? value.toLocaleString("es-ES", { maximumFractionDigits: 1 }) : "—";
  const date = value => value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleString("es-ES", { timeZone: "UTC" }) + " UTC" : "fecha no disponible";
  let generation = 0, controller = null, expires = 0;
  function hide() {
    generation++; controller?.abort(); controller = null; expires = 0;
    $("agent-evidence").hidden = true;
    $("evidence-satellite").replaceChildren(); $("evidence-camera").replaceChildren();
  }
  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text) element.textContent = text;
    if (className) element.className = className;
    return element;
  }
  async function json(url, signal, key = url) {
    const saved = cache.get(key);
    if (saved && Date.now() - saved.at < 60000) return saved.value;
    const response = await fetch(url, { signal: globalThis.AbortSignal.any([signal, globalThis.AbortSignal.timeout(20000)]) });
    if (!response.ok) throw new Error("Fuente no disponible");
    const value = await response.json();
    if (cache.size > 32) cache.delete(cache.keys().next().value);
    cache.set(key, { at: Date.now(), value });
    return value;
  }
  function image(root, url, alt, caption, token, detections = null, bbox = null) {
    const wrap = node("div", null, "evidence-image"), img = node("img"), note = node("p", "Cargando imagen…");
    img.alt = alt;
    img.onload = () => {
      if (token !== generation) return;
      note.textContent = caption; wrap.append(img);
      if (detections && bbox) {
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 900 600"); svg.setAttribute("aria-hidden", "true");
        svg.innerHTML = imagePoints(detections, bbox).filter(p => p.x >= 0 && p.x <= 900 && p.y >= 0 && p.y <= 600)
          .map(p => `<circle cx="${p.x}" cy="${p.y}" r="6"/>`).join("");
        wrap.append(svg);
      }
    };
    img.onerror = () => { if (token === generation) { wrap.replaceChildren(); note.textContent = "Imagen no disponible. El aviso se mantiene."; } };
    root.append(wrap, note); img.src = url;
  }
  async function satellite(incident, thermal, token, signal, mode = "swir") {
    const root = $("evidence-satellite");
    root.replaceChildren(node("h3", "NASA GIBS · " + (mode === "swir" ? "infrarrojo SWIR" : "color natural")));
    if (!thermal) { root.append(node("p", "Sin detecciones FIRMS a ≤10 km en los datos disponibles. Se omite la imagen; no se descarta el aviso.")); return; }
    root.append(node("p", "Consultando mosaico satelital…", "evidence-loading"));
    try {
      const url = `/api/satellite?id=${encodeURIComponent(incident.id)}&mode=${mode}`;
      const picture = await json(url, signal, `${url}|${incident.lat}|${incident.lon}`);
      if (token !== generation || signal.aborted) return;
      if (!/^\/satellite\/[a-f0-9]{24}\.png$/.test(picture.url)) throw new Error("Imagen inválida");
      root.querySelector(".evidence-loading")?.remove();
      const detections = (getData()?.incidents || []).flatMap(i => i.detections || []);
      image(root, picture.url, `NASA ${mode} · ${incident.name}`, `${picture.date} · mosaico diario, no directo. Puntos: detecciones, no confirmación por imagen.`, token, detections, picture.bbox);
      const button = node("button", mode === "swir" ? "Ver color natural" : "Ver infrarrojo SWIR");
      button.onclick = () => { expires = Date.now() + 30000; satellite(incident, thermal, token, signal, mode === "swir" ? "natural" : "swir"); };
      root.append(button);
    } catch {
      if (token === generation && !signal.aborted) { root.querySelector(".evidence-loading")?.remove(); root.append(node("p", "Sin mosaico disponible. Continuamos con el aviso, sin validación por imagen.")); }
    }
  }
  async function camera(match, token, signal) {
    const root = $("evidence-camera");
    root.replaceChildren(node("h3", "Cámara cercana · revisión visual"));
    if (!match) { root.append(node("p", "Sin cámaras verificadas disponibles a ≤10 km. No implica ausencia de incendio.")); return; }
    const item = match.item;
    root.append(node("p", `${item.name} · ${item.source} · ${number(match.distance_km)} km del aviso`));
    if (item.kind === "player") {
      const button = node("button", "Abrir vídeo del proveedor");
      button.onclick = () => openCamera(item);
      root.append(button, node("p", "Requiere abrir el reproductor; puede usar cookies. No se ha analizado el contenido del vídeo."));
      return;
    }
    try {
      const result = await json(`/api/webcam?id=${encodeURIComponent(item.id)}`, signal);
      if (token !== generation || signal.aborted) return;
      if (result.verification_pending || result.kind !== "snapshot" || !/^\/territorial\/[a-f0-9]{24}\.img$/.test(result.url)) throw new Error("Captura no disponible");
      image(root, result.url, `Captura de ${item.name}`, `${result.offline ? "Copia offline. " : ""}Recuperada ${date(result.fetched_at)}. ${result.source_modified ? `Modificada en origen ${date(result.source_modified)}. ` : ""}Recuperación no es hora de captura; no se infiere fuego ni tráfico.`, token);
      const href = safeLink(item.pageUrl);
      if (href) { const link = node("a", "Fuente y autoría"); link.href = href; link.target = "_blank"; link.rel = "noopener noreferrer"; root.append(link); }
    } catch {
      if (token === generation && !signal.aborted) root.append(node("p", "Captura no disponible. La llamada sigue activa."));
    }
  }
  function show(incident) {
    hide(); controller = new globalThis.AbortController();
    const token = generation, signal = controller.signal, payload = getData() || {};
    const { thermal, camera: nearbyCamera } = nearbyEvidence(incident, payload.incidents || [], getCameras());
    $("agent-evidence").hidden = false; expires = Date.now() + 30000;
    $("evidence-title").textContent = incident.demo_report?.location?.label || incident.name;
    $("evidence-status").textContent = payload.status === "offline" ? "MUESTRA HISTÓRICA · SIN CONEXIÓN" : payload.status !== "ready" ? "FUENTES SIN ACTUALIZAR · CONSULTA LAS FECHAS" : "REVISIÓN AUTOMÁTICA DE FUENTES";
    const facts = $("evidence-facts"); facts.replaceChildren();
    const location = incident.demo_report?.location;
    if (location) facts.append(node("p", `${location.approximate || location.precision === 'locality' ? 'Ubicación aproximada' : 'Punto localizado'} · ${location.reason || 'Según ubicación comunicada.'} ${location.source || ''} ${location.attribution || ''}`));
    if (thermal) {
      const i = thermal.incident;
      facts.append(node("p", `NASA FIRMS · detección a ${number(thermal.distance_km)} km. ${i.observations} observaciones en el grupo · última ${date(i.last_seen)}.`));
      facts.append(node("p", `Brillo I4 máximo del grupo: ${number(i.brightness_i4_c)} °C eq. (${number(i.brightness_i4_k)} K), ${date(i.brightness_at_utc)}. No es temperatura de las llamas ni del aire.`));
    } else facts.append(node("p", "NASA FIRMS · sin coincidencia cercana en esta ventana. La ausencia de detección no invalida la llamada."));
    const w = incident.weather || {};
    facts.append(node("p", `NOAA GFS · ambiente a 2 m: ${number(w.air_temperature_c)} °C · viento ${number(w.wind_speed_kmh)} km/h. Modelo, no sensor local. Validez ${date(w.valid_at_utc)} · ciclo ${date(w.model_run_utc)}.`));
    satellite(incident, thermal, token, signal); camera(nearbyCamera, token, signal);
  }
  return { show, hide, tick(now) { if (expires && now > expires) hide(); } };
}

const VEHICLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 6h12v12H2zM14 11h4l4 4v3h-8M5 3h7M5 9h6m-6 3h6"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></svg>';

const AMBULANCE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 7h13l6 6v5H2zM7 9v6m-3-3h6M15 8v5h5"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></svg>';

const HELICOPTER = '<svg viewBox="0 0 32 28" aria-hidden="true"><path class="rotor" d="M3 4h26"/><path d="M16 4v5M12 9h8l7 7v4H9l-5-7H1M9 16h17M12 20v4m10-4v4M8 25h19M18 10v6"/></svg>';

export function createDirectorView({ map, L, document, fetch, focus, clearContext, findIncident, getData, getCameras, openCamera, beforeMove }) {
  const operationView = createOperationView({ document, fetch, map, L, findIncident });
  const $ = id => document.getElementById(id);
  const routes = L.layerGroup().addTo(map), stations = L.layerGroup().addTo(map), alerts = L.layerGroup().addTo(map);
  const vehicles = new Map(), rehearsal = createRouteRehearsal(), rehearsalLayer = L.layerGroup().addTo(map);
  const rehearsalRenderer = L.svg({ pane: 'response-routes' });
  let rehearsalKey = null;
  map.createPane("response-routes"); map.getPane("response-routes").style.zIndex = 420;
  map.createPane("response-vehicles"); map.getPane("response-vehicles").style.zIndex = 425;
  map.attributionControl.addAttribution('Rutas OSM/OSRM y caché local © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> · <a href="https://www.openstreetmap.org/fixthemap" target="_blank" rel="noopener">Corregir mapa</a>');
  let state = null, session = null, sequence = 0, loading = false, paused = false, frame = 0, offset = 0, lastVisualTick = 0;
  let queue = [], current = null, shownUntil = 0, lastContact = 0, contextUntil = 0, routeKey = "";
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const cameraTour = createCameraTour({ map, L });
  const aura = createAura($("agent-aura"), { reduced });
  const evidence = createEvidenceView({ document, fetch, getData, getCameras, openCamera: item => { manual(); openCamera(item); } });
  let following = true, armed = false, nextVisit = 0, lastTarget = "", lastEvidence = "", evidenceAt = 0;
  const sceneView = createSceneView({ map, L, document, fetch, findIncident,
    focus: id => { const incident = findIncident(id); if (incident) { manual(); focus(incident); map.setView([incident.lat, incident.lon], 15.5, { animate: false }); } } });
  map.on('zoom', () => { if (!state?.scenario || map.getZoom() >= 11) stations.addTo(map); else stations.remove(); });

  function followControl() {
    $("follow-toggle").textContent = following ? "Seguimiento IA · activo" : "Reanudar seguimiento IA";
    $("follow-toggle").setAttribute("aria-pressed", String(following));
  }
  function manual() {
    following = false; contextUntil = 0; cameraTour.cancel(); evidence.hide(); followControl();
  }
  function visit(incident, review = false) {
    beforeMove(); focus(incident);
    cameraTour.bounds(selectionBounds(incident), 15.5, reduced.matches);
    contextUntil = Date.now() + 45000; lastTarget = `incident:${incident.id}`;
    if (review && (lastEvidence !== incident.id || Date.now() - evidenceAt > 60000)) {
      evidence.show(incident); lastEvidence = incident.id; evidenceAt = Date.now();
    } else if (lastEvidence !== incident.id) evidence.hide();
  }
  function followVehicle(assignment) {
    beforeMove(); evidence.hide();
    const view = vehicleCameraView(assignment, (Date.now() + offset) / 1000, reduced.matches);
    cameraTour.go(view.center, view.zoom, reduced.matches);
    lastTarget = `vehicle:${assignment.resource.id}`;
  }
  // Solo el título de la decisión, abajo en el centro; la explicación vive en el historial.
  // Cada título nuevo reinicia la animación de entrada; salir quita la clase y CSS hace el fundido.
  function caption(message) {
    const text = $("agent-message");
    text.textContent = message;
    text.style.animation = "none"; void text.offsetWidth; text.style.animation = "";
    $("agent-card").classList.add("is-visible");
  }
  const hideCaption = () => $("agent-card").classList.remove("is-visible");
  function show(event) {
    current = event;
    shownUntil = Date.now() + ({ thinking: 1800, report: 6500, focus: 5000, context: 5000 }[event.kind] || 5500);
    nextVisit = shownUntil + 10000;
    caption(event.message);
    const incident = findIncident(event.incident_id);
    if (incident || event.resource_id) armed = true;
    if (!following || paused) return;
    if (incident && ["report", "focus", "context", "watch", "arrived", "field_report"].includes(event.kind)) visit(incident, ["report", "context", "watch"].includes(event.kind));
    if (event.resource_id && ["dispatch", "reassign", "return", "vehicle"].includes(event.kind)) {
      const assignment = state?.assignments?.[event.resource_id];
      if (assignment) followVehicle(assignment);
    }
  }
  function patrol() {
    const targets = patrolTargets(getData()?.incidents || [], state?.assignments || {});
    if (!targets.length) { armed = false; return; }
    const target = targets[(targets.findIndex(t => t.key === lastTarget) + 1) % targets.length];
    if (target.incident) show({ kind: "watch", visual: true, incident_id: target.incident.id, message: `Revisando ${(target.incident.demo_report?.location?.label || target.incident.name)}`, reason: "Seguimiento del aviso y consulta de fuentes disponibles; no es una nueva decisión del agente." });
    else show({ kind: "vehicle", visual: true, resource_id: target.assignment.resource.id, message: "Seguimiento de recursos en movimiento", reason: `${target.assignment.resource.name} · trayecto de demostración, tiempo acelerado` });
  }
  $("follow-toggle").onclick = () => {
    if (following) manual();
    else { following = true; lastEvidence = ""; nextVisit = 0; followControl(); }
  };
  $("evidence-close").onclick = () => evidence.hide();
  reduced.addEventListener("change", () => cameraTour.cancel());
  followControl();

  function renderAssignments() {
    const assignments = Object.values(state.assignments || {});
    const key = JSON.stringify([assignments.map(a => [a.id, a.status, a.route_revision]), state.stations]);
    if (key === routeKey) return;
    routeKey = key; routes.clearLayers(); stations.clearLayers();
    const active = new Set(assignments.map(a => a.resource.id));
    for (const [id, vehicle] of vehicles) if (!active.has(id)) { vehicle.marker.remove(); vehicles.delete(id); }
    const bases = new Map();
    for (const assignment of assignments) {
      const resource = assignment.resource, police = resource.kind === "police", helicopter = resource.kind === 'helicopter', ambulance = resource.kind === 'ambulance';
      if (assignment.previous_route) L.polyline(assignment.previous_route.coordinates.map(([lon, lat]) => [lat, lon]), { pane: 'response-routes', color: '#a9aeb8', weight: 3, opacity: .45, dashArray: '3 7', interactive: false }).addTo(routes);
      const route = L.polyline(assignment.route.coordinates.map(([lon, lat]) => [lat, lon]), {
        pane: "response-routes", color: assignment.status === 'blocked' ? '#a9aeb8' : helicopter ? "#7b78c9" : police ? "#789bc5" : ambulance ? '#4b9e80' : "#e88578", weight: 3, opacity: assignment.status === 'blocked' ? .2 : assignment.status === "onscene" ? .25 : .75, interactive: false,
        dashArray: assignment.status === 'blocked' ? '2 8' : helicopter ? "3 9" : assignment.status === "returning" ? "5 7" : null,
      }).addTo(routes);
      const base = bases.get(resource.station_id) || { resource, count: 0 }; base.count++; bases.set(resource.station_id, base);
      if (!vehicles.has(resource.id)) {
        const marker = L.marker([resource.lat, resource.lon], { pane: "response-vehicles", title: resource.name,
          icon: L.divIcon({ className: `response-vehicle ${helicopter ? "helicopter" : police ? "police" : ambulance ? 'ambulance' : "fire-engine"}`, html: helicopter ? HELICOPTER : ambulance ? AMBULANCE : VEHICLE, iconSize: [30, 28], iconAnchor: [15, 14] }) }).addTo(map);
        vehicles.set(resource.id, { marker, assignment, route, lastPoint: null });
      } else Object.assign(vehicles.get(resource.id), { assignment, route });
      const label = document.createElement("span");
      label.textContent = `${helicopter ? "Helicóptero · vuelo ilustrativo" : police ? "Patrulla" : ambulance ? 'Ambulancia' : "Camión"} · ${resource.name} · ${assignment.status === 'blocked' ? 'detenido · vía cortada' : assignment.status === 'transporting' ? 'traslado a hospital' : assignment.status === "onscene" ? "en el punto de encuentro" : assignment.status === "returning" ? "regresando" : "en camino"} · ${assignment.route.distance_km.toFixed(1)} km${assignment.route.approximate ? ' · trayectoria aproximada' : ''} · tiempo visual acelerado`;
      vehicles.get(resource.id).marker.unbindTooltip().bindTooltip(label);
    }
    const inventory = engagedStations(state.stations || [...bases.values()].map(({ resource, count }) => ({ ...resource, available: 0, total: count, busy: count })), state.assignments);
    for (const station of inventory) {
      const marker = L.marker([station.lat, station.lon], { pane: "response-vehicles",
        icon: L.divIcon({ className: `response-station ${station.kind}`, html: `${{ fire_engine: 'B', ambulance: 'A', police: 'P', helicopter: 'H' }[station.kind] || ''} ${station.available}/${station.total}`, iconSize: [34, 24], iconAnchor: [17, 12] }) }).addTo(stations);
      const label = document.createElement("span"); label.textContent = `${station.name} · sede de origen de una unidad movilizada · ${station.available} disponibles / ${station.busy} ocupados / ${station.total} total · flota simulada`;
      marker.bindTooltip(label).bindPopup(label.cloneNode(true));
    }
  }

  function renderRehearsal() {
    const active = map.getZoom() > 13 ? rehearsal.active : null;
    if (active === rehearsalKey) return;
    rehearsalKey = active; rehearsalLayer.clearLayers();
    if (!active) return;
    const a = state.assignments[active.resource_id], points = a.route.coordinates.map(([lon, lat]) => [lat, lon]);
    L.polyline(points, { pane: 'response-routes', renderer: rehearsalRenderer, color: '#9180cd', weight: 9, opacity: .18, interactive: false }).addTo(rehearsalLayer);
    L.polyline(points, { pane: 'response-routes', renderer: rehearsalRenderer, color: '#7560bd', weight: 4, opacity: .9,
      dashArray: '12 16', className: 'route-rehearsal', interactive: false }).addTo(rehearsalLayer);
    const [lon, lat] = routePosition(a.route, (active.event.at - a.started_at) / a.travel_seconds);
    L.marker([lat, lon], { pane: 'response-vehicles', interactive: false,
      icon: L.divIcon({ className: 'route-rehearsal-label', html: 'Recalculando · demo', iconSize: [144, 24], iconAnchor: [72, 40] }) }).addTo(rehearsalLayer);
  }

  function stopRehearsal() {
    rehearsal.reset(); renderRehearsal();
    if (current?.kind === 'route_rehearsal') { current = null; hideCaption(); }
  }

  function renderAlerts() {
    alerts.clearLayers();
    for (const [id, alert] of Object.entries(state.alerts || {})) {
      const incident = findIncident(id);
      if (!incident || alert.expires_at * 1000 < Date.now() + offset) continue;
      const circle = L.circle([incident.lat, incident.lon], { pane: "response-routes", radius: 1800, color: "#a99bcf", weight: 1.5, dashArray: "4 8", fillOpacity: .035 }).addTo(alerts);
      const text = document.createElement("span"); text.textContent = `${alert.mode === 'mobile_simulation' ? 'ES-Alert enviado al simulador móvil' : 'Vista previa ES-Alert'} · zona ilustrativa, no perímetro de evacuación. ${alert.message}`;
      circle.bindTooltip(text);
    }
  }

  function tick(timestamp = performance.now()) {
    frame = 0;
    if (document.hidden) return;
    if (lastVisualTick && timestamp - lastVisualTick < 32) {
      frame = requestAnimationFrame(tick);
      return;
    }
    lastVisualTick = timestamp;
    const now = Date.now(), connected = now - lastContact < 10000;
    if (current && now > shownUntil) { current = null; hideCaption(); }
    if (queue.length && current?.kind === 'route_rehearsal') stopRehearsal();
    if (!paused && !current && queue.length) {
      const event = queue[0];
      if (!event.incident_id || findIncident(event.incident_id) || ['cancelled', 'field_report', 'blocked'].includes(event.kind)) show(queue.shift());
      else if (now - (event.queuedAt || event.at * 1000 - offset || now) > 15000) queue.shift();
    }
    const rehearsalEvent = rehearsal.step({ assignments: state?.assignments || {}, now: (now + offset) / 1000,
      enabled: connected && !paused && map.getZoom() > 13 && ['idle', 'watching'].includes(state?.status),
      busy: queue.length > 0 || Boolean(current && !current.visual) || cameraTour.moving(),
      visible: a => { const point = vehicles.get(a.resource.id)?.marker.getLatLng(); return point && map.getBounds().contains(point); },
    });
    renderRehearsal();
    if (rehearsalEvent) { sceneView.addVisualEvent(rehearsalEvent); show(rehearsalEvent); }
    if (connected && following && armed && !paused && !current && !rehearsal.active && !queue.length && !cameraTour.moving() && now > nextVisit) patrol();
    evidence.tick(now); sceneView.tick();
    if (contextUntil && now > contextUntil) { contextUntil = 0; clearContext(); }
    aura.set(connected && (state?.status === "thinking" || current && !["error", "blocked"].includes(current.kind)));
    if (connected && !paused) for (const vehicle of vehicles.values()) {
      const { marker, assignment } = vehicle;
      const progress = reduced.matches ? (assignment.status === "onscene" ? 1 : 0) : ((now + offset) / 1000 - assignment.started_at) / assignment.travel_seconds;
      const [lon, lat] = assignment.held_position || routePosition(assignment.route, progress);
      const key = `${lat.toFixed(6)},${lon.toFixed(6)}`;
      if (key !== vehicle.lastPoint) { marker.setLatLng([lat, lon]); vehicle.lastPoint = key; }
    }
    frame = requestAnimationFrame(tick);
  }

  async function refresh() {
    if (loading || document.hidden) return;
    loading = true;
    try {
      const response = await fetch("/api/director", { signal: globalThis.AbortSignal.timeout(8000) });
      if (!response.ok) throw new Error("Director no disponible");
      const next = await response.json();
      if (session !== next.session_id) {
        sequence = 0; queue = []; current = null; session = next.session_id;
        armed = false; lastTarget = ""; lastEvidence = ""; routeKey = ""; contextUntil = 0;
        cameraTour.cancel(); evidence.hide(); stopRehearsal();
        if (Number.isFinite(map.getZoom())) clearContext();
        hideCaption();
      }
      offset = next.server_time ? next.server_time * 1000 - Date.now() : 0;
      queue.push(...freshEvents(next.events || [], sequence, (Date.now() + offset) / 1000));
      queue = queue.slice(-16);
      sequence = next.sequence || 0; state = next; lastContact = Date.now();
      renderAssignments(); renderAlerts(); sceneView.update(next); operationView.update(next);
      $('director-warning').textContent = directorWarning(next.status);
      $('director-warning').hidden = !directorWarning(next.status);
    } catch {
      $('director-warning').textContent = directorWarning('disconnected');
      $('director-warning').hidden = false;
      aura.set(false); stopRehearsal();
      if (state && state.status !== "disconnected") {
        state.status = "disconnected"; queue = []; cameraTour.cancel(); evidence.hide();
        show({ kind: "error", message: "Conexión con el director interrumpida", reason: "La vista conserva el último estado recibido." });
      }
    } finally { loading = false; }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) { cancelAnimationFrame(frame); frame = 0; cameraTour.cancel(); evidence.hide(); stopRehearsal(); queue = []; current = null; hideCaption(); }
    else { refresh(); if (!frame) frame = requestAnimationFrame(tick); }
  });
  refresh(); setInterval(refresh, 500); frame = requestAnimationFrame(tick);
  return {
    report(incident) {
      armed = true; current = null; lastEvidence = ""; cameraTour.cancel(); evidence.hide();
      queue = queue.filter(e => e.incident_id !== incident.id || !["report", "focus", "context", "watch"].includes(e.kind));
      queue.unshift({ kind: "report", message: `Nuevo aviso de incendio · ${incident.demo_report.location.label}`, reason: "Ubicación comunicada en la llamada · consultando evidencias sin descartar el aviso", incident_id: incident.id, queuedAt: Date.now() });
    },
    call(call) {
      if (!call || call.state === "located" || call.state === 'field_report') return;
      queue.push({ kind: call.error ? "error" : "call", message: call.error || (call.state === "needs_location" ? "Precisando la ubicación del aviso" : call.state === "not_fire" ? "Aviso revisado · incendio no confirmado" : call.ended ? "Llamada finalizada" : "Llamada entrante · recogiendo datos"), reason: "" });
    },
    setPaused(value) { paused = value; aura.setPaused(value); if (value) { cameraTour.cancel(); evidence.hide(); stopRehearsal(); } document.body.classList.toggle("motion-paused", value); },
    manual,
  };
}
