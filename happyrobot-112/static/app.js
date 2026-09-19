(() => {
  "use strict";

  const { Room, RoomEvent, Track } = window.LivekitClient || {};
  const integrated = window.location.pathname.startsWith('/112/');
  const apiBase = integrated ? '/112' : '';
  const post = (path, body = {}) => fetch(`${apiBase}/api/${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const dialerScreen = document.querySelector("#dialer-screen");
  const callScreen = document.querySelector("#call-screen");
  const dialNumberElement = document.querySelector("#dial-number");
  const dialStatus = document.querySelector("#dial-status");
  const callButton = document.querySelector("#call-button");
  const deleteButton = document.querySelector("#delete-button");
  const hangupButton = document.querySelector("#hangup-button");
  const status = document.querySelector("#status");
  const statusDot = document.querySelector("#status-dot");
  const timer = document.querySelector("#timer");
  const syncState = document.querySelector("#sync-state");
  const detailsToggle = document.querySelector("#details-toggle");
  const detailsPanel = document.querySelector("#brief-panel");
  const detailsClose = document.querySelector("#details-close");
  const sheetScrim = document.querySelector("#sheet-scrim");
  const muteButton = document.querySelector("#mute-button");
  const muteIcon = document.querySelector("#mute-icon");
  const muteLabel = document.querySelector("#mute-label");
  const fields = ["ubicacion", "emergencia", "personas", "riesgos", "contacto"];

  let dialNumber = "";
  let room = null;
  let runId = null;
  let pollHandle = null;
  let timerHandle = null;
  let startedAt = 0;
  let polling = false;
  let stopping = false;
  let muted = false;

  function updateClock() {
    document.querySelector("#clock").textContent = new Intl.DateTimeFormat("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date());
  }

  function renderNumber() {
    if (dialNumber) {
      dialNumberElement.textContent = dialNumber;
      deleteButton.hidden = false;
    } else {
      dialNumberElement.innerHTML = '<span class="placeholder">Introduce un número</span>';
      deleteButton.hidden = true;
    }
    if (dialNumber === "112") {
      dialStatus.textContent = "Pulsa llamar para hablar con el operador";
    } else if (dialNumber) {
      dialStatus.textContent = "Esta demo solo atiende el 112";
    } else {
      dialStatus.textContent = "Marca 112 para iniciar la simulación";
    }
    dialStatus.classList.remove("error");
  }

  function appendDigit(digit) {
    if (dialNumber.length >= 12 || room) return;
    dialNumber += digit;
    renderNumber();
  }

  function removeDigit() {
    dialNumber = dialNumber.slice(0, -1);
    renderNumber();
  }

  function setStatus(text, live = false) {
    status.textContent = text;
    statusDot.classList.toggle("live", live);
  }

  function setCallView(active) {
    dialerScreen.hidden = active;
    callScreen.hidden = !active;
  }

  function setMuted(next) {
    muted = next;
    muteButton.setAttribute("aria-pressed", String(muted));
    muteIcon.setAttribute("href", muted ? "#i-mic-off" : "#i-mic");
    muteLabel.textContent = muted ? "Silenciado" : "Silenciar";
  }

  async function toggleMute() {
    if (!room) return;
    const next = !muted;
    setMuted(next);
    try {
      await room.localParticipant.setMicrophoneEnabled(!next);
    } catch (error) {
      setMuted(!next);
    }
  }

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
    const rest = Math.floor(seconds % 60).toString().padStart(2, "0");
    return `${minutes}:${rest}`;
  }

  function startTimer() {
    startedAt = Date.now();
    timer.textContent = "00:00";
    timerHandle = window.setInterval(() => {
      timer.textContent = formatTime((Date.now() - startedAt) / 1000);
    }, 1000);
  }

  function updateSummary(summary) {
    for (const field of fields) {
      const element = document.querySelector(`#summary-${field}`);
      const value = String(summary?.[field] || "pendiente").trim();
      const next = value.charAt(0).toUpperCase() + value.slice(1);
      if (element.textContent !== next) {
        element.textContent = next;
        element.classList.remove("updated");
        void element.offsetWidth;
        element.classList.add("updated");
      }
      element.classList.toggle("pending", value.toLocaleLowerCase("es") === "pendiente");
    }
  }

  async function refreshBrief(targetRunId = runId, final = false) {
    if (!targetRunId || polling) return;
    polling = true;
    try {
      const response = await fetch(`${apiBase}/api/brief?run_id=${encodeURIComponent(targetRunId)}`, {
        cache: "no-store",
      });
      if (!response.ok) throw new Error("No se pudo actualizar la ficha");
      const data = await response.json();
      if (!final && targetRunId !== runId) return;
      updateSummary(data.summary);
      syncState.textContent = data.map_status === 'located' ? 'Aviso enviado al mapa · demo'
        : data.map_status === 'needs_location' ? 'Indica municipio y ubicación más precisa'
        : final ? "Ficha final" : (data.status === "waiting" ? "Esperando datos…" : "Actualizando en directo");
    } catch (error) {
      if (final || targetRunId === runId) syncState.textContent = "Reintentando…";
    } finally {
      polling = false;
    }
  }

  function beginPolling() {
    window.clearInterval(pollHandle);
    pollHandle = window.setInterval(refreshBrief, 900);
    void refreshBrief();
  }

  function toggleDetails(force) {
    const open = typeof force === "boolean" ? force : detailsPanel.hidden;
    detailsPanel.hidden = !open;
    sheetScrim.hidden = !open;
    detailsToggle.setAttribute("aria-expanded", String(open));
  }

  async function startCall() {
    if (dialNumber !== "112") {
      dialStatus.textContent = dialNumber ? "Esta demo solo permite llamar al 112" : "Escribe 112 primero";
      dialStatus.classList.add("error");
      return;
    }
    if (!Room) throw new Error("No se ha podido cargar el módulo de voz");

    callButton.disabled = true;
    setCallView(true);
    setMuted(false);
    setStatus("Llamando…");
    syncState.textContent = "Conectando con HappyRobot";
    timer.textContent = "00:00";

    const response = await post('call');
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "No se pudo iniciar la llamada");

    runId = payload.run_id;
    const currentRoom = new Room({ adaptiveStream: true, dynacast: true });
    room = currentRoom;
    currentRoom.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind !== Track.Kind.Audio) return;
      const audio = track.attach();
      audio.dataset.happyrobotAudio = "true";
      audio.hidden = true;
      document.body.append(audio);
    });
    currentRoom.on(RoomEvent.Disconnected, () => {
      if (!stopping) void stopCall("Llamada finalizada");
    });

    await currentRoom.connect(payload.url, payload.token);
    await currentRoom.localParticipant.setMicrophoneEnabled(true);
    if (room !== currentRoom || runId !== payload.run_id) {
      throw new Error("La llamada se ha desconectado");
    }

    callButton.disabled = false;
    setStatus("En llamada", true);
    syncState.textContent = "Recopilando información";
    startTimer();
    beginPolling();
  }

  async function stopCall(finalStatus = "Llamada finalizada") {
    if (stopping) return;
    stopping = true;
    const finishedRun = runId;
    window.clearInterval(pollHandle);
    window.clearInterval(timerHandle);
    pollHandle = null;
    timerHandle = null;

    const activeRoom = room;
    room = null;
    runId = null;
    if (activeRoom) activeRoom.disconnect();
    document.querySelectorAll("[data-happyrobot-audio]").forEach((node) => node.remove());

    callButton.disabled = false;
    setMuted(false);
    setCallView(false);
    dialStatus.textContent = finalStatus;
    dialStatus.classList.remove("error");
    syncState.textContent = "Ficha final";
    stopping = false;

    if (finishedRun) {
      if (integrated) void post('stop', { run_id: finishedRun });
      window.setTimeout(() => void refreshBrief(finishedRun, true), 1200);
    }
  }

  async function handleStart() {
    try {
      await startCall();
    } catch (error) {
      window.clearInterval(pollHandle);
      window.clearInterval(timerHandle);
      pollHandle = null;
      timerHandle = null;
      stopping = true;
      const failedRoom = room;
      if (integrated && runId) void post('stop', { run_id: runId });
      room = null;
      runId = null;
      if (failedRoom) failedRoom.disconnect();
      document.querySelectorAll("[data-happyrobot-audio]").forEach((node) => node.remove());
      stopping = false;
      callButton.disabled = false;
      setCallView(false);
      dialStatus.textContent = error instanceof Error ? error.message : "Error al iniciar";
      dialStatus.classList.add("error");
      syncState.textContent = "Sin conexión";
    }
  }

  document.querySelectorAll("[data-digit]").forEach((button) => {
    button.addEventListener("click", () => appendDigit(button.dataset.digit));
  });
  deleteButton.addEventListener("click", removeDigit);
  callButton.addEventListener("click", handleStart);
  hangupButton.addEventListener("click", () => void stopCall());
  muteButton.addEventListener("click", () => void toggleMute());
  detailsToggle.addEventListener("click", () => toggleDetails());
  detailsClose.addEventListener("click", () => toggleDetails(false));
  sheetScrim.addEventListener("click", () => toggleDetails(false));

  document.addEventListener("keydown", (event) => {
    if (event.target instanceof HTMLButtonElement && (event.key === " " || event.key === "Enter")) return;
    if (/^[0-9*#]$/.test(event.key)) appendDigit(event.key);
    if (event.key === "Backspace") removeDigit();
    if (event.key === "Enter" && !room) void handleStart();
    if (event.key === "Escape" && !detailsPanel.hidden) toggleDetails(false);
  });

  async function prepareDemo() {
    if (!integrated) return;
    callButton.disabled = true;
    if (window.location.hash) window.history.replaceState(null, '', window.location.pathname);
    try {
      const response = await fetch(`${apiBase}/api/status`);
      const result = await response.json();
      if (!result.configured) throw new Error('HappyRobot no está configurado en el ordenador.');
      if (!result.browser_ready) {
        const session = await post('session');
        if (!session.ok) throw new Error('No se pudo preparar la demo. Recarga para reintentar.');
      }
      callButton.disabled = false;
      dialStatus.textContent = 'Marca 112. El mapa se actualizará automáticamente.';
    } catch (error) { dialStatus.textContent = error.message; }
  }
  updateClock();
  window.setInterval(updateClock, 30000);
  renderNumber();
  updateSummary({});
  void prepareDemo();
})();
