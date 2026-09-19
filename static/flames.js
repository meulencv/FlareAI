import {
  budget, detailedOutline, emberBudget, expired, flameOutline, flicker, heatRadius,
  indexRings, inside, pointInPolygon, polygonArea, rings, spawn, stepParticle, windStroke,
} from "./flow.js";

const WIND_LIFE = 5.5, EMBER_LIFE = 3.4, MAX_EMBERS = 420;

export function confirmedFire(incident, now = Date.now()) {
  const c = incident.confirmation;
  const source = /^https?:\/\//.test(c?.source_url || "") || (c?.demo === true && /^\/api\/demo\/report\/[a-f0-9-]{36}$/.test(c.source_url || ""));
  return c?.status === "confirmed" && Boolean(c.source_name) && source
    && new Date(c.confirmed_at).getTime() <= now && now <= new Date(c.valid_until).getTime();
}

export function fireTint(incident, r, g, b, alpha = 1) {
  if (incident.scenario && !incident.scenario.linked_call_id && incident.scenario.phase !== 'closed') {
    if (incident.scenario.phase !== 'active') return `rgba(82,148,123,${alpha * .45})`;
    return `rgba(${r},${g},${b},${alpha})`;
  }
  if (confirmedFire(incident)) return `rgba(${r},${g},${b},${alpha})`;
  const gray = Math.round(r * .2126 + g * .7152 + b * .0722);
  return `rgba(${gray},${gray},${gray},${alpha})`;
}

export function fireDisplayScale(extent) {
  return Math.max(1, 16 / Math.max(.0001, extent));
}

function smooth(ctx, points) {
  ctx.beginPath();
  ctx.moveTo((points[0].x + points[points.length - 1].x) / 2, (points[0].y + points[points.length - 1].y) / 2);
  for (let i = 0; i < points.length; i++) {
    const point = points[i], next = points[(i + 1) % points.length];
    ctx.quadraticCurveTo(point.x, point.y, (point.x + next.x) / 2, (point.y + next.y) / 2);
  }
  ctx.closePath();
}

function towards(points, centre, factor) {
  return points.map(p => ({ x: centre.x + (p.x - centre.x) * factor, y: centre.y + (p.y - centre.y) * factor }));
}

export function createStage({ map, canvas, sampleWind, random = Math.random }) {
  const ctx = canvas.getContext("2d");
  const embers = new Map();
  const footprints = new Map();
  let particles = [], incidents = [], selectedId = null, country = null;
  let windVisible = true, frame = 0, previous = 0, clock = 0, running = false;
  let paused = false, origin, offset;
  const motionless = matchMedia("(prefers-reduced-motion: reduce)");
  const animated = () => !motionless.matches && !paused;

  const geography = () => {
    const b = map.getBounds();
    return { west: b.getWest(), east: b.getEast(), south: b.getSouth(), north: b.getNorth() };
  };
  const metersPerPixel = () =>
    40075016.686 * Math.cos(map.getCenter().lat * Math.PI / 180) / Math.pow(2, map.getZoom() + 8);
  const point = (lat, lon) => {
    const projected = map.project([lat, lon], map.getZoom());
    return { x: projected.x - origin.x - offset.x, y: projected.y - origin.y - offset.y };
  };

  function resize() {
    const size = map.getSize(), ratio = Math.min(2, window.devicePixelRatio || 1);
    if (canvas.width !== Math.round(size.x * ratio) || canvas.height !== Math.round(size.y * ratio)) {
      canvas.width = Math.round(size.x * ratio); canvas.height = Math.round(size.y * ratio);
      canvas.style.width = `${size.x}px`; canvas.style.height = `${size.y}px`;
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, size.x, size.y);
    return size;
  }

  function windField(size, seconds) {
    if (!windVisible || !country) { particles = []; return; }
    const bounds = geography(), mpp = metersPerPixel();
    const target = budget(size.x, size.y, 6200, 240);
    const land = (lon, lat) => country(lon, lat) && sampleWind(lat, lon)?.from != null;
    particles = particles.filter(p => !expired(p, bounds, 0));
    for (let attempt = 0; particles.length < target && attempt < target; attempt++) {
      const fresh = spawn(bounds, random, WIND_LIFE, land);
      if (!fresh) break;
      particles.push(fresh);
    }
    if (particles.length > target) particles.length = target;
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    for (let i = 0; i < particles.length; i++) {
      const wind = sampleWind(particles[i].lat, particles[i].lon);
      const moved = stepParticle(particles[i], wind, seconds, mpp, { base: 9, gain: .8 });
      const head = point(moved.lat, moved.lon);
      particles[i] = moved;
      const trail = windStroke(moved, wind, mpp, 13 + Math.min(moved.speed, 40) * .4)
        .map(p => point(p.lat, p.lon));
      if (trail.length < 2) continue;
      const fade = Math.min(1, moved.age / .6) * Math.max(0, 1 - moved.age / moved.life);
      const strength = Math.min(1, moved.speed / 38);
      ctx.globalAlpha = fade * .56;
      ctx.strokeStyle = strength > .55 ? "#6d8397" : "#93a6b6";
      ctx.lineWidth = .8 + strength * .7;
      ctx.beginPath();
      ctx.moveTo(trail[0].x, trail[0].y);
      for (const step of trail.slice(1)) ctx.lineTo(step.x, step.y);
      ctx.stroke();
      const previousPoint = trail[trail.length - 2];
      const angle = Math.atan2(head.y - previousPoint.y, head.x - previousPoint.x);
      const wing = 3.1 + strength * 1.8;
      ctx.globalAlpha = fade * .8;
      ctx.beginPath();
      ctx.moveTo(head.x, head.y);
      ctx.lineTo(head.x - Math.cos(angle - .42) * wing, head.y - Math.sin(angle - .42) * wing);
      ctx.moveTo(head.x, head.y);
      ctx.lineTo(head.x - Math.cos(angle + .42) * wing, head.y - Math.sin(angle + .42) * wing);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  function heat(incident, shape, holes, centre, area, time) {
    const selected = incident.id === selectedId;
    const tint = (r, g, b, a) => fireTint(incident, r, g, b, a);
    const pulse = (flicker(incident.lat * 9, time) + 1) / 2;
    const radius = heatRadius(area, incident.observations) * (1 + pulse * .07);
    const aura = ctx.createRadialGradient(centre.x, centre.y, radius * .12, centre.x, centre.y, radius * 2.15);
    aura.addColorStop(0, tint(250, 120, 44, (selected ? .3 : .22) + pulse * .05));
    aura.addColorStop(.45, tint(240, 86, 50, .12));
    aura.addColorStop(1, tint(236, 80, 60, 0));
    ctx.fillStyle = aura;
    ctx.beginPath(); ctx.arc(centre.x, centre.y, radius * 2.15, 0, 2 * Math.PI); ctx.fill();

    const bearing = incident.weather.wind_from_degrees === null ? null : (incident.weather.wind_from_degrees + 180) % 360;
    const extent = Math.max(...shape.map(p => Math.hypot(p.x - centre.x, p.y - centre.y)), .01);
    const amplitude = Math.max(.15, Math.min(26, extent * .24));
    const tongues = flameOutline(shape, time, bearing, amplitude);
    const body = ctx.createLinearGradient(centre.x - radius, centre.y + radius, centre.x + radius, centre.y - radius);
    body.addColorStop(0, tint(198, 45, 32, .62));
    body.addColorStop(.55, tint(238, 84, 45, .66 + pulse * .12));
    body.addColorStop(1, tint(252, 163, 66, .72));
    smooth(ctx, tongues);
    for (const hole of holes) {
      ctx.moveTo(hole[0].x, hole[0].y);
      for (const p of hole.slice(1)) ctx.lineTo(p.x, p.y);
      ctx.closePath();
    }
    ctx.fillStyle = body;
    ctx.fill("evenodd");
    ctx.save();
    ctx.clip("evenodd");

    ctx.globalCompositeOperation = "lighter";
    const core = ctx.createRadialGradient(centre.x, centre.y, 0, centre.x, centre.y, Math.max(6, radius * .85));
    core.addColorStop(0, tint(255, 236, 178, .5 + pulse * .22));
    core.addColorStop(.42, tint(255, 150, 60, .34));
    core.addColorStop(1, tint(255, 110, 50, 0));
    ctx.fillStyle = core;
    smooth(ctx, towards(tongues, centre, .82)); ctx.fill();
    for (let i = 0; i < 7; i++) {
      const edge = shape[Math.floor(i * shape.length / 7)];
      const blend = .24 + (flicker(i * 2.1, time, .5) + 1) * .15;
      const x = centre.x + (edge.x - centre.x) * blend;
      const y = centre.y + (edge.y - centre.y) * blend;
      const spread = radius * (.2 + (flicker(i + incident.lat, time) + 1) * .1);
      const pocket = ctx.createRadialGradient(x, y, 0, x, y, spread);
      pocket.addColorStop(0, tint(255, 235, 146, .45));
      pocket.addColorStop(.4, tint(255, 166, 54, .24));
      pocket.addColorStop(1, tint(255, 128, 37, 0));
      ctx.fillStyle = pocket;
      ctx.beginPath(); ctx.arc(x, y, spread, 0, Math.PI * 2); ctx.fill();
    }
    const stride = Math.max(1, Math.ceil(tongues.length / 22));
    for (let i = 0; i < tongues.length; i += stride) {
      const edge = tongues[i], next = tongues[(i + 1) % tongues.length];
      const glow = .55 + flicker(i / tongues.length * 9 + incident.lon, time, 1.3) * .3;
      const tongue = {
        x: edge.x * .72 + centre.x * .28,
        y: edge.y * .72 + centre.y * .28,
      };
      ctx.fillStyle = tint(255, 185, 61, glow * .38);
      ctx.beginPath();
      ctx.moveTo(edge.x, edge.y);
      ctx.quadraticCurveTo(next.x, next.y, tongue.x, tongue.y);
      ctx.quadraticCurveTo(centre.x * .15 + edge.x * .85, centre.y * .15 + edge.y * .85, edge.x, edge.y);
      ctx.fill();
    }
    ctx.restore();
    ctx.globalCompositeOperation = "source-over";

    if (bearing !== null && radius > 12) {
      const angle = bearing * Math.PI / 180;
      const direction = { x: Math.sin(angle), y: -Math.cos(angle) };
      for (let i = 0; i < shape.length; i += Math.max(1, Math.ceil(shape.length / 24))) {
        const root = shape[i], next = shape[(i + 2) % shape.length];
        const dx = root.x - centre.x, dy = root.y - centre.y;
        const exposure = (dx * direction.x + dy * direction.y) / (Math.hypot(dx, dy) || 1);
        if (exposure < .1) continue;
        const fraction = i / shape.length;
        const pulse = (flicker(fraction * 13, time, 1.2) + 1) / 2;
        const length = amplitude * (1.2 + pulse * 2) * exposure;
        const sway = flicker(fraction * 8, time, 1.5) * amplitude * .4;
        const tip = {
          x: root.x + direction.x * length - direction.y * sway,
          y: root.y + direction.y * length + direction.x * sway,
        };
        const fire = ctx.createLinearGradient(root.x, root.y, tip.x, tip.y);
        fire.addColorStop(0, tint(250, 125, 34, .65));
        fire.addColorStop(.7, tint(255, 181, 62, .42));
        fire.addColorStop(1, tint(255, 196, 96, 0));
        ctx.fillStyle = fire;
        ctx.beginPath(); ctx.moveTo(root.x, root.y);
        ctx.quadraticCurveTo(root.x + direction.x * length * .5, root.y + direction.y * length * .5, tip.x, tip.y);
        ctx.quadraticCurveTo(next.x + direction.x * length * .25, next.y + direction.y * length * .25, next.x, next.y);
        ctx.closePath(); ctx.fill();
      }
    }
    ctx.strokeStyle = selected ? tint(190, 52, 36, .45) : tint(205, 70, 48, .3);
    ctx.lineWidth = .8;
    smooth(ctx, tongues); ctx.stroke();
  }

  function sparks(incident, area, seconds, time, available, project, displayScale) {
    const selected = incident.id === selectedId;
    const target = Math.min(available, emberBudget(incident.observations, selected, map.getZoom()));
    const bounds = geography(), mpp = metersPerPixel() / displayScale;
    const { shapes, cradle } = footprints.get(incident.id);
    const live = (embers.get(incident.id) || []).filter(e => !expired(e, bounds));
    while (live.length < target) {
      const fresh = spawn(cradle, random, EMBER_LIFE, (lon, lat) => pointInPolygon(shapes, lon, lat));
      if (!fresh) break;
      live.push(fresh);
    }
    live.length = Math.min(live.length, target);
    const scale = Math.max(.75, Math.min(2.2, heatRadius(area, incident.observations) / 18));
    for (let i = 0; i < live.length; i++) {
      const wind = sampleWind(live[i].lat, live[i].lon);
      live[i] = stepParticle(live[i], wind, seconds, mpp, { base: 5.5, gain: .5, drift: 3.4 });
      const spot = project(live[i].lat, live[i].lon);
      if (!inside(live[i], bounds)) continue;
      const life = live[i].age / live[i].life;
      const lift = (flicker(live[i].seed, time, 1.4) + 1) / 2;
      const size = Math.max(.45, (1.6 - life) * scale * (.55 + lift * .5));
      ctx.globalAlpha = Math.max(0, Math.sin(Math.PI * Math.min(1, life)) * .95);
      ctx.fillStyle = life < .45 ? fireTint(incident, 255, 217, 161) : fireTint(incident, 242, 118, 74);
      ctx.shadowColor = fireTint(incident, 255, 148, 54); ctx.shadowBlur = 4;
      ctx.beginPath(); ctx.arc(spot.x, spot.y, size, 0, 2 * Math.PI); ctx.fill();
      if (wind?.from != null) {
        const tail = windStroke(live[i], wind, mpp, (1 - life) * 5 * scale)[0];
        if (tail) {
          const end = project(tail.lat, tail.lon);
          ctx.strokeStyle = fireTint(incident, 239, 133, 67); ctx.lineWidth = Math.max(.5, size * .65);
          ctx.beginPath(); ctx.moveTo(end.x, end.y); ctx.lineTo(spot.x, spot.y); ctx.stroke();
        }
      }
    }
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
    embers.set(incident.id, live);
    return live.length;
  }

  function fires(seconds, time) {
    const bounds = geography();
    const margin = metersPerPixel() * 250 / 75000;
    let available = MAX_EMBERS;
    for (const incident of incidents) {
      const { polygons, cradle } = footprints.get(incident.id);
      if (cradle.east < bounds.west - margin || cradle.west > bounds.east + margin
        || cradle.north < bounds.south - margin || cradle.south > bounds.north + margin) {
        embers.delete(incident.id);
        continue;
      }
      const anchor = point(incident.lat, incident.lon);
      const projectedPolygons = polygons.map(polygon => polygon.map(ring => ring.slice(0, -1).map(([lon, lat]) => point(lat, lon))));
      const extent = projectedPolygons.flat(2).reduce((max, p) => Math.max(max, Math.hypot(p.x - anchor.x, p.y - anchor.y)), 0);
      const displayScale = fireDisplayScale(extent);
      const enlarge = p => ({ x: anchor.x + (p.x - anchor.x) * displayScale, y: anchor.y + (p.y - anchor.y) * displayScale });
      let area = 0;
      for (const polygon of projectedPolygons) {
        const projected = polygon.map(ring => ring.map(enlarge));
        const ring = projected[0];
        if (ring.length < 3) continue;
        const centre = {
          x: ring.reduce((sum, p) => sum + p.x, 0) / ring.length,
          y: ring.reduce((sum, p) => sum + p.y, 0) / ring.length,
        };
        const outline = detailedOutline(ring);
        const ringArea = polygonArea(outline);
        area += ringArea;
        heat(incident, outline, projected.slice(1), centre, ringArea, time);
      }
      available -= sparks(incident, area, seconds, time, available, (lat, lon) => enlarge(point(lat, lon)), displayScale);
    }
  }

  function draw(timestamp) {
    frame = 0;
    const seconds = previous ? Math.min(.05, (timestamp - previous) / 1000) : .016;
    previous = timestamp;
    if (animated()) clock += seconds;
    origin = map.getPixelOrigin();
    offset = map.containerPointToLayerPoint([0, 0]);
    canvas.style.transform = `translate(${offset.x}px, ${offset.y}px)`;
    const size = resize();
    windField(size, animated() ? seconds : 0);
    fires(animated() ? seconds : 0, clock);
    if (running && !document.hidden && animated()) frame = requestAnimationFrame(draw);
  }

  function loop() {
    if (!running || frame || document.hidden) return;
    previous = 0;
    frame = requestAnimationFrame(draw);
  }

  document.addEventListener("visibilitychange", () => (document.hidden ? stop(true) : loop()));
  motionless.addEventListener("change", loop);
  map.on("move zoom resize viewreset", loop);

  function stop(keepRunning = false) {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
    running = keepRunning && running;
  }

  return {
    start(boundary) { country = indexRings(boundary); running = true; loop(); },
    stop,
    update(list, selection) {
      incidents = [...list].sort((a, b) => Number(b.id === selection) - Number(a.id === selection));
      selectedId = selection;
      const alive = new Set(list.map(i => i.id));
      for (const id of embers.keys()) if (!alive.has(id)) embers.delete(id);
      footprints.clear();
      for (const incident of list) {
        const geometry = !incident.scenario?.linked_call_id && incident.scenario?.phase !== 'closed' && incident.scenario?.footprint || incident.footprint;
        const shapes = rings(geometry);
        const coordinates = shapes.flat();
        const cradle = coordinates.reduce((b, [lon, lat]) => ({
          west: Math.min(b.west, lon), east: Math.max(b.east, lon),
          south: Math.min(b.south, lat), north: Math.max(b.north, lat),
        }), { west: Infinity, east: -Infinity, south: Infinity, north: -Infinity });
        footprints.set(incident.id, {
          shapes, cradle,
          polygons: geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates,
        });
      }
      loop();
    },
    setWind(visible) { windVisible = visible; loop(); },
    setPaused(value) { paused = value; loop(); },
    get windVisible() { return windVisible; },
  };
}
