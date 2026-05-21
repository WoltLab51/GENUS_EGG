from __future__ import annotations

from genus_egg.kernel.artifacts import ValidationResult
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.meaning_candidate import MeaningCandidate


class ReactionCube:
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
            )

        if reaction.name == "create_memory":
            product = working_set.latest("reaction_product")
            return (
                product.product_type == "memory_proposal"
                and product.continuation_policy == "required"
            )

        return False
