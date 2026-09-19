import { sample, cardinal } from "./wind.js";
import { destination, scenario, imagePoints } from "./simulation.js";
import { createStage } from "./flames.js";
import { rings } from "./flow.js";

const $ = id => document.getElementById(id);
const svg = name => `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
const number = (n, digits = 1) => Number(n).toLocaleString("es-ES", { maximumFractionDigits: digits });
const date = (value, day = false) => new Intl.DateTimeFormat("es-ES", {
  timeZone: "UTC", hour: "2-digit", minute: "2-digit", ...(day ? { day: "2-digit", month: "short" } : {}),
}).format(new Date(value)) + " UTC";
const day = value => new Intl.DateTimeFormat("es-ES", { timeZone: "UTC", day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
const age = value => {
  const hours = Math.max(0, (Date.now() - new Date(value).getTime()) / 3600000);
  return hours < 1 ? `hace ${Math.floor(hours * 60)} min` : `hace ${Math.floor(hours)} h`;
};
const escapeHtml = text => String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const map = L.map("map", {
  zoomControl: false, minZoom: 4, maxZoom: 16, zoomSnap: 0,
  zoomAnimation: false, fadeAnimation: false, scrollWheelZoom: false, preferCanvas: false,
});
map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
L.control.scale({ imperial: false, maxWidth: 110, position: "bottomleft" }).addTo(map);
map.createPane("footprints"); map.getPane("footprints").style.zIndex = 430;
map.createPane("scenario"); map.getPane("scenario").style.zIndex = 440;
const shapeLayer = L.layerGroup().addTo(map), scenarioLayer = L.layerGroup().addTo(map);
map.getPane("mapPane").appendChild($("flow"));
const stage = createStage({
  map, canvas: $("flow"),
  sampleWind: (lat, lon) => (data ? sample(data.wind.regions, lat, lon) : null),
});
let data, country, selected, currentPicture, imageMode = "natural", imageRequest = 0, filter = "all", region = "peninsula";
let windVisible = true, simulationOpen = false, playTimer, refreshing = false, animationPaused = false;
let zoomTarget = null, zoomFrame = 0;
const cachedPictures = new Map();
const views = {
  peninsula: [[35.6, -9.9], [44.1, 4.65]], baleares: [[38.5, .8], [40.4, 4.8]],
  canarias: [[27.4, -18.4], [29.5, -13.25]], ceuta: [[34.9, -6.2], [36.6, -2.1]],
};

function stopPlay() {
  clearInterval(playTimer); playTimer = null;
  $("play").innerHTML = svg("play"); $("play").setAttribute("aria-label", "Reproducir escenario");
}

function setRegion(name) {
  cancelZoom();
  region = name;
  document.querySelectorAll("[data-region]").forEach(b => b.classList.toggle("active", b.dataset.region === name));
  map.fitBounds(views[name], { paddingTopLeft: [30, 180], paddingBottomRight: [35, 110], animate: false });
  $("map-toast").hidden = true;
  if (data && !data.incidents.some(i => map.getBounds().contains([i.lat, i.lon]))) {
    $("map-toast").textContent = "Sin detecciones en esta vista y periodo. No garantiza ausencia de incendios.";
    $("map-toast").hidden = false;
  }
}

function visibleIncidents() {
  const query = $("search").value.trim().toLocaleLowerCase("es");
  return (data?.incidents || []).filter(i =>
    (filter === "all" || i.documented) && `${i.name} ${i.province} ${i.id}`.toLocaleLowerCase("es").includes(query));
}

function renderList() {
  const incidents = visibleIncidents();
  $("list-count").textContent = `${incidents.length}`;
  const list = $("incident-list"); list.replaceChildren();
  if (!incidents.length) {
    const empty = document.createElement("p"); empty.className = "empty";
    empty.textContent = data?.incidents.length ? "No hay zonas que coincidan. Prueba otra búsqueda o el filtro «Todas»." : "Sin detecciones en el periodo disponible. No garantiza ausencia de incendios.";
    list.append(empty);
  }
  for (const i of incidents) {
    const button = document.createElement("button");
    button.className = `incident ${i.id === selected?.id ? "selected" : ""}`;
    button.setAttribute("aria-pressed", String(i.id === selected?.id));
    button.innerHTML = `<span class="incident-dot ${i.low_confidence === i.observations ? "low" : ""}"></span><span class="incident-body"><span class="incident-title"><strong>${escapeHtml(i.name)}</strong><span>${age(i.last_seen)}</span></span><span class="incident-subtitle">${i.documented ? "La Rioja · caso documentado" : `${i.lat.toFixed(3)}° N · ${Math.abs(i.lon).toFixed(3)}° ${i.lon < 0 ? "O" : "E"} · sin confirmar`}</span><span class="incident-meta"><span>${i.observations} detecciones</span><span>${svg("wind")} ${number(i.weather.wind_speed_kmh)} km/h</span></span></span>${selected?.id === i.id ? '<span class="incident-arrow">↗</span>' : ""}`;
    button.addEventListener("click", () => selectIncident(i, true));
    list.append(button);
  }
  renderFires(incidents);
}

function renderFires(incidents) {
  shapeLayer.clearLayers();
  for (const i of incidents) {
    const target = L.circleMarker([i.lat, i.lon], {
      pane: "footprints", radius: 13 + Math.min(11, Math.sqrt(i.observations) * 2.5),
      color: "#00000000", weight: 0, fillColor: "#00000000", fillOpacity: 0, className: "fire-target",
    }).on("click", () => selectIncident(i, true)).addTo(shapeLayer);
    L.geoJSON(i.footprint, {
      pane: "footprints", className: "fire-target",
      style: { color: "#00000000", weight: 12, fillColor: "#00000000", fillOpacity: 0 },
    }).on("click", () => selectIncident(i, true)).addTo(shapeLayer);
    if (i.id === selected?.id) {
      target.bindTooltip(`${escapeHtml(i.name)} · ${i.observations} detecciones`,
        { permanent: true, direction: "right", offset: [14, 0], className: "fire-label" }).openTooltip();
    }
  }
  stage.update(incidents, selected?.id || null);
}

function selectIncident(incident, focus = false) {
  stopPlay(); $("horizon").value = "0";
  selected = incident;
  $("details").classList.add("open");
  $("sidebar").classList.remove("open");
  $("detail-content").hidden = false;
  $("detail-name").textContent = incident.name;
  $("detail-location").textContent = `${incident.province} · ${incident.lat.toFixed(3)}° N, ${Math.abs(incident.lon).toFixed(3)}° ${incident.lon < 0 ? "O" : "E"}`;
  $("detection-tag").textContent = incident.documented ? "Caso documentado · 18 sept" : "Anomalía térmica · sin confirmar";
  $("seen-age").textContent = `Última detección ${age(incident.last_seen)}`;
  $("footprint-area").textContent = number(incident.footprint_ha);
  const w = incident.weather, to = destination(w.wind_from_degrees);
  $("wind-speed").textContent = number(w.wind_speed_kmh);
  $("temperature").textContent = number(w.air_temperature_c);
  $("direction-arrow").style.transform = `rotate(${to || 0}deg)`;
  $("direction-arrow").hidden = to === null;
  $("wind-direction").textContent = to === null ? "Calma · sin dirección" : `Hacia ${cardinal(to)} · desde ${cardinal(w.wind_from_degrees)}`;
  $("weather-time").textContent = date(w.valid_at_utc);
  $("weather-note").textContent = `Rachas ${number(w.wind_gust_kmh)} km/h · GFS 0,25° · ${date(w.valid_at_utc, true)}. Modelo iniciado ${date(w.model_run_utc, true)}.`;
  $("brightness").textContent = number(incident.brightness_i4_c);
  $("brightness-note").textContent = `${number(incident.brightness_i4_k)} K · máximo del grupo · ${date(incident.brightness_at_utc, true)}`;
  $("detection-count").textContent = incident.observations;
  $("passes").textContent = incident.passes;
  $("frp").textContent = number(incident.frp_peak_mw);
  $("detail-caveat").textContent = `${incident.satellites.join(" · ")}. Última detección: ${date(incident.last_seen, true)}. ${incident.low_confidence} de baja confianza. ${incident.documented ? "Caso contrastado en prensa; no confirma que continúe activo." : "La detección de calor no confirma un incendio forestal."}`;
  $("news-link").hidden = !incident.documentation_url;
  if (incident.documentation_url) $("news-link").href = incident.documentation_url;
  $("scenario-direction").textContent = to === null ? "Sin dirección de viento" : `Orientación hacia ${cardinal(to)}`;
  $("simulate").disabled = to === null;
  $("scenario-shortcut").disabled = to === null;
  renderList(); renderScenario();
  if (focus) {
    cancelZoom();
    const bounds = map.getBounds().pad(-.1);
    if (!bounds.contains([incident.lat, incident.lon])) map.setView([incident.lat, incident.lon], 7, { animate: false });
    else map.panTo([incident.lat, incident.lon], { animate: false });
  }
  loadPicture();
}

async function loadPicture() {
  const token = ++imageRequest;
  currentPicture = null;
  $("sat-image").hidden = true; $("image-detections").replaceChildren();
  $("image-message").hidden = false; $("image-message").textContent = "Buscando el mosaico más reciente…";
  $("image-date").textContent = "Comprobando cobertura…"; $("image-source").hidden = true;
  $("enlarge-image").disabled = true;
  const incident = selected;
  const key = `${incident.id}|${imageMode}|${new Date().toISOString().slice(0, 13)}`;
  try {
    let picture = cachedPictures.get(key);
    if (!picture) {
      const response = await fetch(`/api/satellite?id=${encodeURIComponent(incident.id)}&mode=${imageMode}`);
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Imagen no disponible");
      picture = result; cachedPictures.set(key, picture);
    }
    if (token !== imageRequest) return;
    currentPicture = picture;
    const img = $("sat-image");
    img.onload = () => {
      if (token !== imageRequest) return;
      img.hidden = false; $("image-message").hidden = true; $("enlarge-image").disabled = false;
      $("image-detections").innerHTML = imagePoints(incident.detections, picture.bbox)
        .map(p => `<circle cx="${p.x}" cy="${p.y}" r="5"/>`).join("");
    };
    img.onerror = () => { if (token === imageRequest) { $("image-message").hidden = false; $("image-message").textContent = "No se pudo cargar la imagen. Cambia de capa para reintentar."; } };
    img.alt = `Imagen NASA ${imageMode === "natural" ? "color natural" : "SWIR"} de ${incident.name}, ${picture.date}`;
    img.src = picture.url;
    $("image-date").textContent = `${day(picture.date)} · mosaico diario`;
    $("image-source").href = picture.source_url; $("image-source").hidden = false;
  } catch (error) {
    if (token !== imageRequest) return;
    $("image-message").textContent = `Imagen no disponible. ${error.message}`;
    $("image-date").textContent = "Sin imagen reciente confirmada";
  }
}

function renderScenario() {
  scenarioLayer.clearLayers();
  const hours = Number($("horizon").value);
  $("horizon-value").textContent = hours === 0 ? "Ahora" : `+${number(hours)} h`;
  if (!simulationOpen || !selected) return;
  const geometry = scenario(selected, hours, Number($("spread-rate").value));
  if (geometry) L.geoJSON(geometry, {
    pane: "scenario", interactive: false,
    style: { color: "#d4946b", fillColor: "#eabf8c", fillOpacity: .2, weight: 1.5, className: "scenario-outline" },
  }).addTo(scenarioLayer);
}

function closeSimulation() {
  simulationOpen = false; stopPlay(); $("simulation-card").hidden = true; renderScenario();
}

async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    const response = await fetch("/api/data");
    if (!response.ok) throw new Error("No se pudieron actualizar los datos");
    data = await response.json();
    $("zone-count").textContent = data.incidents.length;
    $("tab-count").textContent = data.incidents.length;
    $("obs-count").textContent = data.incidents.reduce((sum, i) => sum + i.observations, 0);
    $("map-date").textContent = `Detecciones en las últimas 24 h · corte ${date(data.fires_checked_at, true)}`;
    $("last-check").textContent = `FIRMS ${date(data.fires_checked_at)} · Meteo ${date(data.wind.checked_at_utc)}`;
    $("feed-state").classList.toggle("warning", data.status !== "ready");
    $("feed-state").innerHTML = `<i></i>${data.status === "ready" ? "Fuentes conectadas" : data.status === "offline" ? "Muestra guardada" : "Datos sin actualizar"}`;
    $("error-banner").hidden = data.status === "ready";
    $("error-banner").textContent = data.status === "offline" ? "Modo sin conexión. Consulta las fechas de la muestra guardada." : "Alguna fuente no está actualizada. Conservamos los últimos datos con su fecha.";
    const next = data.incidents.find(i => i.id === selected?.id) || data.incidents[0];
    if (!selected || next?.id !== selected.id) {
      if (next) selectIncident(next);
      else { selected = null; $("scenario-shortcut").disabled = true; $("detail-content").hidden = true; $("detail-name").textContent = "Sin detecciones"; closeSimulation(); imageRequest++; renderList(); }
    } else {
      const changed = data.wind.valid_at_utc !== selected.weather.valid_at_utc || next.observations !== selected.observations;
      if (changed) selectIncident(next); else { selected = next; $("seen-age").textContent = `Última detección ${age(next.last_seen)}`; renderList(); }
    }
  } catch (error) {
    $("error-banner").hidden = false; $("error-banner").textContent = `${error.message}. Reintentando en un minuto.`;
    $("feed-state").classList.add("warning"); $("feed-state").innerHTML = "<i></i>Sin conexión";
  } finally { refreshing = false; }
}

async function start() {
  const responses = await Promise.all(["spain.geojson", "neighbors.geojson", "provinces.geojson", "places.json"].map(p => fetch(`/${p}`)));
  if (responses.some(r => !r.ok)) throw new Error("No se pudo cargar la cartografía. Recarga la página.");
  const [spain, neighbors, provinces, places] = await Promise.all(responses.map(r => r.json()));
  country = spain;
  L.geoJSON(neighbors, { interactive: false, style: { color: "#e5e9ee", weight: .8, fillColor: "#f2f4f7", fillOpacity: 1 } }).addTo(map);
  L.geoJSON(country, { interactive: false, style: { color: "#cfd6df", weight: 1, fillColor: "#ffffff", fillOpacity: 1 } }).addTo(map);
  L.geoJSON(provinces, { interactive: false, style: { color: "#e7ebf0", weight: .6, fillOpacity: 0 } }).addTo(map);
  for (const place of places) {
    const label = L.marker([place.lat, place.lon], { interactive: false, icon: L.divIcon({
      className: "place-label", html: escapeHtml(place.name), iconSize: [90, 18], iconAnchor: [45, -5],
    }) });
    const show = () => {
      const visible = map.getZoom() > 7 || ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Palma", "A Coruña", "Las Palmas"].includes(place.name);
      if (visible) label.addTo(map); else label.remove();
    };
    map.on("zoomend", show); show();
  }
  stage.start(rings(country.geometry));
  map.on("moveend resize zoomend", () => {
    document.querySelector(".map-label h2").textContent = map.getZoom() > 9 && selected ? `${selected.name}, a escala local.` : "España, bajo observación.";
    document.querySelector(".map-label .eyebrow").textContent = map.getZoom() > 9 ? "DETALLE TERRITORIAL" : "PANORAMA NACIONAL";
  });
  new ResizeObserver(() => map.invalidateSize()).observe($("map"));
  setRegion("peninsula"); await refresh(); setInterval(refresh, 60000);
}

document.querySelectorAll("[data-region]").forEach(b => b.addEventListener("click", () => { closeSimulation(); setRegion(b.dataset.region); }));
document.querySelectorAll("[data-filter]").forEach(b => b.addEventListener("click", () => {
  filter = b.dataset.filter;
  document.querySelectorAll("[data-filter]").forEach(el => el.classList.toggle("active", el === b));
  closeSimulation(); renderList();
}));
document.querySelectorAll("[data-image]").forEach(b => b.addEventListener("click", () => {
  imageMode = b.dataset.image;
  document.querySelectorAll("[data-image]").forEach(el => el.classList.toggle("active", el === b));
  if (selected) loadPicture();
}));
$("search").addEventListener("input", () => { closeSimulation(); renderList(); });
function cancelZoom() {
  if (zoomFrame) cancelAnimationFrame(zoomFrame);
  zoomFrame = 0; zoomTarget = null;
}

function zoomTo(zoom, anchor = null) {
  zoomTarget = Math.max(map.getMinZoom(), Math.min(map.getMaxZoom(), zoom));
  if (zoomFrame) cancelAnimationFrame(zoomFrame);
  const start = map.getZoom(), centre = map.getCenter(), began = performance.now();
  const cursor = anchor ? map.containerPointToLatLng(anchor) : centre;
  const duration = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 220;
  const end = zoomTarget;
  const tick = timestamp => {
    const progress = duration ? Math.min(1, (timestamp - began) / duration) : 1;
    const current = start + (end - start) * (1 - Math.pow(1 - progress, 3));
    const offset = anchor ? map.getSize().divideBy(2).subtract(anchor) : L.point(0, 0);
    const projected = map.project(cursor, current).add(offset);
    map.setView(map.unproject(projected, current), current, { animate: false });
    if (progress < 1) zoomFrame = requestAnimationFrame(tick);
    else { zoomFrame = 0; zoomTarget = null; }
  };
  zoomFrame = requestAnimationFrame(tick);
}

$("map").addEventListener("wheel", event => {
  event.preventDefault();
  const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? map.getSize().y : 1);
  if (!delta) return;
  zoomTo((zoomTarget ?? map.getZoom()) - Math.sign(delta) * Math.min(.75, Math.abs(delta) / 120), map.mouseEventToContainerPoint(event));
}, { passive: false });
map.on("dragstart mousedown touchstart", cancelZoom);
$("zoom-in").onclick = () => zoomTo((zoomTarget ?? map.getZoom()) + 1);
$("zoom-out").onclick = () => zoomTo((zoomTarget ?? map.getZoom()) - 1);
$("motion-toggle").onclick = () => {
  animationPaused = !animationPaused;
  stage.setPaused(animationPaused);
  $("motion-toggle").setAttribute("aria-pressed", String(animationPaused));
  $("motion-toggle").setAttribute("aria-label", animationPaused ? "Reanudar animaciones" : "Pausar animaciones");
  $("motion-toggle").innerHTML = animationPaused ? svg("play") : '<span class="pause-icon">Ⅱ</span>';
};
$("reset-map").onclick = () => { closeSimulation(); setRegion(region); };
$("wind-toggle").onclick = () => {
  windVisible = !windVisible; $("wind-toggle").classList.toggle("active", windVisible);
  $("wind-toggle").setAttribute("aria-pressed", String(windVisible)); stage.setWind(windVisible);
};
$("show-list").onclick = () => { $("sidebar").classList.toggle("open"); $("details").classList.remove("open"); };
$("close-details").onclick = () => {
  $("details").classList.remove("open");
  if (!matchMedia("(max-width:650px)").matches) {
    $("detail-content").hidden = true; $("detail-name").textContent = "Selecciona una zona"; $("detail-location").textContent = "Haz clic en una señal del mapa";
    selected = null; $("scenario-shortcut").disabled = true; imageRequest++; renderList(); closeSimulation();
  }
};
$("focus-fire").onclick = () => {
  if (!selected) return;
  cancelZoom();
  map.setView([selected.lat, selected.lon], 14.5, { animate: false });
  $("details").classList.remove("open");
};
$("simulate").onclick = () => {
  if (!selected) return;
  cancelZoom();
  simulationOpen = true; $("simulation-card").hidden = false;
  $("details").classList.remove("open");
  map.setView([selected.lat, selected.lon], 13, { animate: false });
  $("horizon").value = "1"; renderScenario();
};
$("scenario-shortcut").onclick = () => $("simulate").click();
$("close-simulation").onclick = closeSimulation;
$("horizon").addEventListener("input", () => { stopPlay(); renderScenario(); });
$("spread-rate").addEventListener("change", renderScenario);
$("play").onclick = () => {
  if (playTimer) { stopPlay(); return; }
  if (Number($("horizon").value) >= 6) $("horizon").value = "0";
  $("play").textContent = "Ⅱ"; $("play").setAttribute("aria-label", "Pausar escenario");
  playTimer = setInterval(() => {
    $("horizon").value = String(Math.min(6, Number($("horizon").value) + .1)); renderScenario();
    if (Number($("horizon").value) >= 6) stopPlay();
  }, 200);
};
for (const id of ["about-button", "sources-button", "footer-about"]) $(id).onclick = () => $("about-dialog").showModal();
document.querySelectorAll("[data-close]").forEach(b => b.onclick = () => $(b.dataset.close).close());
for (const id of ["about-dialog", "image-dialog"]) $(id).addEventListener("click", event => { if (event.target === $(id)) $(id).close(); });
$("enlarge-image").onclick = () => {
  if (!currentPicture || !selected) return;
  $("large-image").src = currentPicture.url;
  $("large-detections").innerHTML = $("image-detections").innerHTML;
  $("large-caption").textContent = `${selected.name} · ${day(currentPicture.date)} · ${imageMode === "natural" ? "color natural" : "infrarrojo SWIR"}`;
  $("image-dialog").showModal();
};
document.addEventListener("visibilitychange", () => { if (document.hidden) stopPlay(); });
start().catch(error => { $("error-banner").hidden = false; $("error-banner").textContent = error.message; });
