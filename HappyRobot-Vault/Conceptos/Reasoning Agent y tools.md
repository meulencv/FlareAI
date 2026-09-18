---
tags: [happyrobot, concepto]
---

# Reasoning Agent y tools

Un **Reasoning Agent** es un agente sin canal (ni voz ni texto con una persona): recibe un
prompt, razona y usa tools hasta terminar. Es el "cerebro" ideal para "una IA evalúa los casos".

Lo que aprendimos ejecutándolo de verdad (ver run en `SOS Lab Fn`, 2026-09-18):

- Se crea como nodo `agent` con event `Reasoning Agent`; la API crea automáticamente un nodo
  hijo `prompt` (modelo por defecto `gpt-5.6-luna-max`).
- Las **tools cuelgan del prompt** y sus nodos hijos (Python, Twin, Webhook, Call Workflow, Paths…)
  se ejecutan cuando el agente la invoca. Lo que devuelven esos nodos es lo que ve el agente
  (`preview.steps[].output`), filtrado por los campos **expuestos** (Tool Call Result).
- El agente **no expone su texto final** como variable (solo `events`, `steps`, `name`). Por
  tanto: **todo resultado útil debe salir por tools** (en SOS: `guardar_evaluacion`,
  `guardar_plan`, `proponer_accion` escriben en Twin).
- Sin límite claro, el agente **repite tools** ("volveré a consultar…"): hay que decirle en el
  prompt "llama exactamente una vez" y no re-llamar tras un OK; poner `maxSessionDurationMinutes`.
- Sesión de un run de reasoning: `user_number: "reasoning_agent"`; mensajes en
  `GET /sessions/{id}/messages` (razonamiento + tool calls + respuestas de tool).
- Un run con un tool loop de 3 llamadas tardó ~15 s y consumió ~500 tokens de entrada.

## Patrón que usamos en WF-Assess

1. Nodos deterministas antes del agente preparan **todo el contexto** (SQL de Twin + motor de
   riesgo + resumen en texto) → el prompt lo recibe con `{{<resumen>.texto}}`.
2. El agente decide y **solo escribe vía tools** con esquema (status, confianza, plan, acciones).
3. Un nodo Python en cada tool valida/normaliza y un Write to Twin persiste. Las acciones que no
   requieren aprobación humana disparan WF-Execute desde dentro de la tool (Paths + Call Workflow).

En local (sin plataforma) el mismo contexto lo evalúa una **política determinista**
(`sos/runtime/agents.py`) que produce las mismas llamadas a tools → [[Intérprete local de workflows]].

Relacionado: [[Formato de nodos por API]] · [[Workflows SOS]] · [[Signals]]
