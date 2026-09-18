---
tags: [happyrobot, referencia]
---

# Catálogo de nodos (eventos) relevantes

Obtenido con `GET /integrations/` (278 integraciones) + `GET /integrations/{id}`. `type` 0 = trigger,
1 = acción. Ids estables (los usa `sos/workflows/_builder.py::EV`).

| Integración | Evento | ID |
|---|---|---|
| Webhook | Incoming hook (trigger) | `01929b66-a335-7514-a159-cae2fe715286` |
| Webhook | Predefined request (trigger con schema) | `b329e750-2e0e-4618-ba65-e04bb6a93c5f` |
| Webhook | GET / POST / PUT / PATCH / DELETE | `01926f2a-b1f5-7e65-8203-86c5cd8838b6` / `01926f2b-2973-7ebf-ada1-e984251e27ec` / … |
| Workflow Function | Request (trigger) / Call Workflow | `019d95d2-e3e0-779a-9731-893810e5691f` / `019d95d2-e3ed-73ab-a43c-9b104b0b87d0` |
| AI Agent | Web call (trigger) | `6e32e01e-722f-4b8b-9372-500b845686d1` |
| AI Agent | Inbound Voice Agent / Outbound Voice Agent / Outbound con callback | `0192e5dc-08df-78bf-a549-f43c6bf9f087` / `0192e5dc-090a-7f57-87a0-76308ed6ef28` / `f78cf586-…` |
| AI Agent | Reasoning Agent | `0193d6ba-edd5-7510-9297-442991ef1725` |
| AI Agent | Chatbot Request (trigger) / Text Agent / Inbound Text Agent | `019a7b24-…` / `c1e2f3a4-…` / `019d4a7a-f3e9-72e5-…` |
| Code | Python Sandbox | `019dde7b-3500-7a3c-8f5e-1c2d4e6a8b9c` (Run python legacy retirado) |
| AI | Generate / Extract / Classify | `01926f31-1c45-…` / `01926f30-36a3-…` / `01926f30-36e3-…` |
| Conditions | Paths / Conditional output | `24d80afe-…` / `d6bc678f-…` (Paths se crea como `type: path`) |
| Loop | Loop | `8d8ec06c-…` (se crea como `type: loop`) |
| Schedule | Cron (trigger) / Sleep for seconds / Sleep until | `0192fff4-4da6-7712-a139-53c87250339f` / `b2a3a419-…` / `0efb8daf-…` |
| Twin | Read / Write / Query with SQL | `ebd81a7b-ace2-4225-9410-b657ce8ea412` / `7021bfff-3e47-459c-b871-b0271ca04d9f` / `7cd1c085-aedf-4ccc-94d4-a3f2011e982a` |
| Phone calls | Inbound to number (trigger) / Transfer / Forward | `0192a20c-…` / `01926f25-…` / `1cb6b546-…` |
| Text | Send SMS / Inbound Text Message | `019e3b65-…` / `fa85e0a1-…` |
| Slack | Send channel message / Wait for message reaction (HITL alternativo) | `01926dab-…` / `0192d437-…` |
| File | Knowledge base (RAG) / OCR / Parse file | `4d5f2589-…` / `d6d5a58f-…` / `7690b3ad-…` |
| Google Maps | Geocoding / Distance Matrix (requiere credencial) | `019d4a7a-f3e9-7f9e-…` / `019d4a7a-f3e9-74d0-…` |
| MCP Server | MCP Call | `019d4a7a-f3e9-7748-…` |

Sin credenciales en la org (2026-09-19): teléfonos, SIP, Slack, WhatsApp, Google Maps, Kafka, Redis…
Solo funcionan sin configurar: Webhook, Code, AI, Conditions, Loop, Schedule, Twin (cuando exista),
agentes con web call/reasoning, File/Knowledge base, Email de HappyRobot.

Relacionado: [[Formato de nodos por API]] · [[Workflows y nodos]]
