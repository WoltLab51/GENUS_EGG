from __future__ import annotations

from dataclasses import dataclass

from genus_egg.kernel.artifacts import ReactionProduct, ValidationResult
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.meaning_candidate import MeaningCandidate


@dataclass(frozen=True)
class GuardDecision:
    allow: bool
    reason_code: str


class Guards:
    known_reactions = {
        "parse_user_input",
        "validate_meaning",
        "create_memory_proposal",
        "create_memory",
    }
    forbidden_effects = {
        "write_file",
        "git",
        "github",
        "llm",
        "worker",
        "graphdb",
        "embedding",
        "self_modify",
        "runtime_mutation",
    }

    def decide(self, reaction: ReactionSpec, working_set: WorkingSet) -> GuardDecision:
        for guard in (
            self.unknown_reaction_guard,
            self.forbidden_effect_guard,
            self.missing_content_guard,
            self.low_confidence_guard,
            self.validation_not_allow_guard,
            self.wrong_continuation_policy_guard,
        ):
            decision = guard(reaction, working_set)
            if not decision.allow:
                return decision
        return GuardDecision(True, "allowed")

    def allow(self, reaction: ReactionSpec, working_set: WorkingSet) -> bool:
        return self.decide(reaction, working_set).allow

    def unknown_reaction_guard(
        self, reaction: ReactionSpec, _working_set: WorkingSet
    ) -> GuardDecision:
        if reaction.name not in self.known_reactions:
            return GuardDecision(False, "unknown_reaction")
        return GuardDecision(True, "known_reaction")

    def forbidden_effect_guard(
        self, reaction: ReactionSpec, _working_set: WorkingSet
    ) -> GuardDecision:
        if set(reaction.effects).intersection(self.forbidden_effects):
            return GuardDecision(False, "forbidden_effect")
        return GuardDecision(True, "effects_allowed")

    def missing_content_guard(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> GuardDecision:
        if reaction.name != "create_memory_proposal":
            return GuardDecision(True, "content_not_required")
        if not working_set.has("meaning_candidate"):
            return GuardDecision(True, "meaning_not_available")
        meaning: MeaningCandidate = working_set.latest("meaning_candidate")
        if not meaning.content or not meaning.content.strip():
            return GuardDecision(False, "missing_content")
        return GuardDecision(True, "content_present")

    def low_confidence_guard(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> GuardDecision:
        if reaction.name != "create_memory_proposal":
            return GuardDecision(True, "confidence_not_required")
        if not working_set.has("meaning_candidate"):
            return GuardDecision(True, "meaning_not_available")
        meaning: MeaningCandidate = working_set.latest("meaning_candidate")
        if meaning.interpretation_confidence == "low":
            return GuardDecision(False, "low_confidence")
        return GuardDecision(True, "confidence_allowed")

    def validation_not_allow_guard(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> GuardDecision:
        if reaction.name != "create_memory_proposal":
            return GuardDecision(True, "validation_not_required")
        if not working_set.has("validation_result"):
            return GuardDecision(True, "validation_not_available")
        validation: ValidationResult = working_set.latest("validation_result")
        if validation.result != "allow" or validation.reason_code != "ready":
            return GuardDecision(False, "validation_not_allow")
        return GuardDecision(True, "validation_allowed")

    def wrong_continuation_policy_guard(
        self, reaction: ReactionSpec, working_set: WorkingSet
    ) -> GuardDecision:
        if reaction.name != "create_memory":
            return GuardDecision(True, "continuation_not_required")
        if not working_set.has("reaction_product"):
            return GuardDecision(True, "product_not_available")
        product: ReactionProduct = working_set.latest("reaction_product")
        if product.continuation_policy != "required":
            return GuardDecision(False, "wrong_continuation_policy")
        return GuardDecision(True, "continuation_allowed")
