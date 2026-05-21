from __future__ import annotations

import json

from genus_egg.kernel.artifacts import ReactionProduct
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
