"""Abstract base classes for optimisation algorithms."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from core.problem import ManufacturingProblem
from core.solution import ScheduleSolution


class BaseOptimizer(ABC):
    """Base class every optimisation algorithm should derive from."""

    def __init__(self, **hyperparameters: Any) -> None:
        self.hyperparameters = hyperparameters

    @abstractmethod
    def solve(self, problem: ManufacturingProblem) -> ScheduleSolution:
        """Compute a solution for the provided manufacturing problem."""

    def info(self) -> Dict[str, Any]:
        """Return metadata describing the optimizer."""

        return {"name": self.__class__.__name__, "hyperparameters": self.hyperparameters}
