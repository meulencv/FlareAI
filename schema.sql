CREATE TABLE IF NOT EXISTS flare_migrations (version int8 PRIMARY KEY, applied_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'));
CREATE TABLE IF NOT EXISTS flare_sources (id text PRIMARY KEY, data jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS flare_imports (id text PRIMARY KEY, source_id text NOT NULL REFERENCES flare_sources(id), rows int8 NOT NULL, imported_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'));
CREATE TABLE IF NOT EXISTS flare_grid (
    id text PRIMARY KEY, source_id text NOT NULL REFERENCES flare_sources(id),
    lon float8 NOT NULL, lat float8 NOT NULL, population float8, data jsonb NOT NULL,
    CHECK (lon BETWEEN -180 AND 180 AND lat BETWEEN -90 AND 90)
);
CREATE INDEX IF NOT EXISTS flare_grid_location ON flare_grid (lon, lat);
CREATE TABLE IF NOT EXISTS flare_facilities (
    id text PRIMARY KEY, source_id text NOT NULL REFERENCES flare_sources(id),
    lon float8 NOT NULL, lat float8 NOT NULL, category text NOT NULL, name text NOT NULL, data jsonb NOT NULL,
    CHECK (lon BETWEEN -180 AND 180 AND lat BETWEEN -90 AND 90)
);
CREATE INDEX IF NOT EXISTS flare_facilities_location ON flare_facilities (lon, lat);
CREATE INDEX IF NOT EXISTS flare_facilities_category ON flare_facilities (category);
CREATE TABLE IF NOT EXISTS flare_cameras (
    id text PRIMARY KEY, source_id text NOT NULL REFERENCES flare_sources(id),
    lon float8 NOT NULL, lat float8 NOT NULL, name text NOT NULL, kind text NOT NULL, data jsonb NOT NULL,
    CHECK (lon BETWEEN -180 AND 180 AND lat BETWEEN -90 AND 90)
);
CREATE INDEX IF NOT EXISTS flare_cameras_location ON flare_cameras (lon, lat);
CREATE TABLE IF NOT EXISTS flare_snapshots (
    id text PRIMARY KEY, kind text NOT NULL, valid_at timestamp NOT NULL, data jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS flare_snapshots_latest ON flare_snapshots (kind, valid_at DESC);
CREATE TABLE IF NOT EXISTS flare_incidents (
    id text PRIMARY KEY, lat float8 NOT NULL, lon float8 NOT NULL,
    last_seen timestamp NOT NULL, data jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS flare_incidents_time ON flare_incidents (last_seen DESC);
CREATE TABLE IF NOT EXISTS flare_observations (
    id text PRIMARY KEY, incident_id text REFERENCES flare_incidents(id),
    lat float8 NOT NULL, lon float8 NOT NULL, observed_at timestamp NOT NULL, data jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS flare_observations_incident ON flare_observations (incident_id, observed_at);
CREATE TABLE IF NOT EXISTS flare_confirmations (
    id text PRIMARY KEY, incident_id text NOT NULL REFERENCES flare_incidents(id),
    source_name text NOT NULL, source_url text NOT NULL,
    confirmed_at timestamp NOT NULL, valid_until timestamp NOT NULL,
    status text NOT NULL CHECK (status IN ('confirmed', 'withdrawn')),
    CHECK (valid_until > confirmed_at)
);
CREATE INDEX IF NOT EXISTS flare_confirmations_incident ON flare_confirmations (incident_id, valid_until);
CREATE TABLE IF NOT EXISTS flare_assets (
    id text PRIMARY KEY, kind text NOT NULL, source_id text REFERENCES flare_sources(id),
    path text, data jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS flare_settings (id text PRIMARY KEY, data jsonb NOT NULL);
INSERT INTO flare_migrations(version) VALUES (1) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS flare_camera_checks (
    id text PRIMARY KEY REFERENCES flare_cameras(id),
    status text NOT NULL CHECK (status IN ('available', 'unavailable', 'external')),
    checked_at timestamp NOT NULL, valid_until timestamp NOT NULL,
    media_kind text, data jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS flare_camera_checks_due ON flare_camera_checks (valid_until);
INSERT INTO flare_migrations(version) VALUES (2) ON CONFLICT DO NOTHING;
