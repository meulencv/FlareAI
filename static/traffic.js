export function trafficProgress(clock, index, count, blocked, congestion = 1) {
  const phase = ((clock / (18 * Math.max(1, congestion)) + index / count) % 1 + 1) % 1;
  return blocked ? Math.min(phase, Math.max(.04, .43 - index * .055)) : phase;
}

export function trafficOpacity(zoom) {
  return Math.max(0, Math.min(1, (zoom - 11.7) / 1.2));
}

export function createTraffic({ map, L, document, fetch }) {
  const canvas = document.createElement('canvas');
  canvas.className = 'traffic-canvas'; canvas.setAttribute('aria-hidden', 'true');
  map.getPane('mapPane').append(canvas);
  const ctx = canvas.getContext('2d'), reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let roads = [], blocked = new Set(), congestion = {}, enabled = false, paused = false;
  let frame = 0, last = 0, clock = 0, timer = 0, generation = 0, controller = null, signature = '', pendingKey = '';

  async function load() {
    if (!enabled || !Number.isFinite(map.getZoom()) || map.getZoom() < 11.7 || document.hidden) return;
    const b = map.getBounds();
    const box = [Math.max(2.00001, b.getWest()), Math.max(41.28001, b.getSouth()), Math.min(2.31999, b.getEast()), Math.min(41.53999, b.getNorth())];
    if (box[0] >= box[2] || box[1] >= box[3]) { roads = []; return; }
    const key = box.map(v => v.toFixed(4)).join(',');
    if (key === signature || key === pendingKey) return;
    pendingKey = key;
    controller?.abort(); controller = new globalThis.AbortController();
    const token = ++generation;
    try {
      const response = await fetch(`/api/scenario/roads?bbox=${key}`, { signal: controller.signal });
      if (!response.ok) throw new Error('Red de tráfico no disponible');
      const result = await response.json();
      if (token !== generation) return;
      roads = result.roads; signature = key;
      canvas.dataset.roads = String(roads.length);
      canvas.dataset.status = 'ready';
      paint();
    } catch (error) {
      if (error.name !== 'AbortError') canvas.dataset.status = 'unavailable';
    } finally { if (token === generation) pendingKey = ''; }
  }
  function paint() {
    if (!Number.isFinite(map.getZoom())) return;
    const size = map.getSize(), ratio = Math.min(2, window.devicePixelRatio || 1);
    const origin = map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(canvas, origin);
    if (canvas.width !== Math.round(size.x * ratio) || canvas.height !== Math.round(size.y * ratio)) {
      canvas.width = Math.round(size.x * ratio); canvas.height = Math.round(size.y * ratio);
      canvas.style.width = size.x + 'px'; canvas.style.height = size.y + 'px';
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, size.x, size.y);
    const alpha = enabled ? trafficOpacity(map.getZoom()) : 0;
    canvas.style.opacity = String(alpha);
    if (!alpha) { canvas.dataset.cars = '0'; return; }
    let cars = 0;
    for (const road of roads) {
      const [a, b] = road.coordinates.map(([lon, lat]) => map.latLngToContainerPoint([lat, lon]));
      if (Math.max(a.x, b.x) < 0 || Math.min(a.x, b.x) > size.x || Math.max(a.y, b.y) < 0 || Math.min(a.y, b.y) > size.y) continue;
      const length = Math.hypot(b.x - a.x, b.y - a.y);
      if (length < 14) continue;
      const closed = blocked.has(road.id), slow = congestion[road.id] || 1;
      const count = Math.min(closed ? 7 : 4, Math.max(1, Math.floor(length / 26)));
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      for (let n = 0; n < count && cars < 1000; n++) {
        const progress = trafficProgress(clock + cars % 13, n, count, closed, slow);
        ctx.save(); ctx.translate(a.x + (b.x - a.x) * progress, a.y + (b.y - a.y) * progress); ctx.rotate(angle);
        ctx.fillStyle = closed || slow > 1 ? '#ce6950' : ['#64778a', '#89a5ae', '#bca48b', '#788790'][cars % 4];
        ctx.fillRect(-4, -2.1, 8, 4.2); ctx.fillStyle = '#eaf3f4'; ctx.fillRect(1, -1.6, 1.4, 3.2);
        ctx.restore(); cars++;
      }
      if (cars >= 1000) break;
    }
    canvas.dataset.cars = String(cars);
  }
  function tick(now) {
    frame = 0;
    if (document.hidden) { last = 0; return; }
    if (!paused && !reduced.matches) clock += last ? Math.min(50, now - last) / 1000 : 0;
    last = now; paint();
    if (enabled && map.getZoom() >= 11.7 && !paused && !reduced.matches) frame = requestAnimationFrame(tick);
  }
  function wake() { paint(); if (!frame && !document.hidden) frame = requestAnimationFrame(tick); }
  map.on('move zoom resize', () => { wake(); clearTimeout(timer); timer = setTimeout(load, 250); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) { cancelAnimationFrame(frame); frame = 0; } else { last = 0; load(); wake(); } });
  reduced.addEventListener('change', wake);
  return {
    update(scene) {
      enabled = Boolean(scene?.enabled); blocked = new Set(Object.keys(scene?.closures || {})); congestion = scene?.congestion || {};
      load(); wake();
    },
    setPaused(value) { paused = value; last = 0; wake(); },
  };
}
