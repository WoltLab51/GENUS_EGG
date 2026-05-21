from __future__ import annotations

import json

import pytest

from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.shadow_tester import CodeChangeProposalNotFoundError
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.patching.sandbox_patch_boundary import (
    PatchApprovalRequiredError,
    PatchPathBlockedError,
    SandboxPatchBoundary,
)
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_code_proposal(store: SQLiteStore) -> str:
    need = MaturationSeed(store).draft_memory_indexing_need()
    _, proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    return proposal.code_proposal_id


def test_patch_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "patch_approvals",
        "patch_risk_assessments",
        "sandbox_patches",
        "patch_file_changes",
    }.issubset(store.table_names())
    store.close()


def test_patch_approval_can_be_saved_for_existing_code_proposal(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)

    approval = SandboxPatchBoundary(store).approve(code_proposal_id)

    approvals = store.list_patch_approvals()
    assert approvals == [approval]
    assert approval.status == "approved"
    assert json.loads(approval.payload_json or "{}")["activation"] == "blocked"
    store.close()


def test_sandbox_patch_requires_approval(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)

    with pytest.raises(PatchApprovalRequiredError):
        SandboxPatchBoundary(store).draft(code_proposal_id)

    assert store.list_sandbox_patches() == []
    store.close()


def test_sandbox_patch_can_be_drafted_without_writing_files(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    code_proposal_id = _draft_code_proposal(store)
    boundary = SandboxPatchBoundary(store)
    approval = boundary.approve(code_proposal_id)

    patch, risk, changes = boundary.draft(code_proposal_id)

    assert store.list_sandbox_patches() == [patch]
    assert store.list_patch_risk_assessments() == [risk]
    assert store.list_patch_file_changes() == changes
    assert patch.approval_id == approval.approval_id
    assert patch.status == "draft"
    assert patch.activation == "blocked"
    assert risk.risk_level == "low"
    assert risk.blocked is False
    assert {change.target_path for change in changes} == {
        "src/genus_egg/memory/index.py",
        "tests/test_memory_indexing.py",
    }
    assert all(json.loads(change.payload_json or "{}")["writes_file"] is False for change in changes)
    assert not (tmp_path / "src").exists()
    store.close()


def test_patch_boundary_blocks_unknown_or_forbidden_proposal(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    boundary = SandboxPatchBoundary(store)

    with pytest.raises(CodeChangeProposalNotFoundError):
        boundary.approve("codeproposal_missing")

    code_proposal_id = _draft_code_proposal(store)
    proposal = store.get_code_change_proposal(code_proposal_id)
    assert proposal is not None
    blocked = proposal.__class__(
        code_proposal_id="codeproposal_blocked",
        proposal_id=proposal.proposal_id,
        title=proposal.title,
        rationale=proposal.rationale,
        allowed_paths_json=json.dumps(["src/genus_egg/memory", "tests"]),
        forbidden_paths_json=json.dumps(["src/genus_egg/memory"]),
        status="draft",
        payload_json=proposal.payload_json,
        created_at=proposal.created_at,
    )
    store.save_code_change_proposal(blocked)
    boundary.approve(blocked.code_proposal_id)

    with pytest.raises(PatchPathBlockedError):
        boundary.draft(blocked.code_proposal_id)

    store.close()
