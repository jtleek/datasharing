"""Synthetic data generation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Sequence
import numpy as np
import pandas as pd


@dataclass
class SyntheticScenario:
    """Scenario configuration for synthetic dataset creation."""

    num_jobs: int
    machines: Sequence[str]
    start_date: datetime
    time_between_jobs: timedelta


class SyntheticDataGenerator:
    """Generate synthetic manufacturing datasets."""

    def generate(self, scenario: SyntheticScenario) -> pd.DataFrame:
        rng = np.random.default_rng()
        timestamps = [
            scenario.start_date + i * scenario.time_between_jobs for i in range(scenario.num_jobs)
        ]
        machines = rng.choice(scenario.machines, size=scenario.num_jobs)
        processing_time = rng.integers(10, 240, size=scenario.num_jobs)
        energy = rng.normal(15, 5, size=scenario.num_jobs).clip(min=1)
        data = pd.DataFrame(
            {
                "Job_ID": [f"JOB_{i:05d}" for i in range(scenario.num_jobs)],
                "Machine_ID": machines,
                "Scheduled_Start": timestamps,
                "Scheduled_End": [ts + timedelta(minutes=int(pt)) for ts, pt in zip(timestamps, processing_time)],
                "Processing_Time": processing_time,
                "Energy_Consumption": energy,
            }
        )
        return data


class BenchmarkDataGenerator:
    """Placeholder for benchmark dataset retrieval."""

    def load_instances(self, names: Iterable[str]) -> List[pd.DataFrame]:
        return [pd.DataFrame({"instance": [name]}) for name in names]
