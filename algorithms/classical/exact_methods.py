"""Placeholder exact optimisation methods."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class BranchAndBound(BaseOptimizer):
    """Stub implementation returning the baseline schedule."""

    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        return ScheduleSolution(schedule=problem.jobs, metrics={"status": "not_implemented"})
