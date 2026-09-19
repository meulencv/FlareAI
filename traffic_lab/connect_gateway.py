import json
import os
import threading
import tkinter as tk
import urllib.error
import urllib.request
from tkinter import ttk

from happyrobot import BASE
from remote_setup import STATE, save


def store_credential(gateway_key, authorized_budget):
    happyrobot_key = os.environ.get("HAPPYROBOT_API_KEY")
    if not happyrobot_key:
        raise ValueError("Falta la autorización de HappyRobot en el proceso de configuración")
    value = json.loads(STATE.read_text(encoding="utf-8"))
    url = BASE + f"/workflows/{value['workflow_id']}/variables/{value['credential_variable_id']}"
    request = urllib.request.Request(url, method="PATCH", data=json.dumps({
        "value_production": gateway_key, "is_hidden_in_ui": True}).encode(),
        headers={"Authorization": "Bearer " + happyrobot_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            if response.status not in (200, 204):
                raise ValueError("La plataforma no confirmó la configuración")
    except urllib.error.HTTPError as error:
        raise ValueError(f"HappyRobot respondió HTTP {error.code}. No se ha mostrado ni guardado la clave en disco.") from None
    save({"budget_usd_authorized": authorized_budget, "gateway_credential_configured": True,
          "status": "credential_configured_pending_remote_verification"}, credential_update=True)


def main():
    root = tk.Tk()
    root.title("FlareAI · Conectar Vercel AI Gateway")
    root.geometry("650x390")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.after(1000, lambda: root.attributes("-topmost", False))
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Solo falta tu clave de Vercel", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Pega el valor completo de la API key de AI Gateway.\nSe enviará a la variable oculta del nuevo workflow de HappyRobot.\nNo se guardará en archivos ni se mostrará en la consola.", wraplength=585).pack(anchor="w", pady=(12, 20))
    entry = ttk.Entry(frame, show="*", width=75)
    entry.pack(fill="x")
    entry.focus_set()
    consent = tk.BooleanVar(value=False)
    ttk.Checkbutton(frame, variable=consent,
                    text="Autorizo hasta 2 USD de mis créditos para pruebas puntuales.\nSin recargas, tareas periódicas ni contrataciones.").pack(anchor="w", pady=16)
    message = tk.StringVar(value="No necesitas tocar Vercel CLI ni configurar nodos a mano.")
    ttk.Label(frame, textvariable=message, wraplength=585).pack(anchor="w", pady=(0, 14))
    outcome = {}

    def finish():
        if "error" in outcome:
            message.set(outcome["error"])
            button.configure(state="normal")
            entry.configure(state="normal")
        else:
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.configure(state="disabled")
            message.set("Clave configurada. Ya puedes cerrar esta ventana; continuaré con las pruebas.")
            button.configure(text="Cerrar", command=root.destroy, state="normal")
            print("Credencial configurada en HappyRobot; presupuesto de pruebas autorizado: 2 USD.", flush=True)

    def poll():
        if outcome:
            finish()
        else:
            root.after(200, poll)

    def submit():
        key = entry.get().strip()
        if len(key) < 20 or any(c.isspace() for c in key) or "…" in key or "..." in key:
            message.set("Introduce el valor completo de la clave, no su terminación visible.")
            return
        if not consent.get():
            message.set("Confirma el límite de pruebas para continuar; no se ha enviado la clave.")
            return
        button.configure(state="disabled")
        entry.delete(0, "end")
        entry.configure(state="disabled")
        message.set("Configurando la variable por API…")

        def work(secret):
            try:
                store_credential(secret, 2)
                outcome["ok"] = True
            except (OSError, ValueError, KeyError):
                outcome["error"] = "No se pudo configurar. No se han hecho llamadas de pago. Cierra la ventana y avísame."

        threading.Thread(target=work, args=(key,), daemon=True).start()
        root.after(200, poll)

    button = ttk.Button(frame, text="Conectar y autorizar pruebas", command=submit)
    button.pack(anchor="e")
    root.mainloop()


if __name__ == "__main__":
    main()
