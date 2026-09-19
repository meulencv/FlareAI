const LABELS = { supported: 'Coherente', uncertain: 'Por contrastar', unlikely: 'Poco verosímil', prank: 'Indicios de broma' };
const PHONE = { waiting_arrival: 'Llamada al llegar bomberos', disabled: 'Telefonía pendiente de activar', starting: 'Preparando llamada', dialing: 'Llamada a bomberos en curso', retry_backup: 'Intentando contacto de respaldo', unreachable: 'Sin respuesta de los contactos', uncertain: 'Estado telefónico sin confirmar', completed: 'Parte recibido', needs_report: 'Parte pendiente de revisión' };

export function testimonyRows(records) {
  return records.flatMap(record => {
    const assessment = new Map((record.assessment?.testimonies || []).map(item => [item.id, item]));
    return [...(record.citizen ? [record.citizen] : []), ...(record.testimonies || [])].map(item => ({ ...item, assessment: assessment.get(item.id) }));
  }).sort((a, b) => b.at - a.at || a.id.localeCompare(b.id));
}

export function createOperationView({ document, fetch }) {
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
  const feed = node('aside', '', 'calls-panel'); feed.id = 'calls-panel'; feed.hidden = true;
  const title = node('h2', 'Voces del incidente'), count = node('p', '', 'calls-count');
  const caption = node('p', 'Llamada 112 + testimonios sintéticos · simulacro', 'calls-caption');
  const details = node('div', '', 'operation-conclusions');
  const list = node('ol', '', 'testimony-list'); list.setAttribute('aria-label', 'Testimonios recibidos');
  feed.append(title, count, caption, details, list);
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
  document.body.append(feed, button, brain);
  let signature = '', records = [], memories = [], lastFocus;
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
  return {
    update(state) {
      button.hidden = !state.operations;
      records = state.operations?.incidents || [];
      feed.hidden = !records.length;
      if (!state.operations) return;
      const next = JSON.stringify(records);
      if (signature === next) return;
      signature = next;
      const rows = testimonyRows(records);
      count.textContent = `${rows.length} avisos recibidos · ${state.status === 'collecting' ? 'Recopilando testimonios' : 'Evaluación y respuesta autónoma'}`;
      details.replaceChildren();
      for (const record of records) {
        const box = node('section'); box.append(node('strong', record.name), node('p', PHONE[record.outbound?.status] || 'Seguimiento del incidente'));
        if (record.assessment?.summary) box.append(node('p', record.assessment.summary, 'assessment-summary'));
        for (const request of Object.values(record.requests || {})) box.append(node('small', `${request.kind}: ${request.fulfilled}/${request.quantity} · ${request.status}`));
        if (record.metrics) {
          const m = record.metrics, display = value => value == null ? 'Sin datos' : value.toLocaleString('es-ES');
          box.append(node('p', 'Resultados estimados del simulacro', 'assessment-summary'));
          for (const [label, value] of [['Personas asistidas', m.assisted_people], ['Vidas potencialmente salvadas', m.potential_lives_saved], ['Superficie evitada (ha)', m.avoided_area_ha], ['CO2 evitado (t)', m.avoided_co2_t], ['Valor hipotético central (EUR)', m.carbon_value_eur?.[1]]]) box.append(node('small', `${label}: ${display(value)}`));
          box.append(node('small', 'Supuestos de demo. No son créditos de carbono emitidos ni resultados clínicos.'));
        }
        if (record.report_id) { const link = node('a', 'Operación completada · Descargar PDF'); link.href = `/api/reports/${encodeURIComponent(record.report_id)}.pdf`; link.target = '_blank'; link.rel = 'noopener'; box.append(link); }
        details.append(box);
      }
      const scroll = list.scrollTop;
      list.replaceChildren(...rows.slice(0, 100).map(item => {
        const row = node('li', '', item.source === 'webcall' ? 'testimony real-call' : 'testimony');
        row.append(node('strong', item.speaker), node('time', new Date(item.at * 1000).toLocaleTimeString('es-ES')), node('p', item.text));
        row.append(node('span', item.source === 'webcall' ? 'Webcall' : 'Testimonio simulado', 'testimony-source'));
        if (item.assessment) { row.append(node('span', LABELS[item.assessment.status], `credibility ${item.assessment.status}`)); row.title = item.assessment.reason; }
        return row;
      }));
      list.scrollTop = scroll;
    },
  };
}
