from __future__ import annotations

from dataclasses import dataclass

from genus_egg.activation.activation_boundary import ActivationBoundary
from genus_egg.activation.activation_decision import ActivationDecision
from genus_egg.activation.activation_request import ActivationRequest
from genus_egg.development.capability_proposal import CapabilityProposal
from genus_egg.development.code_change_proposal import CodeChangeProposal
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluation import FitnessEvaluation
from genus_egg.evaluation.shadow_test_plan import ShadowTestPlan
from genus_egg.evaluation.shadow_tester import ShadowTester
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evidence.evidence_chain import EvidenceChain
from genus_egg.evidence.test_run import TestRun
from genus_egg.evidence.test_runner import TestRunner
from genus_egg.lifecycle.capability_activation import CapabilityActivation
from genus_egg.lifecycle.lifecycle_boundary import LifecycleBoundary
from genus_egg.lifecycle.rollback_plan import RollbackPlan
from genus_egg.maturation.capability_need import CapabilityNeed
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.memory.memory_indexer import MemoryIndexer
from genus_egg.patching.patch_approval import PatchApproval
from genus_egg.patching.sandbox_patch import SandboxPatch
from genus_egg.patching.sandbox_patch_boundary import SandboxPatchBoundary
from genus_egg.truth.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class MemoryIndexingGuidePreparation:
    need: CapabilityNeed
    proposal: CapabilityProposal
    code_proposal: CodeChangeProposal
    shadow_plan: ShadowTestPlan
    fitness_evaluation: FitnessEvaluation
    patch_approval: PatchApproval
    sandbox_patch: SandboxPatch
    test_run: TestRun
    evidence_chain: EvidenceChain
    rollback_plan: RollbackPlan
    activation_request: ActivationRequest


@dataclass(frozen=True)
class MemoryIndexingGuideApproval:
    decision: ActivationDecision
    activation: CapabilityActivation
    indexed_count: int


class MemoryIndexingGuide:
    """Orchestrates the existing safe index_memory lifecycle for humans."""

    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def is_active(self) -> bool:
        return MemoryIndexer(self.store).is_active()

    def prepare(self) -> MemoryIndexingGuidePreparation:
        observations = self.store.list_observation_records()
        source_observation_id = observations[-1].observation_id if observations else None

        need = MaturationSeed(self.store).draft_memory_indexing_need(
            source_observation_id=source_observation_id
        )
        proposal, code_proposal = DevelopmentBoundary(
            self.store
        ).draft_memory_indexing_proposal(need.need_id)
        shadow_plan = ShadowTester(self.store).plan(code_proposal.code_proposal_id)
        fitness_evaluation = FitnessEvaluator(self.store).evaluate(
            code_proposal.code_proposal_id
        ).fitness_evaluation

        patch_boundary = SandboxPatchBoundary(self.store)
        patch_approval = patch_boundary.approve(code_proposal.code_proposal_id)
        sandbox_patch, _risk, _changes = patch_boundary.draft(
            code_proposal.code_proposal_id
        )

        test_run, _test_result, _evidence, evidence_chain = TestRunner(
            self.store
        ).run_for_patch(sandbox_patch.patch_id)
        rollback_plan = LifecycleBoundary(self.store).create_rollback_plan(
            code_proposal.code_proposal_id
        )
        activation_request, _candidate, _check = ActivationBoundary(self.store).request(
            code_proposal.code_proposal_id
        )

        return MemoryIndexingGuidePreparation(
            need=need,
            proposal=proposal,
            code_proposal=code_proposal,
            shadow_plan=shadow_plan,
            fitness_evaluation=fitness_evaluation,
            patch_approval=patch_approval,
            sandbox_patch=sandbox_patch,
            test_run=test_run,
            evidence_chain=evidence_chain,
            rollback_plan=rollback_plan,
            activation_request=activation_request,
        )

    def approve(self, activation_request_id: str) -> MemoryIndexingGuideApproval:
        decision, activation, indexed_count = ActivationBoundary(self.store).approve(
            activation_request_id
        )
        return MemoryIndexingGuideApproval(
            decision=decision,
            activation=activation,
            indexed_count=indexed_count,
        )
