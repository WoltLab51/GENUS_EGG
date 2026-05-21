from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitBranchPreparation:
    git_preparation_id: str
    patch_id: str
    branch_name: str
    status: str
    activation: str
    payload_json: str | None
    created_at: str
