---
tags: [happyrobot, proyecto]
---

# Esquema de datos SOS (Twin / Postgres local)

Declarado en `sos/twin/schema.py` → DDL idempotente (`CREATE TABLE IF NOT EXISTS`, vistas con
`CREATE OR REPLACE`). Mismo SQL en Twin y en local. Aplicar: `python -m sos twin migrate`.

| Tabla | Para qué | Claves |
|---|---|---|
| `config` | pesos, umbrales, reglas (jsonb) editables en caliente | `key` pk |
| `assets` | núcleos, hospital, colegio, planta química, puerto, reserva (población, valor asegurado M€, bonos de carbono M€) | `ref` único |
| `contacts` | ciudadanos, mandos, policía, alcalde (rol, prioridad, zona) | `ref` único, `asset_id` |
| `resources` | brigadas, hidroavión, unidad de espuma, dron, patrulla; `capabilities` jsonb, `status` | `ref` único |
| `incidents` | el caso: `type`, `status` (candidate→verified/active→contained→closed / dismissed), `confidence`, `risk_score`, `priority`, `ai_assessment` jsonb | |
| `evidence` | toda entrada cruda (`source_type` call/firms/weather/drone/sensor/manual, `reliability`, `payload`) agrupada por proximidad/tiempo | `incident_id` |
| `weather_observations` | serie meteo por incidente (viento: dirección meteorológica "de dónde viene") | |
| `plans` | histórico de planes (uno nuevo por re-evaluación) | `incident_id` |
| `actions` | cola HITL: `kind` (evacuate_call/coordination_call/dispatch/notify), `status` (proposed→approved/rejected→ready→executing→done/failed), `requires_approval`, `payload` (instrucciones, contacto), `result`, `run_id`, `session_id` | |

Vistas: `v_open_incidents`, `v_pending_actions`, `v_latest_weather`, `v_active_calls`.

Datos de demo: `config/weights.json` (config) y `config/scenarios/demo_es.json` (Serra Calderona:
Serra, Náquera, Segart, Gátova, Olocau, Marines, Estivella, Sagunto, hospital, colegio, planta,
puerto, reserva; 11 contactos; 6 medios). `python -m sos twin seed` es idempotente (upsert por `ref`).

Decisiones: sin PostGIS (lat/lon + haversine en SQL/Python); `ref` estable para poder referenciar
entidades desde prompts y simulador sin UUIDs; `config.value` siempre jsonb (también escalares).
Ojo: `timestamp` sin zona → mezclar `now()` (hora local del servidor) con ISO UTC descoloca 2 h;
por eso ordenamos por `observed_at DESC, created_at DESC`.

Relacionado: [[Twin - base de datos]] · [[Base de datos local embebida]] · [[Motor de riesgo]]
