import json
import threading
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from app import Store, Handler
from test_visual_demo import MemoryDB
from verify_director_ui import instrument_map

store = Store(database=MemoryDB(), demo_enabled=True, director_enabled=True, presentation=True, visual_demo=True)
Handler.store = store
errors=[]
stop=threading.Event()
def work():
    while not stop.is_set():
        try: store.director.step()
        except Exception as e: errors.append(repr(e)); break
        stop.wait(.5)
server=ThreadingHTTPServer(('127.0.0.1',0), Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
threading.Thread(target=work,daemon=True).start()
try:
 with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/api/context?*',lambda r:r.fulfill(status=503,body='{}',content_type='application/json'))
    page.route('**/api/webcams',lambda r:r.fulfill(json={'cameras':[],'sources':[]}))
    page.route('**/roads/**',lambda r:r.abort())
    page.route('**/app.js',instrument_map)
    page.goto(f'http://127.0.0.1:{server.server_port}/')
    page.locator('.response-vehicle').first.wait_for(timeout=45000)
    page.wait_for_function("document.querySelector('#evidence-satellite img')?.naturalWidth > 0 && document.querySelector('#evidence-camera img')?.naturalWidth > 0",timeout=60000)
    page.wait_for_function('window.__directorMap.getZoom() >= 13', timeout=25000)
    page.screenshot(path='/private/tmp/flareai-visual-demo.png')
    assert 'decisiones simuladas' in page.locator('.demo-mode').inner_text()
    state=store.director.public_state()
    assert any(a['resource']['kind']=='helicopter' for a in state['assignments'].values())
    print(json.dumps({'vehicles':len(state['assignments']),'fires':len(state['scenario']['incidents']),'images':page.locator('#agent-evidence img').count(),'zoom':page.evaluate('window.__directorMap.getZoom()'),'errors':errors}))
    assert not errors
    browser.close()
finally:
 stop.set(); server.shutdown(); store.demo.close()
