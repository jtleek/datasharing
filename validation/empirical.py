"""Empirical validation utilities."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats


def friedman_test(results: pd.DataFrame) -> Dict[str, float]:
    pivot = results.pivot(index="replication", columns="algorithm", values="makespan")
    statistic, pvalue = stats.friedmanchisquare(*pivot.T.values)
    return {"statistic": float(statistic), "p_value": float(pvalue)}


def confidence_interval(values: np.ndarray, level: float = 0.95) -> Dict[str, float]:
    mean = float(np.mean(values))
    sem = stats.sem(values)
    interval = stats.t.interval(level, len(values) - 1, loc=mean, scale=sem)
    return {"mean": mean, "lower": float(interval[0]), "upper": float(interval[1])}
