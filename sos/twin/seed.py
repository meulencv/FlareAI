"""Carga config y datos del escenario en Twin (idempotente por `ref` / `key`)."""

from __future__ import annotations

import json
from pathlib import Path

from ..db import Database
from ..settings import CONFIG_DIR


class _JsonValue:
    """Marca un valor (incluso escalar) para escribirlo como jsonb."""

    def __init__(self, v):
        self.v = v


def _lit(v) -> str:
    """Literal SQL seguro para valores simples y jsonb."""
    if isinstance(v, _JsonValue):
        return "'" + json.dumps(v.v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def _upsert(table: str, row: dict, conflict: str, update_cols: list[str]) -> str:
    cols = ", ".join(row)
    vals = ", ".join(_lit(v) for v in row.values())
    sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)
    return f"INSERT INTO {table} ({cols}) VALUES ({vals}) ON CONFLICT ({conflict}) DO UPDATE SET {sets}"


def load_weights(path: Path = CONFIG_DIR / "weights.json") -> dict:
    raw = json.loads(path.read_text())
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def seed_config(db: Database, weights: dict | None = None) -> int:
    weights = weights or load_weights()
    n = 0
    for key, entry in weights.items():
        db.sql(
            _upsert(
                "config",
                {"key": key, "value": _JsonValue(entry["value"]), "description": entry.get("description", "")},
                "key",
                ["value", "description", "updated_at"],
            ).replace("updated_at = EXCLUDED.updated_at", "updated_at = now()")
        )
        n += 1
    return n


def seed_scenario(db: Database, name: str = "demo_es") -> dict[str, int]:
    data = json.loads((CONFIG_DIR / "scenarios" / f"{name}.json").read_text())
    counts = {"assets": 0, "contacts": 0, "resources": 0}

    for a in data["assets"]:
        row = {
            "ref": a["key"], "name": a["name"], "kind": a["kind"], "lat": a["lat"], "lon": a["lon"],
            "population": a.get("population", 0), "insured_value": a.get("insured_value", 0),
            "carbon_credit_value": a.get("carbon_credit_value", 0), "hazard_class": a.get("hazard_class"),
            "priority_weight": a.get("priority_weight", 1), "metadata": a.get("metadata", {}),
        }
        db.sql(_upsert("assets", row, "ref", [c for c in row if c != "ref"]))
        counts["assets"] += 1

    for c in data["contacts"]:
        row = {
            "ref": c["key"], "name": c["name"], "role": c["role"], "phone": c.get("phone"),
            "language": c.get("language", "es"), "priority": c.get("priority", 100), "notes": c.get("notes"),
        }
        sql = _upsert("contacts", row, "ref", [k for k in row if k != "ref"])
        if c.get("asset"):
            # asset_id se resuelve por subconsulta para no depender de UUIDs
            sql = sql.replace(
                f"({', '.join(row)})", f"({', '.join(row)}, asset_id)", 1
            ).replace(
                ") ON CONFLICT", f", (SELECT id FROM assets WHERE ref = {_lit(c['asset'])})) ON CONFLICT", 1
            ) + ", asset_id = EXCLUDED.asset_id"
        db.sql(sql)
        counts["contacts"] += 1

    for r in data["resources"]:
        row = {
            "ref": r["key"], "name": r["name"], "kind": r["kind"], "capabilities": r.get("capabilities", []),
            "lat": r["lat"], "lon": r["lon"], "status": r.get("status", "available"),
            "metadata": r.get("metadata", {}),
        }
        sql = _upsert("resources", row, "ref", [k for k in row if k != "ref"])
        if r.get("contact"):
            sql = sql.replace(
                f"({', '.join(row)})", f"({', '.join(row)}, contact_id)", 1
            ).replace(
                ") ON CONFLICT", f", (SELECT id FROM contacts WHERE ref = {_lit(r['contact'])})) ON CONFLICT", 1
            ) + ", contact_id = EXCLUDED.contact_id"
        db.sql(sql)
        counts["resources"] += 1

    return counts


def reset_operational_data(db: Database) -> None:
    """Borra incidentes/evidencias/acciones/planes/meteo (deja activos, contactos, medios, config)."""
    for t in ("actions", "plans", "weather_observations", "evidence", "incidents"):
        db.sql(f"DELETE FROM {t}")
    db.sql("UPDATE resources SET status = 'available', assigned_incident_id = NULL, eta_min = NULL")
