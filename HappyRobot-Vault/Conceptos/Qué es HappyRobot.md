---
tags: [happyrobot, concepto]
---

# Qué es HappyRobot

HappyRobot es una plataforma de **orquestación de agentes IA** ("AI operating system for the
real economy"): permite construir workflows tipo grafo de nodos donde un agente IA hace/recibe
llamadas de voz, WhatsApp, SMS, email o chat, y puede leer/escribir en sistemas externos (TMS/ERP)
mediante herramientas (tools).

- Web: https://www.happyrobot.ai/
- Docs oficiales: https://docs.happyrobot.ai (⚠️ **bloqueadas tras un código de acceso**, no
  pudimos leerlas directamente)
- Builder / app: https://builder.happyrobot.ai/ (equivalente a `platform.happyrobot.ai` / `platform.eu.happyrobot.ai`)

## Cómo obtuvimos la información

La documentación pública (`docs.happyrobot.ai`) pide un código de acceso, así que en vez de
leer la doc, **inspeccionamos directamente el OpenAPI público** que expone la propia API:

```
GET https://platform.happyrobot.ai/api/v2/docs/json
```

Ese endpoint devuelve el spec OpenAPI 3.0.3 completo (162 paths, 205 operaciones), sin
autenticación. De ahí sacamos todos los endpoints, parámetros y schemas reales.

> Dato curioso (via perfil independiente de api-evangelist.com/GitHub `api-evangelist/happyrobot`):
> la documentación está cerrada con código de acceso pero el OpenAPI está totalmente abierto —
> "an unusual inversion".

## Conceptos clave

| Concepto | Qué es |
|---|---|
| **Workflow** | El grafo completo: trigger + nodos de acción/agente/condición, etc. Equivale a un "flujo" o "agente" desde la UI. |
| **Version** | Cada workflow tiene versiones (borradores). Una versión se **publica** para quedar "live". |
| **Node** | Paso dentro de una versión: `trigger`, `action`, `agent`, `condition`, `loop`, etc. |
| **Event** | Cada nodo referencia un `event_id` — es el "tipo" concreto de trigger/acción (p. ej. "Web call", "Webhook", "Enviar email"...). |
| **Run** | Una ejecución concreta del workflow (p. ej. una llamada). |
| **Session** | La sesión de conversación/llamada asociada a un run. |
| **Template** | Forma rápida de crear un workflow ya configurado (ver [[Templates de workflow]]). |

Relacionado: [[Autenticación y hosts API]] · [[Workflows y nodos]]
