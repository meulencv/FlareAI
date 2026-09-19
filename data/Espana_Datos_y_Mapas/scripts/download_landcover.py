from pathlib import Path

import rasterio
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
URL = (
    "https://zenodo.org/records/3939050/files/"
    "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
)
EXTENTS = {
    "peninsula_baleares_ceuta_melilla": (-9.7, 35.1, 4.5, 44.1),
    "canarias": (-18.3, 27.5, -13.3, 29.6),
}


def main() -> None:
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
        GDAL_HTTP_TIMEOUT="120",
        GDAL_HTTP_MAX_RETRY="3",
        GDAL_HTTP_MULTIPLEX="YES",
        GDAL_CACHEMAX=256,
    ):
        with rasterio.open(URL) as source:
            for name, bounds in EXTENTS.items():
                target = ROOT / "raw" / f"lc2019_{name}.tif"
                if target.exists():
                    continue
                window = from_bounds(*bounds, source.transform).round_offsets().round_lengths()
                print("Downloading", name, window, flush=True)
                data = source.read(1, window=window)
                profile = source.profile.copy()
                profile.update(
                    width=data.shape[1], height=data.shape[0],
                    transform=source.window_transform(window), compress="deflate",
                )
                with rasterio.open(target, "w", **profile) as destination:
                    destination.write(data, 1)
                    destination.update_tags(source_url=URL, reference_year="2019")
                print("Saved", target, target.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
