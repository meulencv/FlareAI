"""Crea/actualiza workflows en HappyRobot a partir de `WorkflowSpec`s.

Estrategia: los nodos se crean **uno a uno en orden DFS**. Como las variables siempre
fluyen aguas abajo, al crear un nodo ya conocemos los ids de todos los nodos a los que
puede referenciar, así que las `Ref` se resuelven en una sola pasada. El trigger va
primero: al añadir un trigger la API borra todos los nodos anteriores de la versión,
lo que convierte cada deploy en un reemplazo limpio.

Ciclo de vida por workflow: (unpublish → unlock) → nodos → variables → publish.
El resultado (ids, slugs, urls de hook) se guarda en `deploy-state.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..happyrobot import HappyRobotClient, HappyRobotError
from ..settings import STATE_FILE
from ._builder import EV, Node, WorkflowSpec, render


def load_state(path: Path = STATE_FILE) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"workflows": {}}


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


class Deployer:
    def __init__(self, client: HappyRobotClient, verbose: bool = True):
        self.c = client
        self.verbose = verbose
        self.state = load_state()

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    # ---- fase 1: asegurar que existen los workflows (para poder referenciarlos) --------------
    def ensure_workflow(self, spec: WorkflowSpec) -> dict:
        entry = self.state["workflows"].get(spec.key)
        existing = None
        if entry:
            try:
                existing = self.c.workflows.get(entry["id"])
            except HappyRobotError as exc:
                if exc.status != 404:
                    raise
        if existing is None:
            for wf in self.c.workflows.list():
                if wf["name"] == spec.name:
                    existing = self.c.workflows.get(wf["id"])
                    break
        if existing is None:
            existing = self.c.workflows.create({"name": spec.name, "icon": spec.icon, "version": {"name": "v1"}})
            self.log(f"  + creado workflow {spec.name} ({existing['id']})")
        data = existing.get("data", existing)
        version = data.get("latest_version") or {}
        entry = {
            **(entry or {}),  # conserva nodes/published del último build
            "id": data["id"],
            "slug": data["slug"],
            "name": spec.name,
            "version_id": version.get("id"),
            "hook_url": f"{self.c.settings.hooks_base}/{data['slug']}",
            "published": bool(version.get("is_published")),
        }
        self.state["workflows"][spec.key] = entry
        return entry

    # ---- fase 2: nodos ------------------------------------------------------------------------
    def build(self, spec: WorkflowSpec) -> dict:
        entry = self.state["workflows"][spec.key]
        wid, vid = entry["id"], entry["version_id"]
        self.log(f"▶ {spec.name}")
        # desbloquear
        try:
            self.c.workflows.unpublish(wid)
        except HappyRobotError:
            pass
        try:
            self.c.versions.unlock(vid)
        except HappyRobotError:
            pass

        ids: dict[str, str] = {}  # nombre lógico → node id
        workflow_ids = {k: v["id"] for k, v in self.state["workflows"].items()}
        workflow_names = {k: v["name"] for k, v in self.state["workflows"].items()}

        def resolve_workflow_refs(obj):
            if isinstance(obj, dict):
                if "__workflow__" in obj:
                    key = obj["__workflow__"]
                    return {"type": "static", "static": {"id": workflow_ids[key], "name": workflow_names[key]}}
                return {k: resolve_workflow_refs(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [resolve_workflow_refs(v) for v in obj]
            return obj

        def create(node: Node, parent_id: str | None) -> str:
            if node.name in ids:
                raise ValueError(f"nombre de nodo duplicado: {node.name}")
            body: dict = {"type": node.type, "name": node.name}
            if node.event:
                body["event_id"] = EV[node.event]
            if parent_id:
                body["parent_node_id"] = parent_id
            cfg = resolve_workflow_refs(render(node.config, ids))
            if node.type in ("trigger", "action", "agent"):
                body["configuration"] = cfg
            if node.type == "trigger" and node.outputs:
                body["webhook_payload"] = node.outputs
            if node.type == "agent":
                body["prompt"] = {"prompt_md": render(node.prompt_md, ids)}
            for k, v in node.extra.items():
                body[k] = render(v, ids)
            res = self.c.versions.add_nodes(vid, [body])
            nid = res["data"][0]["id"]
            ids[node.name] = nid
            self.log(f"    · {node.type:9} {node.name}")

            if node.outputs and node.type != "trigger":
                self.c.put(f"/versions/{vid}/nodes/{nid}/custom-output", {"data": node.outputs})
            if node.type == "trigger" and node.outputs:
                # el sample del trigger también como salida (evita 'missing_variables' al publicar)
                self.c.put(f"/versions/{vid}/nodes/{nid}/custom-output", {"data": node.outputs})

            if node.type == "path":
                # Un path creado solo trae hijos por defecto ("Path 1", "Fallback"); los quitamos
                # para que solo queden las ramas declaradas en el spec.
                for auto in self.c.versions.nodes(vid):
                    if auto.get("parent_id") == nid:
                        self.c.versions.delete_node(vid, auto["id"])

            if node.type == "agent":
                prompt = next(n for n in self.c.versions.nodes(vid) if n.get("parent_id") == nid and n["type"] == "prompt")
                ids[f"{node.name}.prompt"] = prompt["id"]
                pbody: dict = {"type": "prompt", "prompt_md": render(node.prompt_md, ids)}
                if node.initial_message is not None:
                    im = node.initial_message
                    pbody["initial_message"] = render(im, ids) if isinstance(im, list) else im
                if node.model:
                    pbody["model"] = {"type": "static", "static": {"id": node.model, "name": node.model}}
                self.c.versions.update_node(vid, prompt["id"], pbody)
                for key in node.signals:
                    self.c.signals.add_key(nid, key)

            for child in node.children:
                create(child, nid)

            if node.type == "tool":
                gen = self.c.versions.tool_result_generate(vid, nid)["data"]
                for tn in gen.get("nodes", []):
                    fields = [f["path"] for f in tn.get("fields", [])]
                    exposed = fields if node.expose is None else [f for f in fields if f in node.expose]
                    self.c.versions.tool_result_visibility(vid, nid, {"node_id": tn["node_id"], "exposed_fields": exposed})
            return nid

        create(spec.trigger, None)

        # variables de workflow
        self.sync_variables(wid, spec)

        pub = self.c.workflows.publish(wid)
        missing = pub.get("missing_variables") or []
        if missing:
            self.log(f"    ! publish con missing_variables en: {[m['node_name'] for m in missing]}")
        entry["nodes"] = ids
        entry["published"] = True
        save_state(self.state)
        self.log(f"  ✓ publicado {spec.name} — hook: {entry['hook_url']}")
        return entry

    def sync_variables(self, wid: str, spec: WorkflowSpec) -> None:
        wanted = {
            "HAPPYROBOT_API_KEY": (self.c.settings.api_key, True),
            "HAPPYROBOT_API_BASE": (self.c.settings.api_base, False),
        }
        for k, v in spec.variables.items():
            wanted[k] = (v, k in spec.hidden_variables)
        existing = {v["key"]: v for v in self.c.workflows.variables(wid)}
        for key, (value, hidden) in wanted.items():
            if key in existing:
                if existing[key].get("value_production") != value:
                    self.c.workflows.update_variable(wid, existing[key]["id"], value)
            else:
                self.c.workflows.create_variable(wid, key, value, hidden=hidden)

    # ---- orquestación ---------------------------------------------------------------------------
    def deploy(self, specs: list[WorkflowSpec], only: set[str] | None = None) -> None:
        for spec in specs:
            self.ensure_workflow(spec)
        save_state(self.state)
        for spec in specs:
            if only and spec.key not in only:
                continue
            self.build(spec)

    def destroy(self, keys: list[str]) -> None:
        for key in keys:
            entry = self.state["workflows"].pop(key, None)
            if entry:
                try:
                    self.c.workflows.delete(entry["id"])
                    self.log(f"  - borrado {entry['name']}")
                except HappyRobotError as exc:
                    self.log(f"  ! no se pudo borrar {entry['name']}: {exc}")
        save_state(self.state)
