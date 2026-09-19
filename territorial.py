from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
import io
import math
import re
import threading
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from PIL import Image

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'data/territorial'
ROAD_WMS = 'https://servicios.idee.es/wms-inspire/transportes'
IMAGE_RULES = {
    'etraffic.dgt.es': r'/camarasEtraffic/[\w-]+\.jpg',
    'informo.madrid.es': r'/cameras/Camara\d+\.jpg',
    'www.meteogalicia.gal': r'/datosred/camaras/[\w/.-]+\.(jpg|jpeg|png)',
    'www.trafikoa.eus': r'/static/files/tr/camaras/\d+\.jpg',
    'www.trafikoa.net': r'/static/files/tr/camaras/\d+\.jpg',
    'www.trafikoa.euskadi.eus': r'/static/files/tr/camaras/\d+\.jpg',
    'www.bilbao.eus': r'/camarastrafico/[\w/-]+\.jpg',
    'mct.gencat.cat': r'/mct2bo/(RenderService|TransitCamera)',
    'emap.terrassa.cat': r'/it_terrassa/cam\d+\.jpeg',
    'www.bcn.cat': r'/transit/imatges/[\w-]+\.gif',
    'www.hispacams.com': r'/get_imagen_ws\.php',
}
LOCKS = [threading.Lock() for _ in range(32)]
DOWNLOADS = threading.BoundedSemaphore(8)
UNAVAILABLE_IMAGES = {
    '76bd674597bdbe5c437c5a5fad51e7272110e2bbde4ef7a715711a22c0f9382f',
    'e8703ff5957fa4136be7c39ef1bc8c61d7d2c54a46537791a1fb08467145cdb3',
    'e5445ac8a52ad72e85b4e41de424da0d29374c0e9460323200d51ea47e5b8799',
    '03a52a43b8c3b2fcc4e1cae231ba3c2a1d5daa269b7c0900745c8043c8245a30',
    '3b6ace4fb0afcd5eeae11ec27659946fa2028b3fc87ec5fd1878a3057e71b1de',
    'e29891bf5b85afb8016ccd2117ece878b7742ac1752eb3dca7dbe68ef32d8932',
}


def allowed_image(url: str) -> bool:
    try:
        u = urlsplit(url)
        if u.hostname == 'www.hispacams.com':
            query = parse_qs(u.query)
            if not re.fullmatch(r'\d+', query.get('id', [''])[0]) or set(query) - {'id', 'size'}:
                return False
        return bool(not u.username and not u.password and u.port in (None, 443 if u.scheme == 'https' else 80)
                    and (u.scheme == 'https' or u.scheme == 'http' and u.hostname in {'mct.gencat.cat', 'www.bcn.cat'})
                    and re.fullmatch(IMAGE_RULES.get(u.hostname or '', r'(?!)'), u.path))
    except ValueError:
        return False


def allowed_page(url: str) -> bool:
    u = urlsplit(url)
    return u.scheme == 'https' and u.netloc == 'www.hispacams.com' and u.path.startswith('/webcams/')


def allowed_player(url: str) -> bool:
    u = urlsplit(url)
    return u.scheme == 'https' and bool(
        u.netloc == 'rtsp.me' and re.fullmatch(r'/embed/[a-zA-Z0-9]+/?', u.path)
        or u.netloc in {'www.youtube.com', 'www.youtube-nocookie.com'} and re.fullmatch(r'/embed/[\w-]{11}', u.path))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def remote(url: str, allowed: Callable[[str], bool], limit: int = 5_000_000) -> tuple[bytes, dict]:
    opener = build_opener(NoRedirect())
    deadline = time.monotonic() + 20
    for _ in range(4):
        if not allowed(url) or time.monotonic() >= deadline:
            raise RuntimeError('Destino remoto no permitido o tiempo agotado')
        try:
            response = opener.open(Request(url, headers={'User-Agent': 'FlareAIObservatorio/1.0'}), timeout=10)
        except HTTPError as error:
            if error.code not in (301, 302, 303, 307, 308) or not error.headers.get('Location'):
                error.close()
                raise RuntimeError(f'El proveedor no responde (HTTP {error.code})') from None
            target = urljoin(url, error.headers['Location'])
            error.close()
            url = target
            continue
        with response:
            if int(response.headers.get('Content-Length', '0')) > limit:
                raise RuntimeError('Respuesta demasiado grande')
            chunks, size = [], 0
            while True:
                chunk = response.read1(min(65536, limit + 1 - size))
                size += len(chunk)
                if size > limit or time.monotonic() >= deadline:
                    raise RuntimeError('Descarga excede límites')
                if not chunk:
                    break
                chunks.append(chunk)
            return b''.join(chunks), dict(response.headers.items())
    raise RuntimeError('Demasiadas redirecciones')


class Players(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.images: list[str] = []
        self.has_video = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        self.has_video |= tag == 'video'
        if tag == 'iframe':
            self.urls.extend(v.strip() for k, v in attrs if k in {'src', 'data-lazy-src'} and v and allowed_player(v.strip()))
        if tag == 'img' and fields.get('id') == 'player':
            self.images.extend(v.strip() for k, v in attrs if k in {'src', 'data-lazy-src'} and v and allowed_image(v.strip()))


class ExternalCamera(RuntimeError):
    pass


def embeddable(url: str, body: bytes, headers: dict) -> bool:
    if not allowed_player(url):
        return False
    fields = {key.lower(): value for key, value in headers.items()}
    if fields.get('x-frame-options', '').upper() in {'DENY', 'SAMEORIGIN'}:
        return False
    ancestors = re.search(r"frame-ancestors\s+([^;]+)", fields.get('content-security-policy', ''), re.I)
    if ancestors and '*' not in ancestors.group(1).split():
        return False
    text = body.decode('utf-8', errors='replace')
    parser = Players()
    parser.feed(text)
    if urlsplit(url).hostname == 'rtsp.me':
        return parser.has_video
    return bool(re.search(r'"playabilityStatus"\s*:\s*\{\s*"status"\s*:\s*"OK"', text))


def road_url(z: int, x: int, y: int) -> str:
    if not 4 <= z <= 16 or not 0 <= x < 2 ** z or not 0 <= y < 2 ** z:
        raise ValueError('Tesela inválida')
    unit = 40075016.68557849 / 2 ** z
    west, north = x * unit - 20037508.342789244, 20037508.342789244 - y * unit
    def lon(m: float) -> float:
        return m / 20037508.342789244 * 180

    def lat(m: float) -> float:
        return math.degrees(math.atan(math.sinh(m / 6378137)))
    if lon(west) > 5 or lon(west + unit) < -19 or lat(north) < 27 or lat(north - unit) > 44.5:
        raise ValueError('Tesela fuera de España')
    return ROAD_WMS + '?' + urlencode({'SERVICE': 'WMS', 'VERSION': '1.1.1', 'REQUEST': 'GetMap',
        'LAYERS': 'TN.RoadTransportNetwork.RoadLink', 'STYLES': '', 'SRS': 'EPSG:3857',
        'BBOX': f'{west},{north-unit},{west+unit},{north}', 'WIDTH': 256, 'HEIGHT': 256,
        'FORMAT': 'image/png', 'TRANSPARENT': 'TRUE'})


class Territorial:
    def __init__(self, database, offline: bool = False) -> None:
        self.db, self.offline = database, offline

    def cached_image(self, key: str, url: str, allowed: Callable[[str], bool], ttl: int,
                     kind: str, source: str | None = None) -> dict:
        token = hashlib.sha256(key.encode()).hexdigest()[:24]
        with LOCKS[int(token[:4], 16) % len(LOCKS)]:
            cached = self.db.get_asset(key)
            if cached and cached['path'] and (ROOT / cached['path']).exists():
                if self.offline or time.time() - cached['data']['fetched_epoch'] < ttl:
                    if cached['data'].get('sha256') in UNAVAILABLE_IMAGES:
                        raise RuntimeError('La fuente devuelve una plantilla de cámara no disponible')
                    return {**cached['data'], 'offline': self.offline}
            if self.offline:
                raise RuntimeError('Sin imagen local; requiere conexión')
            if not DOWNLOADS.acquire(blocking=False):
                raise RuntimeError('Descargas ocupadas; reintenta en unos segundos')
            try:
                body, headers = remote(url, allowed)
                if hashlib.sha256(body).hexdigest() in UNAVAILABLE_IMAGES:
                    raise RuntimeError('La fuente devuelve una plantilla de cámara no disponible')
                headers = {k.lower(): v for k, v in headers.items()}
                mime = headers.get('content-type', '').split(';')[0]
                if mime not in {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}:
                    raise RuntimeError('El proveedor no devolvió una imagen')
                with Image.open(io.BytesIO(body)) as image:
                    if image.width * image.height > 20_000_000 or kind == 'roads' and image.size != (256, 256):
                        raise RuntimeError('Dimensiones de imagen no válidas')
                    image.verify()
                CACHE.mkdir(parents=True, exist_ok=True)
                path = CACHE / f'{token}.img'
                temporary = path.with_suffix('.part')
                temporary.write_bytes(body)
                temporary.replace(path)
                data = {'url': f'/territorial/{token}.img', 'mime': mime, 'fetched_epoch': time.time(),
                        'fetched_at': datetime.now(timezone.utc).isoformat(), 'source_modified': headers.get('last-modified'),
                        'source_url': url, 'sha256': hashlib.sha256(body).hexdigest(), 'offline': False}
                self.db.asset(key, kind, data, path, source)
                self.db.asset('media:' + token, kind, data, path, source)
                return data
            finally:
                DOWNLOADS.release()

    def webcam(self, identifier: str) -> dict:
        try:
            result = self._webcam(identifier)
            kind = 'snapshot' if result.get('url') else 'player' if result.get('player_url') else None
            if kind is None:
                raise ExternalCamera('La fuente no publica una cámara integrable')
            verified = kind == 'snapshot' or result.get('browser_verified_until', 0) > time.time()
            if not self.offline:
                self.db.camera_check(identifier, 'available' if verified else 'unavailable', kind, {
                    'method': 'image_decoded' if kind == 'snapshot' else 'browser_video_playing' if verified else 'public_embed_accessible',
                    'sha256': result.get('sha256'), 'source_url': result.get('source_url') or result.get('player_url'),
                    'source_modified': result.get('source_modified'), 'emission_verified': kind == 'player' and verified,
                    'browser_verified_until': result.get('browser_verified_until'), 'browser_checked_at': result.get('browser_checked_at'),
                })
            return {**result, 'kind': kind, 'verification_pending': not verified}
        except (OSError, RuntimeError, ValueError) as error:
            if not self.offline:
                self.db.camera_check(identifier, 'external' if isinstance(error, ExternalCamera) else 'unavailable', None,
                                     {'reason': str(error)[:300]})
            raise

    def _webcam(self, identifier: str) -> dict:
        camera = self.db.camera(identifier)
        if camera['kind'] == 'snapshot':
            return self.cached_image('camera:' + identifier, camera['imageUrl'], allowed_image,
                                     max(30, camera['refreshSeconds']), 'webcam', 'camera:' + camera['source'])
        if camera['kind'] == 'player' and allowed_page(camera['pageUrl']) and not self.offline:
            saved = self.db.get_asset('player:' + identifier)
            if saved and saved['data'].get('version') == 2 and time.time() - saved['data']['fetched_epoch'] < 3600:
                data = saved['data']
            else:
                if not DOWNLOADS.acquire(blocking=False):
                    raise RuntimeError('Descargas ocupadas; reintenta en unos segundos')
                try:
                    body, _ = remote(camera['pageUrl'], allowed_page, 2_000_000)
                    parser = Players()
                    parser.feed(body.decode('utf-8', errors='replace'))
                    data = {'player_url': None, 'image_url': next(iter(parser.images), None),
                            'fetched_epoch': time.time(), 'version': 2}
                    if not data['image_url']:
                        for player_url in dict.fromkeys(parser.urls):
                            try:
                                player_body, headers = remote(player_url, allowed_player, 2_000_000)
                            except (OSError, RuntimeError):
                                continue
                            if embeddable(player_url, player_body, headers):
                                data['player_url'] = player_url
                                break
                    if saved and saved['data'].get('player_url') == data['player_url']:
                        data['browser_verified_until'] = saved['data'].get('browser_verified_until', 0)
                    self.db.asset('player:' + identifier, 'player', data)
                finally:
                    DOWNLOADS.release()
            if data.get('image_url'):
                return self.cached_image('camera:' + identifier, data['image_url'], allowed_image, 180, 'webcam', 'camera:' + camera['source'])
            return data
        return {'player_url': None}

    def road(self, z: int, x: int, y: int) -> tuple[bytes, str]:
        url = road_url(z, x, y)
        data = self.cached_image(f'roads:{z}:{x}:{y}', url,
                                 lambda u: u.startswith(ROAD_WMS + '?'), 30 * 86400, 'roads', 'ign-roads')
        return self.media(data['url'].split('/')[-1].split('.')[0])

    def media(self, token: str) -> tuple[bytes, str]:
        asset = self.db.get_asset('media:' + token)
        if asset is None or not asset['path']:
            raise KeyError('Imagen no encontrada')
        path = (ROOT / asset['path']).resolve()
        if not path.is_relative_to(CACHE.resolve()):
            raise ValueError('Ruta no permitida')
        return path.read_bytes(), asset['data']['mime']

    def verify_cameras(self, source: str | None = None, limit: int | None = None, force: bool = False) -> dict:
        with self.db.verification_lock(804024) as acquired:
            return self._verify_cameras(source, limit, force) if acquired else {}

    def _verify_cameras(self, source: str | None = None, limit: int | None = None, force: bool = False) -> dict:
        if self.offline:
            return {}
        checks = self.db.camera_checks()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        groups: dict[str, list] = defaultdict(list)
        for camera in self.db.catalog()['cameras']:
            if source and camera['source'] != source:
                continue
            saved = checks.get(camera['id'])
            if force or not saved or saved['valid_until'] <= now:
                groups[camera['source']].append(camera)
        cameras = [c for row in zip_longest(*groups.values()) for c in row if c is not None]
        cameras.sort(key=lambda camera: checks.get(camera['id'], {}).get('checked_at', datetime.min))
        if limit is not None:
            cameras = cameras[:limit]
        slots = {name: threading.BoundedSemaphore(2) for name in groups}

        def verify(camera: dict) -> str:
            with slots[camera['source']]:
                try:
                    result = self.webcam(camera['id'])
                    return 'player_pending' if result.get('verification_pending') else result['kind']
                except ExternalCamera:
                    return 'external'
                except (OSError, RuntimeError, ValueError):
                    return 'unavailable'
                finally:
                    time.sleep(.2)

        counts: Counter = Counter()
        with ThreadPoolExecutor(max_workers=4) as pool:
            for index, result in enumerate(pool.map(verify, cameras), 1):
                counts[result] += 1
                if index % 100 == 0 or index == len(cameras):
                    print(json.dumps({'checked': index, 'total': len(cameras), 'results': dict(counts)}), flush=True)
        return dict(counts)

    def verification_loop(self) -> None:
        while not self.offline:
            try:
                self.verify_cameras(limit=200)
                import asyncio
                from verify_camera_players import verify_players
                asyncio.run(verify_players(self.db, limit=20))
            except Exception:
                print('Verificación de cámaras pendiente; se reintentará.', flush=True)
            threading.Event().wait(600)


if __name__ == '__main__':
    from database import Database
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['verify-cameras'])
    parser.add_argument('--source')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--force', action='store_true')
    options = parser.parse_args()
    database = Database()
    database.migrate()
    Territorial(database).verify_cameras(options.source, options.limit, options.force)
