from __future__ import annotations

import json

import pytest

from genus_egg.activation.activation_boundary import ActivationBoundary
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.lifecycle.lifecycle_boundary import (
    LifecycleBoundary,
    RollbackPlanRequiredError,
)
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def _ready_proposal(store: SQLiteStore) -> str:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    TestRunner(store).run_for_patch(patch.patch_id)
    FitnessEvaluator(store).evaluate(code_proposal.code_proposal_id)
    return code_proposal.code_proposal_id


def test_lifecycle_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "rollback_plans",
        "capability_activations",
        "capability_monitors",
        "fossil_records",
    }.issubset(store.table_names())
    store.close()


def test_rollback_plan_can_be_saved_and_makes_activation_review_ready(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _ready_proposal(store)
    plan = LifecycleBoundary(store).create_rollback_plan(code_proposal_id)

    request, _, check = ActivationBoundary(store).request(code_proposal_id)

    assert store.list_rollback_plans() == [plan]
    assert request.status == "review_required"
    assert request.reason_code == "explicit_activation_decision_required"
    assert request.activation == "blocked"
    payload = json.loads(request.payload_json or "{}")
    assert payload["rollback_available"] is True
    assert payload["rollback_plan_id"] == plan.rollback_plan_id
    assert check.status == "review_required"
    store.close()


def test_capability_activation_requires_rollback_plan(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _ready_proposal(store)
    request, _, _ = ActivationBoundary(store).request(code_proposal_id)

    with pytest.raises(RollbackPlanRequiredError):
        LifecycleBoundary(store).record_activation_candidate(
            request.activation_request_id
        )

    assert store.list_capability_activations() == []
    store.close()


def test_monitoring_and_fossilization_store_records_without_deleting_truth(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    result = ReactionKernel(store, Ledger(store)).remember("larumipsum")
    code_proposal_id = _ready_proposal(store)
    boundary = LifecycleBoundary(store)
    plan = boundary.create_rollback_plan(code_proposal_id)
    request, _, _ = ActivationBoundary(store).request(code_proposal_id)

    activation = boundary.record_activation_candidate(request.activation_request_id)
    monitor = boundary.monitor(code_proposal_id)
    fossil = boundary.fossilize(
        "capability_activation",
        activation.capability_activation_id,
        "Not useful enough yet.",
    )

    assert result.ledger_entries == 7
    assert activation.rollback_plan_id == plan.rollback_plan_id
    assert activation.activation == "blocked"
    assert monitor.reaction_outcome_count >= 1
    assert monitor.boundary_violation_count == 0
    assert fossil.status == "fossilized"
    assert json.loads(fossil.payload_json or "{}")["deletes_truth"] is False
    assert store.count_rows("memory_objects") == 1
    store.close()
