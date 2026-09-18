---
tags: [happyrobot, concepto]
---

# Apps y MCP servers (lo que no usamos, pero conviene saber)

## Apps (Custom Apps)
Aplicaciones **Next.js gestionadas** (repo GitHub gestionado + Vercel + URL pública
`<slug>.happyrobot.ai`), editor sandbox con agente IA, variables de entorno cifradas, y
`NEXT_PUBLIC_TWIN_GATEWAY` inyectado si el org tiene el gateway de Twin desplegado. Se crean desde
la UI (la API solo permite duplicar: `POST /apps/{slug}/duplicate`) o importando un repo Next.js.
Decidimos hacer el dashboard como **web propia en el repo** (`web/`) por control y velocidad; se
podría importar después como App.

## MCP servers (primera parte)
`https://mcp.platform.eu.happyrobot.ai/{frontal|workflows|twin}/mcp` (OAuth 2.1, sin API key).
Frontal = construir/editar workflows por conversación (el "Workflows MCP" está en mantenimiento).
Instalación en Claude Code:
```bash
claude mcp add --transport http happyrobot-frontal https://mcp.platform.eu.happyrobot.ai/frontal/mcp
# luego /mcp → Authenticate
```
No lo usamos: la API REST con API key nos bastó y queda todo como código reproducible.

## SDK TypeScript
`@happyrobot-ai/sdk` (`client.workflows.triggerRun`, `client.voice.createToken`, helper
`triggerAndWait`); ejemplo completo `github.com/happyrobot-ai/voice-sdk-example`. Nuestro
equivalente en Python es `sos/happyrobot/client.py`.

Relacionado: [[Qué es HappyRobot]] · [[Twin - base de datos]] · [[Dashboard y simulador]]
