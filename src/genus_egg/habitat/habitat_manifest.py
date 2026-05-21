from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HabitatManifest:
    habitat_id: str
    device_id: str
    hostname: str
    os_name: str
    python_version: str
    repo_path: str | None
    data_path: str
    sqlite_path: str
    network_allowed: bool
    git_available: bool
    github_allowed: bool
    model_access: str
    payload_json: str | None
    created_at: str
