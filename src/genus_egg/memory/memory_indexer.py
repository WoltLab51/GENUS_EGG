from __future__ import annotations

import json
import re

from genus_egg.ids import new_id
from genus_egg.memory.memory_index_entry import MemoryIndexEntry
from genus_egg.memory.memory_object import MemoryObject
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class MemoryIndexer:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def is_active(self) -> bool:
        request_ids = {
            candidate.activation_request_id
            for candidate in self.store.list_reaction_spec_candidates()
            if candidate.name == "index_memory"
        }
        return any(
            activation.activation == "active"
            and activation.status == "active"
            and activation.activation_request_id in request_ids
            for activation in self.store.list_capability_activations()
        )

    def index_memory(self, memory: MemoryObject, source: str = "active_reaction") -> bool:
        if not self.is_active():
            return False
        entry = MemoryIndexEntry(
            index_entry_id=new_id("memoryindex"),
            memory_id=memory.memory_id,
            normalized_content=normalize_text(memory.content),
            tokens_json=json.dumps(tokenize(memory.content), sort_keys=True),
            source=source,
            created_at=utc_now(),
        )
        self.store.save_memory_index_entry(entry)
        return True

    def backfill(self) -> int:
        count = 0
        indexed_memory_ids = {
            entry.memory_id for entry in self.store.list_memory_index_entries()
        }
        for memory in self.store.list_memory_objects():
            if memory.memory_id in indexed_memory_ids:
                continue
            if self.index_memory(memory, source="activation_backfill"):
                count += 1
        return count


def normalize_text(text: str) -> str:
    return " ".join(text.casefold().split())


def tokenize(text: str) -> list[str]:
    return sorted(set(re.findall(r"\w+", normalize_text(text))))
