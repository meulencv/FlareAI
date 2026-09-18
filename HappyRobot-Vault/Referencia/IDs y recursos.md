---
tags: [happyrobot, referencia]
---

# IDs y recursos

## Organización
- Org ID: `01a0b58b-d9b2-7773-b751-17c001601327`
- Clúster: **EU** → `https://platform.eu.happyrobot.ai/api/v2`

## API Keys usadas (redactadas — la clave real nunca se guarda en el repo/vault)

| Alias | Últimos 4 caracteres | Permisos | Notas |
|---|---|---|---|
| Key 1 | `...JSs0` | ❌ inválida en host global / sin permiso de creación en EU (`403 Cannot create use cases`) | No usar |
| Key 2 ⭐ | `...UUYeg` | ✅ lectura + creación + publicación | La que usa `voice/server.py` vía `HAPPYROBOT_API_KEY` |

> Recordatorio de seguridad: ambas keys pasaron por el chat de esta sesión. Si se van a usar en
> producción de verdad, **rotarlas** desde la plataforma (Settings > Profile > API Keys) una vez
> terminadas las pruebas.

## Workflows

| Nombre | ID | Slug |
|---|---|---|
| test (preexistente, no nuestro) | `01a0b58b-ed5a-7a09-a663-51761e874588` | `qta0phzc98ww` |
| **FlareAI Web Voice** ⭐ | `01a0b665-2a84-725f-a714-947e427ea6d2` | `cx7sisk9if6q` |

## FlareAI Web Voice — detalle interno
Ver [[FlareAI Web Voice - workflow]] para versión, nodos, prompt y voz aplicados.

## Voz aplicada
- ID: `31hktsdrgix8` — **Ana HR** (es-ES). Ver [[Catálogo de voces]] para alternativas.

Relacionado: [[Endpoints usados]]
