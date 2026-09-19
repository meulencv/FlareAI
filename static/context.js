const number = (value, digits = 0) => value == null ? "sin dato" : Number(value).toLocaleString("es-ES", { maximumFractionDigits: digits });
const escapeHtml = value => String(value).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const soils = { bosque: "bosque", urbano: "urbano", cultivos: "cultivos", matorral: "matorral", herbaceas: "herbáceas", suelo_desnudo: "suelo desnudo", agua: "agua", humedales: "humedales", nieve_hielo: "nieve / hielo", musgos_liquenes: "musgos / líquenes" };

export function safeSourceUrl(value) {
  return /^https:\/\/www\.openstreetmap\.org\/(node|way|relation)\/\d+$/.test(value || "") ? value : null;
}

export function contextSummary(context) {
  const p = context.population, f = context.facilities, wind = context.wind;
  let headline = "Contexto cercano, no evaluación de riesgo";
  if (context.coverage === "no_grid_cells") headline = "Sin cobertura censal en este entorno";
  else if (context.level === "attention") headline = "Atención: elementos a favor del viento";
  else if (!p.inhabited_cells && !f.count) headline = "Sin elementos registrados; no implica ausencia de riesgo";
  const windLabels = {
    calm: "Viento débil (<3 km/h): sin aviso direccional.", missing: "Sin viento válido: solo proximidad.",
    stale: "Meteorología desactualizada: solo proximidad.", historical: "Dirección de la muestra histórica, no aviso actual.",
  };
  const directional = windLabels[wind.status] || `A favor del viento: ${number(p.downwind_residents)} residentes censados y ${number(f.downwind_high_priority)} instalaciones de prioridad alta orientativa.`;
  const land = Object.entries(context.landcover.percentages).filter(([, value]) => value != null && value > 0).sort((a, b) => b[1] - a[1]);
  return {
    headline, directional,
    population: p.residents == null ? "Población: sin datos disponibles." : `${number(p.residents)} residentes censados · ${number(p.inhabited_cells)} celdas habitadas${p.missing_cells ? " · cobertura parcial" : ""}`,
    facilities: `${number(f.count)} elementos OSM · ${number(f.high_priority)} de prioridad alta orientativa`,
    land: land.length ? `Suelo 2019: ${land.slice(0, 3).map(([name, value]) => `${number(value, 1)} % ${soils[name] || name}`).join(" · ")}` : "Suelo 2019: sin cobertura clasificada.",
  };
}

export function pointsVisible(context, zoom, enabled) {
  return Boolean(context && zoom >= 9 && enabled);
}

export function createContextView({ map, L, document, fetch, onFocus = () => {} }) {
  const $ = id => document.getElementById(id);
  const layer = L.layerGroup().addTo(map);
  let context = null, incident = null, request = 0, visible = true;
  const markers = new Map();

  function pointText(point) {
    const info = point.kind === "population" ? `${number(point.residents)} residentes · centro de celda de 1 km²` : point.category_label;
    const direction = point.downwind ? (context.wind.status === "historical" ? " · dirección histórica del viento" : " · a favor del viento") : "";
    return `${info} · ${number(point.distance_km, 2)} km de la huella${direction}`;
  }

  function draw() {
    layer.clearLayers(); markers.clear();
    if (!pointsVisible(context, map.getZoom(), visible && $("context-toggle").checked)) return;
    for (const point of context.points) {
      const color = point.downwind && context.wind.status === "current" ? "#ba6b32" : point.kind === "population" ? "#567b93" : "#8b8071";
      const label = document.createElement("div");
      label.className = "context-popup";
      const title = document.createElement("strong"); title.textContent = point.name;
      const description = document.createElement("p"); description.textContent = pointText(point);
      label.append(title, description);
      if (point.reason) { const reason = document.createElement("p"); reason.textContent = point.reason; label.append(reason); }
      const source = safeSourceUrl(point.source_url);
      if (source) { const link = document.createElement("a"); link.href = source; link.target = "_blank"; link.rel = "noopener"; link.textContent = "Ver elemento OSM"; label.append(link); }
      const marker = L.circleMarker([point.lat, point.lon], {
        radius: point.kind === "population" ? 5 : 6, color, weight: 1.5, fillColor: color, fillOpacity: .35,
        className: "context-marker",
      }).bindPopup(label).addTo(layer);
      markers.set(point.id, marker);
    }
  }

  function focusPoint(point) {
    $("context-toggle").checked = true;
    onFocus();
    map.setView([point.lat, point.lon], Math.max(map.getZoom(), 12), { animate: false });
    draw(); markers.get(point.id)?.openPopup();
  }

  function render() {
    const summary = contextSummary(context);
    $("context-summary").textContent = summary.headline;
    $("context-summary").classList.toggle("attention", context.level === "attention");
    $("context-population").textContent = summary.population;
    $("context-facilities").textContent = summary.facilities;
    $("context-wind").textContent = summary.directional;
    $("context-land").textContent = summary.land;
    const p = context.population;
    $("context-demographics").textContent = `Censo 2021: ${number(p.children_under_15)} menores de 15 años; ${number(p.adults_65_plus)} personas de 65 o más. ${p.age_missing_cells ? "Recuentos parciales. " : ""}Los grupos pueden no sumar el total por protección estadística. No son personas afectadas.`;
    const list = $("context-points"); list.replaceChildren();
    for (const point of context.points) {
      const item = document.createElement("li"), button = document.createElement("button");
      button.type = "button";
      button.innerHTML = `<strong>${escapeHtml(point.name)}</strong><span>${escapeHtml(pointText(point))}</span>`;
      button.onclick = () => focusPoint(point);
      item.append(button); list.append(item);
    }
    $("context-limits").textContent = `${context.points_truncated ? "Se muestran hasta 6 celdas habitadas y 6 instalaciones priorizadas; los totales incluyen todo el entorno. " : ""}Azul: población; gris: instalaciones; ámbar: a favor del viento válido. ${context.method} El inventario OSM no es exhaustivo y puede representar un complejo con varios elementos. ${context.landcover.missing_cells ? `${context.landcover.missing_cells} celdas sin cobertura de suelo. ` : ""}Los datos de distintas fechas no describen una observación simultánea.`;
    $("context-soils").textContent = Object.entries(context.landcover.percentages).map(([name, value]) => `${soils[name]}: ${value == null ? "sin dato" : `${number(value, 1)} %`}`).join(" · ");
    $("context-sources").textContent = Object.values(context.sources).filter(value => !value.startsWith("/")).join(". ");
    $("context-data").hidden = false;
    $("context-focus").disabled = false;
    $("context-toggle").disabled = false;
    $("context-retry").hidden = true;
    draw();
  }

  function clear() {
    request++; context = null; incident = null;
    $("context-data").hidden = true;
    $("context-focus").disabled = true;
    $("context-toggle").disabled = true;
    $("context-retry").hidden = true;
    $("context-summary").classList.remove("attention");
    $("context-summary").textContent = "Contexto pendiente de actualización.";
    layer.clearLayers(); markers.clear();
  }

  async function load(next) {
    clear(); incident = next;
    const token = request;
    $("context-summary").textContent = "Consultando el entorno…";
    try {
      const response = await fetch(`/api/context?id=${encodeURIComponent(next.id)}`);
      if (!response.ok) throw new Error("Contexto no disponible");
      const result = await response.json();
      if (token !== request) return;
      if (result.incident_id !== next.id) throw new Error("Zona distinta");
      context = result; render();
    } catch {
      if (token !== request) return;
      context = null; layer.clearLayers();
      $("context-data").hidden = true;
      $("context-summary").textContent = "Contexto no disponible. No implica ausencia de riesgo.";
      $("context-retry").hidden = false;
    }
  }

  $("context-toggle").onchange = draw;
  $("context-retry").onclick = () => { if (incident) load(incident); };
  $("context-focus").onclick = () => {
    if (!context || !incident) return;
    $("context-toggle").checked = true;
    onFocus();
    const bounds = L.geoJSON(incident.footprint).getBounds();
    for (const point of context.points) bounds.extend([point.lat, point.lon]);
    map.fitBounds(bounds.pad(.2), { maxZoom: 13, paddingTopLeft: [35, 140], paddingBottomRight: [35, 75], animate: false });
    draw();
  };
  map.on("zoomend", draw);
  return { load, clear, setVisible(value) { visible = value; draw(); } };
}
