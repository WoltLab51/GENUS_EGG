from __future__ import annotations

import json

from genus_egg.development.approval_gate import ApprovalGate
from genus_egg.development.capability_proposal import CapabilityProposal
from genus_egg.development.code_change_proposal import CodeChangeProposal
from genus_egg.habitat.permission_profile import PermissionProfile
from genus_egg.ids import new_id
from genus_egg.maturation.proposal_status import ProposalStatus
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class CapabilityNeedNotFoundError(ValueError):
    pass


class DevelopmentBoundary:
    def __init__(
        self,
        store: SQLiteStore,
        permission_profile: PermissionProfile | None = None,
        approval_gate: ApprovalGate | None = None,
    ) -> None:
        self.store = store
        self.permission_profile = permission_profile or PermissionProfile()
        self.approval_gate = approval_gate or ApprovalGate()

    def draft_memory_indexing_proposal(
        self, need_id: str
    ) -> tuple[CapabilityProposal, CodeChangeProposal]:
        if not self.store.get_capability_need(need_id):
            raise CapabilityNeedNotFoundError(f"CapabilityNeed not found: {need_id}")

        capability_proposal = CapabilityProposal(
            proposal_id=new_id("proposal"),
            need_id=need_id,
            proposal_type="reaction_capability",
            description="Add memory indexing reaction",
            status=ProposalStatus.DRAFT.value,
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_capability_proposal(capability_proposal)

        code_change_proposal = CodeChangeProposal(
            code_proposal_id=new_id("codeproposal"),
            proposal_id=capability_proposal.proposal_id,
            title="Add memory indexing reaction",
            rationale=(
                "Repeated memory creation and retrieval would benefit from "
                "indexed lookup."
            ),
            allowed_paths_json=json.dumps(
                ["src/genus_egg/memory", "tests"], sort_keys=True
            ),
            forbidden_paths_json=json.dumps(
                self.permission_profile.forbidden_paths, sort_keys=True
            ),
            status=ProposalStatus.DRAFT.value,
            payload_json=json.dumps(
                {
                    "activation": "blocked",
                    "can_modify_files": self.approval_gate.can_modify_files(),
                    "can_activate": self.approval_gate.can_activate(),
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_code_change_proposal(code_change_proposal)
        return capability_proposal, code_change_proposal
