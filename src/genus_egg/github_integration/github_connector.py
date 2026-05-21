from __future__ import annotations

import json

from genus_egg.evidence.test_runner import SandboxPatchNotFoundError
from genus_egg.github_integration.github_draft_pr import GitHubDraftPr
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class GitHubBlockedError(RuntimeError):
    pass


class GitHubPrerequisiteError(RuntimeError):
    pass


class GitHubConnector:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def draft_pr(self, patch_id: str, repository: str = "origin") -> GitHubDraftPr:
        patch = self.store.get_sandbox_patch(patch_id)
        if patch is None:
            raise SandboxPatchNotFoundError(f"SandboxPatch not found: {patch_id}")

        manifest = self.store.get_latest_habitat_manifest()
        if manifest is None or not manifest.github_allowed:
            raise GitHubBlockedError("github_allowed=false")

        approval = self.store.get_latest_patch_approval(patch.code_proposal_id)
        if approval is None or approval.approval_id != patch.approval_id:
            raise GitHubPrerequisiteError("PatchApproval required")

        preparations = [
            preparation
            for preparation in self.store.list_git_branch_preparations()
            if preparation.patch_id == patch_id
        ]
        if not preparations:
            raise GitHubPrerequisiteError("GitBranchPreparation required")

        if not self._has_passing_evidence(patch_id):
            raise GitHubPrerequisiteError("green EvidenceChain required")

        preparation = preparations[-1]
        draft_pr = GitHubDraftPr(
            github_draft_pr_id=new_id("githubdraftpr"),
            patch_id=patch_id,
            branch_name=preparation.branch_name,
            repository=repository,
            status="draft_ready",
            is_draft=True,
            activation="blocked",
            payload_json=json.dumps(
                {
                    "push": "none",
                    "draft_pr": "prepared",
                    "is_draft": True,
                    "merge": "none",
                    "auto_merge": "none",
                    "issue_mutation": "none",
                    "labels": "none",
                    "reviewers": "none",
                    "secrets": "none",
                    "permissions": "none",
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_github_draft_pr(draft_pr)
        return draft_pr

    def _has_passing_evidence(self, patch_id: str) -> bool:
        runs = [run for run in self.store.list_test_runs() if run.patch_id == patch_id]
        if not runs:
            return False
        run_ids = {run.test_run_id for run in runs}
        return any(
            result.test_run_id in run_ids and result.passed
            for result in self.store.list_test_results()
        )
