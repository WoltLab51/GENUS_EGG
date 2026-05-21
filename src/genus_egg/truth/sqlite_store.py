from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from genus_egg.development.capability_proposal import CapabilityProposal
from genus_egg.development.code_change_proposal import CodeChangeProposal
from genus_egg.evaluation.fitness_evaluation import FitnessEvaluation
from genus_egg.evaluation.shadow_test_plan import ShadowTestPlan
from genus_egg.evidence.evidence_chain import EvidenceChain
from genus_egg.evidence.evidence_record import EvidenceRecord
from genus_egg.evidence.test_result import TestResult
from genus_egg.evidence.test_run import TestRun
from genus_egg.git_integration.git_branch_preparation import GitBranchPreparation
from genus_egg.git_integration.git_status_report import GitStatusReport
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.habitat.habitat_readiness_report import HabitatReadinessReport
from genus_egg.habitat.resource_snapshot import ResourceSnapshot
from genus_egg.kernel.artifacts import ReactionProduct, ReactionRecord, ValidationResult
from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.maturation.observation_record import ObservationRecord
from genus_egg.maturation.reaction_outcome import ReactionOutcome
from genus_egg.memory.memory_object import MemoryObject
from genus_egg.patching.patch_approval import PatchApproval
from genus_egg.patching.patch_file_change import PatchFileChange
from genus_egg.patching.patch_risk_assessment import PatchRiskAssessment
from genus_egg.patching.sandbox_patch import SandboxPatch
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

    def list_ledger_entries(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT ledger_id, chain_id, step, event_type, source_kind, source_id,
                   target_kind, target_id, payload_json, created_at
            FROM ledger_entries
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [dict(row) for row in rows]

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

    def save_resource_snapshot(self, snapshot: ResourceSnapshot) -> None:
        self.connection.execute(
            """
            INSERT INTO resource_snapshots
            (snapshot_id, habitat_id, cpu_count, cpu_label, memory_total_mb,
             memory_available_mb, disk_total_mb, disk_free_mb, temperature_celsius,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.snapshot_id,
                snapshot.habitat_id,
                snapshot.cpu_count,
                snapshot.cpu_label,
                snapshot.memory_total_mb,
                snapshot.memory_available_mb,
                snapshot.disk_total_mb,
                snapshot.disk_free_mb,
                snapshot.temperature_celsius,
                snapshot.payload_json,
                snapshot.created_at,
            ),
        )
        self.connection.commit()

    def list_resource_snapshots(self) -> list[ResourceSnapshot]:
        rows = self.connection.execute(
            """
            SELECT snapshot_id, habitat_id, cpu_count, cpu_label, memory_total_mb,
                   memory_available_mb, disk_total_mb, disk_free_mb,
                   temperature_celsius, payload_json, created_at
            FROM resource_snapshots
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            ResourceSnapshot(
                snapshot_id=row["snapshot_id"],
                habitat_id=row["habitat_id"],
                cpu_count=row["cpu_count"],
                cpu_label=row["cpu_label"],
                memory_total_mb=row["memory_total_mb"],
                memory_available_mb=row["memory_available_mb"],
                disk_total_mb=row["disk_total_mb"],
                disk_free_mb=row["disk_free_mb"],
                temperature_celsius=row["temperature_celsius"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_habitat_readiness_report(
        self, report: HabitatReadinessReport
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO habitat_readiness_reports
            (report_id, habitat_id, snapshot_id, status, reason_code, checks_json,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.report_id,
                report.habitat_id,
                report.snapshot_id,
                report.status,
                report.reason_code,
                report.checks_json,
                report.payload_json,
                report.created_at,
            ),
        )
        self.connection.commit()

    def list_habitat_readiness_reports(self) -> list[HabitatReadinessReport]:
        rows = self.connection.execute(
            """
            SELECT report_id, habitat_id, snapshot_id, status, reason_code,
                   checks_json, payload_json, created_at
            FROM habitat_readiness_reports
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            HabitatReadinessReport(
                report_id=row["report_id"],
                habitat_id=row["habitat_id"],
                snapshot_id=row["snapshot_id"],
                status=row["status"],
                reason_code=row["reason_code"],
                checks_json=row["checks_json"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

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

    def get_code_change_proposal(
        self, code_proposal_id: str
    ) -> CodeChangeProposal | None:
        row = self.connection.execute(
            """
            SELECT code_proposal_id, proposal_id, title, rationale,
                   allowed_paths_json, forbidden_paths_json, status, payload_json,
                   created_at
            FROM code_change_proposals
            WHERE code_proposal_id = ?
            """,
            (code_proposal_id,),
        ).fetchone()
        if row is None:
            return None
        return CodeChangeProposal(
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

    def save_shadow_test_plan(self, plan: ShadowTestPlan) -> None:
        self.connection.execute(
            """
            INSERT INTO shadow_test_plans
            (shadow_plan_id, code_proposal_id, plan_type, status,
             planned_checks_json, activation, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan.shadow_plan_id,
                plan.code_proposal_id,
                plan.plan_type,
                plan.status,
                plan.planned_checks_json,
                plan.activation,
                plan.payload_json,
                plan.created_at,
            ),
        )
        self.connection.commit()

    def list_shadow_test_plans(self) -> list[ShadowTestPlan]:
        rows = self.connection.execute(
            """
            SELECT shadow_plan_id, code_proposal_id, plan_type, status,
                   planned_checks_json, activation, payload_json, created_at
            FROM shadow_test_plans
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            ShadowTestPlan(
                shadow_plan_id=row["shadow_plan_id"],
                code_proposal_id=row["code_proposal_id"],
                plan_type=row["plan_type"],
                status=row["status"],
                planned_checks_json=row["planned_checks_json"],
                activation=row["activation"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_latest_shadow_test_plan_for_code_proposal(
        self, code_proposal_id: str
    ) -> ShadowTestPlan | None:
        row = self.connection.execute(
            """
            SELECT shadow_plan_id, code_proposal_id, plan_type, status,
                   planned_checks_json, activation, payload_json, created_at
            FROM shadow_test_plans
            WHERE code_proposal_id = ?
            ORDER BY created_at DESC, rowid DESC
            LIMIT 1
            """,
            (code_proposal_id,),
        ).fetchone()
        if row is None:
            return None
        return ShadowTestPlan(
            shadow_plan_id=row["shadow_plan_id"],
            code_proposal_id=row["code_proposal_id"],
            plan_type=row["plan_type"],
            status=row["status"],
            planned_checks_json=row["planned_checks_json"],
            activation=row["activation"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def save_fitness_evaluation(self, evaluation: FitnessEvaluation) -> None:
        self.connection.execute(
            """
            INSERT INTO fitness_evaluations
            (evaluation_id, code_proposal_id, shadow_plan_id, score,
             criteria_scores_json, rationale, activation, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation.evaluation_id,
                evaluation.code_proposal_id,
                evaluation.shadow_plan_id,
                evaluation.score,
                evaluation.criteria_scores_json,
                evaluation.rationale,
                evaluation.activation,
                evaluation.payload_json,
                evaluation.created_at,
            ),
        )
        self.connection.commit()

    def list_fitness_evaluations(self) -> list[FitnessEvaluation]:
        rows = self.connection.execute(
            """
            SELECT evaluation_id, code_proposal_id, shadow_plan_id, score,
                   criteria_scores_json, rationale, activation, payload_json,
                   created_at
            FROM fitness_evaluations
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            FitnessEvaluation(
                evaluation_id=row["evaluation_id"],
                code_proposal_id=row["code_proposal_id"],
                shadow_plan_id=row["shadow_plan_id"],
                score=row["score"],
                criteria_scores_json=row["criteria_scores_json"],
                rationale=row["rationale"],
                activation=row["activation"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_patch_approval(self, approval: PatchApproval) -> None:
        self.connection.execute(
            """
            INSERT INTO patch_approvals
            (approval_id, code_proposal_id, approved_by, approval_scope, status,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval.approval_id,
                approval.code_proposal_id,
                approval.approved_by,
                approval.approval_scope,
                approval.status,
                approval.payload_json,
                approval.created_at,
            ),
        )
        self.connection.commit()

    def list_patch_approvals(self) -> list[PatchApproval]:
        rows = self.connection.execute(
            """
            SELECT approval_id, code_proposal_id, approved_by, approval_scope,
                   status, payload_json, created_at
            FROM patch_approvals
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            PatchApproval(
                approval_id=row["approval_id"],
                code_proposal_id=row["code_proposal_id"],
                approved_by=row["approved_by"],
                approval_scope=row["approval_scope"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_latest_patch_approval(self, code_proposal_id: str) -> PatchApproval | None:
        row = self.connection.execute(
            """
            SELECT approval_id, code_proposal_id, approved_by, approval_scope,
                   status, payload_json, created_at
            FROM patch_approvals
            WHERE code_proposal_id = ? AND status = 'approved'
            ORDER BY created_at DESC, rowid DESC
            LIMIT 1
            """,
            (code_proposal_id,),
        ).fetchone()
        if row is None:
            return None
        return PatchApproval(
            approval_id=row["approval_id"],
            code_proposal_id=row["code_proposal_id"],
            approved_by=row["approved_by"],
            approval_scope=row["approval_scope"],
            status=row["status"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def save_patch_risk_assessment(self, risk: PatchRiskAssessment) -> None:
        self.connection.execute(
            """
            INSERT INTO patch_risk_assessments
            (risk_assessment_id, code_proposal_id, risk_level, rationale, blocked,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                risk.risk_assessment_id,
                risk.code_proposal_id,
                risk.risk_level,
                risk.rationale,
                int(risk.blocked),
                risk.payload_json,
                risk.created_at,
            ),
        )
        self.connection.commit()

    def list_patch_risk_assessments(self) -> list[PatchRiskAssessment]:
        rows = self.connection.execute(
            """
            SELECT risk_assessment_id, code_proposal_id, risk_level, rationale,
                   blocked, payload_json, created_at
            FROM patch_risk_assessments
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            PatchRiskAssessment(
                risk_assessment_id=row["risk_assessment_id"],
                code_proposal_id=row["code_proposal_id"],
                risk_level=row["risk_level"],
                rationale=row["rationale"],
                blocked=bool(row["blocked"]),
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_sandbox_patch(self, patch: SandboxPatch) -> None:
        self.connection.execute(
            """
            INSERT INTO sandbox_patches
            (patch_id, code_proposal_id, approval_id, risk_assessment_id, status,
             activation, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patch.patch_id,
                patch.code_proposal_id,
                patch.approval_id,
                patch.risk_assessment_id,
                patch.status,
                patch.activation,
                patch.payload_json,
                patch.created_at,
            ),
        )
        self.connection.commit()

    def list_sandbox_patches(self) -> list[SandboxPatch]:
        rows = self.connection.execute(
            """
            SELECT patch_id, code_proposal_id, approval_id, risk_assessment_id,
                   status, activation, payload_json, created_at
            FROM sandbox_patches
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            SandboxPatch(
                patch_id=row["patch_id"],
                code_proposal_id=row["code_proposal_id"],
                approval_id=row["approval_id"],
                risk_assessment_id=row["risk_assessment_id"],
                status=row["status"],
                activation=row["activation"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_sandbox_patch(self, patch_id: str) -> SandboxPatch | None:
        row = self.connection.execute(
            """
            SELECT patch_id, code_proposal_id, approval_id, risk_assessment_id,
                   status, activation, payload_json, created_at
            FROM sandbox_patches
            WHERE patch_id = ?
            """,
            (patch_id,),
        ).fetchone()
        if row is None:
            return None
        return SandboxPatch(
            patch_id=row["patch_id"],
            code_proposal_id=row["code_proposal_id"],
            approval_id=row["approval_id"],
            risk_assessment_id=row["risk_assessment_id"],
            status=row["status"],
            activation=row["activation"],
            payload_json=row["payload_json"],
            created_at=row["created_at"],
        )

    def save_patch_file_change(self, change: PatchFileChange) -> None:
        self.connection.execute(
            """
            INSERT INTO patch_file_changes
            (file_change_id, patch_id, target_path, change_type, content_preview,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                change.file_change_id,
                change.patch_id,
                change.target_path,
                change.change_type,
                change.content_preview,
                change.payload_json,
                change.created_at,
            ),
        )
        self.connection.commit()

    def list_patch_file_changes(self) -> list[PatchFileChange]:
        rows = self.connection.execute(
            """
            SELECT file_change_id, patch_id, target_path, change_type,
                   content_preview, payload_json, created_at
            FROM patch_file_changes
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            PatchFileChange(
                file_change_id=row["file_change_id"],
                patch_id=row["patch_id"],
                target_path=row["target_path"],
                change_type=row["change_type"],
                content_preview=row["content_preview"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_test_run(self, test_run: TestRun) -> None:
        self.connection.execute(
            """
            INSERT INTO test_runs
            (test_run_id, patch_id, command_name, status, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                test_run.test_run_id,
                test_run.patch_id,
                test_run.command_name,
                test_run.status,
                test_run.payload_json,
                test_run.created_at,
            ),
        )
        self.connection.commit()

    def list_test_runs(self) -> list[TestRun]:
        rows = self.connection.execute(
            """
            SELECT test_run_id, patch_id, command_name, status, payload_json, created_at
            FROM test_runs
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            TestRun(
                test_run_id=row["test_run_id"],
                patch_id=row["patch_id"],
                command_name=row["command_name"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_test_result(self, result: TestResult) -> None:
        self.connection.execute(
            """
            INSERT INTO test_results
            (test_result_id, test_run_id, result, passed, summary, payload_json,
             created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.test_result_id,
                result.test_run_id,
                result.result,
                int(result.passed),
                result.summary,
                result.payload_json,
                result.created_at,
            ),
        )
        self.connection.commit()

    def list_test_results(self) -> list[TestResult]:
        rows = self.connection.execute(
            """
            SELECT test_result_id, test_run_id, result, passed, summary,
                   payload_json, created_at
            FROM test_results
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            TestResult(
                test_result_id=row["test_result_id"],
                test_run_id=row["test_run_id"],
                result=row["result"],
                passed=bool(row["passed"]),
                summary=row["summary"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_evidence_record(self, evidence: EvidenceRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO evidence_records
            (evidence_id, source_kind, source_id, code_proposal_id, evidence_type,
             summary, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence.evidence_id,
                evidence.source_kind,
                evidence.source_id,
                evidence.code_proposal_id,
                evidence.evidence_type,
                evidence.summary,
                evidence.payload_json,
                evidence.created_at,
            ),
        )
        self.connection.commit()

    def list_evidence_records(self) -> list[EvidenceRecord]:
        rows = self.connection.execute(
            """
            SELECT evidence_id, source_kind, source_id, code_proposal_id,
                   evidence_type, summary, payload_json, created_at
            FROM evidence_records
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            EvidenceRecord(
                evidence_id=row["evidence_id"],
                source_kind=row["source_kind"],
                source_id=row["source_id"],
                code_proposal_id=row["code_proposal_id"],
                evidence_type=row["evidence_type"],
                summary=row["summary"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def list_evidence_records_for_code_proposal(
        self, code_proposal_id: str
    ) -> list[EvidenceRecord]:
        return [
            evidence
            for evidence in self.list_evidence_records()
            if evidence.code_proposal_id == code_proposal_id
        ]

    def save_evidence_chain(self, chain: EvidenceChain) -> None:
        self.connection.execute(
            """
            INSERT INTO evidence_chains
            (evidence_chain_id, code_proposal_id, evidence_ids_json, status,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chain.evidence_chain_id,
                chain.code_proposal_id,
                chain.evidence_ids_json,
                chain.status,
                chain.payload_json,
                chain.created_at,
            ),
        )
        self.connection.commit()

    def list_evidence_chains(self) -> list[EvidenceChain]:
        rows = self.connection.execute(
            """
            SELECT evidence_chain_id, code_proposal_id, evidence_ids_json, status,
                   payload_json, created_at
            FROM evidence_chains
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            EvidenceChain(
                evidence_chain_id=row["evidence_chain_id"],
                code_proposal_id=row["code_proposal_id"],
                evidence_ids_json=row["evidence_ids_json"],
                status=row["status"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_git_status_report(self, report: GitStatusReport) -> None:
        self.connection.execute(
            """
            INSERT INTO git_status_reports
            (git_status_id, repo_path, current_branch, head_commit, dirty,
             remotes_json, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.git_status_id,
                report.repo_path,
                report.current_branch,
                report.head_commit,
                int(report.dirty),
                report.remotes_json,
                report.payload_json,
                report.created_at,
            ),
        )
        self.connection.commit()

    def list_git_status_reports(self) -> list[GitStatusReport]:
        rows = self.connection.execute(
            """
            SELECT git_status_id, repo_path, current_branch, head_commit, dirty,
                   remotes_json, payload_json, created_at
            FROM git_status_reports
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            GitStatusReport(
                git_status_id=row["git_status_id"],
                repo_path=row["repo_path"],
                current_branch=row["current_branch"],
                head_commit=row["head_commit"],
                dirty=bool(row["dirty"]),
                remotes_json=row["remotes_json"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def save_git_branch_preparation(self, preparation: GitBranchPreparation) -> None:
        self.connection.execute(
            """
            INSERT INTO git_branch_preparations
            (git_preparation_id, patch_id, branch_name, status, activation,
             payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                preparation.git_preparation_id,
                preparation.patch_id,
                preparation.branch_name,
                preparation.status,
                preparation.activation,
                preparation.payload_json,
                preparation.created_at,
            ),
        )
        self.connection.commit()

    def list_git_branch_preparations(self) -> list[GitBranchPreparation]:
        rows = self.connection.execute(
            """
            SELECT git_preparation_id, patch_id, branch_name, status, activation,
                   payload_json, created_at
            FROM git_branch_preparations
            ORDER BY created_at, rowid
            """
        ).fetchall()
        return [
            GitBranchPreparation(
                git_preparation_id=row["git_preparation_id"],
                patch_id=row["patch_id"],
                branch_name=row["branch_name"],
                status=row["status"],
                activation=row["activation"],
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
