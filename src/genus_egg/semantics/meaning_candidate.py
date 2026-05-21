from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MeaningCandidate:
    meaning_id: str
    chain_id: str
    source_input_id: str
    intent: str
    content: str
    interpretation_confidence: str
    needs_clarification: bool
    adapter_version: str
    created_at: str
