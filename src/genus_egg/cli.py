from __future__ import annotations

import argparse
from pathlib import Path

from genus_egg import __version__
from genus_egg.activation.activation_boundary import (
    ActivationApprovalError,
    ActivationBoundary,
    ActivationPrerequisiteError,
    ActivationRequestNotFoundError,
)
from genus_egg.development.development_boundary import (
    CapabilityNeedNotFoundError,
    DevelopmentBoundary,
    GROWTH_SIMULATION_STATEMENT,
)
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evaluation.shadow_tester import (
    CodeChangeProposalNotFoundError,
    ShadowTester,
)
from genus_egg.evidence.test_runner import SandboxPatchNotFoundError, TestRunner
from genus_egg.git_integration.local_git_connector import (
    DirtyGitTreeError,
    LocalGitConnector,
)
from genus_egg.github_integration.github_connector import (
    GitHubBlockedError,
    GitHubConnector,
    GitHubPrerequisiteError,
)
from genus_egg.guide.memory_indexing_guide import MemoryIndexingGuide
from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.habitat.habitat_contract import HabitatContract
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.lifecycle.lifecycle_boundary import (
    LifecycleBoundary,
    RollbackPlanRequiredError,
)
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.maturation.pattern_detector import PatternDetector
from genus_egg.memory.memory_store import MemoryStore
from genus_egg.memory.memory_indexer import MemoryIndexer
from genus_egg.memory.memory_search import MemorySearch
from genus_egg.patching.sandbox_patch_boundary import (
    PatchApprovalRequiredError,
    PatchPathBlockedError,
    SandboxPatchBoundary,
)
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


DEFAULT_DB = Path("data/genus_egg.sqlite")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="genus-egg")
    parser.add_argument(
        "--version",
        action="version",
        version=f"genus-egg {__version__}",
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    remember = subparsers.add_parser("remember", help="Create a governed memory")
    remember.add_argument("text")

    subparsers.add_parser("memories", help="List stored memories")

    ledger = subparsers.add_parser("ledger", help="List ledger entries for a chain")
    ledger.add_argument("--chain", required=True)

    habitat = subparsers.add_parser("habitat", help="Probe and store the local habitat")
    habitat.add_argument(
        "action",
        nargs="?",
        choices=["probe", "readiness"],
        default="probe",
    )
    habitat.add_argument("--db", default=argparse.SUPPRESS, help="SQLite database path")

    subparsers.add_parser("observations", help="List maturation observations")

    needs = subparsers.add_parser("needs", help="List or draft capability needs")
    needs.add_argument(
        "action",
        nargs="?",
        choices=["list", "draft-memory-indexing", "detect"],
        default="list",
    )

    proposals = subparsers.add_parser(
        "proposals", help="List or draft development proposals"
    )
    proposals.add_argument(
        "action",
        nargs="?",
        choices=["list", "draft-memory-indexing"],
        default="list",
    )
    proposals.add_argument("--need")

    growth = subparsers.add_parser("growth", help="Run draft-only growth simulations")
    growth.add_argument(
        "action",
        choices=["simulate-memory-indexing"],
    )
    growth.add_argument("--need")

    shadow = subparsers.add_parser("shadow", help="Create draft-only shadow plans")
    shadow.add_argument("action", choices=["plan"])
    shadow.add_argument("--code-proposal")

    fitness = subparsers.add_parser(
        "fitness", help="Evaluate draft code proposals without activation"
    )
    fitness.add_argument("action", choices=["evaluate", "list"])
    fitness.add_argument("--code-proposal")

    patch = subparsers.add_parser("patch", help="Approve or draft sandbox patches")
    patch.add_argument("action", choices=["approve", "draft", "list"])
    patch.add_argument("--code-proposal")

    tests = subparsers.add_parser("tests", help="Run controlled GENUS test checks")
    tests.add_argument("action", choices=["run"])
    tests.add_argument("--patch")

    evidence = subparsers.add_parser("evidence", help="List stored evidence records")
    evidence.add_argument("action", choices=["list"])

    git_parser = subparsers.add_parser("git", help="Inspect or prepare local Git")
    git_parser.add_argument("action", choices=["status", "prepare-branch"])
    git_parser.add_argument("--repo", default=".")
    git_parser.add_argument("--patch")

    github = subparsers.add_parser("github", help="Prepare draft-only GitHub PRs")
    github.add_argument("action", choices=["draft-pr"])
    github.add_argument("--patch")
    github.add_argument("--repository", default="origin")

    activation = subparsers.add_parser("activation", help="Model activation requests")
    activation.add_argument("action", choices=["request", "reject", "approve", "list"])
    activation.add_argument("--code-proposal")
    activation.add_argument("--request")
    activation.add_argument("--rationale", default="Rejected by explicit boundary.")

    memory = subparsers.add_parser("memory", help="Search or inspect memory index")
    memory.add_argument("action", choices=["search", "index-status"])
    memory.add_argument("query", nargs="?")

    rollback = subparsers.add_parser("rollback", help="Create or list rollback plans")
    rollback.add_argument("action", choices=["plan", "list"])
    rollback.add_argument("--code-proposal")

    monitor = subparsers.add_parser("monitor", help="Create or list monitors")
    monitor.add_argument("action", choices=["capability", "activation", "list"])
    monitor.add_argument("--code-proposal")
    monitor.add_argument("--request")

    fossilize = subparsers.add_parser("fossilize", help="Create or list fossils")
    fossilize.add_argument("action", choices=["record", "list"])
    fossilize.add_argument("--source-kind")
    fossilize.add_argument("--source-id")
    fossilize.add_argument("--reason", default="No longer eligible for activation.")

    guide = subparsers.add_parser("guide", help="Run guided safe GENUS flows")
    guide.add_argument("action", choices=["memory-indexing"])

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = SQLiteStore(args.db)
    ledger = Ledger(store)

    try:
        if args.command == "remember":
            result = ReactionKernel(store, ledger).remember(args.text)
            if result.outcome != "completed":
                print(f"Outcome: {result.outcome}")
                print(f"Reason: {result.reason_code}")
                print(f"Chain: {result.chain_id}")
                print(f"Ledger entries: {result.ledger_entries}")
                return 1
            print(f"Memory created: {result.memory_content}")
            print(f"Chain: {result.chain_id}")
            print(f"Ledger entries: {result.ledger_entries}")
            print("Outcome: completed")
            return 0

        if args.command == "memories":
            memories = MemoryStore(store).list_memories()
            for memory in memories:
                print(f"{memory.memory_id}\t{memory.chain_id}\t{memory.content}")
            return 0

        if args.command == "ledger":
            entries = ledger.list_by_chain(args.chain)
            for entry in entries:
                print(
                    f"{entry.step}\t{entry.event_type}\t"
                    f"{entry.source_kind}:{entry.source_id}\t"
                    f"{entry.target_kind or '-'}:{entry.target_id or '-'}"
                )
            return 0

        if args.command == "habitat":
            manifest = EnvironmentProbe(args.db).probe()
            store.save_habitat_manifest(manifest)
            if args.action == "readiness":
                contract = HabitatContract()
                snapshot = contract.snapshot_resources(manifest)
                report = contract.assess(manifest, snapshot)
                store.save_resource_snapshot(snapshot)
                store.save_habitat_readiness_report(report)
                print(f"habitat_id: {manifest.habitat_id}")
                print(f"snapshot_id: {snapshot.snapshot_id}")
                print(f"readiness: {report.status}")
                print(f"reason: {report.reason_code}")
                print(f"cpu_count: {snapshot.cpu_count}")
                print(f"memory_total_mb: {snapshot.memory_total_mb or 'unknown'}")
                print(f"disk_free_mb: {snapshot.disk_free_mb}")
                print("Activation: blocked")
                return 0
            print(f"habitat_id: {manifest.habitat_id}")
            print(f"os_name: {manifest.os_name}")
            print(f"repo_path: {manifest.repo_path}")
            print(f"sqlite_path: {manifest.sqlite_path}")
            print(f"git_available: {str(manifest.git_available).lower()}")
            print(f"network_allowed: {str(manifest.network_allowed).lower()}")
            return 0

        if args.command == "observations":
            for observation in store.list_observation_records():
                print(
                    f"{observation.observation_id}\t{observation.chain_id}\t"
                    f"{observation.observation_type}"
                )
            return 0

        if args.command == "needs":
            if args.action == "draft-memory-indexing":
                observations = store.list_observation_records()
                source_observation_id = (
                    observations[-1].observation_id if observations else None
                )
                need = MaturationSeed(store).draft_memory_indexing_need(
                    source_observation_id=source_observation_id
                )
                print(f"CapabilityNeed drafted: {need.description}")
                print(f"Need: {need.need_id}")
                print(f"Status: {need.status}")
                print(f"Activation: none")
                return 0

            if args.action == "detect":
                need = PatternDetector(store).detect_memory_indexing_need()
                if need is None:
                    print("PatternDetector: no capability need detected")
                    return 0

                print(f"PatternDetector detected: {need.description}")
                print(f"Need: {need.need_id}")
                print(f"Status: {need.status}")
                print("Activation: none")
                return 0

            for need in store.list_capability_needs():
                print(f"{need.need_id}\t{need.status}\t{need.description}")
            return 0

        if args.command == "proposals":
            if args.action == "draft-memory-indexing":
                if not args.need:
                    print("Missing required --need NEED_ID")
                    return 2
                try:
                    proposal, code_proposal = (
                        DevelopmentBoundary(store).draft_memory_indexing_proposal(
                            args.need
                        )
                    )
                except CapabilityNeedNotFoundError as error:
                    print(str(error))
                    return 1

                print(f"CapabilityProposal drafted: {proposal.description}")
                print(f"Proposal: {proposal.proposal_id}")
                print(f"CodeProposal: {code_proposal.code_proposal_id}")
                print(f"Status: {proposal.status}")
                print("Activation: blocked")
                return 0

            for proposal in store.list_capability_proposals():
                print(f"{proposal.proposal_id}\t{proposal.status}\t{proposal.description}")
            return 0

        if args.command == "growth":
            if not args.need:
                print("Missing required --need NEED_ID")
                return 2
            try:
                proposal, code_proposal = (
                    DevelopmentBoundary(store).draft_memory_indexing_proposal(
                        args.need
                    )
                )
            except CapabilityNeedNotFoundError as error:
                print(str(error))
                return 1

            print(GROWTH_SIMULATION_STATEMENT)
            print(f"Proposal: {proposal.proposal_id}")
            print(f"CodeProposal: {code_proposal.code_proposal_id}")
            print(f"Rationale: {code_proposal.rationale}")
            print("Testplan:")
            print("- Add tests for index_memory ReactionSpec registration.")
            print("- Add tests that MemoryIndexEntry records are created from MemoryObject.")
            print("- Add retrieval tests proving indexed lookup improves memory search.")
            print("Patch: none")
            print("Git: none")
            print("Activation: blocked")
            return 0

        if args.command == "shadow":
            if not args.code_proposal:
                print("Missing required --code-proposal CODE_PROPOSAL_ID")
                return 2
            try:
                plan = ShadowTester(store).plan(args.code_proposal)
            except CodeChangeProposalNotFoundError as error:
                print(str(error))
                return 1

            print(f"ShadowTestPlan created: {plan.shadow_plan_id}")
            print(f"CodeProposal: {plan.code_proposal_id}")
            print(f"Status: {plan.status}")
            print("Patch: none")
            print("Git: none")
            print(f"Activation: {plan.activation}")
            return 0

        if args.command == "fitness":
            if args.action == "evaluate":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    report = FitnessEvaluator(store).evaluate(args.code_proposal)
                except CodeChangeProposalNotFoundError as error:
                    print(str(error))
                    return 1

                evaluation = report.fitness_evaluation
                print(f"FitnessEvaluation created: {evaluation.evaluation_id}")
                print(f"CodeProposal: {evaluation.code_proposal_id}")
                print(f"ShadowPlan: {evaluation.shadow_plan_id}")
                print(f"Score: {evaluation.score}")
                print(f"Rationale: {evaluation.rationale}")
                print("Patch: none")
                print("Git: none")
                print(f"Activation: {evaluation.activation}")
                return 0

            for evaluation in store.list_fitness_evaluations():
                print(
                    f"{evaluation.evaluation_id}\t{evaluation.code_proposal_id}\t"
                    f"{evaluation.score}\t{evaluation.activation}"
                )
            return 0

        if args.command == "patch":
            boundary = SandboxPatchBoundary(store)
            if args.action == "approve":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    approval = boundary.approve(args.code_proposal)
                except CodeChangeProposalNotFoundError as error:
                    print(str(error))
                    return 1
                print(f"PatchApproval created: {approval.approval_id}")
                print(f"CodeProposal: {approval.code_proposal_id}")
                print(f"Status: {approval.status}")
                print("Activation: blocked")
                return 0

            if args.action == "draft":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    patch, risk, changes = boundary.draft(args.code_proposal)
                except (
                    CodeChangeProposalNotFoundError,
                    PatchApprovalRequiredError,
                    PatchPathBlockedError,
                ) as error:
                    print(str(error))
                    return 1
                print(f"SandboxPatch drafted: {patch.patch_id}")
                print(f"CodeProposal: {patch.code_proposal_id}")
                print(f"Risk: {risk.risk_level}")
                print(f"FileChanges: {len(changes)}")
                print(f"Status: {patch.status}")
                print("Git: none")
                print("GitHub: none")
                print(f"Activation: {patch.activation}")
                return 0

            for patch in store.list_sandbox_patches():
                print(
                    f"{patch.patch_id}\t{patch.code_proposal_id}\t"
                    f"{patch.status}\t{patch.activation}"
                )
            return 0

        if args.command == "tests":
            if not args.patch:
                print("Missing required --patch PATCH_ID")
                return 2
            try:
                test_run, test_result, evidence, chain = TestRunner(store).run_for_patch(
                    args.patch
                )
            except SandboxPatchNotFoundError as error:
                print(str(error))
                return 1
            print(f"TestRun created: {test_run.test_run_id}")
            print(f"TestResult: {test_result.test_result_id}")
            print(f"Evidence: {evidence.evidence_id}")
            print(f"EvidenceChain: {chain.evidence_chain_id}")
            print(f"Result: {test_result.result}")
            print("Command: sandbox_patch_static_check")
            print("Shell: none")
            print("Activation: blocked")
            return 0

        if args.command == "evidence":
            for evidence in store.list_evidence_records():
                print(
                    f"{evidence.evidence_id}\t{evidence.code_proposal_id}\t"
                    f"{evidence.evidence_type}\t{evidence.summary}"
                )
            return 0

        if args.command == "git":
            connector = LocalGitConnector(store, repo_path=args.repo)
            if args.action == "status":
                report = connector.status()
                print(f"GitStatus: {report.git_status_id}")
                print(f"Branch: {report.current_branch or 'unknown'}")
                print(f"Dirty: {str(report.dirty).lower()}")
                print(f"Head: {report.head_commit or 'unknown'}")
                print("Mode: read-only")
                return 0

            if not args.patch:
                print("Missing required --patch PATCH_ID")
                return 2
            try:
                preparation = connector.prepare_branch(args.patch)
            except (ValueError, DirtyGitTreeError) as error:
                print(str(error))
                return 1
            print(f"GitBranchPreparation: {preparation.git_preparation_id}")
            print(f"Patch: {preparation.patch_id}")
            print(f"Branch: {preparation.branch_name}")
            print(f"Status: {preparation.status}")
            print("Push: none")
            print("Merge: none")
            print(f"Activation: {preparation.activation}")
            return 0

        if args.command == "github":
            if not args.patch:
                print("Missing required --patch PATCH_ID")
                return 2
            try:
                draft_pr = GitHubConnector(store).draft_pr(
                    args.patch, repository=args.repository
                )
            except (
                SandboxPatchNotFoundError,
                GitHubBlockedError,
                GitHubPrerequisiteError,
            ) as error:
                print(str(error))
                return 1
            print(f"GitHubDraftPR: {draft_pr.github_draft_pr_id}")
            print(f"Patch: {draft_pr.patch_id}")
            print(f"Branch: {draft_pr.branch_name}")
            print(f"Repository: {draft_pr.repository}")
            print(f"Draft: {str(draft_pr.is_draft).lower()}")
            print(f"Status: {draft_pr.status}")
            print("Push: none")
            print("Merge: none")
            print(f"Activation: {draft_pr.activation}")
            return 0

        if args.command == "activation":
            boundary = ActivationBoundary(store)
            if args.action == "request":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    request, candidate, check = boundary.request(args.code_proposal)
                except (CodeChangeProposalNotFoundError, ActivationPrerequisiteError) as error:
                    print(str(error))
                    return 1
                print(f"ActivationRequest: {request.activation_request_id}")
                print(f"CodeProposal: {request.code_proposal_id}")
                print(f"ReactionSpecCandidate: {candidate.candidate_id}")
                print(f"RuntimeCompatibilityCheck: {check.compatibility_check_id}")
                print(f"Status: {request.status}")
                print(f"Reason: {request.reason_code}")
                print(f"Activation: {request.activation}")
                return 0

            if args.action == "reject":
                if not args.request:
                    print("Missing required --request REQUEST_ID")
                    return 2
                try:
                    decision = boundary.reject(args.request, args.rationale)
                except ActivationRequestNotFoundError as error:
                    print(str(error))
                    return 1
                print(f"ActivationDecision: {decision.activation_decision_id}")
                print(f"Request: {decision.activation_request_id}")
                print(f"Decision: {decision.decision}")
                print(f"Status: {decision.status}")
                print(f"Activation: {decision.activation}")
                return 0

            if args.action == "approve":
                if not args.request:
                    print("Missing required --request REQUEST_ID")
                    return 2
                try:
                    decision, activation, indexed_count = boundary.approve(args.request)
                except (ActivationRequestNotFoundError, ActivationApprovalError) as error:
                    print(str(error))
                    return 1
                print(f"ActivationDecision: {decision.activation_decision_id}")
                print(f"CapabilityActivation: {activation.capability_activation_id}")
                print(f"Request: {decision.activation_request_id}")
                print("Capability: index_memory")
                print(f"Status: {activation.status}")
                print(f"Activation: {activation.activation}")
                print(f"Backfilled: {indexed_count}")
                return 0

            for request in store.list_activation_requests():
                print(
                    f"{request.activation_request_id}\t{request.code_proposal_id}\t"
                    f"{request.status}\t{request.activation}"
                )
            return 0

        if args.command == "rollback":
            boundary = LifecycleBoundary(store)
            if args.action == "plan":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    plan = boundary.create_rollback_plan(args.code_proposal)
                except CodeChangeProposalNotFoundError as error:
                    print(str(error))
                    return 1
                print(f"RollbackPlan: {plan.rollback_plan_id}")
                print(f"CodeProposal: {plan.code_proposal_id}")
                print(f"Status: {plan.status}")
                print("Activation: blocked")
                return 0

            for plan in store.list_rollback_plans():
                print(f"{plan.rollback_plan_id}\t{plan.code_proposal_id}\t{plan.status}")
            return 0

        if args.command == "monitor":
            boundary = LifecycleBoundary(store)
            if args.action == "capability":
                if not args.code_proposal:
                    print("Missing required --code-proposal CODE_PROPOSAL_ID")
                    return 2
                try:
                    monitor = boundary.monitor(args.code_proposal)
                except CodeChangeProposalNotFoundError as error:
                    print(str(error))
                    return 1
                print(f"CapabilityMonitor: {monitor.monitor_id}")
                print(f"CodeProposal: {monitor.code_proposal_id}")
                print(f"Outcomes: {monitor.reaction_outcome_count}")
                print(f"Errors: {monitor.error_count}")
                print(f"BoundaryViolations: {monitor.boundary_violation_count}")
                print(f"UtilityScore: {monitor.utility_score}")
                print("Activation: blocked")
                return 0

            if args.action == "activation":
                if not args.request:
                    print("Missing required --request REQUEST_ID")
                    return 2
                try:
                    activation = boundary.record_activation_candidate(args.request)
                except (ActivationRequestNotFoundError, RollbackPlanRequiredError) as error:
                    print(str(error))
                    return 1
                print(f"CapabilityActivation: {activation.capability_activation_id}")
                print(f"Request: {activation.activation_request_id}")
                print(f"RollbackPlan: {activation.rollback_plan_id}")
                print(f"Status: {activation.status}")
                print(f"Activation: {activation.activation}")
                return 0

            for monitor in store.list_capability_monitors():
                print(
                    f"{monitor.monitor_id}\t{monitor.code_proposal_id}\t"
                    f"{monitor.utility_score}\t{monitor.status}"
                )
            return 0

        if args.command == "fossilize":
            boundary = LifecycleBoundary(store)
            if args.action == "record":
                if not args.source_kind or not args.source_id:
                    print("Missing required --source-kind KIND and --source-id ID")
                    return 2
                fossil = boundary.fossilize(
                    args.source_kind, args.source_id, args.reason
                )
                print(f"FossilRecord: {fossil.fossil_record_id}")
                print(f"Source: {fossil.source_kind}:{fossil.source_id}")
                print(f"Status: {fossil.status}")
                print("Activation: blocked")
                return 0

            for fossil in store.list_fossil_records():
                print(
                    f"{fossil.fossil_record_id}\t{fossil.source_kind}:"
                    f"{fossil.source_id}\t{fossil.status}"
                )
            return 0

        if args.command == "memory":
            if args.action == "index-status":
                indexer = MemoryIndexer(store)
                print(f"Active: {str(indexer.is_active()).lower()}")
                print(f"Memories: {len(store.list_memory_objects())}")
                print(f"Indexed: {len(store.list_memory_index_entries())}")
                return 0

            if not args.query:
                print("Missing required query")
                return 2
            results = MemorySearch(store).search(args.query)
            if not results:
                print("No memories found")
                return 0
            for result in results:
                print(
                    f"{result.memory.memory_id}\t{result.memory.content}\t"
                    f"match={result.match}"
                )
            return 0

        if args.command == "guide":
            if args.action == "memory-indexing":
                guide = MemoryIndexingGuide(store)
                print("Guide: memory-indexing")
                if guide.is_active():
                    print("Active: true")
                    print(f"Memories: {len(store.list_memory_objects())}")
                    print(f"Indexed: {len(store.list_memory_index_entries())}")
                    print(f'Next: genus-egg --db {args.db} memory search "term"')
                    return 0

                try:
                    preparation = guide.prepare()
                except (RuntimeError, ValueError) as error:
                    print(str(error))
                    return 1

                print(f"CapabilityNeed: {preparation.need.need_id}")
                print(f"CapabilityProposal: {preparation.proposal.proposal_id}")
                print(f"CodeProposal: {preparation.code_proposal.code_proposal_id}")
                print(f"ShadowTestPlan: {preparation.shadow_plan.shadow_plan_id}")
                print(f"FitnessEvaluation: {preparation.fitness_evaluation.evaluation_id}")
                print(f"PatchApproval: {preparation.patch_approval.approval_id}")
                print(f"SandboxPatch: {preparation.sandbox_patch.patch_id}")
                print(f"TestRun: {preparation.test_run.test_run_id}")
                print(f"EvidenceChain: {preparation.evidence_chain.evidence_chain_id}")
                print(f"RollbackPlan: {preparation.rollback_plan.rollback_plan_id}")
                print(
                    f"ActivationRequest: "
                    f"{preparation.activation_request.activation_request_id}"
                )
                print("Activation: blocked")
                try:
                    answer = input("Approve index_memory activation? [y/N] ")
                except EOFError:
                    answer = ""
                if answer.strip().lower() not in {"y", "yes"}:
                    print("Decision: skipped")
                    print("Activation: blocked")
                    print(
                        f"Next: genus-egg --db {args.db} activation approve "
                        f"--request {preparation.activation_request.activation_request_id}"
                    )
                    return 0

                try:
                    approval = guide.approve(
                        preparation.activation_request.activation_request_id
                    )
                except (RuntimeError, ValueError) as error:
                    print(str(error))
                    return 1

                print(f"ActivationDecision: {approval.decision.activation_decision_id}")
                print(
                    f"CapabilityActivation: "
                    f"{approval.activation.capability_activation_id}"
                )
                print("Capability: index_memory")
                print(f"Status: {approval.activation.status}")
                print(f"Activation: {approval.activation.activation}")
                print(f"Backfilled: {approval.indexed_count}")
                return 0

        return 2
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
