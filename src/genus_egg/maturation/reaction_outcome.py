from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReactionOutcome:
    outcome_id: str
    chain_id: str
    final_status: str
    final_product_type: str | None
    success: bool
    reason_code: str | None
    duration_ms: int | None
    created_at: str
