---
tags: [happyrobot, referencia, api]
---

# Endpoints usados (chuleta)

Base: `https://platform.eu.happyrobot.ai/api/v2` — header siempre
`Authorization: Bearer $HAPPYROBOT_API_KEY`.

| Método | Path | Para qué |
|---|---|---|
| GET | `/workflows/?limit=N` | Listar workflows de la org |
| POST | `/workflows/` | Crear workflow (plain / from_template / version+nodes) |
| GET | `/workflows/{id}` | Ver un workflow |
| GET | `/workflows/templates` | Listar templates disponibles |
| POST | `/workflows/{id}/publish` | Publicar última versión (`{"environment":"production"}`) |
| POST | `/workflows/{id}/unpublish` | Despublicar (necesario antes de editar nodos) |
| GET | `/workflows/{id}/runs?limit=N` | Ver llamadas/ejecuciones recientes |
| GET | `/versions/{version_id}/nodes` | Listar nodos de una versión |
| GET | `/versions/{version_id}/nodes/{node_id}` | Ver un nodo concreto |
| PUT | `/versions/{version_id}/nodes/{node_id}` | Editar un nodo (falla si versión bloqueada) |
| POST | `/versions/{version_id}/unlock` | Desbloquear versión para poder editar nodos |
| POST | `/versions/{version_id}/lock` | Bloquear versión |
| POST | `/versions/{version_id}/fork` | Crear una copia editable de la versión |
| GET | `/voices/?limit=N` | Catálogo de voces disponibles |
| POST | `/voice/tokens/` | Generar token LiveKit para una llamada web (`{"workflow_id": "..."}`) |
| GET | `/events/{event_id}/config-schema` | Schema de configuración de un tipo de nodo/evento |

## Endpoint público sin auth (para explorar el spec)

```
GET https://platform.happyrobot.ai/api/v2/docs/json
```
Devuelve el OpenAPI 3.0.3 completo. Útil para volver a explorar cualquier endpoint que no esté
documentado aquí (guardamos una copia local en
`/tmp/.../scratchpad/spec.json` durante la sesión — no persistente, hay que re-descargarlo si
se necesita otra vez).

Relacionado: [[Autenticación y hosts API]] · [[Workflows y nodos]]

## Añadidos en la sesión 2026-09-19 (S.O.S.)

| Endpoint | Uso |
|---|---|
| `POST /workflows/` (plano) · `POST /versions/{v}/nodes` · `PUT …/nodes/{n}` · `DELETE …/nodes/{n}` | construir workflows por código |
| `PUT /versions/{v}/nodes/{n}/custom-output` | declarar salida de ejemplo (variables aguas abajo) |
| `POST /versions/{v}/nodes/{n}/test` | ejecutar un nodo suelto con valores de ejemplo |
| `GET /versions/{v}/nodes/{n}/available-vars` | ver qué variables (grupos/campos) ve un nodo |
| `GET /events/{event_id}/config-schema?use_case_id=` | campos de configuración de cada tipo de nodo |
| `GET /integrations/`, `GET /integrations/{id}` | catálogo de 278 integraciones y sus eventos (ids de nodo) |
| `POST /versions/{v}/tools/{t}/tool-call-result/generate` · `PUT …/visibility` | activar tools de agentes |
| `POST /workflows/{id}/variables` · `PATCH …/{var}` | variables de workflow (API key oculta, FIRMS key) |
| `POST /workflows/{id}/runs` | disparar run con payload (equivalente al hook) |
| `GET /runs/{id}/nodes` · `GET /runs/{id}/outputs/{oid}` · `GET /runs/{id}/sessions` · `GET /sessions/{id}/messages` | depurar runs y ver el razonamiento del agente |
| `POST /signals/` · `POST /signals/keys` | avisar a agentes en llamada |
| `POST /voice/tokens/` con `data` / con `session_id` (+`should_takeover`) | web call con parámetros / escuchar / tomar el control |
| `POST /twin/sql` · `GET /twin/schema` | base de datos (pendiente de provisionar) |
| `POST /realtime/tokens` (`runs_firehose`) | feed en vivo (previsto para el dashboard) |

