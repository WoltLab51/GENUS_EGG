from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestResult:
    test_result_id: str
    test_run_id: str
    result: str
    passed: bool
    summary: str
    payload_json: str | None
    created_at: str
