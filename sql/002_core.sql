CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.person (
    person_key  TEXT PRIMARY KEY,
    first_name  TEXT,
    last_name   TEXT,
    email       TEXT,
    phone       TEXT,
    birth_date  DATE,
    state       TEXT,
    updated_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.source_link (
    source      TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    person_key  TEXT NOT NULL REFERENCES core.person (person_key),
    PRIMARY KEY (source, source_id)
);
