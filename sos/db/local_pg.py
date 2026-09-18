"""Postgres embebido dentro del proyecto (`.local/pg`), sin instalar nada fuera de la carpeta.

Binarios: zonky embedded-postgres (darwin-arm64) descomprimidos en `.local/pg/dist`.
Datos: `.local/pg/data`. Socket/puerto: 127.0.0.1:54329. Todo está en .gitignore.

    python -m sos db start | stop | status
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

from ..settings import REPO_ROOT

PG_DIR = REPO_ROOT / ".local" / "pg"
BIN = PG_DIR / "dist" / "bin"
DATA = PG_DIR / "data"
LOG = PG_DIR / "postgres.log"
PORT = int(os.environ.get("SOS_PG_PORT", "54329"))
DBNAME = "sos"
USER = "sos"
DSN = f"postgresql://{USER}@127.0.0.1:{PORT}/{DBNAME}"


def _port_open() -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def installed() -> bool:
    return (BIN / "postgres").exists()


def init() -> None:
    if DATA.exists():
        return
    DATA.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(BIN / "initdb"), "-D", str(DATA), "-U", USER, "--auth=trust", "-E", "UTF8", "--no-locale"],
                   check=True, capture_output=True)


def start() -> str:
    if not installed():
        raise SystemExit("Postgres embebido no encontrado en .local/pg/dist (ver vault → Base de datos local).")
    init()
    if not _port_open():
        subprocess.run([str(BIN / "pg_ctl"), "-D", str(DATA), "-l", str(LOG), "-o", f"-p {PORT} -c listen_addresses=127.0.0.1 -k {PG_DIR}",
                        "-w", "start"], check=True, capture_output=True)
        for _ in range(50):
            if _port_open():
                break
            time.sleep(0.1)
    # base de datos de trabajo (el bundle no trae psql/createdb: usamos psycopg)
    import psycopg

    with psycopg.connect(f"postgresql://{USER}@127.0.0.1:{PORT}/postgres", autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DBNAME,)).fetchone()
        if not exists:
            conn.execute(f"CREATE DATABASE {DBNAME}")
    return DSN


def stop() -> None:
    if DATA.exists() and _port_open():
        subprocess.run([str(BIN / "pg_ctl"), "-D", str(DATA), "-m", "fast", "stop"], capture_output=True)


def status() -> str:
    if not installed():
        return "no instalado"
    return f"running en 127.0.0.1:{PORT}" if _port_open() else "parado"


def ensure_running() -> str:
    return start()
