from __future__ import annotations

import argparse
import csv
import io
import json
import re
import socket
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from socketserver import BaseServer
from typing import cast
from urllib.parse import parse_qs, urlsplit

import psycopg

from context import ATLAS_ROOT, Atlas
from database import Database, local_start
from territorial import Territorial
from gfs import DATA, ROOT, Snapshot, iso, update, utcnow
from incidents import Collection, Incident, assemble, refresh_fires
from satellite import picture


class Store:
    def __init__(self, offline: bool = False, database: Database | None = None) -> None:
        self.offline = offline
        self.db = database
        self.territorial = Territorial(database, offline) if database else None
        self.lock = threading.Lock()
        self.atlas_lock = threading.Lock()
        self.atlas: Atlas | None = None
        self.fires = cast(Collection, database.snapshot('fires') if database else json.loads((DATA / "firms/focos_espana.geojson").read_text()))
        self.weather = cast(Snapshot, database.snapshot('weather') if database else json.loads((DATA / "latest.json").read_text()))
        self.errors: dict[str, str] = {}
        provinces = database.get_asset('map:provinces.geojson') if database else None
        self.provinces = provinces['data']['features'] if provinces else None
        self.incidents = assemble(self.fires, self.weather, datetime.fromisoformat(self.fires["analysis_at_utc"]) if offline else None, self.provinces)
        if self.db:
            self.db.save_incidents([dict(i) for i in self.incidents])

    def refresh_loop(self) -> None:
        next_fires = 0.0
        while True:
            try:
                weather = update()
                if self.db:
                    self.db.save_snapshot('weather', dict(weather))
                with self.lock:
                    self.weather = weather
                    self.errors.pop("weather", None)
            except Exception as error:
                with self.lock:
                    self.errors["weather"] = str(error)
            if time.monotonic() >= next_fires:
                try:
                    fires = refresh_fires()
                    if self.db:
                        self.db.save_snapshot('fires', dict(fires))
                    with self.lock:
                        self.fires = fires
                        self.errors.pop("fires", None)
                    next_fires = time.monotonic() + 1800
                except Exception as error:
                    with self.lock:
                        self.errors["fires"] = str(error)
            try:
                with self.lock:
                    incidents = assemble(self.fires, self.weather, province_features=self.provinces)
                if self.db:
                    self.db.save_incidents([dict(i) for i in incidents])
                with self.lock:
                    self.incidents = incidents
                    self.errors.pop('database', None)
            except Exception:
                with self.lock:
                    self.errors['database'] = 'No se pudo guardar la actualización local'
            threading.Event().wait(600)

    def payload(self) -> dict[str, object]:
        now = utcnow()
        confirmed = self.db.confirmations(now) if self.db and not self.offline else {}
        with self.lock:
            weather_age = (now - datetime.fromisoformat(self.weather["valid_at_utc"].replace("Z", "+00:00"))).total_seconds()
            fire_age = (now - datetime.fromisoformat(self.fires["analysis_at_utc"])).total_seconds()
            model_age = (now - datetime.fromisoformat(self.weather["model_run_utc"].replace("Z", "+00:00"))).total_seconds()
            incidents = self.incidents if self.offline else [
                i for i in self.incidents if (now - datetime.fromisoformat(i["last_seen"])).total_seconds() <= 86400
            ]
            return {
                "generated_at": iso(now),
                "status": "offline" if self.offline else "stale" if self.errors or weather_age > 7200 or fire_age > 7200 or model_age > 43200 else "ready",
                "errors": dict(self.errors),
                "incidents": [{**i, 'confirmation': confirmed.get(i['id'], {'status': 'unconfirmed', 'reason': 'FIRMS identifica anomalías térmicas; no confirma incendios forestales.'})} for i in incidents], "wind": self.weather,
                "fires_checked_at": self.fires["analysis_at_utc"], "window_hours": 24,
                "fire_refresh_seconds": 1800, "weather_refresh_seconds": 600,
                "classification": "thermal_clusters_not_exhaustive_fire_inventory",
            }

    def context(self, identifier: str) -> dict:
        with self.lock:
            incident = next((i for i in self.incidents if i["id"] == identifier), None)
            weather_error = "weather" in self.errors
            if incident is None or (not self.offline and (utcnow() - datetime.fromisoformat(incident["last_seen"])).total_seconds() > 86400):
                raise KeyError("Zona no encontrada en el periodo disponible")
        if self.db:
            atlas = self.db.nearby_atlas(dict(incident))
        else:
            with self.atlas_lock:
                if self.atlas is None:
                    self.atlas = Atlas.load()
                atlas = self.atlas
        return atlas.analyze(dict(incident), now=utcnow(), offline=self.offline, weather_error=weather_error)

    def find(self, identifier: str) -> Incident:
        with self.lock:
            for incident in self.incidents:
                if incident["id"] == identifier:
                    return incident
        raise KeyError("Zona no encontrada")


class Handler(SimpleHTTPRequestHandler):
    store: Store

    def __init__(self, request: socket.socket, client_address: tuple[str, int], server: BaseServer) -> None:
        super().__init__(request, client_address, server, directory=str(ROOT / "static"))

    def send_bytes(self, body: bytes, mime: str, status: int = 200, download: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if mime.startswith("application") else "public, max-age=3600")
        self.send_header("X-Content-Type-Options", "nosniff")
        if download:
            self.send_header("Content-Disposition", 'attachment; filename="flareai-espana.json"')
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_json(self, data: object, status: int = 200, download: bool = False) -> None:
        self.send_bytes(json.dumps(data, ensure_ascii=False, allow_nan=False).encode(), "application/json; charset=utf-8", status, download)

    def do_GET(self) -> None:
        route = urlsplit(self.path)
        query = parse_qs(route.query)
        try:
            if route.path == "/api/data":
                self.send_json(self.store.payload(), download="download" in query)
            elif route.path == "/api/incidents.csv":
                output = io.StringIO()
                fields = ["id", "name", "province", "lat", "lon", "observations", "last_seen",
                          "documented", "frp_peak_mw", "brightness_i4_c", "footprint_ha", "burned_area_ha",
                          "wind_speed_kmh", "wind_from_degrees", "wind_gust_kmh", "air_temperature_c", "valid_at_utc"]
                writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                for incident in cast(list[Incident], self.store.payload()["incidents"]):
                    writer.writerow({**incident, **incident["weather"]})
                self.send_bytes(output.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8")
            elif route.path == "/api/context":
                self.send_json(self.store.context(query["id"][0]))
            elif route.path == "/atlas/sources":
                self.send_bytes((ATLAS_ROOT / "FUENTES.md").read_bytes(), "text/plain; charset=utf-8")
            elif route.path == '/api/webcams' and self.store.db:
                self.send_json(self.store.db.catalog(verified=True))
            elif route.path == '/api/webcam' and self.store.territorial:
                self.send_json(self.store.territorial.webcam(query['id'][0]))
            elif route.path == '/webcams/sources':
                self.send_bytes((DATA / 'espana-en-directo/docs/FUENTES.md').read_bytes(), 'text/plain; charset=utf-8')
            elif re.fullmatch(r'/roads/\d{1,2}/\d{1,5}/\d{1,5}\.png', route.path) and self.store.territorial:
                z, x, y = map(int, route.path.removesuffix('.png').split('/')[2:])
                body, mime = self.store.territorial.road(z, x, y)
                self.send_bytes(body, mime)
            elif re.fullmatch(r'/territorial/[a-f0-9]{24}\.img', route.path) and self.store.territorial:
                body, mime = self.store.territorial.media(route.path.rsplit('/', 1)[1].split('.')[0])
                self.send_bytes(body, mime)
            elif route.path == "/api/satellite":
                result = picture(self.store.find(query["id"][0]), query.get("mode", ["natural"])[0], self.store.offline, self.store.db)
                if self.store.db:
                    key = result['url'].rsplit('/', 1)[1].split('.')[0]
                    self.store.db.asset('satellite:' + key, 'satellite', dict(result), DATA / 'satellite' / (key + '.png'))
                self.send_json(result)
            elif re.fullmatch(r"/satellite/[a-f0-9]{24}\.png", route.path):
                self.send_bytes((DATA / "satellite" / route.path.rsplit("/", 1)[1]).read_bytes(), "image/png")
            elif route.path in {'/spain.geojson', '/neighbors.geojson', '/provinces.geojson', '/places.json'} and self.store.db:
                asset = self.store.db.get_asset('map:' + route.path[1:])
                if asset is None:
                    raise KeyError('Cartografía no importada')
                self.send_json(asset['data']['places'] if route.path == '/places.json' else asset['data'])
            elif route.path in {"/", "/index.html", "/styles.css", "/app.js", "/wind.js", "/simulation.js",
                                "/flow.js", "/flames.js", "/context.js", "/heat.js", "/infrastructure.js",
                                "/spain.geojson", "/neighbors.geojson", "/provinces.geojson", "/places.json",
                                "/vendor/leaflet.js", "/vendor/leaflet.css"}:
                super().do_GET()
            else:
                self.send_error(404)
        except (KeyError, ValueError) as error:
            self.send_json({"error": str(error)}, 400)
        except psycopg.Error:
            self.send_json({'error': 'Base de datos no disponible'}, 503)
        except (OSError, RuntimeError) as error:
            self.send_json({"error": str(error)}, 503)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--offline", action="store_true")
    options = parser.parse_args()
    database = Database()
    if not database.url:
        local_start()
    database.bootstrap()
    Handler.store = Store(options.offline, database)
    if not options.offline:
        threading.Thread(target=Handler.store.refresh_loop, daemon=True).start()
        if Handler.store.territorial:
            threading.Thread(target=Handler.store.territorial.verification_loop, daemon=True).start()
    print(f"FlareAI · puerto {options.port}", flush=True)
    ThreadingHTTPServer((options.host, options.port), Handler).serve_forever()
