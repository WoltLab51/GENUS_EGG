from __future__ import annotations

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
    store.close()
