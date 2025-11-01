"""Placeholder deep reinforcement learning scheduler."""
from __future__ import annotations

from core.base_optimizer import BaseOptimizer
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class DQNOptimizer(BaseOptimizer):
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        return ScheduleSolution(schedule=problem.jobs, metrics={"status": "dqn_stub"})
