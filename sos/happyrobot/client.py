"""HTTP base + sub-clientes por área (twin, workflows, voice, signals, runs).

Solo usa `urllib` para no exigir dependencias. Auth: `Authorization: Bearer <key>`
(único formato que acepta la plataforma).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..settings import Settings


class HappyRobotError(RuntimeError):
    def __init__(self, status: int, method: str, path: str, body: Any):
        self.status = status
        self.body = body
        msg = body.get("message") if isinstance(body, dict) else body
        super().__init__(f"{method} {path} -> {status}: {msg}")


class HappyRobotClient:
    def __init__(self, settings: Settings | None = None, timeout: int = 60):
        self.settings = settings or Settings.from_env()
        self.timeout = timeout
        self.twin = TwinAPI(self)
        self.workflows = WorkflowsAPI(self)
        self.versions = VersionsAPI(self)
        self.voice = VoiceAPI(self)
        self.signals = SignalsAPI(self)
        self.runs = RunsAPI(self)

    # -- transporte -----------------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        params: dict[str, Any] | None = None,
        base: str | None = None,
    ) -> Any:
        url = (base or self.settings.api_base) + path
        if params:
            url += "?" + urllib.parse.urlencode(
                {k: v for k, v in params.items() if v is not None}
            )
        # La API rechaza POST/PUT/PATCH/DELETE sin cuerpo con Content-Type JSON → enviamos {}.
        if body is None and method in ("POST", "PUT", "PATCH", "DELETE"):
            body = {}
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                parsed = json.loads(raw)
            except ValueError:
                parsed = raw.decode(errors="replace")
            raise HappyRobotError(exc.code, method, path, parsed) from None
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return raw.decode(errors="replace")

    def get(self, path: str, **params: Any) -> Any:
        return self.request("GET", path, params=params or None)

    def post(self, path: str, body: Any = None, **params: Any) -> Any:
        return self.request("POST", path, body=body, params=params or None)

    def put(self, path: str, body: Any = None) -> Any:
        return self.request("PUT", path, body=body)

    def patch(self, path: str, body: Any = None) -> Any:
        return self.request("PATCH", path, body=body)

    def delete(self, path: str, body: Any = None) -> Any:
        return self.request("DELETE", path, body=body)

    # -- utilidades -----------------------------------------------------------
    def describe_key(self) -> dict:
        return self.get("/api-key/describe")

    def org(self) -> dict:
        return self.get("/org/")["data"]


class _Sub:
    def __init__(self, c: HappyRobotClient):
        self.c = c


class TwinAPI(_Sub):
    """Base de datos Twin (Postgres gestionado). SQL libre vía /twin/sql."""

    def available(self) -> bool:
        try:
            self.schema()
            return True
        except HappyRobotError as exc:
            if exc.status == 404:
                return False
            raise

    def schema(self) -> list[dict]:
        return self.c.get("/twin/schema")

    def sql(self, sql: str) -> dict:
        return self.c.post("/twin/sql", {"sql": sql})

    def rows(self, sql: str) -> list[dict]:
        return self.sql(sql)["rows"]

    def create_table(self, table_name: str, columns: list[dict]) -> dict:
        return self.c.post("/twin/tables", {"tableName": table_name, "columns": columns})

    def drop_table(self, table_name: str) -> dict:
        return self.c.delete(f"/twin/tables/{table_name}")

    def table(self, table_name: str) -> dict:
        return self.c.get(f"/twin/tables/{table_name}")

    def insert(self, table_name: str, values: dict) -> dict:
        # La API exige valores string; serializamos jsonb/None aquí.
        return self.c.post(f"/twin/tables/{table_name}/rows", {"values": _stringify(values)})

    def update(self, table_name: str, primary_key: dict, updates: dict) -> dict:
        return self.c.patch(
            f"/twin/tables/{table_name}/rows",
            {"primaryKey": primary_key, "updates": updates},
        )

    def delete_rows(self, table_name: str, row_keys: list[dict]) -> dict:
        return self.c.delete(f"/twin/tables/{table_name}/rows", {"rowKeys": row_keys})

    def create_dump(self, workflow_id: str, table_name: str, include: list[str] | None = None, pk: str | None = None) -> dict:
        body: dict[str, Any] = {"workflowId": workflow_id, "tableName": table_name}
        if include:
            body["include"] = include
        if pk:
            body["pk"] = pk
        return self.c.post("/twin/dump", body)


class WorkflowsAPI(_Sub):
    def list(self) -> list[dict]:
        out: list[dict] = []
        page = 1
        while True:
            d = self.c.get("/workflows/", page=page, page_size=50)
            out += d["data"]
            if not d.get("pagination", {}).get("has_next_page"):
                return out
            page += 1

    def get(self, workflow_id: str) -> dict:
        return self.c.get(f"/workflows/{workflow_id}")

    def create(self, body: dict) -> dict:
        return self.c.post("/workflows/", body)

    def update(self, workflow_id: str, body: dict) -> dict:
        return self.c.patch(f"/workflows/{workflow_id}", body)

    def delete(self, workflow_id: str) -> Any:
        return self.c.delete(f"/workflows/{workflow_id}")

    def publish(self, workflow_id: str, environment: str = "production") -> Any:
        return self.c.post(f"/workflows/{workflow_id}/publish", {"environment": environment})

    def unpublish(self, workflow_id: str, environment: str = "production") -> Any:
        return self.c.post(f"/workflows/{workflow_id}/unpublish", {"environment": environment})

    def trigger(self, workflow_id: str, payload: dict, environment: str = "production") -> dict:
        return self.c.post(
            f"/workflows/{workflow_id}/runs", {"payload": payload, "environment": environment}
        )

    def runs(self, workflow_id: str, **params: Any) -> dict:
        return self.c.get(f"/workflows/{workflow_id}/runs", **params)

    def versions(self, workflow_id: str) -> list[dict]:
        d = self.c.get(f"/workflows/{workflow_id}/versions")
        return d["data"] if isinstance(d, dict) else d

    def variables(self, workflow_id: str) -> list[dict]:
        d = self.c.get(f"/workflows/{workflow_id}/variables")
        return d["data"] if isinstance(d, dict) else d

    def create_variable(self, workflow_id: str, key: str, value: str, hidden: bool = False) -> dict:
        return self.c.post(
            f"/workflows/{workflow_id}/variables",
            {
                "key": key,
                "value_production": value,
                "value_staging": value,
                "value_development": value,
                "is_hidden_in_ui": hidden,
            },
        )

    def update_variable(self, workflow_id: str, variable_id: str, value: str) -> dict:
        return self.c.patch(
            f"/workflows/{workflow_id}/variables/{variable_id}",
            {"value_production": value, "value_staging": value, "value_development": value},
        )


class VersionsAPI(_Sub):
    def get(self, version_id: str) -> dict:
        return self.c.get(f"/versions/{version_id}/")

    def nodes(self, version_id: str) -> list[dict]:
        d = self.c.get(f"/versions/{version_id}/nodes")
        return d["data"] if isinstance(d, dict) else d

    def node(self, version_id: str, node_id: str) -> dict:
        d = self.c.get(f"/versions/{version_id}/nodes/{node_id}")
        return d.get("data", d) if isinstance(d, dict) else d

    def add_nodes(self, version_id: str, nodes: list[dict]) -> Any:
        return self.c.post(f"/versions/{version_id}/nodes", {"nodes": nodes})

    def update_node(self, version_id: str, node_id: str, body: dict) -> Any:
        return self.c.put(f"/versions/{version_id}/nodes/{node_id}", body)

    def delete_node(self, version_id: str, node_id: str) -> Any:
        return self.c.delete(f"/versions/{version_id}/nodes/{node_id}")

    def available_vars(self, version_id: str, node_id: str) -> Any:
        return self.c.get(f"/versions/{version_id}/nodes/{node_id}/available-vars")

    def lock(self, version_id: str) -> Any:
        return self.c.post(f"/versions/{version_id}/lock")

    def unlock(self, version_id: str) -> Any:
        return self.c.post(f"/versions/{version_id}/unlock")

    def publish(self, version_id: str, environment: str = "production") -> Any:
        return self.c.post(f"/versions/{version_id}/publish", {"environment": environment})

    def unpublish(self, version_id: str, environment: str = "production") -> Any:
        return self.c.post(f"/versions/{version_id}/unpublish", {"environment": environment})

    def fork(self, version_id: str, name: str | None = None) -> Any:
        return self.c.post(f"/versions/{version_id}/fork", {"name": name} if name else {})

    def tool_result_generate(self, version_id: str, tool_id: str) -> Any:
        return self.c.post(f"/versions/{version_id}/tools/{tool_id}/tool-call-result/generate")

    def tool_result_inspect(self, version_id: str, tool_id: str) -> Any:
        return self.c.post(f"/versions/{version_id}/tools/{tool_id}/tool-call-result/inspect")

    def tool_result_visibility(self, version_id: str, tool_id: str, body: dict) -> Any:
        return self.c.put(f"/versions/{version_id}/tools/{tool_id}/tool-call-result/visibility", body)

    def test_node(self, version_id: str, node_id: str, body: dict | None = None) -> Any:
        return self.c.post(f"/versions/{version_id}/nodes/{node_id}/test", body or {})


class VoiceAPI(_Sub):
    def token(self, workflow_id: str, data: dict | None = None, env: str = "production", ttl: int | None = None) -> dict:
        body: dict[str, Any] = {"workflow_id": workflow_id, "env": env}
        if data:
            body["data"] = data
        if ttl:
            body["ttl_seconds"] = ttl
        return self.c.post("/voice/tokens/", body)

    def join(self, session_id: str, takeover: bool = False) -> dict:
        return self.c.post("/voice/tokens/", {"session_id": session_id, "should_takeover": takeover})

    def voices(self) -> Any:
        return self.c.get("/voices/")

    def realtime_token(self, channel: str, **ids: str) -> dict:
        return self.c.post("/realtime/tokens", {"channel": channel, **ids})


class SignalsAPI(_Sub):
    def publish(self, key: str, payload: dict, env: str = "production", metadata: dict | None = None) -> dict:
        body: dict[str, Any] = {"key": key, "payload": payload, "env": env}
        if metadata:
            body["metadata"] = metadata
        return self.c.post("/signals/", body)

    def schedule(self, key: str, payload: dict, delay_seconds: int, env: str = "production") -> dict:
        return self.c.post(
            "/signals/scheduled-signals",
            {"key": key, "payload": payload, "delay_seconds": delay_seconds, "env": env},
        )

    def keys(self) -> list[str]:
        return self.c.get("/signals/keys")["keys"]

    def add_key(self, node_id: str, key: str) -> dict:
        return self.c.post("/signals/keys", {"node_id": node_id, "key": key})


class RunsAPI(_Sub):
    def get(self, run_id: str) -> dict:
        return self.c.get(f"/runs/{run_id}")

    def nodes(self, run_id: str) -> Any:
        return self.c.get(f"/runs/{run_id}/nodes")

    def sessions(self, run_id: str) -> Any:
        return self.c.get(f"/runs/{run_id}/sessions")

    def cancel(self, run_id: str) -> Any:
        return self.c.post(f"/runs/{run_id}/cancel")

    def session_messages(self, session_id: str) -> Any:
        return self.c.get(f"/sessions/{session_id}/messages")


def _stringify(values: dict) -> dict[str, str]:
    """La API de filas exige strings: jsonb → json, bool → 'true', None → ''."""
    out: dict[str, str] = {}
    for k, v in values.items():
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = "true" if v else "false"
        elif isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = str(v)
    return out
