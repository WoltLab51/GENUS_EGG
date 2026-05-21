from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePath


@dataclass(frozen=True)
class PermissionProfile:
    allowed_write_paths: list[str] = field(default_factory=lambda: ["./data", "./sandbox"])
    forbidden_paths: list[str] = field(
        default_factory=lambda: [".env", "secrets", ".git/config"]
    )
    user_approval_required: bool = True
    network_allowed: bool = False
    github_allowed: bool = False

    def blocks_path(self, path: str) -> bool:
        normalized = _normalize(path)
        for forbidden_path in self.forbidden_paths:
            forbidden = _normalize(forbidden_path)
            if normalized == forbidden or normalized.startswith(f"{forbidden}/"):
                return True
        return False

    def to_payload(self) -> dict[str, object]:
        return {
            "allowed_write_paths": self.allowed_write_paths,
            "forbidden_paths": self.forbidden_paths,
            "user_approval_required": self.user_approval_required,
        }


def _normalize(path: str) -> str:
    cleaned = path.replace("\\", "/").removeprefix("./").strip("/")
    return PurePath(cleaned).as_posix()
