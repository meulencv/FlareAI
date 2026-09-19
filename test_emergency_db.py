import json
import math
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from build_emergency_db import (
    Cache, build, classify_osm, decode_text, deduplicate, distance_km, make_record,
    normalize_phones, parse_madrid, parse_overpass, parse_sanidad, parse_wfs,
    Geography, ROOT, OSM_FILTERS, OVERPASS, osm_query, plan_osm_queries,
    proximity, validate_overpass, write_database,
)


def record(identifier, name="Hospital de prueba", lon=-3.7, lat=40.4, source="osm", **extra):
    return make_record(source, identifier, name=name, categories=["hospital"],
                       lon=lon, lat=lat, province="Madrid", **extra)


class EmergencyTests(unittest.TestCase):
    def test_decode_realistic_encodings(self):
        for encoding in ("utf-8", "cp1252"):
            self.assertEqual(decode_text("Cádiz;Chamberí".encode(encoding)), "Cádiz;Chamberí")

    def test_contacts_never_invent_prefix_for_short_codes(self):
        self.assertEqual(normalize_phones("91 480 00 03 / Urgencias 112 / 061"),
                         ["+34914800003", "112", "061"])
        self.assertEqual(normalize_phones("No disponible"), [])
        self.assertEqual(normalize_phones("+34 914800003;0034 914800003"), ["+34914800003"])

    def test_categories_and_inactive_facilities(self):
        self.assertIn("police", classify_osm({"amenity": "police", "name": "Guardia Civil"}))
        self.assertIn("forest_fire_base", classify_osm({"emergency": "fire_station", "name": "Base INFOCA"}))
        self.assertEqual(classify_osm({"amenity": "hospital", "disused": "yes"}), [])
        self.assertEqual(classify_osm({"aeroway": "helipad"}), ["helipad"])
        self.assertEqual(classify_osm({"emergency": "no", "amenity": "cafe"}), [])
        self.assertEqual(classify_osm({"highway": "residential", "name": "Calle Protección Civil"}), [])

    def test_overpass_partial_errors_and_missing_count_are_rejected(self):
        for payload in ({"remark": "runtime error", "elements": []}, {"elements": []}):
            with self.assertRaises(ValueError):
                validate_overpass(json.dumps(payload).encode())
        validate_overpass(json.dumps({"elements": [{"type": "count", "tags": {"total": "0"}}]}).encode())

    def test_osm_center_is_not_claimed_as_entrance(self):
        result = parse_overpass({"elements": [{"type": "way", "id": 1,
                    "center": {"lat": 40.4, "lon": -3.7}, "tags": {"amenity": "hospital"}}]})
        self.assertEqual(result[0]["coordinate_method"], "osm_bbox_center")
        self.assertIsNone(result[0]["name"])
        self.assertIsNone(result[0]["metadata"]["open_24h"])

    def test_rdf_missing_coordinates_are_preserved(self):
        raw = b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:v="http://www.w3.org/2001/vcard-rdf/3.0#"><rdf:Description rdf:about="https://example.org/?id=1"><v:NAME>Hospital prueba</v:NAME><v:TEL>112</v:TEL></rdf:Description></rdf:RDF>'
        result = parse_sanidad(raw, "sanidad_hospitals", "hospital")
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["lat"])
        self.assertEqual(result[0]["phones"], ["112"])
        with_schema = raw.replace(b'</rdf:RDF>', b'<rdf:Description rdf:about="https://example.org/schema#TAC"><v:TAC>schema</v:TAC></rdf:Description></rdf:RDF>')
        self.assertEqual(len(parse_sanidad(with_schema, "sanidad_hospitals", "hospital")), 1)

    def test_urgent_location_name_is_extracted_not_invented(self):
        raw = b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:v="http://www.w3.org/2001/vcard-rdf/3.0#"><rdf:Description rdf:about="https://example.org/?id=1"><v:NAME>PUNTO DE ATENCION CONTINUADA</v:NAME><v:Street>CENTRO SALUD PRUEBA - CALLE MAYOR 1</v:Street></rdf:Description></rdf:RDF>'
        result = parse_sanidad(raw, "sanidad_urgent", "emergency_department")[0]
        self.assertEqual(result["name"], "CENTRO SALUD PRUEBA")
        self.assertEqual(result["address"], "CALLE MAYOR 1")
        self.assertIsNone(result["lat"])
        self.assertEqual(result["metadata"]["source_service_name"], "PUNTO DE ATENCION CONTINUADA")

    def test_real_province_aliases_cover_all_communities(self):
        geography = Geography(ROOT / "static/provinces.geojson")
        row = record("1", lon=-8.41, lat=43.36)
        row["province"] = None
        geography.enrich(row)
        self.assertEqual(row["province"], "A Coruña")
        self.assertEqual(row["autonomous_community"], "Galicia")

    def test_query_plan_reuses_complete_national_cache(self):
        import hashlib
        import urllib.parse
        with tempfile.TemporaryDirectory() as folder:
            cache = Cache(Path(folder), offline=True)
            self.assertEqual(len(plan_osm_queries(cache)), 19)
            for filters in OSM_FILTERS.values():
                url = OVERPASS[0] + '?' + urllib.parse.urlencode({'data': osm_query(filters)})
                (Path(folder) / (hashlib.sha256(url.encode()).hexdigest() + '.json')).write_text('{}')
            self.assertEqual(len(plan_osm_queries(cache)), 5)
            cache.refresh = True
            self.assertEqual(len(plan_osm_queries(cache)), 19)

    def test_madrid_semicolon_csv(self):
        raw = 'PK;NOMBRE;LATITUD;LONGITUD;TELEFONO\n1;Chamberí;40.44;-3.70;91 480 00 03\n'.encode("cp1252")
        result = parse_madrid(raw)
        self.assertEqual(result[0]["name"], "Chamberí")
        self.assertEqual(result[0]["phones"], ["+34914800003"])

    def test_wfs_single_multipoint_and_truncation(self):
        payload = {"type": "FeatureCollection", "numberMatched": 1, "features": [
            {"id": "x.1", "geometry": {"type": "MultiPoint", "coordinates": [[-3.7, 40.4]]},
             "properties": {"nombre": "Prueba", "telefono": "No disponible"}}]}
        result = parse_wfs(payload, "dera_fire", "fire_station")
        self.assertEqual(result[0]["lon"], -3.7)
        payload["numberMatched"] = 2
        with self.assertRaises(ValueError):
            parse_wfs(payload, "dera_fire", "fire_station")

    def test_dedup_is_geographic_and_preserves_different_sites(self):
        facilities, links = deduplicate([record("node/1"), record("way/2", lon=-3.7001),
                                        record("node/3", lon=-3.8)])
        self.assertEqual(len(facilities), 2)
        self.assertEqual(len(links), 3)
        self.assertEqual(len({link["facility_id"] for link in links}), 2)

    def test_no_transitive_chain_merge(self):
        facilities, _ = deduplicate([record("1", lat=40.4), record("2", lat=40.401),
                                      record("3", lat=40.402)])
        self.assertEqual(len(facilities), 2)

    def test_no_merge_unnamed_or_generic_facilities(self):
        for name in (None, "Hospital", "Policía Local"):
            facilities, _ = deduplicate([record("1", name), record("2", name)])
            self.assertEqual(len(facilities), 2)

    def test_unlocated_hospitals_match_unique_name_and_province(self):
        facilities, links = deduplicate([record("1"), record("2", source="sanidad_hospitals", lon=None, lat=None)])
        self.assertEqual(len(facilities), 1)
        self.assertEqual(links[-1]["match_method"], "unique_name_province")
        self.assertEqual(facilities[0]["lat"], 40.4)

    def test_generic_emergency_number_is_not_identity(self):
        facilities, _ = deduplicate([record("1", "Hospital A", phones=["112"]),
                                    record("2", "Hospital B", source="sanidad_hospitals", lon=None, lat=None, phones=["112"])])
        self.assertEqual(len(facilities), 2)

    def test_invalid_and_half_coordinates(self):
        for lon, lat in ((math.nan, 40), (180, 40), (None, 40)):
            with self.assertRaises(ValueError):
                record("1", lon=lon, lat=lat)

    def test_database_integrity_rtree_and_exact_radius(self):
        facilities, links = deduplicate([record("1"), record("2", lon=-3.8),
                                        record("3", name="Sin coordenadas", lon=None, lat=None)])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            write_database(path, facilities, links, [], {"build_id": "test"})
            with closing(sqlite3.connect(path)) as db, db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(db.execute("SELECT count(*) FROM facility_rtree").fetchone()[0], 2)
                result = proximity(db, 40.4, -3.7, 1)
                self.assertEqual(len(result), 1)
                self.assertAlmostEqual(result[0]["distance_km"], 0)
                db.execute("UPDATE facilities SET lon=-3.701 WHERE id=?", (facilities[0]["id"],))
                self.assertEqual(len(proximity(db, 40.4, -3.701, .01)), 1)
                db.execute("UPDATE facilities SET lat=NULL, lon=NULL WHERE id=?", (facilities[0]["id"],))
                self.assertEqual(db.execute("SELECT count(*) FROM facility_rtree").fetchone()[0], 1)

    def test_distance_and_invalid_queries(self):
        self.assertAlmostEqual(distance_km(40, -3, 41, -3), 111.195, places=2)
        with sqlite3.connect(":memory:") as db:
            for lat, lon, radius in ((math.nan, -3, 2), (40, -3, -1), (91, 0, 1)):
                with self.assertRaises(ValueError):
                    proximity(db, lat, lon, radius)

    def test_distinct_categories_and_ambiguous_matches_stay_separate(self):
        other = record("2")
        other["categories"] = ["police"]
        facilities, _ = deduplicate([record("1"), other])
        self.assertEqual(len(facilities), 2)
        facilities, links = deduplicate([record("1"), record("2", lon=-3.8),
            record("3", source="sanidad_hospitals", lon=None, lat=None)])
        self.assertEqual(len(facilities), 3)
        self.assertEqual(links[-1]["match_method"], "new_record")
        self.assertEqual(len(facilities[-1]["metadata"]["ambiguous_match_candidates"]), 2)

    def test_official_fields_win_without_discarding_osm_coordinates(self):
        facilities, links = deduplicate([record("1", address="Dirección OSM"),
            record("2", source="sanidad_hospitals", lon=None, lat=None, address="Dirección oficial")])
        self.assertEqual(facilities[0]["address"], "Dirección oficial")
        self.assertEqual(facilities[0]["coordinate_method"], "published_point")
        self.assertEqual(links[0]["address"], "Dirección OSM")
        self.assertEqual(facilities[0]["field_sources"]["lat"], "osm:1")

    def test_cache_retry_offline_and_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Cache(Path(folder), retries=2)
            response = unittest.mock.MagicMock()
            response.__enter__.return_value = response
            response.read.return_value = b'{"valid":true}'
            response.url = "https://example.org/data"
            response.headers.get.return_value = None
            with patch("urllib.request.urlopen", side_effect=[OSError("temporary"), response]) as request, patch("time.sleep"):
                data, meta = cache.fetch("osm", response.url, json.loads)
                self.assertEqual(request.call_count, 2)
            with patch("urllib.request.urlopen") as request:
                cached, evidence = Cache(Path(folder), offline=True).fetch("osm", response.url, json.loads)
                self.assertEqual(cached, data)
                self.assertEqual(evidence["sha256"], meta["sha256"])
                self.assertTrue(evidence["cache_hit"])
                request.assert_not_called()
            import gzip
            (Path(folder) / meta["file"]).write_bytes(gzip.compress(b'{}'))
            with self.assertRaises(ValueError):
                Cache(Path(folder), offline=True).fetch("osm", response.url, json.loads)

    def test_incomplete_acquisition_does_not_publish_or_replace(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            previous = output / "emergencias_espana.db"
            previous.write_bytes(b"existing build")
            args = SimpleNamespace(cache_dir=output / "cache", offline=True, refresh=False,
                                   retries=1, overpass_endpoint=None, allow_partial=False)
            with patch("build_emergency_db.acquire", return_value=([], [], [{"source": "osm", "status": "failed"}])):
                self.assertEqual(build(args), 2)
            self.assertEqual(previous.read_bytes(), b"existing build")
            self.assertTrue((output / "cache/last_acquisition.json").exists())

    def test_refresh_does_not_accept_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                Cache(Path(folder), offline=True, refresh=True)

    def test_offline_never_contacts_network(self):
        with tempfile.TemporaryDirectory() as folder, patch("urllib.request.urlopen") as request:
            cache = Cache(Path(folder), offline=True)
            with self.assertRaises(FileNotFoundError):
                cache.fetch("missing", "https://example.org", lambda data: None)
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
