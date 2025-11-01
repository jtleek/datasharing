"""Data ingestion utilities for the RMS optimisation framework."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError


class DataSchema(BaseModel):
    """Minimal schema used to validate ingested datasets."""

    Job_ID: str
    Machine_ID: str
    Scheduled_Start: str
    Scheduled_End: str


class DataValidator:
    """Validate raw data sources using `pydantic` models."""

    def __init__(self, schema: type[BaseModel] = DataSchema) -> None:
        self.schema = schema

    def validate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        errors: List[str] = []
        for row in dataframe.to_dict(orient="records"):
            try:
                self.schema(**row)
            except ValidationError as exc:
                errors.append(str(exc))
        if errors:
            raise ValueError("Invalid dataset detected:\n" + "\n".join(errors[:5]))
        return dataframe


class DataLoader:
    """Load multiple dataset formats into pandas DataFrames."""

    def __init__(self, validator: Optional[DataValidator] = None) -> None:
        self.validator = validator or DataValidator()

    def load(self, sources: Iterable[Path], validate: bool = True) -> pd.DataFrame:
        frames: List[pd.DataFrame] = []
        for source in sources:
            frame = self._load_single(source)
            frames.append(frame)
        data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return self.validator.validate(data) if validate and not data.empty else data

    def _load_single(self, path: Path) -> pd.DataFrame:
        suffix = Path(path).suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path)
        if suffix in {".parquet", ".pq"}:
            return pd.read_parquet(path)
        if suffix in {".json"}:
            return pd.read_json(path)
        raise ValueError(f"Unsupported file format: {suffix}")


class DataPreprocessor:
    """Simple preprocessing utilities for baseline experiments."""

    datetime_columns: List[str] = ["Scheduled_Start", "Scheduled_End"]

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        for column in self.datetime_columns:
            if column in df:
                df[column] = pd.to_datetime(df[column])
        df = df.drop_duplicates()
        df = df.fillna(method="ffill").fillna(method="bfill")
        return df
