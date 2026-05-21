from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitStatusReport:
    git_status_id: str
    repo_path: str
    current_branch: str | None
    head_commit: str | None
    dirty: bool
    remotes_json: str
    payload_json: str | None
    created_at: str
