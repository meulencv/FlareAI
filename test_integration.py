import json
import math
import threading
import unittest
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer
from typing import cast
from unittest.mock import patch

from PIL import Image

from app import Handler, Store
from gfs import DATA, ROOT, Region, Snapshot, decode, point, ranges
from incidents import Collection, Incident, Observation, assemble, cluster, footprint
from satellite import coverage_fraction
from verify_api import verify


class IntegrationTests(unittest.TestCase):
    weather: Snapshot
    collection: Collection
    at: datetime
    incidents: list[Incident]

    @classmethod
    def setUpClass(cls) -> None:
        cls.weather = cast(Snapshot, json.loads((ROOT / "examples/weather.json").read_text()))
        cls.collection = cast(Collection, json.loads((ROOT / "examples/firms.geojson").read_text()))
        cls.at = datetime.fromisoformat(cls.collection["analysis_at_utc"])
        cls.incidents = assemble(cls.collection, cls.weather, cls.at)

    def test_every_observation_is_accounted_for(self) -> None:
        expected = [o for o in self.collection["features"]
                    if self.at - timedelta(hours=24) <= datetime.fromisoformat(o["properties"]["acquired_at_utc"]) <= self.at]
        self.assertEqual(sum(i["observations"] for i in self.incidents), len(expected))
        self.assertEqual(len({i["id"] for i in self.incidents}), len(self.incidents))
        self.assertTrue(all(i["burned_area_ha"] is None for i in self.incidents))
        self.assertTrue(all(i["footprint_ha"] > 0 for i in self.incidents))

    def test_temperature_units_and_wind_direction(self) -> None:
        grid = Region(name="test", west=0, south=0, step=1, nx=2, ny=2,
                      u=[3] * 4, v=[4] * 4, gust=[10] * 4, temperature=[293.15] * 4)
        dataset = self.weather.copy()
        dataset["regions"] = [grid]
        result = point(dataset, .5, .5)
        self.assertEqual(result["air_temperature_c"], 20)
        self.assertEqual(result["wind_speed_kmh"], 18)
        self.assertEqual(result["wind_gust_kmh"], 36)
        self.assertEqual(result["wind_from_degrees"], 216.9)

    def test_actual_temperature_grib_metadata(self) -> None:
        run = datetime.fromisoformat(self.weather["model_run_utc"].replace("Z", "+00:00"))
        valid = datetime.fromisoformat(self.weather["valid_at_utc"].replace("Z", "+00:00"))
        folder = DATA / "evidence" / f"{run:%Y%m%d_%H}_f{self.weather['forecast_hour']:03d}"
        raw = decode((folder / "temperature.grib2").read_bytes(), "temperature", run, valid)
        grid = self.weather["regions"][0]
        row = round((90 - grid["south"]) * 4)
        col = round((grid["west"] % 360) * 4)
        self.assertAlmostEqual(grid["temperature"][0], raw[row, col], places=3)
        selected = ranges(next(folder.glob("*.idx")).read_text())
        self.assertEqual(set(selected), {"u", "v", "gust", "temperature"})

    def test_all_regions_have_finite_reasonable_temperature(self) -> None:
        for grid in self.weather["regions"]:
            self.assertEqual(len(grid["temperature"]), grid["nx"] * grid["ny"])
            self.assertTrue(all(math.isfinite(t) and 180 < t < 340 for t in grid["temperature"]))

    def test_duplicate_passes_do_not_double_footprint(self) -> None:
        observation = self.collection["features"][0]
        lon, lat = observation["geometry"]["coordinates"]
        _, single = footprint([observation], lon, lat)
        _, duplicate = footprint([observation, observation], lon, lat)
        self.assertEqual(single, duplicate)

    def test_clustering_is_connected_and_order_independent(self) -> None:
        def observation(lon: float) -> Observation:
            result = self.collection["features"][0].copy()
            result["geometry"] = {"coordinates": [lon, 40]}
            return result
        a, b, c, distant = [observation(x) for x in [0, .03, .06, 1]]
        self.assertEqual(sorted(map(len, cluster([a, c, distant, b]))), [1, 3])
        self.assertEqual(sorted(map(len, cluster([b, distant, c, a]))), [1, 3])

    def test_brightness_is_distinct_from_air_temperature(self) -> None:
        igea = next(i for i in self.incidents if i["documented"])
        self.assertEqual(igea["name"], "Igea")
        self.assertEqual(igea["passes"], 4)
        self.assertEqual(igea["observations"], 15)
        self.assertAlmostEqual(igea["brightness_i4_c"], igea["brightness_i4_k"] - 273.15, places=1)
        self.assertNotEqual(igea["brightness_i4_c"], igea["weather"]["air_temperature_c"])

    def test_empty_recent_window_is_not_an_old_fire(self) -> None:
        self.assertEqual(assemble(self.collection, self.weather, self.at + timedelta(days=3)), [])

    def test_offline_sample_is_dated_not_discarded(self) -> None:
        with patch("app.utcnow", return_value=self.at + timedelta(days=3)):
            store = Store(offline=True)
            payload = store.payload()
        self.assertEqual(payload["status"], "offline")
        self.assertGreater(len(store.incidents), 0)

    def test_black_opaque_or_transparent_images_are_not_photos(self) -> None:
        for color in [(0, 0, 0, 255), (255, 255, 255, 0)]:
            self.assertEqual(coverage_fraction(Image.new("RGBA", (30, 20), color)), 0)
        self.assertEqual(coverage_fraction(Image.new("RGBA", (30, 20), (80, 100, 90, 255))), 1)

    def test_offline_http_and_both_archived_images(self) -> None:
        store = Store(offline=True)
        store.fires, store.weather, store.incidents = self.collection, self.weather, self.incidents
        Handler.store = store
        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                with patch("satellite.urlopen", side_effect=AssertionError("El modo offline no debe contactar a NASA")):
                    verify(f"http://127.0.0.1:{server.server_port}")
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()
