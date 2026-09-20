import json
import os
import time
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from app import Store
from database import seed_asset
from visual_demo import enabled

ROOT = Path(__file__).parent


class MemoryDB:
    dynamic_cloud = False

    def __init__(self):
        self.saved = {}
        self.assets = {}

    def get_asset(self, key):
        if key not in self.assets:
            if key.startswith('map:'):
                value = json.loads((ROOT / 'static' / key[4:]).read_text())
                self.assets[key] = {'data': {'places': value} if key.endswith('places.json') else value}
            else:
                self.assets[key] = seed_asset(key)
        return self.assets[key]

    def snapshot(self, kind):
        return json.loads((ROOT / 'examples' / ('firms.geojson' if kind == 'fires' else 'weather.json')).read_text())

    def save_incidents(self, rows):
        pass

    def start_demo(self, session):
        pass

    def confirmations(self, now):
        return {}

    def save_director(self, session, state):
        self.saved = deepcopy(state)

    def director_history(self, session):
        return {'session_id': session, 'events': self.saved.get('events', [])}


class VisualTests(unittest.TestCase):
    def test_local_is_unchanged_and_render_defaults_to_visual(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(enabled())
        with patch.dict(os.environ, {'RENDER_SERVICE_ID': 'demo'}, clear=True):
            self.assertTrue(enabled())
        with patch.dict(os.environ, {'RENDER_SERVICE_ID': 'demo', 'FLAREAI_VISUAL_DEMO': '0'}, clear=True):
            self.assertFalse(enabled())

    def test_real_graph_cycle_with_helicopter_extinction_and_controls(self):
        store = Store(database=MemoryDB(), demo_enabled=True, director_enabled=True, presentation=True, visual_demo=True)
        d = store.director
        d.visual.random.seed(8)
        self.assertFalse(store.presentation)
        self.assertFalse(store.allow_outbound)
        self.assertFalse(store.demo.provider.ready)
        self.assertIsNone(d.operations)
        now = time.time()
        kinds = set()
        maximum = 0
        for second in range(0, 181, 3):
            with patch('time.time', return_value=now + second):
                d.step()
                maximum = max(maximum, len(d.scene.data['incidents']))
                kinds.update(a['resource']['kind'] for a in d.state['assignments'].values())
                if second == 3:
                    identifier = next(iter(d.scene.data['incidents']))
                    d.scene.command({'action': 'wind', 'incident_id': identifier, 'value': 145})
                    self.assertEqual(d.scene.data['incidents'][identifier]['wind_to'], 145)
                    d.scene.command({'action': 'random_closure'})
                    self.assertTrue(d.scene.data['closures'])
        self.assertTrue({'fire_engine', 'ambulance', 'police', 'helicopter'} <= kinds)
        self.assertGreaterEqual(maximum, 2)
        self.assertIn('closed', {e['kind'] for e in d.state['events']})
        self.assertIn('return', {e['kind'] for e in d.state['events']})
        self.assertEqual(d.state['mode'], 'visual_demo')
        self.assertEqual(d.state['runs'], [])
        store.demo.close()


if __name__ == '__main__':
    unittest.main()
