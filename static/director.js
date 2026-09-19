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

export function freshEvents(events, sequence, now) {
  return events.filter(event => event.sequence > sequence && now - event.at < 90);
}

const VEHICLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 6h12v12H2zM14 11h4l4 4v3h-8M5 3h7M5 9h6m-6 3h6"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/></svg>';

export function createDirectorView({ map, L, document, fetch, focus, clearContext, findIncident }) {
  const $ = id => document.getElementById(id);
  const routes = L.layerGroup().addTo(map), stations = L.layerGroup().addTo(map), alerts = L.layerGroup().addTo(map);
  const vehicles = new Map();
  map.createPane("response-routes"); map.getPane("response-routes").style.zIndex = 420;
  map.createPane("response-vehicles"); map.getPane("response-vehicles").style.zIndex = 425;
  map.attributionControl.addAttribution('Rutas locales © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> · <a href="https://www.openstreetmap.org/fixthemap" target="_blank" rel="noopener">Corregir mapa</a>');
  let state = null, session = null, sequence = 0, loading = false, paused = false, frame = 0, offset = 0;
  let queue = [], current = null, shownUntil = 0, lastContact = 0, contextUntil = 0, routeKey = "";
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");

  function show(event) {
    current = event;
    shownUntil = Date.now() + ({ thinking: 1800, report: 4000, focus: 2500, context: 3500 }[event.kind] || 4500);
    $("agent-card").hidden = false;
    $("agent-label").textContent = event.kind === "report" ? "AVISO RECIBIDO" : event.kind === "error" || event.kind === "blocked" ? "FLAREAI · REVISIÓN" : "FLAREAI · DIRECTOR";
    $("agent-message").textContent = event.message;
    $("agent-reason").textContent = event.reason || "";
    const incident = findIncident(event.incident_id);
    if (incident && ["focus", "context"].includes(event.kind)) {
      focus(incident, event.kind === "focus");
      contextUntil = Date.now() + 45000;
    }
    if (event.resource_id && ["dispatch", "reassign", "return"].includes(event.kind)) {
      const assignment = state?.assignments[event.resource_id];
      if (assignment) map.fitBounds(assignment.route.coordinates.map(([lon, lat]) => [lat, lon]), { padding: [90, 100], maxZoom: 14, animate: false });
    }
  }

  function renderAssignments() {
    const assignments = Object.values(state.assignments || {});
    const key = JSON.stringify(assignments.map(a => [a.id, a.status]));
    if (key === routeKey) return;
    routeKey = key; routes.clearLayers(); stations.clearLayers();
    const active = new Set(assignments.map(a => a.resource.id));
    for (const [id, vehicle] of vehicles) if (!active.has(id)) { vehicle.marker.remove(); vehicles.delete(id); }
    const bases = new Map();
    for (const assignment of assignments) {
      const resource = assignment.resource, police = resource.kind === "police";
      const route = L.polyline(assignment.route.coordinates.map(([lon, lat]) => [lat, lon]), {
        pane: "response-routes", color: police ? "#789bc5" : "#e88578", weight: 3, opacity: assignment.status === "onscene" ? .25 : .75, interactive: false,
        dashArray: assignment.status === "returning" ? "5 7" : null,
      }).addTo(routes);
      const base = bases.get(resource.station_id) || { resource, count: 0 }; base.count++; bases.set(resource.station_id, base);
      if (!vehicles.has(resource.id)) {
        const marker = L.marker([resource.lat, resource.lon], { pane: "response-vehicles", title: resource.name,
          icon: L.divIcon({ className: `response-vehicle ${police ? "police" : "fire-engine"}`, html: VEHICLE, iconSize: [30, 28], iconAnchor: [15, 14] }) }).addTo(map);
        vehicles.set(resource.id, { marker, assignment, route });
      } else Object.assign(vehicles.get(resource.id), { assignment, route });
      const label = document.createElement("span");
      label.textContent = `${police ? "Patrulla" : "Camión"} · ${resource.name} · ${assignment.status === "onscene" ? "en el punto de encuentro" : assignment.status === "returning" ? "regresando" : "en camino"} · ${assignment.route.distance_km.toFixed(1)} km · tiempo visual acelerado`;
      vehicles.get(resource.id).marker.unbindTooltip().bindTooltip(label);
    }
    for (const { resource, count } of bases.values()) {
      const marker = L.marker([resource.lat, resource.lon], { pane: "response-vehicles",
        icon: L.divIcon({ className: "response-station", html: String(count), iconSize: [24, 24], iconAnchor: [12, 12] }) }).addTo(stations);
      const label = document.createElement("span"); label.textContent = `${resource.name} · ${count} recurso${count === 1 ? "" : "s"} asignado${count === 1 ? "" : "s"}`;
      marker.bindTooltip(label);
    }
  }

  function renderAlerts() {
    alerts.clearLayers();
    for (const [id, alert] of Object.entries(state.alerts || {})) {
      const incident = findIncident(id);
      if (!incident || alert.expires_at * 1000 < Date.now() + offset) continue;
      const circle = L.circle([incident.lat, incident.lon], { pane: "response-routes", radius: 1800, color: "#a99bcf", weight: 1.5, dashArray: "4 8", fillOpacity: .035 }).addTo(alerts);
      const text = document.createElement("span"); text.textContent = `Vista previa ES-Alert · zona ilustrativa, no perímetro de evacuación. ${alert.message}`;
      circle.bindTooltip(text);
    }
  }

  function tick() {
    frame = 0;
    if (document.hidden) return;
    const now = Date.now(), connected = now - lastContact < 10000;
    if (current && now > shownUntil) { current = null; $("agent-card").hidden = true; }
    if (!current && queue.length) show(queue.shift());
    if (contextUntil && now > contextUntil) { contextUntil = 0; clearContext(); }
    $("agent-aura").hidden = !connected || !(state?.status === "thinking" || current && !["error", "blocked"].includes(current.kind));
    if (connected && !paused) for (const { marker, assignment } of vehicles.values()) {
      const progress = reduced.matches ? (assignment.status === "onscene" ? 1 : 0) : ((now + offset) / 1000 - assignment.started_at) / assignment.travel_seconds;
      const [lon, lat] = routePosition(assignment.route, progress);
      marker.setLatLng([lat, lon]);
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
        $("agent-card").hidden = true;
      }
      offset = next.server_time ? next.server_time * 1000 - Date.now() : 0;
      queue.push(...freshEvents(next.events || [], sequence, (Date.now() + offset) / 1000));
      queue = queue.slice(-16);
      sequence = next.sequence || 0; state = next; lastContact = Date.now();
      renderAssignments(); renderAlerts();
    } catch {
      $("agent-aura").hidden = true;
      if (state && state.status !== "disconnected") {
        state.status = "disconnected"; queue = [];
        show({ kind: "error", message: "Conexión con el director interrumpida", reason: "La vista conserva el último estado recibido." });
      }
    } finally { loading = false; }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) { cancelAnimationFrame(frame); frame = 0; }
    else { refresh(); if (!frame) frame = requestAnimationFrame(tick); }
  });
  refresh(); setInterval(refresh, 2000); frame = requestAnimationFrame(tick);
  return {
    report(incident) { contextUntil = Date.now() + 45000; queue.push({ kind: "report", message: `Nuevo aviso de incendio · ${incident.demo_report.location.label}`, reason: "Ubicación comunicada en la llamada", incident_id: incident.id }); },
    call(call) {
      if (!call || call.state === "located") return;
      queue.push({ kind: call.error ? "error" : "call", message: call.error || (call.state === "needs_location" ? "Precisando la ubicación del aviso" : call.state === "not_fire" ? "Aviso revisado · incendio no confirmado" : call.ended ? "Llamada finalizada" : "Llamada entrante · recogiendo datos"), reason: "" });
    },
    setPaused(value) { paused = value; document.body.classList.toggle("motion-paused", value); },
    manual() { contextUntil = 0; },
  };
}
