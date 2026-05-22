from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from genus_egg.kernel.artifacts import ValidationResult
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.meaning_candidate import MeaningCandidate


@dataclass(frozen=True)
class ReactionCoordinate:
    intent: str
    context: str
    reaction_state: str

    @property
    def code(self) -> "ReactionCode":
        return ReactionCode.from_coordinate(self)


class ReactionCode(IntEnum):
    BLOCKED = 0
    MEMORY_REQUEST_NORMAL_READY = 7

    @classmethod
    def from_coordinate(cls, coordinate: ReactionCoordinate) -> "ReactionCode":
        intent_bit = 1 if coordinate.intent == "memory_request" else 0
        context_bit = 1 if coordinate.context == "normal" else 0
        state_bit = 1 if coordinate.reaction_state == "ready" else 0
        value = (intent_bit << 2) | (context_bit << 1) | state_bit
        if value == cls.MEMORY_REQUEST_NORMAL_READY:
            return cls.MEMORY_REQUEST_NORMAL_READY
        return cls.BLOCKED


class ReactionCube:
    def coordinate(self, working_set: WorkingSet) -> ReactionCoordinate:
        intent = "none"
        if working_set.has("meaning_candidate"):
            meaning: MeaningCandidate = working_set.latest("meaning_candidate")
            intent = meaning.intent

        reaction_state = "blocked"
        if working_set.has("validation_result"):
            validation: ValidationResult = working_set.latest("validation_result")
            if validation.result == "allow" and validation.reason_code == "ready":
                reaction_state = "ready"

        return ReactionCoordinate(
            intent=intent,
            context="normal",
            reaction_state=reaction_state,
        )

    def allows(self, reaction: ReactionSpec, working_set: WorkingSet) -> bool:
        if reaction.name in {"parse_user_input", "validate_meaning"}:
            return True

        if reaction.name == "create_memory_proposal":
            meaning: MeaningCandidate = working_set.latest("meaning_candidate")
            validation: ValidationResult = working_set.latest("validation_result")
            return (
                meaning.intent == "memory_request"
                and validation.result == "allow"
                and validation.reason_code == "ready"
                and self.coordinate(working_set).code
                == ReactionCode.MEMORY_REQUEST_NORMAL_READY
            )

        if reaction.name == "create_memory":
            product = working_set.latest("reaction_product")
            return (
                product.product_type == "memory_proposal"
                and product.continuation_policy == "required"
            )

        return False
