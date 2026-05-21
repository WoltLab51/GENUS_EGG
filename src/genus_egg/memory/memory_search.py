from __future__ import annotations

import json

from genus_egg.memory.memory_indexer import normalize_text, tokenize
from genus_egg.memory.memory_search_result import MemorySearchResult
from genus_egg.truth.sqlite_store import SQLiteStore


class MemorySearch:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def search(self, query: str) -> list[MemorySearchResult]:
        normalized_query = normalize_text(query)
        if not normalized_query:
            return []
        query_tokens = set(tokenize(query))
        memories = {memory.memory_id: memory for memory in self.store.list_memory_objects()}
        results: list[MemorySearchResult] = []
        for entry in self.store.list_memory_index_entries():
            memory = memories.get(entry.memory_id)
            if memory is None:
                continue
            entry_tokens = set(json.loads(entry.tokens_json))
            if normalized_query in entry.normalized_content:
                results.append(MemorySearchResult(memory, entry, normalized_query))
                continue
            matched_tokens = sorted(query_tokens.intersection(entry_tokens))
            if matched_tokens:
                results.append(MemorySearchResult(memory, entry, matched_tokens[0]))
        return results
