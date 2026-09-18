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
| Key 2 ⭐ | `...UUYeg` | ✅ lectura + creación + publicación + voz + signals · ❌ `twin.manage` | En `.env` (`HAPPYROBOT_API_KEY`); también como variable oculta en cada workflow SOS |

> Recordatorio de seguridad: ambas keys pasaron por el chat de esta sesión. Si se van a usar en
> producción de verdad, **rotarlas** desde la plataforma (Settings > Profile > API Keys) una vez
> terminadas las pruebas.

## Workflows

| Nombre | ID | Slug |
|---|---|---|
| test (preexistente, no nuestro) | `01a0b58b-ed5a-7a09-a663-51761e874588` | `qta0phzc98ww` |
| **FlareAI Web Voice** ⭐ | `01a0b665-2a84-725f-a714-947e427ea6d2` | `cx7sisk9if6q` |

## Workflows SOS (desplegados por `sos deploy` el 2026-09-19)

| Clave | Nombre | ID | Slug | Publicado |
|---|---|---|---|---|
| `ingest` | SOS · Ingesta de evidencias | `01a0b6af-6187-718d-a54e-ebf4162a7374` | `e63ungrodwxy` | sí |
| `assess` | SOS · Evaluación de incidente | `01a0b6af-627b-7d58-91de-3fb3ad486030` | `5rh0j7skhb1s` | sí |
| `execute` | SOS · Ejecución de acción | `01a0b6b6-8b65-72ef-8874-a4beda03c135` | `nfso7alppk61` | sí |
| `approve` | SOS · Aprobación humana | `01a0b6b6-8c32-706d-be34-981b6a16e18c` | `oloo648gpi35` | sí |
| `outbound_voice` | SOS · Llamada saliente (web call) | `01a0b6b9-41f2-7384-ae09-6879170ba8c3` | `thsat57aqgdi` | sí |
| `citizen_inbound` | SOS · 112 virtual (web call) | `01a0b6c9-7925-7352-982f-89e9648ba3ad` | `fr98xnx7qvqk` | sí |
| `weather_inject` | SOS · Meteo: observación y giro de viento | `01a0b6c9-79fc-7cb5-bc01-111002ee2984` | `tt2c77n1j1g6` | sí |
| `weather_feeder` | SOS · Meteo: sondeo Open-Meteo (cron) | `01a0b6c9-7add-78c8-8905-b3a95c5ec1cd` | `cih11v2rnz6i` | **no** (hasta Twin) |
| `firms_feeder` | SOS · FIRMS: sondeo satélite (cron) | `01a0b6c9-7bbb-7768-8db3-0a85221a1524` | `lmdrjfbvjxsm` | **no** (hasta Twin/key) |

Hooks: `https://platform.eu.happyrobot.ai/hooks/<slug>` (requieren `Authorization: Bearer`).
Ids de nodos por workflow en `deploy-state.json` (se regeneran en cada deploy). Los workflows de
laboratorio "SOS Lab" se borraron. Ver [[Workflows SOS]].

## Twin
- Estado: **no provisionado** (404) — activar en Settings → Twin Database. Key 2 sin `twin.manage` (403 en `/twin/sql`).
- Local: Postgres embebido `127.0.0.1:54329`, db `sos`, usuario `sos` → [[Base de datos local embebida]].

## Postgres embebido
- Binarios: zonky `embedded-postgres-binaries-darwin-arm64v8` 17.11.0 en `.local/pg/dist` (no versionado).

## FlareAI Web Voice — detalle interno
Ver [[FlareAI Web Voice - workflow]] para versión, nodos, prompt y voz aplicados.

## Voz aplicada
- ID: `31hktsdrgix8` — **Ana HR** (es-ES). Ver [[Catálogo de voces]] para alternativas.

Relacionado: [[Endpoints usados]]
