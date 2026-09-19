from __future__ import annotations

import json
import os
from typing import Any, Protocol


class Database(Protocol):
    name: str

    def sql(self, sql: str) -> dict: ...

    def rows(self, sql: str) -> list[dict]: ...

    def close(self) -> None: ...


def _jsonable(v: Any) -> Any:
    """Normaliza tipos de psycopg (datetime, Decimal, UUID) a lo que devuelve la API de Twin."""
    import datetime as dt
    import decimal
    import uuid

    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_jsonable(x) for x in v]
    return v


class TwinDatabase:
    name = "twin"

    def __init__(self, client=None):
        from ..happyrobot import HappyRobotClient

        self.client = client or HappyRobotClient()

    def sql(self, sql: str) -> dict:
        return self.client.twin.sql(sql)

    def rows(self, sql: str) -> list[dict]:
        return self.sql(sql)["rows"]

    def close(self) -> None:
        pass


class LocalDatabase:
    name = "local"

    def __init__(self, dsn: str | None = None):
        import psycopg
        from psycopg.rows import dict_row

        from .local_pg import ensure_running

        self.dsn = dsn or ensure_running()
        self.conn = psycopg.connect(self.dsn, row_factory=dict_row, autocommit=True)

    def sql(self, sql: str) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(sql)
            command = (cur.statusmessage or "").split(" ")[0]
            rows = [ _jsonable(dict(r)) for r in cur.fetchall()] if cur.description else []
            return {"command": command, "rowCount": cur.rowcount if cur.rowcount >= 0 else None, "rows": rows,
                    "fields": [{"name": d.name, "dataTypeId": d.type_code} for d in (cur.description or [])],
                    "truncated": False, "truncationReason": None, "returnedRows": len(rows)}

    def rows(self, sql: str) -> list[dict]:
        return self.sql(sql)["rows"]

    def close(self) -> None:
        self.conn.close()


def twin_usable(client=None) -> bool:
    from ..happyrobot import HappyRobotClient, HappyRobotError

    try:
        c = client or HappyRobotClient()
        c.twin.sql("SELECT 1")
        return True
    except (HappyRobotError, SystemExit):
        return False


def get_database(mode: str | None = None, client=None) -> Database:
    mode = (mode or os.environ.get("SOS_DB") or "auto").lower()
    if mode == "twin":
        return TwinDatabase(client)
    if mode == "local":
        return LocalDatabase()
    return TwinDatabase(client) if twin_usable(client) else LocalDatabase()


def dumps(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False)
