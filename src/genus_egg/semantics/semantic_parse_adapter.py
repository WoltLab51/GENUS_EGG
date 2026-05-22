from __future__ import annotations

from genus_egg.semantics.command_parse_adapter import CommandParseAdapter
from genus_egg.semantics.meaning_candidate import MeaningCandidate
from genus_egg.semantics.raw_input import RawInput


class SemanticParseAdapter(CommandParseAdapter):
    """Compatibility wrapper; free-language semantics are not implemented."""

    def parse(self, raw_input: RawInput) -> MeaningCandidate:
        return super().parse(raw_input)
