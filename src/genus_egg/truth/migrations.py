from __future__ import annotations

import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_inputs (
    input_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meaning_candidates (
    meaning_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_input_id TEXT NOT NULL,
    intent TEXT NOT NULL,
    content TEXT,
    interpretation_confidence TEXT NOT NULL,
    needs_clarification INTEGER NOT NULL,
    adapter_version TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_results (
    validation_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_meaning_id TEXT NOT NULL,
    result TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reactions (
    reaction_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_validation_id TEXT,
    reaction_type TEXT NOT NULL,
    context TEXT NOT NULL,
    reaction_state TEXT NOT NULL,
    resolver_mode TEXT NOT NULL,
    cube_coord INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reaction_products (
    product_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    produced_by_reaction_id TEXT NOT NULL,
    product_type TEXT NOT NULL,
    continuation_policy TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_objects (
    memory_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    memory_state TEXT NOT NULL,
    source_product_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    ledger_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    step INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_kind TEXT,
    target_id TEXT,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habitat_manifest (
    habitat_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    hostname TEXT NOT NULL,
    os_name TEXT NOT NULL,
    python_version TEXT NOT NULL,
    repo_path TEXT,
    data_path TEXT NOT NULL,
    sqlite_path TEXT NOT NULL,
    network_allowed INTEGER NOT NULL,
    git_available INTEGER NOT NULL,
    github_allowed INTEGER NOT NULL,
    model_access TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
"""


def apply_migrations(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()
