import { fireDisplayScale } from "./flames.js";

export const facilitiesVisible = zoom => zoom >= 13;

export function fireExclusionBoxes(incidents, project) {
  return incidents.map(incident => {
    const geometry = incident.footprint;
    const coordinates = geometry.type === "Polygon" ? geometry.coordinates.flat() : geometry.coordinates.flat(2);
    const points = coordinates.map(([lon, lat]) => project([lat, lon]));
    const center = project([incident.lat, incident.lon]);
    const extent = Math.max(.0001, ...points.map(p => Math.hypot(p.x - center.x, p.y - center.y)));
    const scale = fireDisplayScale(extent);
    return { left: Math.min(...points.map(p => center.x + (p.x - center.x) * scale)) - 30,
      right: Math.max(...points.map(p => center.x + (p.x - center.x) * scale)) + 30,
      top: Math.min(...points.map(p => center.y + (p.y - center.y) * scale)) - 30,
      bottom: Math.max(...points.map(p => center.y + (p.y - center.y) * scale)) + 30 };
  });
}

export const obscuresFire = (p, boxes) => boxes.some(b => p.x >= b.left && p.x <= b.right && p.y >= b.top && p.y <= b.bottom);

const CATEGORIES = {
  combustibles_quimica: ["Combustibles / química", "tank"], gasolinera: ["Gasolinera", "fuel"],
  central_combustion: ["Central de combustión", "power"], aeropuerto_aerodromo: ["Aeropuerto / aeródromo", "air"],
  helipuerto: ["Helipuerto", "air"], puerto: ["Puerto", "port"], puerto_deportivo: ["Puerto deportivo", "port"],
  fabrica: ["Fábrica", "factory"], area_industrial: ["Área industrial", "factory"],
  vertedero: ["Vertedero", "waste"], gestion_residuos: ["Centro de residuos", "waste"],
};
const PATHS = {
  camera: '<rect x="3" y="6" width="18" height="14" rx="3"/><path d="m8 6 2-3h4l2 3"/><circle cx="12" cy="13" r="3"/>',
  fuel: '<path d="M4 21V4h9v17M2 21h13M6 7h5v5H6zM13 14h3v4a2 2 0 0 0 4 0V8l-3-3M18 6v5h2"/>',
  factory: '<path d="M3 21V11l6-4v5l6-4v13zM17 21V3h3l1 18M6 16h1m4 0h1"/>',
  tank: '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 4 14 4 14 0V6M5 12c0 4 14 4 14 0"/>',
  power: '<path d="m13 2-8 12h6l-1 8 9-13h-7z"/>',
  air: '<path d="M12 2v20M3 12l9-5 9 5M8 21l4-3 4 3"/>',
  port: '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M8 11h8M3 14c0 9 18 9 18 0M1 16l2-2 2 2m14 0 2-2 2 2"/>',
  waste: '<path d="M5 7h14M9 7V4h6v3M7 7l1 14h8l1-14M10 10v7m4-7v7"/>',
};
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true">${PATHS[name] || PATHS.factory}</svg>`;
const WASTE_CATEGORIES = new Set(["vertedero", "gestion_residuos"]);
export const FACILITY_LIMIT = 2, FACILITY_TOTAL = 8;
const family = poi => CATEGORIES[poi.category]?.[1] || "factory";
const rank = poi => [poi.priority === "alta_orientativa" ? 0 : 1, Number.isFinite(poi.distance_km) ? poi.distance_km : Infinity];
const compare = (a, b) => { const [pa, da] = rank(a), [pb, db] = rank(b); return pa - pb || da - db; };

// Muestra representativa: como mucho FACILITY_LIMIT por familia de icono y FACILITY_TOTAL en total,
// priorizando prioridad alta orientativa y cercanía; residuos solo con prioridad alta.
export function relevantFacilities(facilities) {
  const slots = new Map(), chosen = [];
  for (const poi of [...facilities].filter(poi => !WASTE_CATEGORIES.has(poi.category) || poi.priority === "alta_orientativa").sort(compare)) {
    const slot = slots.get(family(poi)) || 0;
    if (slot >= FACILITY_LIMIT) continue;
    slots.set(family(poi), slot + 1); chosen.push({ poi, slot });
  }
  const kept = new Set(chosen.sort((a, b) => a.slot - b.slot || compare(a.poi, b.poi)).slice(0, FACILITY_TOTAL).map(c => c.poi.id));
  return facilities.filter(poi => kept.has(poi.id));
}
const number = value => Number(value).toLocaleString("es-ES", { maximumFractionDigits: 2 });

export function roadEvents(events) {
  const stable = { ...events };
  delete stable.viewprereset;
  return stable;
}

export function camerasVisible(zoom) {
  return zoom >= 10;
}

export function safeLink(value) {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}

export function groupPlaces(points, project, size = 64) {
  const groups = new Map();
  for (const point of points) {
    const p = project([point.lat, point.lon]);
    const key = size ? `${Math.floor(p.x / size)}:${Math.floor(p.y / size)}` : `${point.lat}:${point.lon}`;
    if (!groups.has(key)) groups.set(key, { items: [], lat: 0, lon: 0 });
    const group = groups.get(key);
    group.items.push(point); group.lat += point.lat; group.lon += point.lon;
  }
  return [...groups.values()].map(g => ({ ...g, lat: g.lat / g.items.length, lon: g.lon / g.items.length }));
}

export function facilityDetails(poi, wind) {
  const [category, symbol] = CATEGORIES[poi.category] || ["Instalación", "factory"];
  return {
    name: poi.name || category, category, icon: symbol,
    distance: Number.isFinite(poi.distance_km) ? `${number(poi.distance_km)} km de la huella térmica` : "Distancia no disponible",
    priority: poi.priority === "alta_orientativa" ? "Prioridad alta orientativa" : "Prioridad de revisión",
    wind: wind.status === "current" ? (poi.downwind ? "En dirección del viento actual" : "Fuera del sector del viento actual")
      : wind.status === "historical" ? "Orientación histórica, no aviso actual" : "Sin viento actual válido",
  };
}

export function createInfrastructure({ map, L, document, fetch }) {
  const facilities = L.layerGroup().addTo(map), cameras = L.layerGroup().addTo(map);
  let context = null, catalog = null, active = null, sequence = 0, timer = null, repaint = null, fires = [];
  const status = document.getElementById("infrastructure-status");
  const problems = new Map();
  function problem(key, message) {
    if (message) problems.set(key, message); else problems.delete(key);
    status.textContent = [...problems.values()].join(" · ");
    status.hidden = !problems.size;
  }
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  function link(parent, text, value) {
    const url = safeLink(value);
    if (!url) return;
    const node = make("a", text); node.href = url; node.target = "_blank"; node.rel = "noopener noreferrer";
    parent.append(node);
  }
  function stopMedia() {
    sequence++; clearInterval(timer); timer = null;
    if (active) active.node.querySelectorAll("iframe, img").forEach(node => node.remove());
    active = null;
    document.getElementById("map").classList.remove("place-open");
  }
  function popup(item, type) {
    if (active) map.closePopup(active.popup);
    stopMedia();
    const root = make("section", null, "place-card");
    const shown = L.popup({ className: "place-popup", maxWidth: 360, minWidth: 230,
      autoPanPaddingTopLeft: [20, 100], autoPanPaddingBottomRight: [20, 110] })
      .setLatLng([item.lat, item.lon]).setContent(root).openOn(map);
    active = { popup: shown, node: root, type };
    document.getElementById("map").classList.add("place-open");
    shown.on("remove", () => { if (active?.popup === shown) stopMedia(); });
    return root;
  }
  function facility(poi) {
    const root = popup(poi, "facility"), detail = facilityDetails(poi, context?.wind || {});
    root.append(make("p", detail.category, "place-eyebrow"), make("h3", detail.name), make("p", detail.distance, "place-distance"));
    root.append(make("p", detail.priority), make("p", poi.reason || "Actividad publicada en OpenStreetMap."), make("p", detail.wind));
    root.append(make("p", `OSM ${poi.source_date || "2026-09-18"} · ${poi.coordinate_method || "posición representativa"}. Riesgo oficial no evaluado. No confirma afección.`, "place-note"));
    link(root, "Ver instalación en OpenStreetMap ↗", poi.source_url);
    active.popup.update();
  }
  function camera(item) {
    const root = popup(item, "camera"), token = sequence;
    const source = catalog?.sources.find(s => s.id === item.source);
    root.append(make("p", source?.name || item.source, "place-eyebrow"), make("h3", item.name), make("p", item.place));
    const media = make("div", null, "camera-media"), message = make("p", "Consultando imagen…", "place-note");
    message.setAttribute("role", "status");
    root.append(media, message);
    const updated = source?.updatedAt || source?.checkedAt;
    root.append(make("p", `Catálogo ${updated ? new Date(updated).toLocaleString("es-ES") : "sin fecha"}. Ubicación publicada, no verificada sobre el terreno.`, "place-note"));
    if (item.coordinateNote) root.append(make("p", item.coordinateNote, "place-note"));
    link(root, "Fuente y autoría ↗", item.pageUrl);
    link(root, "Condiciones de la fuente ↗", source?.licenseUrl);
    let loading = false;
    function unavailable(text) {
      if (token !== sequence) return;
      clearInterval(timer); timer = null;
      media.replaceChildren(); message.textContent = text;
      catalog.cameras = catalog.cameras.filter(camera => camera.id !== item.id);
      render(); active.popup.update();
    }
    async function load() {
      if (loading || token !== sequence || document.hidden) return;
      loading = true;
      try {
        const response = await fetch(`/api/webcam?id=${encodeURIComponent(item.id)}`);
        if (!response.ok) throw new Error("Cámara no disponible. Se oculta del mapa hasta una nueva comprobación.");
        const result = await response.json();
        if (token !== sequence) return;
        if (result.verification_pending) throw new Error("Cámara pendiente de comprobar la reproducción. Se oculta temporalmente.");
        if (result.kind === "snapshot") {
          if (!/^\/territorial\/[a-f0-9]{24}\.img$/.test(result.url)) throw new Error("Imagen no válida");
          const image = make("img"); image.alt = `Captura de ${item.name}`;
          image.onload = () => { if (token === sequence) { media.replaceChildren(image); active.popup.update(); } };
          image.onerror = () => unavailable("No se pudo mostrar la captura. Cámara oculta temporalmente.");
          image.src = `${result.url}?v=${encodeURIComponent(result.fetched_at)}`;
          const modified = result.source_modified ? new Date(result.source_modified) : null;
          const old = modified && Date.now() - modified.getTime() > 1800000;
          message.textContent = `${result.offline ? "Copia offline" : "Captura periódica, no vídeo"}. Recuperada ${new Date(result.fetched_at).toLocaleString("es-ES")}. ${modified && Number.isFinite(modified.getTime()) ? `Modificada en origen: ${modified.toLocaleString("es-ES")}. ` : ""}${old ? "Imagen antigua. " : ""}La hora de recuperación no garantiza la hora de captura.`;
        } else if (safeLink(result.player_url)) {
          const frame = make("iframe"); frame.title = item.name;
          frame.referrerPolicy = "no-referrer";
          frame.setAttribute("sandbox", "allow-scripts allow-same-origin allow-presentation");
          frame.setAttribute("allow", "autoplay; fullscreen; picture-in-picture"); frame.src = result.player_url;
          media.replaceChildren(frame);
          message.textContent = "Reproductor del proveedor. La disponibilidad y la emisión dependen de la fuente.";
        } else {
          unavailable("La fuente no publica una cámara integrable. Se retira del mapa.");
        }
      } catch (error) {
        unavailable(error.message);
      } finally {
        loading = false;
        if (token === sequence) active.popup.update();
      }
    }
    if (item.kind === "snapshot") {
      load(); timer = setInterval(load, Math.max(30, item.refreshSeconds || 180) * 1000);
    } else if (item.kind === "player") {
      const button = make("button", "Ver cámara", "camera-play");
      message.textContent = "Al abrir el vídeo contactas con el proveedor, que puede usar cookies.";
      button.onclick = () => { button.remove(); load(); };
      media.append(button);
    } else unavailable("Cámara sin medio integrable.");
    active.popup.update();
  }
  function grouped(group, type) {
    const latitudes = group.items.map(p => p.lat), longitudes = group.items.map(p => p.lon);
    if (map.getZoom() < 15 && (Math.max(...latitudes) !== Math.min(...latitudes) || Math.max(...longitudes) !== Math.min(...longitudes))) {
      map.fitBounds(group.items.map(p => [p.lat, p.lon]), { maxZoom: Math.min(16, map.getZoom() + 3), padding: [70, 150], animate: false });
      return;
    }
    const root = popup(group, type);
    root.append(make("h3", `${group.items.length} ${type === "camera" ? "cámaras" : "instalaciones"}`));
    const list = make("div", null, "place-choices");
    for (const item of group.items) {
      const button = make("button", item.name || CATEGORIES[item.category]?.[0] || "Instalación");
      button.onclick = () => type === "camera" ? camera(item) : facility(item);
      list.append(button);
    }
    root.append(list);
    active.popup.update();
  }
  function draw(points, layer, type) {
    layer.clearLayers();
    if (type === "facility" && !facilitiesVisible(map.getZoom())) return;
    const bounds = map.getBounds().pad(.05);
    const exclusions = fireExclusionBoxes(fires, p => map.latLngToContainerPoint(p));
    const visible = points.filter(p => bounds.contains([p.lat, p.lon]) && !obscuresFire(map.latLngToContainerPoint([p.lat, p.lon]), exclusions));
    const groups = groupPlaces(visible, p => map.project(p, map.getZoom()), map.getZoom() >= 14 ? 0 : type === "camera" ? 76 : 42);
    for (const group of groups) {
      if (obscuresFire(map.latLngToContainerPoint([group.lat, group.lon]), exclusions)) continue;
      const single = group.items.length === 1, item = group.items[0];
      const name = single ? item.name || CATEGORIES[item.category]?.[0] || "Instalación" : `${group.items.length} ${type === "camera" ? "cámaras" : "instalaciones"}`;
      const symbol = type === "camera" ? "camera" : facilityDetails(item, {}).icon;
      const marker = L.marker([group.lat, group.lon], { pane: "infrastructure", title: name, alt: name,
        icon: L.divIcon({ className: `place-marker ${type}${single ? "" : " is-group"}`, iconSize: [30, 30], iconAnchor: [15, 15],
          html: icon(symbol) + (single ? "" : `<b>${group.items.length}</b>`) }) });
      marker.on("click", () => {
        document.getElementById("heat-tip").hidden = true;
        if (!single) grouped(group, type); else if (type === "camera") camera(item); else facility(item);
      });
      marker.addTo(layer);
    }
  }
  function render() {
    if (catalog && camerasVisible(map.getZoom())) draw(catalog.cameras.filter(c => ["snapshot", "player"].includes(c.kind)), cameras, "camera");
    else {
      cameras.clearLayers();
      if (active?.type === "camera") map.closePopup(active.popup);
    }
    draw(relevantFacilities(context?.potential.facilities || []), facilities, "facility");
  }
  map.createPane("infrastructure"); map.getPane("infrastructure").style.zIndex = 470;
  map.on("zoom", () => {
    if (!facilitiesVisible(map.getZoom())) {
      facilities.clearLayers();
      if (active?.type === "facility") map.closePopup(active.popup);
    }
    if (!camerasVisible(map.getZoom())) {
      cameras.clearLayers();
      if (active?.type === "camera") map.closePopup(active.popup);
    }
  });
  map.on("moveend zoomend resize", () => { clearTimeout(repaint); repaint = setTimeout(render, 100); });
  map.createPane("roads"); map.getPane("roads").style.zIndex = 403; map.getPane("roads").style.pointerEvents = "none";
  const StableRoadLayer = L.TileLayer.extend({
    getEvents() { return roadEvents(L.TileLayer.prototype.getEvents.call(this)); },
  });
  const roads = new StableRoadLayer("/roads/{z}/{x}/{y}.png", { pane: "roads", opacity: .48, minZoom: 4, maxZoom: 16,
    bounds: [[27, -19], [44.5, 5]], noWrap: true, updateWhenIdle: true,
    attribution: 'Carreteras © <a href="https://www.scne.es" target="_blank" rel="noopener">SCNE/IGN</a> · CC BY 4.0' });
  let tileFailed = false;
  roads.on("loading", () => { tileFailed = false; });
  roads.on("tileerror", () => { tileFailed = true; problem("roads", "Carreteras: cobertura no disponible en parte de esta vista"); });
  roads.on("load", () => { if (!tileFailed) problem("roads", null); });
  roads.addTo(map);
  let loadingCatalog = false, attributed = false, catalogAt = 0;
  async function loadCatalog() {
    if (loadingCatalog) return;
    loadingCatalog = true;
    try {
      const response = await fetch("/api/webcams");
      if (!response.ok) throw new Error("Catálogo no disponible");
      const result = await response.json();
      if (!Array.isArray(result.cameras) || !Array.isArray(result.sources)) throw new Error("Catálogo inválido");
      catalog = result; catalogAt = Date.now();
      if (!attributed) {
        map.attributionControl.addAttribution('<a href="/webcams/sources" target="_blank" rel="noopener">Cámaras públicas · fuentes y cobertura parcial</a>');
        attributed = true;
      }
      render(); problem("cameras", null);
    } catch { problem("cameras", "Cámaras: catálogo no disponible"); }
    finally { loadingCatalog = false; }
  }
  setInterval(() => { if (!document.hidden) loadCatalog(); }, 60000);
  return {
    setIncidents(value) { fires = value; render(); },
    setContext(value) {
      context = value;
      if (active?.type === "facility") map.closePopup(active.popup);
      facilities.clearLayers();
      if (context) draw(relevantFacilities(context.potential.facilities), facilities, "facility");
    },
    cameras: () => Date.now() - catalogAt < 70000 ? catalog?.cameras || [] : [],
    openCamera: camera,
    load: loadCatalog,
  };
}
