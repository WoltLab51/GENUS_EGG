from __future__ import annotations

from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.meaning_candidate import MeaningCandidate
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def _validation_for(tmp_path, meaning: MeaningCandidate):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)
    working_set = WorkingSet(meaning.chain_id)
    working_set.add("meaning_candidate", meaning)
    validation = ReactionKernel(store, ledger)._validate_meaning(working_set)
    store.close()
    return validation


def _meaning(
    intent: str = "memory_request",
    content: str = "larumipsum",
    confidence: str = "high",
    needs_clarification: bool = False,
) -> MeaningCandidate:
    return MeaningCandidate(
        meaning_id="meaning_1",
        chain_id="chain_1",
        source_input_id="input_1",
        intent=intent,
        content=content,
        interpretation_confidence=confidence,
        needs_clarification=needs_clarification,
        adapter_version="test",
        created_at="2026-05-23T00:00:00Z",
    )


def test_validation_allows_known_memory_request(tmp_path):
    validation = _validation_for(tmp_path, _meaning())

    assert validation.result == "allow"
    assert validation.reason_code == "ready"


def test_validation_rejects_unknown_intent(tmp_path):
    validation = _validation_for(tmp_path, _meaning(intent="free_language"))

    assert validation.result == "reject"
    assert validation.reason_code == "unknown_intent"


def test_validation_rejects_empty_memory_content(tmp_path):
    validation = _validation_for(tmp_path, _meaning(content=" "))

    assert validation.result == "reject"
    assert validation.reason_code == "missing_content"


def test_validation_rejects_low_confidence(tmp_path):
    validation = _validation_for(tmp_path, _meaning(confidence="low"))

    assert validation.result == "reject"
    assert validation.reason_code == "low_confidence"


def test_validation_rejects_needs_clarification_without_follow_up(tmp_path):
    validation = _validation_for(tmp_path, _meaning(needs_clarification=True))

    assert validation.result == "reject"
    assert validation.reason_code == "needs_clarification"
