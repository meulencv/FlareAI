"""Ejecuta el código de los nodos Python del sandbox en local (mismo contrato: input_data → output)."""
import json

from sos.workflows import ingest


def run(code: str, input_data: dict) -> dict:
    ns = {"input_data": input_data}
    exec(code, ns)
    return ns["output"]


def test_ingest_preparar_and_decidir_new_incident():
    prep = run(ingest.PREPARAR, {**ingest.SAMPLE, "now_iso": "2026-09-18T20:00:00Z"})
    assert prep["ok"] and prep["lat"] == 39.7
    assert "SELECT id::text AS id" in prep["sql_find"] and "cluster_radius_km" in prep["sql_find"]
    dec = run(ingest.DECIDIR, {**prep, "rows": "[]"})
    assert dec["is_new"] is True and dec["type"] == "wildfire" and dec["status"] == "candidate"
    assert len(dec["incident_id"]) == 36 and len(dec["evidence_id"]) == 36


def test_ingest_decidir_existing_incident_keeps_its_data():
    prep = run(ingest.PREPARAR, {**ingest.SAMPLE, "now_iso": "x", "reliability": ""})
    rows = json.dumps([{"id": "abc-123", "type": "unknown", "status": "verified", "lat": 39.71, "lon": -0.48}])
    dec = run(ingest.DECIDIR, {**prep, "rows": rows})
    assert dec["is_new"] is False and dec["incident_id"] == "abc-123"
    assert dec["type"] == "wildfire"  # adopta el tipo porque era unknown
    assert dec["status"] == "verified" and dec["inc_lat"] == 39.71
    assert dec["reliability"] == 0.5  # default para 'call'


def test_ingest_preparar_rejects_bad_coords():
    prep = run(ingest.PREPARAR, {**ingest.SAMPLE, "lat": "abc"})
    assert prep["ok"] is False
