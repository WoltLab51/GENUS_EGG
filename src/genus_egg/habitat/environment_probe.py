from __future__ import annotations

import json
import platform
import shutil
import socket
import sys
from pathlib import Path

from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.habitat.permission_profile import PermissionProfile
from genus_egg.ids import new_id
from genus_egg.time import utc_now


class EnvironmentProbe:
    """Read-only probe for the local GENUS habitat."""

    def __init__(
        self,
        db_path: str | Path,
        repo_path: str | Path | None = None,
        permission_profile: PermissionProfile | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.repo_path = Path(repo_path).resolve() if repo_path is not None else Path.cwd()
        self.permission_profile = permission_profile or PermissionProfile()

    def probe(self) -> HabitatManifest:
        hostname = socket.gethostname()
        db_path = self.db_path
        data_path = db_path.parent if db_path.parent != Path("") else Path(".")
        payload = self.permission_profile.to_payload()
        return HabitatManifest(
            habitat_id=new_id("habitat"),
            device_id="local_machine",
            hostname=hostname,
            os_name=platform.system(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            repo_path=str(self.repo_path),
            data_path=str(data_path),
            sqlite_path=str(db_path),
            network_allowed=self.permission_profile.network_allowed,
            git_available=shutil.which("git") is not None,
            github_allowed=self.permission_profile.github_allowed,
            model_access="local_stub",
            payload_json=json.dumps(payload, sort_keys=True),
            created_at=utc_now(),
        )
