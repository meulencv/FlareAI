from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import sqlite3
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from contextlib import closing
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable

from shapely import STRtree
from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = 1
EARTH_KM = 6371.0088
OVERPASS = ("https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
SANIDAD = "https://www.sanidad.gob.es/ciudadanos/centros.do?metodo="
DERA = "https://www.ideandalucia.es/services/DERA_g12_servicios/wfs"
MADRID = ("https://datos.madrid.es/dataset/211642-0-bomberos-parques/resource/"
          "211642-3-bomberos-parques-csv/download/211642-3-bomberos-parques-csv.csv")
CATEGORIES = {
    "hospital": "Hospital", "health_centre": "Centro sanitario (urgencias no confirmadas)",
    "emergency_department": "Urgencias sanitarias", "fire_station": "Parque de bomberos",
    "forest_fire_base": "Base de extinción forestal", "police": "Policía / Guardia Civil",
    "civil_protection": "Protección Civil", "coordination_centre": "Centro de coordinación",
    "ambulance_station": "Base de ambulancias", "rescue_station": "Base / puesto de salvamento",
    "helipad": "Helipuerto (uso de emergencia no necesariamente confirmado)",
    "humanitarian": "Organización humanitaria",
}
OSM_FILTERS = {
    "health": ['[amenity~"^(hospital|clinic|doctors)$"]', '[healthcare~"^(hospital|clinic|centre)$"]',
               '[emergency=emergency_ward_entrance]'],
    "fire": ['[amenity=fire_station]', '[emergency=fire_station]',
             '[name~"INFOCA|BRIF|[Bb]ase [Ff]orestal|[Bb]ase de [Bb]rigada"]'],
    "police": ['[amenity=police]', '[police~"^(station|offices)$"]'],
    "response": ['[emergency~"^(ambulance_station|rescue_station|water_rescue_station|control_centre|disaster_response|mountain_rescue)$"]',
                 '[office~"^(civil_protection|disaster_response)$"]',
                 '[name~"[Pp]rotecci[oó]n [Cc]ivil|[Pp]rotecci[oó] [Cc]ivil|[Cc]entro.*[Ee]mergencias|[Cc]entre.*[Ee]mergències"]'],
    "heli": ['[aeroway~"^(helipad|heliport)$"]'],
}
DERA_LAYERS = {
    "health": ("g12_01_CentroSalud", "health_centre"),
    "hospitals": ("g12_02_Hospital_CAE", "hospital"),
    "police": ("g12_26_Policia", "police"),
    "fire": ("g12_29_ParqueBomberos", "fire_station"),
    "guardia": ("g12_34_GuardiaCivil", "police"),
    "coordination": ("g12_35_GestionEmergencias", "coordination_centre"),
    "humanitarian": ("g12_36_OrganizacionesHumanitarias", "humanitarian"),
    "rescue": ("g12_37_PuestosSocorro", "rescue_station"),
}
REGIONS = {
    "Andalucía": "Almería|Cádiz|Córdoba|Granada|Huelva|Jaén|Málaga|Sevilla",
    "Aragón": "Huesca|Teruel|Zaragoza", "Principado de Asturias": "Asturias",
    "Illes Balears": "Balears, Illes|Illes Balears", "Canarias": "Palmas, Las|Las Palmas|Santa Cruz de Tenerife",
    "Cantabria": "Cantabria", "Castilla y León": "Ávila|Burgos|León|Palencia|Salamanca|Segovia|Soria|Valladolid|Zamora",
    "Castilla-La Mancha": "Albacete|Ciudad Real|Cuenca|Guadalajara|Toledo",
    "Cataluña": "Barcelona|Girona|Lleida|Tarragona", "Comunitat Valenciana": "Alicante|Castellón|Valencia",
    "Extremadura": "Badajoz|Cáceres", "Galicia": "Coruña, A|A Coruña|Lugo|Ourense|Pontevedra",
    "Comunidad de Madrid": "Madrid", "Región de Murcia": "Murcia", "Comunidad Foral de Navarra": "Navarra",
    "País Vasco": "Alava|Álava|Araba/Álava|Gipuzkoa|Guipúzcoa|Bizkaia|Vizcaya",
    "La Rioja": "Rioja, La|La Rioja", "Ceuta": "Ceuta", "Melilla": "Melilla",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":"))


def clean(value: object) -> str | None:
    text = re.sub(r"\s+", " ", str(value)).strip() if value is not None else ""
    return None if text.lower() in {"", "none", "null", "no disponible", "sin datos", "s/d"} else text


def normalized(value: object) -> str:
    text = unicodedata.normalize("NFKD", clean(value) or "").casefold()
    return " ".join(re.findall(r"[a-z0-9]+", "".join(c for c in text if not unicodedata.combining(c))))


PROVINCE_REGION = {normalized(p): region for region, names in REGIONS.items() for p in names.split("|")}
PROVINCE_ALIASES = {
    "alava": "Álava", "araba alava": "Álava", "guipuzcoa": "Gipuzkoa", "vizcaya": "Bizkaia",
    "coruna a": "A Coruña", "coruna": "A Coruña", "la coruna": "A Coruña",
    "balears illes": "Illes Balears", "palmas las": "Las Palmas", "rioja la": "La Rioja",
    "alicante alacant": "Alicante", "castellon castello": "Castellón", "valencia valencia": "Valencia",
}
PROVINCE_NAMES = {normalized(p): p for names in REGIONS.values() for p in names.split("|")}


def province_name(value: object) -> str | None:
    key = normalized(value)
    return PROVINCE_ALIASES.get(key, PROVINCE_NAMES.get(key, clean(value)))


def decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def normalize_phones(value: object) -> list[str]:
    text = clean(value) or ""
    matches = re.findall(r"(?<!\d)(?:(?:\+34|0034)[ .-]*)?[6789](?:[ .-]*\d){8}(?!\d)|(?<!\d)(?:112|061|062|080|085|091|092)(?!\d)", text)
    result = []
    for match in matches:
        digits = re.sub(r"\D", "", match)
        if len(digits) > 9:
            digits = digits[-9:]
        number = f"+34{digits}" if len(digits) == 9 else digits
        if number not in result:
            result.append(number)
    return result


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((phi2 - phi1) / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def make_record(source: str, identifier: str, *, name=None, categories=None, lat=None, lon=None, **fields) -> dict:
    if (lat is None) != (lon is None):
        raise ValueError("Par de coordenadas incompleto")
    if lat is not None:
        lat, lon = float(lat), float(lon)
        if not (math.isfinite(lat) and math.isfinite(lon) and 27 <= lat <= 44.5 and -19 <= lon <= 5):
            raise ValueError(f"Coordenadas fuera del ámbito español: {lat}, {lon}")
    category_list = sorted(set(categories or []))
    if not category_list or set(category_list) - CATEGORIES.keys():
        raise ValueError(f"Categorías inválidas: {category_list}")
    record = {"source": source, "source_record_id": str(identifier), "name": clean(name),
              "categories": category_list, "lat": lat, "lon": lon,
              "address": None, "municipality": None, "province": None, "autonomous_community": None,
              "postcode": None, "phones": [], "email": None, "website": None, "operator": None,
              "coordinate_method": "published_point" if lat is not None else "unlocated",
              "metadata": {}, "raw": {}, "source_url": None, "download_id": None}
    record.update(fields)
    record["province"] = province_name(record["province"])
    if record["province"]:
        record["autonomous_community"] = PROVINCE_REGION.get(normalized(record["province"]), record["autonomous_community"])
    return record


def classify_osm(tags: dict) -> list[str]:
    if any(tags.get(key) == "yes" for key in ("disused", "abandoned", "demolished", "construction")):
        return []
    name = "" if tags.get("highway") or tags.get("place") else normalized(tags.get("name"))
    categories = set()
    amenity, emergency, healthcare = tags.get("amenity"), tags.get("emergency"), tags.get("healthcare")
    if amenity == "hospital" or healthcare == "hospital":
        categories.add("hospital")
    elif amenity in {"clinic", "doctors"} or healthcare in {"clinic", "centre"}:
        categories.add("health_centre")
    if emergency == "emergency_ward_entrance" or (emergency == "yes" and categories & {"hospital", "health_centre"}):
        categories.add("emergency_department")
    if amenity == "fire_station" or emergency == "fire_station":
        categories.add("fire_station")
    if re.search(r"\b(infoca|brif)\b|base forestal|base de brigada", name):
        categories.add("forest_fire_base")
    if amenity == "police" or tags.get("police") in {"station", "offices"}:
        categories.add("police")
    mapping = {"ambulance_station": "ambulance_station", "rescue_station": "rescue_station",
               "water_rescue_station": "rescue_station", "mountain_rescue": "rescue_station",
               "control_centre": "coordination_centre", "disaster_response": "civil_protection"}
    if emergency in mapping:
        categories.add(mapping[emergency])
    if tags.get("office") in {"civil_protection", "disaster_response"} or re.search(r"proteccio[n]? civil", name):
        categories.add("civil_protection")
    if re.search(r"centr[oe].*emergenc", name):
        categories.add("coordination_centre")
    if tags.get("aeroway") in {"helipad", "heliport"}:
        categories.add("helipad")
    return sorted(categories)


def validate_overpass(data: bytes) -> None:
    payload = json.loads(data)
    elements = payload.get("elements")
    if payload.get("remark") or not isinstance(elements, list):
        raise ValueError(f"Respuesta Overpass incompleta: {payload.get('remark', 'sin elementos')}")
    counts = [e for e in elements if e.get("type") == "count"]
    if len(counts) != 1 or int(counts[0]["tags"]["total"]) != len(elements) - 1:
        raise ValueError("Overpass no entregó el marcador de recuento completo")


def police_force(name: object, operator: object = None) -> str | None:
    text = normalized(f"{name or ''} {operator or ''}")
    for phrase, force in (("guardia civil", "guardia_civil"), ("policia nacional", "policia_nacional"),
                          ("mossos", "mossos_esquadra"), ("ertzaintza", "ertzaintza"),
                          ("policia foral", "policia_foral"), ("policia canaria", "policia_canaria"),
                          ("policia local", "policia_local"), ("policia municipal", "policia_local"),
                          ("guardia urbana", "policia_local"), ("udaltzaingoa", "policia_local")):
        if phrase in text:
            return force
    return None


def parse_overpass(payload: dict) -> list[dict]:
    records = []
    for element in payload["elements"]:
        if element["type"] == "count":
            continue
        tags = element.get("tags", {})
        categories = classify_osm(tags)
        if not categories:
            continue
        coords = element if element["type"] == "node" else element.get("center", {})
        identifier = f"{element['type']}/{element['id']}"
        hours = tags.get("opening_hours")
        metadata = {"open_24h": True if hours == "24/7" else None, "opening_hours": hours,
                    "emergency": tags.get("emergency"), "access": tags.get("access"),
                    "wheelchair": tags.get("wheelchair"), "healthcare": tags.get("healthcare"),
                    "emergency_heli_use": tags.get("emergency") if "helipad" in categories else None,
                    "classification_method": "osm_tags_and_name_rules", "osm_version": element.get("version"),
                    "osm_timestamp": element.get("timestamp"), "operator_type": tags.get("operator:type"),
                    "police_force_inferred": police_force(tags.get("name"), tags.get("operator")) if "police" in categories else None}
        records.append(make_record("osm", identifier, name=tags.get("name") or tags.get("official_name"),
            categories=categories, lat=coords.get("lat"), lon=coords.get("lon"),
            address=clean(tags.get("addr:full") or " ".join(filter(None, (tags.get("addr:street"), tags.get("addr:housenumber"))))),
            municipality=clean(tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village")),
            province=tags.get("addr:province"), postcode=clean(tags.get("addr:postcode") or tags.get("postal_code")),
            phones=normalize_phones(tags.get("contact:phone") or tags.get("phone")),
            email=clean(tags.get("contact:email") or tags.get("email")),
            website=clean(tags.get("contact:website") or tags.get("website")), operator=clean(tags.get("operator")),
            coordinate_method="osm_node" if element["type"] == "node" else "osm_bbox_center",
            metadata=metadata, raw=element, source_url=f"https://www.openstreetmap.org/{identifier}"))
    return records


def parse_sanidad(data: bytes, source: str, category: str) -> list[dict]:
    root = ET.fromstring(decode_text(data))
    records = []
    for element in root.findall("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"):
        values = {child.tag.rsplit("}", 1)[-1]: clean(child.text) for child in element}
        url = element.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"]
        if not values.get("NAME"):
            continue
        identifier = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["id"][0]
        name, address = values.get("NAME"), values.get("Street")
        name_method = "published_name"
        if category == "emergency_department" and address:
            location, separator, street = address.partition(" - ")
            if separator and normalized(location).startswith(("centro salud ", "centro de salud ", "consultorio ", "hospital ")):
                name, address, name_method = location, street, "location_name_extracted_from_published_address"
        records.append(make_record(source, identifier, name=name, categories=[category],
            address=address, municipality=values.get("Locality"), province=values.get("Region"),
            autonomous_community=values.get("addressRegion"), postcode=values.get("Pcode"),
            phones=normalize_phones(values.get("TEL")), source_url=url, raw=values,
            metadata={"official_code": values.get("code") or identifier, "source_attributes": values,
                      "open_24h": None, "geocoding_status": "not_published", "name_method": name_method,
                      "source_service_name": values.get("NAME")}))
    if not records:
        raise ValueError("Catálogo Sanidad vacío o esquema cambiado")
    return records


def parse_madrid(data: bytes) -> list[dict]:
    rows = csv.DictReader(io.StringIO(decode_text(data)), delimiter=";")
    if not {"PK", "NOMBRE", "LATITUD", "LONGITUD"}.issubset(rows.fieldnames or []):
        raise ValueError("Esquema CSV Madrid no reconocido")
    return [make_record("madrid_fire", row["PK"], name=row["NOMBRE"], categories=["fire_station"],
                lat=row["LATITUD"], lon=row["LONGITUD"],
                address=clean(" ".join(row.get(k, "") for k in ("CLASE-VIAL", "NOMBRE-VIA", "NUM"))),
                municipality=clean(row.get("LOCALIDAD")), province="Madrid", postcode=clean(row.get("CODIGO-POSTAL")),
                phones=normalize_phones(row.get("TELEFONO")), email=clean(row.get("EMAIL")),
                source_url=clean(row.get("CONTENT-URL")), raw=row,
                metadata={"opening_hours": clean(row.get("HORARIO")), "open_24h": None}) for row in rows]


def parse_wfs(payload: dict, source: str, category: str) -> list[dict]:
    features = payload.get("features", [])
    if payload.get("type") != "FeatureCollection" or int(payload.get("numberMatched", payload.get("totalFeatures", -1))) != len(features):
        raise ValueError("Respuesta WFS truncada o sin recuento comprobable")
    records = []
    for feature in features:
        props, geom = feature["properties"], feature.get("geometry")
        lat = lon = None
        if geom:
            coords = geom["coordinates"]
            if geom["type"] == "MultiPoint" and len(coords) == 1:
                coords = coords[0]
            elif geom["type"] != "Point":
                raise ValueError("Geometría WFS no puntual")
            lon, lat = coords[:2]
        categories = [category]
        kind = normalized(props.get("tipo"))
        if source == "dera_hospitals" and ("especialidad" in kind or "consultas" in kind) and "hospital" not in kind:
            categories = ["health_centre"]
        if "proteccion civil" in normalized(props.get("nombre")):
            categories.append("civil_protection")
        records.append(make_record(source, str(props.get("id_dera", feature["id"])), name=props.get("nombre"),
            categories=categories, lat=lat, lon=lon, address=clean(props.get("direccion")),
            municipality=clean(props.get("municipio")), province=props.get("provincia"),
            phones=normalize_phones(" / ".join(str(props.get(k) or "") for k in ("telefono", "telefono2"))),
            email=clean(props.get("correo")), website=clean(props.get("web")), raw=props,
            source_url=DERA, metadata={"municipality_ine": props.get("cod_mun"), "source_type": props.get("tipo"), "open_24h": None,
                "police_force_inferred": "guardia_civil" if source == "dera_guardia" else police_force(props.get("nombre")) if category == "police" else None}))
    return records


class Cache:
    def __init__(self, root: Path, *, offline=False, refresh=False, retries=3) -> None:
        if offline and refresh:
            raise ValueError("--offline y --refresh son incompatibles")
        self.root, self.offline, self.refresh, self.retries = root, offline, refresh, retries
        root.mkdir(parents=True, exist_ok=True)

    def has(self, url: str) -> bool:
        return (self.root / (hashlib.sha256(url.encode()).hexdigest() + ".json")).exists()

    def fetch(self, source: str, url: str, validate: Callable[[bytes], object]) -> tuple[bytes, dict]:
        key = hashlib.sha256(url.encode()).hexdigest()
        meta_path = self.root / f"{key}.json"
        if meta_path.exists() and not self.refresh:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            data = gzip.decompress((self.root / meta["file"]).read_bytes())
            if hashlib.sha256(data).hexdigest() != meta["sha256"]:
                raise ValueError(f"Caché corrupta: {meta_path}")
            validate(data)
            return data, {**meta, "cache_hit": True}
        if self.offline:
            raise FileNotFoundError(f"Sin caché offline para {source}: {url}")
        print(f"Descargando {source} desde {urllib.parse.urlparse(url).netloc}", flush=True)
        for attempt in range(self.retries):
            delay = min(60, 3 * 2 ** attempt)
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "FlareAI-EmergencyAtlas/1.0 (public-data research)",
                                                              "Accept": "*/*", "Accept-Encoding": "identity"})
                with urllib.request.urlopen(request, timeout=240) as response:
                    data = response.read()
                    headers = {key: response.headers.get(key) for key in ("Content-Type", "ETag", "Last-Modified", "Date")}
                    final_url = response.url
                validate(data)
                digest = hashlib.sha256(data).hexdigest()
                filename = f"{digest}.raw.gz"
                atomic_write(self.root / filename, gzip.compress(data, mtime=0))
                meta = {"id": key, "source_id": source, "url": url, "final_url": final_url,
                        "retrieved_at": now(), "sha256": digest, "bytes": len(data), "file": filename,
                        "headers": headers, "cache_hit": False}
                atomic_write(meta_path, dumps(meta).encode())
                return data, meta
            except (OSError, ValueError, ET.ParseError) as exc:
                if isinstance(exc, urllib.error.HTTPError):
                    retry_after = exc.headers.get("Retry-After", "")
                    if retry_after.isdigit():
                        delay = min(300, max(delay, int(retry_after)))
                    if exc.code in {400, 401, 403, 404, 406}:
                        raise
                if attempt + 1 == self.retries:
                    raise
                print(f"Reintento {source}: {type(exc).__name__}: {exc}; espera {delay}s", file=sys.stderr, flush=True)
                time.sleep(delay)
        raise RuntimeError("Número de reintentos inválido")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def source_catalog() -> list[dict]:
    sources = [
        {"id": "osm", "name": "OpenStreetMap contributors", "url": "https://www.openstreetmap.org/copyright",
         "license": "ODbL-1.0", "scope": "España: Península, Baleares, Canarias, Ceuta y Melilla", "official": False},
        {"id": "madrid_fire", "name": "Ayuntamiento de Madrid - parques de bomberos", "url": MADRID,
         "license": "CC-BY-4.0", "scope": "Municipio de Madrid", "official": True},
    ]
    for suffix, method in (("hospitals", "hospitalesRDF"), ("urgent", "dispositivosRDF")):
        sources.append({"id": f"sanidad_{suffix}", "name": f"Ministerio de Sanidad - {method}",
                        "url": SANIDAD + method, "license": "Condiciones de reutilización Ministerio de Sanidad; ver aviso legal",
                        "scope": "España", "official": True})
    for suffix, (layer, _) in DERA_LAYERS.items():
        sources.append({"id": f"dera_{suffix}", "name": f"IECA / Junta de Andalucía - {layer}",
                        "url": DERA, "license": "CC-BY-4.0", "scope": "Andalucía", "official": True})
    return sources


def osm_query(filters: list[str], bbox: str = "", timeout: int = 180) -> str:
    area = '(area.es)' + (f'({bbox})' if bbox else '')
    return (f'[out:json][timeout:{timeout}];area["ISO3166-1"="ES"][admin_level=2]->.es;('
            + ''.join(f'nwr{selector}{area};' for selector in filters) + ');out center meta;out count;')


def plan_osm_queries(cache: Cache, endpoints=OVERPASS) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []
    name_filters: list[str] = []
    for group, filters in OSM_FILTERS.items():
        full = osm_query(filters)
        if not cache.refresh and any(cache.has(endpoint + '?' + urllib.parse.urlencode({'data': full})) for endpoint in endpoints):
            queries.append((group, full))
        else:
            queries.append((group, osm_query([s for s in filters if not s.startswith('[name')])))
            name_filters.extend(s for s in filters if s.startswith('[name'))
    if name_filters:
        boxes = [(south, west, south + 3, west + 4) for south in (35, 38, 41) for west in (-10, -6, -2, 2)]
        boxes.extend([(27, -19, 30, -15), (27, -15, 30, -12)])
        for index, bounds in enumerate(boxes):
            queries.append((f'named_{index:02d}', osm_query(name_filters, ','.join(str(v) for v in bounds), 90)))
    return queries


def acquire(cache: Cache, endpoints=OVERPASS) -> tuple[list[dict], list[dict], list[dict]]:
    records, downloads, statuses = [], [], []

    def save_batch(task, source, rows, meta, extra=None):
        meta.update(extra or {})
        downloads.append(meta)
        for row in rows:
            row["download_id"] = meta["id"]
        records.extend(rows)
        statuses.append({"task": task, "source": source, "status": "ok", "records": len(rows),
                         "download_id": meta["id"], "retrieved_at": meta["retrieved_at"], **(extra or {})})
        print(f"{task}: {len(rows)} registros", flush=True)

    for suffix, method, category in (("hospitals", "hospitalesRDF", "hospital"), ("urgent", "dispositivosRDF", "emergency_department")):
        source = f"sanidad_{suffix}"
        try:
            data, meta = cache.fetch(source, SANIDAD + method, lambda b: parse_sanidad(b, source, category))
            save_batch(source, source, parse_sanidad(data, source, category), meta)
        except (OSError, ValueError, ET.ParseError, KeyError) as exc:
            statuses.append({"task": source, "source": source, "status": "failed", "error": str(exc)})
    try:
        data, meta = cache.fetch("madrid_fire", MADRID, parse_madrid)
        save_batch("madrid_fire", "madrid_fire", parse_madrid(data), meta)
    except (OSError, ValueError, KeyError) as exc:
        statuses.append({"task": "madrid_fire", "source": "madrid_fire", "status": "failed", "error": str(exc)})
    for suffix, (layer, category) in DERA_LAYERS.items():
        source = f"dera_{suffix}"
        parameters = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                      "typeNames": f"DERA_g12_servicios:{layer}", "outputFormat": "application/json",
                      "srsName": "EPSG:4326", "count": 10000, "sortBy": "id_dera"}
        url = DERA + "?" + urllib.parse.urlencode(parameters)
        try:
            data, meta = cache.fetch(source, url, lambda b: parse_wfs(json.loads(b), source, category))
            payload = json.loads(data)
            save_batch(source, source, parse_wfs(payload, source, category), meta, {"response_timestamp": payload.get("timeStamp")})
        except (OSError, ValueError, KeyError) as exc:
            statuses.append({"task": source, "source": source, "status": "failed", "error": str(exc)})
    for group, query in plan_osm_queries(cache, endpoints):
        errors = []
        preferred = sorted(endpoints, key=lambda endpoint: not cache.has(endpoint + "?" + urllib.parse.urlencode({"data": query}))) if not cache.refresh else endpoints
        for endpoint in preferred:
            try:
                url = endpoint + "?" + urllib.parse.urlencode({"data": query})
                data, meta = cache.fetch("osm", url, validate_overpass)
                payload = json.loads(data)
                save_batch(f"osm_{group}", "osm", parse_overpass(payload), meta,
                           {"osm_base_timestamp": payload.get("osm3s", {}).get("timestamp_osm_base"), "query": query})
                if not cache.offline and not meta["cache_hit"]:
                    time.sleep(2)
                break
            except (OSError, ValueError, KeyError) as exc:
                errors.append(f"{endpoint}: {exc}")
        else:
            statuses.append({"task": f"osm_{group}", "source": "osm", "status": "failed", "errors": errors})
    unique: dict[tuple[str, str], dict] = {}
    for row in records:
        key = (row["source"], row["source_record_id"])
        previous = unique.get(key)
        if previous is None or (row["metadata"].get("osm_timestamp") or "") > (previous["metadata"].get("osm_timestamp") or ""):
            unique[key] = row
    return list(unique.values()), downloads, statuses


class Geography:
    def __init__(self, path: Path) -> None:
        data = path.read_bytes()
        self.sha256 = hashlib.sha256(data).hexdigest()
        features = json.loads(data)["features"]
        self.names = [province_name(f["properties"]["shapeName"]) or str(f["properties"]["shapeName"]) for f in features]
        self.shapes = [shape(f["geometry"]) for f in features]
        self.tree = STRtree(self.shapes)
        if len(self.names) != 52 or len(set(self.names)) != 52:
            raise ValueError("Se esperaban 52 provincias/ciudades autónomas diferentes")
        if any(normalized(name) not in PROVINCE_REGION for name in self.names):
            raise ValueError("Provincia sin correspondencia de comunidad autónoma")

    def enrich(self, record: dict) -> None:
        if record["lat"] is None:
            return
        point = Point(record["lon"], record["lat"])
        hits = self.tree.query(point, predicate="intersects")
        method = "point_in_province"
        if len(hits):
            index = int(hits[0])
        else:
            index = int(self.tree.nearest(point))
            if self.shapes[index].distance(point) > .005:
                record["metadata"]["province_spatial_status"] = "outside_boundary_unresolved"
                return
            method = "nearest_province_within_0.005_degrees"
        province = self.names[index]
        if record["province"] and normalized(record["province"]) != normalized(province):
            record["metadata"]["province_conflict"] = {"published": record["province"], "spatial": province}
        if not record["province"]:
            record["province"] = province
            record["metadata"]["province_method"] = method
        else:
            record["metadata"]["province_method"] = "published"
        record["autonomous_community"] = PROVINCE_REGION.get(normalized(record["province"]))
        record["metadata"]["boundary_sha256"] = self.sha256


def distinctive(name: object) -> bool:
    generic = {"hospital", "centro", "de", "del", "la", "el", "salud", "policia", "local", "guardia", "civil",
               "nacional", "parque", "bomberos", "proteccion", "urgencias", "consultorio", "clinica", "base"}
    words = normalized(name).split()
    return len(words) >= 2 and bool(set(words) - generic)


def compatible(a: dict, b: dict) -> bool:
    first, second = set(a["categories"]), set(b["categories"])
    return bool(first & second or (first & {"health_centre", "emergency_department"} and second & {"health_centre", "emergency_department"}))


def name_score(a: object, b: object) -> float:
    first, second = normalized(a), normalized(b)
    if not first or not second:
        return 0.0
    if set(re.findall(r"\d+", first)) != set(re.findall(r"\d+", second)):
        return 0.0
    return SequenceMatcher(None, first, second).ratio()


def deduplicate(records: list[dict]) -> tuple[list[dict], list[dict]]:
    facilities: list[dict] = []
    links: list[dict] = []
    grid: dict[tuple[int, int], list[int]] = defaultdict(list)
    names: dict[tuple[str, str], set[int]] = defaultdict(set)
    phones: dict[str, set[int]] = defaultdict(set)
    addresses: dict[tuple[str, str, str], set[int]] = defaultdict(set)
    members: dict[int, list[tuple[float, float]]] = defaultdict(list)
    seen = set()
    scalar_fields = ("name", "address", "municipality", "province", "autonomous_community", "postcode", "email", "website", "operator")
    ordered = sorted(records, key=lambda r: (r["lat"] is None, r["source"] == "osm", r["source"], r["source_record_id"]))
    for row in ordered:
        identity = (row["source"], row["source_record_id"])
        if identity in seen:
            continue
        seen.add(identity)
        name_key = (normalized(row["name"]), normalized(row["province"]))
        address_key = (normalized(row["address"]), normalized(row["municipality"]), normalized(row["province"]))
        matches: list[tuple[int, str, float, float | None]] = []
        score: float | None = None
        distance: float | None = None
        if row["lat"] is not None:
            cell = (math.floor(row["lon"] / .005), math.floor(row["lat"] / .005))
            candidates = {i for dx in (-1, 0, 1) for dy in (-1, 0, 1) for i in grid.get((cell[0] + dx, cell[1] + dy), [])}
            for i in sorted(candidates):
                target = facilities[i]
                if not compatible(row, target):
                    continue
                distance = distance_km(row["lat"], row["lon"], target["lat"], target["lon"])
                score = name_score(row["name"], target["name"])
                if distinctive(row["name"]) and distinctive(target["name"]) and distance <= .15 and (score == 1 or score >= .93 and distance <= .1):
                    if all(distance_km(row["lat"], row["lon"], lat, lon) <= .15 for lat, lon in members[i]):
                        matches.append((i, "name_and_distance", score, round(distance, 6)))
        else:
            candidates = set()
            if all(name_key) and distinctive(row["name"]):
                candidates |= names.get(name_key, set())
            for phone in row["phones"]:
                if phone.startswith("+34"):
                    candidates |= phones.get(phone, set())
            if all(address_key):
                candidates |= addresses.get(address_key, set())
            for i in sorted(candidates):
                target = facilities[i]
                if not compatible(row, target) or normalized(row["province"]) != normalized(target["province"]):
                    continue
                if row["source"] in target["source_ids"]:
                    continue
                if all(name_key) and distinctive(row["name"]) and name_key[0] == normalized(target["name"]):
                    matches.append((i, "unique_name_province", 1.0, None))
                elif all(address_key) and i in addresses.get(address_key, set()):
                    matches.append((i, "unique_address_municipality", 1.0, None))
                elif name_score(row["name"], target["name"]) >= .7 and any(p.startswith("+34") and p in target["phones"] for p in row["phones"]):
                    matches.append((i, "unique_phone_name_province", name_score(row["name"], target["name"]), None))
        if len(matches) == 1:
            i, method, score, distance = matches[0]
            target = facilities[i]
            priority = row["source"] != "osm"
            for field in scalar_fields:
                if row[field] and (not target[field] or priority and target["field_sources"].get(field, "").startswith("osm:")):
                    if target[field] and target[field] != row[field]:
                        target["metadata"].setdefault("conflicting_fields", []).append(field)
                    target[field] = row[field]
                    target["field_sources"][field] = ":".join(identity)
            target["categories"] = sorted(set(target["categories"]) | set(row["categories"]))
            target["phones"] = sorted(set(target["phones"]) | set(row["phones"]))
            target["source_ids"] = sorted(set(target["source_ids"]) | {row["source"]})
            target["metadata"]["deduplicated"] = True
            target["metadata"].setdefault("linked_source_metadata", {})[":".join(identity)] = row["metadata"]
            if target["metadata"].get("open_24h") is None and row["metadata"].get("open_24h") is True:
                target["metadata"]["open_24h"] = True
                target["field_sources"]["open_24h"] = ":".join(identity)
        else:
            i, method, score, distance = len(facilities), "new_record", None, None
            target = {k: v for k, v in row.items() if k not in {"raw", "metadata"}}
            target["metadata"] = dict(row["metadata"])
            target["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "flareai-emergency:" + ":".join(identity)))
            target["source_ids"] = [row["source"]]
            target["field_sources"] = {k: ":".join(identity) for k in (*scalar_fields, "lat", "lon") if row.get(k) is not None}
            if len(matches) > 1:
                target["metadata"]["ambiguous_match_candidates"] = [facilities[m[0]]["id"] for m in matches]
            facilities.append(target)
            if row["lat"] is not None:
                grid[cell].append(i)
        if row["lat"] is not None:
            members[i].append((row["lat"], row["lon"]))
        names[name_key].add(i)
        addresses[address_key].add(i)
        for phone in row["phones"]:
            phones[phone].add(i)
        links.append({**row, "facility_id": target["id"], "match_method": method, "match_score": score, "match_distance_km": distance})
    return facilities, links


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE build_metadata(key TEXT PRIMARY KEY, value_json TEXT NOT NULL CHECK(json_valid(value_json)));
CREATE TABLE sources(id TEXT PRIMARY KEY, name TEXT NOT NULL, url TEXT, license TEXT, scope TEXT, official INTEGER NOT NULL);
CREATE TABLE downloads(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id), metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)));
CREATE TABLE categories(id TEXT PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE facilities(
    pk INTEGER PRIMARY KEY, id TEXT NOT NULL UNIQUE, name TEXT, address TEXT, municipality TEXT,
    province TEXT, autonomous_community TEXT, postcode TEXT, lat REAL, lon REAL,
    phone TEXT, email TEXT, website TEXT, operator TEXT, coordinate_method TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    CHECK((lat IS NULL AND lon IS NULL) OR (lat IS NOT NULL AND lon IS NOT NULL AND lat BETWEEN 27 AND 44.5 AND lon BETWEEN -19 AND 5))
);
CREATE TABLE facility_categories(facility_id TEXT NOT NULL REFERENCES facilities(id), category_id TEXT NOT NULL REFERENCES categories(id), PRIMARY KEY(facility_id,category_id));
CREATE TABLE contacts(facility_id TEXT NOT NULL REFERENCES facilities(id), kind TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY(facility_id,kind,value));
CREATE TABLE source_records(
    source_id TEXT NOT NULL REFERENCES sources(id), source_record_id TEXT NOT NULL,
    facility_id TEXT NOT NULL REFERENCES facilities(id), download_id TEXT REFERENCES downloads(id),
    source_url TEXT, match_method TEXT NOT NULL, match_score REAL, match_distance_km REAL,
    normalized_json TEXT NOT NULL CHECK(json_valid(normalized_json)), raw_json TEXT NOT NULL CHECK(json_valid(raw_json)),
    PRIMARY KEY(source_id,source_record_id)
);
CREATE INDEX facilities_province ON facilities(province,municipality);
CREATE INDEX facilities_region ON facilities(autonomous_community);
CREATE INDEX facilities_name ON facilities(name COLLATE NOCASE);
CREATE INDEX categories_lookup ON facility_categories(category_id,facility_id);
CREATE INDEX source_records_facility ON source_records(facility_id);
CREATE VIRTUAL TABLE facility_rtree USING rtree(pk,min_lon,max_lon,min_lat,max_lat);
CREATE TRIGGER facilities_insert AFTER INSERT ON facilities WHEN NEW.lat IS NOT NULL BEGIN
    INSERT INTO facility_rtree VALUES(NEW.pk,NEW.lon,NEW.lon,NEW.lat,NEW.lat);
END;
CREATE TRIGGER facilities_delete AFTER DELETE ON facilities BEGIN
    DELETE FROM facility_rtree WHERE pk=OLD.pk;
END;
CREATE TRIGGER facilities_update AFTER UPDATE OF pk,lat,lon ON facilities BEGIN
    DELETE FROM facility_rtree WHERE pk=OLD.pk;
    INSERT INTO facility_rtree SELECT NEW.pk,NEW.lon,NEW.lon,NEW.lat,NEW.lat WHERE NEW.lat IS NOT NULL;
END;
CREATE VIEW unlocated_facilities AS SELECT * FROM facilities WHERE lat IS NULL;
CREATE VIEW coverage AS SELECT f.autonomous_community,f.province,c.category_id,
    count(*) AS records,sum(f.lat IS NOT NULL) AS geocoded FROM facilities f
    JOIN facility_categories c ON c.facility_id=f.id GROUP BY 1,2,3;
"""


def facility_metadata(row: dict) -> dict:
    return {**row["metadata"], "field_sources": row["field_sources"], "source_ids": row["source_ids"],
            "operational_status": "not_verified", "dispatch_authorized": False}


def write_database(path: Path, facilities: list[dict], links: list[dict], downloads: list[dict], metadata: dict) -> None:
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript(SCHEMA)
        db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        catalog = {row["id"]: row for row in source_catalog()}
        for link in links:
            if link["source"] not in catalog:
                raise ValueError(f"Fuente no registrada: {link['source']}")
        db.executemany("INSERT INTO sources VALUES(:id,:name,:url,:license,:scope,:official)", catalog.values())
        db.executemany("INSERT INTO categories VALUES(?,?)", CATEGORIES.items())
        db.executemany("INSERT INTO build_metadata VALUES(?,?)", [(k, dumps(v)) for k, v in metadata.items()])
        db.executemany("INSERT INTO downloads VALUES(?,?,?)", [(d["id"], d["source_id"], dumps(d)) for d in downloads])
        for row in facilities:
            values = [row[k] for k in ("id", "name", "address", "municipality", "province", "autonomous_community", "postcode", "lat", "lon")]
            values.extend([row["phones"][0] if row["phones"] else None, row["email"], row["website"], row["operator"], row["coordinate_method"], dumps(facility_metadata(row))])
            db.execute("INSERT INTO facilities(id,name,address,municipality,province,autonomous_community,postcode,lat,lon,phone,email,website,operator,coordinate_method,metadata_json) VALUES(" + ",".join("?" for _ in values) + ")", values)
            db.executemany("INSERT INTO facility_categories VALUES(?,?)", [(row["id"], c) for c in row["categories"]])
            db.executemany("INSERT INTO contacts VALUES(?,?,?)", [(row["id"], "phone", p) for p in row["phones"]])
        for link in links:
            normalized_row = {k: v for k, v in link.items() if k != "raw"}
            db.execute("INSERT INTO source_records VALUES(?,?,?,?,?,?,?,?,?,?)", (
                link["source"], link["source_record_id"], link["facility_id"], link["download_id"], link["source_url"],
                link["match_method"], link["match_score"], link["match_distance_km"], dumps(normalized_row), dumps(link["raw"])))
        db.execute("ANALYZE")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Base SQLite inconsistente")
        expected = sum(row["lat"] is not None for row in facilities)
        if db.execute("SELECT count(*) FROM facility_rtree").fetchone()[0] != expected:
            raise ValueError("Índice espacial incompleto")


def proximity(db: sqlite3.Connection, lat: float, lon: float, radius_km: float, category: str | None = None, limit: int = 100) -> list[dict]:
    if not all(math.isfinite(v) for v in (lat, lon, radius_km)) or not -90 <= lat <= 90 or not -180 <= lon <= 180 or not 0 < radius_km <= 2000 or limit <= 0:
        raise ValueError("Coordenadas, radio (0,2000] km o límite inválidos")
    if category is not None and category not in CATEGORIES:
        raise ValueError("Categoría desconocida")
    delta_lat = math.degrees(radius_km / EARTH_KM)
    max_lat = min(90, abs(lat) + delta_lat)
    delta_lon = 180 if max_lat == 90 else min(180, delta_lat / math.cos(math.radians(max_lat)))
    west, east = lon - delta_lon, lon + delta_lon
    if west < -180 or east > 180:
        west, east = -180, 180
    if not any(row[0] == "distance_km" and row[4] == 4 for row in db.execute("PRAGMA function_list")):
        db.create_function("distance_km", 4, distance_km, deterministic=True)
    cursor = db.execute("""
        SELECT f.*,distance_km(?,?,f.lat,f.lon) AS distance_km FROM facility_rtree r
        JOIN facilities f ON f.pk=r.pk
        WHERE r.max_lon>=? AND r.min_lon<=? AND r.max_lat>=? AND r.min_lat<=?
        AND (? IS NULL OR EXISTS(SELECT 1 FROM facility_categories c WHERE c.facility_id=f.id AND c.category_id=?))
        AND distance_km(?,?,f.lat,f.lon)<=? ORDER BY distance_km,f.id LIMIT ?
    """, (lat, lon, west, east, lat - delta_lat, lat + delta_lat, category, category, lat, lon, radius_km, limit))
    fields = [col[0] for col in cursor.description]
    return [dict(zip(fields, row)) for row in cursor]


def geojson_bytes(facilities: list[dict], metadata: dict) -> bytes:
    features = []
    for row in facilities:
        if row["lat"] is None:
            continue
        properties = {k: row[k] for k in ("name", "categories", "address", "municipality", "province", "autonomous_community",
                       "postcode", "phones", "email", "website", "operator", "coordinate_method")}
        properties["metadata"] = facility_metadata(row)
        features.append({"type": "Feature", "id": row["id"], "geometry": {"type": "Point", "coordinates": [row["lon"], row["lat"]]}, "properties": properties})
    return dumps({"type": "FeatureCollection", "metadata": metadata, "features": features}).encode("utf-8")


def report(facilities: list[dict], links: list[dict], statuses: list[dict], geography: Geography) -> dict:
    geocoded = [row for row in facilities if row["lat"] is not None]
    return {"schema_version": SCHEMA_VERSION, "build_id": str(uuid.uuid4()), "built_at": now(),
            "acquisition_complete": all(s["status"] == "ok" for s in statuses), "inventory_exhaustive": False,
            "operationally_verified": False, "source_status": statuses, "source_catalog": source_catalog(),
            "boundary_sha256": geography.sha256, "records": len(facilities), "geocoded": len(geocoded),
            "unlocated": len(facilities) - len(geocoded), "source_records": len(links),
            "merged_records": len(links) - len(facilities),
            "geocoded_by_region": {region: sum(r["autonomous_community"] == region for r in geocoded) for region in REGIONS},
            "geocoded_by_province": {p: sum(r["province"] == p for r in geocoded) for p in sorted(set(geography.names))},
            "geocoded_by_category": {c: sum(c in r["categories"] for r in geocoded) for c in CATEGORIES},
            "missing_fields_geocoded": {f: sum(not r[f] for r in geocoded) for f in ("name", "address", "municipality", "province", "phones")},
            "matching_methods": dict(Counter(r["match_method"] for r in links)),
            "osm_snapshot_dates": sorted({s["osm_base_timestamp"] for s in statuses if s.get("osm_base_timestamp")}),
            "geocoded_region_category_matrix": {region: {c: sum(r["autonomous_community"] == region and c in r["categories"] for r in geocoded) for c in CATEGORIES} for region in REGIONS},
            "limitations": ["Cobertura de consulta nacional; no equivale a inventario exhaustivo.",
                            "Sin coordenadas publicadas ni enlace inequívoco: solo SQLite, nunca punto inventado.",
                            "OSM es colaborativo; las fechas de instantánea difieren entre servidores y descargas.",
                            "Centros, teléfonos, disponibilidad, capacidades y rutas requieren verificación operativa.",
                            "Helipuertos generales no implican autorización ni capacidad de uso en emergencias.",
                            "La deduplicación conservadora puede dejar duplicados; enlaces inferidos auditables.",
                            "Municipios solo publicados, no inferidos desde el núcleo de población más cercano."],
            "attribution": "© OpenStreetMap contributors (ODbL); Ministerio de Sanidad; Ayuntamiento de Madrid; IECA/Junta de Andalucía (CC BY 4.0); geoBoundaries/INE (límites provinciales)."}


def build(args) -> int:
    cache = Cache(args.cache_dir, offline=args.offline, refresh=args.refresh, retries=args.retries)
    records, downloads, statuses = acquire(cache, tuple(args.overpass_endpoint) if args.overpass_endpoint else OVERPASS)
    acquisition = {"attempted_at": now(), "sources": statuses}
    atomic_write(args.cache_dir / "last_acquisition.json", dumps(acquisition).encode())
    failed = [s for s in statuses if s["status"] != "ok"]
    for status in failed:
        print(dumps(status), file=sys.stderr)
    if failed and not args.allow_partial:
        print("Adquisición incompleta: no se publican artefactos. Reejecutar para reanudar; --allow-partial acepta explícitamente un resultado parcial.", file=sys.stderr)
        return 2
    if args.download_only:
        return 0
    if not records:
        raise ValueError("No hay registros que compilar")
    geography = Geography(args.provinces)
    for row in records:
        geography.enrich(row)
    facilities, links = deduplicate(records)
    metadata = report(facilities, links, statuses, geography)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    db_path = output / "emergencias_espana.db"
    geo_path = output / "emergencias_espana.geojson"
    with tempfile.TemporaryDirectory(prefix=".emergency-build-", dir=output) as temporary:
        stage = Path(temporary) / db_path.name
        write_database(stage, facilities, links, downloads, metadata)
        geo_data = geojson_bytes(facilities, metadata)
        geo = json.loads(geo_data)
        if len(geo["features"]) != metadata["geocoded"]:
            raise ValueError("GeoJSON y SQLite no coinciden")
        metadata["artifacts"] = {db_path.name: {"sha256": hashlib.sha256(stage.read_bytes()).hexdigest(), "bytes": stage.stat().st_size},
                                 geo_path.name: {"sha256": hashlib.sha256(geo_data).hexdigest(), "bytes": len(geo_data)}}
        atomic_write(geo_path, geo_data)
        os.replace(stage, db_path)
        atomic_write(output / "emergencias_espana.manifest.json", json.dumps(metadata, ensure_ascii=False, sort_keys=True, allow_nan=False, indent=2).encode("utf-8"))
    print(dumps({k: metadata[k] for k in ("build_id", "records", "geocoded", "unlocated", "merged_records", "geocoded_by_region", "geocoded_by_category")}), flush=True)
    return 0


def verify_bundle(output: Path) -> dict:
    manifest = json.loads((output / "emergencias_espana.manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["artifacts"].items():
        data = (output / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected["sha256"] or len(data) != expected["bytes"]:
            raise ValueError(f"Artefacto modificado o publicación interrumpida: {name}")
    geo = json.loads((output / "emergencias_espana.geojson").read_text(encoding="utf-8"))
    if geo["metadata"]["build_id"] != manifest["build_id"]:
        raise ValueError("GeoJSON pertenece a otra compilación")
    path = output / "emergencias_espana.db"
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)] or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite no supera integridad o claves externas")
        build_id = json.loads(db.execute("SELECT value_json FROM build_metadata WHERE key='build_id'").fetchone()[0])
        if build_id != manifest["build_id"]:
            raise ValueError("SQLite pertenece a otra compilación")
        counts = db.execute("SELECT count(*),sum(lat IS NOT NULL) FROM facilities").fetchone()
        if counts != (manifest["records"], manifest["geocoded"]):
            raise ValueError("Recuentos del manifiesto incorrectos")
        points = {row[0]: [row[1], row[2]] for row in db.execute("SELECT id,lon,lat FROM facilities WHERE lat IS NOT NULL")}
        if {f["id"]: f["geometry"]["coordinates"] for f in geo["features"]} != points or len(geo["features"]) != len(points):
            raise ValueError("Identificadores/coordenadas GeoJSON diferentes a SQLite")
        if db.execute("SELECT count(*) FROM facility_rtree").fetchone()[0] != len(points):
            raise ValueError("Recuento RTree incorrecto")
        invalid = db.execute("SELECT count(*) FROM facilities f LEFT JOIN facility_rtree r ON r.pk=f.pk WHERE f.lat IS NOT NULL AND (r.pk IS NULL OR r.min_lon>f.lon OR r.max_lon<f.lon OR r.min_lat>f.lat OR r.max_lat<f.lat)").fetchone()[0]
        if invalid:
            raise ValueError("RTree no contiene las coordenadas reales")
        spatial_checks = []
        for lat, lon in ((40.4168, -3.7038), (28.1248, -15.43), (39.57, 2.65), (35.89, -5.32), (35.29, -2.94)):
            indexed = {r["id"] for r in proximity(db, lat, lon, 20, limit=100000)}
            full_scan = {identifier for identifier, (x, y) in points.items() if distance_km(lat, lon, y, x) <= 20}
            if indexed != full_scan:
                raise ValueError("Consulta espacial no equivale al barrido exacto")
            spatial_checks.append({"lat": lat, "lon": lon, "radius_km": 20, "matches": len(indexed)})
        source_counts = dict(db.execute("SELECT source_id,count(*) FROM source_records GROUP BY source_id"))
    return {"verified": True, "build_id": build_id, "records": counts[0], "geocoded": counts[1],
            "source_counts": source_counts, "spatial_checks": spatial_checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas auditable de infraestructura pública de emergencias en España")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data/emergency_sources")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    parser.add_argument("--provinces", type=Path, default=ROOT / "static/provinces.geojson")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--download-only", action="store_true")
    parser.add_argument("--verify", action="store_true", help="Verifica hashes, integridad, GeoJSON y consultas RTree sin red")
    parser.add_argument("--overpass-endpoint", action="append", help="Endpoint HTTPS; repetible, en orden de preferencia")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--near", nargs=3, type=float, metavar=("LAT", "LON", "RADIO_KM"))
    parser.add_argument("--category", choices=sorted(CATEGORIES))
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if args.retries < 1 or args.retries > 5:
        parser.error("--retries debe estar entre 1 y 5")
    if args.offline and args.refresh:
        parser.error("--offline y --refresh son incompatibles")
    if args.overpass_endpoint and any(not u.startswith("https://") for u in args.overpass_endpoint):
        parser.error("Los endpoints deben utilizar HTTPS")
    if args.verify:
        print(dumps(verify_bundle(args.output_dir)))
        return 0
    if args.near:
        path = args.output_dir / "emergencias_espana.db"
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            print(dumps(proximity(db, args.near[0], args.near[1], args.near[2], category=args.category, limit=args.limit)))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    lock = args.output_dir / ".emergency-build.lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        parser.error(f"Otro escritor o bloqueo de una ejecución interrumpida: {lock}")
    try:
        with os.fdopen(handle, "w") as stream:
            stream.write(str(os.getpid()))
        return build(args)
    finally:
        lock.unlink()


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
