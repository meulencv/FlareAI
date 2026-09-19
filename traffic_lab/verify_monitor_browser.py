import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Comprueba una consulta existente en Edge; no inicia inferencias")
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8790/?job=" + args.job_id)
        deadline = time.monotonic() + 240
        value = None
        while time.monotonic() < deadline:
            response = page.request.get("http://127.0.0.1:8790/api/remote/job?id=" + args.job_id)
            value = response.json()
            if value.get("status") in {"completed", "failed"}:
                break
            page.wait_for_timeout(1500)
        page.wait_for_timeout(3500)
        page.screenshot(path=str(ROOT / "monitor-current.png"), full_page=True)
        if value is None or value.get("status") != "completed":
            raise AssertionError("La consulta no se completó: " + json.dumps(value, ensure_ascii=True))
        if not value.get("selected") or len(value.get("results", [])) != len(value["selected"]):
            raise AssertionError("Faltan resultados de cámaras elegidas")
        assert page.locator(".remote-card").count() == len(value["selected"])
        assert page.locator(".local-lab").evaluate("element => !element.open")
        captures = [result["captured_at"] for result in value["results"] if result.get("captured_at")]
        if not captures:
            raise AssertionError("No se ha leído ningún reloj en esta prueba positiva")
        future = page.evaluate("values => Math.max(...values.map(v => Date.parse(v))) + 601000", captures)
        page.evaluate("future => {Date.now = () => future;}", future)
        page.wait_for_timeout(1200)
        for card in page.locator(".remote-card").all():
            assert card.locator(".remote-metrics strong").inner_text() == "—"
        page.screenshot(path=str(ROOT / "monitor-expired-test.png"), full_page=True)
        assert not errors, errors
        report = {"job": value, "javascript_errors": errors, "cards_rendered": len(value["selected"]),
                  "expiry_test": "passed_with_simulated_browser_clock", "new_paid_calls_by_this_script": 0}
        (ROOT / "verification-monitor.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"job_id": args.job_id, "status": value["status"], "cameras": [camera["id"] for camera in value["selected"]],
                          "clock_readings": captures, "budget": value["budget"], "javascript_errors": errors,
                          "expiry_test": "passed"}, ensure_ascii=True, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
