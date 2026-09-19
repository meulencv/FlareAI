from __future__ import annotations

import argparse
import asyncio
import html
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone

from database import ROOT, Database
from territorial import allowed_player


async def verify_players(database: Database, limit: int | None = None, force: bool = False, retry_failed: bool = False) -> dict:
    with database.verification_lock(804025) as acquired:
        return await _verify_players(database, limit, force, retry_failed) if acquired else {}


async def _verify_players(database: Database, limit: int | None = None, force: bool = False, retry_failed: bool = False) -> dict:
    from playwright.async_api import Error, async_playwright

    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', str(ROOT / '.local/playwright-browsers'))
    checks = database.camera_checks()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    candidates = []
    for camera in database.catalog()['cameras']:
        if camera['kind'] != 'player':
            continue
        saved = checks.get(camera['id'])
        if retry_failed and (not saved or saved['status'] != 'unavailable'):
            continue
        if not (force or retry_failed) and saved and saved['valid_until'] > now and saved['data'].get('method') in {'image_decoded', 'browser_video_playing', 'browser_embed_failed'}:
            continue
        asset = database.get_asset('player:' + camera['id'])
        if asset and allowed_player(asset['data'].get('player_url') or ''):
            candidates.append((camera, asset['data']))
    if limit is not None:
        candidates = candidates[:limit]
    if not candidates:
        return {}
    counts: Counter = Counter()
    semaphore = asyncio.Semaphore(4)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()

        async def check(camera: dict, media: dict) -> None:
            async with semaphore:
                page = await browser.new_page(viewport={'width': 640, 'height': 480})
                status, reason = 'unavailable', 'No se observó reproducción en el visor integrado'
                previous: dict[str, float] = {}
                clicked: set[str] = set()
                try:
                    content = '<!doctype html><iframe style="width:600px;height:400px" sandbox="allow-scripts allow-same-origin allow-presentation" referrerpolicy="no-referrer" allow="autoplay; fullscreen" src="' + html.escape(media['player_url'], quote=True) + '"></iframe>'
                    await page.route('http://127.0.0.1:8090/__camera-check', lambda route: route.fulfill(status=200, content_type='text/html', body=content))
                    await page.goto('http://127.0.0.1:8090/__camera-check', wait_until='domcontentloaded')
                    deadline = time.monotonic() + 12
                    while time.monotonic() < deadline:
                        blocked = False
                        for frame in page.frames[1:]:
                            try:
                                text = await frame.locator('body').inner_text(timeout=500)
                                if 'only be viewed on the specified sites' in text.lower():
                                    status, reason, blocked = 'external', 'El proveedor restringe el reproductor a sus dominios autorizados', True
                                    break
                                if frame.url not in clicked:
                                    for control in await frame.get_by_role('button', name='Play', exact=True).all():
                                        if await control.is_visible():
                                            await control.click(timeout=800)
                                            clicked.add(frame.url)
                                            break
                                videos = await frame.locator('video').evaluate_all('(nodes) => nodes.map(v => { v.muted=true; if(v.paused) v.play().catch(()=>{}); return {width:v.videoWidth, ready:v.readyState, time:v.currentTime}; })')
                                for index, video in enumerate(videos):
                                    key = frame.url + str(index)
                                    if video['width'] > 0 and video['ready'] >= 2 and video['time'] > previous.get(key, video['time']):
                                        status, reason, blocked = 'available', 'Vídeo integrado con fotogramas y reproducción observada', True
                                        break
                                    previous[key] = video['time']
                            except Error:
                                continue
                            if blocked:
                                break
                        if blocked:
                            break
                        await asyncio.sleep(.4)
                except Error:
                    reason = 'El reproductor no se pudo cargar en el navegador'
                finally:
                    await page.close()
                data = {**media, 'browser_verified_until': time.time() + 21600 if status == 'available' else 0,
                        'browser_checked_at': datetime.now(timezone.utc).isoformat()}
                database.asset('player:' + camera['id'], 'player', data)
                database.camera_check(camera['id'], status, 'player' if status == 'available' else None,
                                      {'method': 'browser_video_playing' if status == 'available' else 'browser_embed_failed',
                                       'reason': reason, 'emission_verified': status == 'available', 'source_url': media['player_url'],
                                       'browser_verified_until': data['browser_verified_until'], 'browser_checked_at': data['browser_checked_at']})
                counts[status] += 1
                if sum(counts.values()) % 10 == 0 or sum(counts.values()) == len(candidates):
                    print(json.dumps({'players_checked': sum(counts.values()), 'total': len(candidates), 'results': dict(counts)}), flush=True)

        try:
            await asyncio.gather(*(check(camera, media) for camera, media in candidates))
        finally:
            await browser.close()
    return dict(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--retry-failed', action='store_true')
    options = parser.parse_args()
    asyncio.run(verify_players(Database(), options.limit, options.force, options.retry_failed))
