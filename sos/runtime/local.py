"""Ejecuta un `WorkflowSpec` en local reproduciendo la semántica observada de HappyRobot.

Semántica reproducida (ver vault → "Formato de nodos por API"):
- Las variables llegan a los nodos como **texto**: números → "39.7", booleanos → "true"/"false",
  listas/objetos → JSON. Rutas con punto (`rows.0.id`) acceden a campos anidados.
- Python Sandbox: `input_data` (dict de strings) → `output`.
- Query Twin SQL → `{"rows": [...]}`; Write to Twin → upsert por columna primaria.
- Paths: se evalúan las ramas condicionales en orden; si ninguna cumple, la de fallback.
- Call Workflow: ejecuta el otro spec (síncrono aquí, aunque sea fire & forget).
- Agent: delega en una política (`agents.py`) que decide qué tools invocar; cada tool ejecuta
  sus nodos hijos con los parámetros como variables del nodo tool.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from ..db import Database
from ..workflows._builder import Node, Raw, Ref, WorkflowSpec

AgentPolicy = Callable[["LocalRuntime", Node, "RunContext"], list[tuple[str, dict]]]


@dataclass
class RunResult:
    workflow: str
    run_id: str
    outputs: dict[str, Any]
    log: list[str]
    children: list["RunResult"] = field(default_factory=list)
    error: str | None = None

    def find(self, node: str) -> Any:
        return self.outputs.get(node)


@dataclass
class RunContext:
    spec: WorkflowSpec
    run_id: str
    outputs: dict[str, Any] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)
    result: RunResult | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def dig(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if isinstance(cur, str):
            try:
                cur = json.loads(cur)
            except ValueError:
                return None
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


class LocalRuntime:
    def __init__(self, db: Database, specs: dict[str, WorkflowSpec], policies: dict[str, AgentPolicy] | None = None,
                 verbose: bool = False, http: Callable[[str, str, dict, str | None], dict] | None = None):
        self.db = db
        self.specs = specs
        self.policies = policies or {}
        self.verbose = verbose
        self.http = http or self._http
        self.signals: list[dict] = []  # señales publicadas (simuladas)

    # ---- API pública --------------------------------------------------------------------------
    def run(self, key: str, payload: dict) -> RunResult:
        spec = self.specs[key]
        ctx = RunContext(spec, str(uuid.uuid4()))
        ctx.result = RunResult(spec.key, ctx.run_id, ctx.outputs, ctx.log)
        ctx.outputs[spec.trigger.name] = {k: to_text(v) for k, v in payload.items()}
        self._log(ctx, f"▶ {spec.key} run={ctx.run_id[:8]} payload={json.dumps(payload, ensure_ascii=False)[:160]}")
        try:
            for child in spec.trigger.children:
                self._exec(child, ctx)
        except Exception as exc:  # noqa: BLE001
            ctx.result.error = f"{type(exc).__name__}: {exc}"
            self._log(ctx, f"✗ error: {ctx.result.error}")
            raise
        return ctx.result

    # ---- resolución de variables --------------------------------------------------------------
    def value(self, ref: Ref, ctx: RunContext) -> Any:
        if ref.node == "$current":
            return {"run_id": ctx.run_id, "use_case_id": ctx.spec.key, "use_case_name": ctx.spec.name,
                    "run_url": f"local://{ctx.spec.key}/{ctx.run_id}"}.get(ref.field, "")
        if ref.node == "$time":
            return _now_iso() if ref.field == "now_iso" else datetime.now().strftime("%A, %B %d, %Y %H:%M")
        if ref.node == "$vars":
            return ctx.spec.variables.get(ref.field, "")
        out = ctx.outputs.get(ref.node)
        if out is None:
            return ""
        return dig(out, ref.field)

    def text(self, obj: Any, ctx: RunContext) -> str:
        """Paragraph / Raw / str / Ref → texto ya resuelto."""
        if isinstance(obj, Ref):
            return to_text(self.value(obj, ctx))
        if isinstance(obj, Raw):
            return "".join(self.text(p, ctx) for p in obj.parts)
        if isinstance(obj, str):
            return obj
        if isinstance(obj, list):  # paragraph[]
            out = []
            for para in obj:
                if isinstance(para, dict) and para.get("type") == "paragraph":
                    for ch in para.get("children", []):
                        if isinstance(ch, Ref):
                            out.append(to_text(self.value(ch, ctx)))
                        elif isinstance(ch, dict) and ch.get("type") == "variable":
                            out.append(to_text(self.value(Ref(ch["group_id"], ch["variable_id"]), ctx)))
                        elif isinstance(ch, dict):
                            out.append(ch.get("text", ""))
                        else:
                            out.append(str(ch))
                else:
                    out.append(self.text(para, ctx))
            return "".join(out)
        if isinstance(obj, dict):
            return json.dumps(obj)
        return to_text(obj)

    def kv(self, pairs: list[dict], ctx: RunContext) -> dict[str, str]:
        return {p["key"]: self.text(p["value"], ctx) for p in pairs or []}

    # ---- ejecución ------------------------------------------------------------------------------
    def _log(self, ctx: RunContext, msg: str) -> None:
        ctx.log.append(msg)
        if self.verbose:
            print("   " + msg)

    def _exec(self, node: Node, ctx: RunContext) -> Any:
        handler = getattr(self, f"_n_{node.type}", None)
        if node.type == "action":
            handler = getattr(self, f"_a_{node.event}", None)
        if handler is None:
            raise NotImplementedError(f"nodo no soportado en local: {node.type}/{node.event}")
        out = handler(node, ctx)
        ctx.outputs[node.name] = out
        self._log(ctx, f"· {node.name} → {json.dumps(out, ensure_ascii=False, default=str)[:140]}")
        if node.type not in ("path", "loop", "agent", "tool", "condition"):
            for child in node.children:
                self._exec(child, ctx)
        return out

    # triggers no se ejecutan (su salida es el payload)
    def _a_python(self, node: Node, ctx: RunContext) -> Any:
        input_data = self.kv(node.config.get("input_data", []), ctx)
        ns: dict[str, Any] = {"input_data": input_data}
        exec(node.config["code"], ns)  # noqa: S102 — es el mismo código que corre en el sandbox
        return ns.get("output", {})

    def _a_twin_sql(self, node: Node, ctx: RunContext) -> Any:
        sql = self.text(node.config["sql"], ctx)
        rows = self.db.rows(sql)
        return {"rows": rows[: int(node.config.get("maxRows") or 100)]}

    def _a_twin_write(self, node: Node, ctx: RunContext) -> Any:
        table = node.config["tableName"]
        cols, vals, pk = [], [], None
        for cv in node.config["columnValues"]:
            raw = self.text(cv["value"], ctx)
            typ = cv["type"]
            if raw == "" and typ != "text":
                lit = "NULL"
            elif typ in ("float8", "int8"):
                lit = repr(float(raw)) if typ == "float8" else str(int(float(raw)))
            elif typ == "boolean":
                lit = "true" if raw.lower() in ("true", "1", "yes") else "false"
            elif typ == "jsonb":
                lit = "'" + raw.replace("'", "''") + "'::jsonb"
            else:
                lit = "'" + raw.replace("'", "''") + "'"
                if typ in ("uuid", "timestamp"):
                    lit += f"::{typ}"
            cols.append(cv["columnName"])
            vals.append(lit)
            if cv.get("isPrimary"):
                pk = cv["columnName"]
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(vals)})"
        if pk:
            sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != pk)
            sql += f" ON CONFLICT ({pk}) DO UPDATE SET {sets}" if sets else f" ON CONFLICT ({pk}) DO NOTHING"
        self.db.sql(sql)
        return {"ok": True, "table": table}

    def _a_twin_read(self, node: Node, ctx: RunContext) -> Any:
        ops = {"equals": "=", "not_equal": "<>", "greater_than": ">", "less_than": "<", "greater_or_equal": ">=", "less_or_equal": "<=", "contains": "ILIKE"}
        where = []
        for f in node.config.get("filters", []):
            v = self.text(f["value"], ctx).replace("'", "''")
            v = f"'%{v}%'" if f["operator"] == "contains" else f"'{v}'"
            where.append(f"{f['column']} {ops[f['operator']]} {v}")
        sql = f"SELECT * FROM {node.config['tableName']}" + (" WHERE " + " AND ".join(where) if where else "")
        if node.config.get("orderByColumn"):
            sql += f" ORDER BY {node.config['orderByColumn']} {node.config.get('orderByDirection', 'asc')}"
        sql += f" LIMIT {int(self.text(node.config.get('limit', '100'), ctx) or 100)}"
        return {"rows": self.db.rows(sql)}

    def _a_http_post(self, node: Node, ctx: RunContext) -> Any:
        url = self.text(node.config["url"], ctx)
        headers = {h["key"]: self.text(h["value"], ctx) for h in node.config.get("headers", [])}
        body = self.text(node.config["body"]["raw"], ctx)
        return self.http("POST", url, headers, body)

    def _a_http_get(self, node: Node, ctx: RunContext) -> Any:
        url = self.text(node.config["url"], ctx)
        params = {p["key"]: self.text(p["value"], ctx) for p in node.config.get("params", [])}
        if params:
            from urllib.parse import urlencode

            url += ("&" if "?" in url else "?") + urlencode(params)
        headers = {h["key"]: self.text(h["value"], ctx) for h in node.config.get("headers", [])}
        return self.http("GET", url, headers, None)

    def _a_call_workflow(self, node: Node, ctx: RunContext) -> Any:
        key = node.config["to_workflow"]["__workflow__"]
        data = self.kv(node.config.get("data", []), ctx)
        child = self.run(key, data)
        ctx.result.children.append(child)
        return {"call_workflow_data": {"status": "completed", "child_run_id": child.run_id, "child_use_case_id": key}}

    def _a_sleep(self, node: Node, ctx: RunContext) -> Any:
        return {"slept": True}

    def _n_path(self, node: Node, ctx: RunContext) -> Any:
        chosen = None
        for branch in node.children:
            if branch.extra.get("type_of_condition") == "conditional" and self._cond(branch, ctx):
                chosen = branch
                break
        if chosen is None:
            chosen = next((b for b in node.children if b.extra.get("type_of_condition") == "fallback"), None)
        if chosen is None:
            return {"path": None}
        ctx.outputs[chosen.name] = {"taken": True}
        for child in chosen.children:
            self._exec(child, ctx)
        return {"path": chosen.name}

    def _cond(self, branch: Node, ctx: RunContext) -> bool:
        for cond in branch.extra.get("conditions", []):
            for or_ in cond["ors"]:
                ok = True
                for and_ in or_["ands"]:
                    left = to_text(self.value(and_["field"], ctx))
                    right = self.text(and_.get("value", ""), ctx) if "value" in and_ else ""
                    ok = ok and _compare(and_["condition"], left, right)
                if ok:
                    return True
        return False

    def _n_loop(self, node: Node, ctx: RunContext) -> Any:
        over = node.extra["iterate_over"]
        if isinstance(over, Raw) and len(over.parts) == 1 and isinstance(over.parts[0], Ref):
            items = self.value(over.parts[0], ctx)
        else:
            items = self.text(over, ctx)
        if isinstance(items, str):
            try:
                items = json.loads(items) if items else []
            except ValueError:
                items = []
        var = node.extra.get("loop_variable", "item")
        for i, item in enumerate(items or []):
            ctx.outputs[node.name] = {var: item, "iteration_index": i}
            for child in node.children:
                self._exec(child, ctx)
        return {"iterations": len(items or [])}

    def _n_agent(self, node: Node, ctx: RunContext) -> Any:
        policy = self.policies.get(f"{ctx.spec.key}.{node.name}") or self.policies.get(node.name)
        if policy is None:
            raise NotImplementedError(f"sin política local para el agente {ctx.spec.key}.{node.name}")
        calls = policy(self, node, ctx)
        events = []
        for tool_name, params in calls:
            tool = next((t for t in node.children if t.name == tool_name), None)
            if tool is None:
                raise KeyError(f"tool desconocida {tool_name}")
            ctx.outputs[tool.name] = {k: to_text(v) for k, v in params.items()}
            self._log(ctx, f"  ⚙ tool {tool_name}({json.dumps(params, ensure_ascii=False)[:120]})")
            for child in tool.children:
                self._exec(child, ctx)
            events.append({"action": tool_name, "arguments": params})
        return {"name": node.name, "steps": len(calls), "events": events}

    def _n_tool(self, node: Node, ctx: RunContext) -> Any:  # nunca se ejecuta directamente
        return {"skipped": True}

    def _n_condition(self, node: Node, ctx: RunContext) -> Any:
        return {"skipped": True}

    # ---- HTTP real (para feeders: Open-Meteo, FIRMS) -------------------------------------------
    @staticmethod
    def _http(method: str, url: str, headers: dict, body: str | None) -> dict:
        import urllib.request

        req = urllib.request.Request(url, data=body.encode() if body else None, method=method, headers={"User-Agent": "sos-local", **headers})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode(errors="replace")
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {"data": parsed}
        except ValueError:
            return {"body": raw}


def _compare(op: str, left: str, right: str) -> bool:
    def num(s: str) -> float | None:
        try:
            return float(s)
        except (TypeError, ValueError):
            return None

    if op == "text_equals":
        return left == right
    if op == "text_not_equals":
        return left != right
    if op == "text_contains":
        return right in left
    if op == "text_not_contains":
        return right not in left
    if op == "boolean_true":
        return left.lower() in ("true", "1", "yes")
    if op == "boolean_false":
        return left.lower() not in ("true", "1", "yes")
    if op == "is_empty":
        return left == ""
    l, r = num(left), num(right)
    if l is None or r is None:
        return False
    return {"number_equals": l == r, "number_not_equals": l != r, "number_greater_than": l > r,
            "number_greater_than_or_equal_to": l >= r, "number_less_than": l < r, "number_less_than_or_equal_to": l <= r}.get(op, False)


_ = re  # (reservado para futuras expresiones de loop)
