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
  headingText.append(node('span', 'MEMORIA OPERATIVA · SIMULACIONES'), node('h1', 'Lo que hemos aprendido.'));
  const back = node('button', 'Volver al mapa'); back.type = 'button';
  heading.append(headingText, back);
  const search = node('input'); search.type = 'search'; search.placeholder = 'Buscar incidente o aprendizaje'; search.setAttribute('aria-label', 'Buscar memorias');
  const notice = node('p', 'Twin conserva la memoria; los Markdown se sincronizan al vault local.', 'brain-notice');
  const workspace = node('div', '', 'brain-workspace'), sidebar = node('nav', '', 'brain-notes');
  const graph = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); graph.setAttribute('viewBox', '0 0 800 600'); graph.setAttribute('aria-label', 'Relaciones entre operaciones y aprendizajes'); graph.classList.add('brain-graph');
  const article = node('article', '', 'brain-article'); article.append(node('p', 'Selecciona una nota o un informe.'));
  workspace.append(sidebar, graph, article); brain.append(heading, search, notice, workspace);
  document.body.append(button, settingsButton, settingsPanel, brain);
  let records = [], memories = [], lastFocus;
  function close() { brain.hidden = true; button.setAttribute('aria-expanded', 'false'); lastFocus?.focus(); }
  back.onclick = close;
  brain.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
  function select(item) {
    article.replaceChildren(node('h2', item.title), node('p', item.kind === 'report' ? 'Informe de simulación' : 'Aprendizaje basado en un ensayo', 'brain-notice'), node('pre', item.markdown || item.text));
    if (item.kind === 'report') {
      const link = node('a', 'Descargar informe PDF', 'report-download'); link.href = `/api/reports/${encodeURIComponent(item.id)}.pdf`; link.target = '_blank'; link.rel = 'noopener'; article.prepend(link);
    }
  }
  function renderBrain() {
    sidebar.replaceChildren(); graph.replaceChildren();
    const query = search.value.toLocaleLowerCase('es');
    const items = memories.filter(item => `${item.title} ${item.text || ''}`.toLocaleLowerCase('es').includes(query));
    const positions = new Map(items.map((item, i) => {
      const angle = i * 2.39996, radius = 50 + 35 * Math.sqrt(i);
      return [item.id, { x: 400 + Math.cos(angle) * Math.min(radius, 310), y: 300 + Math.sin(angle) * Math.min(radius, 230) }];
    }));
    for (const item of items) for (const target of item.reports || []) {
      const from = positions.get(item.id), to = positions.get(target);
      if (!to) continue;
      const line = document.createElementNS(graph.namespaceURI, 'line');
      for (const [key, value] of Object.entries({ x1: from.x, y1: from.y, x2: to.x, y2: to.y })) line.setAttribute(key, value);
      graph.append(line);
    }
    for (const item of items) {
      const choice = node('button', item.title); choice.onclick = () => select(item); sidebar.append(choice);
      const position = positions.get(item.id), group = document.createElementNS(graph.namespaceURI, 'g');
      group.setAttribute('transform', `translate(${position.x} ${position.y})`); group.setAttribute('tabindex', '0'); group.setAttribute('role', 'button'); group.setAttribute('aria-label', item.title);
      const circle = document.createElementNS(graph.namespaceURI, 'circle'); circle.setAttribute('r', item.kind === 'report' ? '13' : '8'); circle.setAttribute('fill', item.kind === 'report' ? '#ee9477' : '#8d80c4');
      const text = document.createElementNS(graph.namespaceURI, 'text'); text.setAttribute('y', '29'); text.setAttribute('text-anchor', 'middle'); text.textContent = item.title.slice(0, 28);
      group.append(circle, text); group.onclick = () => select(item); group.onkeydown = event => { if (event.key === 'Enter') select(item); }; graph.append(group);
    }
    if (!items.length) sidebar.append(node('p', 'Aún no hay memorias. No se generan aprendizajes si no hay nada útil que conservar.'));
  }
  search.oninput = renderBrain;
  button.onclick = async () => {
    lastFocus = document.activeElement; brain.hidden = false; button.setAttribute('aria-expanded', 'true'); back.focus();
    try {
      const response = await fetch('/api/brain', { signal: globalThis.AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error('No se pudo consultar Twin');
      memories = (await response.json()).notes; renderBrain();
      notice.textContent = 'Notas breves en Twin y archivos Markdown reales en el vault local. No son protocolos de emergencia.';
    } catch { notice.textContent = 'Memoria temporalmente no disponible. Puedes volver al mapa y reintentar; no se han perdido datos.'; }
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
  function renderWitnesses() {
    if (!witnesses) return;
    const alive = new Set();
    for (const record of records) {
      const incident = findIncident(record.id);
      if (!incident) continue;
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
      renderWitnesses();
    },
  };
}
