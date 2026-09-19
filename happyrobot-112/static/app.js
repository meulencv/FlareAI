(() => {
  "use strict";

  const { Room, RoomEvent, Track } = window.LivekitClient || {};
  const button = document.querySelector("#call-button");
  const buttonLabel = document.querySelector("#button-label");
  const status = document.querySelector("#status");
  const statusDot = document.querySelector("#status-dot");
  const timer = document.querySelector("#timer");
  const syncState = document.querySelector("#sync-state");
  const fields = ["ubicacion", "emergencia", "personas", "riesgos", "contacto"];

  let room = null;
  let runId = null;
  let pollHandle = null;
  let timerHandle = null;
  let startedAt = 0;
  let polling = false;
  let stopping = false;

  function setStatus(text, live = false) {
    status.textContent = text;
    statusDot.classList.toggle("live", live);
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
      const response = await fetch(`/api/brief?run_id=${encodeURIComponent(targetRunId)}`, {
        cache: "no-store",
      });
      if (!response.ok) throw new Error("No se pudo actualizar la ficha");
      const data = await response.json();
      if (!final && targetRunId !== runId) return;
      updateSummary(data.summary);
      syncState.textContent = final
        ? "Ficha final"
        : (data.status === "waiting" ? "Escuchando…" : "Actualizada");
      syncState.classList.toggle("live", !final);
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

  async function startCall() {
    if (!Room) throw new Error("No se ha podido cargar el módulo de voz");
    button.disabled = true;
    setStatus("Preparando…");
    syncState.textContent = "Conectando";

    const response = await fetch("/api/call", { method: "POST" });
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

    buttonLabel.textContent = "Terminar llamada";
    button.classList.add("active");
    button.disabled = false;
    setStatus("En llamada", true);
    syncState.textContent = "Escuchando…";
    syncState.classList.add("live");
    startTimer();
    beginPolling();
  }

  async function stopCall(finalStatus = "Simulación terminada") {
    if (stopping) return;
    stopping = true;
    const finishedRun = runId;
    window.clearInterval(pollHandle);
    window.clearInterval(timerHandle);
    pollHandle = null;
    timerHandle = null;

    const activeRoom = room;
    room = null;
    if (activeRoom) activeRoom.disconnect();
    document.querySelectorAll("[data-happyrobot-audio]").forEach((node) => node.remove());

    buttonLabel.textContent = "Iniciar otra simulación";
    button.classList.remove("active");
    button.disabled = false;
    setStatus(finalStatus);
    syncState.textContent = "Ficha final";
    syncState.classList.remove("live");
    runId = null;
    stopping = false;

    if (finishedRun) {
      window.setTimeout(() => void refreshBrief(finishedRun, true), 1200);
    }
  }

  button.addEventListener("click", async () => {
    if (room) {
      await stopCall();
      return;
    }
    try {
      await startCall();
    } catch (error) {
      window.clearInterval(pollHandle);
      window.clearInterval(timerHandle);
      pollHandle = null;
      timerHandle = null;
      stopping = true;
      const failedRoom = room;
      room = null;
      runId = null;
      if (failedRoom) failedRoom.disconnect();
      document.querySelectorAll("[data-happyrobot-audio]").forEach((node) => node.remove());
      stopping = false;
      button.disabled = false;
      button.classList.remove("active");
      buttonLabel.textContent = "Reintentar";
      setStatus(error instanceof Error ? error.message : "Error al iniciar");
      syncState.textContent = "Sin conexión";
      syncState.classList.remove("live");
    }
  });

  updateSummary({});
})();
