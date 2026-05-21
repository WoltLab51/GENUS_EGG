from __future__ import annotations

import json

import pytest

from genus_egg.activation.activation_boundary import (
    ActivationApprovalError,
    ActivationBoundary,
)
from genus_egg.activation.activation_request import ActivationRequest
from genus_egg.activation.reaction_spec_candidate import ReactionSpecCandidate
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.lifecycle.lifecycle_boundary import LifecycleBoundary
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.memory.memory_search import MemorySearch
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def _ready_activation_request(store: SQLiteStore) -> str:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    TestRunner(store).run_for_patch(patch.patch_id)
    FitnessEvaluator(store).evaluate(code_proposal.code_proposal_id)
    LifecycleBoundary(store).create_rollback_plan(code_proposal.code_proposal_id)
    request, _, _ = ActivationBoundary(store).request(code_proposal.code_proposal_id)
    return request.activation_request_id


def test_memory_index_table_exists(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert "memory_index_entries" in store.table_names()
    store.close()


def test_remember_does_not_index_before_activation(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    result = ReactionKernel(store, Ledger(store)).remember("larumipsum")

    assert result.ledger_entries == 7
    assert store.list_memory_index_entries() == []
    store.close()


def test_activation_approval_backfills_existing_memories(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ReactionKernel(store, Ledger(store)).remember("Blue Memory Seed")
    request_id = _ready_activation_request(store)

    decision, activation, indexed_count = ActivationBoundary(store).approve(request_id)

    assert decision.decision == "approved"
    assert decision.activation == "active"
    assert activation.status == "active"
    assert activation.activation == "active"
    assert indexed_count == 1
    entries = store.list_memory_index_entries()
    assert len(entries) == 1
    assert json.loads(entries[0].tokens_json) == ["blue", "memory", "seed"]
    store.close()


def test_new_memories_are_indexed_after_activation_without_ledger_change(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ReactionKernel(store, Ledger(store)).remember("first memory")
    request_id = _ready_activation_request(store)
    ActivationBoundary(store).approve(request_id)

    result = ReactionKernel(store, Ledger(store)).remember("second memory")

    assert result.ledger_entries == 7
    assert len(store.list_memory_objects()) == 2
    assert len(store.list_memory_index_entries()) == 2
    search_results = MemorySearch(store).search("second")
    assert len(search_results) == 1
    assert search_results[0].memory.content == "second memory"
    store.close()


def test_memory_search_handles_empty_results(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ReactionKernel(store, Ledger(store)).remember("visible memory")
    request_id = _ready_activation_request(store)
    ActivationBoundary(store).approve(request_id)

    assert MemorySearch(store).search("absent") == []
    store.close()


def test_activation_approval_requires_review_ready_request(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    TestRunner(store).run_for_patch(patch.patch_id)
    FitnessEvaluator(store).evaluate(code_proposal.code_proposal_id)
    request, _, _ = ActivationBoundary(store).request(code_proposal.code_proposal_id)

    with pytest.raises(ActivationApprovalError):
        ActivationBoundary(store).approve(request.activation_request_id)
    store.close()


def test_activation_approval_allows_only_index_memory_candidate(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    request = ActivationRequest(
        activation_request_id=new_id("activationrequest"),
        code_proposal_id="codeproposal_manual",
        status="review_required",
        reason_code="explicit_activation_decision_required",
        activation="blocked",
        payload_json=None,
        created_at=utc_now(),
    )
    store.save_activation_request(request)
    store.save_reaction_spec_candidate(
        ReactionSpecCandidate(
            candidate_id=new_id("reactionspeccandidate"),
            activation_request_id=request.activation_request_id,
            name="other_capability",
            status="candidate_blocked",
            payload_json=None,
            created_at=utc_now(),
        )
    )

    with pytest.raises(ActivationApprovalError, match="Only index_memory"):
        ActivationBoundary(store).approve(request.activation_request_id)
    store.close()
