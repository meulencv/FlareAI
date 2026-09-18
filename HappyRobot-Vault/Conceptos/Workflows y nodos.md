---
tags: [happyrobot, concepto, api]
---

# Workflows y nodos

## Endpoints principales de workflows

```
GET    /workflows/                          Listar workflows
POST   /workflows/                          Crear workflow
GET    /workflows/{workflow_id}             Ver un workflow (acepta UUID o slug)
PATCH  /workflows/{workflow_id}              Actualizar
DELETE /workflows/{workflow_id}              Borrar
GET    /workflows/{workflow_id}/versions     Listar versiones
GET    /workflows/templates                  Listar templates disponibles
POST   /workflows/{workflow_id}/duplicate    Duplicar
POST   /workflows/{workflow_id}/publish      Publicar la última versión
POST   /workflows/{workflow_id}/unpublish    Despublicar
GET    /workflows/{workflow_id}/runs         Listar runs (ejecuciones)
POST   /workflows/{workflow_id}/runs         Disparar un run
GET    /workflows/{workflow_id}/sessions     Listar sesiones
```

## Estructura de un workflow al crearlo

`POST /workflows/` admite 3 modos (mutuamente excluyentes):

1. **Plain**: workflow vacío con una versión inicial.
2. **`from_template`**: usa una plantilla predefinida (ver [[Templates de workflow]]). Las
   credenciales se auto-descubren de la organización. **Este es el que usamos.**
3. **`version` + `nodes`**: defines tú los nodos a mano. El primer nodo debe ser `type: trigger`;
   los siguientes referencian a su padre vía `parent_index`.

## Tipos de nodo (`type`)

Visto en el schema: `trigger`, `action`, `agent`, `condition`, `cron`, `loop`, `loop_break`,
`loop_end`, `prompt` (nodo de prompt del agente).

Cada nodo tiene:
- `id` — UUID propio del nodo dentro de la versión.
- `event_id` — UUID que identifica el "tipo concreto" (p. ej. el evento "Web call" o "Webhook").
  Se puede consultar su schema de configuración con `GET /events/{event_id}/config-schema`.
- `configuration` — objeto JSON libre (JSONB) con los parámetros específicos del nodo/evento.
- `parent_id` / `parent_node_index` — quién es el nodo padre en el grafo.

## Versiones: publicar, despublicar, bloqueo

- Una versión **nueva** (recién creada) está desbloqueada → se puede editar sus nodos con
  `PUT /versions/{version_id}/nodes/{node_id}`.
- **Al publicarla** (`POST /workflows/{id}/publish`), la versión queda **bloqueada**: cualquier
  intento de `PUT` sobre sus nodos da:
  ```json
  {"error":"Bad Request","message":"Cannot update nodes on a locked version. Unlock or fork the version first.","statusCode":400}
  ```
- Para volver a editarla: `POST /versions/{version_id}/unlock` (o `unlock` tras
  `unpublish`), editar, y `POST /workflows/{id}/publish` de nuevo.
  (Alternativa si se quiere conservar la versión anterior: `POST /versions/{version_id}/fork`.)

  > Flujo real que usamos (ver [[Problemas y soluciones]]):
  > `unpublish` → `unlock` → `PUT nodes/{node_id}` → `publish`.

## Endpoints de nodos

```
GET    /versions/{version_id}/nodes                          Listar nodos de una versión
POST   /versions/{version_id}/nodes                          Añadir nodos
GET    /versions/{version_id}/nodes/{node_id}                 Ver un nodo
PUT    /versions/{version_id}/nodes/{node_id}                 Actualizar un nodo (bloqueado si versión publicada)
GET    /versions/{version_id}/nodes/{node_id}/available-vars  Variables disponibles para ese nodo
GET    /versions/{version_id}/nodes/{node_id}/config-schema   Schema de configuración del nodo
POST   /versions/{version_id}/nodes/{node_id}/test            Testear un nodo individual
```

Relacionado: [[Templates de workflow]] · [[Problemas y soluciones]] · [[FlareAI Web Voice - workflow]]
