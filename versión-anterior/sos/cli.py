"""CLI: python -m sos <comando>

  status                 org, API key, Twin y workflows desplegados
  db start|stop|status   Postgres embebido local (.local/pg)
  db which               qué backend se usa ahora (SOS_DB=auto|local|twin)
  twin migrate           aplica el esquema (idempotente) al backend activo
  twin seed [escenario]  carga config + activos/contactos/medios del escenario (default demo_es)
  twin status            qué tablas/vistas existen
  twin reset             borra datos operativos (incidentes, evidencias, acciones...)
  twin sql "<SQL>"       ejecuta SQL y muestra filas
  twin sync-to-twin      copia config/assets/contacts/resources del Postgres local a Twin
  deploy [clave ...]     crea/actualiza y publica los workflows (todos o los indicados)
  destroy <clave ...>    borra workflows desplegados
  ingest <json>          envía un sobre de evidencia al hook de ingesta
"""

from __future__ import annotations

import json
import sys

from .happyrobot import HappyRobotClient, HappyRobotError


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[0], argv[1:]
    c = HappyRobotClient()
    try:
        {
            "status": cmd_status, "twin": cmd_twin, "db": cmd_db, "deploy": cmd_deploy,
            "destroy": cmd_destroy, "ingest": cmd_ingest,
        }[cmd](c, args)
    except KeyError:
        print(f"comando desconocido: {cmd}\n{__doc__}")
        sys.exit(2)
    except HappyRobotError as exc:
        print(f"ERROR API: {exc}")
        if isinstance(exc.body, dict):
            print(json.dumps(exc.body, indent=1, ensure_ascii=False)[:2000])
        sys.exit(1)


def cmd_status(c: HappyRobotClient, args: list[str]) -> None:
    from .twin.migrate import status as twin_status
    from .workflows.deploy import load_state

    k = c.describe_key()
    print(f"Org: {k['org_name']} ({k['org_slug']})  key: {k['prefix']}...{k['lastFour']}  base: {c.settings.api_base}")
    from .db import get_database, local_pg
    print("Postgres local:", local_pg.status())
    db = get_database(client=c)
    print(f"Backend activo: {db.name}")
    twin_status(db)
    db.close()
    print("Workflows desplegados (deploy-state.json):")
    for key, e in load_state()["workflows"].items():
        print(f"  {key:12} {e['name']:35} id={e['id']} hook={e.get('hook_url')}")


def cmd_db(c: HappyRobotClient, args: list[str]) -> None:
    from .db import get_database, local_pg

    sub = args[0] if args else "status"
    if sub == "start":
        print("local postgres:", local_pg.start())
    elif sub == "stop":
        local_pg.stop(); print("parado")
    elif sub == "status":
        print("local postgres:", local_pg.status())
    elif sub == "which":
        db = get_database(client=c); print("backend activo:", db.name); db.close()
    else:
        print("subcomando db desconocido")


def cmd_twin(c: HappyRobotClient, args: list[str]) -> None:
    from .db import get_database
    from .twin import migrate, seed

    sub = args[0] if args else "status"
    db = get_database(client=c)
    print(f"[backend: {db.name}]")
    if sub == "migrate":
        migrate.migrate(db)
    elif sub == "seed":
        n = seed.seed_config(db)
        counts = seed.seed_scenario(db, args[1] if len(args) > 1 else "demo_es")
        print(f"config: {n} claves · {counts}")
    elif sub == "status":
        migrate.status(db)
    elif sub == "reset":
        seed.reset_operational_data(db)
        print("datos operativos borrados")
    elif sub == "drop-all":
        migrate.drop_all(db)
        print("esquema eliminado")
    elif sub == "sql":
        res = db.sql(" ".join(args[1:]))
        print(f"{res['command']} rowCount={res['rowCount']}")
        for r in res["rows"]:
            print(json.dumps(r, ensure_ascii=False))
    elif sub == "sync-to-twin":
        from .twin.sync import sync_reference_data
        from .db.base import LocalDatabase, TwinDatabase

        print(sync_reference_data(LocalDatabase(), TwinDatabase(c)))
    else:
        print("subcomando twin desconocido")
    db.close()


def cmd_deploy(c: HappyRobotClient, args: list[str]) -> None:
    from .workflows.deploy import Deployer
    from .workflows.registry import all_specs

    Deployer(c).deploy(all_specs(), only=set(args) or None)


def cmd_destroy(c: HappyRobotClient, args: list[str]) -> None:
    from .workflows.deploy import Deployer

    Deployer(c).destroy(args)


def cmd_ingest(c: HappyRobotClient, args: list[str]) -> None:
    from .workflows.deploy import load_state

    payload = json.loads(args[0]) if args else {}
    wf = load_state()["workflows"]["ingest"]
    print(c.workflows.trigger(wf["id"], payload))
