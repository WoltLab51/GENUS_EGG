from __future__ import annotations

import json
import subprocess

import pytest

from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.git_integration.local_git_connector import DirtyGitTreeError, LocalGitConnector
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
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


def _init_git_repo(path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def test_git_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {"git_status_reports", "git_branch_preparations"}.issubset(
        store.table_names()
    )
    store.close()


def test_git_status_is_read_only_report(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _init_git_repo(tmp_path)

    report = LocalGitConnector(store, repo_path=tmp_path).status()

    assert store.list_git_status_reports() == [report]
    assert json.loads(report.payload_json or "{}")["git"] == "read_only"
    assert store.list_git_branch_preparations() == []
    store.close()


def test_prepare_branch_creates_preparation_and_evidence_record(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    _init_git_repo(repo_path)
    patch_id = _draft_patch(store)

    preparation = LocalGitConnector(store, repo_path=repo_path).prepare_branch(patch_id)

    assert store.list_git_branch_preparations() == [preparation]
    assert preparation.branch_name.startswith("genus/sandbox-")
    assert preparation.activation == "blocked"
    payload = json.loads(preparation.payload_json or "{}")
    assert payload["branch_created"] is False
    assert payload["push"] == "none"
    assert payload["merge"] == "none"
    evidence = store.list_evidence_records()[-1]
    assert evidence.source_kind == "git_branch_preparation"
    store.close()


def test_prepare_branch_blocks_dirty_tree(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    patch_id = _draft_patch(store)
    connector = LocalGitConnector(store, repo_path=tmp_path)

    original_status = connector.status
    report = original_status()
    dirty_report = report.__class__(
        git_status_id=report.git_status_id,
        repo_path=report.repo_path,
        current_branch=report.current_branch,
        head_commit=report.head_commit,
        dirty=True,
        remotes_json=report.remotes_json,
        payload_json=report.payload_json,
        created_at=report.created_at,
    )
    connector.status = lambda: dirty_report  # type: ignore[method-assign]

    with pytest.raises(DirtyGitTreeError):
        connector.prepare_branch(patch_id)

    assert store.list_git_branch_preparations() == []
    store.close()
