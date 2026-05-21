from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestRun:
    test_run_id: str
    patch_id: str
    command_name: str
    status: str
    payload_json: str | None
    created_at: str
