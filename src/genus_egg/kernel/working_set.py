from __future__ import annotations

from collections import defaultdict
from typing import Any


class WorkingSet:
    def __init__(self, chain_id: str) -> None:
        self.chain_id = chain_id
        self._artifacts: dict[str, list[Any]] = defaultdict(list)
        self.last_artifact_kind: str | None = None

    def add(self, kind: str, artifact: Any) -> None:
        self._artifacts[kind].append(artifact)
        self.last_artifact_kind = kind

    def has(self, kind: str) -> bool:
        return bool(self._artifacts.get(kind))

    def latest(self, kind: str) -> Any:
        artifacts = self._artifacts.get(kind)
        if not artifacts:
            raise KeyError(f"no artifact of kind {kind}")
        return artifacts[-1]
