from __future__ import annotations

import json
import pytest

from genus_egg.kernel.artifacts import ReactionProduct, ValidationResult
from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.truth.sqlite_store import SQLiteStore


def test_sqlite_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "raw_inputs",
        "meaning_candidates",
        "validation_results",
        "reactions",
        "reaction_products",
        "memory_objects",
        "ledger_entries",
    }.issubset(store.table_names())

    store.close()


def test_payload_json_roundtrip(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    product = ReactionProduct(
        product_id="product_1",
        chain_id="chain_1",
        produced_by_reaction_id="reaction_1",
        product_type="memory_proposal",
        continuation_policy="required",
        payload_json=json.dumps({"content": "larumipsum"}, sort_keys=True),
        created_at="2026-05-21T00:00:00Z",
    )

    store.save_reaction_product(product)
    row = store.fetch_one("reaction_products")

    assert json.loads(row["payload_json"]) == {"content": "larumipsum"}
    store.close()


def test_invalid_validation_result_is_blocked(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    validation = ValidationResult(
        validation_id="validation_1",
        chain_id="chain_1",
        source_meaning_id="meaning_1",
        result="clarify",
        reason_code="needs_clarification",
        created_at="2026-05-23T00:00:00Z",
    )

    with pytest.raises(ValueError, match="validation.result"):
        store.save_validation_result(validation)

    store.close()


def test_invalid_capability_need_status_is_blocked(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    need = CapabilityNeed(
        need_id="need_1",
        source_observation_id=None,
        need_type="memory_indexing",
        description="Need",
        status="active",
        payload_json=None,
        created_at="2026-05-23T00:00:00Z",
    )

    with pytest.raises(ValueError, match="capability_need.status"):
        store.save_capability_need(need)

    store.close()
