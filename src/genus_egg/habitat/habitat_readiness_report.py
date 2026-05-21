from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HabitatReadinessReport:
    report_id: str
    habitat_id: str
    snapshot_id: str
    status: str
    reason_code: str
    checks_json: str
    payload_json: str | None
    created_at: str
