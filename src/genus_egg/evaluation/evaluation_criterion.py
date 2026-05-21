from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCriterion:
    name: str
    description: str


EVALUATION_CRITERIA = [
    EvaluationCriterion(
        name="safety_boundary_fit",
        description="Proposal keeps hard safety boundaries intact.",
    ),
    EvaluationCriterion(
        name="habitat_fit",
        description="Proposal fits the current closed Habitat permission profile.",
    ),
    EvaluationCriterion(
        name="test_plan_quality",
        description="Proposal carries a concrete and testable draft plan.",
    ),
    EvaluationCriterion(
        name="scope_control",
        description="Proposal scope is narrow and stays inside allowed paths.",
    ),
    EvaluationCriterion(
        name="memory_flow_benefit",
        description="Proposal can plausibly improve the memory flow.",
    ),
    EvaluationCriterion(
        name="rollback_readiness",
        description="Proposal can be discarded without runtime change.",
    ),
    EvaluationCriterion(
        name="activation_risk",
        description="Proposal keeps activation blocked.",
    ),
]
