import json
import tempfile
import unittest
from pathlib import Path

from budget import Budget
from incident_workflow import extract_results, validate_choice
from traffic_catalog import Catalog, nearby_cameras, normalize_incident


class SelectionTests(unittest.TestCase):
    def cameras(self):
        return [{"id": "a", "lat": 40.4, "lon": -3.7}, {"id": "b", "lat": 40.41, "lon": -3.7},
                {"id": "far", "lat": 41.4, "lon": -3.7}]

    def test_geographic_query_is_bounded_and_sorted(self):
        result = nearby_cameras(self.cameras(), {"lat": 40.4, "lon": -3.7, "radius_km": 5})
        self.assertEqual([camera["id"] for camera in result], ["a", "b"])
        self.assertEqual(result[0]["distance_km"], 0)

    def test_bad_locations_and_massive_radii_are_rejected(self):
        for incident in ({"lat": True, "lon": -3}, {"lat": float("nan"), "lon": -3},
                         {"lat": 40, "lon": -3, "radius_km": 1000}, {"lat": 99, "lon": -3}):
            with self.assertRaises(ValueError):
                normalize_incident(incident)

    def test_ai_cannot_invent_duplicate_or_select_too_many_cameras(self):
        candidates = json.dumps(self.cameras())
        for ids in (["invented"], ["a", "a"], ["a", "b", "far"], "a"):
            self.assertEqual(validate_choice(candidates, json.dumps(ids), "Test")["items"], [])

    def test_valid_ai_selection_keeps_only_catalog_data(self):
        result = validate_choice(json.dumps(self.cameras()), '["b","a"]', "Elegidas por carretera")
        self.assertEqual([camera["id"] for camera in result["items"]], ["b", "a"])
        self.assertEqual(result["selected_count"], 2)

    def test_no_cameras_is_not_free_traffic(self):
        result = validate_choice("[]", "[]", "No hay cámaras cercanas")
        self.assertEqual(result["selection_status"], "no_selection")

    def test_remote_results_are_extracted_without_returning_headers(self):
        result = {"engine": "multimodal_estimate_not_yolo", "camera_id": "a", "density": "unknown"}
        wrapped = {"headers": {"Authorization": "test-secret"}, "nested": [{"result_json": json.dumps(result)}]}
        self.assertEqual(extract_results(wrapped), [result])
        self.assertNotIn("test-secret", json.dumps(extract_results(wrapped)))

    def test_local_catalog_can_resolve_incident_without_writing_database(self):
        catalog = Catalog.load()
        result = catalog.nearby({"lat": 40.4859, "lon": -3.694, "radius_km": 5})
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 12)
        self.assertTrue(all(camera["distance_km"] <= 5 for camera in result))


class RemoteResultTests(unittest.TestCase):
    def test_async_child_is_followed_and_parent_waits_for_it(self):
        from unittest.mock import patch
        import incident_workflow
        child = "00000000-0000-4000-8000-000000000001"
        state = {"nodes": {"query": "q", "validate": "v", "call": "c", "call_second": "c2"},
                 "catalog_count": 1, "catalog_sha256": "hash", "catalog_copied_at": "date"}
        vision = {"workflow_id": "vision", "nodes": {"finalize": "final"}}
        result = {"camera_id": "a", "engine": "multimodal_estimate_not_yolo", "usage_cost_usd": 0.001}

        class Fake:
            complete = False

            def request(self, method, path):
                values = {
                    "/runs/parent": {"status": "completed"},
                    "/runs/parent/nodes": [{"node_id": "v", "output_id": "selection", "status": "succeeded"},
                                           {"node_id": "c", "output_id": "call", "status": "succeeded"}],
                    "/runs/parent/outputs/selection": {"data": {"selected_json": '[{"id":"a"}]'}},
                    "/runs/parent/outputs/call": {"data": {"call_workflow_data": {"child_run_id": child}}},
                    f"/runs/{child}": {"workflow_id": "vision", "status": "completed" if self.complete else "running"},
                    f"/runs/{child}/nodes": [{"node_persistent_id": "final", "output_id": "result"}] if self.complete else [],
                    f"/runs/{child}/outputs/result": {"data": {"result_json": json.dumps(result)}},
                }
                return values[path]

        api = Fake()
        with patch.object(incident_workflow, "load", return_value=state), patch.object(incident_workflow, "vision_state", return_value=vision):
            self.assertEqual(incident_workflow.read_run(api, "parent")["status"], "pending")
            api.complete = True
            value = incident_workflow.read_run(api, "parent")
            self.assertEqual(value["status"], "completed")
            self.assertEqual(value["results"][0]["child_run_id"], child)


class BudgetTests(unittest.TestCase):
    def test_pending_requests_count_towards_cap_and_settlement_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            budget = Budget(Path(folder) / "budget.db", 2, 0.0019968)
            budget.reserve("a")
            budget.reserve("b")
            with self.assertRaises(ValueError):
                budget.reserve("c")
            budget.settle("a", [0.001, 0.001])
            budget.settle("a", [1, 1])
            budget.reserve("c")
            self.assertLess(budget.status()["used_or_reserved_usd"], 2)

    def test_unknown_cost_is_not_refunded(self):
        with tempfile.TemporaryDirectory() as folder:
            budget = Budget(Path(folder) / "budget.db", 1)
            budget.reserve("a")
            budget.settle("a", [None, None])
            self.assertAlmostEqual(budget.status()["remaining_usd"], 0.1)
            with self.assertRaises(ValueError):
                budget.reserve("b")

    def test_uncertain_reservation_is_reconciled_only_with_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            budget = Budget(Path(folder) / "budget.db", 2)
            budget.reserve("a")
            budget.settle("a", [None, None])
            proof = {"status": "completed", "run_id": "trace", "selected": [{"id": "a"}, {"id": "b"}],
                     "results": [{"usage_cost_usd": 0.001}, {"usage_cost_usd": 0.002}]}
            budget.reconcile_actual("a", proof)
            budget.reconcile_actual("a", proof)
            self.assertAlmostEqual(budget.status()["used_or_reserved_usd"], 0.003)
            with self.assertRaises(ValueError):
                budget.release_unbilled("a", {"status": "completed", "run_id": "trace", "call_attempt_count": 0})

    def test_cannot_release_an_attempted_call_as_unbilled(self):
        with tempfile.TemporaryDirectory() as folder:
            budget = Budget(Path(folder) / "budget.db", 2)
            budget.reserve("a")
            with self.assertRaises(ValueError):
                budget.release_unbilled("a", {"status": "completed", "run_id": "trace", "call_attempt_count": 1})
            self.assertAlmostEqual(budget.status()["used_or_reserved_usd"], 0.9)

    def test_constructor_does_not_raise_an_existing_spending_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budget.db"
            Budget(path, 1)
            self.assertEqual(Budget(path, 100).status()["cap_usd"], 1)


if __name__ == "__main__":
    unittest.main()
