from __future__ import annotations

from dataclasses import dataclass

from genus_egg.evaluation.fitness_evaluation import FitnessEvaluation
from genus_egg.evaluation.shadow_test_plan import ShadowTestPlan


@dataclass(frozen=True)
class EvaluationReport:
    shadow_plan: ShadowTestPlan
    fitness_evaluation: FitnessEvaluation
    status: str
    activation: str
