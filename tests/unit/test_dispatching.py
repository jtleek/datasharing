from __future__ import annotations

import pandas as pd

from algorithms.classical.dispatching_rules import FCFSRule
from problems.job_shop import create_job_shop_problem


def test_fcfs_returns_sorted_schedule():
    data = pd.DataFrame(
        {
            "Job_ID": ["A", "B"],
            "Machine_ID": ["M1", "M1"],
            "Scheduled_Start": ["2023-01-01T09:00:00", "2023-01-01T08:00:00"],
            "Scheduled_End": ["2023-01-01T10:00:00", "2023-01-01T09:00:00"],
            "Processing_Time": [60, 60],
        }
    )
    problem = create_job_shop_problem(data)
    optimizer = FCFSRule()
    solution = optimizer.solve(problem)
    assert list(solution.schedule["Job_ID"]) == ["B", "A"]
