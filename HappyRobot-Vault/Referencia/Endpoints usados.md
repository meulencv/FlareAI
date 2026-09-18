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
