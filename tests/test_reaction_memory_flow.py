from __future__ import annotations

from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def test_remember_creates_memory_and_full_ledger_chain(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    result = ReactionKernel(store, ledger).remember("larumipsum")

    assert result.outcome == "completed"
    assert result.reason_code == "memory_created"
    assert result.memory_content == "larumipsum"
    assert store.count_rows("raw_inputs") == 1
    assert store.count_rows("meaning_candidates") == 1
    assert store.count_rows("validation_results") == 1
    assert store.count_rows("reaction_products") == 1
    assert store.count_rows("memory_objects") == 1

    entries = ledger.list_by_chain(result.chain_id)
    assert [entry.event_type for entry in entries] == [
        "raw_input_created",
        "meaning_candidate_created",
        "validation_result_created",
        "reaction_created",
        "reaction_product_created",
        "memory_object_created",
        "chain_completed",
    ]
    store.close()


def test_memory_retrieval_works(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)
    ReactionKernel(store, ledger).remember("larumipsum")

    memories = store.list_memory_objects()

    assert len(memories) == 1
    assert memories[0].content == "larumipsum"
    store.close()
