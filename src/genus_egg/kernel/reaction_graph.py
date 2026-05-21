from __future__ import annotations

from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet


class ReactionGraph:
    def __init__(self) -> None:
        self._edges = {
            ("raw_input", "parse_user_input"),
            ("meaning_candidate", "validate_meaning"),
            ("validation_result", "create_memory_proposal"),
            ("reaction_product", "create_memory"),
        }

    def allows_if_continuation(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> bool:
        return (working_set.last_artifact_kind, reaction.name) in self._edges
