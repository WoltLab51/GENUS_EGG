from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryIndexEntry:
    index_entry_id: str
    memory_id: str
    normalized_content: str
    tokens_json: str
    source: str
    created_at: str
