from __future__ import annotations

from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet


class ReactionRegistry:
    def __init__(self, specs: list[ReactionSpec]) -> None:
        self._specs = list(specs)

    def find_enabled(self, working_set: WorkingSet) -> list[ReactionSpec]:
        return [spec for spec in self._specs if spec.is_enabled(working_set)]
