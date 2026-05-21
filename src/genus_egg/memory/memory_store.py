from __future__ import annotations

from genus_egg.memory.memory_object import MemoryObject
from genus_egg.truth.sqlite_store import SQLiteStore


class MemoryStore:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def list_memories(self) -> list[MemoryObject]:
        return self.store.list_memory_objects()
