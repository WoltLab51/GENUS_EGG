from __future__ import annotations

import inspect
import sqlite3

from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def test_ledger_records_monotonic_steps(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    first = ledger.record("chain_1", "first", "test", "source")
    second = ledger.record("chain_1", "second", "test", "source")

    assert first.step == 1
    assert second.step == 2
    assert [entry.event_type for entry in ledger.list_by_chain("chain_1")] == [
        "first",
        "second",
    ]
    store.close()


def test_ledger_has_no_public_mutation_api(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    assert not hasattr(ledger, "update")
    assert not hasattr(ledger, "delete")
    source = inspect.getsource(Ledger).upper()
    assert "UPDATE LEDGER_ENTRIES" not in source
    assert "DELETE FROM LEDGER_ENTRIES" not in source
    store.close()


def test_ledger_rejects_duplicate_chain_step(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)
    first = ledger.record("chain_1", "first", "test", "source")

    try:
        store.connection.execute(
            """
            INSERT INTO ledger_entries
            (ledger_id, chain_id, step, event_type, source_kind, source_id,
             target_kind, target_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "ledger_duplicate",
                first.chain_id,
                first.step,
                "duplicate",
                "test",
                "source",
                None,
                None,
                None,
                "2026-05-23T00:00:00Z",
            ),
        )
    except sqlite3.IntegrityError as error:
        assert "UNIQUE" in str(error)
    else:
        raise AssertionError("duplicate ledger step was not blocked")
    finally:
        store.close()
