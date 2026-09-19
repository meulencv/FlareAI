from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import subprocess
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from context import ATLAS_ROOT, GRID_FIELDS, Atlas

ROOT = Path(__file__).resolve().parent
PG = ROOT / '.local/pg'
CATALOG = ROOT / 'data/espana-en-directo/data/catalog.json'
TABLES = ('sources', 'imports', 'grid', 'facilities', 'cameras', 'snapshots', 'incidents',
          'observations', 'confirmations', 'assets', 'settings', 'camera_checks', 'demo_sessions', 'demo_calls',
          'director_state', 'director_events')


def local_start() -> None:
    binary = PG / 'dist/bin'
    if not (binary / 'pg_ctl').exists():
        raise RuntimeError('Instala PostgreSQL en .local/pg/dist o configura FLAREAI_DATABASE_URL.')
    PG.mkdir(parents=True, exist_ok=True)
    PG.chmod(0o700)
    data = PG / 'data'
    if not (data / 'PG_VERSION').exists():
        subprocess.run([str(binary / 'initdb'), '-D', str(data), '-U', 'flareai',
                        '--auth-local=trust', '--auth-host=reject', '-E', 'UTF8', '--no-locale'], check=True)
    status = subprocess.run([str(binary / 'pg_ctl'), '-D', str(data), 'status'], capture_output=True)
    if status.returncode:
        subprocess.run([str(binary / 'pg_ctl'), '-D', str(data), '-l', str(PG / 'postgres.log'),
                        '-o', f"-p 54330 -c listen_addresses='' -k {PG}", '-w', 'start'], check=True)
    with psycopg.connect(host=str(PG), port=54330, user='flareai', dbname='postgres', autocommit=True) as conn:
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname='flareai'").fetchone():
            conn.execute('CREATE DATABASE flareai')


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc).replace(tzinfo=None)


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class Database:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or os.environ.get('FLAREAI_DATABASE_URL')

    @contextmanager
    def connect(self) -> Iterator[Any]:
        options: dict[str, Any] = {'row_factory': dict_row, 'connect_timeout': 5,
                                  'options': '-c statement_timeout=20000 -c timezone=UTC'}
        if self.url:
            conn = psycopg.connect(self.url, **options)
        else:
            conn = psycopg.connect(host=str(PG), port=54330, user='flareai', dbname='flareai', **options)
        with conn:
            yield conn

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.execute('SELECT pg_advisory_xact_lock(804021)')
            conn.execute((ROOT / 'schema.sql').read_text())

    def director_setting(self, value: dict | None = None) -> dict:
        with self.connect() as conn:
            if value is not None:
                conn.execute("INSERT INTO flare_settings VALUES ('director-workflow',%s) ON CONFLICT(id) DO UPDATE SET data=EXCLUDED.data", (Jsonb(value),))
            row = conn.execute("SELECT data FROM flare_settings WHERE id='director-workflow'").fetchone()
            return row['data'] if row else {}

    def save_director(self, session_id: str, state: dict) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO flare_director_state(session_id,data) VALUES (%s,%s) ON CONFLICT(session_id) DO UPDATE SET data=EXCLUDED.data,updated_at=(now() AT TIME ZONE 'UTC')", (session_id, Jsonb(state)))
            for event in state['events']:
                conn.execute('INSERT INTO flare_director_events VALUES (%s,%s,%s) ON CONFLICT DO NOTHING', (session_id, event['sequence'], Jsonb(event)))

    def source(self, conn: Any, identifier: str, data: dict) -> None:
        conn.execute('INSERT INTO flare_sources VALUES (%s,%s) ON CONFLICT (id) DO UPDATE SET data=EXCLUDED.data',
                     (identifier, Jsonb(data)))

    def import_atlas(self) -> None:
        with self.connect() as conn:
            conn.execute('SELECT pg_advisory_xact_lock(804022)')
            conn.execute('SET LOCAL statement_timeout=0')
            self.source(conn, 'atlas-grid-2021-2019', {'population_year': 2021, 'landcover_year': 2019, 'license_url': '/atlas/sources'})
            self.source(conn, 'osm-2026-09-18', {'date': '2026-09-18', 'license': 'ODbL 1.0', 'license_url': '/atlas/sources'})
            for kind, filename, source in [('grid', 'espana_rejilla_1km.csv.gz', 'atlas-grid-2021-2019'),
                                            ('facilities', 'instalaciones_atencion_incendios.csv', 'osm-2026-09-18')]:
                if conn.execute('SELECT 1 FROM flare_imports WHERE id=%s', (source,)).fetchone():
                    continue
                path = ATLAS_ROOT / 'output' / filename
                stream = gzip.open(path, 'rt', encoding='utf-8', newline='') if kind == 'grid' else path.open(encoding='utf-8', newline='')
                count = 0
                with stream, conn.cursor() as cur:
                    columns = 'id,source_id,lon,lat,population,data' if kind == 'grid' else 'id,source_id,lon,lat,category,name,data'
                    with cur.copy(f'COPY flare_{kind} ({columns}) FROM STDIN') as copy:
                        for row in csv.DictReader(stream):
                            lon, lat = float(row['lon']), float(row['lat'])
                            if not math.isfinite(lon + lat):
                                raise ValueError('Coordenadas inválidas en atlas')
                            if kind == 'grid':
                                identifier = f"cell:{int(float(row['x_min_3035']))}:{int(float(row['y_min_3035']))}"
                                population = float(row['poblacion']) if row['poblacion'] else None
                                copy.write_row((identifier, source, lon, lat, population, Jsonb(row)))
                            else:
                                identifier = f"{row['osm_type']}:{row['osm_id']}"
                                data = {'id': identifier, 'lon': lon, 'lat': lat, 'name': row['nombre'],
                                        'category': row['categoria'], 'priority': row['prioridad_preventiva'],
                                        'reason': row['criterio'], 'source_url': row['url_osm'],
                                        'coordinate_method': row['metodo_coordenada'], 'boundary_location': row['ubicacion_limite'],
                                        'source_date': row['fecha_datos_osm'], 'grid_x': float(row['x_min_3035']),
                                        'grid_y': float(row['y_min_3035']), 'original': row}
                                copy.write_row((identifier, source, lon, lat, row['categoria'], row['nombre'], Jsonb(data)))
                            count += 1
                conn.execute('INSERT INTO flare_imports(id,source_id,rows) VALUES (%s,%s,%s)', (source, source, count))
                self.asset(f'import:{source}', 'source_archive', {'sha256': digest(path), 'rows': count}, path, source, conn)

    def import_catalog(self) -> None:
        with self.connect() as conn:
            conn.execute('SELECT pg_advisory_xact_lock(804023)')
            if conn.execute("SELECT 1 FROM flare_imports WHERE id='webcams-initial'").fetchone():
                return
            catalog = json.loads(CATALOG.read_text())
            for source in catalog['sources']:
                self.source(conn, 'camera:' + source['id'], source)
            from territorial import allowed_image
            for camera in catalog['cameras']:
                if not math.isfinite(camera['lon'] + camera['lat']) or not (-19 <= camera['lon'] <= 5 and 27 <= camera['lat'] <= 44.5):
                    raise ValueError('Coordenadas de cámara inválidas')
                if camera['kind'] == 'snapshot' and not allowed_image(camera.get('imageUrl', '')):
                    raise ValueError('Imagen de cámara fuera de fuentes admitidas')
                conn.execute('INSERT INTO flare_cameras VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING',
                             (camera['id'], 'camera:' + camera['source'], camera['lon'], camera['lat'], camera['name'], camera['kind'], Jsonb(camera)))
            self.source(conn, 'webcams', {'description': 'Catálogo Faro importado; fechas originales por proveedor', 'license_url': '/webcams/sources'})
            conn.execute("INSERT INTO flare_imports(id,source_id,rows) VALUES ('webcams-initial','webcams',%s)", (len(catalog['cameras']),))

    def nearby_atlas(self, incident: dict) -> Atlas:
        from context import RADIUS_KM
        from shapely.geometry import shape
        west, south, east, north = shape(incident['footprint']).bounds
        dx = RADIUS_KM / (111.32 * math.cos(math.radians(incident['lat'])))
        dy = RADIUS_KM / 111.32
        bounds = (west - dx, east + dx, south - dy, north + dy)
        with self.connect() as conn:
            cells = conn.execute('SELECT data FROM flare_grid WHERE lon BETWEEN %s AND %s AND lat BETWEEN %s AND %s', bounds).fetchall()
            facilities = conn.execute('SELECT data FROM flare_facilities WHERE lon BETWEEN %s AND %s AND lat BETWEEN %s AND %s', bounds).fetchall()
        grid = np.array([tuple(float(r['data'][name]) if r['data'][name] else math.nan for name in GRID_FIELDS) for r in cells],
                        dtype=[(name, 'f8') for name in GRID_FIELDS])
        return Atlas(grid, [{k: v for k, v in r['data'].items() if k != 'original'} for r in facilities])

    def catalog(self, verified: bool = False) -> dict:
        with self.connect() as conn:
            if verified:
                from territorial import UNAVAILABLE_IMAGES
                rows = conn.execute("SELECT c.data, h.media_kind, h.checked_at FROM flare_cameras c JOIN flare_camera_checks h ON h.id=c.id WHERE h.status='available' AND h.data->>'method' IN ('image_decoded','browser_video_playing') AND coalesce(h.data->>'sha256','') <> ALL(%s) AND h.valid_until > (now() AT TIME ZONE 'UTC') ORDER BY c.id", (list(UNAVAILABLE_IMAGES),))
                cameras = [{**r['data'], 'kind': r['media_kind'], 'verified_at': r['checked_at'].isoformat() + 'Z'} for r in rows]
            else:
                cameras = [r['data'] for r in conn.execute('SELECT data FROM flare_cameras ORDER BY id')]
            return {'cameras': cameras,
                    'sources': [r['data'] for r in conn.execute("SELECT data FROM flare_sources WHERE id LIKE 'camera:%%' ORDER BY id")],
                    'mode': 'verified_media' if verified else 'imported_catalog', 'exhaustive': False}

    def camera_check(self, identifier: str, status: str, media_kind: str | None, data: dict) -> None:
        from datetime import timedelta
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        hours = 6 if status == 'available' else 24 if status == 'external' else 1
        expires = now + timedelta(hours=hours)
        if status == 'available' and media_kind == 'player':
            expires = min(expires, datetime.fromtimestamp(data.get('browser_verified_until', 0), timezone.utc).replace(tzinfo=None))
        with self.connect() as conn:
            conn.execute('INSERT INTO flare_camera_checks VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET status=EXCLUDED.status,checked_at=EXCLUDED.checked_at,valid_until=EXCLUDED.valid_until,media_kind=EXCLUDED.media_kind,data=EXCLUDED.data',
                         (identifier, status, now, expires, media_kind, Jsonb(data)))

    @contextmanager
    def verification_lock(self, key: int) -> Iterator[bool]:
        with self.connect() as conn:
            yield conn.execute('SELECT pg_try_advisory_xact_lock(%s) AS acquired', (key,)).fetchone()['acquired']

    def camera_checks(self) -> dict:
        with self.connect() as conn:
            rows = conn.execute('SELECT id,status,checked_at,valid_until,media_kind,data FROM flare_camera_checks')
            return {r['id']: r for r in rows}

    def camera(self, identifier: str) -> dict:
        with self.connect() as conn:
            row = conn.execute('SELECT data FROM flare_cameras WHERE id=%s', (identifier,)).fetchone()
            if row is None:
                raise KeyError('Cámara desconocida')
            return row['data']

    def snapshot(self, kind: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute('SELECT data FROM flare_snapshots WHERE kind=%s ORDER BY valid_at DESC LIMIT 1', (kind,)).fetchone()
            return row['data'] if row else None

    def save_snapshot(self, kind: str, value: dict) -> None:
        valid = value['valid_at_utc'] if kind == 'weather' else value['analysis_at_utc']
        identifier = f'{kind}:{valid}'
        with self.connect() as conn:
            conn.execute('INSERT INTO flare_snapshots VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET data=EXCLUDED.data',
                         (identifier, kind, utc(valid), Jsonb(value)))

    def save_incidents(self, incidents: list[dict]) -> None:
        with self.connect() as conn:
            for item in incidents:
                conn.execute('INSERT INTO flare_incidents VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET lat=EXCLUDED.lat,lon=EXCLUDED.lon,last_seen=EXCLUDED.last_seen,data=EXCLUDED.data',
                             (item['id'], item['lat'], item['lon'], utc(item['last_seen']), Jsonb(item)))
                for detection in item['detections']:
                    identifier = detection.get('id') or hashlib.sha256(json.dumps(detection, sort_keys=True).encode()).hexdigest()
                    conn.execute('INSERT INTO flare_observations VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET incident_id=EXCLUDED.incident_id',
                                 (identifier, item['id'], detection['lat'], detection['lon'], utc(detection['at']), Jsonb(detection)))

    def start_demo(self, identifier: str) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO flare_demo_sessions VALUES (%s,now() AT TIME ZONE 'UTC')", (identifier,))

    def save_demo_call(self, session_id: str, run_id: str, data: dict) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO flare_demo_calls VALUES (%s,%s,now() AT TIME ZONE 'UTC',%s) ON CONFLICT (id) DO UPDATE SET updated_at=EXCLUDED.updated_at,data=EXCLUDED.data WHERE flare_demo_calls.session_id=EXCLUDED.session_id", (run_id, session_id, Jsonb(data)))

    def confirmations(self, at: datetime) -> dict[str, dict]:
        moment = at.astimezone(timezone.utc).replace(tzinfo=None)
        with self.connect() as conn:
            rows = conn.execute('SELECT DISTINCT ON (incident_id) * FROM flare_confirmations WHERE confirmed_at<=%s ORDER BY incident_id,confirmed_at DESC,id DESC', (moment,))
            return {r['incident_id']: {'status': 'confirmed', 'source_name': r['source_name'], 'source_url': r['source_url'],
                                       'confirmed_at': r['confirmed_at'].isoformat() + 'Z', 'valid_until': r['valid_until'].isoformat() + 'Z'}
                    for r in rows if r['status'] == 'confirmed' and r['valid_until'] >= moment}

    def asset(self, identifier: str, kind: str, data: dict, path: Path | None = None,
              source: str | None = None, conn: Any = None) -> None:
        if conn is None:
            with self.connect() as connection:
                self.asset(identifier, kind, data, path, source, connection)
            return
        relative = str(path.relative_to(ROOT)) if path else None
        conn.execute('INSERT INTO flare_assets VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET path=EXCLUDED.path,data=EXCLUDED.data',
                     (identifier, kind, source, relative, Jsonb(data)))

    def get_asset(self, identifier: str) -> dict | None:
        with self.connect() as conn:
            return conn.execute('SELECT * FROM flare_assets WHERE id=%s', (identifier,)).fetchone()

    def bootstrap(self) -> None:
        self.migrate()
        self.import_atlas()
        self.import_catalog()
        for kind, path in [('fires', ROOT / 'data/firms/focos_espana.geojson'), ('weather', ROOT / 'data/latest.json')]:
            if self.snapshot(kind) is None:
                self.save_snapshot(kind, json.loads(path.read_text()))
        from context import POTENTIAL_MODEL
        with self.connect() as conn:
            conn.execute('INSERT INTO flare_settings VALUES (%s,%s) ON CONFLICT DO NOTHING', ('attention-potential-v1', Jsonb(POTENTIAL_MODEL)))
            self.source(conn, 'ign-roads', {'url': 'https://servicios.idee.es/wms-inspire/transportes',
                                          'layer': 'TN.RoadTransportNetwork.RoadLink', 'license': 'CC BY 4.0 · SCNE/IGN'})
        for path in (ROOT / 'static').glob('*.geojson'):
            if self.get_asset('map:' + path.name) is None:
                self.asset('map:' + path.name, 'cartography', json.loads(path.read_text()), path)
        path = ROOT / 'static/places.json'
        if self.get_asset('map:places.json') is None:
            self.asset('map:places.json', 'cartography', {'places': json.loads(path.read_text())}, path)
        for path in (ROOT / 'data/satellite').glob('*.json'):
            if not path.name.endswith('.request.json') and self.get_asset('satellite:' + path.stem) is None:
                self.asset('satellite:' + path.stem, 'satellite', json.loads(path.read_text()), path.with_suffix('.png'))

    def satellite(self, bbox: list[float], mode: str) -> dict | None:
        with self.connect() as conn:
            rows = conn.execute("SELECT data,path FROM flare_assets WHERE kind='satellite' AND data->'bbox'=%s AND data->>'mode'=%s ORDER BY data->>'checked_at_utc' DESC", (Jsonb(bbox), mode))
            return next((row['data'] for row in rows if row['path'] and (ROOT / row['path']).is_file()), None)

    def stats(self) -> dict:
        with self.connect() as conn:
            return {table: conn.execute(f'SELECT count(*) AS n FROM flare_{table}').fetchone()['n'] for table in TABLES}

    def export(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        with self.connect() as conn:
            conn.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            (directory / 'schema.sql').write_text((ROOT / 'schema.sql').read_text())
            for table in TABLES:
                with conn.cursor(name='export_' + table) as cur, (directory / f'flare_{table}.jsonl').open('x') as output:
                    order = {'director_state': 'session_id', 'director_events': 'session_id,sequence'}.get(table, 'id')
                    columns = "id,data - 'hook_key' AS data" if table == 'settings' else '*'
                    cur.execute(f'SELECT {columns} FROM flare_{table} ORDER BY {order}')
                    for row in cur:
                        output.write(json.dumps(row, ensure_ascii=False, default=lambda v: v.isoformat()) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['start', 'import', 'stats', 'export'])
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()
    db = Database()
    if args.command == 'start':
        local_start()
    elif args.command == 'import':
        db.bootstrap()
        print(json.dumps(db.stats(), indent=2))
    elif args.command == 'stats':
        print(json.dumps(db.stats(), indent=2))
    elif args.directory is None:
        parser.error('export requiere --directory nuevo')
    else:
        db.export(args.directory)
