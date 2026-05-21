from __future__ import annotations

import json

from genus_egg.ids import new_id
from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.maturation.observation_record import ObservationRecord
from genus_egg.maturation.proposal_status import ProposalStatus
from genus_egg.maturation.reaction_outcome import ReactionOutcome
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class MaturationSeed:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def record_successful_memory_chain(
        self,
        chain_id: str,
        reason_code: str,
        duration_ms: int | None,
        ledger_entries: int,
    ) -> tuple[ReactionOutcome, ObservationRecord]:
        outcome = ReactionOutcome(
            outcome_id=new_id("outcome"),
            chain_id=chain_id,
            final_status="completed",
            final_product_type="memory_object",
            success=True,
            reason_code=reason_code,
            duration_ms=duration_ms,
            created_at=utc_now(),
        )
        self.store.save_reaction_outcome(outcome)

        observation = ObservationRecord(
            observation_id=new_id("observation"),
            chain_id=chain_id,
            observation_type="reaction_chain_completed",
            payload_json=json.dumps(
                {
                    "final_status": outcome.final_status,
                    "final_product_type": outcome.final_product_type,
                    "reason_code": outcome.reason_code,
                    "ledger_entries": ledger_entries,
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_observation_record(observation)
        return outcome, observation

    def draft_memory_indexing_need(
        self, source_observation_id: str | None = None
    ) -> CapabilityNeed:
        need = CapabilityNeed(
            need_id=new_id("need"),
            source_observation_id=source_observation_id,
            need_type="capability_improvement",
            description="Memory retrieval could improve through indexing.",
            status=ProposalStatus.DRAFT.value,
            payload_json=json.dumps(
                {
                    "evidence": [
                        "memory_created",
                        "memory_query_failed_or_limited",
                    ]
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_capability_need(need)
        return need
