"""Ejecuta los workflows reales con el intérprete local sobre el Postgres embebido.

Se salta si el Postgres local no está disponible (`python -m sos db start`).
"""
import json

import pytest

from sos.db import local_pg
from sos.workflows import approve, assess, execute, ingest, outbound_voice, citizen_inbound, weather

pytestmark = pytest.mark.skipif(not local_pg.installed(), reason="Postgres embebido no instalado (.local/pg)")


@pytest.fixture(scope="module")
def db():
    from sos.db.base import LocalDatabase
    from sos.twin import migrate, seed

    d = LocalDatabase()
    migrate.migrate(d, verbose=False)
    seed.seed_config(d)
    seed.seed_scenario(d)
    seed.reset_operational_data(d)
    yield d
    d.close()


@pytest.fixture
def rt(db):
    from sos.runtime import LocalRuntime
    from sos.runtime.agents import POLICIES

    specs = {s.key: s for s in (ingest.spec, assess.spec, execute.spec, approve.spec, outbound_voice.spec, citizen_inbound.spec, weather.inject)}
    r = LocalRuntime(db, specs, POLICIES, http=lambda m, u, h, b: {"status": "mock"})
    r.scenario = {}
    return r


ENV = {"source_type": "call", "source_ref": "t", "lat": "39.70", "lon": "-0.47", "observed_at": "", "reliability": "",
       "incident_type": "wildfire", "summary": "Humo", "details_json": "{}"}


def test_single_call_creates_candidate_and_recon(db, rt):
    from sos.twin import seed
    seed.reset_operational_data(db)
    rt.run("ingest", ENV)
    inc = db.rows("SELECT status, confidence FROM incidents")
    assert len(inc) == 1 and inc[0]["status"] == "candidate"
    acts = db.rows("SELECT kind, status FROM actions")
    assert acts == [{"kind": "dispatch", "status": "proposed"}]


def test_two_sources_verify_and_plan(db, rt):
    from sos.twin import seed
    seed.reset_operational_data(db)
    rt.run("ingest", ENV)
    inc = db.rows("SELECT id::text AS id FROM incidents")[0]["id"]
    rt.run("weather_inject", {"incident_id": inc, "wind_speed_kmh": "40", "wind_dir_deg": "270", "temp_c": "30", "humidity": "20", "source": "t"})
    rt.run("ingest", {**ENV, "source_type": "firms", "source_ref": "f1", "reliability": "0.85"})
    assert db.rows("SELECT count(*) AS n FROM incidents")[0]["n"] == 1  # agrupado
    i = db.rows("SELECT status, priority FROM incidents")[0]
    assert i["status"] in ("verified", "active") and i["priority"] >= 3
    kinds = {a["kind"] for a in db.rows("SELECT kind FROM actions")}
    assert {"evacuate_call", "coordination_call", "dispatch"} <= kinds
    assert db.rows("SELECT count(*) AS n FROM plans")[0]["n"] >= 1
    # notify se auto-aprueba y ejecuta
    assert db.rows("SELECT status FROM actions WHERE kind = 'notify'")[0]["status"] == "done"


def test_approve_execute_and_call_result(db, rt):
    a = db.rows("SELECT id::text AS id FROM actions WHERE kind = 'evacuate_call' AND status = 'proposed' LIMIT 1")[0]["id"]
    rt.run("approve", {"action_id": a, "decision": "approve", "operator": "test", "note": ""})
    assert db.rows(f"SELECT status FROM actions WHERE id = '{a}'")[0]["status"] == "ready"
    row = db.rows(f"SELECT a.incident_id::text AS incident_id, a.kind, c.name FROM actions a JOIN contacts c ON c.id = a.contact_id WHERE a.id = '{a}'")[0]
    rt.scenario["outbound"] = {"*": {"outcome": "accepted", "notes": "ok", "new_info": ""}}
    rt.run("outbound_voice", {"action_id": a, "incident_id": row["incident_id"], "kind": row["kind"], "role": "citizen", "contact_name": row["name"],
                              "place": "Serra", "instructions": "x", "incident_summary": "s", "incident_lat": "39.7", "incident_lon": "-0.47"})
    r = db.rows(f"SELECT status, result FROM actions WHERE id = '{a}'")[0]
    assert r["status"] == "done" and r["result"]["outcome"] == "accepted"


def test_wind_shift_reevaluates_and_signals(db, rt):
    inc = db.rows("SELECT id::text AS id FROM incidents")[0]["id"]
    before = db.rows("SELECT count(*) AS n FROM plans")[0]["n"]
    sent = []
    rt.http = lambda m, u, h, b: (sent.append(json.loads(b)), {"status": "published"})[1]
    rt.run("weather_inject", {"incident_id": inc, "wind_speed_kmh": "45", "wind_dir_deg": "90", "temp_c": "30", "humidity": "20", "source": "t"})
    assert sent and sent[0]["key"] == f"incident.{inc}" and sent[0]["payload"]["event"] == "wind_shift"
    assert db.rows("SELECT count(*) AS n FROM plans")[0]["n"] == before + 1
    threatened = db.rows("SELECT ai_assessment FROM incidents")[0]["ai_assessment"]["threatened_assets"]
    assert "olocau" in threatened and "segart" not in threatened
    assert db.rows("SELECT count(*) AS n FROM actions WHERE kind = 'evacuate_call' AND status = 'proposed'")[0]["n"] >= 1


def test_citizen_inbound_creates_evidence(db, rt):
    from sos.twin import seed
    seed.reset_operational_data(db)
    rt.scenario["aviso"] = {"lugar_ref": "naquera", "lugar_texto": "Náquera", "tipo": "wildfire", "descripcion": "humo", "nombre": "X", "telefono": "1"}
    rt.run("citizen_inbound", {})
    ev = db.rows("SELECT source_type, lat, lon, payload FROM evidence")
    assert ev and ev[0]["source_type"] == "call" and abs(ev[0]["lat"] - 39.6531) < 1e-3
    assert ev[0]["payload"]["caller"] == "X"
