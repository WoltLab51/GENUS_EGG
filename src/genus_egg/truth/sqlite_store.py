from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from genus_egg.development.capability_proposal import CapabilityProposal
from genus_egg.development.code_change_proposal import CodeChangeProposal
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.kernel.artifacts import ReactionProduct, ReactionRecord, ValidationResult
from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.maturation.observation_record import ObservationRecord
from genus_egg.maturation.reaction_outcome import ReactionOutcome
from genus_egg.memory.memory_object import MemoryObject
from genus_egg.semantics.meaning_candidate import MeaningCandidate
from genus_egg.semantics.raw_input import RawInput
from genus_egg.truth.migrations import apply_migrations


class SQLiteStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        apply_migrations(self.connection)

    def close(self) -> None:
        self.connection.close()

    def table_names(self) -> set[str]:
        rows = self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return {row["name"] for row in rows}

    def save_raw_input(self, raw_input: RawInput) -> None:
        self.connection.execute(
            """
            INSERT INTO raw_inputs
            (input_id, chain_id, signal_type, source_type, raw_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                raw_input.input_id,
                raw_input.chain_id,
                raw_input.signal_type,
                raw_input.source_type,
                raw_input.raw_text,
                raw_input.created_at,
            ),
        )
        self.connection.commit()

    def save_meaning_candidate(self, meaning: MeaningCandidate) -> None:
        self.connection.execute(
            """
            INSERT INTO meaning_candidates
            (meaning_id, chain_id, source_input_id, intent, content,
             interpretation_confidence, needs_clarification, adapter_version,
             created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meaning.meaning_id,
                meaning.chain_id,
                meaning.source_input_id,
                meaning.intent,
                meaning.content,
                meaning.interpretation_confidence,
                int(meaning.needs_clarification),
                meaning.adapter_version,
                meaning.created_at,
            ),
        )
        self.connection.commit()

    def save_validation_result(self, validation: ValidationResult) -> None:
        self.connection.execute(
            """
            INSERT INTO validation_results
            (validation_id, chain_id, source_meaning_id, result, reason_code,
             created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                validation.validation_id,
                validation.chain_id,
                validation.source_meaning_id,
                validation.result,
                validation.reason_code,
                validation.created_at,
            ),
        )
        self.connection.commit()

    def save_reaction(self, reaction: ReactionRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO reactions
            (reaction_id, chain_id, source_validation_id, reaction_type, context,
             reaction_state, resolver_mode, cube_coord, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reaction.reaction_id,
                reaction.chain_id,
                reaction.source_validation_id,
                reaction.reaction_type,
                reaction.context,
                reaction.reaction_state,
                reaction.resolver_mode,
                reaction.cube_coord,
                reaction.created_at,
            ),
        )
        self.connection.commit()

    def save_reaction_product(self, product: ReactionProduct) -> None:
        self.connection.execute(
            """
            INSERT INTO reaction_products
            (product_id, chain_id, produced_by_reaction_id, product_type,
             continuation_policy, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.product_id,
                product.chain_id,
                product.produced_by_reaction_id,
                product.product_type,
                product.continuation_policy,
                product.payload_json,
                product.created_at,
            ),
        )
        self.connection.commit()

    def save_memory_object(self, memory: MemoryObject) -> None:
        self.connection.execute(
            """
            INSERT INTO memory_objects
            (memory_id, chain_id, memory_type, content, memory_state,
             source_product_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.memory_id,
                memory.chain_id,
                memory.memory_type,
                memory.content,
                memory.memory_state,
                memory.source_product_id,
                memory.created_at,
            ),
        )
        self.connection.commit()

    def list_memory_objects(self) -> list[MemoryObject]:
        rows = self.connection.execute(
            """
            SELECT memory_id, chain_id, memory_type, content, memory_state,
                   source_product_id, created_at
            FROM memory_objects
            ORDER BY created_at, memory_id
            """
        ).fetchall()
        return [
            MemoryObject(
                memory_id=row["memory_id"],
                chain_id=row["chain_id"],
                memory_type=row["memory_type"],
                content=row["content"],
                memory_state=row["memory_state"],
                source_product_id=row["source_product_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_habitat_manifest(self, manifest: HabitatManifest) -> None:
        self.connection.execute(
            """
            INSERT INTO habitat_manifest
            (habitat_id, device_id, hostname, os_name, python_version, repo_path,
             data_path, sqlite_path, network_allowed, git_available,
             github_allowed, model_access, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                manifest.habitat_id,
                manifest.device_id,
                manifest.hostname,
                manifest.os_name,
                manifest.python_version,
                manifest.repo_path,
                manifest.data_path,
                manifest.sqlite_path,
                int(manifest.network_allowed),
                int(manifest.git_available),
                int(manifest.github_allowed),
                manifest.model_access,
                manifest.payload_json,
                manifest.created_at,
            ),
        )
        self.connection.commit()

    def get_latest_habitat_manifest(self) -> HabitatManifest | None:
        row = self.connection.execute(
            """
            SELECT habitat_id, device_id, hostname, os_name, python_version,
                   repo_path, data_path, sqlite_path, network_allowed,
                   git_available, github_allowed, model_access, payload_json,
                   created_at
            FROM habitat_manifest
            ORDER BY created_at DESC, rowid DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        return HabitatManifest(
            habitat_id=row["habitat_id"],
            device_id=row["device_id"],
            hostname=row["hostname"],
            os_name=row["os_name"],
            python_version=row["python_version"],
            repo_path=row["repo_path"],
            data_path=row["data_path"],
            sqlite_path=row["sqlite_path"],
            network_allowed=bool(row["network_allowed"]),
            git_available=bool(row["git_available"]),
            github_allowed=bool(row["github_allowed"]),
            model_access=row["model_access"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def save_reaction_outcome(self, outcome: ReactionOutcome) -> None:
        self.connection.execute(
            """
            INSERT INTO reaction_outcomes
            (outcome_id, chain_id, final_status, final_product_type, success,
             reason_code, duration_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                outcome.outcome_id,
                outcome.chain_id,
                outcome.final_status,
                outcome.final_product_type,
                int(outcome.success),
                outcome.reason_code,
                outcome.duration_ms,
                outcome.created_at,
            ),
        )
        self.connection.commit()

    def list_reaction_outcomes(self) -> list[ReactionOutcome]:
        rows = self.connection.execute(
            """
            SELECT outcome_id, chain_id, final_status, final_product_type,
                   success, reason_code, duration_ms, created_at
            FROM reaction_outcomes
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            ReactionOutcome(
                outcome_id=row["outcome_id"],
                chain_id=row["chain_id"],
                final_status=row["final_status"],
                final_product_type=row["final_product_type"],
                success=bool(row["success"]),
                reason_code=row["reason_code"],
                duration_ms=row["duration_ms"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_observation_record(self, observation: ObservationRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO observation_records
            (observation_id, chain_id, observation_type, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                observation.observation_id,
                observation.chain_id,
                observation.observation_type,
                observation.payload_json,
                observation.created_at,
            ),
        )
        self.connection.commit()

    def list_observation_records(self) -> list[ObservationRecord]:
        rows = self.connection.execute(
            """
            SELECT observation_id, chain_id, observation_type, payload_json, created_at
            FROM observation_records
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            ObservationRecord(
                observation_id=row["observation_id"],
                chain_id=row["chain_id"],
                observation_type=row["observation_type"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_capability_need(self, need: CapabilityNeed) -> None:
        self.connection.execute(
            """
            INSERT INTO capability_needs
            (need_id, source_observation_id, need_type, description, status,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                need.need_id,
                need.source_observation_id,
                need.need_type,
                need.description,
                need.status,
                need.payload_json,
                need.created_at,
            ),
        )
        self.connection.commit()

    def list_capability_needs(self) -> list[CapabilityNeed]:
        rows = self.connection.execute(
            """
            SELECT need_id, source_observation_id, need_type, description, status,
                   payload_json, created_at
            FROM capability_needs
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            CapabilityNeed(
                need_id=row["need_id"],
                source_observation_id=row["source_observation_id"],
                need_type=row["need_type"],
                description=row["description"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_capability_need(self, need_id: str) -> CapabilityNeed | None:
        row = self.connection.execute(
            """
            SELECT need_id, source_observation_id, need_type, description, status,
                   payload_json, created_at
            FROM capability_needs
            WHERE need_id = ?
            """,
            (need_id,),
        ).fetchone()
        if row is None:
            return None
        return CapabilityNeed(
            need_id=row["need_id"],
            source_observation_id=row["source_observation_id"],
            need_type=row["need_type"],
            description=row["description"],
            status=row["status"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def find_capability_need(
        self, need_type: str, description: str
    ) -> CapabilityNeed | None:
        row = self.connection.execute(
            """
            SELECT need_id, source_observation_id, need_type, description, status,
                   payload_json, created_at
            FROM capability_needs
            WHERE need_type = ? AND description = ?
            ORDER BY created_at, rowid
            LIMIT 1
            """,
            (need_type, description),
        ).fetchone()
        if row is None:
            return None
        return CapabilityNeed(
            need_id=row["need_id"],
            source_observation_id=row["source_observation_id"],
            need_type=row["need_type"],
            description=row["description"],
            status=row["status"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def save_capability_proposal(self, proposal: CapabilityProposal) -> None:
        self.connection.execute(
            """
            INSERT INTO capability_proposals
            (proposal_id, need_id, proposal_type, description, status,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                proposal.proposal_id,
                proposal.need_id,
                proposal.proposal_type,
                proposal.description,
                proposal.status,
                proposal.payload_json,
                proposal.created_at,
            ),
        )
        self.connection.commit()

    def list_capability_proposals(self) -> list[CapabilityProposal]:
        rows = self.connection.execute(
            """
            SELECT proposal_id, need_id, proposal_type, description, status,
                   payload_json, created_at
            FROM capability_proposals
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            CapabilityProposal(
                proposal_id=row["proposal_id"],
                need_id=row["need_id"],
                proposal_type=row["proposal_type"],
                description=row["description"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_code_change_proposal(self, proposal: CodeChangeProposal) -> None:
        self.connection.execute(
            """
            INSERT INTO code_change_proposals
            (code_proposal_id, proposal_id, title, rationale, allowed_paths_json,
             forbidden_paths_json, status, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                proposal.code_proposal_id,
                proposal.proposal_id,
                proposal.title,
                proposal.rationale,
                proposal.allowed_paths_json,
                proposal.forbidden_paths_json,
                proposal.status,
                proposal.payload_json,
                proposal.created_at,
            ),
        )
        self.connection.commit()

    def list_code_change_proposals(self) -> list[CodeChangeProposal]:
        rows = self.connection.execute(
            """
            SELECT code_proposal_id, proposal_id, title, rationale,
                   allowed_paths_json, forbidden_paths_json, status, payload_json,
                   created_at
            FROM code_change_proposals
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            CodeChangeProposal(
                code_proposal_id=row["code_proposal_id"],
                proposal_id=row["proposal_id"],
                title=row["title"],
                rationale=row["rationale"],
                allowed_paths_json=row["allowed_paths_json"],
                forbidden_paths_json=row["forbidden_paths_json"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def count_rows(self, table: str) -> int:
        if table not in self.table_names():
            raise ValueError(f"unknown table: {table}")
        row = self.connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def fetch_one(self, table: str) -> dict[str, Any]:
        if table not in self.table_names():
            raise ValueError(f"unknown table: {table}")
        row = self.connection.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
        return dict(row) if row else {}
