from __future__ import annotations

import json

from genus_egg.kernel.artifacts import ReactionProduct
from genus_egg.kernel.reaction_graph import ReactionEdge, ReactionGraph
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet


def _reaction(name: str) -> ReactionSpec:
    return ReactionSpec(name, "reaction_product", "memory_object", lambda _: object())


def _working_set(product_type: str = "memory_proposal", continuation: str = "required"):
    working_set = WorkingSet("chain_1")
    working_set.add(
        "reaction_product",
        ReactionProduct(
            product_id="product_1",
            chain_id="chain_1",
            produced_by_reaction_id="reaction_1",
            product_type=product_type,
            continuation_policy=continuation,
            payload_json=json.dumps({"content": "larumipsum"}, sort_keys=True),
            created_at="2026-05-23T00:00:00Z",
        ),
    )
    return working_set


def test_allowed_edge_runs_through():
    graph = ReactionGraph()

    assert graph.allows_if_continuation(_reaction("create_memory"), _working_set())


def test_missing_edge_blocks():
    graph = ReactionGraph()
    graph._edges.remove(
        ReactionEdge(
            "reaction_product",
            "create_memory",
            required_product_type="memory_proposal",
            continuation_required=True,
            terminal_behavior="complete_chain",
        )
    )

    assert not graph.allows_if_continuation(_reaction("create_memory"), _working_set())


def test_wrong_product_type_edge_blocks():
    graph = ReactionGraph()

    assert not graph.allows_if_continuation(
        _reaction("create_memory"), _working_set(product_type="unknown")
    )


def test_wrong_continuation_edge_blocks():
    graph = ReactionGraph()

    assert not graph.allows_if_continuation(
        _reaction("create_memory"), _working_set(continuation="optional")
    )
