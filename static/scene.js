import { createTraffic } from './traffic.js';

export function priorityLine(record) {
  return record ? `Prioridad ${Number(record.priority).toFixed(1)}/10 · ${record.priority_reason}` : '';
}

export function extinctionLine(record) {
  if (!record || !['active', 'contained'].includes(record.phase)) return '';
  const working = record.suppression_power || 0;
  const pct = Math.max(0, Math.min(100, Number(record.extinguished_pct) || 0));
  return working ? `Extinción simulada ${pct} % · ${working} ${working === 1 ? 'medio trabajando' : 'medios trabajando'} · más medios, antes` : record.phase === 'active' ? 'Fuego creciendo · medios en camino' : '';
}

const HOSPITAL_ROLES = {
  transfer: 'destino del traslado de la ambulancia',
  reserved: 'plaza ficticia reservada en esta sesión',
  avoided: 'descartado por quedar dentro del entorno del fuego',
  threatened: 'próximo a un fuego del escenario',
};

export const HOSPITAL_THREAT_LIMIT = 1;
const nearKm = (a, b) => Math.hypot((a.lat - b.lat) * 111.32, (a.lon - b.lon) * 111.32 * Math.cos(a.lat * Math.PI / 180));

export function engagedHospitals(scene, assignments = {}) {
  const transfers = new Set(Object.values(assignments).map(a => a.hospital_id).filter(Boolean));
  const discarded = new Set(Object.values(assignments).flatMap(a => a.avoided_hospital_ids || []));
  const open = Object.values(scene?.incidents || {}).filter(record => record.phase !== 'closed');
  const hospitals = scene?.hospitals || [];
  const role = hospital => transfers.has(hospital.id) ? 'transfer' : hospital.occupied > 0 ? 'reserved'
    : discarded.has(hospital.id) ? 'avoided' : null;
  const threatened = hospitals.filter(hospital => !role(hospital))
    .map(hospital => ({ hospital, km: Math.min(...open.filter(record => (record.hospital_threats || []).includes(hospital.name)).map(record => nearKm(hospital, record))) }))
    .filter(candidate => Number.isFinite(candidate.km)).sort((a, b) => a.km - b.km)
    .slice(0, HOSPITAL_THREAT_LIMIT).map(candidate => candidate.hospital.id);
  return hospitals.flatMap(hospital => {
    const kind = role(hospital) || (threatened.includes(hospital.id) ? 'threatened' : null);
    return kind ? [{ ...hospital, role: kind, role_label: HOSPITAL_ROLES[kind] }] : [];
  });
}

export const THREAT_MARGIN_KM = .3;

// Superficie de riesgo ilustrativa: sigue el contorno del fuego del escenario con un margen
// reducido, más amplio a favor del viento. Sin huella disponible recae en un círculo pequeño.
export function threatOutline(record, footprint, marginKm = THREAT_MARGIN_KM) {
  const ring = footprint?.type === 'Polygon' ? footprint.coordinates[0] : null;
  const east = 111.32 * Math.cos(record.lat * Math.PI / 180), wind = record.wind_to * Math.PI / 180;
  if (!ring || ring.length < 4) {
    return Array.from({ length: 48 }, (_, i) => {
      const angle = i / 48 * 2 * Math.PI, reach = record.radius_km + marginKm;
      return [record.lat + Math.cos(angle) * reach / 111.32, record.lon + Math.sin(angle) * reach / east];
    });
  }
  return ring.slice(0, -1).map(([lon, lat]) => {
    const dx = (lon - record.lon) * east, dy = (lat - record.lat) * 111.32, length = Math.hypot(dx, dy) || 1;
    const downwind = Math.max(0, (dx * Math.sin(wind) + dy * Math.cos(wind)) / length);
    const reach = marginKm * (.7 + downwind * .9);
    return [lat + dy / length * reach / 111.32, lon + dx / length * reach / east];
  });
}

export function createSceneView({ map, L, document, fetch, focus, findIncident = () => null }) {
  const $ = id => document.getElementById(id), traffic = createTraffic({ map, L, document, fetch });
  const hospitals = L.layerGroup(), cuts = L.layerGroup().addTo(map), hazards = L.layerGroup().addTo(map);
  let state = null, session = null, offset = 0, renderedSequence = -1, mapKey = '', events = new Map(), historyLoading = false;
  const toggle = $('history-toggle'), panel = $('decision-panel');
  function node(tag, text, className = '') {
    const item = document.createElement(tag); item.textContent = text; item.className = className; return item;
  }
  function visibility() {
    if (map.getZoom() >= 11 && state?.scenario) hospitals.addTo(map); else hospitals.remove();
  }
  map.on('zoom', visibility);
  async function post(action, extra = {}) {
    $('scene-feedback').textContent = 'Aplicando cambio del escenario…';
    try {
      const response = await fetch('/api/scenario', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action, incident_id: $('scene-incident').value, ...extra }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'No se pudo aplicar el cambio');
      $('scene-feedback').textContent = 'Cambio aplicado · observa la reacción y el historial.';
    } catch (error) { $('scene-feedback').textContent = error.message; }
  }
  toggle.onclick = () => {
    panel.hidden = !panel.hidden; toggle.setAttribute('aria-expanded', String(!panel.hidden));
    if (!panel.hidden) { $('agent-evidence').hidden = true; loadHistory(); }
  };
  $('history-close').onclick = () => { panel.hidden = true; toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); };
  $('scene-barcelona').onclick = () => { map.fitBounds([[41.34, 2.05], [41.48, 2.27]], { animate: false }); };
  for (const button of document.querySelectorAll('[data-scene-action]')) button.onclick = () => post(button.dataset.sceneAction);
  $('scene-field').onclick = () => post('field', { role: $('scene-role').value, report: $('scene-report').value });
  $('cancel-alert').onclick = async () => {
    const id = $('cancel-alert').dataset.id;
    try {
      const response = await fetch('/api/director/cancel-alert', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
      if (!response.ok) throw new Error('La propuesta ya no está pendiente');
      $('alert-countdown').hidden = true;
    } catch (error) { $('alert-countdown-message').textContent = error.message; }
  };
  function history() {
    if (renderedSequence === events.size) return;
    renderedSequence = events.size;
    const list = $('decision-history'), bottom = list.scrollHeight - list.scrollTop - list.clientHeight < 50;
    list.replaceChildren();
    for (const event of [...events.values()].sort((a, b) => a.sequence - b.sequence)) {
      const entry = node('li', '', `history-event ${event.kind}`);
      entry.append(node('time', new Date(event.at * 1000).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })), node('strong', event.message), node('p', event.reason || ''));
      if (event.incident_id) {
        const button = node('button', state?.scenario?.incidents[event.incident_id]?.name || 'Ver aviso');
        button.onclick = () => focus(event.incident_id); entry.append(button);
      }
      list.append(entry);
    }
    if (bottom) list.scrollTop = list.scrollHeight;
    $('history-count').textContent = `${events.size} pasos · memoria de esta sesión`;
  }
  async function loadHistory() {
    if (historyLoading) return;
    historyLoading = true;
    const token = session;
    try {
      const response = await fetch('/api/director/history');
      if (!response.ok) throw new Error('Historial no disponible');
      const result = await response.json();
      if (token !== session || result.session_id !== session) return;
      for (const event of result.events) events.set(event.sequence, event);
      history();
    } catch { $('history-count').textContent = 'Historial SQL no disponible; se conservan los eventos recibidos.'; }
    finally { historyLoading = false; }
  }
  function renderWorld() {
    const scene = state?.scenario;
    $('scene-controls').hidden = !scene;
    $('scene-status').textContent = !scene ? 'Observatorio · escenario de sala desactivado' : state.status === 'unconfigured' || state.status === 'auth_required' ? 'Director no conectado · sin nuevas decisiones IA' : `Director: ${{ thinking: 'decidiendo', watching: 'vigilando', idle: 'vigilando', error: 'reintentando', limited: 'límite de cuota' }[state.status] || state.status} · escenario simulado`;
    if (!scene) return;
    const select = $('scene-incident'), selected = select.value;
    const records = Object.values(scene.incidents).filter(r => !r.linked_call_id);
    const options = records.filter(r => r.phase !== 'closed').map(r => [r.id, r.name]);
    if (JSON.stringify(options) !== select.dataset.options) {
      select.dataset.options = JSON.stringify(options); select.replaceChildren();
      for (const [id, name] of options) { const option = node('option', name); option.value = id; select.append(option); }
      if (options.some(([id]) => id === selected)) select.value = selected;
    }
    $('scene-summary').replaceChildren();
    for (const record of records) {
      const card = node('button', '', 'scene-incident-card');
      card.append(node('strong', record.name), node('span', priorityLine(record)), node('small', `${record.source === 'sensor' ? 'Sensor FIRMS' : record.source === 'call' ? 'Llamada 112' : 'Ejercicio simulado'} · ${{ active: 'Intervención', contained: 'Contenido', watching: 'Vigilancia', releasing: 'Retirada', closed: 'Cerrado' }[record.phase]}`), node('small', extinctionLine(record)), node('small', record.contrast.label));
      card.onclick = () => focus(record.id); $('scene-summary').append(card);
    }
    const engaged = engagedHospitals(scene, state.assignments);
    const key = JSON.stringify([engaged, scene.closures, records.map(r => [r.id, Math.round(r.radius_km * 30), r.phase, r.wind_to, Boolean(findIncident(r.id)?.scenario?.footprint)])]);
    if (key === mapKey) return;
    mapKey = key; hospitals.clearLayers(); cuts.clearLayers(); hazards.clearLayers();
    for (const hospital of engaged) {
      const marker = L.marker([hospital.lat, hospital.lon], { icon: L.divIcon({ className: `hospital-marker ${hospital.role}`, html: 'H', iconSize: [25, 25], iconAnchor: [12, 12] }) }).addTo(hospitals);
      const detail = node('div', '');
      detail.append(node('strong', hospital.name || 'Hospital del atlas'), node('p', `Visible porque está ${hospital.role_label}.`),
        node('p', `${hospital.emergency_ward === 'own' ? 'Urgencias publicadas en el recinto' : 'Urgencias publicadas junto al recinto'}${hospital.official_registry ? ' · consta en el registro estatal de hospitales' : ' · sin coincidencia en el registro estatal'}${hospital.registered_beds ? ` · ${hospital.registered_beds} camas registradas` : ''}. Dato documental del atlas, no disponibilidad actual.`),
        node('p', hospital.merged_ids?.length ? `Unifica ${hospital.merged_ids.length + 1} registros del atlas situados en el mismo recinto.` : ''),
        node('p', `${hospital.capacity - hospital.occupied}/${hospital.capacity} plazas ficticias · capacidad NO real`));
      marker.bindTooltip(node('span', `${hospital.name} · ${hospital.role_label} · ${hospital.capacity - hospital.occupied}/${hospital.capacity} demo`)).bindPopup(detail);
    }
    for (const closure of Object.values(scene.closures)) {
      const points = closure.coordinates.map(([lon, lat]) => [lat, lon]);
      L.polyline(points, { color: '#c94048', weight: 7, dashArray: '5 4' }).bindTooltip(node('span', closure.label)).addTo(cuts);
      const middle = [(points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2];
      L.marker(middle, { icon: L.divIcon({ className: 'closure-marker', html: '×', iconSize: [24, 24] }) }).addTo(cuts);
    }
    for (const record of records) {
      if (record.phase === 'closed') continue;
      const color = record.phase === 'active' ? '#e37554' : '#60a18c';
      const angle = record.wind_to * Math.PI / 180, length = (record.radius_km + .55) / 111.32;
      const end = [record.lat + Math.cos(angle) * length, record.lon + Math.sin(angle) * length / Math.cos(record.lat * Math.PI / 180)];
      L.polyline([[record.lat, record.lon], end], { color: '#738a9c', weight: 2, dashArray: '4 5', interactive: false }).addTo(hazards);
      L.marker(end, { interactive: false, icon: L.divIcon({ className: 'scenario-wind', html: `Viento demo ${Math.round(record.wind_to)}°`, iconSize: [110, 20] }) }).addTo(hazards);
      if (record.maritime) L.marker([record.lat, record.lon], { icon: L.divIcon({ className: 'maritime-marker', html: '<svg viewBox="0 0 32 28" aria-hidden="true"><path d="M3 16h26l-5 8H8zM10 15V8h12v7M16 8V3M3 27l6-2 7 2 7-2 6 2"/></svg>', iconSize: [34, 30] }) }).bindTooltip(node('span', 'Barco comunicado en llamada · posición ilustrativa')).addTo(hazards);
      const footprint = findIncident(record.id)?.scenario?.footprint;
      L.polygon(threatOutline(record, footprint), { color, weight: 1.2, dashArray: '4 7', fillColor: color, fillOpacity: .07, interactive: false, className: 'threat-surface' }).addTo(hazards);
      const label = node('div', ''); label.append(node('strong', priorityLine(record)), node('p', `${record.exposed_population} residentes censales en el entorno simulado · no afectados medidos`), node('p', `Viento del escenario hacia ${Math.round(record.wind_to)}° · crecimiento y contención ilustrativos`));
      L.circleMarker([record.lat, record.lon], { radius: 14, opacity: 0, fillOpacity: 0 }).bindTooltip(label).addTo(hazards);
    }
    visibility();
  }
  return {
    update(next) {
      state = next; offset = (next.server_time || Date.now() / 1000) * 1000 - Date.now();
      if (session !== next.session_id) { session = next.session_id; events = new Map(); renderedSequence = -1; mapKey = ''; if (!panel.hidden) loadHistory(); }
      for (const event of next.events || []) events.set(event.sequence, event);
      history(); renderWorld(); traffic.update(next.scenario);
      const invalidated = [...events.values()].reverse().find(e => e.kind === 'invalidated');
      $('plan-invalidated').hidden = !invalidated || Date.now() + offset - invalidated.at * 1000 > 16000;
      if (invalidated) $('plan-invalidated').textContent = `Plan anterior invalidado · ${invalidated.reason} · recalculando`;
    },
    tick() {
      const proposal = Object.values(state?.pending_alerts || {}).sort((a, b) => a.due_at - b.due_at)[0];
      $('alert-countdown').hidden = !proposal;
      if (proposal) {
        const remaining = Math.max(0, Math.ceil(proposal.due_at - (Date.now() + offset) / 1000));
        $('alert-countdown-number').textContent = remaining ? String(remaining) : '…';
        $('alert-countdown-message').textContent = `${proposal.message} · envío solo al simulador móvil`;
        $('cancel-alert').dataset.id = proposal.id;
      }
    },
    setPaused(value) { traffic.setPaused(value); },
  };
}
