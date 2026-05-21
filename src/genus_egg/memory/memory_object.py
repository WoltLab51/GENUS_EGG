from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryObject:
    memory_id: str
    chain_id: str
    memory_type: str
    content: str
    memory_state: str
    source_product_id: str
    created_at: str
