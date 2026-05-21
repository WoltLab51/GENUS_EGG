from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeCompatibilityCheck:
    compatibility_check_id: str
    activation_request_id: str
    status: str
    reason_code: str
    payload_json: str | None
    created_at: str
