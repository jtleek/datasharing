"""Problem representations for RMS optimisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class ManufacturingProblem:
    """Encapsulate the data describing a scheduling instance."""

    jobs: pd.DataFrame
    objectives: List[str]
    constraints: Dict[str, float] = field(default_factory=dict)
    metadata: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        if not isinstance(self.jobs, pd.DataFrame):
            raise TypeError("jobs must be provided as a pandas DataFrame")
        if not self.objectives:
            raise ValueError("At least one objective must be specified")
