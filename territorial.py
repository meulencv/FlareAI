from __future__ import annotations

import hashlib
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
from urllib.parse import urlencode, urljoin, urlsplit
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
    'www.bilbao.eus': r'/camarastrafico/[\w/-]+\.jpg',
    'mct.gencat.cat': r'/mct2bo/(RenderService|TransitCamera)',
    'emap.terrassa.cat': r'/it_terrassa/cam\d+\.jpeg',
    'www.bcn.cat': r'/transit/imatges/[\w-]+\.gif',
}
LOCKS = [threading.Lock() for _ in range(32)]
DOWNLOADS = threading.BoundedSemaphore(8)


def allowed_image(url: str) -> bool:
    try:
        u = urlsplit(url)
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
                raise RuntimeError('El proveedor no responde') from None
            target = urljoin(url, error.headers['Location'])
            error.close()
            url = target
            continue
        with response:
            if int(response.headers.get('Content-Length', '0')) > limit:
                raise RuntimeError('Respuesta demasiado grande')
            chunks, size = [], 0
            while True:
                chunk = response.read(min(65536, limit + 1 - size))
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'iframe':
            self.urls.extend(v.strip() for k, v in attrs if k in {'src', 'data-lazy-src'} and v and allowed_player(v.strip()))


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
                    return {**cached['data'], 'offline': self.offline}
            if self.offline:
                raise RuntimeError('Sin imagen local; requiere conexión')
            if not DOWNLOADS.acquire(blocking=False):
                raise RuntimeError('Descargas ocupadas; reintenta en unos segundos')
            try:
                body, headers = remote(url, allowed)
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
        camera = self.db.camera(identifier)
        if camera['kind'] == 'snapshot':
            return self.cached_image('camera:' + identifier, camera['imageUrl'], allowed_image,
                                     max(30, camera['refreshSeconds']), 'webcam', 'camera:' + camera['source'])
        if camera['kind'] == 'player' and allowed_page(camera['pageUrl']) and not self.offline:
            saved = self.db.get_asset('player:' + identifier)
            if saved and time.time() - saved['data']['fetched_epoch'] < 3600:
                return saved['data']
            if not DOWNLOADS.acquire(blocking=False):
                raise RuntimeError('Descargas ocupadas; reintenta en unos segundos')
            try:
                body, _ = remote(camera['pageUrl'], allowed_page, 2_000_000)
                parser = Players()
                parser.feed(body.decode('utf-8', errors='replace'))
                data = {'player_url': next(iter(parser.urls), None), 'fetched_epoch': time.time()}
                self.db.asset('player:' + identifier, 'player', data)
                return data
            finally:
                DOWNLOADS.release()
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
