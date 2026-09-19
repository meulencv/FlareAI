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
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from socketserver import BaseServer
from typing import cast
from urllib.parse import parse_qs, urlsplit

import psycopg

from context import ATLAS_ROOT, Atlas
from database import Database, local_start
from demo import DemoBridge, PHONE_ROOT
from director import Director
from territorial import Territorial
from gfs import DATA, ROOT, Snapshot, iso, update, utcnow
from incidents import Collection, Incident, assemble, refresh_fires
from satellite import picture


class Store:
    def __init__(self, offline: bool = False, database: Database | None = None, demo_enabled: bool = False, director_enabled: bool = False) -> None:
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
        self.demo = DemoBridge(database) if database and demo_enabled else None
        self.director = Director(self) if self.demo and director_enabled and not offline else None

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
            payload: dict[str, object] = {
                "generated_at": iso(now),
                "status": "offline" if self.offline else "stale" if self.errors or weather_age > 7200 or fire_age > 7200 or model_age > 43200 else "ready",
                "errors": dict(self.errors),
                "incidents": [{**i, 'confirmation': confirmed.get(i['id'], {'status': 'unconfirmed', 'reason': 'FIRMS identifica anomalías térmicas; no confirma incendios forestales.'})} for i in incidents], "wind": self.weather,
                "fires_checked_at": self.fires["analysis_at_utc"], "window_hours": 24,
                "fire_refresh_seconds": 1800, "weather_refresh_seconds": 600,
                "classification": "thermal_clusters_not_exhaustive_fire_inventory",
            }
        if self.demo:
            payload['incidents'] = self.demo.overlay(cast(list[dict], payload['incidents']), dict(self.weather), now)
            payload['demo'] = self.demo.public_state()
        return payload

    def context(self, identifier: str) -> dict:
        incident = self.find(identifier)
        with self.lock:
            weather_error = "weather" in self.errors
        if self.db:
            atlas = self.db.nearby_atlas(dict(incident))
        else:
            with self.atlas_lock:
                if self.atlas is None:
                    self.atlas = Atlas.load()
                atlas = self.atlas
        result = atlas.analyze(dict(incident), now=utcnow(), offline=self.offline, weather_error=weather_error)
        if incident.get('source_kind') == 'call':
            result['method'] = 'Entorno del punto comunicado en llamada de demo. Ubicación orientativa, sin huella térmica medida.'
            result['geometry_role'] = 'illustrative_report_location'
        return result

    def find(self, identifier: str) -> Incident:
        for incident in cast(list[Incident], self.payload()['incidents']):
            if incident['id'] == identifier:
                return incident
        raise KeyError("Zona no encontrada")


class Handler(SimpleHTTPRequestHandler):
    store: Store
    mobile_only = False

    def __init__(self, request: socket.socket, client_address: tuple[str, int], server: BaseServer) -> None:
        super().__init__(request, client_address, server, directory=str(ROOT / "static"))

    def end_headers(self) -> None:
        if self.path.startswith('/112/'):
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Permissions-Policy', 'microphone=(self)')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; connect-src 'self' wss://*.happyrobot.ai https://*.happyrobot.ai; style-src 'self'; media-src 'self' blob:; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'")
        super().end_headers()

    def browser_token(self) -> str:
        cookie: SimpleCookie = SimpleCookie()
        cookie.load(self.headers.get('Cookie', ''))
        return cookie['flare_demo'].value if 'flare_demo' in cookie else ''

    def read_body(self) -> dict:
        size = int(self.headers.get('Content-Length', '0'))
        if not 0 <= size <= 4096 or self.headers.get_content_type() != 'application/json':
            raise ValueError('Se requiere JSON pequeño')
        body = json.loads(self.rfile.read(size) or b'{}')
        if not isinstance(body, dict):
            raise ValueError('Objeto JSON requerido')
        return body

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path not in {'/112/api/session', '/112/api/call', '/112/api/stop'} or not self.store.demo:
            self.send_error(404)
            return
        try:
            origin = self.headers.get('Origin')
            if origin and urlsplit(origin).netloc != self.headers.get('Host'):
                raise PermissionError('Origen no permitido')
            body = self.read_body()
            demo = self.store.demo
            if path == '/112/api/session':
                if demo.authorized(self.browser_token()):
                    self.send_json({'ready': True})
                    return
                token = demo.open_browser()
                self.send_response(200)
                secure = '; Secure' if self.headers.get('X-Forwarded-Proto') == 'https' else ''
                self.send_header('Set-Cookie', f'flare_demo={token}; Path=/112/; HttpOnly; SameSite=Strict; Max-Age=21600{secure}')
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                content = b'{"ready":true}'
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            elif path == '/112/api/call':
                owner = self.browser_token()
                if not demo.authorized(owner):
                    raise PermissionError('Abre primero el marcador de la demo')
                number = body.get('number', '112')
                if number not in {'112', '123'}:
                    raise ValueError('Número no disponible')
                binding = None
                if number == '123':
                    incident = cast(dict, dict(self.store.find(str(body.get('incident_id', '')))))
                    report = incident.get('demo_report')
                    if not report or report.get('cancelled'):
                        raise ValueError('Aviso no disponible')
                    resource_id = body.get('resource_id')
                    if resource_id:
                        assignment = self.store.director.public_state()['assignments'].get(resource_id) if self.store.director else None
                        if not assignment or assignment['incident_id'] != incident['id'] or assignment['status'] == 'returning':
                            raise ValueError('Recurso no asignado al aviso')
                    binding = {**report['location'], 'run_id': report['run_id'], 'incident_id': incident['id'], 'resource_id': resource_id}
                self.send_json(demo.create_call(owner, 'firefighter' if number == '123' else 'citizen', binding))
            else:
                demo.stop(str(body.get('run_id', '')), self.browser_token())
                self.send_json({'ok': True})
        except PermissionError as error:
            self.send_json({'error': str(error)}, 403)
        except (ValueError, KeyError):
            self.send_json({'error': 'Solicitud no válida'}, 400)
        except Exception:
            self.send_json({'error': 'No se pudo contactar con HappyRobot. Reintenta desde el marcador.'}, 503)

    def log_message(self, fmt: str, *args: object) -> None:
        if self.path.startswith('/112/'):
            print(f'{self.address_string()} {self.command} {urlsplit(self.path).path}', flush=True)
        else:
            super().log_message(fmt, *args)

    def do_HEAD(self) -> None:
        self.send_error(405)

    def send_bytes(self, body: bytes, mime: str, status: int = 200, download: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store" if mime.startswith("application") or self.path.startswith('/112/') else "public, max-age=3600")
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
        if self.mobile_only and route.path == '/':
            self.send_response(302)
            self.send_header('Location', '/112/')
            self.end_headers()
            return
        if self.mobile_only and not route.path.startswith('/112/'):
            self.send_error(404)
            return
        try:
            if route.path in {'/112/alerts/', '/112/alerts.html', '/112/alerts.js', '/112/alerts.css'}:
                name = 'alerts.html' if route.path.endswith('/') else route.path.rsplit('/', 1)[1]
                mime = 'text/html; charset=utf-8' if name.endswith('.html') else 'text/css' if name.endswith('.css') else 'text/javascript'
                self.send_bytes((PHONE_ROOT / name).read_bytes(), mime)
            elif route.path in {'/112/', '/112/index.html', '/112/app.js', '/112/audio.js', '/112/styles.css'}:
                name = route.path.rsplit('/', 1)[1] or 'index.html'
                mime = 'text/html; charset=utf-8' if name.endswith('.html') else 'text/css' if name.endswith('.css') else 'text/javascript'
                self.send_bytes((PHONE_ROOT / name).read_bytes(), mime)
            elif route.path == '/112/api/status':
                self.send_json({'integrated': True, 'browser_ready': bool(self.store.demo and self.store.demo.authorized(self.browser_token())),
                                'configured': bool(self.store.demo and self.store.demo.provider.ready),
                                'firefighter_configured': bool(self.store.demo and self.store.demo.provider.responder_ready)})
            elif route.path in {'/112/api/incidents', '/112/api/alerts'} and self.store.demo:
                if not self.store.demo.authorized(self.browser_token()):
                    raise PermissionError('Abre primero la demo')
                if route.path.endswith('/alerts'):
                    after = int(query['after'][0]) if 'after' in query else None
                    if after is not None and not 0 <= after <= 1000000:
                        raise ValueError('Secuencia no válida')
                    self.send_json(self.store.director.alert_feed(after) if self.store.director else {'session_id': self.store.demo.session_id, 'sequence': 0, 'events': [], 'mode': 'simulation_only'})
                else:
                    assignments = self.store.director.public_state()['assignments'] if self.store.director else {}
                    self.send_json({'incidents': [{'id': i['id'], 'label': i['demo_report']['location']['label'],
                        'precision': i['demo_report']['location']['precision'], 'resources': [a['resource'] | {'status': a['status']} for a in assignments.values() if a['incident_id'] == i['id'] and a['status'] != 'returning']}
                        for i in cast(list[dict], self.store.payload()['incidents']) if i.get('demo_report') and not i['demo_report'].get('cancelled')]})
            elif route.path == '/112/api/brief' and self.store.demo:
                self.send_json(self.store.demo.brief(query.get('run_id', [''])[0], self.browser_token()))
            elif route.path == '/api/demo/setup' and self.store.demo:
                if self.client_address[0] not in {'127.0.0.1', '::1'}:
                    raise PermissionError('Configuración solo desde el ordenador local')
                runtime = ROOT / '.local/demo-public.json'
                public = json.loads(runtime.read_text()).get('url') if runtime.exists() else None
                self.send_json({'public_url': public, 'local_url': '/112/',
                                'ready': bool(self.store.demo.provider.ready), 'session_id': self.store.demo.session_id})
            elif route.path.startswith('/api/demo/report/') and self.store.demo:
                run_id = route.path.rsplit('/', 1)[1]
                with self.store.demo.lock:
                    call = self.store.demo.calls[run_id]
                    self.send_json({'source': 'Parte de bomberos de demostración' if call.get('role') == 'firefighter' else 'Llamada web de demostración, no confirmación oficial',
                                    'summary': call['summary'], 'location': call['location'], 'part': call.get('part', {})})
            elif route.path == '/api/director':
                self.send_json(self.store.director.public_state() if self.store.director else {'status': 'disabled', 'events': [], 'assignments': {}, 'alerts': {}})
            elif route.path == "/api/data":
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
                                "/flow.js", "/flames.js", "/context.js", "/heat.js", "/infrastructure.js", "/director.js",
                                "/spain.geojson", "/neighbors.geojson", "/provinces.geojson", "/places.json",
                                "/vendor/leaflet.js", "/vendor/leaflet.css"}:
                super().do_GET()
            else:
                self.send_error(404)
        except PermissionError:
            self.send_json({'error': 'Acceso no autorizado'}, 403)
        except (KeyError, ValueError) as error:
            self.send_json({"error": str(error)}, 400)
        except psycopg.Error:
            self.send_json({'error': 'Base de datos no disponible'}, 503)
        except (OSError, RuntimeError) as error:
            self.send_json({"error": str(error)}, 503)


class MobileHandler(Handler):
    mobile_only = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument('--mobile-port', type=int, default=8112)
    options = parser.parse_args()
    database = Database()
    if not database.url:
        local_start()
    database.bootstrap()
    Handler.store = Store(options.offline, database, demo_enabled=not options.offline, director_enabled=True)
    if Handler.store.director:
        threading.Thread(target=Handler.store.director.loop, daemon=True).start()
    if Handler.store.demo:
        threading.Thread(target=Handler.store.demo.loop, daemon=True).start()
        mobile = ThreadingHTTPServer(('127.0.0.1', options.mobile_port), MobileHandler)
        threading.Thread(target=mobile.serve_forever, daemon=True).start()
    if not options.offline:
        threading.Thread(target=Handler.store.refresh_loop, daemon=True).start()
        if Handler.store.territorial:
            threading.Thread(target=Handler.store.territorial.verification_loop, daemon=True).start()
    print(f"FlareAI · puerto {options.port}", flush=True)
    ThreadingHTTPServer((options.host, options.port), Handler).serve_forever()
