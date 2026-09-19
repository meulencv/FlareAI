import L from 'leaflet';
import Supercluster from 'supercluster';
import 'leaflet/dist/leaflet.css';
import './style.css';
import { type Camera, type Catalog, catalogSchema, distanceKm, inSpainBounds, normalize } from './model.ts';
import { places } from './places.ts';

function el<T extends HTMLElement = HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) throw new Error(`Elemento no encontrado: ${id}`);
  return node as T;
}
const escape = (s: string): string => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] || c));
const number = (n: number): string => new Intl.NumberFormat('es-ES').format(n);
const date = (s?: string): string => s ? new Date(s).toLocaleString('es-ES') : 'No disponible';
const colors: Record<string, string> = { traffic: '#527e9a', landscape: '#328a68', tourism: '#c48948' };
const categories = { traffic: 'Tráfico', landscape: 'Paisaje', tourism: 'Turismo' };
const map = L.map('map', { zoomControl: false, minZoom: 4, maxZoom: 18 }).setView([39.9, -3.8], 6);
L.control.zoom({ position: 'bottomright' }).addTo(map);
const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19,
}).addTo(map);
tiles.on('tileerror', () => {
  el('map-warning').hidden = false;
  el('map-warning').textContent = 'No se han cargado algunas teselas. La lista de cámaras sigue disponible.';
});
const markers = L.layerGroup().addTo(map);
const pointLayer = L.layerGroup().addTo(map);
let catalog: Catalog = { cameras: [], sources: [] };
let filtered: Camera[] = [];
let category = 'all';
let point: { lat: number; lon: number; name: string } | null = null;
let selected: Camera | null = null;
let search = '';
let visibleLimit = 60;
let cluster = new Supercluster<{ cameraId: string; category: string }>({ radius: 44, maxZoom: 16 }).load([]);
let timer: ReturnType<typeof setTimeout> | undefined;
let imageController: AbortController | undefined;
let imageObjectUrl: string | undefined;
let playerController: AbortController | undefined;
let toastTimer: ReturnType<typeof setTimeout>;
let favorites = new Set<string>();
try {
  const raw: unknown = JSON.parse(localStorage.getItem('faro-favorites') || '[]');
  if (Array.isArray(raw)) favorites = new Set(raw.filter((v): v is string => typeof v === 'string'));
} catch { /* Local storage may be unavailable in private browsing. */ }

function toast(message: string): void {
  clearTimeout(toastTimer);
  el('toast').textContent = message;
  el('toast').hidden = false;
  toastTimer = setTimeout(() => { el('toast').hidden = true; }, 5000);
}
function sourceName(camera: Camera): string {
  return catalog.sources.find(s => s.id === camera.source)?.name || camera.source;
}
function cameraFromHash(): Camera | undefined {
  try {
    const id = decodeURIComponent(location.hash.slice(1));
    return catalog.cameras.find(c => c.id === id);
  } catch {
    return undefined;
  }
}
function distanceLabel(camera: Camera): string {
  if (!point) return camera.kind === 'snapshot' ? 'Captura' : camera.kind === 'link' ? 'Enlace' : 'Reproductor';
  const km = distanceKm(point, camera);
  return km < 1 ? `${Math.round(km * 1000)} m` : `${km.toLocaleString('es-ES', { maximumFractionDigits: 1 })} km`;
}
function updateFavorites(): void {
  el('favorite-total').textContent = String(favorites.size);
  if (selected) {
    const button = document.getElementById('favorite');
    if (button) {
      button.textContent = favorites.has(selected.id) ? '★ Guardada' : '☆ Guardar';
      button.setAttribute('aria-pressed', String(favorites.has(selected.id)));
    }
  }
}

function applyFilters(): void {
  const source = el<HTMLSelectElement>('source-filter').value;
  const radius = Number(el<HTMLSelectElement>('radius').value);
  const favoritesOnly = el<HTMLInputElement>('favorites-only').checked;
  filtered = catalog.cameras.filter(c =>
    (category === 'all' || c.category === category)
    && (!source || c.source === source)
    && (!search || normalize(`${c.name} ${c.place} ${sourceName(c)}`).includes(search))
    && (!favoritesOnly || favorites.has(c.id))
    && (!point || !radius || distanceKm(point, c) <= radius),
  );
  cluster = new Supercluster<{ cameraId: string; category: string }>({ radius: 44, maxZoom: 16 });
  cluster.load(filtered.map(c => ({
    type: 'Feature', geometry: { type: 'Point', coordinates: [c.lon, c.lat] },
    properties: { cameraId: c.id, category: c.category },
  })));
  visibleLimit = 60;
  renderMarkers();
  renderList();
  drawPoint();
}

function renderMarkers(): void {
  markers.clearLayers();
  const bounds = map.getBounds();
  const features = cluster.getClusters([bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()], Math.floor(map.getZoom()));
  for (const feature of features) {
    const [lon, lat] = feature.geometry.coordinates;
    const properties = feature.properties;
    if ('cluster' in properties && properties.cluster) {
      const marker = L.marker([lat, lon], {
        icon: L.divIcon({
          className: 'cluster-marker',
          html: `<span>${number(properties.point_count)}</span>`,
          iconSize: [44, 44], iconAnchor: [22, 22],
        }),
        title: `${properties.point_count} cámaras. Acercar.`,
      });
      marker.on('click', () => map.setView([lat, lon], cluster.getClusterExpansionZoom(properties.cluster_id)));
      marker.addTo(markers);
    } else {
      const c = catalog.cameras.find(camera => camera.id === properties.cameraId);
      if (!c) continue;
      const marker = L.marker([lat, lon], {
        icon: L.divIcon({
          className: `camera-marker${selected?.id === c.id ? ' is-selected' : ''}`,
          html: `<span style="--marker-color:${colors[c.category]}"></span>`,
          iconSize: [24, 24], iconAnchor: [12, 12],
        }),
        title: c.name,
      });
      marker.bindTooltip(escape(c.name), { direction: 'top' });
      marker.on('click', () => selectCamera(c));
      marker.addTo(markers);
    }
  }
}

function renderList(): void {
  const bounds = map.getBounds();
  const cameras = point ? [...filtered].sort((a, b) => distanceKm(point!, a) - distanceKm(point!, b))
    : filtered.filter(c => bounds.contains([c.lat, c.lon]));
  el('result-count').textContent = `${number(cameras.length)} webcams`;
  el('result-subtitle').textContent = point ? 'Ordenadas por distancia en línea recta' : 'En esta vista del mapa';
  const list = el('camera-list');
  if (!cameras.length) {
    list.innerHTML = `<div class="empty-state"><span class="empty-icon">⌖</span><h3>No hay cámaras aquí</h3><p>Amplía el mapa, aumenta el radio o cambia los filtros. La cobertura depende de los catálogos disponibles.</p></div>`;
    return;
  }
  list.innerHTML = cameras.slice(0, visibleLimit).map(c => `
    <button class="camera-card${c.id === selected?.id ? ' active' : ''}" data-camera="${escape(c.id)}">
      <span class="card-icon ${c.category}">${c.kind === 'snapshot' ? '▣' : c.kind === 'link' ? '↗' : '▷'}</span>
      <span class="card-content"><span class="card-source">${escape(sourceName(c))}${favorites.has(c.id) ? ' · ★' : ''}</span><strong>${escape(c.name)}</strong><span class="card-place">${escape(c.place)}</span></span>
      <span class="card-distance">${distanceLabel(c)}<span aria-hidden="true">↗</span></span>
    </button>`).join('');
  if (cameras.length > visibleLimit) {
    const more = document.createElement('button');
    more.className = 'more-button';
    more.textContent = `Mostrar más (${number(cameras.length - visibleLimit)} restantes)`;
    more.addEventListener('click', () => { visibleLimit += 60; renderList(); });
    list.append(more);
  }
}
el('camera-list').addEventListener('click', event => {
  const button = (event.target as HTMLElement).closest<HTMLElement>('[data-camera]');
  const camera = catalog.cameras.find(c => c.id === button?.dataset.camera);
  if (camera) selectCamera(camera);
});

function drawPoint(): void {
  pointLayer.clearLayers();
  el('point-banner').hidden = !point;
  if (!point) return;
  el('point-banner').innerHTML = `<span><strong>⌖ ${escape(point.name)}</strong><small>${point.lat.toFixed(5)}, ${point.lon.toFixed(5)}</small></span><button id="clear-point" aria-label="Quitar punto de búsqueda">×</button>`;
  el('clear-point').addEventListener('click', () => { point = null; applyFilters(); });
  L.marker([point.lat, point.lon], {
    icon: L.divIcon({ className: 'search-point', html: '<span></span>', iconSize: [26, 26], iconAnchor: [13, 13] }),
    title: point.name, interactive: false,
  }).addTo(pointLayer);
  const radius = Number(el<HTMLSelectElement>('radius').value);
  if (radius) L.circle([point.lat, point.lon], { radius: radius * 1000, color: '#2b7055', weight: 1.5, dashArray: '5 5', fillOpacity: 0.04, interactive: false }).addTo(pointLayer);
}
function setPoint(lat: number, lon: number, name: string, fly = false): void {
  point = { lat, lon, name };
  if (fly) map.setView([lat, lon], 11);
  applyFilters();
}
map.on('click', (e: L.LeafletMouseEvent) => setPoint(e.latlng.lat, e.latlng.lng, 'Punto seleccionado'));
map.on('moveend', () => { renderMarkers(); renderList(); });

function releaseMedia(): void {
  clearTimeout(timer);
  imageController?.abort();
  playerController?.abort();
  if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
  imageObjectUrl = undefined;
}
function closeInspector(): void {
  releaseMedia();
  selected = null;
  el('inspector').hidden = true;
  el('inspector').replaceChildren();
  history.replaceState(null, '', location.pathname + location.search);
  renderMarkers();
  renderList();
}

async function refreshImage(camera: Camera): Promise<void> {
  if (selected?.id !== camera.id || document.hidden) return;
  imageController?.abort();
  const controller = new AbortController();
  imageController = controller;
  clearTimeout(timer);
  const frame = el('media');
  el('image-status').textContent = 'Consultando al proveedor…';
  try {
    const response = await fetch(`/api/cameras/${encodeURIComponent(camera.id)}/image?t=${Date.now()}`, { signal: controller.signal });
    if (!response.ok) throw new Error('No se puede consultar esta cámara ahora.');
    const blob = await response.blob();
    if (selected?.id !== camera.id || controller.signal.aborted) return;
    if (imageObjectUrl) URL.revokeObjectURL(imageObjectUrl);
    imageObjectUrl = URL.createObjectURL(blob);
    const image = new Image();
    image.alt = `Última imagen publicada: ${camera.name}`;
    image.src = imageObjectUrl;
    await image.decode();
    if (selected?.id !== camera.id || controller.signal.aborted) return;
    frame.replaceChildren(image);
    const modified = response.headers.get('X-Source-Last-Modified');
    const fetched = response.headers.get('X-Fetched-At') || new Date().toISOString();
    const stale = modified && Date.now() - Date.parse(modified) > 30 * 60000;
    el('image-status').textContent = stale ? 'Atención: imagen con más de 30 minutos' : 'Imagen recibida · fecha de captura no garantizada';
    el('image-status').classList.toggle('stale', Boolean(stale));
    el('image-meta').innerHTML = `<span>Recuperada: ${escape(date(fetched))}</span><span>Modificada en origen: ${escape(date(modified || undefined))}</span>${camera.imageTimestamp ? `<span>Captura según MeteoGalicia: ${escape(camera.imageTimestamp.replace('T', ' '))} (hora peninsular)</span>` : ''}`;
  } catch {
    if (controller.signal.aborted || selected?.id !== camera.id) return;
    frame.innerHTML = '<div class="media-message"><span>⊘</span><strong>Imagen no disponible</strong><p>El proveedor no responde o la cámara está fuera de servicio. Prueba más tarde o abre la fuente original.</p></div>';
    el('image-status').textContent = 'No disponible en esta consulta';
    el('image-meta').textContent = `Consulta: ${date(new Date().toISOString())}`;
  } finally {
    if (selected?.id === camera.id && !controller.signal.aborted && el<HTMLInputElement>('auto-refresh').checked) {
      timer = setTimeout(() => { void refreshImage(camera); }, camera.refreshSeconds * 1000);
    }
  }
}

async function loadPlayer(camera: Camera): Promise<void> {
  playerController?.abort();
  const controller = new AbortController();
  playerController = controller;
  el('media').innerHTML = '<div class="media-message"><span class="loader"></span><p>Buscando el reproductor público…</p></div>';
  try {
    const response = await fetch(`/api/cameras/${encodeURIComponent(camera.id)}/player`, { signal: controller.signal });
    if (!response.ok) throw new Error('No disponible');
    const result: { url: string | null } = await response.json();
    if (selected?.id !== camera.id || controller.signal.aborted) return;
    if (!result.url) throw new Error('Sin reproductor integrable');
    const iframe = document.createElement('iframe');
    iframe.src = result.url;
    iframe.title = camera.name;
    iframe.allow = 'autoplay; fullscreen; picture-in-picture';
    iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-presentation allow-popups');
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    iframe.allowFullscreen = true;
    el('media').replaceChildren(iframe);
    el('image-status').textContent = 'Reproductor del proveedor · comprueba su indicador de directo';
  } catch {
    if (controller.signal.aborted || selected?.id !== camera.id) return;
    el('media').innerHTML = '<div class="media-message"><span>↗</span><strong>Disponible en la web de origen</strong><p>Esta cámara no ofrece un reproductor integrable accesible. Usa «Abrir fuente original».</p></div>';
    el('image-status').textContent = 'Visualización externa';
  }
}

function selectCamera(camera: Camera): void {
  releaseMedia();
  selected = camera;
  history.replaceState(null, '', `#${encodeURIComponent(camera.id)}`);
  const inspector = el('inspector');
  inspector.hidden = false;
  const source = catalog.sources.find(s => s.id === camera.source);
  inspector.innerHTML = `
    <div class="inspector-top"><span class="type-badge ${camera.category}">${categories[camera.category]}</span><button id="close-inspector" class="icon-button" aria-label="Cerrar cámara">×</button></div>
    <h2>${escape(camera.name)}</h2><p class="inspector-place">${escape(camera.place)}</p>
    <div id="media" class="media"><div class="media-message"><span>${camera.kind === 'snapshot' ? '▣' : '▷'}</span><strong>${camera.kind === 'snapshot' ? 'Cargando imagen…' : 'Una ventana a este lugar'}</strong>${camera.kind === 'player' ? '<p>Carga el reproductor público del proveedor para ver la cámara.</p><button id="load-player" class="primary-button">Cargar reproductor</button>' : camera.kind === 'link' ? '<p>El proveedor publica un reproductor externo. Usa «Abrir fuente original» para verlo en su página.</p>' : '<span class="loader"></span>'}</div></div>
    <div class="image-info"><strong id="image-status">${camera.kind === 'snapshot' ? 'Captura periódica' : camera.kind === 'link' ? 'Enlace al proveedor · emisión sin verificar' : 'Vídeo de un tercero · sin verificar'}</strong><div id="image-meta"></div></div>
    ${camera.kind === 'snapshot' ? `<div class="refresh-row"><label><input type="checkbox" id="auto-refresh" checked /> Renovar cada ${Math.round(camera.refreshSeconds / 60)} min</label><button id="refresh-image" class="text-button">↻ Consultar</button></div>` : '<p class="provider-note">El reproductor puede mostrar publicidad o no permitir la reproducción aquí.</p>'}
    <a class="source-link" href="${escape(camera.pageUrl)}" target="_blank" rel="noopener noreferrer">Abrir fuente original <span>↗</span></a>
    <div class="camera-actions"><button id="favorite" aria-pressed="false">☆ Guardar</button><button id="share">Copiar enlace</button><button id="nearby">⌖ Cerca de aquí</button></div>
    <div class="metadata"><span>PROCEDENCIA</span><a href="${escape(source?.url || camera.pageUrl)}" target="_blank" rel="noopener noreferrer">${escape(sourceName(camera))} ↗</a><p>${escape(source?.license || '')}</p><p>${camera.lat.toFixed(5)}, ${camera.lon.toFixed(5)} · Ubicación del proveedor</p>${camera.coordinateNote ? `<p>${escape(camera.coordinateNote)}</p>` : ''}<p>Catálogo consultado: ${escape(date(source?.updatedAt))}</p>${source?.status === 'error' ? '<p class="stale">La última sincronización falló; se conservan datos anteriores.</p>' : ''}</div>`;
  el('close-inspector').addEventListener('click', closeInspector);
  el('favorite').addEventListener('click', () => {
    if (favorites.has(camera.id)) favorites.delete(camera.id); else favorites.add(camera.id);
    try { localStorage.setItem('faro-favorites', JSON.stringify([...favorites])); }
    catch { toast('El navegador no permite guardar favoritos de forma permanente.'); }
    updateFavorites();
    applyFilters();
  });
  el('share').addEventListener('click', () => {
    if (!navigator.clipboard) { toast('Copia el enlace desde la barra de direcciones.'); return; }
    void navigator.clipboard.writeText(location.href).then(() => toast('Enlace copiado')).catch(() => toast('Copia el enlace desde la barra de direcciones.'));
  });
  el('nearby').addEventListener('click', () => setPoint(camera.lat, camera.lon, camera.name, true));
  if (camera.kind === 'snapshot') {
    el('refresh-image').addEventListener('click', () => { void refreshImage(camera); });
    el('auto-refresh').addEventListener('change', () => {
      clearTimeout(timer);
      if (el<HTMLInputElement>('auto-refresh').checked) void refreshImage(camera);
    });
    void refreshImage(camera);
  } else if (camera.kind === 'player') {
    el('load-player').addEventListener('click', () => { void loadPlayer(camera); });
  }
  updateFavorites();
  map.setView([camera.lat, camera.lon], Math.max(map.getZoom(), 11));
  if (window.matchMedia('(min-width: 761px)').matches) {
    map.panBy([inspector.offsetWidth / 2, 0], { animate: false });
  }
  renderMarkers();
  renderList();
}

function searchPlaces(): void {
  const value = el<HTMLInputElement>('search').value.trim();
  const coordinate = value.match(/^(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)$/);
  if (coordinate) {
    const lat = Number(coordinate[1]), lon = Number(coordinate[2]);
    if (!inSpainBounds(lat, lon)) { toast('Usa latitud, longitud dentro de España, por ejemplo 40.4168, -3.7038.'); return; }
    search = '';
    el('search-results').hidden = true;
    setPoint(lat, lon, 'Coordenadas', true);
    return;
  }
  search = normalize(value);
  const suggestions = search ? places.filter(p => normalize(p[0]).includes(search)).slice(0, 5) : [];
  const container = el('search-results');
  container.hidden = !suggestions.length;
  container.replaceChildren();
  suggestions.forEach(([name, lat, lon]) => {
    const button = document.createElement('button');
    button.textContent = `⌖ ${name}`;
    button.addEventListener('click', () => {
      el<HTMLInputElement>('search').value = name;
      search = '';
      container.hidden = true;
      setPoint(lat, lon, name, true);
    });
    container.append(button);
  });
  applyFilters();
  if (filtered.length && !suggestions.length) map.fitBounds(L.latLngBounds(filtered.map(c => [c.lat, c.lon])), { maxZoom: 12, padding: [45, 45] });
  if (!filtered.length && !suggestions.length && search) toast('Sin coincidencias. Puedes seleccionar cualquier punto del mapa o introducir coordenadas.');
}
el('search-form').addEventListener('submit', e => { e.preventDefault(); searchPlaces(); });
el<HTMLInputElement>('search').addEventListener('input', () => {
  if (!el<HTMLInputElement>('search').value) { search = ''; el('search-results').hidden = true; applyFilters(); }
});
document.querySelectorAll<HTMLButtonElement>('[data-category]').forEach(button => button.addEventListener('click', () => {
  category = button.dataset.category || 'all';
  document.querySelectorAll<HTMLButtonElement>('[data-category]').forEach(b => {
    b.classList.toggle('selected', b === button);
    b.setAttribute('aria-pressed', String(b === button));
  });
  applyFilters();
}));
['source-filter', 'radius', 'favorites-only'].forEach(id => el(id).addEventListener('change', () => {
  if (id === 'radius' && !point && el<HTMLSelectElement>('radius').value !== '0') {
    const center = map.getCenter();
    point = { lat: center.lat, lon: center.lng, name: 'Centro del mapa' };
    toast('Radio aplicado al centro del mapa. Puedes elegir otro punto con un clic.');
  }
  applyFilters();
}));

el('locate').addEventListener('click', () => {
  if (!navigator.geolocation) { toast('Este navegador no admite geolocalización. Elige un punto del mapa.'); return; }
  toast('Esperando permiso para usar tu ubicación…');
  navigator.geolocation.getCurrentPosition(pos => {
    setPoint(pos.coords.latitude, pos.coords.longitude, 'Mi ubicación', true);
  }, () => toast('No se pudo obtener tu ubicación. Elige un punto en el mapa.'), { timeout: 10000 });
});
el('reset').addEventListener('click', () => {
  category = 'all'; point = null; search = '';
  el<HTMLInputElement>('search').value = '';
  el<HTMLSelectElement>('source-filter').value = '';
  el<HTMLSelectElement>('radius').value = '0';
  el<HTMLInputElement>('favorites-only').checked = false;
  el('search-results').hidden = true;
  document.querySelectorAll<HTMLButtonElement>('[data-category]').forEach(b => {
    b.classList.toggle('selected', b.dataset.category === 'all');
    b.setAttribute('aria-pressed', String(b.dataset.category === 'all'));
  });
  closeInspector();
  document.querySelectorAll<HTMLElement>('[data-region]').forEach(b => b.classList.toggle('region-selected', b.dataset.region === 'peninsula'));
  map.setView([39.9, -3.8], 6);
  applyFilters();
});
const regions: Record<string, [number, number, number]> = {
  peninsula: [39.9, -3.8, 6], baleares: [39.5, 2.8, 8], canarias: [28.35, -15.8, 7], ceuta: [35.4, -4.1, 8],
};
document.querySelectorAll<HTMLButtonElement>('[data-region]').forEach(button => button.addEventListener('click', () => {
  const [lat, lon, zoom] = regions[button.dataset.region || 'peninsula'];
  point = null;
  closeInspector();
  document.querySelectorAll('[data-region]').forEach(b => b.classList.toggle('region-selected', b === button));
  map.setView([lat, lon], zoom);
  applyFilters();
}));
function renderSources(): void {
  el('source-cards').innerHTML = catalog.sources.map(s => `
    <article class="source-card"><div><h3><a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.name)} ↗</a></h3><span class="source-status ${s.status}">${s.status === 'ok' ? 'Catálogo sincronizado' : s.status === 'pending' ? 'Pendiente' : 'Sincronización fallida'}</span></div><strong>${number(s.count)} <small>cámaras</small></strong><p>${escape(s.note)}</p><p class="source-detail">Última sincronización correcta: ${escape(date(s.updatedAt))} · ${number(s.excluded)} registros excluidos</p>${s.error ? `<p class="stale">Se conservan los datos anteriores, si existen. ${escape(s.error)}</p>` : ''}<a class="license" href="${escape(s.licenseUrl)}" target="_blank" rel="noopener noreferrer">${escape(s.license)} ↗</a></article>`).join('');
}
const dialog = el<HTMLDialogElement>('sources-dialog');
['sources-open', 'about-small'].forEach(id => el(id).addEventListener('click', () => { renderSources(); dialog.showModal(); }));
el('sources-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !dialog.open) closeInspector(); });
document.addEventListener('visibilitychange', () => {
  clearTimeout(timer);
  if (!document.hidden && selected?.kind === 'snapshot' && el<HTMLInputElement>('auto-refresh').checked) void refreshImage(selected);
});
window.addEventListener('resize', () => map.invalidateSize());
window.addEventListener('hashchange', () => {
  const camera = cameraFromHash();
  if (camera) selectCamera(camera);
});

async function loadCatalog(initial = false): Promise<void> {
  try {
    const response = await fetch('/api/catalog');
    if (!response.ok) throw new Error('Error de catálogo');
    const raw: unknown = await response.json();
    catalog = catalogSchema.parse(raw);
    const select = el<HTMLSelectElement>('source-filter');
    const value = select.value;
    select.innerHTML = '<option value="">Todas las fuentes</option>' + catalog.sources.map(s => `<option value="${escape(s.id)}">${escape(s.name)} (${number(s.count)})</option>`).join('');
    select.value = value;
    const errors = catalog.sources.filter(s => s.status === 'error');
    el('catalog-total').textContent = `${number(catalog.cameras.length)} catalogadas · ${catalog.sources.filter(s => s.status === 'ok').length} fuentes sincronizadas`;
    if (errors.length) toast(`${errors.length} fuentes sin sincronizar. Consulta «Fuentes y cobertura».`);
    if (selected) {
      const updated = catalog.cameras.find(c => c.id === selected?.id);
      if (updated) Object.assign(selected, updated);
    }
    applyFilters();
    if (initial && location.hash) {
      const camera = cameraFromHash();
      if (camera) selectCamera(camera);
    }
    if (!catalog.cameras.length) {
      el('camera-list').innerHTML = '<div class="empty-state"><span class="loader"></span><h3>Preparando el catálogo</h3><p>Las fuentes se están sincronizando. Esta vista se actualiza automáticamente.</p></div>';
    }
  } catch {
    if (!catalog.cameras.length) el('camera-list').innerHTML = '<div class="empty-state"><h3>No se pudo cargar el catálogo</h3><p>Comprueba la conexión. Se reintentará automáticamente.</p><button id="retry" class="primary-button">Reintentar</button></div>';
    document.getElementById('retry')?.addEventListener('click', () => { void loadCatalog(true); });
    toast('El servidor no responde. Se conservan los datos ya cargados.');
  }
}
updateFavorites();
void loadCatalog(true);
setInterval(() => { if (!document.hidden) void loadCatalog(); }, 60000);
