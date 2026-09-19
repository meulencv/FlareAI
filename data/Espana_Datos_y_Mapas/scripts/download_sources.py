from pathlib import Path
from shutil import copyfileobj
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
SOURCES = {
    "Eurostat_Census-GRID_2021_V3.zip":
        "https://gisco-services.ec.europa.eu/census/2021/Eurostat_Census-GRID_2021_V3.zip",
    "nuts2_2024.geojson":
        "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
        "NUTS_RG_01M_2024_4326_LEVL_2.geojson",
    "spain.osm.pbf": "https://download.geofabrik.de/europe/spain-latest.osm.pbf",
    "canarias.osm.pbf": "https://download.geofabrik.de/africa/canary-islands-latest.osm.pbf",
    "zenodo.json": "https://zenodo.org/api/records/3939050",
}


def main() -> None:
    RAW.mkdir(exist_ok=True)
    (ROOT / "output").mkdir(exist_ok=True)
    for name, url in SOURCES.items():
        target = RAW / name
        if target.exists():
            continue
        partial = target.with_suffix(target.suffix + ".part")
        print("Downloading", name, flush=True)
        with urlopen(url, timeout=180) as response, partial.open("wb") as output:
            copyfileobj(response, output, length=1024 * 1024)
        partial.replace(target)
    with ZipFile(RAW / "Eurostat_Census-GRID_2021_V3.zip") as archive:
        for name in ["ESTAT_Census_2021_country.csv.zip", "read.me"]:
            target = RAW / name
            if not target.exists():
                with archive.open(f"Eurostat_Census-GRID_2021_V3/{name}") as source, target.open("wb") as output:
                    copyfileobj(source, output)


if __name__ == "__main__":
    main()
