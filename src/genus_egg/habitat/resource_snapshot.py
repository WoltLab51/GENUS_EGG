from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSnapshot:
    snapshot_id: str
    habitat_id: str
    cpu_count: int | None
    cpu_label: str
    memory_total_mb: int | None
    memory_available_mb: int | None
    disk_total_mb: int
    disk_free_mb: int
    temperature_celsius: float | None
    payload_json: str | None
    created_at: str
