from __future__ import annotations

import json

from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.truth.sqlite_store import SQLiteStore


class PatternDetector:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def detect_memory_indexing_need(self) -> CapabilityNeed | None:
        observations = self.store.list_observation_records()
        memory_observations = [
            observation
            for observation in observations
            if observation.observation_type == "reaction_chain_completed"
            and json.loads(observation.payload_json).get("reason_code")
            == "memory_created"
        ]
        if not memory_observations:
            return None

        existing_need = self.store.find_capability_need(
            need_type="capability_improvement",
            description="Memory retrieval could improve through indexing.",
        )
        if existing_need is not None:
            return existing_need

        return MaturationSeed(self.store).draft_memory_indexing_need(
            source_observation_id=memory_observations[-1].observation_id
        )
