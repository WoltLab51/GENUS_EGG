from __future__ import annotations

import json
from pathlib import PurePath

from genus_egg.evaluation.shadow_tester import CodeChangeProposalNotFoundError
from genus_egg.ids import new_id
from genus_egg.patching.patch_approval import PatchApproval
from genus_egg.patching.patch_file_change import PatchFileChange
from genus_egg.patching.patch_risk_assessment import PatchRiskAssessment
from genus_egg.patching.sandbox_patch import SandboxPatch
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class PatchApprovalRequiredError(ValueError):
    pass


class PatchPathBlockedError(ValueError):
    pass


class SandboxPatchBoundary:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def approve(self, code_proposal_id: str) -> PatchApproval:
        if self.store.get_code_change_proposal(code_proposal_id) is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )
        approval = PatchApproval(
            approval_id=new_id("patchapproval"),
            code_proposal_id=code_proposal_id,
            approved_by="user",
            approval_scope="draft_sandbox_patch",
            status="approved",
            payload_json=json.dumps(
                {"activation": "blocked", "git": "none", "github": "none"},
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_patch_approval(approval)
        return approval

    def draft(
        self, code_proposal_id: str
    ) -> tuple[SandboxPatch, PatchRiskAssessment, list[PatchFileChange]]:
        proposal = self.store.get_code_change_proposal(code_proposal_id)
        if proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )
        approval = self.store.get_latest_patch_approval(code_proposal_id)
        if approval is None:
            raise PatchApprovalRequiredError(
                f"PatchApproval required for CodeChangeProposal: {code_proposal_id}"
            )

        allowed_paths = json.loads(proposal.allowed_paths_json)
        forbidden_paths = json.loads(proposal.forbidden_paths_json)
        planned_paths = ["src/genus_egg/memory/index.py", "tests/test_memory_indexing.py"]
        for path in planned_paths:
            if not _is_allowed(path, allowed_paths) or _is_forbidden(
                path, forbidden_paths
            ):
                raise PatchPathBlockedError(f"Patch path blocked: {path}")

        risk = PatchRiskAssessment(
            risk_assessment_id=new_id("patchrisk"),
            code_proposal_id=code_proposal_id,
            risk_level="low",
            rationale=(
                "Draft touches only memory indexing and tests inside allowed paths; "
                "activation remains blocked."
            ),
            blocked=False,
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_patch_risk_assessment(risk)

        patch = SandboxPatch(
            patch_id=new_id("sandboxpatch"),
            code_proposal_id=code_proposal_id,
            approval_id=approval.approval_id,
            risk_assessment_id=risk.risk_assessment_id,
            status="draft",
            activation="blocked",
            payload_json=json.dumps(
                {"patch_type": "sandbox", "git": "none", "github": "none"},
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_sandbox_patch(patch)

        changes = [
            PatchFileChange(
                file_change_id=new_id("filechange"),
                patch_id=patch.patch_id,
                target_path="src/genus_egg/memory/index.py",
                change_type="add",
                content_preview="Define draft MemoryIndexEntry and index lookup boundary.",
                payload_json=json.dumps({"writes_file": False}, sort_keys=True),
                created_at=utc_now(),
            ),
            PatchFileChange(
                file_change_id=new_id("filechange"),
                patch_id=patch.patch_id,
                target_path="tests/test_memory_indexing.py",
                change_type="add",
                content_preview="Cover draft memory indexing behavior.",
                payload_json=json.dumps({"writes_file": False}, sort_keys=True),
                created_at=utc_now(),
            ),
        ]
        for change in changes:
            self.store.save_patch_file_change(change)
        return patch, risk, changes


def _is_allowed(path: str, allowed_paths: list[str]) -> bool:
    normalized = _normalize(path)
    return any(
        normalized == _normalize(allowed)
        or normalized.startswith(f"{_normalize(allowed)}/")
        for allowed in allowed_paths
    )


def _is_forbidden(path: str, forbidden_paths: list[str]) -> bool:
    normalized = _normalize(path)
    return any(
        normalized == _normalize(forbidden)
        or normalized.startswith(f"{_normalize(forbidden)}/")
        for forbidden in forbidden_paths
    )


def _normalize(path: str) -> str:
    return PurePath(path.replace("\\", "/").removeprefix("./").strip("/")).as_posix()
