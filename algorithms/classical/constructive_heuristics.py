"""Constructive heuristic stubs for early experimentation."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class NEHHeuristic(BaseOptimizer):
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        schedule = problem.jobs.sort_values("Processing_Time")
        return ScheduleSolution(schedule=schedule, metrics={"status": "heuristic_stub"})
