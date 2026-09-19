const form = document.querySelector("#telegram-form");
const connectForm = document.querySelector("#connect-form");
const send = document.querySelector("#send");
const connect = document.querySelector("#connect");
const pairCheck = document.querySelector("#pair-check");
const message = document.querySelector("#message");
const refresh = document.querySelector("#refresh");
let config;
let busy = false;
let runId;

async function api(path, body) {
  const options = { signal: window.AbortSignal.timeout(path === "/api/connect" ? 90000 : 45000) };
  if (body !== undefined) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-CSRF-Token": config.csrf_token };
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Error HTTP ${response.status}`);
  return data;
}

function status(title, detail, state = "") {
  document.querySelector("#status-title").textContent = title;
  document.querySelector("#status-message").textContent = detail;
  document.querySelector(".status-card").dataset.state = state;
}

function render(data) {
  config = data;
  const connection = document.querySelector("#connection");
  connection.textContent = data.reason || "Bot conectado · Chat vinculado · Listo para solicitar un simulacro";
  connection.classList.toggle("error", !data.workflow_configured);
  connect.disabled = !data.workflow_configured || busy;
  connectForm.hidden = Boolean(data.bot_username);
  document.querySelector("#pairing").hidden = !data.bot_username;
  document.querySelector("#bot-name").textContent = data.bot_username ? `Bot: @${data.bot_username}` : "";
  const link = document.querySelector("#pair-link");
  link.hidden = !data.pair_link;
  link.href = data.pair_link || "#";
  document.querySelector("#pair-help").hidden = Boolean(data.chat);
  pairCheck.hidden = Boolean(data.chat);
  pairCheck.disabled = busy;
  document.querySelector("#recipient").value = data.chat ? `${data.chat.name} · Chat privado vinculado` : "Pendiente de vinculación";
  document.querySelector("#simulation-prefix").textContent = data.simulation_prefix;
  document.querySelector("#workflow-link").href = data.workflow_url;
  document.querySelector("#verify-workflow").disabled = busy || !data.workflow_configured || data.workflow_verified;
  if (data.workflow_verified) document.querySelector("#workflow-status").textContent = "Autenticación de HappyRobot verificada. La comprobación no envía a ningún chat real.";
  updateButton();
}

function updateButton() {
  send.disabled = !config?.ready || busy || !document.querySelector("#confirmed").checked;
}

connectForm.addEventListener("submit", async event => {
  event.preventDefault();
  if (busy || !config?.workflow_configured || !connectForm.reportValidity()) return;
  busy = true;
  connect.disabled = true;
  const tokenInput = document.querySelector("#bot-token");
  const body = { token: tokenInput.value.trim(), confirmed_store_token: document.querySelector("#store-consent").checked };
  tokenInput.value = "";
  const setup = document.querySelector("#setup-status");
  setup.textContent = "Comprobando el bot y configurando HappyRobot…";
  try {
    render(await api("/api/connect", body));
    setup.textContent = "Bot conectado. Abre el enlace de arriba y pulsa Iniciar en Telegram.";
    setup.classList.remove("error");
  } catch (error) {
    setup.textContent = error.message;
    setup.classList.add("error");
  } finally {
    body.token = "";
    busy = false;
    render(config);
  }
});

pairCheck.addEventListener("click", async () => {
  if (busy) return;
  busy = true;
  pairCheck.disabled = true;
  const setup = document.querySelector("#setup-status");
  try {
    const data = await api("/api/pair", {});
    render(data);
    setup.textContent = data.chat ? "Chat vinculado. Ya puedes autorizar un simulacro." : "Todavía no aparece la vinculación. Abre el enlace exacto de arriba y pulsa Iniciar en Telegram.";
    setup.classList.remove("error");
  } catch (error) {
    setup.textContent = error.message;
    setup.classList.add("error");
  } finally {
    busy = false;
    render(config);
  }
});

document.querySelector("#verify-workflow").addEventListener("click", async () => {
  if (busy) return;
  busy = true;
  render(config);
  const output = document.querySelector("#workflow-status");
  output.textContent = "Comprobando el webhook sin un chat destinatario real…";
  try {
    render(await api("/api/verify-workflow", {}));
    output.classList.remove("error");
  } catch (error) {
    output.textContent = error.message;
    output.classList.add("error");
  } finally {
    busy = false;
    render(config);
  }
});

async function checkRun() {
  const data = await api(`/api/runs/${encodeURIComponent(runId)}`);
  if (["completed", "succeeded"].includes(data.status)) {
    status("Workflow completado.", "Comprueba el mensaje en Telegram. Este estado no confirma que se haya leído.", "success");
    return true;
  }
  if (["failed", "canceled", "skipped"].includes(data.status)) {
    status("No se completó el envío.", data.error || "Revisa el nodo de Telegram en HappyRobot antes de repetir.", "error");
    return true;
  }
  status("Simulacro en proceso.", `Estado en HappyRobot: ${data.status}. No vuelvas a enviarlo mientras se comprueba.`);
  return false;
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (busy || !config?.ready || !form.reportValidity()) return;
  busy = true;
  updateButton();
  refresh.hidden = true;
  document.querySelector("#run-id").hidden = true;
  status("Solicitando el simulacro…", "El mensaje se enviará únicamente al chat vinculado.");
  try {
    const data = await api("/api/send", { message: message.value,
      confirmed: document.querySelector("#confirmed").checked, request_id: window.crypto.randomUUID() });
    runId = data.run_id;
    document.querySelector("#run-id").textContent = `Run: ${runId}`;
    document.querySelector("#run-id").hidden = false;
    refresh.hidden = false;
    let done = false;
    for (let attempt = 0; attempt < 20 && !done; attempt++) {
      done = await checkRun();
      if (!done) await new Promise(resolve => setTimeout(resolve, 3000));
    }
    if (!done) status("Sigue en proceso.", "Consulta el estado sin volver a enviar el simulacro.");
  } catch (error) {
    status("Resultado no confirmado.", `${error.message} Revisa HappyRobot antes de repetir: la petición podría haberse procesado.`, "error");
  } finally {
    busy = false;
    document.querySelector("#confirmed").checked = false;
    updateButton();
  }
});

refresh.addEventListener("click", async () => {
  if (!runId) return;
  refresh.disabled = true;
  try { await checkRun(); }
  catch (error) { status("Estado no confirmado.", error.message, "error"); }
  finally { refresh.disabled = false; }
});
message.addEventListener("input", () => {
  document.querySelector("#count").textContent = `${message.value.length} / 1500`;
});
document.querySelector("#count").textContent = `${message.value.length} / 1500`;
document.querySelector("#confirmed").addEventListener("change", updateButton);
try { render(await api("/api/config")); }
catch { document.querySelector("#connection").textContent = "No se pudo conectar al servidor local. Recarga la página."; }
