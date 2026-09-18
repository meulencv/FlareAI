---
tags: [happyrobot, índice]
---

# 🧭 Índice — Vault HappyRobot / FlareAI Voice

Este vault documenta todo lo descubierto y construido sobre **HappyRobot** para el proyecto
**FlareAI Web Voice** (una web con botón para hablar por voz con un agente IA, sin teléfono real).

> Objetivo del vault: que la próxima vez que se retome este trabajo (yo u otro asistente),
> se pueda leer aquí el contexto completo sin tener que redescubrir nada.

## Mapa de notas

### Conceptos (cómo funciona HappyRobot en general)
- [[Qué es HappyRobot]]
- [[Autenticación y hosts API]]
- [[Workflows y nodos]]
- [[Templates de workflow]]
- [[Voice Tokens y LiveKit]]
- [[Catálogo de voces]]

### Proyecto (lo que hemos construido nosotros)
- [[FlareAI Web Voice - workflow]]
- [[Web app - server y frontend]]
- [[Cómo arrancar todo]]

### Referencia
- [[IDs y recursos]]
- [[Endpoints usados]]
- [[Problemas y soluciones]]

### Bitácora
- [[2026-09-18]]

## Estado actual (resumen rápido)
- ✅ Workflow **FlareAI Web Voice** creado, publicado y en `production` en el clúster **EU**.
- ✅ Trigger: **Web call** (sin teléfono, sin SIP, sin credenciales extra).
- ✅ Voz cambiada a **español (es-ES)** — voz "Ana HR".
- ✅ Web local funcionando en `http://localhost:8000` (`voice/server.py` + `voice/index.html`).
- 🔑 API key real vive solo en variable de entorno `HAPPYROBOT_API_KEY`, nunca en el repo (ver [[Autenticación y hosts API]]).

Ver detalles técnicos completos en [[FlareAI Web Voice - workflow]] y [[Web app - server y frontend]].
