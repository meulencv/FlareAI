const form = document.querySelector("#sms-form");
const send = document.querySelector("#send");
const message = document.querySelector("#message");
const connection = document.querySelector("#connection");
const refresh = document.querySelector("#refresh");
let config;
let runId;
let busy = false;
let generation = 0;

function status(title, detail, state = "") {
  document.querySelector("#status-title").textContent = title;
  document.querySelector("#status-message").textContent = detail;
  document.querySelector(".status-card").dataset.state = state;
}

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, signal: window.AbortSignal.timeout(45000) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Error HTTP ${response.status}`);
  return data;
}

function updateButton() {
  send.disabled = !config?.ready || busy || !document.querySelector("#confirmed").checked;
}

function updateCount() {
  document.querySelector("#count").textContent = `${message.value.length} / 480`;
}

async function checkRun(id, expectedGeneration) {
  const data = await api(`/api/runs/${encodeURIComponent(id)}`);
  if (expectedGeneration !== generation) return true;
  if (["completed", "succeeded"].includes(data.status)) {
    status("Workflow completado.", "HappyRobot ha completado la ejecución. Comprueba la recepción en tu móvil: esto no es una confirmación de entrega.", "success");
    return true;
  }
  if (["failed", "canceled", "skipped"].includes(data.status)) {
    status("La ejecución no se completó.", data.error || `Estado: ${data.status}. Revisa el nodo Send SMS en HappyRobot antes de repetir el envío.`, "error");
    return true;
  }
  status("Solicitud aceptada.", `Estado en HappyRobot: ${data.status}. Esperando el resultado del workflow.`);
  return false;
}

async function pollRun(id, expectedGeneration) {
  try {
    for (let attempt = 0; attempt < 20; attempt++) {
      if (expectedGeneration !== generation || await checkRun(id, expectedGeneration)) return;
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    if (expectedGeneration === generation) status("Sigue en proceso.", "Puedes consultar el estado sin volver a enviar el SMS.");
  } catch (error) {
    if (expectedGeneration === generation) status("Estado pendiente de confirmar.", error.message, "error");
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (busy || !config?.ready || !form.reportValidity()) return;
  busy = true;
  generation++;
  const current = generation;
  runId = null;
  refresh.hidden = true;
  document.querySelector("#run-id").hidden = true;
  updateButton();
  send.textContent = "Solicitando envío…";
  status("Conectando con HappyRobot…", "No cierres esta página ni repitas la petición.");
  try {
    const data = await api("/api/send", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": config.csrf_token },
      body: JSON.stringify({
        to: document.querySelector("#to").value,
        message: message.value,
        confirmed: document.querySelector("#confirmed").checked,
        request_id: window.crypto.randomUUID(),
      }),
    });
    runId = data.run_id;
    const runLabel = document.querySelector("#run-id");
    runLabel.textContent = `Run: ${runId}`;
    runLabel.hidden = false;
    refresh.hidden = false;
    status("Solicitud aceptada.", "El workflow está en marcha. Todavía no confirma entrega al destinatario.");
    await pollRun(runId, current);
  } catch (error) {
    status("Envío no confirmado.", `${error.message} Si hubo un fallo de conexión, revisa las ejecuciones de HappyRobot antes de repetir.`, "error");
  } finally {
    document.querySelector("#confirmed").checked = false;
    busy = false;
    send.textContent = "Enviar otro SMS →";
    updateButton();
  }
});

refresh.addEventListener("click", async () => {
  if (!runId) return;
  refresh.disabled = true;
  try { await checkRun(runId, generation); }
  catch (error) { status("No se pudo consultar.", error.message, "error"); }
  finally { refresh.disabled = false; }
});
message.addEventListener("input", updateCount);
document.querySelector("#confirmed").addEventListener("change", updateButton);
updateCount();
try {
  config = await api("/api/config");
  document.querySelector("#sender").value = config.sender;
  connection.textContent = config.ready ? "Conectado al servidor local · Workflow SMS configurado" : config.reason;
  connection.classList.toggle("error", !config.ready);
  updateButton();
} catch {
  connection.textContent = "No se pudo conectar al servidor local. Recarga la página.";
  connection.classList.add("error");
}
