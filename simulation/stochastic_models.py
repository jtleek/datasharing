"""Stochastic models for manufacturing processes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class ProcessingTimeModel:
    distribution: Callable[[int], np.ndarray]

    def sample(self, size: int) -> np.ndarray:
        return self.distribution(size)
