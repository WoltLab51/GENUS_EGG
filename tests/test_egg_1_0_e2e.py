from __future__ import annotations

import json
import subprocess

from genus_egg.activation.activation_boundary import ActivationBoundary
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


def test_complete_egg_1_0_end_to_end_demo(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    result = ReactionKernel(store, Ledger(store)).remember("larumipsum")
    assert result.ledger_entries == 7

    manifest = EnvironmentProbe(store.db_path).probe()
    store.save_habitat_manifest(manifest)
    contract = HabitatContract()
    resources = contract.snapshot_resources(manifest)
    store.save_resource_snapshot(resources)
    store.save_habitat_readiness_report(contract.assess(manifest, resources))

    need = MaturationSeed(store).draft_memory_indexing_need(
        store.list_observation_records()[-1].observation_id
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

    repo_path = tmp_path / "repo"
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
    GitHubConnector(store).draft_pr(patch.patch_id, repository="WoltLab51/GENUS_EGG")

    lifecycle = LifecycleBoundary(store)
    lifecycle.create_rollback_plan(code_proposal.code_proposal_id)
    request, _, _ = ActivationBoundary(store).request(code_proposal.code_proposal_id)
    activation = lifecycle.record_activation_candidate(request.activation_request_id)
    lifecycle.monitor(code_proposal.code_proposal_id)
    lifecycle.fossilize(
        "capability_activation",
        activation.capability_activation_id,
        "End-to-end demo remains blocked.",
    )
    ActivationBoundary(store).reject(request.activation_request_id, "Demo rejection.")

    assert store.count_rows("memory_objects") == 1
    assert store.count_rows("ledger_entries") == 7
    assert store.count_rows("habitat_readiness_reports") == 1
    assert store.count_rows("capability_needs") == 1
    assert store.count_rows("code_change_proposals") == 1
    assert store.count_rows("shadow_test_plans") == 1
    assert store.count_rows("fitness_evaluations") == 1
    assert store.count_rows("sandbox_patches") == 1
    assert store.count_rows("evidence_chains") == 1
    assert store.count_rows("git_branch_preparations") == 1
    assert store.count_rows("github_draft_prs") == 1
    assert store.count_rows("activation_requests") == 1
    assert store.count_rows("rollback_plans") == 1
    assert store.count_rows("capability_activations") == 1
    assert store.count_rows("capability_monitors") == 1
    assert store.count_rows("fossil_records") == 1
    assert store.count_rows("activation_decisions") == 1
    assert store.list_capability_activations()[0].activation == "blocked"
    store.close()
