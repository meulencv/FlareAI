"""Aplica el esquema (idempotente) sobre cualquier backend: Twin o Postgres local."""

from __future__ import annotations

from ..db import Database
from .schema import TABLES, VIEWS, all_ddl


def migrate(db: Database, verbose: bool = True) -> None:
    for stmt in all_ddl():
        head = stmt.strip().split("\n", 1)[0][:80]
        try:
            db.sql(stmt)
            if verbose:
                print(f"  ok   {head}")
        except Exception as exc:  # noqa: BLE001 — mostramos la sentencia que falla
            print(f"  FAIL {head}\n       {exc}")
            raise
    if verbose:
        print(f"Esquema aplicado en [{db.name}]: {len(TABLES)} tablas, {len(VIEWS)} vistas.")


def status(db: Database) -> None:
    have = {r["table_name"] for r in db.rows(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")}
    for t in TABLES:
        print(f"  {'✓' if t.name in have else '✗'} tabla {t.name}")
    for v in VIEWS:
        print(f"  {'✓' if v.name in have else '✗'} vista {v.name}")


def drop_all(db: Database) -> None:
    """Destructivo: elimina todo el esquema (solo para resetear la demo)."""
    for v in VIEWS:
        db.sql(f"DROP VIEW IF EXISTS {v.name}")
    for t in reversed(TABLES):
        db.sql(f"DROP TABLE IF EXISTS {t.name} CASCADE")
