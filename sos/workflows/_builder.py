"""Mini-DSL para definir workflows de HappyRobot y traducirlos al JSON de la API.

Formatos descubiertos empíricamente (ver vault → "Formato de nodos por API"):

- Texto enriquecido ("paragraph"): `[{"type":"paragraph","children":[{"text":".."}, VAR, ..]}]`
  donde VAR = `{"type":"variable","children":[{"text":""}],"group_id":<node_id>,"variable_id":<campo>}`.
- `key_value_pairs`: `[{"key": str, "value": <paragraph>}]`.
- En cadenas crudas (body.raw del Webhook, sql del nodo Twin) se usa el token
  `{{$var:<group_id>.<campo>}}`.
- Grupos especiales: variables de workflow = `use_case_variables`, `current`, `time`.
- Los ids de nodo solo se conocen tras crearlos → se referencian por NOMBRE (`Ref("nodo","campo")`)
  y `render()` los sustituye en una segunda pasada.
- Un `agent` crea automáticamente un hijo `prompt`; los `tool` cuelgan del prompt, y los nodos
  hijos del tool se ejecutan al invocarlo. El agente solo "emite" resultados a través de tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---- eventos (ids de la plataforma; estables en el catálogo de integraciones) ----------------

EV = {
    # triggers
    "incoming_hook": "01929b66-a335-7514-a159-cae2fe715286",
    "predefined_request": "b329e750-2e0e-4618-ba65-e04bb6a93c5f",
    "workflow_function_request": "019d95d2-e3e0-779a-9731-893810e5691f",
    "web_call": "6e32e01e-722f-4b8b-9372-500b845686d1",
    "cron": "0192fff4-4da6-7712-a139-53c87250339f",
    # acciones
    "python": "019dde7b-3500-7a3c-8f5e-1c2d4e6a8b9c",
    "http_get": "01926f2a-b1f5-7e65-8203-86c5cd8838b6",
    "http_post": "01926f2b-2973-7ebf-ada1-e984251e27ec",
    "call_workflow": "019d95d2-e3ed-73ab-a43c-9b104b0b87d0",
    "twin_sql": "7cd1c085-aedf-4ccc-94d4-a3f2011e982a",
    "twin_write": "7021bfff-3e47-459c-b871-b0271ca04d9f",
    "twin_read": "ebd81a7b-ace2-4225-9410-b657ce8ea412",
    "ai_extract": "01926f30-36a3-7394-8f73-eeead5d7f948",
    "ai_generate": "01926f31-1c45-7b87-a458-c9527cb7e542",
    "sleep": "b2a3a419-732f-4ffd-ac37-e597b2b426a8",
    # agentes
    "reasoning_agent": "0193d6ba-edd5-7510-9297-442991ef1725",
    "inbound_voice_agent": "0192e5dc-08df-78bf-a549-f43c6bf9f087",
    "outbound_voice_agent": "0192e5dc-090a-7f57-87a0-76308ed6ef28",
}

SPECIAL_GROUPS = {"$vars": "use_case_variables", "$current": "current", "$time": "time"}


# ---- referencias y texto ----------------------------------------------------------------------


@dataclass(frozen=True)
class Ref:
    """Referencia a la salida `field` del nodo `node` (por nombre) o a un grupo especial."""

    node: str
    field: str

    def group_id(self, ids: dict[str, str]) -> str:
        if self.node in SPECIAL_GROUPS:
            return SPECIAL_GROUPS[self.node]
        return ids.get(self.node, f"__pending__{self.node}")


class Raw:
    """Cadena cruda con tokens de variable.

    style="var"   → `{{$var:<group>.<campo>}}` (body.raw del Webhook, sql del nodo Twin).
    style="plain" → `{{<group>.<campo>}}` (prompt_md de los agentes; ahí `$var` NO se resuelve).
    """

    def __init__(self, *parts: str | Ref, style: str = "var"):
        self.parts = parts
        self.style = style

    def render(self, ids: dict[str, str]) -> str:
        out = []
        for p in self.parts:
            if isinstance(p, Ref):
                g = p.group_id(ids)
                out.append(f"{{{{$var:{g}.{p.field}}}}}" if self.style == "var" else f"{{{{{g}.{p.field}}}}}")
            else:
                out.append(str(p))
        return "".join(out)


def Prompt(*parts: str | Ref) -> Raw:
    """Texto de prompt con variables (`{{group.campo}}`)."""
    return Raw(*parts, style="plain")


def P(*parts: str | Ref) -> list:
    """Paragraph enriquecido a partir de trozos de texto y Refs."""
    children: list[Any] = []
    for p in parts:
        children.append(p if isinstance(p, Ref) else {"text": str(p)})
    if not children:
        children = [{"text": ""}]
    return [{"type": "paragraph", "children": children}]


def KV(**pairs: Any) -> list[dict]:
    """key_value_pairs: cada valor puede ser str, Ref o paragraph ya construido."""
    out = []
    for k, v in pairs.items():
        if isinstance(v, list):
            out.append({"key": k, "value": v})
        else:
            out.append({"key": k, "value": P(v)})
    return out


def static(id_: str, name: str | None = None) -> dict:
    return {"type": "static", "static": {"id": id_, "name": name or id_}}


def render(obj: Any, ids: dict[str, str]) -> Any:
    if isinstance(obj, Ref):
        return {"type": "variable", "children": [{"text": ""}], "group_id": obj.group_id(ids), "variable_id": obj.field}
    if isinstance(obj, Raw):
        return obj.render(ids)
    if isinstance(obj, dict):
        return {k: render(v, ids) for k, v in obj.items()}
    if isinstance(obj, list):
        return [render(v, ids) for v in obj]
    return obj


# ---- nodos --------------------------------------------------------------------------------------


@dataclass
class Node:
    name: str
    type: str  # trigger | action | agent | tool | path | condition | loop | loop_break
    event: str | None = None  # clave de EV
    config: dict = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    outputs: dict | None = None  # muestra de salida → custom-output (habilita variables aguas abajo)
    extra: dict = field(default_factory=dict)  # campos de nivel superior (prompt, function, conditions...)
    prompt_md: str | Raw | None = None  # solo agent (Prompt(...) para variables)
    initial_message: str | list | None = None  # solo agent (voz): str o P(...) con variables
    signals: list[str] = field(default_factory=list)  # solo agent: topics custom (p.ej. "incident.*")
    model: str | None = None  # solo agent
    expose: list[str] | None = None  # solo tool: campos del resultado visibles para el agente (None = todos)

    def add(self, *nodes: "Node") -> "Node":
        self.children.extend(nodes)
        return self

    def walk(self):
        yield self
        for ch in self.children:
            yield from ch.walk()


def Trigger(name: str, event: str, config: dict | None = None, sample: dict | None = None) -> Node:
    cfg = dict(config or {})
    if sample and "params" not in cfg and event in ("predefined_request", "incoming_hook", "workflow_function_request", "web_call"):
        cfg["params"] = list(sample.keys())
    return Node(name, "trigger", event, cfg, outputs=sample)


def Action(name: str, event: str, config: dict, outputs: dict | None = None) -> Node:
    return Node(name, "action", event, config, outputs=outputs)


def Python(name: str, code: str, inputs: dict | None = None, outputs: dict | None = None, profile: str = "standard") -> Node:
    cfg: dict[str, Any] = {"execution_profile": profile, "code": code}
    if inputs:
        cfg["input_data"] = KV(**inputs)
    return Action(name, "python", cfg, outputs)


def HttpPost(name: str, url: str | Raw, body: Raw | str, headers: dict[str, Any] | None = None, outputs: dict | None = None, ignore_5xx: bool = False) -> Node:
    cfg: dict[str, Any] = {
        "url": P(url) if isinstance(url, str) else P(*url.parts),
        "webhookSchemaVersion": 2,
        "body": {"schemaVersion": 2, "contentType": "application/json", "raw": body},
        "ignore5XX": ignore_5xx,
    }
    if headers:
        cfg["headers"] = [{"key": k, "value": v if isinstance(v, list) else P(v)} for k, v in headers.items()]
    return Action(name, "http_post", cfg, outputs)


def HttpGet(name: str, url: str | Raw, headers: dict[str, Any] | None = None, params: dict[str, Any] | None = None, outputs: dict | None = None) -> Node:
    cfg: dict[str, Any] = {"url": P(url) if isinstance(url, str) else P(*url.parts), "webhookSchemaVersion": 2}
    if headers:
        cfg["headers"] = [{"key": k, "value": v if isinstance(v, list) else P(v)} for k, v in headers.items()]
    if params:
        cfg["params"] = [{"key": k, "value": v if isinstance(v, list) else P(v)} for k, v in params.items()]
    return Action(name, "http_get", cfg, outputs)


def TwinSQL(name: str, sql: Raw | str, max_rows: int = 100, outputs: dict | None = None) -> Node:
    """Consulta de solo lectura (SELECT/WITH) contra Twin. Devuelve filas."""
    return Action(name, "twin_sql", {"sql": sql, "maxRows": max_rows}, outputs)


def TwinExec(name: str, sql: Raw | str, outputs: dict | None = None) -> Node:
    """Cualquier SQL (INSERT/UPDATE/...) vía la API pública de Twin, con la API key en variable
    de workflow `HAPPYROBOT_API_KEY`. Es el 'escape hatch' para escribir desde un workflow.
    Nota: los tokens {{$var}} se sustituyen en crudo → las comillas deben venir ya escapadas."""
    raw = Raw('{"sql": "', *(sql.parts if isinstance(sql, Raw) else (sql,)), '"}')
    return HttpPost(
        name,
        Raw(Ref("$vars", "HAPPYROBOT_API_BASE"), "/twin/sql"),
        raw,
        headers={"Authorization": P("Bearer ", Ref("$vars", "HAPPYROBOT_API_KEY"))},
        outputs=outputs or {"command": "INSERT", "rowCount": 1, "rows": []},
    )


def TwinWrite(name: str, table: str, values: dict[str, tuple[str, Any]], primary: str | None = None, outputs: dict | None = None) -> Node:
    """Nodo nativo 'Write to Twin' (insert; upsert si `primary` está en `values`).

    values: {columna: (tipo, valor)} con tipo ∈ text|uuid|float8|int8|boolean|timestamp|jsonb y
    valor str|Ref|paragraph. Corre 'como la org': no necesita API key ni permisos twin.manage.
    """
    cols = []
    for col, (typ, val) in values.items():
        cols.append({"columnName": col, "type": typ, "isPrimary": col == primary, "value": val if isinstance(val, list) else P(val)})
    return Action(name, "twin_write", {"tableName": table, "columnValues": cols}, outputs)


def TwinRead(name: str, table: str, filters: list[tuple[str, str, Any]] | None = None, limit: int = 100, order_by: str | None = None, desc: bool = False, outputs: dict | None = None) -> Node:
    """Nodo nativo 'Read from Twin'. filters: [(columna, operador, valor)] con operador ∈
    equals|not_equal|greater_than|less_than|greater_or_equal|less_or_equal|contains."""
    cfg: dict[str, Any] = {"tableName": table, "limit": P(str(limit)),
                           "filters": [{"column": c, "operator": op, "value": v if isinstance(v, list) else P(v)} for c, op, v in (filters or [])]}
    if order_by:
        cfg["orderByColumn"] = order_by
        cfg["orderByDirection"] = "desc" if desc else "asc"
    return Action(name, "twin_read", cfg, outputs)


def CallWorkflow(name: str, workflow_ref: str, data: dict[str, Any], fire_and_forget: bool = True, timeout_s: int = 300) -> Node:
    """`workflow_ref` es el nombre lógico del workflow destino (se resuelve a id en deploy)."""
    cfg = {
        "to_workflow": {"__workflow__": workflow_ref},
        "use_caller_environment": True,
        "fire_and_forget": fire_and_forget,
        "timeout": P(str(timeout_s)),
        "data": KV(**data),
    }
    return Action(name, "call_workflow", cfg)


def Paths(name: str, *branches: Node) -> Node:
    return Node(name, "path", None, {}, list(branches))


def When(name: str, ref: Ref, op: str, value: str | None = None, *nodes: Node) -> Node:
    """Rama condicional. op: text_equals, number_greater_than, boolean_true, is_empty, ..."""
    cond: dict[str, Any] = {"id": f"c_{name}", "ors": [{"id": f"o_{name}", "ands": [{"id": f"a_{name}", "field": ref, "condition": op}]}]}
    if value is not None:
        cond["ors"][0]["ands"][0]["value"] = P(value)
    return Node(name, "condition", None, {}, list(nodes), extra={"type_of_condition": "conditional", "conditions": [cond]})


def Otherwise(name: str, *nodes: Node) -> Node:
    return Node(name, "condition", None, {}, list(nodes), extra={"type_of_condition": "fallback"})


def Loop(name: str, over: Ref, var: str, *nodes: Node, parallel: bool = False) -> Node:
    # iterate_over es una expresión de texto ({{$var:...}}); en local se resuelve a la lista.
    return Node(name, "loop", None, {}, list(nodes), extra={"iterate_over": Raw(over), "loop_variable": var, "execute_in_parallel": parallel})


def Agent(name: str, event: str, prompt_md: str | Raw, config: dict | None = None, initial_message: str | list | None = None, model: str | None = None, signals: list[str] | None = None) -> Node:
    return Node(name, "agent", event, dict(config or {}), [], prompt_md=prompt_md, initial_message=initial_message, model=model, signals=list(signals or []))


def Tool(name: str, description: str, params: list[dict], *children: Node, message: str | None = None, expose: list[str] | None = None) -> Node:
    """params: [{"name","description","required"?, "example"?}]"""
    fn = {
        "description": P(description),
        "parameters": [
            {"name": p["name"], "description": P(p["description"]), "required": p.get("required", False), "example": p.get("example", "")}
            for p in params
        ],
        "message": {"type": "fixed", "message": P(message)} if message else {"type": "none"},
    }
    return Node(name, "tool", None, {}, list(children), extra={"function": fn}, expose=expose)


@dataclass
class WorkflowSpec:
    key: str  # nombre lógico estable (clave en deploy-state.json)
    name: str  # nombre visible en la plataforma
    icon: str
    trigger: Node
    variables: dict[str, str] = field(default_factory=dict)  # variables de workflow (valor por defecto)
    hidden_variables: set[str] = field(default_factory=set)
    description: str = ""

    def nodes(self) -> list[Node]:
        return list(self.trigger.walk())
