import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app import Store
from context import Atlas
from database import Database


@unittest.skipUnless(os.environ.get('FLAREAI_TEST_DATABASE') == '1', 'Requiere PostgreSQL importado: FLAREAI_TEST_DATABASE=1')
class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database()
        cls.atlas = Atlas.load()
        cls.store = Store(offline=True, database=cls.db)

    def test_counts_and_idempotent_import(self):
        before = self.db.stats()
        self.db.import_atlas()
        self.db.import_catalog()
        self.assertEqual(before, self.db.stats())
        self.assertEqual(before['grid'], 511226)
        self.assertEqual(before['facilities'], 44787)
        self.assertEqual(before['cameras'], 2926)
        with self.db.connect() as conn:
            total = conn.execute('SELECT sum(population) AS n FROM flare_grid').fetchone()['n']
            self.assertEqual(total, 47400134)

    def test_sql_bounding_queries_match_full_atlas(self):
        for incident in self.store.incidents[:3]:
            local = self.db.nearby_atlas(dict(incident))
            self.assertLess(len(local.grid), 2000)
            result = local.analyze(dict(incident), offline=True)
            reference = self.atlas.analyze(dict(incident), offline=True)
            for field in ('population', 'facilities', 'landcover', 'potential'):
                self.assertEqual(result[field], reference[field])

    def test_snapshot_restore_and_unconfirmed_default(self):
        with patch('app.Atlas.load', side_effect=AssertionError('No CSV en consultas SQL')):
            result = self.store.context(self.store.incidents[0]['id'])
        self.assertTrue(result['potential']['samples'])
        self.assertTrue(all(i['confirmation']['status'] == 'unconfirmed' for i in self.store.payload()['incidents']))
        self.assertEqual(self.db.snapshot('weather'), dict(self.store.weather))
        from satellite import picture
        image = picture(self.store.incidents[0], 'natural', True, self.db)
        self.assertIn('/satellite/', image['url'])

    def test_demo_restart_ignores_persisted_calls_and_browser_sessions(self):
        from contextlib import nullcontext
        from unittest.mock import Mock
        from uuid import uuid4
        from test_demo import message
        with self.db.connect() as conn, conn.transaction(force_rollback=True):
            with patch.object(self.db, 'connect', side_effect=lambda: nullcontext(conn)), patch('demo.HappyRobotProvider', return_value=Mock()):
                original = Store(offline=True, database=self.db, demo_enabled=True)
                token = original.demo.open_browser()
                run = str(uuid4())
                original.demo.register(run, token)
                original.demo.accept(run, [message()])
                self.assertTrue(any(i.get('demo_report') for i in original.payload()['incidents']))
                fresh = Store(offline=True, database=self.db, demo_enabled=True)
                self.assertNotEqual(original.demo.session_id, fresh.demo.session_id)
                self.assertFalse(fresh.demo.authorized(token))
                self.assertEqual(fresh.payload()['demo']['calls'], [])
                self.assertFalse(any(i.get('demo_report') for i in fresh.payload()['incidents']))
                self.assertEqual(conn.execute('SELECT count(*) AS n FROM flare_demo_calls WHERE id=%s', (run,)).fetchone()['n'], 1)

    def test_only_verified_integrable_recent_media_is_visible(self):
        from contextlib import nullcontext
        from datetime import timedelta
        from uuid import uuid4
        from psycopg.types.json import Jsonb
        from territorial import UNAVAILABLE_IMAGES
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        ids = [str(uuid4()) for _ in range(5)]
        cases = [('available', 'image_decoded', now + timedelta(hours=1), ''),
                 ('available', 'public_embed_accessible', now + timedelta(hours=1), ''),
                 ('external', 'browser_embed_failed', now + timedelta(hours=1), ''),
                 ('available', 'image_decoded', now - timedelta(hours=1), ''),
                 ('available', 'image_decoded', now + timedelta(hours=1), next(iter(UNAVAILABLE_IMAGES)))]
        with self.db.connect() as conn, conn.transaction(force_rollback=True):
            for identifier, (status, method, valid, checksum) in zip(ids, cases):
                conn.execute('INSERT INTO flare_cameras VALUES (%s,%s,0,40,%s,%s,%s)',
                             (identifier, 'webcams', 'test', 'snapshot', Jsonb({'id': identifier})))
                conn.execute('INSERT INTO flare_camera_checks VALUES (%s,%s,%s,%s,%s,%s)',
                             (identifier, status, now, valid, 'snapshot', Jsonb({'method': method, 'sha256': checksum})))
            with patch.object(self.db, 'connect', side_effect=lambda: nullcontext(conn)):
                visible = {camera['id'] for camera in self.db.catalog(verified=True)['cameras']}
            self.assertIn(ids[0], visible)
            for identifier in ids[1:]:
                self.assertNotIn(identifier, visible)

    def test_parameterized_camera_lookup_and_foreign_keys(self):
        with self.assertRaises(KeyError):
            self.db.camera("x' OR '1'='1")
        camera = self.db.catalog()['cameras'][0]
        self.assertEqual(self.db.camera(camera['id']), camera)
        with self.db.connect() as conn:
            fks = conn.execute("SELECT count(*) AS n FROM pg_constraint WHERE contype='f' AND conrelid::regclass::text LIKE 'flare_%'").fetchone()['n']
            self.assertGreaterEqual(fks, 6)

    def test_confirmation_expiry_and_withdrawal(self):
        at = datetime(2026, 9, 19, tzinfo=timezone.utc)
        class Connection:
            def execute(self, sql, args):
                return [dict(incident_id='a', status='confirmed', confirmed_at=datetime(2026, 9, 18), valid_until=datetime(2026, 9, 20), source_name='Fuente', source_url='https://example.org'),
                        dict(incident_id='b', status='confirmed', confirmed_at=datetime(2026, 9, 18), valid_until=datetime(2026, 9, 18)),
                        dict(incident_id='c', status='withdrawn', confirmed_at=datetime(2026, 9, 18), valid_until=datetime(2026, 9, 20))]
        with patch.object(self.db, 'connect') as connect:
            connect.return_value.__enter__.return_value = Connection()
            self.assertEqual(list(self.db.confirmations(at)), ['a'])


if __name__ == '__main__':
    unittest.main()
