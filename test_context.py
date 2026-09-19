import json
import math
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from shapely.geometry import box, mapping

from app import Handler, Store
from context import Atlas, GRID_FIELDS, wind_state


NOW = datetime(2026, 9, 19, 8, tzinfo=timezone.utc)


def incident():
    return {
        "id": "test", "lat": 40.0, "lon": -3.0,
        "footprint": mapping(box(-3.001, 39.999, -2.999, 40.001)),
        "weather": {"wind_speed_kmh": 15, "wind_from_degrees": 270,
                    "valid_at_utc": NOW.isoformat(), "model_run_utc": NOW.isoformat()},
    }


def grid_row(lon, lat=40, population=10, forest=50, surface=1):
    values = {name: 0.0 for name in GRID_FIELDS}
    values.update(lon=lon, lat=lat, poblacion=population, menores_15=2, mayores_65=3,
                  superficie_clasificada_km2=surface, pct_suelo_bosque=forest,
                  pct_suelo_urbano=100 - forest, x_min_3035=lon * 100000, y_min_3035=lat * 100000)
    return tuple(values[name] for name in GRID_FIELDS)


def facility(lon, identifier="way:1", lat=40):
    return {"id": identifier, "lon": lon, "lat": lat, "name": "Depósito de prueba",
            "category": "combustibles_quimica", "priority": "alta_orientativa",
            "reason": "Combustible declarado; revisar", "source_url": "https://www.openstreetmap.org/way/1"}


def atlas(rows=(), facilities=()):
    return Atlas(np.array(list(rows), dtype=[(name, "f8") for name in GRID_FIELDS]), list(facilities))


class ContextTests(unittest.TestCase):
    def test_wind_goes_east_when_it_comes_from_west(self):
        result = atlas([grid_row(-2.98), grid_row(-3.02)], [facility(-2.98), facility(-3.02, "way:2")]).analyze(incident(), now=NOW)
        self.assertEqual(result["population"]["residents"], 20)
        self.assertEqual(result["population"]["downwind_residents"], 10)
        self.assertEqual(result["facilities"]["downwind_high_priority"], 1)
        self.assertEqual(result["wind"]["towards_degrees"], 90)
        self.assertEqual(result["level"], "attention")

    def test_north_wrap_and_calm_missing_stale_wind(self):
        item = incident()
        item["weather"]["wind_from_degrees"] = 180
        result = atlas([grid_row(-3, 40.02), grid_row(-3, 39.98)]).analyze(item, now=NOW)
        self.assertEqual(result["population"]["downwind_residents"], 10)
        for change in [{"wind_speed_kmh": 1}, {"wind_from_degrees": None},
                       {"wind_from_degrees": math.nan}, {"wind_speed_kmh": None},
                       {"valid_at_utc": (NOW - timedelta(hours=3)).isoformat()},
                       {"model_run_utc": (NOW - timedelta(hours=13)).isoformat()}]:
            item = incident()
            item["weather"].update(change)
            result = atlas([grid_row(-2.98)]).analyze(item, now=NOW)
            self.assertIsNone(result["population"]["downwind_residents"])
            self.assertEqual(result["population"]["residents"], 10)
            self.assertFalse(any(p["downwind"] for p in result["points"]))

    def test_weather_error_disables_direction_and_offline_is_historical(self):
        self.assertFalse(wind_state(incident()["weather"], NOW, weather_error=True)["usable"])
        result = atlas([grid_row(-2.98)]).analyze(incident(), now=NOW + timedelta(days=3), offline=True)
        self.assertEqual(result["wind"]["status"], "historical")
        self.assertEqual(result["level"], "nearby")
        self.assertEqual(result["population"]["downwind_residents"], 10)

    def test_radius_is_from_footprint_not_cluster_centroid(self):
        item = incident()
        item["footprint"] = mapping(box(-3.12, 39.999, -2.88, 40.001))
        result = atlas([grid_row(-2.86), grid_row(-2.7)], [facility(-2.86)]).analyze(item, now=NOW)
        self.assertEqual(result["population"]["residents"], 10)
        self.assertLess(result["points"][0]["distance_km"], 2)
        self.assertEqual(result["facilities"]["count"], 1)

    def test_inside_footprint_is_not_given_an_arbitrary_wind_bearing(self):
        result = atlas([grid_row(-3)]).analyze(incident(), now=NOW)
        self.assertEqual(result["points"][0]["distance_km"], 0)
        self.assertFalse(result["points"][0]["downwind"])
        self.assertEqual(result["population"]["downwind_residents"], 0)

    def test_soil_is_area_weighted_and_missing_is_not_zero(self):
        result = atlas([grid_row(-2.98, forest=100, surface=.2), grid_row(-3.02, forest=0, surface=.8)]).analyze(incident(), now=NOW)
        self.assertEqual(result["landcover"]["percentages"]["bosque"], 20)
        result = atlas([grid_row(-2.98, forest=math.nan, surface=0)]).analyze(incident(), now=NOW)
        self.assertIsNone(result["landcover"]["percentages"]["bosque"])
        self.assertEqual(result["landcover"]["missing_cells"], 1)
        json.dumps(result, allow_nan=False)

    def test_empty_or_partial_coverage_is_not_an_all_clear(self):
        result = atlas().analyze(incident(), now=NOW)
        self.assertEqual(result["coverage"], "no_grid_cells")
        self.assertIsNone(result["population"]["residents"])
        result = atlas([grid_row(-2.98, population=math.nan)]).analyze(incident(), now=NOW)
        self.assertIsNone(result["population"]["residents"])
        self.assertEqual(result["population"]["missing_cells"], 1)

    def test_population_not_counted_again_for_multiple_installations(self):
        result = atlas([grid_row(-2.98)], [facility(-2.98), facility(-2.981, "way:2")]).analyze(incident(), now=NOW)
        self.assertEqual(result["population"]["residents"], 10)
        self.assertEqual(result["facilities"]["count"], 2)

    def test_points_are_bounded_without_truncating_totals(self):
        result = atlas([grid_row(-2.98 + i * .0001) for i in range(20)],
                       [facility(-2.98, f"way:{i}") for i in range(20)]).analyze(incident(), now=NOW)
        self.assertLessEqual(len(result["points"]), 12)
        self.assertEqual(result["population"]["residents"], 200)
        self.assertEqual(result["facilities"]["count"], 20)
        self.assertTrue(result["points_truncated"])

    def test_missing_atlas_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(OSError):
                Atlas.load(Path(folder))


class AtlasIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = Atlas.load()

    def test_delivered_counts_and_national_population(self):
        self.assertEqual(len(self.atlas.grid), 511226)
        self.assertEqual(len(self.atlas.facilities), 44787)
        self.assertEqual(int(self.atlas.grid["poblacion"].sum()), 47400134)
        self.assertEqual(len({p["id"] for p in self.atlas.facilities}), 44787)

    def test_peninsula_islands_and_autonomous_cities(self):
        for lon, lat in [(-3.70, 40.42), (2.65, 39.57), (-15.43, 28.12), (-5.32, 35.89), (-2.94, 35.29)]:
            with self.subTest(lon=lon, lat=lat):
                item = incident()
                item.update(lon=lon, lat=lat, footprint=mapping(box(lon-.001, lat-.001, lon+.001, lat+.001)))
                result = self.atlas.analyze(item, now=NOW)
                self.assertGreater(result["population"]["residents"], 0)
                self.assertGreater(result["facilities"]["count"], 0)
                self.assertLessEqual(len(result["points"]), 12)
                json.dumps(result, allow_nan=False)

    def test_http_contract_and_missing_dataset_do_not_break_core_api(self):
        store = Store(offline=True)
        store.atlas = self.atlas
        class TestHandler(Handler):
            pass
        TestHandler.store = store
        with ThreadingHTTPServer(("127.0.0.1", 0), TestHandler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                with urlopen(base + "/api/context?id=" + store.incidents[0]["id"]) as response:
                    result = json.load(response)
                    self.assertEqual(result["incident_id"], store.incidents[0]["id"])
                    self.assertGreater(result["population"]["residents"], 0)
                for path in ["/api/context", "/api/context?id=unknown", "/api/context?id="]:
                    with self.assertRaises(HTTPError) as error:
                        urlopen(base + path)
                    self.assertEqual(error.exception.code, 400)
                    error.exception.close()
                with urlopen(base + "/atlas/sources") as response:
                    self.assertIn("ODbL", response.read().decode())
                store.atlas = None
                with patch("app.Atlas.load", side_effect=FileNotFoundError("Atlas no instalado")):
                    with self.assertRaises(HTTPError) as error:
                        urlopen(base + "/api/context?id=" + store.incidents[0]["id"])
                    self.assertEqual(error.exception.code, 503)
                    error.exception.close()
                    with urlopen(base + "/api/data") as response:
                        self.assertGreater(len(json.load(response)["incidents"]), 0)
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
