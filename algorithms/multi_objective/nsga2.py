"""Skeleton implementation of NSGA-II placeholder."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class NSGAII(BaseOptimizer):
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        return ScheduleSolution(schedule=problem.jobs, metrics={"status": "nsga2_stub"})
