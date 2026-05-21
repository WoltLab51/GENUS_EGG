from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    validation_id: str
    chain_id: str
    source_meaning_id: str
    result: str
    reason_code: str
    created_at: str


@dataclass(frozen=True)
class ReactionRecord:
    reaction_id: str
    chain_id: str
    source_validation_id: str | None
    reaction_type: str
    context: str
    reaction_state: str
    resolver_mode: str
    cube_coord: int | None
    created_at: str


@dataclass(frozen=True)
class ReactionProduct:
    product_id: str
    chain_id: str
    produced_by_reaction_id: str
    product_type: str
    continuation_policy: str
    payload_json: str
    created_at: str


@dataclass(frozen=True)
class KernelResult:
    chain_id: str
    outcome: str
    reason_code: str
    ledger_entries: int
    memory_content: str | None = None
