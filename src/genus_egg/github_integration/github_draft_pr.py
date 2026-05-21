from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubDraftPr:
    github_draft_pr_id: str
    patch_id: str
    branch_name: str
    repository: str
    status: str
    is_draft: bool
    activation: str
    payload_json: str | None
    created_at: str
