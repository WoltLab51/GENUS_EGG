from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from genus_egg.kernel.working_set import WorkingSet


@dataclass(frozen=True)
class ReactionSpec:
    name: str
    required_kind: str
    produced_kind: str
    execute: Callable[[WorkingSet], object]

    def is_enabled(self, working_set: WorkingSet) -> bool:
        if not working_set.has(self.required_kind):
            return False
        if working_set.has(self.produced_kind):
            return False
        return True
