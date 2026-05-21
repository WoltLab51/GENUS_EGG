from __future__ import annotations

import json
import subprocess
from pathlib import Path

from genus_egg.evidence.evidence_record import EvidenceRecord
from genus_egg.git_integration.git_branch_preparation import GitBranchPreparation
from genus_egg.git_integration.git_status_report import GitStatusReport
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class DirtyGitTreeError(RuntimeError):
    pass


class GitUnavailableError(RuntimeError):
    pass


class LocalGitConnector:
    def __init__(self, store: SQLiteStore, repo_path: str | Path = ".") -> None:
        self.store = store
        self.repo_path = Path(repo_path)

    def status(self) -> GitStatusReport:
        current_branch = self._git(["branch", "--show-current"], allow_failure=True)
        head_commit = self._git(["rev-parse", "HEAD"], allow_failure=True)
        porcelain = self._git(["status", "--porcelain"], allow_failure=True)
        remotes = self._git(["remote", "-v"], allow_failure=True)
        report = GitStatusReport(
            git_status_id=new_id("gitstatus"),
            repo_path=str(self.repo_path.resolve()),
            current_branch=current_branch or None,
            head_commit=head_commit or None,
            dirty=bool(porcelain.strip()),
            remotes_json=json.dumps(remotes.splitlines(), sort_keys=True),
            payload_json=json.dumps({"git": "read_only"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_git_status_report(report)
        return report

    def prepare_branch(self, patch_id: str) -> GitBranchPreparation:
        patch = self.store.get_sandbox_patch(patch_id)
        if patch is None:
            raise ValueError(f"SandboxPatch not found: {patch_id}")
        report = self.status()
        if report.dirty:
            raise DirtyGitTreeError("Git working tree is dirty")

        branch_name = f"genus/sandbox-{patch_id.removeprefix('sandboxpatch_')[:12]}"
        preparation = GitBranchPreparation(
            git_preparation_id=new_id("gitprep"),
            patch_id=patch_id,
            branch_name=branch_name,
            status="prepared",
            activation="blocked",
            payload_json=json.dumps(
                {
                    "branch_created": False,
                    "patch_applied": False,
                    "push": "none",
                    "merge": "none",
                    "rebase": "none",
                    "force_push": "none",
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_git_branch_preparation(preparation)
        self.store.save_evidence_record(
            EvidenceRecord(
                evidence_id=new_id("evidence"),
                source_kind="git_branch_preparation",
                source_id=preparation.git_preparation_id,
                code_proposal_id=patch.code_proposal_id,
                evidence_type="local_git_preparation",
                summary=f"Prepared local branch record {branch_name}; no push or merge.",
                payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
                created_at=utc_now(),
            )
        )
        return preparation

    def _git(self, args: list[str], allow_failure: bool = False) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            if allow_failure:
                return ""
            raise GitUnavailableError(completed.stderr.strip() or "git unavailable")
        return completed.stdout.strip()
