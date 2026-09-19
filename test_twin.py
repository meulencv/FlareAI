import unittest
from unittest.mock import Mock

from twin import TwinDatabase, bind_sql


class TwinTests(unittest.TestCase):
    def test_sql_values_are_quoted_not_interpolated(self):
        self.assertEqual(bind_sql('SELECT %s AS value', ("O'Brien",)), "SELECT 'O''Brien' AS value")
        self.assertIn("''; DROP TABLE", bind_sql('SELECT %s', ("'; DROP TABLE test; --",)))
        with self.assertRaises(ValueError):
            bind_sql('SELECT %s, %s', ('one',))

    def test_director_state_and_events_are_one_atomic_statement(self):
        client = Mock()
        client.request.return_value = {'rows': [], 'truncated': False}
        db = TwinDatabase(client=client)
        db.save_director('session', {'events': [{'sequence': 1, 'kind': 'decision'}], 'assignments': {}})
        self.assertEqual(client.request.call_count, 1)
        sql = client.request.call_args.args[2]['sql']
        self.assertIn('SELECT flare_live_save_director_v1', sql)
        from twin import SAVE_DIRECTOR_SQL
        self.assertIn('flare_live_events', SAVE_DIRECTOR_SQL)
        self.assertIn('ON CONFLICT', SAVE_DIRECTOR_SQL)

    def test_static_methods_still_use_local_database(self):
        self.assertNotIn('get_asset', TwinDatabase.__dict__)
        self.assertNotIn('nearby_atlas', TwinDatabase.__dict__)

    def test_pagination_never_accepts_truncated_rows(self):
        client = Mock()
        client.request.side_effect = [
            {'rows': [{'id': 'discard'}], 'truncated': True},
            {'rows': [{'id': 1}, {'id': 2}], 'truncated': False},
            {'rows': [{'id': 3}], 'truncated': False},
        ]
        db = TwinDatabase(client=client)
        self.assertEqual(db.rows('SELECT id FROM flare_grid ORDER BY id', page_size=4), [{'id': 1}, {'id': 2}, {'id': 3}])
        queries = [call.args[2]['sql'] for call in client.request.call_args_list]
        self.assertIn('LIMIT 2 OFFSET 0', queries[1])
        self.assertIn('LIMIT 2 OFFSET 2', queries[2])

    def test_single_oversized_row_fails_explicitly(self):
        client = Mock()
        client.request.return_value = {'rows': [], 'truncated': True}
        with self.assertRaisesRegex(RuntimeError, 'demasiado grande'):
            TwinDatabase(client=client).rows('SELECT data FROM flare_grid', page_size=1)

    def test_settings_keep_private_hook_out_of_export(self):
        from twin import public_setting
        self.assertEqual(public_setting({'name': 'workflow', 'hook_key': 'private', 'api_key': 'private'}), {'name': 'workflow'})

    def test_contacts_require_international_numbers_and_distinct_priority(self):
        from twin import validate_contacts
        contacts = [{'id': 'first', 'phone': '+34900000001', 'priority': 1, 'role': 'firefighter', 'enabled': True},
                    {'id': 'backup', 'phone': '+34900000002', 'priority': 2, 'role': 'firefighter', 'enabled': True}]
        self.assertEqual(validate_contacts(contacts), contacts)
        with self.assertRaises(ValueError):
            validate_contacts([{**contacts[0], 'phone': '112'}])
        with self.assertRaises(ValueError):
            validate_contacts([contacts[0], {**contacts[1], 'priority': 1}])


if __name__ == '__main__':
    unittest.main()
