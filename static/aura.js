// Marco luminoso en el borde interior de la pantalla mientras el director IA procesa o comunica.
// Forma: la del marco «Apple Intelligence» (rectángulo redondeado pegado al borde, apple-intelligence-frame.html).
// Aspecto: el de BottomWave.jsx (LogiOptiAI, Interhack 26): dos trazos azul/violeta muy difuminados (blur CSS),
// translúcidos, con resplandor y deslizándose en sentidos opuestos. Ondulación mínima, casi recta.
const layers = [
  // Resplandor de fondo, muy abierto: el div difuso rgba(96,165,250,.2) blur 30 del original, ensanchado al seguir el borde.
  { color: "rgba(96, 165, 250, 0.2)", width: 90, blur: 45, alpha: .3, amplitude: 0, period: 360, speed: 0 },
  // Onda azul: mismo color; el trazo y el desenfoque se amplían para igualar la suavidad de la onda SVG (que sumaba
  // stroke 16 + amplitud + blur 16 sobre un elemento estirado).
  { color: "rgba(56, 189, 248, 0.4)", width: 26, blur: 30, alpha: 1, amplitude: 2.5, period: 360, speed: 240 },
  // Onda violeta: sentido inverso, 2 periodos cada 2,5 s.
  { color: "rgba(168, 85, 247, 0.5)", width: 20, blur: 24, alpha: 1, amplitude: 3, period: 360, speed: -288, phase: .5 },
];
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

// Métricas del marco Apple Intelligence: inset 7–11 px y radio 18–30 px según el lado corto.
export function frameMetrics(width, height) {
  const side = Math.min(width, height);
  return { inset: clamp(side * .01, 7, 11), radius: clamp(side * .03, 18, 30) };
}

export function perimeterLength(width, height, inset, radius) {
  const rw = Math.max(1, width - inset * 2 - radius * 2), rh = Math.max(1, height - inset * 2 - radius * 2);
  return rw * 2 + rh * 2 + Math.PI * radius * 2;
}

// Punto sobre el perímetro redondeado para t ∈ [0, 1), en sentido horario desde la esquina superior izquierda.
export function perimeterPoint(t, width, height, inset, radius) {
  const left = inset, top = inset, right = width - inset, bottom = height - inset;
  const rw = Math.max(1, right - left - radius * 2), rh = Math.max(1, bottom - top - radius * 2), corner = Math.PI * radius / 2;
  let d = (((t % 1) + 1) % 1) * (rw * 2 + rh * 2 + corner * 4);
  const arc = (cx, cy, from) => u => ({ x: cx + Math.cos(from + u * Math.PI / 2) * radius, y: cy + Math.sin(from + u * Math.PI / 2) * radius });
  const parts = [
    [rw, u => ({ x: left + radius + rw * u, y: top })], [corner, arc(right - radius, top + radius, -Math.PI / 2)],
    [rh, u => ({ x: right, y: top + radius + rh * u })], [corner, arc(right - radius, bottom - radius, 0)],
    [rw, u => ({ x: right - radius - rw * u, y: bottom })], [corner, arc(left + radius, bottom - radius, Math.PI / 2)],
    [rh, u => ({ x: left, y: bottom - radius - rh * u })], [corner, arc(left + radius, top + radius, Math.PI)],
  ];
  for (const [length, at] of parts) { if (d <= length) return at(d / length); d -= length; }
  return { x: left + radius, y: top };
}

// Perímetro con una ondulación suave desplazada a lo largo del borde (amplitud en px, periodo en px, fase en px).
export function wavyFrame(width, height, inset, radius, amplitude, period, shift, step = 6) {
  const total = perimeterLength(width, height, inset, radius), count = Math.max(8, Math.ceil(total / step)), points = [];
  for (let i = 0; i < count; i++) {
    const t = i / count, p = perimeterPoint(t, width, height, inset, radius), q = perimeterPoint(t + 1e-4, width, height, inset, radius);
    const dx = q.x - p.x, dy = q.y - p.y, norm = Math.hypot(dx, dy) || 1;
    const offset = amplitude ? amplitude * Math.sin((t * total + shift) / period * Math.PI * 2) : 0;
    points.push({ x: p.x + (-dy / norm) * offset, y: p.y + (dx / norm) * offset });
  }
  return points;
}

// El contenedor lleva un canvas por capa. El desenfoque se aplica con CSS `filter: blur()` sobre cada canvas, no con
// `ctx.filter`: Safari no implementa el filtro del canvas 2D y dibujaba los trazos totalmente nítidos.
export function createAura(container, { reduced = matchMedia("(prefers-reduced-motion: reduce)"), requestFrame = requestAnimationFrame, cancelFrame = cancelAnimationFrame } = {}) {
  const canvases = Array.from(container.querySelectorAll("canvas")).slice(0, layers.length);
  const contexts = canvases.map(canvas => canvas.getContext("2d", { alpha: true, colorSpace: "display-p3" }) || canvas.getContext("2d", { alpha: true }));
  canvases.forEach((canvas, i) => { canvas.style.filter = `blur(${layers[i].blur}px)`; canvas.style.opacity = String(layers[i].alpha); });
  let active = false, paused = false, width = 0, height = 0, raf = 0, started = 0;

  function resize() {
    width = window.innerWidth; height = window.innerHeight;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvases.forEach((canvas, i) => {
      canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
      contexts[i].setTransform(dpr, 0, 0, dpr, 0, 0);
    });
  }
  function still() { return reduced.matches || paused; }

  function render(now) {
    raf = 0;
    if (!active) return;
    if (!width || !height) resize();
    const seconds = still() ? 0 : (now - started) / 1000;
    const { inset, radius } = frameMetrics(width, height);
    layers.forEach((layer, i) => {
      const ctx = contexts[i];
      if (!ctx) return;
      const points = wavyFrame(width, height, inset, radius, layer.amplitude, layer.period, seconds * layer.speed + (layer.phase || 0) * layer.period);
      ctx.clearRect(0, 0, width, height);
      ctx.lineJoin = "round"; ctx.lineCap = "round";
      ctx.beginPath();
      points.forEach((p, j) => j ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
      ctx.closePath();
      ctx.lineWidth = layer.width; ctx.strokeStyle = layer.color;
      ctx.stroke();
    });
    if (!still()) raf = requestFrame(render);
  }
  function schedule() { if (!raf && active) raf = requestFrame(render); }

  function set(next) {
    next = Boolean(next);
    if (next === active) return;
    active = next;
    container.classList.toggle("ai-active", active);
    if (active) { resize(); started = performance.now(); schedule(); }
    else if (raf) { cancelFrame(raf); raf = 0; }
    // Al desactivar se conserva el último fotograma para que el fundido de salida no corte la luz.
  }
  window.addEventListener("resize", () => { if (!active) return; resize(); schedule(); });
  reduced.addEventListener("change", schedule);
  return { set, setPaused(value) { paused = Boolean(value); schedule(); }, get active() { return active; } };
}
