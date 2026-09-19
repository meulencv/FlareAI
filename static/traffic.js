export const TRAFFIC_LIMIT = 48;
const MIN_ZOOM = 13, RADIUS_KM = .65;

export function trafficProgress(clock, index, count, blocked, congestion = 1) {
  const phase = ((clock / (18 * Math.max(1, congestion)) + index / count) % 1 + 1) % 1;
  return blocked ? Math.min(phase, Math.max(.04, .43 - index * .055)) : phase;
}

export function trafficOpacity(zoom) {
  return Math.max(0, Math.min(1, zoom - MIN_ZOOM));
}

function segmentDistance(coordinates, point) {
  const east = 111.32 * Math.cos(point.lat * Math.PI / 180);
  const [[ax, ay], [bx, by]] = coordinates.map(([lon, lat]) => [(lon - point.lon) * east, (lat - point.lat) * 111.32]);
  const dx = bx - ax, dy = by - ay, length = dx * dx + dy * dy;
  const t = length ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / length)) : 0;
  return Math.hypot(ax + dx * t, ay + dy * t);
}

export function localTrafficRoads(roads, vehicles, blocked = new Set()) {
  if (!vehicles.length) return [];
  return roads.map(road => ({ road, distance: Math.min(...vehicles.map(v => segmentDistance(road.coordinates, v))) }))
    .filter(item => item.distance <= RADIUS_KM)
    .sort((a, b) => Number(blocked.has(b.road.id)) - Number(blocked.has(a.road.id)) || a.distance - b.distance || String(a.road.id).localeCompare(String(b.road.id)))
    .slice(0, TRAFFIC_LIMIT / 2).map(item => item.road);
}

export function trafficRouteRoads(vehicles) {
  const roads = new Map();
  for (const { route } of vehicles) {
    if (!route || route.approximate || route.mode === 'air') continue;
    for (let i = 1; i < route.coordinates.length; i++) {
      const coordinates = route.coordinates.slice(i - 1, i + 1);
      const id = route.edge_ids?.[i - 1] || coordinates.map(p => p.join(',')).sort().join(':');
      roads.set(id, { id, coordinates });
    }
  }
  return [...roads.values()];
}

export function createTraffic({ map, L, document, fetch, getVehicles = () => [] }) {
  const canvas = document.createElement('canvas');
  canvas.className = 'traffic-canvas'; canvas.setAttribute('aria-hidden', 'true');
  map.getPane('mapPane').append(canvas);
  const ctx = canvas.getContext('2d'), reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let roads = [], fallback = [], selected = [], selectedAt = 0, blocked = new Set(), congestion = {}, enabled = false, paused = false;
  let frame = 0, last = 0, lastPaint = 0, clock = 0, timer = 0, generation = 0, controller = null, signature = '', pendingKey = '', session = null;

  function visibleVehicles() {
    if (!Number.isFinite(map.getZoom()) || map.getZoom() <= MIN_ZOOM) return [];
    const bounds = map.getBounds();
    return getVehicles().filter(v => bounds.contains([v.lat, v.lon]));
  }
  function clearRoads() {
    generation++; controller?.abort(); controller = null; pendingKey = ''; signature = ''; roads = [];
    selectedAt = 0; selected = []; canvas.dataset.roads = '0';
  }
  async function load() {
    const vehicles = visibleVehicles();
    if (!enabled || !vehicles.length || document.hidden) { clearRoads(); return; }
    const latPad = RADIUS_KM / 111.32, lonPad = latPad / Math.cos(41.4 * Math.PI / 180);
    const lower = value => Math.floor(value / .004) * .004, upper = value => Math.ceil(value / .004) * .004;
    const box = [Math.max(2.00001, lower(Math.min(...vehicles.map(v => v.lon)) - lonPad)),
      Math.max(41.28001, lower(Math.min(...vehicles.map(v => v.lat)) - latPad)),
      Math.min(2.31999, upper(Math.max(...vehicles.map(v => v.lon)) + lonPad)),
      Math.min(41.53999, upper(Math.max(...vehicles.map(v => v.lat)) + latPad))];
    if (box[0] >= box[2] || box[1] >= box[3]) { clearRoads(); return; }
    const key = box.map(v => v.toFixed(5)).join(',');
    if (key === signature || key === pendingKey) return;
    pendingKey = key;
    controller?.abort(); controller = new globalThis.AbortController();
    const token = ++generation;
    try {
      const response = await fetch(`/api/scenario/roads?bbox=${key}`, { signal: controller.signal });
      if (!response.ok) throw new Error('Red de tráfico no disponible');
      const result = await response.json();
      if (token !== generation) return;
      roads = result.roads; signature = key; selectedAt = 0;
      canvas.dataset.roads = String(roads.length);
      canvas.dataset.status = 'ready';
      paint();
    } catch (error) {
      if (token === generation && error.name !== 'AbortError') canvas.dataset.status = 'unavailable';
    } finally { if (token === generation) pendingKey = ''; }
  }
  function paint() {
    if (!Number.isFinite(map.getZoom())) return;
    const size = map.getSize(), ratio = Math.min(1.5, window.devicePixelRatio || 1);
    const origin = map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(canvas, origin);
    if (canvas.width !== Math.round(size.x * ratio) || canvas.height !== Math.round(size.y * ratio)) {
      canvas.width = Math.round(size.x * ratio); canvas.height = Math.round(size.y * ratio);
      canvas.style.width = size.x + 'px'; canvas.style.height = size.y + 'px';
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, size.x, size.y);
    const vehicles = visibleVehicles(), alpha = vehicles.length ? trafficOpacity(map.getZoom()) : 0;
    canvas.style.opacity = String(alpha);
    if (!alpha) { canvas.dataset.cars = '0'; return; }
    const centres = vehicles.map(v => map.latLngToContainerPoint([v.lat, v.lon]));
    let cars = 0;
    if (!selectedAt || Date.now() - selectedAt > 250) {
      const candidates = new Map([...fallback, ...roads].map(road => [road.id, road]));
      const drawable = [...candidates.values()].filter(road => {
        const [a, b] = road.coordinates.map(([lon, lat]) => map.latLngToContainerPoint([lat, lon]));
        return Math.hypot(b.x - a.x, b.y - a.y) >= 10;
      });
      selected = localTrafficRoads(drawable, vehicles, blocked); selectedAt = Date.now();
    }
    for (const road of selected) {
      const [a, b] = road.coordinates.map(([lon, lat]) => map.latLngToContainerPoint([lat, lon]));
      if (Math.max(a.x, b.x) < 0 || Math.min(a.x, b.x) > size.x || Math.max(a.y, b.y) < 0 || Math.min(a.y, b.y) > size.y) continue;
      const length = Math.hypot(b.x - a.x, b.y - a.y);
      if (length < 10) continue;
      const closed = blocked.has(road.id), slow = congestion[road.id] || 1;
      const count = Math.min(2, Math.max(1, Math.floor(length / 65)));
      const seed = [...String(road.id)].reduce((sum, char) => (sum * 31 + char.charCodeAt(0)) >>> 0, 0);
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      for (let n = 0; n < count && cars < TRAFFIC_LIMIT; n++) {
        const progress = trafficProgress(clock + seed % 97, n, count, closed, slow);
        const x = a.x + (b.x - a.x) * progress, y = a.y + (b.y - a.y) * progress;
        const point = road.coordinates[0].map((v, i) => v + (road.coordinates[1][i] - v) * progress);
        const distance = Math.min(...centres.map(p => Math.hypot(p.x - x, p.y - y)));
        if (x < 0 || x > size.x || y < 0 || y > size.y || distance > 220
          || !vehicles.some(v => segmentDistance([point, point], v) <= RADIUS_KM)) continue;
        ctx.save(); ctx.globalAlpha = Math.min(1, (220 - distance) / 60);
        ctx.translate(x, y); ctx.rotate(angle);
        ctx.fillStyle = closed || slow > 1 ? '#ce6950' : ['#64778a', '#89a5ae', '#bca48b', '#788790'][seed % 4];
        ctx.fillRect(-4, -2.1, 8, 4.2); ctx.fillStyle = '#eaf3f4'; ctx.fillRect(1, -1.6, 1.4, 3.2);
        ctx.restore(); cars++;
      }
      if (cars >= TRAFFIC_LIMIT) break;
    }
    canvas.dataset.cars = String(cars);
  }
  function tick(now) {
    frame = 0;
    if (document.hidden) { last = 0; return; }
    if (lastPaint && now - lastPaint < 32) {
      frame = requestAnimationFrame(tick);
      return;
    }
    lastPaint = now;
    if (!paused && !reduced.matches) clock += last ? Math.min(50, now - last) / 1000 : 0;
    last = now; paint();
    if (visibleVehicles().length && !paused && !reduced.matches) frame = requestAnimationFrame(tick);
    else last = 0;
  }
  function wake() { if (!frame && !document.hidden) frame = requestAnimationFrame(tick); }
  map.on('move zoom resize', () => { selectedAt = 0; wake(); clearTimeout(timer); timer = setTimeout(load, 250); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) { cancelAnimationFrame(frame); frame = 0; clearRoads(); } else { last = 0; load(); wake(); } });
  reduced.addEventListener('change', wake);
  return {
    update(scene, sessionId) {
      if (session !== sessionId) { clearRoads(); session = sessionId; }
      enabled = Boolean(scene?.enabled); blocked = new Set(Object.keys(scene?.closures || {})); congestion = scene?.congestion || {};
      fallback = [...trafficRouteRoads(getVehicles()), ...Object.values(scene?.closures || {})]; selectedAt = 0;
      load(); wake();
    },
    setPaused(value) { paused = value; last = 0; wake(); },
  };
}
