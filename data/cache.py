"""Simple caching utilities for large datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import joblib
import pandas as pd


class DataCache:
    """Persist dataframes using joblib for quick reloads."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_or_compute(self, name: str, factory: Callable[[], pd.DataFrame]) -> pd.DataFrame:
        path = self.cache_dir / f"{name}.pkl"
        if path.exists():
            return joblib.load(path)
        dataframe = factory()
        joblib.dump(dataframe, path)
        return dataframe
