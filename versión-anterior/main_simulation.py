#!/usr/bin/env python3
"""Simulación interactiva del S.O.S. Agentic Crisis Engine (entregable del reto).

    python main_simulation.py            # local: Postgres embebido + intérprete de workflows
    python main_simulation.py --cloud    # HappyRobot real (requiere Twin provisionado y `sos deploy`)
    python main_simulation.py --verbose  # muestra cada nodo ejecutado
    python main_simulation.py --pause 2  # pausa entre pasos (para presentar)

Escenario: incendio forestal en la Serra Calderona con giro de viento de 180°
(ver `sos/simulation/scenario_wind_shift.py`).
"""

from __future__ import annotations

import argparse
import sys

from sos.db import get_database
from sos.simulation import scenario_wind_shift as sc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cloud", action="store_true", help="dispara los workflows reales en HappyRobot")
    ap.add_argument("--verbose", action="store_true", help="traza de cada nodo ejecutado (modo local)")
    ap.add_argument("--pause", type=float, default=0.0, help="segundos de pausa entre pasos")
    ap.add_argument("--no-reset", action="store_true", help="no borrar incidentes/acciones previos")
    args = ap.parse_args()

    n = sc.Narrator()
    if args.cloud:
        from sos.happyrobot import HappyRobotClient

        client = HappyRobotClient()
        db = get_database("twin", client)
        driver = sc.CloudDriver(client, n)
        n.say("Modo CLOUD: workflows reales en HappyRobot, base de datos Twin.")
    else:
        db = get_database("local")
        driver = sc.LocalDriver(db, verbose=args.verbose)
        n.say("Modo LOCAL: Postgres embebido (.local/pg) + intérprete de los mismos workflows. Sin Twin, sin LLM.")

    # Asegura esquema y datos de referencia
    from sos.twin import migrate, seed

    migrate.migrate(db, verbose=False)
    if not db.rows("SELECT 1 FROM assets LIMIT 1"):
        seed.seed_config(db)
        seed.seed_scenario(db)

    sc.run(db, driver, n, reset=not args.no_reset, pause=args.pause)
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
