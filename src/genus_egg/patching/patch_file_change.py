from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatchFileChange:
    file_change_id: str
    patch_id: str
    target_path: str
    change_type: str
    content_preview: str
    payload_json: str | None
    created_at: str
