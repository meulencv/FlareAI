from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import threading
import time
import uuid
from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Iterator

from psycopg import sql
from psycopg.types.json import Jsonb

from database import Database, ROOT

SCHEMA = '''
CREATE TABLE IF NOT EXISTS flare_live_sessions (id text PRIMARY KEY, started_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'));
CREATE TABLE IF NOT EXISTS flare_live_calls (id text PRIMARY KEY, session_id text NOT NULL REFERENCES flare_live_sessions(id), updated_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'), data jsonb NOT NULL);
CREATE INDEX IF NOT EXISTS flare_live_calls_session ON flare_live_calls(session_id, id);
ALTER TABLE flare_live_calls ADD COLUMN IF NOT EXISTS owner_hash text;
ALTER TABLE flare_live_calls ADD COLUMN IF NOT EXISTS ended_at timestamp;
CREATE TABLE IF NOT EXISTS flare_live_web_requests (id text PRIMARY KEY, session_id text NOT NULL REFERENCES flare_live_sessions(id), owner_hash text NOT NULL, status text NOT NULL, expires_at timestamp NOT NULL, run_id text, data jsonb NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS flare_live_state (session_id text PRIMARY KEY REFERENCES flare_live_sessions(id), updated_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'), data jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS flare_live_events (session_id text NOT NULL REFERENCES flare_live_sessions(id), sequence int8 NOT NULL, data jsonb NOT NULL, PRIMARY KEY(session_id, sequence));
CREATE TABLE IF NOT EXISTS flare_live_settings (id text PRIMARY KEY, data jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS flare_contacts (id text PRIMARY KEY, phone text NOT NULL CHECK (phone ~ '^\\+[1-9][0-9]{7,14}$'), role text NOT NULL, priority int8 NOT NULL, enabled boolean NOT NULL DEFAULT true, UNIQUE(role, priority));
CREATE TABLE IF NOT EXISTS flare_live_documents (id text PRIMARY KEY, kind text NOT NULL, session_id text, updated_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'), data jsonb NOT NULL);
CREATE INDEX IF NOT EXISTS flare_live_documents_kind ON flare_live_documents(kind, session_id, id);
CREATE TABLE IF NOT EXISTS flare_live_leases (id text PRIMARY KEY, owner text NOT NULL, expires_at timestamp NOT NULL);
'''


SAVE_DIRECTOR_SQL = '''CREATE FUNCTION flare_live_save_director_v1(s text, v jsonb, events jsonb)
RETURNS boolean LANGUAGE plpgsql AS $body$
BEGIN
    INSERT INTO flare_live_state(session_id,data) VALUES(s,v)
    ON CONFLICT(session_id) DO UPDATE SET data=EXCLUDED.data,updated_at=(now() AT TIME ZONE 'UTC');
    INSERT INTO flare_live_events SELECT s,(e->>'sequence')::bigint,e FROM jsonb_array_elements(events) AS e
    ON CONFLICT DO NOTHING;
    RETURN true;
END;
$body$'''


RESERVE_WEB_SQL = '''CREATE FUNCTION flare_live_reserve_web_v1(s text, o text, r text)
RETURNS jsonb LANGUAGE plpgsql AS $body$
DECLARE previous flare_live_web_requests;
BEGIN
    PERFORM pg_advisory_xact_lock(804035);
    SELECT * INTO previous FROM flare_live_web_requests WHERE id=r;
    IF FOUND THEN
        IF previous.owner_hash<>o OR previous.session_id<>s THEN RAISE EXCEPTION 'REQUEST_OWNER'; END IF;
        IF previous.expires_at<(now() AT TIME ZONE 'UTC') THEN RAISE EXCEPTION 'REQUEST_EXPIRED'; END IF;
        RETURN jsonb_build_object('created',false,'status',previous.status,'data',previous.data);
    END IF;
    IF EXISTS (SELECT 1 FROM flare_live_web_requests w LEFT JOIN flare_live_calls c ON c.id=w.run_id
        WHERE w.session_id=s AND w.owner_hash=o AND w.status IN ('pending','ready','uncertain') AND c.ended_at IS NULL
        AND w.expires_at>(now() AT TIME ZONE 'UTC')) THEN RAISE EXCEPTION 'CALL_ACTIVE'; END IF;
    IF (SELECT count(*) FROM flare_live_web_requests w LEFT JOIN flare_live_calls c ON c.id=w.run_id
        WHERE w.session_id=s AND w.status IN ('pending','ready','uncertain') AND c.ended_at IS NULL
        AND w.expires_at>(now() AT TIME ZONE 'UTC'))>=16 THEN RAISE EXCEPTION 'CALL_CAPACITY'; END IF;
    INSERT INTO flare_live_web_requests(id,session_id,owner_hash,status,expires_at)
        VALUES(r,s,o,'pending',(now() AT TIME ZONE 'UTC')+interval '20 minutes');
    RETURN jsonb_build_object('created',true,'status','pending');
END;
$body$'''


def bind_sql(statement: str, values: tuple = ()) -> str:
    parts = statement.split('%s')
    if len(parts) != len(values) + 1:
        raise ValueError('Número de parámetros SQL incorrecto')
    output = parts[0]
    for value, part in zip(values, parts[1:]):
        if isinstance(value, (dict, list)):
            value = Jsonb(value)
        output += sql.Literal(value).as_string() + part
    return output


def public_setting(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: public_setting(v) for k, v in value.items() if k not in {'hook_key', 'api_key', 'token', 'owner', 'phone'}}
    if isinstance(value, list):
        return [public_setting(v) for v in value]
    return value


def validate_contacts(contacts: list[dict]) -> list[dict]:
    ids, positions = set(), set()
    for contact in contacts:
        position = (contact.get('role'), contact.get('priority'))
        if (not re.fullmatch(r'[a-z0-9_-]{1,64}', contact.get('id', ''))
                or not re.fullmatch(r'\+[1-9][0-9]{7,14}', contact.get('phone', ''))
                or contact.get('role') not in {'firefighter', 'caller'}
                or type(contact.get('priority')) is not int or contact['priority'] < 0
                or type(contact.get('enabled')) is not bool
                or contact['id'] in ids or position in positions):
            raise ValueError('Contacto, teléfono internacional o prioridad no válidos')
        ids.add(contact['id'])
        positions.add(position)
    return contacts


class TwinDatabase(Database):
    dynamic_cloud = True

    def __init__(self, url: str | None = None, client=None) -> None:
        super().__init__(url)
        if client is None:
            from demo import HappyRobotProvider
            provider = HappyRobotProvider()
            provider.module.load_env(ROOT / '.env.presentation')
            client = provider.client
            client.key = os.environ.get('FLAREAI_TWIN_API_KEY') or client.key
        self.client = client
        self._cache: dict[str, tuple[float, Any]] = {}
        self._cache_lock = threading.RLock()
        self._lease_failed = threading.Event()
        self._last_event: dict[str, int] = {}

    def execute(self, statement: str, values: tuple = ()) -> dict:
        if self._lease_failed.is_set():
            raise RuntimeError('Se perdió el control exclusivo de la sala; reinicia antes de actuar')
        try:
            result = self.client.request('POST', '/twin/sql', {'sql': bind_sql(statement, values) if values else statement})
        except Exception as error:
            status = getattr(error, 'status', None)
            if status in {401, 403}:
                raise PermissionError('Twin requiere una credencial con acceso SQL') from None
            raise RuntimeError(f'Twin no disponible (HTTP {status or "sin respuesta"}); no se han confirmado cambios') from None
        if not isinstance(result, dict) or not isinstance(result.get('rows'), list):
            raise RuntimeError('Respuesta SQL de Twin no válida')
        for field in result.get('fields', []):
            if field.get('dataTypeId') in {20, 21, 23}:
                for row in result['rows']:
                    if row.get(field['name']) is not None:
                        row[field['name']] = int(row[field['name']])
        return result

    def rows(self, statement: str, values: tuple = (), page_size: int = 200) -> list[dict]:
        page_size = max(1, min(500, page_size))
        query, rows, offset = bind_sql(statement, values), [], 0
        while True:
            page = self.execute(f'SELECT * FROM ({query}) AS paged LIMIT {page_size} OFFSET {offset}')
            if page.get('truncated'):
                if page_size == 1:
                    raise RuntimeError('Documento dinámico demasiado grande para Twin; no se acepta una respuesta parcial')
                page_size = max(1, page_size // 2)
                continue
            batch = page['rows']
            rows.extend(batch)
            if len(batch) < page_size:
                return rows
            offset += len(batch)

    def cached(self, key: str, ttl: float, load):
        with self._cache_lock:
            found = self._cache.get(key)
            if found and found[0] > time.monotonic():
                return deepcopy(found[1])
        value = load()
        with self._cache_lock:
            self._cache[key] = (time.monotonic() + ttl, deepcopy(value))
        return value

    def invalidate(self, *keys: str) -> None:
        with self._cache_lock:
            for key in keys:
                self._cache.pop(key, None)

    def setting(self, identifier: str, value: dict | None = None) -> dict:
        if value is not None:
            self.execute('INSERT INTO flare_live_settings VALUES (%s,%s) ON CONFLICT(id) DO UPDATE SET data=EXCLUDED.data', (identifier, value))
            with self._cache_lock:
                self._cache.pop('setting:' + identifier, None)
            return value
        def load():
            rows = self.rows('SELECT data FROM flare_live_settings WHERE id=%s', (identifier,))
            return rows[0]['data'] if rows else {}
        return self.cached('setting:' + identifier, 10, load)

    def director_setting(self, value: dict | None = None) -> dict:
        current = self.setting('presentation-director')
        if current.get('published'):
            return self.setting('presentation-director', value)
        return self.setting('director-workflow', value)

    def responder_setting(self, value: dict | None = None) -> dict:
        return self.setting('outbound-workflow', value)

    def migrate_live(self) -> None:
        for statement in SCHEMA.split(';'):
            if statement.strip():
                self.execute(statement)
        exists = self.rows("SELECT to_regprocedure('flare_live_save_director_v1(text,jsonb,jsonb)')::text AS name")
        if not exists[0]['name']:
            self.execute(SAVE_DIRECTOR_SQL)
        exists = self.rows("SELECT to_regprocedure('flare_live_reserve_web_v1(text,text,text)')::text AS name")
        if not exists[0]['name']:
            self.execute(RESERVE_WEB_SQL)
        if not self.director_setting():
            existing = Database.director_setting(self)
            if existing:
                self.director_setting(existing)

    def bootstrap(self) -> None:
        super().bootstrap()
        self.migrate_live()

    def start_demo(self, identifier: str) -> None:
        self.execute('INSERT INTO flare_live_sessions(id) VALUES (%s) ON CONFLICT DO NOTHING', (identifier,))

    def save_demo_call(self, session_id: str, run_id: str, data: dict) -> None:
        self.execute("INSERT INTO flare_live_calls(id,session_id,data) VALUES (%s,%s,%s) ON CONFLICT(id) DO UPDATE SET data=EXCLUDED.data,updated_at=(now() AT TIME ZONE 'UTC') WHERE flare_live_calls.session_id=EXCLUDED.session_id", (run_id, session_id, data))

    def demo_calls(self, session_id: str) -> list[dict]:
        return self.rows('SELECT id,data,ended_at FROM flare_live_calls WHERE session_id=%s AND owner_hash IS NOT NULL ORDER BY id', (session_id,))

    def director_history(self, session_id: str) -> dict:
        rows = self.rows('SELECT data FROM flare_live_events WHERE session_id=%s ORDER BY sequence', (session_id,))
        return {'session_id': session_id, 'events': [r['data'] for r in rows]}

    def save_director(self, session_id: str, state: dict) -> None:
        last = self._last_event.get(session_id, 0)
        events = [event for event in state['events'] if event['sequence'] > last]
        compact = {k: v for k, v in state.items() if k != 'events'}
        if len(json.dumps(compact, ensure_ascii=False).encode()) > 750000:
            raise RuntimeError('Estado de sala demasiado grande; no se guardará parcialmente')
        self.execute('SELECT flare_live_save_director_v1(%s,%s,%s)', (session_id, compact, events))
        if events:
            self._last_event[session_id] = max(e['sequence'] for e in events)

    def document(self, identifier: str, kind: str = '', value: dict | None = None, session_id: str | None = None) -> dict | None:
        if value is not None:
            self.execute("INSERT INTO flare_live_documents(id,kind,session_id,data) VALUES (%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET data=EXCLUDED.data,updated_at=(now() AT TIME ZONE 'UTC') WHERE flare_live_documents.kind=EXCLUDED.kind AND flare_live_documents.session_id IS NOT DISTINCT FROM EXCLUDED.session_id", (identifier, kind, session_id, value))
            return value
        rows = self.rows('SELECT data FROM flare_live_documents WHERE id=%s', (identifier,))
        return rows[0]['data'] if rows else None

    def documents(self, kind: str, session_id: str | None = None) -> list[dict]:
        query = 'SELECT id,data FROM flare_live_documents WHERE kind=%s'
        values: tuple = (kind,)
        if session_id is not None:
            query += ' AND session_id=%s'
            values += (session_id,)
        return self.rows(query + ' ORDER BY id', values)

    def contacts(self, value: list[dict] | None = None, role: str = 'firefighter') -> list[dict]:
        if value is not None:
            validate_contacts(value)
            self.execute('INSERT INTO flare_contacts SELECT * FROM jsonb_populate_recordset(NULL::flare_contacts,%s) ON CONFLICT(id) DO UPDATE SET phone=EXCLUDED.phone,role=EXCLUDED.role,priority=EXCLUDED.priority,enabled=EXCLUDED.enabled', (value,))
        return self.rows('SELECT id,phone,role,priority,enabled FROM flare_contacts WHERE role=%s AND enabled ORDER BY priority,id', (role,))

    @contextmanager
    def verification_lock(self, key: int) -> Iterator[bool]:
        if key != 804030:
            with super().verification_lock(key) as acquired:
                yield acquired
            return
        owner = str(uuid.uuid4())
        query = "INSERT INTO flare_live_leases VALUES (%s,%s,(now() AT TIME ZONE 'UTC')+interval '90 seconds') ON CONFLICT(id) DO UPDATE SET owner=EXCLUDED.owner,expires_at=EXCLUDED.expires_at WHERE flare_live_leases.expires_at<(now() AT TIME ZONE 'UTC') OR flare_live_leases.owner=EXCLUDED.owner RETURNING owner"
        acquired = bool(self.execute(query, (str(key), owner))['rows'])
        stop = threading.Event()
        def renew():
            while not stop.wait(15):
                try:
                    if not self.execute(query, (str(key), owner))['rows']:
                        self._lease_failed.set()
                        return
                except Exception:
                    self._lease_failed.set()
                    return
        worker = threading.Thread(target=renew, daemon=True)
        if acquired:
            worker.start()
        try:
            yield acquired
        finally:
            stop.set()
            if acquired:
                worker.join(timeout=25)
            if acquired and not self._lease_failed.is_set():
                self.execute("UPDATE flare_live_leases SET expires_at=(now() AT TIME ZONE 'UTC') WHERE id=%s AND owner=%s", (str(key), owner))

    def heartbeat(self, session_id: str) -> None:
        self.document('active-room', 'room', {'session_id': session_id, 'heartbeat_at': time.time(), 'mode': 'simulation_only'})

    def stop_room(self, session_id: str) -> None:
        self.execute("UPDATE flare_live_documents SET data=jsonb_set(data,'{heartbeat_at}','0'::jsonb) WHERE id='active-room' AND data->>'session_id'=%s", (session_id,))

    def reset_demo(self) -> None:
        """Además del vaciado local heredado, vacía las llamadas/estado/documentos dinámicos de Twin.
        Nunca toca `flare_contacts` (teléfonos de bomberos) ni `flare_live_settings`/`flare_live_leases`."""
        super().reset_demo()
        for table in ('flare_live_calls', 'flare_live_web_requests', 'flare_live_events',
                      'flare_live_state', 'flare_live_documents', 'flare_live_sessions'):
            self.execute(f'DELETE FROM {table}')

    def fingerprint(self) -> dict:
        rows = self.rows("SELECT tablename FROM pg_tables WHERE schemaname='public' AND (tablename LIKE 'flare_live_%%' OR tablename='flare_contacts') ORDER BY tablename")
        return {'backend': 'happyrobot_twin', 'tables': [r['tablename'] for r in rows], 'static_backend': 'local',
                'schema_sha256': hashlib.sha256(SCHEMA.encode()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'status', 'contacts'])
    options = parser.parse_args()
    database = TwinDatabase()
    if options.command == 'prepare':
        database.migrate_live()
    elif options.command == 'contacts':
        raw = os.environ.get('FLAREAI_CONTACTS_JSON', '')
        if not raw:
            raise SystemExit('Configura FLAREAI_CONTACTS_JSON en el entorno privado, nunca en el código')
        database.contacts(json.loads(raw))
    print(json.dumps(database.fingerprint(), ensure_ascii=False))
