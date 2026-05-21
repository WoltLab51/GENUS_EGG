from __future__ import annotations

import json

import pytest

from genus_egg.activation.activation_boundary import (
    ActivationBoundary,
    ActivationPrerequisiteError,
)
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.truth.sqlite_store import SQLiteStore


def _proposal_and_patch(store: SQLiteStore) -> tuple[str, str]:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    return code_proposal.code_proposal_id, patch.patch_id


def _ready_proposal(store: SQLiteStore) -> str:
    code_proposal_id, patch_id = _proposal_and_patch(store)
    TestRunner(store).run_for_patch(patch_id)
    FitnessEvaluator(store).evaluate(code_proposal_id)
    return code_proposal_id


def test_activation_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "activation_requests",
        "activation_decisions",
        "reaction_spec_candidates",
        "runtime_compatibility_checks",
    }.issubset(store.table_names())
    store.close()


def test_activation_request_requires_fitness_evidence_and_approval(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )

    with pytest.raises(ActivationPrerequisiteError, match="FitnessEvaluation"):
        ActivationBoundary(store).request(code_proposal.code_proposal_id)

    assert store.list_activation_requests() == []
    store.close()


def test_activation_request_stays_blocked_without_rollback_data(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _ready_proposal(store)

    request, candidate, check = ActivationBoundary(store).request(code_proposal_id)

    assert store.list_activation_requests() == [request]
    assert store.list_reaction_spec_candidates() == [candidate]
    assert store.list_runtime_compatibility_checks() == [check]
    assert request.status == "blocked"
    assert request.reason_code == "rollback_data_missing"
    assert request.activation == "blocked"
    payload = json.loads(request.payload_json or "{}")
    assert payload["rollback_available"] is False
    assert payload["score_activates"] is False
    assert check.status == "blocked"
    store.close()


def test_activation_can_be_rejected_and_fossilized_as_decision(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _ready_proposal(store)
    request, _, _ = ActivationBoundary(store).request(code_proposal_id)

    decision = ActivationBoundary(store).reject(
        request.activation_request_id, "No rollback plan."
    )

    assert store.list_activation_decisions() == [decision]
    assert decision.decision == "rejected"
    assert decision.activation == "blocked"
    assert json.loads(decision.payload_json or "{}")["fossilized"] is True
    store.close()
