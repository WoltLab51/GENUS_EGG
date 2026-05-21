from __future__ import annotations

import json

from genus_egg.evidence.evidence_chain import EvidenceChain
from genus_egg.evidence.evidence_record import EvidenceRecord
from genus_egg.evidence.test_result import TestResult
from genus_egg.evidence.test_run import TestRun
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class SandboxPatchNotFoundError(ValueError):
    pass


class TestRunner:
    __test__ = False

    ALLOWED_COMMAND = "sandbox_patch_static_check"

    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def run_for_patch(
        self, patch_id: str
    ) -> tuple[TestRun, TestResult, EvidenceRecord, EvidenceChain]:
        patch = self.store.get_sandbox_patch(patch_id)
        if patch is None:
            raise SandboxPatchNotFoundError(f"SandboxPatch not found: {patch_id}")

        changes = [
            change
            for change in self.store.list_patch_file_changes()
            if change.patch_id == patch_id
        ]
        passed = patch.status == "draft" and patch.activation == "blocked" and bool(changes)
        status = "completed"
        result = "passed" if passed else "failed"
        summary = (
            "Sandbox patch is draft-only, has file change records, and activation is blocked."
            if passed
            else "Sandbox patch is missing draft status, blocked activation, or file changes."
        )

        test_run = TestRun(
            test_run_id=new_id("testrun"),
            patch_id=patch_id,
            command_name=self.ALLOWED_COMMAND,
            status=status,
            payload_json=json.dumps(
                {"shell": "none", "allowed_command": self.ALLOWED_COMMAND},
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_test_run(test_run)

        test_result = TestResult(
            test_result_id=new_id("testresult"),
            test_run_id=test_run.test_run_id,
            result=result,
            passed=passed,
            summary=summary,
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_test_result(test_result)

        evidence = EvidenceRecord(
            evidence_id=new_id("evidence"),
            source_kind="test_result",
            source_id=test_result.test_result_id,
            code_proposal_id=patch.code_proposal_id,
            evidence_type="sandbox_patch_static_check",
            summary=summary,
            payload_json=json.dumps({"passed": passed}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_evidence_record(evidence)

        chain = EvidenceChain(
            evidence_chain_id=new_id("evidencechain"),
            code_proposal_id=patch.code_proposal_id,
            evidence_ids_json=json.dumps([evidence.evidence_id], sort_keys=True),
            status="complete" if passed else "blocked",
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_evidence_chain(chain)
        return test_run, test_result, evidence, chain
