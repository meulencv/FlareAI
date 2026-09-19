import { createHeatLayer } from "./heat.js";

export function selectionBounds(incident, radius = 5) {
  const geometry = incident.footprint;
  const points = geometry.type === "Polygon" ? geometry.coordinates.flat() : geometry.coordinates.flat(2);
  const lons = points.map(p => p[0]), lats = points.map(p => p[1]);
  const dx = radius / (111.32 * Math.cos(incident.lat * Math.PI / 180)), dy = radius / 111.32;
  return [[Math.min(...lats) - dy, Math.min(...lons) - dx], [Math.max(...lats) + dy, Math.max(...lons) + dx]];
}

export function potentialLabel(context) {
  if (context.potential.status === "unavailable") return "Riesgo inmediato · sin cobertura suficiente";
  if (!context.potential.samples.some(sample => Number.isFinite(sample.score) && sample.score > 0)) {
    return "Riesgo inmediato · sin señal suficiente";
  }
  if (context.wind.status === "historical") return "Riesgo inmediato · contexto histórico";
  if (["stale", "missing", "calm"].includes(context.wind.status)) return "Riesgo inmediato · sin viento actual";
  return "Riesgo inmediato alrededor";
}

export function createContextView({ map, document, fetch, canvas, onFocus = () => {}, onContext = () => {} }) {
  const $ = id => document.getElementById(id);
  const tip = $("heat-tip");
  let context = null, request = 0, visible = true;
  const attribution = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a> · INE/Eurostat 2021 · Copernicus 2019';

  const heat = createHeatLayer({ map, canvas, document, onHover(hovered) {
    if (!hovered || !hovered.text || !visible || !context || map.getContainer?.()?.classList?.contains("place-open")) { tip.hidden = true; return; }
    tip.textContent = hovered.text;
    tip.style.transform = `translate(${hovered.point.x}px, ${hovered.point.y}px)`;
    tip.hidden = false;
  } });

  function paint() {
    onContext(visible ? context : null);
    $("potential-key").hidden = !visible || !context;
    tip.hidden = true;
    if (!context || !visible) {
      heat.clear();
      map.attributionControl?.removeAttribution(attribution);
      return;
    }
    $("potential-status").textContent = potentialLabel(context);
    const scored = context.potential.samples.filter(sample => Number.isFinite(sample.score) && sample.score > 0);
    $("potential-key").classList.toggle("no-signal", !scored.length);
    $("potential-key").title = "Intensidad orientativa de revisión, no probabilidad de incendio. Pasa el ratón para ver qué hay. Población 2021 · suelo 2019 · OSM 2026.";
    heat.set(context.potential.samples, context);
    if (scored.length) map.attributionControl?.addAttribution(attribution);
    else map.attributionControl?.removeAttribution(attribution);
  }

  function clear() {
    request++; context = null;
    onContext(null);
    heat.clear();
    map.attributionControl?.removeAttribution(attribution);
    tip.hidden = true;
    $("potential-key").hidden = true;
    $("potential-key").classList.remove("no-signal");
  }

  async function load(incident, { focus = false } = {}) {
    clear();
    const token = request;
    if (focus) {
      onFocus();
      map.fitBounds(selectionBounds(incident), {
        maxZoom: 12.5, paddingTopLeft: [24, 170], paddingBottomRight: [24, 90], animate: false,
      });
    }
    $("potential-key").hidden = !visible;
    $("potential-status").textContent = "Analizando entorno…";
    try {
      const response = await fetch(`/api/context?id=${encodeURIComponent(incident.id)}`);
      if (!response.ok) throw new Error("Contexto no disponible");
      const result = await response.json();
      if (token !== request) return;
      if (result.incident_id !== incident.id || !result.potential?.samples) throw new Error("Contexto inválido");
      context = result; paint();
    } catch {
      if (token !== request) return;
      context = null; heat.clear();
      $("potential-key").hidden = !visible;
      $("potential-key").classList.add("no-signal");
      $("potential-status").textContent = "Riesgo inmediato · no disponible";
      $("potential-key").title = "Reintentamos en la siguiente actualización. No implica ausencia de riesgo.";
    }
  }

  return { load, clear, setVisible(value) {
    if (visible === value) return;
    visible = value;
    paint();
  } };
}
