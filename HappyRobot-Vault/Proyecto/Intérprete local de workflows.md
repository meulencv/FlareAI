---
tags: [happyrobot, proyecto]
---

# Intérprete local de workflows (`sos/runtime`)

Ejecuta los **mismos `WorkflowSpec`** que se despliegan en HappyRobot, en local, reproduciendo la
semántica observada de la plataforma. Motivo: poder correr el simulador y el dashboard sin Twin,
y testear los workflows (variables, SQL, código de nodos) antes de desplegarlos.

- Variables como texto (números → "39.7", booleanos → "true", listas → JSON), rutas con punto.
- `python` → `exec(code, {"input_data": …})`; `twin_sql` → `{"rows": …}`; `twin_write` → upsert
  por columna primaria; `twin_read`; `http_get/post` (real: Open-Meteo funciona en local);
  `call_workflow` → ejecuta el otro spec en línea; `path` (condiciones con los mismos operadores);
  `loop`; `agent` → **política** que devuelve `[(tool, params)]` y se ejecutan los hijos de la tool.
- Políticas (`sos/runtime/agents.py`): `analista` (fiabilidad combinada `1-Π(1-r)` sobre fuentes
  distintas; verified si ≥ `min_independent_sources` y confianza ≥ 0.6 o alguna fuente ≥ 0.9;
  plan y acciones a partir del motor de riesgo; dedupe por (kind, ref) contra `prior_actions`),
  `voz_saliente` y `voz_112` (guionizadas por `runtime.scenario`).
- Los signals van por HTTP real salvo que el driver los intercepte (el simulador los muestra).

Limitación honesta: en local **no hay LLM ni voz**; la calidad de decisión del Reasoning Agent
solo se ve en cloud. La política local existe para que el flujo completo sea demostrable y testeable.

Tests: `tests/test_runtime_local.py` (5 escenarios, requiere el Postgres embebido).

Relacionado: [[Base de datos local embebida]] · [[Workflows SOS]] · [[Escenario demo - giro de viento]]
