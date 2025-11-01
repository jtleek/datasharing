"""Hybrid optimisation placeholder."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class AdaptiveHybridOptimizer(BaseOptimizer):
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        return ScheduleSolution(schedule=problem.jobs, metrics={"status": "hybrid_stub"})
