---
tags: [happyrobot, índice]
---

# 🧭 Índice — Vault HappyRobot / S.O.S. Agentic Crisis Engine

Este vault documenta todo lo descubierto y construido sobre **HappyRobot**: primero la web de voz
**FlareAI Web Voice** (2026-09-18) y después el **S.O.S. Agentic Crisis Engine** para el reto de
HackSpain 2026 (2026-09-19): gestión autónoma de crisis con Twin, workflows, Reasoning Agent, voz
y dashboard con aprobación humana.

> Objetivo del vault: que la próxima vez que se retome este trabajo (yo u otro asistente), se pueda
> leer aquí el contexto completo sin tener que redescubrir nada. Empieza por
> [[SOS Crisis Engine - arquitectura]] y [[Cómo arrancar todo]].

## Mapa de notas

### Conceptos (cómo funciona HappyRobot en general)
- [[Qué es HappyRobot]]
- [[Autenticación y hosts API]]
- [[Workflows y nodos]]
- [[Formato de nodos por API]] ← el JSON real de cada nodo (no está en la doc)
- [[Twin - base de datos]]
- [[Reasoning Agent y tools]]
- [[Signals]]
- [[Python Sandbox]]
- [[Templates de workflow]]
- [[Voice Tokens y LiveKit]]
- [[Catálogo de voces]]
- [[Apps y MCP]]

### Proyecto (lo que hemos construido)
- [[SOS Crisis Engine - arquitectura]]
- [[Workflows SOS]] (los 9 desplegados)
- [[Esquema de datos SOS]]
- [[Motor de riesgo]]
- [[Base de datos local embebida]]
- [[Intérprete local de workflows]]
- [[Dashboard y simulador]]
- [[Escenario demo - giro de viento]]
- [[Cómo desplegar - sos deploy]]
- [[Cómo arrancar todo]]
- Legacy 2026-09-18: [[FlareAI Web Voice - workflow]] · [[Web app - server y frontend]]

### Referencia
- [[IDs y recursos]]
- [[Endpoints usados]]
- [[Catálogo de nodos]]
- [[Problemas y soluciones]] (18 problemas concretos y su solución)

### Bitácora
- [[2026-09-18]] — agente de voz web + vault
- [[2026-09-19]] — S.O.S. Crisis Engine completo (plan, laboratorio de formatos, deploy, local, simulador, dashboard)

## Estado actual (resumen rápido, 2026-09-19)
- ✅ **9 workflows SOS** publicados en HappyRobot (EU, org `hackspainteam3`), definidos como código y
  desplegables con `python -m sos deploy`. Los 2 cron (meteo, FIRMS) despublicados hasta tener Twin.
- ⚠️ **Twin no provisionado** (404) y API key sin `twin.manage` → **acción del usuario**:
  Settings → Twin Database → Enable + key con Full Twin access. Mientras: Postgres embebido en
  `.local/pg` con el mismo esquema, y `sos twin sync-to-twin` para migrar.
- ✅ `python main_simulation.py` funciona en local de punta a punta (aviso 112 → satélite →
  verificación IA → plan/acciones → aprobación → llamadas → giro de viento → re-plan + signal).
- ✅ Dashboard en `http://localhost:8000` (`python web/server.py`), voz por web call (agente básico
  hasta que haya Twin).
- ✅ 12 tests (`.venv/bin/python -m pytest -q tests`). Commit `be1bb86` + docs.
- 🔑 Secretos solo en `.env` / variables de workflow; nunca en repo ni vault.
