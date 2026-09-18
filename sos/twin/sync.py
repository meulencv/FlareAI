"""Copia los datos de referencia (config, assets, contacts, resources) de un backend a otro.

Uso típico: `python -m sos twin sync-to-twin` cuando Twin esté provisionado, para llevar lo que
ya está cargado en el Postgres local. Los datos operativos (incidentes...) no se copian: se
regeneran con el simulador.
"""

from __future__ import annotations

import json

from ..db import Database

TABLES = ["config", "assets", "contacts", "resources"]
CONFLICT = {"config": "key", "assets": "ref", "contacts": "ref", "resources": "ref"}


def _lit(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def sync_reference_data(src: Database, dst: Database) -> dict[str, int]:
    counts = {}
    for t in TABLES:
        rows = src.rows(f"SELECT * FROM {t}")
        n = 0
        for r in rows:
            cols = [c for c in r if c not in ("created_at", "updated_at")]
            vals = [r[c] for c in cols]
            if t == "config":
                vals = [json.dumps(v) if c == "value" and not isinstance(v, (dict, list)) else v for c, v in zip(cols, vals)]
                lits = [("'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb") if c == "value" else _lit(v) for c, v in zip(cols, vals)]
            else:
                lits = [_lit(v) for v in vals]
            sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != CONFLICT[t])
            dst.sql(f"INSERT INTO {t} ({', '.join(cols)}) VALUES ({', '.join(lits)}) ON CONFLICT ({CONFLICT[t]}) DO UPDATE SET {sets}")
            n += 1
        counts[t] = n
    return counts
