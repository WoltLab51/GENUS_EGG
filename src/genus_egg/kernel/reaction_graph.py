from __future__ import annotations

from dataclasses import dataclass

from genus_egg.kernel.artifacts import ReactionProduct
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet


@dataclass(frozen=True)
class ReactionEdge:
    from_kind: str
    to_reaction: str
    required_product_type: str | None = None
    continuation_required: bool | None = None
    terminal_behavior: str | None = None


class ReactionGraph:
    def __init__(self) -> None:
        self._edges = [
            ReactionEdge("raw_input", "parse_user_input"),
            ReactionEdge("meaning_candidate", "validate_meaning"),
            ReactionEdge("validation_result", "create_memory_proposal"),
            ReactionEdge(
                "reaction_product",
                "create_memory",
                required_product_type="memory_proposal",
                continuation_required=True,
                terminal_behavior="complete_chain",
            ),
        ]

    def allows_if_continuation(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> bool:
        edge = next(
            (
                edge
                for edge in self._edges
                if edge.from_kind == working_set.last_artifact_kind
                and edge.to_reaction == reaction.name
            ),
            None,
        )
        if edge is None:
            return False
        if edge.required_product_type is not None:
            if not working_set.has(edge.from_kind):
                return False
            product: ReactionProduct = working_set.latest(edge.from_kind)
            if product.product_type != edge.required_product_type:
                return False
        if edge.continuation_required is not None:
            if not working_set.has(edge.from_kind):
                return False
            product = working_set.latest(edge.from_kind)
            required = product.continuation_policy == "required"
            if required != edge.continuation_required:
                return False
        return True
