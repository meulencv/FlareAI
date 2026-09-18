---
tags: [happyrobot, proyecto, workflow]
---

# FlareAI Web Voice — workflow

El workflow de HappyRobot que da vida al agente de voz de la web. Ver también
[[Web app - server y frontend]] para el cliente que lo consume.

## Identificadores (clúster EU)

| Recurso | Valor |
|---|---|
| Workflow name | `FlareAI Web Voice` |
| Workflow ID | `01a0b665-2a84-725f-a714-947e427ea6d2` |
| Workflow slug | `cx7sisk9if6q` |
| Versión (Version 1) ID | `01a0b665-2a8f-7fb7-8180-646759935a59` |
| Nodo "Web Call" (trigger, action) | `01a0b665-2a94-7a82-a246-f8bc0d39e7c0` |
| Nodo "Prompt" | `01a0b665-2a9d-7d67-94b3-cb6a9568eb4f` |
| Nodo "Inbound Voice Agent" (config de voz/idioma) | `01a0b665-2a9d-7d67-94b3-cb6977e2ebb2` |
| Base URL API | `https://platform.eu.happyrobot.ai/api/v2` |

## Cómo se creó

Desde el template `inbound-voice-agent` (ver [[Templates de workflow]]):

```bash
curl -X POST -H "Authorization: Bearer $HAPPYROBOT_API_KEY" \
  -H "Content-Type: application/json" \
  "https://platform.eu.happyrobot.ai/api/v2/workflows/" \
  -d '{
    "name": "FlareAI Web Voice",
    "icon": "microphone",
    "from_template": {
      "template": "inbound-voice-agent",
      "inputs": {
        "agent_name": "Flare",
        "prompt": {
          "prompt_md": "# Rol\nEres Flare, un asistente de voz amable de FlareAI.\n\n# Instrucciones\n- Habla siempre en español, de forma natural y breve (1-2 frases por turno).\n- Responde a lo que te pregunte el usuario y ofrece ayuda.\n- Si el usuario se despide, despídete cordialmente.",
          "initial_message": "¡Hola! Soy Flare, tu asistente de voz. ¿En qué puedo ayudarte?",
          "initial_message_uninterruptible": false
        }
      }
    }
  }'
```

Luego se publicó:
```bash
curl -X POST -H "Authorization: Bearer $HAPPYROBOT_API_KEY" \
  "https://platform.eu.happyrobot.ai/api/v2/workflows/01a0b665-2a84-725f-a714-947e427ea6d2/publish" \
  -d '{"environment":"production"}'
```

## Cambio de idioma/voz a español

Configuración inicial (template por defecto) venía en **inglés** (`en` / `en-us`, voz "Paul").
El usuario pidió español. Se editó el nodo "Inbound Voice Agent":

```json
"agent": {
  "voices": [{"type":"static","static":{"id":"31hktsdrgix8","name":"Ana HR"}}],
  "languages": [{"type":"static","static":{"id":"es","name":"Spanish"}}],
  "language_accents": [{"type":"static","static":{"id":"es-es","name":"Spanish (Spain)"}}]
}
```

**Flujo necesario** (una versión publicada está bloqueada, ver [[Problemas y soluciones]]):

```bash
W=01a0b665-2a84-725f-a714-947e427ea6d2
V=01a0b665-2a8f-7fb7-8180-646759935a59
N=01a0b665-2a9d-7d67-94b3-cb6977e2ebb2

# 1. despublicar
curl -X POST .../workflows/$W/unpublish -d '{}'
# 2. desbloquear la versión
curl -X POST .../versions/$V/unlock -d '{}'
# 3. actualizar el nodo (PUT con el objeto completo: type, event_id, name, configuration)
curl -X PUT .../versions/$V/nodes/$N -d @update.json
# 4. publicar de nuevo
curl -X POST .../workflows/$W/publish -d '{"environment":"production"}'
```

Verificado con `GET /versions/{V}/nodes/{N}` → `agent.voices/languages/language_accents`
apuntan a Ana HR / es / es-es. ✅

## Estado actual
- **Publicado y live** en `production`.
- Voz: **Ana HR** (es-ES).
- Prompt en español, breve, tono cercano.

Relacionado: [[IDs y recursos]] · [[Catálogo de voces]] · [[Problemas y soluciones]]
