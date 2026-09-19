from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from validate_package import digest

ROOT = Path(__file__).resolve().parents[1]
RAW_INCLUDED = [
    "read.me", "zenodo.json",
    "lc2019_peninsula_baleares_ceuta_melilla.tif", "lc2019_canarias.tif",
]


def main() -> None:
    files = [ROOT / name for name in [
        "README.md", "FUENTES.md", "requirements.txt", "Atlas_Espana.pdf",
    ]]
    files += sorted((ROOT / "scripts").glob("*.py"))
    files += sorted((ROOT / "mapas").glob("*"))
    files += [
        path for path in sorted((ROOT / "output").glob("*"))
        if path.name != "censo_preparado.parquet"
    ]
    files += [ROOT / "raw" / name for name in RAW_INCLUDED]
    manifest = ROOT / "SHA256SUMS.txt"
    manifest.write_text("".join(
        f"{digest(path)}  {path.relative_to(ROOT)}\n" for path in files
    ))
    target = ROOT / "Espana_Datos_y_Mapas.zip"
    with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files + [manifest]:
            archive.write(path, Path("Espana_Datos_y_Mapas") / path.relative_to(ROOT))
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        print("Archive entries:", len(archive.namelist()))
    print("Archive:", target, "bytes:", target.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
