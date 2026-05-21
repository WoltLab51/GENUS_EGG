from __future__ import annotations

import json

from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def test_maturation_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "reaction_outcomes",
        "observation_records",
        "capability_needs",
    }.issubset(store.table_names())
    store.close()


def test_successful_reaction_chain_creates_outcome_and_observation(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    result = ReactionKernel(store, ledger).remember("larumipsum")

    outcomes = store.list_reaction_outcomes()
    observations = store.list_observation_records()
    assert result.reason_code == "memory_created"
    assert result.ledger_entries == 7
    assert len(outcomes) == 1
    assert outcomes[0].chain_id == result.chain_id
    assert outcomes[0].final_status == "completed"
    assert outcomes[0].final_product_type == "memory_object"
    assert outcomes[0].success is True
    assert outcomes[0].reason_code == "memory_created"
    assert len(observations) == 1
    assert observations[0].chain_id == result.chain_id
    assert observations[0].observation_type == "reaction_chain_completed"
    assert json.loads(observations[0].payload_json)["ledger_entries"] == 7
    store.close()


def test_capability_need_can_be_created_as_draft_without_activation(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    need = MaturationSeed(store).draft_memory_indexing_need()
    needs = store.list_capability_needs()

    assert len(needs) == 1
    assert needs[0] == need
    assert need.need_type == "capability_improvement"
    assert need.description == "Memory retrieval could improve through indexing."
    assert need.status == "draft"
    assert "activation" not in json.loads(need.payload_json or "{}")
    store.close()
