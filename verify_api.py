import argparse
import csv
import hashlib
import io
import json
from typing import TypedDict, cast
from urllib.error import HTTPError
from urllib.request import urlopen

from PIL import Image

from gfs import ROOT, iso, utcnow, write_json
from incidents import Incident
from satellite import Picture, coverage_fraction


class Payload(TypedDict):
    status: str
    incidents: list[Incident]
    fires_checked_at: str


def verify(base: str) -> None:
    with urlopen(base + "/api/data", timeout=15) as response:
        payload = cast(Payload, json.load(response))
    with urlopen(base + "/api/incidents.csv", timeout=15) as response:
        rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8-sig"))))
    assert len(rows) == len(payload["incidents"])
    assert all(i["burned_area_ha"] is None for i in payload["incidents"])
    assert all(i["weather"]["air_temperature_c"] is not None for i in payload["incidents"])
    incident = payload["incidents"][0]
    pictures = []
    for mode in ["natural", "swir"]:
        with urlopen(f"{base}/api/satellite?id={incident['id']}&mode={mode}", timeout=180) as response:
            picture = cast(Picture, json.load(response))
        with urlopen(base + picture["url"], timeout=15) as response:
            body = response.read()
        with Image.open(io.BytesIO(body)) as image:
            assert image.size == (900, 600)
            coverage = coverage_fraction(image)
            assert coverage >= .5
        pictures.append({**picture, "sha256": hashlib.sha256(body).hexdigest(), "coverage": coverage})
    for route, expected in [("/api/satellite", 400), ("/api/satellite?id=unknown", 400),
                            ("/api/satellite?id=" + incident["id"] + "&mode=invalid", 400),
                            ("/requirements.txt", 404)]:
        try:
            urlopen(base + route, timeout=10)
            raise AssertionError("La ruta inválida debería fallar")
        except HTTPError as error:
            assert error.code == expected
    result = {
        "checked_at": iso(utcnow()), "base_url": base, "status": payload["status"],
        "zones": len(rows), "observations": sum(i["observations"] for i in payload["incidents"]),
        "fires_checked_at": payload["fires_checked_at"], "example": incident,
        "pictures": pictures, "csv_json_count_match": True, "invalid_routes_checked": 4,
    }
    path = ROOT / "evidence" / f"api_{payload['status']}.json"
    write_json(path, result)
    print(f"API verificada: {len(rows)} zonas, ambas imágenes, CSV y cuatro rutas inválidas. {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8090")
    verify(parser.parse_args().url.rstrip("/"))
