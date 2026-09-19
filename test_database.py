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
