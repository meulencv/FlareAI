from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / 'happyrobot-112/static'
FILES = ('index.html', 'app.js', 'audio.js', 'styles.css', 'alerts.html', 'alerts.js', 'alerts.css')


def package(output: Path, src: bool = False) -> None:
    app = 'src/app' if src else 'app'
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'x', compression=ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(STATIC / name, 'public/112/' + name)
        archive.write(ROOT / 'happyrobot-112/cloud/route.js', app + '/112/api/[...path]/route.js')
        archive.writestr(app + '/112/route.js', "export function GET(request) { return Response.redirect(new URL('/112/index.html', request.url), 307); }\n")
        archive.writestr(app + '/112/alerts/route.js', "export function GET(request) { return Response.redirect(new URL('/112/alerts.html', request.url), 307); }\n")
        archive.writestr('.env.example', 'HAPPYROBOT_API_KEY=\nTWIN_API_KEY=\nHAPPYROBOT_WORKFLOW_ID=\nDEMO_ACCESS_CODE=\nDEMO_COOKIE_SECRET=\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / '.local' / ('112-happyrobot-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '.zip'))
    parser.add_argument('--src', action='store_true', help='Usar src/app si la plantilla Next.js tiene esa estructura')
    args = parser.parse_args()
    package(args.output, args.src)
    print(args.output)
