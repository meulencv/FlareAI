export function notificationBatch(payload, session, sequence, now = Date.now() / 1000) {
  const reset = session !== payload.session_id;
  return { session: payload.session_id, sequence: payload.sequence,
    events: reset ? [] : (payload.events || []).filter(e => e.sequence > sequence && e.expires_at > now && ['alert', 'cancel'].includes(e.kind)) };
}

export function createAlertReceiver({ document, window, fetch }) {
  const $ = id => document.getElementById(id);
  let audio = null, oscillator = null, soundGain = null, wakeLock = null, session = null, sequence = 0;
  let armed = false, loading = false, current = null, queue = [];
  const accessCode = new URLSearchParams(window.location?.hash?.slice(1) || '').get('code') || '';
  if (window.location?.hash) window.history.replaceState(null, '', window.location.pathname);
  function stopSound() {
    if (oscillator) { oscillator.onended = null; try { oscillator.stop(); } catch {} oscillator.disconnect(); oscillator = null; }
    soundGain?.disconnect(); soundGain = null;
    window.navigator.vibrate?.(0);
    document.body.dataset.sounding = 'false';
  }
  function audioStatus(message) {
    const ready = audio?.state === 'running';
    const text = message || (ready
      ? 'Audio habilitado · si no lo oyes, sube el volumen multimedia y comprueba la salida de audio.'
      : 'Audio suspendido o no habilitado. Pulsa activar sonido.');
    $('sound-status').textContent = text;
    $('alert-sound-status').textContent = text;
    $('retry-alert-sound').hidden = ready;
    $('activate-alerts').textContent = ready ? 'Probar sonido fuerte' : 'Activar recepción y sonido';
  }
  function sound(duration = 8) {
    stopSound(); audioStatus();
    if (!audio || audio.state !== 'running') return;
    const gain = audio.createGain(), start = audio.currentTime;
    soundGain = gain;
    oscillator = audio.createOscillator(); oscillator.type = 'sine';
    oscillator.connect(gain); gain.connect(audio.destination); gain.gain.setValueAtTime(0, start);
    for (let i = 0; i < duration / .4; i++) {
      const at = start + i * .4;
      oscillator.frequency.setValueAtTime(i % 2 ? 1000 : 800, at);
      gain.gain.setValueAtTime(0, at); gain.gain.linearRampToValueAtTime(.85, at + .02);
      gain.gain.setValueAtTime(.85, at + .25); gain.gain.linearRampToValueAtTime(0, at + .3);
    }
    oscillator.onended = stopSound;
    oscillator.start(start); oscillator.stop(start + duration);
    document.body.dataset.sounding = 'true'; window.navigator.vibrate?.([250, 150, 250, 150, 250]);
  }
  function showNext() {
    queue = queue.filter(e => e.expires_at > Date.now() / 1000);
    if (current || !queue.length) return;
    current = queue.shift();
    $('alert-message').textContent = current.message;
    $('alert-time').textContent = new Date(current.at * 1000).toLocaleString('es-ES') + ' · ' + (current.source === 'firefighter_request' ? 'Solicitado por bomberos' : 'Decisión del director');
    $('received-alert').hidden = false;
    $('ack-alert').focus(); sound();
  }
  function dismiss() {
    stopSound(); current = null; $('received-alert').hidden = true;
    showNext();
  }
  async function holdScreen() {
    if (armed && !document.hidden && !wakeLock && window.navigator.wakeLock) {
      try { wakeLock = await window.navigator.wakeLock.request('screen'); wakeLock.addEventListener('release', () => { wakeLock = null; }); } catch {}
    }
  }
  async function poll(baseline = false) {
    if (loading || !armed) return;
    loading = true;
    try {
      const response = await fetch('/112/api/alerts' + (baseline ? '' : `?after=${sequence}`), { cache: 'no-store', signal: globalThis.AbortSignal.timeout(8000) });
      if (response.status === 403) {
        armed = false; stopSound(); queue = []; current = null; $('received-alert').hidden = true;
        document.body.dataset.armed = 'false'; $('activate-alerts').disabled = false;
        $('receiver-status').textContent = 'La sesión ha cambiado. Pulsa activar para vincular este móvil.';
        return;
      }
      if (!response.ok) throw new Error('Receptor temporalmente sin conexión');
      const payload = await response.json(), batch = notificationBatch(payload, session, sequence);
      if (session !== null && session !== batch.session) { stopSound(); current = null; queue = []; $('received-alert').hidden = true; }
      session = batch.session; sequence = batch.sequence;
      for (const event of batch.events) {
        if (event.kind === 'cancel') {
          queue = queue.filter(e => e.incident_id !== event.incident_id);
          if (current?.incident_id === event.incident_id) { stopSound(); current = null; $('received-alert').hidden = true; }
        } else queue.push(event);
      }
      $('receiver-status').textContent = 'Receptor conectado · esperando nuevas alertas de demostración';
      showNext();
    } catch {
      $('receiver-status').textContent = 'Sin conexión con el servidor. Reintentando; no se garantiza recepción.';
    } finally { loading = false; }
  }
  async function activate() {
    $('activate-alerts').disabled = true; $('retry-alert-sound').disabled = true;
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) throw new Error('Este navegador no permite el sonido de la demo');
      try { if (window.navigator.audioSession) window.navigator.audioSession.type = 'playback'; } catch {}
      if (!audio || audio.state === 'closed') {
        audio = new Audio();
        audio.onstatechange = () => { if (audio.state !== 'running') stopSound(); audioStatus(); };
      }
      await audio.resume();
      if (audio.state !== 'running') throw new Error('No se pudo habilitar audio. Toca activar de nuevo.');
      sound(current ? 8 : .8);
      if (!armed) {
        const response = await fetch('/112/api/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ access_code: accessCode }) });
        if (!response.ok) throw new Error('No se pudo vincular el receptor');
        armed = true; document.body.dataset.armed = 'true';
        await poll(true);
      }
      await holdScreen();
    } catch (error) {
      audioStatus(error.message);
    } finally { $('activate-alerts').disabled = false; $('retry-alert-sound').disabled = false; }
  }
  $('activate-alerts').onclick = activate;
  $('retry-alert-sound').onclick = activate;
  $('ack-alert').onclick = dismiss;
  document.addEventListener('visibilitychange', () => { if (!document.hidden) { audioStatus(); void poll(); void holdScreen(); } });
  window.addEventListener('pagehide', () => { stopSound(); void wakeLock?.release(); });
  const timer = window.setInterval(() => void poll(), 1500);
  return { stop() { window.clearInterval(timer); stopSound(); void wakeLock?.release(); }, poll };
}

if (typeof document !== 'undefined') createAlertReceiver({ document, window, fetch });
