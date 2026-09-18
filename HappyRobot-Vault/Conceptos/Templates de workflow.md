---
tags: [happyrobot, concepto, api]
---

# Templates de workflow

`GET /workflows/templates` devuelve 6 plantillas disponibles. Cada una crea automáticamente
un workflow con su trigger + nodo de agente ya conectados.

| Template | Qué crea | Credenciales necesarias |
|---|---|---|
| `voice-agent` | Agente de voz **saliente** (llama a un teléfono dado en el payload del webhook trigger) | Requiere **SIP trunk** configurado en la org |
| **`inbound-voice-agent`** ⭐ | Agente de voz que **responde llamadas entrantes**, con trigger **Web call** | **Ninguna extra** — es el que usamos |
| `whatsapp-agent` | Agente saliente de WhatsApp | Credenciales WhatsApp |
| `sms-agent` | Agente saliente de SMS | Credenciales Twilio SMS |
| `email-agent` | Agente saliente de email | Credenciales Gmail |
| `chatbot-agent` | Chatbot de texto vía widget | Ninguna extra |

## Por qué elegimos `inbound-voice-agent`

El usuario pidió explícitamente: *"solo web call, no teléfono real"*. `voice-agent` es para
llamadas salientes reales (necesita SIP trunk, un teléfono de verdad). `inbound-voice-agent`
en cambio se dispara desde un **trigger de tipo Web call**, pensado para llamadas de voz desde
navegador vía WebRTC/LiveKit — exactamente lo que necesitábamos, y sin credenciales de
telefonía.

## Payload para crear desde template

```json
POST /workflows/
{
  "name": "FlareAI Web Voice",
  "icon": "microphone",
  "from_template": {
    "template": "inbound-voice-agent",
    "inputs": {
      "agent_name": "Flare",
      "prompt": {
        "prompt_md": "# Rol\n...",
        "initial_message": "¡Hola! Soy Flare...",
        "initial_message_uninterruptible": false
      }
    }
  }
}
```

`inputs.prompt` acepta también `model` (LLM, como `TemplatedValue` con `type: static` +
`static: {id, name}`) e `initial_message_delay_ms`.

Relacionado: [[FlareAI Web Voice - workflow]] · [[Workflows y nodos]]
