---
tags: [happyrobot, proyecto, guía]
---

# Cómo arrancar todo (guía rápida)

```bash
cd /Users/meulencv/development/projects/FlareAI/voice
export HAPPYROBOT_API_KEY=sk_live_...   # ver la key real en tu gestor de secretos, no aquí
python3 server.py
```

Abrir **http://localhost:8000**, pulsar **"🎙️ Iniciar llamada"**, aceptar el permiso de
micrófono del navegador, y hablar con Flare (en español).

## Arrancarlo en background (para que no se corte al cerrar la sesión)

```bash
cd voice
HAPPYROBOT_API_KEY=sk_live_... nohup python3 server.py > /tmp/hr-voice.log 2>&1 &
```

## Dónde ver las llamadas / transcripciones

En la plataforma HappyRobot (clúster **EU** → https://platform.eu.happyrobot.ai), dentro del
workflow **FlareAI Web Voice**:
- **Runs**: cada llamada queda como un run (`GET /workflows/{id}/runs`).
- **Sessions**: transcripción + audio de cada conversación.

También por API:
```bash
curl -H "Authorization: Bearer $HAPPYROBOT_API_KEY" \
  "https://platform.eu.happyrobot.ai/api/v2/workflows/01a0b665-2a84-725f-a714-947e427ea6d2/runs?limit=5"
```

## Si quieres cambiar el prompt o la voz

Dos formas:
1. **Desde la UI del builder** (más fácil): editar el nodo, y pulsar "Publish" ahí mismo.
2. **Por API** (lo que hicimos nosotros): seguir el flujo
   unpublish → unlock → PUT node → publish, documentado en
   [[FlareAI Web Voice - workflow]].

Relacionado: [[Web app - server y frontend]] · [[IDs y recursos]]
