from __future__ import annotations

import json

import pytest

from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.evaluation_criterion import EVALUATION_CRITERIA
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evaluation.shadow_tester import (
    CodeChangeProposalNotFoundError,
    ShadowTester,
)
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_code_proposal(store: SQLiteStore) -> str:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    return code_proposal.code_proposal_id


def test_shadow_and_fitness_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {"shadow_test_plans", "fitness_evaluations"}.issubset(
        store.table_names()
    )
    store.close()


def test_shadow_plan_can_be_created_from_existing_code_proposal(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)

    plan = ShadowTester(store).plan(code_proposal_id)
    plans = store.list_shadow_test_plans()

    assert plans == [plan]
    assert plan.code_proposal_id == code_proposal_id
    assert plan.status == "draft"
    assert plan.activation == "blocked"
    checks = json.loads(plan.planned_checks_json)
    assert [check["criterion"] for check in checks] == [
        criterion.name for criterion in EVALUATION_CRITERIA
    ]
    assert all(check["executes_code"] is False for check in checks)
    payload = json.loads(plan.payload_json or "{}")
    assert payload["patch"] == "none"
    assert payload["git"] == "none"
    assert payload["github"] == "none"
    assert payload["writes_files"] is False
    assert payload["activation"] == "blocked"
    store.close()


def test_shadow_plan_requires_existing_code_proposal(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    with pytest.raises(CodeChangeProposalNotFoundError):
        ShadowTester(store).plan("codeproposal_missing")

    assert store.list_shadow_test_plans() == []
    store.close()


def test_fitness_evaluation_can_be_stored_and_listed(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)

    report = FitnessEvaluator(store).evaluate(code_proposal_id)
    evaluations = store.list_fitness_evaluations()
    plans = store.list_shadow_test_plans()

    assert len(plans) == 1
    assert evaluations == [report.fitness_evaluation]
    assert report.shadow_plan == plans[0]
    assert report.status == "draft"
    assert report.activation == "blocked"
    evaluation = evaluations[0]
    assert evaluation.code_proposal_id == code_proposal_id
    assert evaluation.shadow_plan_id == plans[0].shadow_plan_id
    assert 0 <= evaluation.score <= 100
    assert evaluation.score >= 90
    assert evaluation.activation == "blocked"
    assert "activation is blocked" in evaluation.rationale
    criteria_scores = json.loads(evaluation.criteria_scores_json)
    assert set(criteria_scores) == {criterion.name for criterion in EVALUATION_CRITERIA}
    payload = json.loads(evaluation.payload_json or "{}")
    assert payload["patch"] == "none"
    assert payload["git"] == "none"
    assert payload["github"] == "none"
    assert payload["workers"] == "none"
    assert payload["activation"] == "blocked"
    store.close()


def test_fitness_evaluation_reuses_existing_shadow_plan(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)
    plan = ShadowTester(store).plan(code_proposal_id)

    report = FitnessEvaluator(store).evaluate(code_proposal_id)

    assert report.shadow_plan == plan
    assert len(store.list_shadow_test_plans()) == 1
    store.close()


def test_fitness_evaluation_requires_existing_code_proposal(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    with pytest.raises(CodeChangeProposalNotFoundError):
        FitnessEvaluator(store).evaluate("codeproposal_missing")

    assert store.list_fitness_evaluations() == []
    store.close()
