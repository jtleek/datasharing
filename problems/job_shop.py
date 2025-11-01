"""Job shop problem factory."""
from __future__ import annotations

import pandas as pd

from core.problem import ManufacturingProblem


def create_job_shop_problem(data: pd.DataFrame) -> ManufacturingProblem:
    objectives = ["makespan", "energy"]
    constraints = {"machine_capacity": 1.0}
    return ManufacturingProblem(jobs=data, objectives=objectives, constraints=constraints)
