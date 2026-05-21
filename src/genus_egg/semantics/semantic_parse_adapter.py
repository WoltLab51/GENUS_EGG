from __future__ import annotations

from genus_egg.ids import new_id
from genus_egg.semantics.meaning_candidate import MeaningCandidate
from genus_egg.semantics.raw_input import RawInput
from genus_egg.time import utc_now


class SemanticParseAdapter:
    """Deterministic v0 adapter: models may interpret later, but not here."""

    version = "deterministic-v0"

    def parse(self, raw_input: RawInput) -> MeaningCandidate:
        return MeaningCandidate(
            meaning_id=new_id("meaning"),
            chain_id=raw_input.chain_id,
            source_input_id=raw_input.input_id,
            intent="memory_request",
            content=raw_input.raw_text,
            interpretation_confidence="high",
            needs_clarification=False,
            adapter_version=self.version,
            created_at=utc_now(),
        )
