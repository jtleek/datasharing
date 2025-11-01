"""Monte Carlo simulation helper."""
from __future__ import annotations

from typing import Callable

import numpy as np


class MonteCarloEngine:
    def __init__(self, repetitions: int) -> None:
        self.repetitions = repetitions

    def estimate(self, func: Callable[[], float]) -> float:
        samples = np.array([func() for _ in range(self.repetitions)])
        return float(samples.mean())
