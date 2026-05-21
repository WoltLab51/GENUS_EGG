from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FossilRecord:
    fossil_record_id: str
    source_kind: str
    source_id: str
    reason: str
    status: str
    payload_json: str | None
    created_at: str
