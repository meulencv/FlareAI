export function preferredSpeaker(devices) {
  return devices.find(device => device.kind === 'audiooutput' && device.deviceId && !['default', 'communications'].includes(device.deviceId)
    && /speaker|altavoz|hands.?free|manos libres|haut.?parleur/i.test(device.label)
    && !/head|earpiece|receiver|auricular|bluetooth/i.test(device.label)) || null;
}

export function createSpeakerOutput({ window, document, onStatus, onDevices }) {
  let context = null, destination = null, relay = null, generation = 0;
  const tracks = new Map();
  async function prepare() {
    const Audio = window.AudioContext || window.webkitAudioContext;
    if (!Audio) return;
    if (!context) {
      context = new Audio(); destination = context.createMediaStreamDestination();
      relay = document.createElement('audio'); relay.autoplay = true; relay.setAttribute('playsinline', '');
      relay.dataset.happyrobotAudio = 'relay'; relay.hidden = true; relay.volume = 1;
      relay.srcObject = destination.stream; document.body.append(relay);
    }
    const current = context, player = relay;
    await current.resume(); await player.play();
    if (current !== context) return;
    for (const [track, entry] of tracks) {
      if (!entry.source) {
        entry.source = current.createMediaStreamSource(new window.MediaStream([track.mediaStreamTrack]));
        entry.source.connect(destination);
      }
      entry.element.muted = true;
    }
  }
  function fallback() {
    if (relay) relay.pause();
    for (const entry of tracks.values()) { entry.element.muted = false; void entry.element.play().catch(() => {}); }
  }
  function attach(track) {
    if (tracks.has(track)) return;
    const element = track.attach(); element.dataset.happyrobotAudio = 'source'; element.hidden = true; element.volume = 1;
    element.setAttribute('playsinline', ''); document.body.append(element);
    tracks.set(track, { element, source: null });
    const token = generation;
    void prepare().catch(() => { if (token === generation) { fallback(); onStatus('Pulsa Altavoz para habilitar la reproducción de voz.', false); } });
  }
  function detach(track) {
    const entry = tracks.get(track);
    if (!entry) return;
    entry.source?.disconnect(); track.detach(entry.element); entry.element.remove(); tracks.delete(track);
  }
  async function select(deviceId) {
    const token = generation;
    await prepare();
    if (token !== generation) return;
    if (!relay?.setSinkId) { onStatus('El navegador no permite seleccionar altavoz. Usa la salida de audio del móvil y elige Altavoz, sin desconectar el micrófono.', false); return; }
    await relay.setSinkId(deviceId);
    if (token !== generation) return;
    onStatus(deviceId && deviceId !== 'default' ? 'Salida seleccionada para la voz. Ajusta el volumen multimedia del móvil.' : 'Salida predeterminada del sistema; el navegador no confirma qué altavoz físico usa.', Boolean(deviceId && deviceId !== 'default'));
  }
  async function activate(ask = false) {
    const token = generation;
    try {
      await prepare();
      if (token !== generation) return;
      if (ask && window.navigator.mediaDevices.selectAudioOutput) {
        const selected = await window.navigator.mediaDevices.selectAudioOutput();
        if (token !== generation) return;
        await select(selected.deviceId);
      } else {
        const devices = (await window.navigator.mediaDevices.enumerateDevices()).filter(device => device.kind === 'audiooutput');
        if (token !== generation) return;
        onDevices(devices);
        const speaker = preferredSpeaker(devices);
        if (speaker && relay?.setSinkId) await select(speaker.deviceId);
        else onStatus('Manos libres solicitado. Si oyes el auricular, elige Altavoz en el control de audio del móvil; este navegador no expone una salida seleccionable.', false);
      }
    } catch {
      if (token !== generation) return;
      if (context?.state !== 'running') fallback();
      onStatus('No se pudo cambiar la salida. La llamada continúa; elige Altavoz desde los controles de audio del móvil.', false);
    }
  }
  function close() {
    generation++;
    for (const track of [...tracks.keys()]) detach(track);
    if (relay) { relay.pause(); relay.srcObject = null; relay.remove(); relay = null; }
    destination?.stream.getTracks().forEach(track => track.stop()); destination = null;
    if (context) { void context.close().catch(() => {}); context = null; }
  }
  return { prepare, attach, detach, activate, select, close };
}
