const $ = id => document.getElementById(id);
const levels = {low: 'DENSIDAD BAJA', moderate: 'DENSIDAD MEDIA', high: 'DENSIDAD ALTA', unknown: 'NO CONCLUYENTE'};
let observation = null;
let cloudReady = false;
let busy = false;
let cloudBusy = false;

async function api(path, body) {
  const response = await fetch(path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || `HTTP ${response.status}`);
  return value;
}

function providerAge() {
  const timestamp = observation?.evidence.source.source_updated_at;
  return typeof timestamp === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/i.test(timestamp)
    ? (Date.now() - Date.parse(timestamp)) / 1000 : NaN;
}

function controls() {
  $('analyze').disabled = busy || cloudBusy;
  $('camera').disabled = busy || cloudBusy;
  $('mode').disabled = busy || cloudBusy;
  $('download').disabled = !observation || busy;
  const evidence = observation?.evidence;
  const age = providerAge();
  const eligible = evidence?.calibration?.status === 'aligned' && evidence.zones.some(zone => zone.vehicle_count > 0)
    && (evidence.source.mode === 'demo' || (Number.isFinite(age) && age >= -60 && age <= 600));
  $('cloud').disabled = !eligible || !cloudReady || busy || cloudBusy;
}

function formatTime(value) {
  return typeof value === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/i.test(value) && Number.isFinite(Date.parse(value))
    ? new Date(value).toLocaleString('es-ES', {timeZone: 'Europe/Madrid', timeZoneName: 'short'}) : 'No verificada';
}

function updateTime() {
  if (!observation) return;
  const result = observation.evidence;
  const age = providerAge();
  result.freshness = !Number.isFinite(age) || age < -60 ? 'unverified' : age > 600 ? 'stale' : 'recent';
  $('updated').textContent = formatTime(result.source.source_updated_at);
  $('analyzed').textContent = formatTime(result.analyzed_at);
  $('captured').textContent = result.capture_time_verified ? formatTime(result.captured_at) : 'NO VERIFICADA · no equivale a la fecha HTTP';
  $('age').textContent = Number.isFinite(age) && age >= -60
    ? `${Math.floor(Math.max(0, age) / 60)} min ${Math.floor(Math.max(0, age) % 60)} s${age > 600 ? ' · CADUCADA' : ' · captura aún no verificada'}` : 'Desconocida o reloj incoherente';
  $('source-badge').textContent = result.source.mode === 'demo' ? 'MUESTRA HISTÓRICA'
    : age > 600 ? 'ACTUALIZACIÓN > 10 MIN' : 'HORA DE CAPTURA NO VERIFICADA';
  controls();
}

function resetReadout() {
  $('image').hidden = true;
  $('empty').hidden = false;
  for (const id of ['updated', 'analyzed', 'age', 'scene-count', 'quality']) $(id).textContent = '—';
  $('captured').textContent = 'No verificada';
  $('calibration-message').textContent = 'Encuadre pendiente de comprobar.';
  $('source-badge').textContent = 'SIN ANALIZAR';
  $('json').textContent = '{}';
  $('warnings').replaceChildren();
}

function zoneCard(zone) {
  const card = document.createElement('div');
  card.className = 'zone';
  card.innerHTML = '<div class="zone-title"></div><div class="zone-values"><div><strong></strong><small>DETECCIONES</small></div><span class="level"></span></div><p class="coverage"></p>';
  card.querySelector('.zone-title').textContent = zone.name;
  card.querySelector('strong').textContent = zone.vehicle_count ?? '—';
  const level = card.querySelector('.level');
  level.classList.add(zone.density);
  level.textContent = zone.vehicle_count === null ? 'ZONA DESACTIVADA' : levels[zone.density];
  card.querySelector('.coverage').textContent = zone.vehicle_count === null ? 'El encuadre no coincide con la referencia.'
    : zone.vehicle_count === 0 ? 'Sin detecciones; no demuestra ausencia de coches.'
      : `Cobertura de cajas: ${zone.box_coverage_pct} % · No es aforo`;
  return card;
}

$('analyze').addEventListener('click', async () => {
  busy = true;
  observation = null;
  resetReadout();
  controls();
  $('status').textContent = 'Comprobando encuadre y buscando vehículos a varias escalas…';
  $('zones').textContent = 'Analizando…';
  $('cloud-summary').textContent = 'Aún no se ha ejecutado para esta imagen.';
  $('cloud-check').textContent = '';
  $('run-id').textContent = '';
  $('cloud-status').textContent = 'Esperando análisis local.';
  try {
    const data = await api('/api/analyze', {camera_id: $('camera').value, mode: $('mode').value});
    observation = data;
    const result = data.evidence;
    $('image').src = data.image;
    $('image').hidden = false;
    $('empty').hidden = true;
    $('zones').replaceChildren(...result.zones.map(zoneCard));
    if (!result.zones.length) $('zones').textContent = 'Sin zona de carretera configurada.';
    const aligned = result.calibration?.status === 'aligned';
    $('calibration-message').textContent = aligned
      ? 'Encuadre coincidente con la referencia. Las zonas están activas; el conteo puede omitir vehículos.'
      : 'ENCUADRE NO VALIDADO: no se dibujan ni utilizan las zonas antiguas. Solo se muestran detecciones de toda la imagen.';
    $('scene-count').textContent = result.scene?.vehicle_count ?? '—';
    $('quality').textContent = result.quality.status === 'unusable' ? 'Imagen no evaluable'
      : aligned ? 'Calidad básica superada · encuadre coincidente' : 'Calidad básica superada · ZONAS NO VÁLIDAS';
    $('latency').textContent = `${result.elapsed_ms} ms · imagen completa + teselas`;
    $('json').textContent = JSON.stringify(result, null, 2);
    $('warnings').replaceChildren(...result.warnings.map(text => {const li = document.createElement('li'); li.textContent = text; return li;}));
    $('status').textContent = `${aligned ? 'Análisis terminado' : 'Análisis parcial: requiere calibración'} · ${result.source.name} · ${result.source.sha256.slice(0, 12)}…`;
    $('cloud-status').textContent = !aligned ? 'Resumen por carretera bloqueado: el encuadre no está validado.'
      : cloudReady ? 'El resumen usa estas detecciones, no vuelve a analizar la imagen.' : 'Modo local. HappyRobot no está configurado en este proceso.';
    updateTime();
  } catch (error) {
    resetReadout();
    $('status').textContent = `No se pudo analizar: ${error.message}. No se ha emitido una lectura nueva.`;
    $('zones').textContent = 'Sin datos vigentes.';
    $('source-badge').textContent = 'ERROR DE ADQUISICIÓN';
  } finally {busy = false; controls();}
});

$('download').addEventListener('click', () => {
  if (!observation) return;
  const url = URL.createObjectURL(new Blob([JSON.stringify(observation.evidence, null, 2)], {type: 'application/json'}));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `traffic-${observation.evidence.source.camera_id}.json`;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

function findResult(value) {
  if (!value || typeof value !== 'object') return null;
  if (typeof value.result_json === 'string') return JSON.parse(value.result_json);
  for (const child of Object.values(value)) {
    const result = findResult(child);
    if (result) return result;
  }
  return null;
}

$('cloud').addEventListener('click', async () => {
  cloudBusy = true;
  controls();
  $('cloud-status').textContent = 'Iniciando ejecución en HappyRobot…';
  try {
    const started = await api('/api/workflow', {observation_id: observation.observation_id});
    $('run-id').textContent = `RUN ${started.run_id}`;
    for (let attempt = 0; attempt < 40; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      const run = await api(`/api/run?id=${encodeURIComponent(started.run_id)}`);
      if (run.status === 'completed') {
        const result = findResult(run.output);
        if (!result) throw new Error('La ejecución terminó sin el contrato de salida esperado');
        $('cloud-summary').textContent = result.operator_summary;
        $('cloud-check').textContent = result.operator_check;
        $('cloud-status').textContent = `Completado en HappyRobot · ${levels[result.density]} · Revisión humana obligatoria`;
        return;
      }
      if (run.status === 'failed') throw new Error('La ejecución ha fallado en HappyRobot; consulta el run indicado');
      $('cloud-status').textContent = `Workflow en curso · ${run.nodes?.filter(n => ['completed', 'succeeded'].includes(n.status)).length ?? 0} pasos completados`;
    }
    $('cloud-status').textContent = 'La ejecución sigue pendiente. Consulta el run en HappyRobot; no se reenvía automáticamente.';
  } catch (error) {$('cloud-status').textContent = error.message;}
  finally {cloudBusy = false; controls();}
});

for (const id of ['camera', 'mode']) {
  $(id).addEventListener('change', () => {
    observation = null;
    resetReadout();
    $('zones').textContent = 'Pulsa Analizar imagen para medir la nueva selección.';
    $('cloud-summary').textContent = 'Aún no se ha ejecutado para esta selección.';
    $('cloud-check').textContent = '';
    $('run-id').textContent = '';
    $('cloud-status').textContent = 'Primero analiza la nueva selección.';
    $('status').textContent = 'Selección cambiada. Pulsa Analizar imagen.';
    controls();
  });
}

setInterval(updateTime, 1000);
api('/api/cameras').then(data => {
  cloudReady = data.cloud_ready;
  for (const camera of data.cameras) {
    const option = document.createElement('option');
    option.value = camera.id;
    option.textContent = camera.name;
    $('camera').append(option);
  }
  $('status').textContent = 'YOLO local · encuadre verificado antes de contar por carretera · detecciones parciales, no aforo.';
  controls();
}).catch(error => {$('status').textContent = error.message;});
