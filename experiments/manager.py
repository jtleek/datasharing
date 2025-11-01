"""Experiment orchestration utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

import pandas as pd

from algorithms.classical.dispatching_rules import DISPATCHING_RULES
from config.base_config import ExperimentalConfig
from core.metrics import evaluate_schedule
from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


@dataclass
class ExperimentResult:
    algorithm: str
    metrics: Dict[str, float]


class ExperimentManager:
    """Coordinate data loading, algorithm execution, and metric logging."""

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config

    def run(self, problem: ManufacturingProblem) -> List[ExperimentResult]:
        results: List[ExperimentResult] = []
        for name, cls in DISPATCHING_RULES.items():
            optimizer = cls()
            solution = optimizer.solve(problem)
            results.append(ExperimentResult(algorithm=name, metrics=solution.metrics))
        return results

    def summarise(self, results: List[ExperimentResult]) -> pd.DataFrame:
        return pd.DataFrame([{"algorithm": r.algorithm, **r.metrics} for r in results])


def export_results(results: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(path, index=False)
