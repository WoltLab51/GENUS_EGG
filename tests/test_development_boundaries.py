from __future__ import annotations

import json

import pytest

from genus_egg.development.approval_gate import ApprovalBlockedError, ApprovalGate
from genus_egg.development.development_boundary import (
    CapabilityNeedNotFoundError,
    DevelopmentBoundary,
)
from genus_egg.habitat.permission_profile import PermissionProfile
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.truth.sqlite_store import SQLiteStore


def test_development_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {
        "capability_proposals",
        "code_change_proposals",
    }.issubset(store.table_names())
    store.close()


def test_draft_capability_and_code_change_proposals_can_be_saved_and_loaded(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    need = MaturationSeed(store).draft_memory_indexing_need()

    proposal, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )

    proposals = store.list_capability_proposals()
    code_proposals = store.list_code_change_proposals()
    assert proposals == [proposal]
    assert code_proposals == [code_proposal]
    assert proposals[0].status == "draft"
    assert code_proposals[0].status == "draft"
    assert code_proposals[0].title == "Add memory indexing reaction"
    assert (
        code_proposals[0].rationale
        == "Repeated memory creation and retrieval would benefit from indexed lookup."
    )
    assert json.loads(code_proposals[0].allowed_paths_json) == [
        "src/genus_egg/memory",
        "tests",
    ]
    assert {".env", "secrets", ".git/config"}.issubset(
        set(json.loads(code_proposals[0].forbidden_paths_json))
    )
    assert json.loads(code_proposals[0].payload_json or "{}") == {
        "activation": "blocked",
        "can_activate": False,
        "can_modify_files": False,
    }
    store.close()


def test_code_change_proposal_requires_existing_capability_need(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    with pytest.raises(CapabilityNeedNotFoundError):
        DevelopmentBoundary(store).draft_memory_indexing_proposal("need_missing")

    assert store.list_capability_proposals() == []
    assert store.list_code_change_proposals() == []
    store.close()


def test_approval_gate_blocks_file_modification_and_activation():
    gate = ApprovalGate()

    assert gate.can_modify_files("src/genus_egg/memory/index.py") is False
    assert gate.can_activate("proposal_1") is False
    with pytest.raises(ApprovalBlockedError):
        gate.assert_not_active()


def test_permission_profile_forbidden_paths_remain_blocked():
    profile = PermissionProfile()

    assert profile.blocks_path(".env")
    assert profile.blocks_path("secrets/api.txt")
    assert profile.blocks_path(".git/config")
