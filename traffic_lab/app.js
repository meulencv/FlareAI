const $ = id => document.getElementById(id);
const levels = {low: 'DENSIDAD BAJA', moderate: 'DENSIDAD MEDIA', high: 'DENSIDAD ALTA', unknown: 'NO EVALUABLE'};
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

function controls() {
  $('analyze').disabled = busy || cloudBusy;
  $('camera').disabled = busy || cloudBusy;
  $('mode').disabled = busy || cloudBusy;
  $('download').disabled = !observation || busy;
  $('cloud').disabled = !observation || !cloudReady || busy || cloudBusy;
}

function zoneCard(zone) {
  const card = document.createElement('div');
  card.className = 'zone';
  card.innerHTML = '<div class="zone-title"></div><div class="zone-values"><div><strong></strong><small>VEHÍCULOS</small></div><span class="level"></span></div><p class="coverage"></p>';
  card.querySelector('.zone-title').textContent = zone.name;
  card.querySelector('strong').textContent = zone.vehicle_count ?? '—';
  const level = card.querySelector('.level');
  level.classList.add(zone.density);
  level.textContent = levels[zone.density];
  card.querySelector('.coverage').textContent = `Cobertura de cajas: ${zone.box_coverage_pct ?? '—'} % · No es aforo`;
  return card;
}

$('analyze').addEventListener('click', async () => {
  busy = true;
  observation = null;
  controls();
  $('status').textContent = 'Obteniendo imagen y ejecutando el detector local…';
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
    if (!result.zones.length) $('zones').textContent = 'Sin zona de carretera válida. No se emite un nivel de tráfico.';
    $('source-badge').textContent = result.source.mode === 'demo' ? 'MUESTRA HISTÓRICA' : result.freshness === 'recent' ? 'IMAGEN RECIENTE DEL PROVEEDOR' : 'FECHA ANTIGUA / NO VERIFICADA';
    $('updated').textContent = result.source.source_updated_at ? new Date(result.source.source_updated_at).toLocaleString('es-ES') : 'No verificada';
    $('quality').textContent = result.quality.status === 'unusable' ? 'No evaluable' : 'Controles básicos superados · revisar encuadre';
    $('latency').textContent = `${result.elapsed_ms} ms · CPU / ONNX`;
    $('json').textContent = JSON.stringify(result, null, 2);
    $('warnings').replaceChildren(...result.warnings.map(text => {const li = document.createElement('li'); li.textContent = text; return li;}));
    $('status').textContent = `Análisis terminado · ${result.source.name} · ${result.source.sha256.slice(0, 12)}…`;
    $('cloud-status').textContent = cloudReady ? 'Listo para ejecutar el workflow remoto con esta evidencia.' : 'Modo local. Arranca el servidor con HAPPYROBOT_API_KEY y despliega el workflow.';
  } catch (error) {
    $('status').textContent = `No se pudo analizar: ${error.message}. No se ha emitido una lectura nueva.`;
    $('image').hidden = true;
    $('empty').hidden = false;
    $('zones').textContent = 'Sin datos vigentes.';
    $('updated').textContent = '—';
    $('quality').textContent = '—';
    $('source-badge').textContent = 'ERROR DE ADQUISICIÓN';
    $('json').textContent = '{}';
    $('warnings').replaceChildren();
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
    $('image').hidden = true;
    $('empty').hidden = false;
    $('zones').textContent = 'Pulsa Analizar imagen para medir la nueva selección.';
    $('source-badge').textContent = 'SIN ANALIZAR';
    $('updated').textContent = '—';
    $('quality').textContent = '—';
    $('json').textContent = '{}';
    $('warnings').replaceChildren();
    $('cloud-summary').textContent = 'Aún no se ha ejecutado para esta selección.';
    $('cloud-check').textContent = '';
    $('run-id').textContent = '';
    $('cloud-status').textContent = 'Primero analiza la nueva selección.';
    $('status').textContent = 'Selección cambiada. Pulsa Analizar imagen.';
    controls();
  });
}

api('/api/cameras').then(data => {
  cloudReady = data.cloud_ready;
  for (const camera of data.cameras) {
    const option = document.createElement('option');
    option.value = camera.id;
    option.textContent = camera.name;
    $('camera').append(option);
  }
  $('status').textContent = 'Listo. El modo muestra funciona sin conexión tras preparar el modelo.';
  controls();
}).catch(error => {$('status').textContent = error.message;});
