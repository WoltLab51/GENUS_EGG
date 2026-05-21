from __future__ import annotations

from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet


class Guards:
    def allow(self, reaction: ReactionSpec, working_set: WorkingSet) -> bool:
        return True
