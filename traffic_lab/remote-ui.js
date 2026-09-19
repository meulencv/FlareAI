(() => {
  const el = id => document.getElementById(id);
  const labels = {low: 'Baja', moderate: 'Media', high: 'Alta', unknown: 'No evaluable'};
  const cards = new Map();
  let ready = false;
  let running = false;
  let job = null;
  let nextRefresh = 0;
  let pollTimer = null;
  let incidents = [];

  async function request(path, body) {
    const response = await fetch(path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {});
    const value = await response.json();
    if (!response.ok) throw new Error(value.error || `HTTP ${response.status}`);
    return value;
  }

  function text(tag, value, className = '') {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    return node;
  }

  function format(value, zone = 'Europe/Madrid') {
    return value && Number.isFinite(Date.parse(value))
      ? new Date(value).toLocaleString('es-ES', {timeZone: zone, timeZoneName: 'short'}) : 'No disponible';
  }

  function updateBudget(budget) {
    if (!budget) return;
    el('remote-budget').textContent = `Presupuesto local Vercel: ${budget.remaining_usd.toFixed(3)} / ${budget.cap_usd.toFixed(2)} USD disponibles`;
    if (budget.remaining_usd < 0.9) {
      el('remote-auto').checked = false;
      el('remote-budget').textContent += ' · no alcanza para otra reserva de dos imágenes';
    }
  }

  function updateControls() {
    el('remote-submit').disabled = !ready || running;
    el('remote-submit').textContent = running ? 'Consultando HappyRobot…' : 'Analizar entorno con IA';
    for (const id of ['remote-incident', 'remote-lat', 'remote-lon', 'remote-radius', 'remote-description']) el(id).disabled = running;
    el('remote-export').disabled = !job || !['completed', 'failed'].includes(job.status);
  }

  function fillCards(value) {
    for (const camera of value.selected || []) {
      if (cards.has(camera.id)) continue;
      const card = document.createElement('article');
      card.className = 'remote-card panel';
      const header = document.createElement('div');
      header.className = 'panel-head';
      const badge = text('span', 'ANALIZANDO', 'badge');
      header.append(text('h3', camera.name), badge);
      const image = document.createElement('img');
      image.alt = `Vista de ${camera.name}`;
      image.loading = 'lazy';
      image.src = `/api/remote/image?job=${encodeURIComponent(value.job_id)}&camera=${encodeURIComponent(camera.id)}`;
      const imageNotice = text('p', 'Vista del proveedor: puede haberse renovado después del análisis.', 'muted');
      image.addEventListener('error', () => {image.hidden = true; imageNotice.textContent = 'La vista del proveedor no está disponible. Consulta el estado del análisis.';});
      const body = document.createElement('div');
      body.className = 'remote-card-body';
      const count = text('strong', '—');
      const density = text('span', 'Esperando resultado');
      const metrics = document.createElement('div');
      metrics.className = 'remote-metrics';
      metrics.append(count, text('span', 'vehículos estimados · no aforo'), density);
      const timing = document.createElement('dl');
      timing.className = 'metadata';
      const fields = {};
      for (const [key, label] of [['capture', 'Hora leída en la imagen'], ['age', 'Antigüedad · máximo 10 min'], ['analysis', 'Hora del análisis'], ['expiry', 'Caduca a las']]) {
        fields[key] = text('dd', '—');
        timing.append(text('dt', label), fields[key]);
      }
      const reason = text('p', 'HappyRobot está analizando esta cámara.');
      const caveat = text('p', 'El reloj se transcribe mediante IA. No es una verificación independiente de la cámara.', 'notice');
      body.append(text('p', `${camera.source} · ${camera.distance_km?.toFixed(2) ?? '—'} km en línea recta · ${camera.id}`, 'muted'),
        metrics, timing, reason, caveat, imageNotice);
      card.append(header, image, body);
      el('remote-results').append(card);
      cards.set(camera.id, {badge, count, density, fields, reason});
    }
  }

  function refreshClocks() {
    if (!job) return;
    for (const camera of job.selected || []) {
      const card = cards.get(camera.id);
      if (!card) continue;
      const result = (job.results || []).find(item => item.camera_id === camera.id);
      if (!result) {
        if (['completed', 'failed'].includes(job.status)) {
          card.badge.textContent = 'SIN RESULTADO';
          card.reason.textContent = 'No se pudo obtener una lectura válida de esta fuente. No se considera tráfico libre.';
        }
        continue;
      }
      const age = result.captured_at ? (Date.now() - Date.parse(result.captured_at)) / 1000 : NaN;
      const fresh = Number.isFinite(age) && age >= 0 && age <= 600;
      const usable = fresh && !['future', 'stale'].includes(result.freshness) && result.image_status === 'road_visible' && result.visual_estimate?.vehicle_count_estimate != null;
      card.badge.textContent = !Number.isFinite(age) ? 'HORA DESCONOCIDA' : age < 0 || result.freshness === 'future' ? 'RELOJ INCOHERENTE' : age > 600 || result.freshness === 'stale' ? 'CADUCADA' : usable ? '≤10 MIN SEGÚN RELOJ' : 'IMAGEN NO EVALUABLE';
      card.badge.dataset.state = usable ? 'recent' : 'unknown';
      card.count.textContent = usable ? result.visual_estimate.vehicle_count_estimate : '—';
      card.density.textContent = usable ? `Densidad ${labels[result.visual_estimate.density]?.toLowerCase() || 'no evaluable'}` : 'Sin lectura actual utilizable';
      card.fields.capture.textContent = result.timestamp_text
        ? `${result.timestamp_text} · ${result.capture_timezone} · leída por IA` : 'No se pudo leer fecha y hora completas';
      card.fields.age.textContent = Number.isFinite(age) && age >= 0 ? `${Math.floor(age / 60)} min ${Math.floor(age % 60)} s` : 'No verificable';
      card.fields.analysis.textContent = format(result.analyzed_at, result.capture_timezone);
      card.fields.expiry.textContent = format(result.expires_at, result.capture_timezone);
      card.reason.textContent = usable ? result.reason : age > 600
        ? 'La hora leída por IA queda fuera de los 10 minutos. Puede ser una captura antigua o una lectura errónea del reloj; se descarta como estado actual.'
        : 'Falta una imagen o un reloj legible y coherente. No se inventa que la carretera esté libre.';
    }
    if (el('remote-auto').checked && !running) {
      el('remote-next').textContent = document.hidden ? 'Seguimiento pausado: pestaña oculta.'
        : `Siguiente consulta en ${Math.max(0, Math.ceil((nextRefresh - Date.now()) / 1000))} s; máximo dos cámaras.`;
    } else if (!el('remote-auto').checked) el('remote-next').textContent = 'Sin consultas periódicas activas.';
  }

  function render(value) {
    if (!job && value.incident) {
      el('remote-lat').value = value.incident.lat;
      el('remote-lon').value = value.incident.lon;
      el('remote-radius').value = value.incident.radius_km;
      el('remote-description').value = value.incident.description;
    }
    job = value;
    updateBudget(value.budget);
    fillCards(value);
    const selected = value.selected?.length || 0;
    el('remote-run').textContent = value.run_id ? `RUN ${value.run_id}` : 'Preparando ejecución…';
    el('remote-reason').textContent = value.selection_reason || 'La IA está consultando el catálogo y seleccionando cámaras.';
    if (value.status === 'failed') {
      el('remote-state').textContent = value.error || 'La ejecución remota no se ha completado. Consulta el RUN indicado.';
    } else if (value.status === 'completed') {
      el('remote-state').textContent = selected
        ? `Consulta terminada · ${selected} cámaras elegidas entre ${value.candidate_count ?? '—'} candidatas.`
        : 'Sin cámaras seleccionadas en ese radio. Esto no significa que no haya tráfico.';
    } else el('remote-state').textContent = selected ? `Analizando ${value.results?.length || 0} de ${selected} cámaras…` : 'Consultando catálogo y seleccionando cámaras en HappyRobot…';
    el('remote-json').textContent = JSON.stringify(value, null, 2);
    refreshClocks();
  }

  async function poll(id) {
    try {
      const value = await request(`/api/remote/job?id=${encodeURIComponent(id)}`);
      render(value);
      if (!['completed', 'failed'].includes(value.status)) {
        pollTimer = setTimeout(() => poll(id), 2500);
        return;
      }
      if (value.status === 'failed') el('remote-auto').checked = false;
      running = false;
      nextRefresh = Date.now() + 180000;
      updateControls();
    } catch (error) {
      running = false;
      el('remote-auto').checked = false;
      el('remote-state').textContent = `No se pudo consultar el resultado: ${error.message}. No se reenvía la petición.`;
      updateControls();
    }
  }

  async function start() {
    if (running || !ready) return;
    running = true;
    job = null;
    cards.clear();
    el('remote-results').replaceChildren();
    el('remote-state').textContent = 'Iniciando consulta remota…';
    el('remote-reason').textContent = '';
    el('remote-run').textContent = '';
    updateControls();
    try {
      const incident = {id: el('remote-incident').value || 'manual', lat: Number(el('remote-lat').value), lon: Number(el('remote-lon').value),
        radius_km: Number(el('remote-radius').value), description: el('remote-description').value};
      const result = await request('/api/remote/start', {incident});
      await poll(result.job_id);
    } catch (error) {
      running = false;
      el('remote-auto').checked = false;
      el('remote-state').textContent = error.message;
      updateControls();
    }
  }

  el('remote-form').addEventListener('submit', event => {event.preventDefault(); start();});
  el('remote-auto').addEventListener('change', () => {nextRefresh = Date.now() + 180000; refreshClocks();});
  el('remote-incident').addEventListener('change', () => {
    const incident = incidents.find(item => item.id === el('remote-incident').value);
    if (!incident) return;
    el('remote-lat').value = incident.lat;
    el('remote-lon').value = incident.lon;
    el('remote-radius').value = incident.radius_km;
    el('remote-description').value = incident.description;
  });
  el('remote-export').addEventListener('click', async () => {
    if (!job) return;
    try {
      const current = await request(`/api/remote/job?id=${encodeURIComponent(job.job_id)}`);
      render(current);
      const data = {...current, exported_at: new Date().toISOString()};
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
      const link = document.createElement('a'); link.href = url; link.download = `trafico-${job.job_id}.json`; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {el('remote-state').textContent = `No se exportó un estado sin revalidar: ${error.message}`;}
  });
  setInterval(() => {
    refreshClocks();
    if (el('remote-auto').checked && !document.hidden && !running && ready && job && Date.now() >= nextRefresh) start();
  }, 1000);
  document.addEventListener('visibilitychange', refreshClocks);
  window.addEventListener('beforeunload', () => clearTimeout(pollTimer));

  request('/api/remote/status').then(status => {
    ready = status.ready;
    el('remote-catalog').textContent = `${status.catalog_count} candidatos · copia de catálogo: ${format(status.catalog_copied_at)} · máximo ${status.max_cameras} por consulta; no es tráfico en directo`;
    updateBudget(status.budget);
    el('remote-state').textContent = ready ? 'Listo. Introduce la ubicación o selecciona un incidente del mapa.' : 'Falta configurar la conexión con HappyRobot en este servidor.';
    updateControls();
    const requested = new URLSearchParams(window.location.search).get('job');
    const restore = requested && /^[a-f0-9-]{36}$/i.test(requested) ? requested : status.active_job_id;
    if (restore) {running = true; updateControls(); poll(restore);}
  }).catch(error => {el('remote-state').textContent = error.message;});
  function loadIncidents() {
    request('/api/remote/incidents').then(value => {
      incidents = value.incidents || [];
      const previous = el('remote-incident').value;
      const manual = document.createElement('option'); manual.value = ''; manual.textContent = 'Ubicación manual';
      el('remote-incident').replaceChildren(manual);
      for (const incident of incidents) {
        const option = document.createElement('option'); option.value = incident.id; option.textContent = incident.description;
        el('remote-incident').append(option);
      }
      if (incidents.some(item => item.id === previous)) el('remote-incident').value = previous;
      el('remote-flare').textContent = value.available ? `${incidents.length} incidentes del mapa · fuente ${value.source_status || 'sin estado'} · contexto de ubicación, no confirmación actual del incidente.` : value.reason;
    }).catch(() => {el('remote-flare').textContent = 'Mapa no disponible. Usa las coordenadas manuales.';});
  }
  loadIncidents();
  setInterval(() => {if (!document.hidden && !running) loadIncidents();}, 60000);
})();
