from __future__ import annotations

import json
import subprocess

import pytest

from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.git_integration.local_git_connector import LocalGitConnector
from genus_egg.github_integration.github_connector import (
    GitHubBlockedError,
    GitHubConnector,
    GitHubPrerequisiteError,
)
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.ids import new_id
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_patch(store: SQLiteStore) -> str:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    boundary = SandboxPatchBoundary(store)
    boundary.approve(code_proposal.code_proposal_id)
    patch, _, _ = boundary.draft(code_proposal.code_proposal_id)
    return patch.patch_id


def _allow_github(store: SQLiteStore) -> None:
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


def _init_git_repo(path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def test_github_draft_pr_table_exists(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert "github_draft_prs" in store.table_names()
    store.close()


def test_github_allowed_false_blocks_by_default(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    patch_id = _draft_patch(store)

    with pytest.raises(GitHubBlockedError):
        GitHubConnector(store).draft_pr(patch_id)

    assert store.list_github_draft_prs() == []
    store.close()


def test_draft_pr_requires_evidence_and_git_preparation(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    patch_id = _draft_patch(store)
    _allow_github(store)

    with pytest.raises(GitHubPrerequisiteError, match="GitBranchPreparation"):
        GitHubConnector(store).draft_pr(patch_id)

    assert store.list_github_draft_prs() == []
    store.close()


def test_draft_pr_record_is_always_draft_and_blocked(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    _init_git_repo(repo_path)
    patch_id = _draft_patch(store)
    _allow_github(store)
    TestRunner(store).run_for_patch(patch_id)
    LocalGitConnector(store, repo_path=repo_path).prepare_branch(patch_id)

    draft_pr = GitHubConnector(store).draft_pr(patch_id, repository="WoltLab51/GENUS_EGG")

    assert store.list_github_draft_prs() == [draft_pr]
    assert draft_pr.is_draft is True
    assert draft_pr.activation == "blocked"
    payload = json.loads(draft_pr.payload_json or "{}")
    assert payload["push"] == "none"
    assert payload["merge"] == "none"
    assert payload["issue_mutation"] == "none"
    assert payload["labels"] == "none"
    assert payload["reviewers"] == "none"
    store.close()
