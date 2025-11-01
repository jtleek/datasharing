"""Implementation of classical dispatching rules."""
from __future__ import annotations

import pandas as pd

from core.base_optimizer import BaseOptimizer
from core.metrics import evaluate_schedule
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class DispatchingRule(BaseOptimizer):
    """Base class for dispatching rules."""

    rule_name: str = "dispatching_rule"

    def _priority(self, jobs: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        data = problem.jobs.copy()
        data["priority"] = self._priority(data)
        schedule = data.sort_values("priority").drop(columns=["priority"])
        return ScheduleSolution(schedule=schedule, metrics=evaluate_schedule(schedule))


class FCFSRule(DispatchingRule):
    rule_name = "fcfs"

    def _priority(self, jobs: pd.DataFrame) -> pd.Series:
        return pd.to_datetime(jobs["Scheduled_Start"]).rank(method="first")


class SPTRule(DispatchingRule):
    rule_name = "spt"

    def _priority(self, jobs: pd.DataFrame) -> pd.Series:
        return jobs["Processing_Time"].rank(method="first")


class LPTRule(DispatchingRule):
    rule_name = "lpt"

    def _priority(self, jobs: pd.DataFrame) -> pd.Series:
        return -jobs["Processing_Time"].rank(method="first")


DISPATCHING_RULES = {
    "fcfs": FCFSRule,
    "spt": SPTRule,
    "lpt": LPTRule,
}
