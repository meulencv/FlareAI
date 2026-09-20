from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import re
import signal
import socket
import threading
import time
from datetime import datetime
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from socketserver import BaseServer
from typing import cast
from urllib.parse import parse_qs, urlencode, urlsplit

import psycopg

from context import ATLAS_ROOT, Atlas
from database import Database, local_start
from demo import DemoBridge, PHONE_ROOT
from director import Director
from territorial import Territorial
from twin import TwinDatabase
from gfs import DATA, ROOT, Snapshot, iso, update, utcnow
from incidents import Collection, Incident, assemble, refresh_fires
from satellite import picture


CARTOGRAPHY = {'/spain.geojson', '/neighbors.geojson', '/provinces.geojson', '/places.json'}
# Despliegue tras un proxy (Render): las órdenes de sala llegan con la dirección del proxy, no loopback.
# Con FLAREAI_PUBLIC_CONTROLS=1 se aceptan de cualquier cliente; queda la comprobación de origen del mismo host.
PUBLIC_CONTROLS = os.environ.get('FLAREAI_PUBLIC_CONTROLS') == '1'
# URL pública del propio servicio (Render la publica en RENDER_EXTERNAL_URL) para enlazar el 112 sin túnel.
PUBLIC_URL = (os.environ.get('FLAREAI_PUBLIC_URL') or os.environ.get('RENDER_EXTERNAL_URL') or '').rstrip('/')


class Cartography:
    """Cartografía estática servida desde SQL: se serializa y comprime una sola vez por proceso.
    Antes cada carga de página volvía a serializar 3,4 MB de provincias sin caché HTTP."""

    def __init__(self, database) -> None:
        self.db = database
        self.lock = threading.Lock()
        self.entries: dict[str, tuple[str, bytes, bytes]] = {}

    def entry(self, path: str) -> tuple[str, bytes, bytes]:
        with self.lock:
            cached = self.entries.get(path)
            if cached:
                return cached
            asset = self.db.get_asset('map:' + path[1:])
            if asset is None:
                raise KeyError('Cartografía no importada')
            raw = json.dumps(asset['data']['places'] if path == '/places.json' else asset['data'], ensure_ascii=False, allow_nan=False).encode()
            entry = ('"' + hashlib.sha256(raw).hexdigest()[:24] + '"', raw, gzip.compress(raw, 6))
            self.entries[path] = entry
            return entry


class Store:
    def __init__(self, offline: bool = False, database: Database | None = None, demo_enabled: bool = False, director_enabled: bool = False, hackathon: bool = False, presentation: bool = False, allow_outbound: bool = False) -> None:
        self.offline = offline
        self.presentation = presentation
        self.allow_outbound = allow_outbound
        self.hackathon = hackathon or presentation
        self.db = database
        self.territorial = Territorial(database, offline) if database else None
        self.cartography = Cartography(database) if database else None
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
        if self.director and self.director.scene:
            with self.director.lock:
                payload = self.director.scene.overlay(payload)
        if self.demo:
            payload['incidents'] = self.demo.overlay(cast(list[dict], payload['incidents']), dict(self.weather), now)
            payload['demo'] = self.demo.public_state()
        if self.director and self.director.scene:
            with self.director.lock:
                payload = self.director.scene.overlay(payload)
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

    def local_client(self) -> bool:
        """Órdenes de sala y configuración del 112: solo loopback, salvo despliegue tras proxy (ver PUBLIC_CONTROLS)."""
        return PUBLIC_CONTROLS or self.client_address[0] in {'127.0.0.1', '::1'}

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
        if path in {'/api/scenario', '/api/director/cancel-alert', '/api/admin/reset'}:
            if self.mobile_only or not self.local_client():
                self.send_error(404)
                return
            try:
                control_origin = urlsplit(self.headers.get('Origin', ''))
                if control_origin.netloc != self.headers.get('Host') or control_origin.scheme not in {'http', 'https'}:
                    raise PermissionError('Se requiere una orden local del mismo origen')
                if path == '/api/admin/reset':
                    if not self.store.db:
                        raise ValueError('No hay base de datos configurada')
                    with self.store.lock:
                        self.store.db.reset_demo()
                        if self.store.demo:
                            self.store.db.start_demo(self.store.demo.session_id)
                            self.store.demo.reset()
                        if self.store.director:
                            self.store.director.reset_demo()
                    self.send_json({'ok': True})
                    return
                director = self.store.director
                if not director or not director.scene:
                    raise ValueError('Arranca con --hackathon para activar el escenario')
                body = self.read_body()
                with director.lock:
                    if path.endswith('cancel-alert'):
                        director.cancel_alert(str(body.get('id', '')))
                    else:
                        director.scene.command(body)
                        director.save()
                self.send_json({'ok': True})
            except PermissionError as error:
                self.send_json({'error': str(error)}, 403)
            except (ValueError, KeyError, RuntimeError) as error:
                self.send_json({'error': str(error)}, 400)
            return
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
                if number != '112':
                    raise ValueError('Esta demo solo admite 112; bomberos recibe una llamada saliente')
                self.send_json(demo.create_call(owner, 'citizen'))
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

    def send_cartography(self, etag: str, raw: bytes, compressed: bytes) -> None:
        if self.headers.get('If-None-Match') == etag:
            self.send_response(304)
            self.send_header('ETag', etag)
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            return
        gzipped = 'gzip' in self.headers.get('Accept-Encoding', '')
        body = compressed if gzipped else raw
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'public, max-age=86400')
        self.send_header('ETag', etag)
        self.send_header('Vary', 'Accept-Encoding')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if gzipped:
            self.send_header('Content-Encoding', 'gzip')
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
        if route.path == '/healthz':
            # Sonda de la plataforma (Render): el servidor solo atiende una vez cargados datos y escenario.
            director = self.store.director
            if director:
                with director.lock:
                    status = str(director.state['status'])
            self.send_json({'ok': True, 'director': status if director else 'disabled'})
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
                    self.send_json({'incidents': [{'id': i['id'], 'label': i.get('demo_report', {}).get('location', {}).get('label', i['name']),
                        'precision': i.get('demo_report', {}).get('location', {}).get('precision', 'area'), 'resources': [a['resource'] | {'status': a['status']} for a in assignments.values() if a['incident_id'] == i['id'] and a['status'] != 'returning']}
                        for i in cast(list[dict], self.store.payload()['incidents']) if (i.get('demo_report') or i.get('sensor_report') or i.get('scene_report'))
                        and not i.get('demo_report', {}).get('cancelled') and i.get('scenario', {}).get('phase') not in {'closed', 'releasing'}]})
            elif route.path == '/112/api/brief' and self.store.demo:
                self.send_json(self.store.demo.brief(query.get('run_id', [''])[0], self.browser_token()))
            elif route.path == '/api/demo/setup' and self.store.demo:
                if not self.local_client():
                    raise PermissionError('Configuración solo desde el ordenador local')
                runtime = ROOT / '.local/demo-public.json'
                tunnel = json.loads(runtime.read_text()).get('url') if runtime.exists() else None
                public = tunnel
                phone_url = alert_url = None
                hosted_app = False
                if self.store.presentation:
                    configured = cast(TwinDatabase, self.store.db).setting('phone-web').get('url', '')
                    target = urlsplit(configured)
                    hosted = f'https://{target.netloc}' if target.scheme == 'https' and target.hostname and not target.username and not target.password else None
                    hosted_app = bool(hosted)
                    public = hosted or tunnel
                    if hosted:
                        fragment = '#' + urlencode({'code': os.environ['FLAREAI_DEMO_ACCESS_CODE']}) if os.environ.get('FLAREAI_DEMO_ACCESS_CODE') else ''
                        phone_url = hosted + '/112/' + fragment
                        alert_url = hosted + '/112/alerts/' + fragment
                if not phone_url and tunnel:
                    phone_url, alert_url = tunnel + '/112/', tunnel + '/112/alerts/'
                if not phone_url and PUBLIC_URL.startswith('https://'):
                    # Sin túnel ni App alojada, el propio servicio publicado sirve /112/ y /112/alerts/.
                    public = public or PUBLIC_URL
                    phone_url, alert_url = PUBLIC_URL + '/112/', PUBLIC_URL + '/112/alerts/'
                self.send_json({'public_url': public, 'phone_url': phone_url, 'alert_url': alert_url, 'cloud': hosted_app, 'local_url': '/112/',
                                'ready': bool(self.store.demo.provider.ready), 'session_id': self.store.demo.session_id})
            elif route.path.startswith('/api/demo/report/') and self.store.demo:
                run_id = route.path.rsplit('/', 1)[1]
                with self.store.demo.lock:
                    call = self.store.demo.calls[run_id]
                    self.send_json({'source': 'Parte de bomberos de demostración' if call.get('role') == 'firefighter' else 'Llamada web de demostración, no confirmación oficial',
                                    'summary': call['summary'], 'location': call['location'], 'part': call.get('part', {})})
            elif route.path == '/api/scenario/roads' and self.store.director and self.store.director.scene:
                from local_routes import in_demo
                bounds = [float(v) for v in query.get('bbox', [''])[0].split(',')]
                if len(bounds) != 4 or not in_demo(bounds[:2]) or not in_demo(bounds[2:]) or not bounds[0] < bounds[2] or not bounds[1] < bounds[3]:
                    raise ValueError('Caja fuera del área precargada')
                self.send_json({'roads': self.store.director.router.demo_roads(bounds), 'attribution': '© OpenStreetMap contributors · ODbL'})
            elif route.path == '/api/director/history' and self.store.director and self.store.db:
                self.send_json(self.store.db.director_history(self.store.director.session_id))
            elif route.path == '/api/brain' and self.store.presentation:
                from reports import brain_notes, sync_memories
                cloud = cast(TwinDatabase, self.store.db)
                def load_brain():
                    sync_memories(cloud)
                    return brain_notes(cloud)
                self.send_json({'notes': cloud.cached('brain', 5, load_brain)})
            elif re.fullmatch(r'/api/reports/[a-f0-9]{24}\.pdf', route.path) and self.store.presentation:
                from reports import pdf_bytes, report_markdown
                identifier = route.path.rsplit('/', 1)[1].removesuffix('.pdf')
                report = cast(TwinDatabase, self.store.db).document('report:' + identifier)
                if report is None:
                    raise KeyError('Informe no encontrado')
                self.send_bytes(pdf_bytes(report_markdown(report)), 'application/pdf')
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
            elif route.path in CARTOGRAPHY and self.store.cartography:
                self.send_cartography(*self.store.cartography.entry(route.path))
            elif route.path in {"/", "/index.html", "/styles.css", "/app.js", "/wind.js", "/simulation.js",
                                "/flow.js", "/flames.js", "/cartography.js", "/context.js", "/heat.js", "/infrastructure.js", "/director.js", "/scene.js", "/traffic.js", "/operations.js", "/aura.js",
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
    # PORT lo fija la plataforma de despliegue (Render usa 10000); en local sigue siendo 8090.
    parser.add_argument("--port", type=int, default=int(os.environ.get('PORT') or 8090))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument('--mobile-port', type=int, default=8112)
    parser.add_argument('--hackathon', action='store_true', help='Activa el escenario de sala Barcelona; requiere red precargada')
    parser.add_argument('--presentation', action='store_true', help='Centro local, estado dinámico Twin y flujo de presentación')
    parser.add_argument('--allow-outbound', action='store_true', help='Autoriza llamadas reales a los contactos habilitados en Twin')
    options = parser.parse_args()
    if options.presentation and options.offline:
        parser.error('--presentation necesita Twin y HappyRobot online')
    # FLAREAI_ALLOW_OUTBOUND=1 equivale a --allow-outbound cuando el comando de arranque es fijo (Render).
    allow_outbound = options.allow_outbound or os.environ.get('FLAREAI_ALLOW_OUTBOUND') == '1'

    def terminate(signum: int, frame: object) -> None:
        # Las plataformas detienen el proceso con SIGTERM: se trata como Ctrl-C para liberar la sala y cerrar ordenadamente.
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
    with ThreadingHTTPServer((options.host, options.port), Handler) as server:
        mobile = None
        worker = None
        store = None
        mobile_started = False
        try:
            if not options.offline:
                mobile = ThreadingHTTPServer(('127.0.0.1', options.mobile_port), MobileHandler)
            database: Database = TwinDatabase() if options.presentation else Database()
            if not database.url:
                local_start()
            database.bootstrap()
            store = Handler.store = Store(options.offline, database, demo_enabled=not options.offline, director_enabled=True,
                hackathon=options.hackathon, presentation=options.presentation, allow_outbound=allow_outbound)
            if store.director:
                worker = threading.Thread(target=store.director.loop, daemon=True)
                worker.start()
            if store.demo:
                threading.Thread(target=store.demo.loop, daemon=True).start()
            if mobile:
                threading.Thread(target=mobile.serve_forever, daemon=True).start()
                mobile_started = True
            if not options.offline:
                threading.Thread(target=store.refresh_loop, daemon=True).start()
                if store.territorial:
                    threading.Thread(target=store.territorial.verification_loop, daemon=True).start()
            print(f"FlareAI · puerto {options.port}", flush=True)
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if store and store.director:
                store.director.stop_event.set()
            if mobile_started and mobile:
                mobile.shutdown()
            if mobile:
                mobile.server_close()
            if store and store.demo:
                store.demo.close()
            if worker:
                worker.join(timeout=25)
            if store and store.demo and isinstance(store.db, TwinDatabase):
                try:
                    store.db.stop_room(store.demo.session_id)
                except (RuntimeError, PermissionError):
                    pass

