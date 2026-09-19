const LABELS = { supported: 'Coherente', uncertain: 'Por contrastar', unlikely: 'Poco verosímil', prank: 'Indicios de broma' };
const PHONE = { waiting_arrival: 'Llamada al llegar bomberos', disabled: 'Telefonía pendiente de activar', starting: 'Preparando llamada', dialing: 'Llamada a bomberos en curso', retry_backup: 'Intentando contacto de respaldo', unreachable: 'Sin respuesta de los contactos', uncertain: 'Estado telefónico sin confirmar', completed: 'Parte recibido', needs_report: 'Parte pendiente de revisión' };

export function testimonyRows(records) {
  return records.flatMap(record => {
    const assessment = new Map((record.assessment?.testimonies || []).map(item => [item.id, item]));
    return [...(record.citizen ? [record.citizen] : []), ...(record.testimonies || [])].map(item => ({ ...item, assessment: assessment.get(item.id) }));
  }).sort((a, b) => b.at - a.at || a.id.localeCompare(b.id));
}

export function hashSeed(text) {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i++) { hash ^= text.charCodeAt(i); hash = Math.imul(hash, 16777619) >>> 0; }
  return hash;
}

// Personitas alrededor del aviso: posición ilustrativa estable por id (no es la ubicación real
// del llamante). La llamada 112 queda junto al foco; los testimonios se reparten en un anillo.
export function witnessPosition(item, incident, radiusKm = .18) {
  const seed = hashSeed(item.id);
  // Ángulo áureo por número de testigo para repartirlos alrededor, con un poco de jitter del id.
  const index = Number((item.speaker || '').match(/(\d+)/)?.[1]) || seed % 24;
  const angle = (index * 137.508 + (seed % 41) - 20) * Math.PI / 180;
  // Fuera del contorno máximo del fuego ilustrativo (hasta 1,9 × radio medio).
  const edge = radiusKm * 1900;
  const meters = item.source === 'webcall' ? edge + 50 : edge + 120 + ((seed >>> 9) % 560);
  const east = 111320 * Math.cos(incident.lat * Math.PI / 180);
  return [incident.lat + Math.cos(angle) * meters / 111320, incident.lon + Math.sin(angle) * meters / east];
}

export function mergeBrainNotes(notes = []) {
  const entries = [
    ['base-evidence', 'Contrastar antes de decidir', 'Cruzar la ubicación y los testimonios con los partes de equipos y las fuentes disponibles. Una anomalía térmica es una señal de contraste, no una confirmación oficial de incendio.', ['base-weather', 'base-resources']],
    ['base-weather', 'Viento y territorio', 'Revisar dirección, intensidad y fecha del viento junto a población, vegetación e instalaciones próximas. Separar observaciones actuales de datos históricos y del escenario calculado.', ['base-evidence', 'base-resources']],
    ['base-resources', 'Recursos y accesos', 'Comprobar disponibilidad y recorrido antes de asignar una unidad. Repartir la cobertura entre sedes y conservar alternativas cuando un acceso esté cortado. La proximidad no garantiza el acceso.', ['base-learning']],
    ['base-learning', 'Cerrar el ciclo y aprender', 'Conservar decisiones, partes y resultados con su procedencia. La llegada de un vehículo no confirma la extinción. Al cerrar, vincular el informe y las lecciones observadas para la siguiente revisión.', ['base-evidence']],
  ];
  const merged = new Map(entries.map(([id, title, text, links]) => [id, { id, title, text, links, kind: 'base', source: 'curated_base', reports: [] }]));
  for (const note of notes) merged.set(note.id, { ...note, links: note.links || (note.kind === 'base' ? [] : ['base-learning']) });
  return [...merged.values()];
}

const PERSON = '<svg viewBox="0 0 20 24" aria-hidden="true"><circle cx="10" cy="5.5" r="4"/><path d="M3 23c0-6 3-9 7-9s7 3 7 9z"/></svg>';

export function createOperationView({ document, fetch, map = null, L = null, findIncident = () => null }) {
  const node = (tag, text = '', className = '') => {
    const element = document.createElement(tag); element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const button = node('button', 'Cerebro', 'brain-toggle'); button.id = 'brain-toggle';
  button.setAttribute('aria-label', 'Abrir cerebro y memorias de FlareAI');
  button.setAttribute('aria-expanded', 'false'); button.hidden = true;
  const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  icon.setAttribute('viewBox', '0 0 24 24'); icon.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(icon.namespaceURI, 'path');
  path.setAttribute('d', 'M12 5C9 0 4 3 5 7C0 8 2 14 4 14C2 19 7 22 10 19L12 17L14 19C17 22 22 19 20 14C22 14 24 8 19 7C20 3 15 0 12 5ZM12 5V17M5 7L8 9M4 14L8 13M19 7L16 9M20 14L16 13');
  icon.append(path); button.prepend(icon);
  const settingsButton = node('button', '', 'settings-toggle'); settingsButton.id = 'settings-toggle'; settingsButton.type = 'button';
  settingsButton.setAttribute('aria-label', 'Ajustes de la demo'); settingsButton.setAttribute('aria-expanded', 'false'); settingsButton.hidden = true;
  const gearIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  gearIcon.setAttribute('viewBox', '0 0 24 24'); gearIcon.setAttribute('aria-hidden', 'true');
  const gearCircle = document.createElementNS(gearIcon.namespaceURI, 'path'); gearCircle.setAttribute('d', 'M12 15a3 3 0 100-6 3 3 0 000 6z');
  const gearTeeth = document.createElementNS(gearIcon.namespaceURI, 'path');
  gearTeeth.setAttribute('d', 'M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z');
  gearIcon.append(gearCircle, gearTeeth); settingsButton.append(gearIcon);
  const settingsPanel = node('section', '', 'settings-panel'); settingsPanel.id = 'settings-panel'; settingsPanel.hidden = true;
  settingsPanel.setAttribute('role', 'dialog'); settingsPanel.setAttribute('aria-label', 'Ajustes de la demo');
  settingsPanel.append(node('h2', 'Ajustes de la demo'));
  settingsPanel.append(node('p', 'Vacía incendios, llamadas y partes de simulaciones anteriores para empezar una demo desde cero. No modifica los teléfonos de contacto de bomberos.', 'settings-notice'));
  const resetButton = node('button', 'Restablecer base de datos', 'settings-reset'); resetButton.type = 'button';
  const resetStatus = node('p', '', 'settings-status');
  settingsPanel.append(resetButton, resetStatus);
  settingsButton.onclick = () => {
    settingsPanel.hidden = !settingsPanel.hidden;
    settingsButton.setAttribute('aria-expanded', String(!settingsPanel.hidden));
  };
  resetButton.onclick = async () => {
    if (!globalThis.confirm('¿Restablecer la base de datos? Se borrarán los incendios, llamadas y partes de simulaciones anteriores. Los teléfonos de contacto de bomberos no se tocan.')) return;
    resetButton.disabled = true; resetStatus.textContent = 'Restableciendo…';
    try {
      const response = await fetch('/api/admin/reset', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}', signal: globalThis.AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).error || 'No se pudo restablecer');
      resetStatus.textContent = 'Base de datos restablecida. Ya puedes empezar una nueva demo.';
    } catch (error) {
      resetStatus.textContent = error.message && error.message !== 'No se pudo restablecer' ? error.message : 'No se pudo restablecer. Reintenta desde el servidor local.';
    } finally {
      resetButton.disabled = false;
    }
  };
  const witnesses = map && L ? L.layerGroup().addTo(map) : null, markers = new Map();
  if (map && !map.getPane('witnesses')) { map.createPane('witnesses'); map.getPane('witnesses').style.zIndex = 418; }
  const brain = node('section', '', 'brain-view'); brain.id = 'brain-view'; brain.hidden = true;
  const heading = node('header'), headingText = node('div');
  headingText.append(node('span', 'FLAREAI / MEMORIA'), node('h1', 'Conocimiento conectado.'));
  const back = node('button', 'Volver al mapa'); back.type = 'button';
  heading.append(headingText, back);
  const search = node('input'); search.type = 'search'; search.placeholder = 'Buscar incidente o aprendizaje'; search.setAttribute('aria-label', 'Buscar memorias');
  const notice = node('p', 'Abriendo el baúl de conocimiento…', 'brain-notice');
  const workspace = node('div', '', 'brain-workspace'), sidebar = node('nav', '', 'brain-notes');
  const graphPanel = node('div', '', 'brain-graph-panel');
  const graph = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); graph.setAttribute('viewBox', '0 0 800 600'); graph.setAttribute('aria-label', 'Grafo de conocimiento: base, aprendizajes e informes'); graph.classList.add('brain-graph');
  const graphTools = node('div', '', 'brain-graph-tools');
  const resetGraph = node('button', 'Centrar grafo'); resetGraph.onclick = centerGraph;
  function centerGraph() {
    const bounds = graph.getBBox(), width = Math.max(320, bounds.width + 100), height = Math.max(260, bounds.height + 100);
    graph.setAttribute('viewBox', `${bounds.x + bounds.width / 2 - width / 2} ${bounds.y + bounds.height / 2 - height / 2} ${width} ${height}`);
  }
  graphTools.append(node('span', 'GRAFO GLOBAL'), resetGraph);
  graphPanel.append(graphTools, graph, node('div', 'Violeta · Base    /    Turquesa · Aprendizaje    /    Coral · Informe', 'brain-legend'));
  const article = node('article', '', 'brain-article'); article.append(node('p', 'Selecciona un nodo para explorar sus conexiones.'));
  workspace.append(sidebar, graphPanel, article); brain.append(heading, search, notice, workspace);
  document.body.append(button, settingsButton, settingsPanel, brain);
  let records = [], memories = mergeBrainNotes(), lastFocus, selectedId, lastBrainLoad = 0, loadingBrain = false, baseSynced = false, needsCenter = true;
  const labels = { base: 'Conocimiento base', memory: 'Aprendizaje de operación', report: 'Informe final', vault: 'Baúl de conocimiento' };
  const vault = { id: 'vault', title: 'FlareAI · Memoria', kind: 'vault', text: 'La base de conocimiento, los aprendizajes y los informes de cada operación, conectados en un mismo lugar.\n\nSelecciona una nota para explorar sus vínculos. Arrastra el fondo o usa la rueda para recorrer el grafo.' };
  const targets = item => [...(item.links || []), ...(item.reports || []), ...(item.kind === 'base' ? ['vault'] : [])];
  function close() { brain.hidden = true; button.setAttribute('aria-expanded', 'false'); lastFocus?.focus(); }
  back.onclick = close;
  brain.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
  function select(item) {
    selectedId = item.id;
    article.replaceChildren(node('span', labels[item.kind], 'brain-note-kind'), node('h2', item.title));
    if (item.kind === 'report') {
      const link = node('a', 'Descargar informe PDF', 'report-download'); link.href = `/api/reports/${encodeURIComponent(item.id)}.pdf`; link.target = '_blank'; link.rel = 'noopener'; article.append(link);
    }
    for (const line of (item.markdown || item.text || '').split('\n')) {
      if (!line.trim() || line.startsWith('# ')) continue;
      article.append(node(line.startsWith('## ') ? 'h3' : 'p', line.replace(/^## |^- /g, '')));
    }
    if (item.kind === 'base') article.append(node('p', baseSynced ? 'Base curada · disponible en el contexto del director.' : 'Base local · pendiente de sincronizar con el director.', 'brain-notice'));
    const related = [vault, ...memories].filter(other => other.id !== item.id && (targets(item).includes(other.id) || targets(other).includes(item.id)));
    if (related.length) article.append(node('h3', 'Notas conectadas'));
    for (const other of related) {
      const link = node('button', `[[ ${other.title} ]]`, 'brain-backlink'); link.onclick = () => select(other); article.append(link);
    }
    for (const element of workspace.querySelectorAll('[data-note]')) element.classList.toggle('is-selected', element.dataset.note === item.id);
    for (const edge of graph.querySelectorAll('line')) edge.classList.toggle('is-connected', edge.dataset.from === item.id || edge.dataset.to === item.id);
  }
  function renderBrain() {
    sidebar.replaceChildren(node('h2', 'FlareAI-Memoria'), node('p', `${memories.length} notas · Markdown`, 'brain-notice')); graph.replaceChildren();
    const query = search.value.toLocaleLowerCase('es');
    const matches = memories.filter(item => `${item.title} ${item.text || ''} ${item.markdown || ''}`.toLocaleLowerCase('es').includes(query));
    const items = [vault, ...matches.slice(0, 120)];
    const positions = new Map(items.map((item, i) => {
      const angle = i * 2.39996, radius = 145 + 26 * Math.sqrt(i);
      return [item.id, i === 0 ? { x: 400, y: 300 } : { x: 400 + Math.cos(angle) * Math.min(radius, 285), y: 300 + Math.sin(angle) * Math.min(radius, 215) }];
    }));
    const edges = [], seen = new Set();
    for (const item of items) for (const target of targets(item)) {
      const key = [item.id, target].sort().join(':');
      if (!positions.has(target) || seen.has(key)) continue;
      seen.add(key); edges.push([item.id, target]);
    }
    for (let step = 0; step < 80; step++) {
      for (let i = 1; i < items.length; i++) {
        const p = positions.get(items[i].id);
        for (let j = 0; j < items.length; j++) {
          if (i === j) continue;
          const q = positions.get(items[j].id), dx = p.x - q.x, dy = p.y - q.y, d = Math.max(30, Math.hypot(dx, dy));
          p.x += dx / d * 950 / (d * d); p.y += dy / d * 950 / (d * d);
        }
        p.x = Math.max(110, Math.min(690, p.x)); p.y = Math.max(70, Math.min(520, p.y));
      }
      for (const [a, b] of edges) {
        const p = positions.get(a), q = positions.get(b), dx = q.x - p.x, dy = q.y - p.y, d = Math.max(1, Math.hypot(dx, dy)), force = (d - 175) * .008;
        if (a !== 'vault') { p.x += dx / d * force; p.y += dy / d * force; }
        if (b !== 'vault') { q.x -= dx / d * force; q.y -= dy / d * force; }
      }
    }
    for (const [a, b] of edges) {
      const from = positions.get(a), to = positions.get(b), line = document.createElementNS(graph.namespaceURI, 'line');
      for (const [key, value] of Object.entries({ x1: from.x, y1: from.y, x2: to.x, y2: to.y })) line.setAttribute(key, value);
      line.dataset.from = a; line.dataset.to = b; graph.append(line);
    }
    for (const kind of ['base', 'memory', 'report']) {
      sidebar.append(node('h3', `${labels[kind]} · ${matches.filter(item => item.kind === kind).length}`));
      for (const item of matches.filter(item => item.kind === kind)) {
        const choice = node('button', item.title); choice.dataset.note = item.id; choice.onclick = () => select(item); sidebar.append(choice);
      }
    }
    for (const item of items) {
      const position = positions.get(item.id), group = document.createElementNS(graph.namespaceURI, 'g');
      group.dataset.note = item.id;
      group.setAttribute('transform', `translate(${position.x} ${position.y})`); group.setAttribute('tabindex', '0'); group.setAttribute('role', 'button'); group.setAttribute('aria-label', item.title);
      const circle = document.createElementNS(graph.namespaceURI, 'circle'); circle.setAttribute('r', item.kind === 'vault' ? '20' : item.kind === 'base' ? '11' : '8'); circle.setAttribute('fill', { vault: '#8574a8', base: '#a390be', memory: '#67a995', report: '#d9977b' }[item.kind]);
      const text = document.createElementNS(graph.namespaceURI, 'text'); text.setAttribute('y', '32'); text.setAttribute('text-anchor', 'middle'); text.textContent = item.title.length > 30 ? item.title.slice(0, 28) + '…' : item.title;
      group.append(circle, text); group.onclick = () => select(item); group.onkeydown = event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(item); } }; graph.append(group);
    }
    if (!matches.length) sidebar.append(node('p', 'No hay notas que coincidan con la búsqueda.'));
    if (matches.length > 120) sidebar.append(node('p', 'Grafo: primeras 120 coincidencias. Usa la búsqueda para acotar.'));
    select(items.find(item => item.id === selectedId) || vault);
  }
  let drag;
  graph.onpointerdown = event => {
    if (event.target.closest('g')) return;
    drag = { x: event.clientX, y: event.clientY, box: graph.getAttribute('viewBox').split(' ').map(Number) }; graph.setPointerCapture(event.pointerId);
  };
  graph.onpointermove = event => {
    if (!drag) return;
    const [x, y, w, h] = drag.box, scale = Math.max(w / graph.clientWidth, h / graph.clientHeight);
    graph.setAttribute('viewBox', `${x - (event.clientX - drag.x) * scale} ${y - (event.clientY - drag.y) * scale} ${w} ${h}`);
  };
  graph.onpointerup = graph.onpointercancel = () => { drag = null; };
  graph.addEventListener('wheel', event => {
    event.preventDefault();
    const [x, y, w, h] = graph.getAttribute('viewBox').split(' ').map(Number), next = Math.max(300, Math.min(1800, w * (event.deltaY > 0 ? 1.12 : .89))), ratio = next / w;
    graph.setAttribute('viewBox', `${x + (w - next) / 2} ${y + (h - h * ratio) / 2} ${next} ${h * ratio}`);
  }, { passive: false });
  search.oninput = () => { renderBrain(); centerGraph(); };
  async function refreshBrain() {
    if (loadingBrain) return;
    loadingBrain = true; lastBrainLoad = Date.now();
    try {
      const response = await fetch('/api/brain', { signal: globalThis.AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error('Memoria no disponible');
      const notes = (await response.json()).notes;
      if (!Array.isArray(notes)) throw new Error('Formato de memoria no válido');
      baseSynced = notes.filter(item => item.kind === 'base').length >= 4;
      memories = mergeBrainNotes(notes); renderBrain();
      if (needsCenter && !brain.hidden) { centerGraph(); needsCenter = false; }
      notice.textContent = `4 notas base · ${memories.filter(item => item.kind === 'memory').length} aprendizajes · ${memories.filter(item => item.kind === 'report').length} informes · ${baseSynced ? 'Contexto IA conectado' : 'Base local'}`;
    } catch { notice.textContent = 'Base local disponible. No se pudo actualizar el historial; se conservan las notas cargadas.'; }
    finally { loadingBrain = false; }
  }
  button.onclick = () => {
    lastFocus = document.activeElement; brain.hidden = false; button.setAttribute('aria-expanded', 'true'); back.focus();
    needsCenter = true; renderBrain(); centerGraph();
    refreshBrain();
  };
  function tooltipFor(item, record) {
    const box = node('div', '', 'witness-card');
    const head = node('strong', item.source === 'webcall' ? 'Llamada 112' : item.speaker);
    head.append(node('time', ` · ${new Date(item.at * 1000).toLocaleTimeString('es-ES')}`));
    box.append(head, node('p', item.text));
    if (item.source === 'webcall') {
      box.append(node('small', PHONE[record.outbound?.status] || 'Seguimiento del incidente'));
      if (record.assessment?.summary) box.append(node('small', record.assessment.summary));
      if (record.report_id) box.append(node('small', 'Operación completada · informe PDF en Cerebro', 'witness-report'));
    } else if (item.assessment) {
      box.append(node('small', `${LABELS[item.assessment.status] || 'Evaluación pendiente'} · ${item.assessment.reason || ''}`));
    } else box.append(node('small', 'Testimonio simulado · pendiente de evaluar'));
    return box;
  }
  function iconFor(item, record) {
    const status = item.assessment?.status || 'pending';
    const note = item.source === 'webcall' ? 'Llamada 112' : 'Llamada registrada';
    return L.divIcon({ className: `witness-marker ${item.source === 'webcall' ? 'real-call' : 'simulated'} credibility-${status}${record.report_id && item.source === 'webcall' ? ' has-report' : ''}`,
      html: `<span class="witness-body">${PERSON}<span class="witness-note">${note}</span></span>`, iconSize: [22, 26], iconAnchor: [11, 26], tooltipAnchor: [0, -24] });
  }
  function renderWitnesses(state) {
    if (!witnesses) return;
    const alive = new Set();
    for (const record of records) {
      const incident = findIncident(record.id);
      const phase = state.scenario?.incidents?.[record.id]?.phase ?? state.auto?.[record.id]?.phase ?? incident?.scenario?.phase;
      if (!incident || phase === 'closed' || record.reported || record.report_id || incident.demo_report?.cancelled) continue;
      const radius = incident.scenario?.radius_km ?? .18;
      for (const item of testimonyRows([record]).slice(0, 100)) {
        alive.add(item.id);
        const key = JSON.stringify([item.assessment?.status, record.report_id, record.outbound?.status, record.assessment?.summary, Math.round(radius * 20)]);
        let entry = markers.get(item.id);
        if (!entry) {
          const marker = L.marker(witnessPosition(item, incident, radius), { icon: iconFor(item, record), pane: 'witnesses', keyboard: false, riseOnHover: true, alt: `${item.speaker}: ${item.text}` });
          marker.bindTooltip(tooltipFor(item, record), { direction: 'top', className: 'witness-tooltip', opacity: 1 });
          marker.addTo(witnesses);
          entry = { marker, key }; markers.set(item.id, entry);
        } else if (entry.key !== key) {
          entry.marker.setIcon(iconFor(item, record)); entry.marker.setTooltipContent(tooltipFor(item, record));
          entry.marker.setLatLng(witnessPosition(item, incident, radius)); entry.key = key;
        }
      }
    }
    for (const [id, entry] of markers) if (!alive.has(id)) { witnesses.removeLayer(entry.marker); markers.delete(id); }
  }
  return {
    update(state) {
      button.hidden = !state.operations;
      settingsButton.hidden = !state.operations;
      if (!state.operations) settingsPanel.hidden = true;
      records = state.operations?.incidents || [];
      if (!brain.hidden && Date.now() - lastBrainLoad > 10000) refreshBrain();
      renderWitnesses(state);
    },
  };
}
