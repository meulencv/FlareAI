const TAU = Math.PI * 2;
const STOPS = [
  [0, [255, 246, 228, 0]],
  [.2, [251, 227, 176, 95]],
  [.45, [246, 189, 127, 155]],
  [.72, [231, 133, 95, 198]],
  [1, [187, 72, 65, 230]],
];

export function heatPalette(stops = STOPS) {
  const lut = new Uint8ClampedArray(256 * 4);
  for (let i = 0; i < 256; i++) {
    const position = i / 255;
    let low = stops[0], high = stops[stops.length - 1];
    for (let s = 0; s < stops.length - 1; s++) {
      if (position >= stops[s][0] && position <= stops[s + 1][0]) { low = stops[s]; high = stops[s + 1]; break; }
    }
    const span = high[0] - low[0];
    const ratio = span ? (position - low[0]) / span : 0;
    for (let channel = 0; channel < 4; channel++) {
      lut[i * 4 + channel] = low[1][channel] + (high[1][channel] - low[1][channel]) * ratio;
    }
  }
  return lut;
}

export function colorize(pixels, palette, maxAlpha = .8, floor = 4) {
  for (let i = 0; i < pixels.length; i += 4) {
    const density = pixels[i + 3];
    if (density < floor) { pixels[i + 3] = 0; continue; }
    const offset = density * 4;
    pixels[i] = palette[offset];
    pixels[i + 1] = palette[offset + 1];
    pixels[i + 2] = palette[offset + 2];
    pixels[i + 3] = palette[offset + 3] * maxAlpha;
  }
  return pixels;
}

export function heatRadiusPixels(metersPerPixel, meters = 1600, minimum = 18, maximum = 190) {
  if (!(metersPerPixel > 0)) return minimum;
  return Math.max(minimum, Math.min(maximum, meters / metersPerPixel));
}

export function sampleAlpha(score, cap = .55) {
  if (!Number.isFinite(score)) return 0;
  return cap * Math.min(1, Math.max(0, score) / 100) ** .75;
}

export function nearestSample(samples, project, x, y, maxPixels) {
  let best = null, bestDistance = maxPixels;
  for (const sample of samples) {
    const point = project(sample.lat, sample.lon);
    const distance = Math.hypot(point.x - x, point.y - y);
    if (distance <= bestDistance) { best = sample; bestDistance = distance; }
  }
  return best;
}

export function hoverSummary(sample, facilities = [], wind = {}) {
  if (!sample) return null;
  const known = new Map(facilities.map(item => [item.id, item]));
  const evidence = sample.evidence || {};
  const parts = [];
  const nearby = (evidence.facility_ids || []).map(id => known.get(id)).filter(Boolean);
  for (const item of nearby.slice(0, 2)) {
    parts.push(item.name ? `${item.name}` : item.category_label || "Instalación registrada");
  }
  if (nearby.length > 2) parts.push(`+${nearby.length - 2} instalaciones`);
  if (Number.isFinite(evidence.population) && evidence.population > 0) {
    parts.push(`${Math.round(evidence.population).toLocaleString("es-ES")} residentes`);
  }
  if (Number.isFinite(evidence.vegetation_pct)) parts.push(`${Math.round(evidence.vegetation_pct)} % vegetación`);
  if (!parts.length) parts.push("Sin elementos registrados");
  if (sample.downwind && wind.status === "current") parts.push("a favor del viento");
  const distance = Number.isFinite(sample.distance_km)
    ? (sample.distance_km < .1 ? "en la huella" : `a ${sample.distance_km.toFixed(1).replace(".", ",")} km`) : null;
  if (distance) parts.push(distance);
  return parts.join(" · ");
}

export function createHeatLayer({ map, canvas, document, onHover = () => {}, resolution = .6 }) {
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const palette = heatPalette();
  let samples = [], facilities = [], wind = {}, frame = 0, origin, offset;

  const metersPerPixel = () =>
    40075016.686 * Math.cos(map.getCenter().lat * Math.PI / 180) / Math.pow(2, map.getZoom() + 8);
  const project = (lat, lon) => {
    const projected = map.project([lat, lon], map.getZoom());
    return { x: projected.x - origin.x - offset.x, y: projected.y - origin.y - offset.y };
  };

  function paint() {
    frame = 0;
    origin = map.getPixelOrigin();
    offset = map.containerPointToLayerPoint([0, 0]);
    canvas.style.transform = `translate(${offset.x}px, ${offset.y}px)`;
    const size = map.getSize();
    const width = Math.max(1, Math.round(size.x * resolution));
    const height = Math.max(1, Math.round(size.y * resolution));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width; canvas.height = height;
      canvas.style.width = `${size.x}px`; canvas.style.height = `${size.y}px`;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const scored = samples.filter(sample => Number.isFinite(sample.score) && sample.score > 0);
    if (!scored.length) return;
    const radius = heatRadiusPixels(metersPerPixel()) * resolution;
    let painted = 0;
    for (const sample of scored) {
      const point = project(sample.lat, sample.lon);
      const x = point.x * resolution, y = point.y * resolution;
      if (x < -radius || y < -radius || x > width + radius || y > height + radius) continue;
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      const alpha = sampleAlpha(sample.score);
      gradient.addColorStop(0, `rgba(0,0,0,${alpha})`);
      gradient.addColorStop(.55, `rgba(0,0,0,${alpha * .45})`);
      gradient.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = gradient;
      ctx.beginPath(); ctx.arc(x, y, radius, 0, TAU); ctx.fill();
      painted++;
    }
    if (!painted) return;
    const image = ctx.getImageData(0, 0, width, height);
    colorize(image.data, palette);
    ctx.putImageData(image, 0, 0);
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(paint);
  }

  function hover(event) {
    if (!samples.length || !origin) return onHover(null);
    const point = event.containerPoint;
    const reach = heatRadiusPixels(metersPerPixel()) * .55;
    const sample = nearestSample(samples, project, point.x, point.y, Math.max(26, reach));
    onHover(sample ? { text: hoverSummary(sample, facilities, wind), point, id: sample.id } : null);
  }

  map.on("move zoom resize viewreset", schedule);
  map.on("mousemove", hover);
  map.on("mouseout dragstart zoomstart", () => onHover(null));
  if (document) document.addEventListener("visibilitychange", () => { if (!document.hidden) schedule(); });

  return {
    set(next, context) {
      samples = next || [];
      facilities = context?.potential?.facilities || [];
      wind = context?.wind || {};
      schedule();
    },
    clear() { samples = []; facilities = []; onHover(null); schedule(); },
    redraw: schedule,
  };
}
