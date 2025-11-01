"""Core metrics for manufacturing optimisation."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def compute_makespan(schedule: pd.DataFrame) -> float:
    if schedule.empty:
        return 0.0
    end_times = pd.to_datetime(schedule["Scheduled_End"])
    start_times = pd.to_datetime(schedule["Scheduled_Start"])
    return float((end_times.max() - start_times.min()).total_seconds() / 60.0)


def compute_energy(schedule: pd.DataFrame) -> float:
    return float(schedule.get("Energy_Consumption", pd.Series(dtype=float)).sum())


def evaluate_schedule(schedule: pd.DataFrame) -> Dict[str, float]:
    return {
        "makespan": compute_makespan(schedule),
        "energy": compute_energy(schedule),
    }
