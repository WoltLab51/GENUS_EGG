from __future__ import annotations

import json

from genus_egg.kernel.artifacts import ReactionProduct, ValidationResult
from genus_egg.kernel.guards import Guards
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.meaning_candidate import MeaningCandidate


def _reaction(name: str, effects: tuple[str, ...] = ()) -> ReactionSpec:
    return ReactionSpec(name, "meaning_candidate", "validation_result", lambda _: object(), effects)


def _meaning(
    content: str = "larumipsum",
    confidence: str = "high",
) -> MeaningCandidate:
    return MeaningCandidate(
        meaning_id="meaning_1",
        chain_id="chain_1",
        source_input_id="input_1",
        intent="memory_request",
        content=content,
        interpretation_confidence=confidence,
        needs_clarification=False,
        adapter_version="test",
        created_at="2026-05-23T00:00:00Z",
    )


def test_guard_allows_normal_memory_proposal():
    working_set = WorkingSet("chain_1")
    working_set.add("meaning_candidate", _meaning())
    working_set.add(
        "validation_result",
        ValidationResult(
            "validation_1",
            "chain_1",
            "meaning_1",
            "allow",
            "ready",
            "2026-05-23T00:00:00Z",
        ),
    )

    decision = Guards().decide(_reaction("create_memory_proposal"), working_set)

    assert decision.allow is True
    assert decision.reason_code == "allowed"


def test_missing_content_guard_blocks():
    working_set = WorkingSet("chain_1")
    working_set.add("meaning_candidate", _meaning(content=" "))

    decision = Guards().decide(_reaction("create_memory_proposal"), working_set)

    assert decision.allow is False
    assert decision.reason_code == "missing_content"


def test_low_confidence_guard_blocks():
    working_set = WorkingSet("chain_1")
    working_set.add("meaning_candidate", _meaning(confidence="low"))

    decision = Guards().decide(_reaction("create_memory_proposal"), working_set)

    assert decision.allow is False
    assert decision.reason_code == "low_confidence"


def test_validation_not_allow_guard_blocks():
    working_set = WorkingSet("chain_1")
    working_set.add("meaning_candidate", _meaning())
    working_set.add(
        "validation_result",
        ValidationResult(
            "validation_1",
            "chain_1",
            "meaning_1",
            "reject",
            "missing_content",
            "2026-05-23T00:00:00Z",
        ),
    )

    decision = Guards().decide(_reaction("create_memory_proposal"), working_set)

    assert decision.allow is False
    assert decision.reason_code == "validation_not_allow"


def test_wrong_continuation_policy_guard_blocks():
    working_set = WorkingSet("chain_1")
    working_set.add(
        "reaction_product",
        ReactionProduct(
            product_id="product_1",
            chain_id="chain_1",
            produced_by_reaction_id="reaction_1",
            product_type="memory_proposal",
            continuation_policy="optional",
            payload_json=json.dumps({"content": "larumipsum"}, sort_keys=True),
            created_at="2026-05-23T00:00:00Z",
        ),
    )

    decision = Guards().decide(_reaction("create_memory"), working_set)

    assert decision.allow is False
    assert decision.reason_code == "wrong_continuation_policy"


def test_unknown_reaction_guard_blocks():
    decision = Guards().decide(_reaction("unknown_reaction"), WorkingSet("chain_1"))

    assert decision.allow is False
    assert decision.reason_code == "unknown_reaction"


def test_forbidden_effect_guard_blocks():
    decision = Guards().decide(
        _reaction("parse_user_input", effects=("github",)), WorkingSet("chain_1")
    )

    assert decision.allow is False
    assert decision.reason_code == "forbidden_effect"
