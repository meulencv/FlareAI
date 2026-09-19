import json
from pathlib import Path

from sos.risk.engine import angle_diff, bearing_deg, compute_risk, haversine_km

SCEN = json.loads((Path(__file__).parent.parent / "config/scenarios/demo_es.json").read_text())
CFG = {k: v["value"] for k, v in json.loads((Path(__file__).parent.parent / "config/weights.json").read_text()).items() if not k.startswith("_")}
FIRE = {"lat": 39.70, "lon": -0.47, "type": "wildfire"}  # oeste de Serra


def test_geometry():
    assert abs(haversine_km(39.70, -0.47, 39.70, -0.47)) < 1e-9
    assert abs(bearing_deg(0, 0, 0, 1) - 90) < 1e-6  # hacia el este
    assert angle_diff(350, 10) == 20


def test_wind_from_west_threatens_serra_not_gatova():
    r = compute_risk(FIRE, {"wind_speed_kmh": 40, "wind_dir_deg": 270}, SCEN["assets"], SCEN["resources"], CFG)
    names = [t["ref"] for t in r["threatened_assets"]]
    assert "serra" in names and "ceip_serra" in names
    assert "gatova" not in names
    assert r["priority"] >= 3
    assert r["needed_capabilities"] == ["water"]
    assert r["recommended_resources"][0]["compatible"] is True


def test_wind_shift_180_changes_targets():
    before = compute_risk(FIRE, {"wind_speed_kmh": 40, "wind_dir_deg": 270}, SCEN["assets"], config=CFG)
    after = compute_risk(FIRE, {"wind_speed_kmh": 40, "wind_dir_deg": 90}, SCEN["assets"], config=CFG)
    b = {t["ref"] for t in before["threatened_assets"]}
    a = {t["ref"] for t in after["threatened_assets"]}
    assert "serra" in b and "serra" not in a
    assert "olocau" in a and "olocau" not in b


def test_no_weather_only_perimeter():
    r = compute_risk({"lat": 39.6836, "lon": -0.4216, "type": "wildfire"}, None, SCEN["assets"], config=CFG)
    assert all(t["reason"] == "perimetro" for t in r["threatened_assets"])
    assert any(t["ref"] == "serra" for t in r["threatened_assets"])
