"""Simplified simulated annealing skeleton."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class SimulatedAnnealing(BaseOptimizer):
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        return ScheduleSolution(schedule=problem.jobs.sample(frac=1.0, random_state=42), metrics={"status": "annealing_stub"})
