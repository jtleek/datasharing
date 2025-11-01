"""Theoretical validation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ComplexityAnalysis:
    algorithm: str
    time_complexity: str
    space_complexity: str


def document_complexity(algorithm: str, time_complexity: str, space_complexity: str) -> Dict[str, str]:
    return {
        "algorithm": algorithm,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
    }
