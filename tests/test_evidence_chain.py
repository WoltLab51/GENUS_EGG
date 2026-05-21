from __future__ import annotations

import json

import pytest

from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evidence.test_runner import SandboxPatchNotFoundError, TestRunner
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_patch(store: SQLiteStore) -> tuple[str, str]:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    return code_proposal.code_proposal_id, patch.patch_id


def test_evidence_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {"test_runs", "test_results", "evidence_records", "evidence_chains"}.issubset(
        store.table_names()
    )
    store.close()


def test_test_runner_creates_evidence_chain_for_sandbox_patch(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id, patch_id = _draft_patch(store)

    test_run, test_result, evidence, chain = TestRunner(store).run_for_patch(patch_id)

    assert store.list_test_runs() == [test_run]
    assert store.list_test_results() == [test_result]
    assert store.list_evidence_records() == [evidence]
    assert store.list_evidence_chains() == [chain]
    assert test_run.command_name == "sandbox_patch_static_check"
    assert json.loads(test_run.payload_json or "{}")["shell"] == "none"
    assert test_result.passed is True
    assert evidence.code_proposal_id == code_proposal_id
    assert json.loads(chain.evidence_ids_json) == [evidence.evidence_id]
    assert chain.status == "complete"
    store.close()


def test_test_runner_blocks_unknown_patch(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    with pytest.raises(SandboxPatchNotFoundError):
        TestRunner(store).run_for_patch("sandboxpatch_missing")

    assert store.list_test_runs() == []
    assert store.list_evidence_records() == []
    store.close()


def test_fitness_evaluation_references_evidence_when_available(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id, patch_id = _draft_patch(store)
    _, _, evidence, _ = TestRunner(store).run_for_patch(patch_id)

    report = FitnessEvaluator(store).evaluate(code_proposal_id)
    payload = json.loads(report.fitness_evaluation.payload_json or "{}")
    criteria = json.loads(report.fitness_evaluation.criteria_scores_json)

    assert payload["references_evidence_ids"] == [evidence.evidence_id]
    assert criteria["test_plan_quality"] == 100
    assert report.fitness_evaluation.activation == "blocked"
    store.close()
