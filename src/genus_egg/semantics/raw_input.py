from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RawInput:
    input_id: str
    chain_id: str
    signal_type: str
    source_type: str
    raw_text: str
    created_at: str
