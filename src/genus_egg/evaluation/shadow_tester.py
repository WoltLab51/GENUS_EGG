from __future__ import annotations

import json

from genus_egg.evaluation.evaluation_criterion import EVALUATION_CRITERIA
from genus_egg.evaluation.shadow_test_plan import ShadowTestPlan
from genus_egg.ids import new_id
from genus_egg.maturation.proposal_status import ProposalStatus
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class CodeChangeProposalNotFoundError(ValueError):
    pass


class ShadowTester:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def plan(self, code_proposal_id: str) -> ShadowTestPlan:
        code_proposal = self.store.get_code_change_proposal(code_proposal_id)
        if code_proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )

        planned_checks = [
            {
                "criterion": criterion.name,
                "mode": "static_review_only",
                "executes_code": False,
            }
            for criterion in EVALUATION_CRITERIA
        ]
        plan = ShadowTestPlan(
            shadow_plan_id=new_id("shadowplan"),
            code_proposal_id=code_proposal_id,
            plan_type="proposal_shadow_test",
            status=ProposalStatus.DRAFT.value,
            planned_checks_json=json.dumps(planned_checks, sort_keys=True),
            activation="blocked",
            payload_json=json.dumps(
                {
                    "patch": "none",
                    "git": "none",
                    "github": "none",
                    "executes_code": False,
                    "writes_files": False,
                    "activation": "blocked",
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_shadow_test_plan(plan)
        return plan
