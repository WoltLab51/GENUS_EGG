from __future__ import annotations

from dataclasses import dataclass

from genus_egg.memory.memory_index_entry import MemoryIndexEntry
from genus_egg.memory.memory_object import MemoryObject


@dataclass(frozen=True)
class MemorySearchResult:
    memory: MemoryObject
    index_entry: MemoryIndexEntry
    match: str
