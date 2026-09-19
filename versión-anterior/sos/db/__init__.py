"""Acceso a la base de datos con la misma interfaz que Twin (`sql(...) → {rows, rowCount, command}`).

Backends:
  - twin   → API pública de HappyRobot (`POST /twin/sql`).
  - local  → Postgres embebido en `.local/pg` (mismo dialecto: el SQL es idéntico).

Selección: variable de entorno `SOS_DB` = twin | local | auto (por defecto auto: Twin si está
provisionado y la key tiene permiso, si no local).
"""

from .base import Database, get_database

__all__ = ["Database", "get_database"]
