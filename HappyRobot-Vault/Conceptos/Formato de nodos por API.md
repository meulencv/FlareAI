---
tags: [happyrobot, concepto]
---

# Formato de nodos por API (lo que NO está en la documentación)

La doc describe los nodos desde la UI; el JSON exacto que espera la API lo descubrimos creando
un workflow de laboratorio y leyendo los errores de validación (son de `zod` y muy explícitos).
Todo esto está codificado en `sos/workflows/_builder.py` (mini-DSL) y `sos/workflows/deploy.py`.

## Reglas generales

- **Crear nodos**: `POST /versions/{v}/nodes {"nodes": [...]}`. Cada nodo: `type` ∈ trigger | action
  | agent | tool | path | condition | loop | loop_break, `event_id` (trigger/action/agent), `name`,
  `parent_node_id` **o** `parent_node_index`. Si el lote incluye un trigger, **reemplaza todos los
  nodos** de la versión (así redesplegamos limpio).
- `PUT /versions/{v}/nodes/{n}` exige repetir `type` y `event_id`. En el director, los nodos creados
  como `trigger`/`agent` se devolvieron como `action`: usar el tipo real para actualizar.
- `webhook_payload` se pasa al nivel superior del cuerpo POST/PUT, no dentro de `configuration`.
  Incoming hook entrega el cuerpo recibido bajo `data`: referenciar `data.context_json` en el prompt.
  Tras un fork, consultar `available-vars`: el grupo puede conservar el ID persistente original.
- No usar automáticamente `configuration.api_key` devuelta por GET como clave literal del hook:
  se observó un token transformado distinto del valor de la UI. Conservar la credencial backend.
- Una versión **publicada está bloqueada**: `unpublish` → `unlock` → editar → `publish`.
- Los nodos se crean **uno a uno en orden DFS**: como las variables solo fluyen aguas abajo, al
  crear un nodo ya conocemos los ids de todos los que puede referenciar.
- `PUT /versions/{v}/nodes/{n}/custom-output {"data": {...}}` declara la salida de ejemplo de un
  nodo (necesario para que los siguientes puedan referenciar sus campos sin ejecutar tests).
- POST/PUT/DELETE **sin cuerpo** fallan (`Body cannot be empty…`): enviar siempre `{}`.
- `POST /workflows/` con nodos inline: van en `version.nodes` (no en la raíz) y con `parent_node_index`.

## Texto enriquecido y variables

```json
[{"type": "paragraph", "children": [
   {"text": "Bearer "},
   {"type": "variable", "children": [{"text": ""}], "group_id": "<node_id>", "variable_id": "campo"}]}]
```
- `group_id` = id del nodo (o `use_case_variables` para variables de workflow, `current`, `time`).
- `variable_id` admite rutas con punto: `rows.0.id`, `headers.Accept-Encoding`.
- `key_value_pairs` (input_data del Python, data de Call Workflow): `[{"key": "x", "value": [PARAGRAPH]}]`.
- En **cadenas crudas** (`body.raw` del Webhook, `sql` del nodo Twin): token `{{$var:<group>.<campo>}}`.
- En **prompt_md** de los agentes: `{{<node_id>.<campo>}}`, `{{current.run_id}}`, `{{time.now_iso}}`
  (**`{{$var:…}}` NO se resuelve en prompts**, ni `{{campo}}` a secas).
- `initial_message` acepta string o PARAGRAPH (con variables).

## Cómo llegan los valores a los nodos

Todo llega como **texto**: números `"39.7"`, booleanos `"true"`, **listas como JSON** ✅, pero
**objetos anidados como `map[k:v]` (formato Go) ❌** → nunca pasar objetos entre nodos: pasar
campos sueltos (`payload.text`) o serializar a JSON string en el nodo origen. Las filas de Twin
llegan como lista JSON → `json.loads` en Python.

## Nodos concretos

| Nodo | event_id | configuration |
|---|---|---|
| Incoming hook | `01929b66-a335-7514-a159-cae2fe715286` | con `webhook_payload` de ejemplo la API lo convierte en **Predefined request** (`b329e750-…`) con `params: [...]`. `callable_by_workflows: true` para poder llamarlo con Call Workflow |
| Workflow Function Request | `019d95d2-e3e0-779a-9731-893810e5691f` | `{"params": ["incident_id"]}`; expone también `caller_node_id`, `parent_run_id` |
| Web call | `6e32e01e-722f-4b8b-9372-500b845686d1` | `{"params": [...], "require_webcall_auth": true}`; los `data` del token de voz deben coincidir con `params` |
| Cron | `0192fff4-4da6-7712-a139-53c87250339f` | `{"cron": {"expression": "*/5 * * * *"}}` (aceptado) |
| Python Sandbox | `019dde7b-3500-7a3c-8f5e-1c2d4e6a8b9c` | `{"code": "...", "execution_profile": "standard\|advanced", "input_data": KV}`. **Sin red.** `output = {...}` |
| Webhook POST/GET | `01926f2b-…` / `01926f2a-…` | `url: PARAGRAPH`, `webhookSchemaVersion: 2`, `headers: [{key, value: PARAGRAPH}]`, `params` igual, `body: {"schemaVersion": 2, "contentType": "application/json", "raw": "<string con {{$var}}>"}`. Respuesta JSON → variables (`rows`, `headers.X`…) |
| Call Workflow | `019d95d2-e3ed-73ab-a43c-9b104b0b87d0` | `to_workflow: {"type":"static","static":{"id","name"}}`, `data: KV`, `fire_and_forget`, `timeout: PARAGRAPH`, `use_caller_environment: true` |
| Paths | `type: "path"` (sin event) | hijos `type: "condition"` con `type_of_condition: conditional\|fallback` y `conditions: [{id, ors:[{id, ands:[{id, field:{group_id,variable_id}, condition:"text_equals", value: PARAGRAPH}]}]}]`. Un path creado solo trae hijos por defecto ("Path 1", "Fallback"): **borrarlos** |
| Loop | `type: "loop"` | `iterate_over: "{{$var:<node>.rows}}"` (**string**), `loop_variable`, `execute_in_parallel`; dentro se referencia `Ref(loop, "item.campo")` |
| Reasoning Agent | `0193d6ba-edd5-7510-9297-442991ef1725` (`type: agent`) | crea automáticamente un hijo `prompt`; `prompt: {prompt_md}` en la creación o `PUT` al prompt. Config: `name: PARAGRAPH`, `maxSessionDurationMinutes: PARAGRAPH`… **No expone su respuesta** como variable: solo actúa vía tools |
| Inbound Voice Agent | `0192e5dc-08df-78bf-a549-f43c6bf9f087` | `agent: {name, voices:[static], languages:[static], language_accents:[static]}`; también para web calls salientes simuladas |
| Tool | `type: "tool"`, `parent` = el agente | `function: {description: PARAGRAPH, parameters: [{name, description: PARAGRAPH, required, example}], message: {type: none\|fixed}}`. Sus **nodos hijos** se ejecutan al invocarla; los parámetros son variables `Ref(tool, param)`. Antes de publicar: `POST …/tools/{t}/tool-call-result/generate` y `PUT …/visibility {node_id, exposed_fields}` |
| Signals en un agente | — | `POST /signals/keys {node_id, key}` deja `agentSignalsConfig: {enabled, customTopics:[{bindings, topicName}], shouldRespondOnSignal}` |

Los ids de eventos son estables (catálogo `GET /integrations/{id}`), ver [[Catálogo de nodos]].

Relacionado: [[Workflows y nodos]] · [[Twin - base de datos]] · [[Reasoning Agent y tools]] · [[Workflows SOS]] · [[Problemas y soluciones]]
