from __future__ import annotations

import argparse
import threading
import time
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from playwright.sync_api import expect, sync_playwright

from app import Handler, Store
from database import Database
from demo import DemoBridge, HappyRobotProvider
from director import Director
from test_demo import message


def verify(audio: Path) -> None:
    if not audio.is_file():
        raise ValueError('Se requiere un WAV PCM de prueba con el parte hablado, sin datos personales')
    database = Database()
    store = Store(offline=True, database=database)
    provider = HappyRobotProvider(database)
    if not provider.responder_ready:
        raise RuntimeError('Publica primero el workflow de bomberos')
    store.demo = DemoBridge(database, provider=provider, resolver=lambda query: {
        'lat': 41.1189, 'lon': 1.2445, 'label': 'Tarragona · prueba de voz sintética', 'precision': 'coordinates', 'source': 'test_fixture'})
    citizen = str(uuid.uuid4())
    store.demo.register(citizen)
    store.demo.accept(citizen, [message('Tarragona')])
    store.demo.calls[citizen]['poll_until'] = 0
    incident_id = 'demo:' + citizen
    store.director = Director(store, planner=SimpleNamespace(ready=False))

    class VoiceHandler(Handler):
        def log_message(self, *args):
            pass

    VoiceHandler.store = store
    with ThreadingHTTPServer(('127.0.0.1', 0), VoiceHandler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(args=['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
                    '--use-file-for-fake-audio-capture=' + str(audio.resolve()) + '%noloop'])
                page = browser.new_page(permissions=['microphone'], viewport={'width': 390, 'height': 844})
                page.add_init_script('''
const capture = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
navigator.mediaDevices.getUserMedia = constraints => capture({...constraints, audio: constraints.audio ? {
  ...(typeof constraints.audio === 'object' ? constraints.audio : {}), echoCancellation: false, noiseSuppression: false, autoGainControl: false
} : false});
window.__voicePeers = [];
const Peer = window.RTCPeerConnection;
window.RTCPeerConnection = class extends Peer { constructor(...args) { super(...args); window.__voicePeers.push(this); } };
''')
                page.goto(f'http://127.0.0.1:{server.server_port}/112/')
                page.locator('[data-number="123"]').click()
                page.locator('#incident-choice').select_option(incident_id)
                page.locator('#call-button').click()
                expect(page.locator('#status')).to_have_text('En llamada', timeout=45000)
                run_id = next(key for key in store.demo.calls if key != citizen)
                print('Webcall real de bomberos con audio sintético:', run_id, flush=True)
                deadline = time.monotonic() + 85
                required = {'llegada': 'confirmada', 'incendio': 'confirmado', 'es_alert': 'solicitado', 'refuerzos': 'solicitado', 'helicoptero': 'solicitado'}
                while time.monotonic() < deadline:
                    store.demo.poll_once()
                    part = store.demo.calls[run_id]['part']
                    if all(part.get(key) == value for key, value in required.items()):
                        break
                    page.wait_for_timeout(2000)
                stats = page.evaluate('''async () => {
  const result = [];
  for (const pc of window.__voicePeers) for (const row of (await pc.getStats()).values()) {
    if (row.type === 'outbound-rtp' && row.kind === 'audio') result.push({type: row.type, bytes: row.bytesSent, packets: row.packetsSent});
    if (row.type === 'media-source' && row.kind === 'audio') result.push({type: row.type, energy: row.totalAudioEnergy});
  }
  return result;
}''')
                print('Estadísticas de audio de prueba:', stats, flush=True)
                page.locator('#hangup-button').click()
                store.director.step()
                captured = dict(store.demo.calls[run_id]['part'])
                browser.close()
                if not all(captured.get(key) == value for key, value in required.items()):
                    print('Campos recibidos:', captured, flush=True)
                    raise RuntimeError('La voz real no produjo todos los campos esperados; no se considera verificada')
                assert store.director.alert_feed(0)['events'], 'El parte debe activar el receptor simulado'
                database.asset('responder-voice-verification', 'test_evidence', {'run_id': run_id, 'workflow_id': provider.responder_workflow_id,
                    'input': 'synthetic Spanish speech over real LiveKit webcall; civilian location fixture', 'part': captured,
                    'notifications': store.director.alert_feed(0)['events'], 'at': time.time()})
                print('Voz sintética → HappyRobot real → actualizar_parte → llegada/confirmación/refuerzos/helicóptero/ES-Alert: OK', flush=True)
        finally:
            server.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cloud', action='store_true', help='Consume cuota de voz HappyRobot; no contacta con servicios reales')
    parser.add_argument('--audio', type=Path, required=True)
    args = parser.parse_args()
    if not args.cloud:
        parser.error('Se requiere --cloud explícito para consumir cuota de voz')
    verify(args.audio)
