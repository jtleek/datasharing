"""Plotting utilities for experiments."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


def bar_performance(results: pd.DataFrame, metric: str, output: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(results["algorithm"], results[metric])
    ax.set_ylabel(metric)
    ax.set_xlabel("Algorithm")
    ax.set_title(f"Performance comparison on {metric}")
    ax.grid(True, axis="y", alpha=0.3)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)
    return output
