from __future__ import annotations

import subprocess
import json

from genus_egg.activation.activation_boundary import ActivationBoundary
from genus_egg.cockpit.data_adapter import CockpitDataAdapter
from genus_egg.cockpit.html_renderer import CockpitHtmlRenderer
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evaluation.shadow_tester import ShadowTester
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.git_integration.local_git_connector import LocalGitConnector
from genus_egg.github_integration.github_connector import GitHubConnector
from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.habitat.habitat_contract import HabitatContract
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.ids import new_id
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.lifecycle.lifecycle_boundary import LifecycleBoundary
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.time import utc_now
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def _populate_cockpit_fixture(store: SQLiteStore) -> None:
    result = ReactionKernel(store, Ledger(store)).remember("larumipsum")
    manifest = EnvironmentProbe(store.db_path).probe()
    store.save_habitat_manifest(manifest)
    contract = HabitatContract()
    snapshot = contract.snapshot_resources(manifest)
    store.save_resource_snapshot(snapshot)
    store.save_habitat_readiness_report(contract.assess(manifest, snapshot))
    need = MaturationSeed(store).draft_memory_indexing_need(
        source_observation_id=store.list_observation_records()[-1].observation_id
    )
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    ShadowTester(store).plan(code_proposal.code_proposal_id)
    FitnessEvaluator(store).evaluate(code_proposal.code_proposal_id)
    patch_boundary = SandboxPatchBoundary(store)
    patch_boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = patch_boundary.draft(code_proposal.code_proposal_id)
    TestRunner(store).run_for_patch(patch.patch_id)
    repo_path = store.db_path.parent / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    LocalGitConnector(store, repo_path=repo_path).prepare_branch(patch.patch_id)
    store.save_habitat_manifest(
        HabitatManifest(
            habitat_id=new_id("habitat"),
            device_id="device",
            hostname="host",
            os_name="test-os",
            python_version="3.12",
            repo_path=".",
            data_path="./data",
            sqlite_path=str(store.db_path),
            network_allowed=False,
            git_available=True,
            github_allowed=True,
            model_access="local_stub",
            payload_json=json.dumps({"user_approval_required": True}),
            created_at=utc_now(),
        )
    )
    GitHubConnector(store).draft_pr(patch.patch_id)
    lifecycle = LifecycleBoundary(store)
    lifecycle.create_rollback_plan(code_proposal.code_proposal_id)
    activation_request, _, _ = ActivationBoundary(store).request(
        code_proposal.code_proposal_id
    )
    _, capability_activation, _ = ActivationBoundary(store).approve(
        activation_request.activation_request_id
    )
    lifecycle.monitor(code_proposal.code_proposal_id)
    lifecycle.fossilize(
        "capability_activation",
        capability_activation.capability_activation_id,
        "Inspection fixture fossil.",
    )
    assert result.ledger_entries == 7


def test_cockpit_data_adapter_reads_all_relevant_object_counts(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)

    snapshot = CockpitDataAdapter(store).snapshot()

    assert snapshot.memory_count == 1
    assert snapshot.memory_index_entry_count == 1
    assert snapshot.ledger_entry_count == 7
    assert snapshot.habitat_manifest_count == 2
    assert snapshot.resource_snapshot_count == 1
    assert snapshot.habitat_readiness_report_count == 1
    assert snapshot.reaction_outcome_count == 1
    assert snapshot.observation_count == 1
    assert snapshot.capability_need_count == 1
    assert snapshot.capability_proposal_count == 1
    assert snapshot.code_change_proposal_count == 1
    assert snapshot.shadow_plan_count == 1
    assert snapshot.fitness_evaluation_count == 1
    assert snapshot.patch_approval_count == 1
    assert snapshot.sandbox_patch_count == 1
    assert snapshot.test_run_count == 1
    assert snapshot.evidence_record_count == 2
    assert snapshot.evidence_chain_count == 1
    assert snapshot.git_status_count == 1
    assert snapshot.git_preparation_count == 1
    assert snapshot.github_draft_pr_count == 1
    assert snapshot.activation_request_count == 1
    assert snapshot.activation_decision_count == 1
    assert snapshot.rollback_plan_count == 1
    assert snapshot.capability_activation_count == 1
    assert snapshot.capability_monitor_count == 1
    assert snapshot.fossil_record_count == 1
    assert snapshot.latest_habitat_id is not None
    assert snapshot.latest_fitness_score is not None
    assert snapshot.activation_state == "active"
    store.close()


def test_cockpit_adapter_is_read_only(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)
    before = {
        table: store.count_rows(table)
        for table in [
            "memory_objects",
            "memory_index_entries",
            "ledger_entries",
            "habitat_manifest",
            "resource_snapshots",
            "habitat_readiness_reports",
            "reaction_outcomes",
            "observation_records",
            "capability_needs",
            "capability_proposals",
            "code_change_proposals",
            "shadow_test_plans",
            "fitness_evaluations",
            "patch_approvals",
            "sandbox_patches",
            "patch_file_changes",
            "patch_risk_assessments",
            "test_runs",
            "test_results",
            "evidence_records",
            "evidence_chains",
            "git_status_reports",
            "git_branch_preparations",
            "github_draft_prs",
            "activation_requests",
            "activation_decisions",
            "reaction_spec_candidates",
            "runtime_compatibility_checks",
            "rollback_plans",
            "capability_activations",
            "capability_monitors",
            "fossil_records",
        ]
    }

    CockpitDataAdapter(store).snapshot()
    after = {table: store.count_rows(table) for table in before}

    assert after == before
    store.close()


def test_cockpit_html_renderer_is_read_only_and_shows_boundaries(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)
    snapshot = CockpitDataAdapter(store).snapshot()
    before = store.count_rows("fitness_evaluations")

    html = CockpitHtmlRenderer().render(snapshot)

    assert "GENUS EGG Inspection Cockpit" in html
    assert "Memories" in html
    assert "Ledger Entries" in html
    assert "Activation: active" in html
    assert "Mode: read-only" in html
    assert store.count_rows("fitness_evaluations") == before
    store.close()
