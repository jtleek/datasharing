"""
Data transformation utilities for AI-ready formats
"""
import pandas as pd
import json
from typing import Any, Dict, List, Optional
from io import StringIO, BytesIO
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transform data into various AI-ready formats
    """

    @staticmethod
    def to_json(data: Any, pretty: bool = False) -> str:
        """
        Convert data to JSON format

        Args:
            data: Input data
            pretty: Pretty print JSON

        Returns:
            JSON string
        """
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient="records", indent=2 if pretty else None)
        else:
            return json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)

    @staticmethod
    def to_csv(data: Any) -> str:
        """
        Convert data to CSV format

        Args:
            data: Input data (dict, list of dicts, or DataFrame)

        Returns:
            CSV string
        """
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
            return df.to_csv(index=False)
        else:
            raise ValueError("Unsupported data type for CSV conversion")

    @staticmethod
    def to_parquet(data: Any) -> bytes:
        """
        Convert data to Parquet format (optimized for AI/ML)

        Args:
            data: Input data

        Returns:
            Parquet bytes
        """
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported data type for Parquet conversion")

        buffer = BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        return buffer.getvalue()

    @staticmethod
    def clean_dataset(data: Any) -> pd.DataFrame:
        """
        Clean dataset for AI training

        - Remove duplicates
        - Handle missing values
        - Standardize column names
        - Remove empty columns

        Args:
            data: Input data

        Returns:
            Cleaned DataFrame
        """
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported data type")

        # Standardize column names (lowercase, replace spaces with underscores)
        df.columns = [
            col.lower().replace(" ", "_").replace("-", "_") for col in df.columns
        ]

        # Remove completely empty columns
        df = df.dropna(axis=1, how="all")

        # Remove duplicate rows
        df = df.drop_duplicates()

        # Fill missing numeric values with 0, strings with empty string
        for col in df.columns:
            if df[col].dtype in ["float64", "int64"]:
                df[col].fillna(0, inplace=True)
            elif df[col].dtype == "object":
                df[col].fillna("", inplace=True)

        return df

    @staticmethod
    def get_data_quality_metrics(data: Any) -> Dict[str, Any]:
        """
        Calculate data quality metrics

        Args:
            data: Input data

        Returns:
            Dictionary with quality metrics
        """
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])

        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0

        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "completeness_score": round(completeness, 3),
            "missing_values": int(missing_cells),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "column_types": df.dtypes.astype(str).to_dict(),
        }

    @staticmethod
    def sample_data(data: Any, n: int = 100) -> Any:
        """
        Sample data for preview

        Args:
            data: Input data
            n: Number of samples

        Returns:
            Sampled data
        """
        if isinstance(data, pd.DataFrame):
            return data.head(n)
        elif isinstance(data, list):
            return data[:n]
        else:
            return data

    @staticmethod
    def normalize_brazilian_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply Brazilian-specific data normalizations

        - Clean CPF/CNPJ formats
        - Normalize date formats
        - Clean currency values

        Args:
            df: Input DataFrame

        Returns:
            Normalized DataFrame
        """
        df = df.copy()

        # Clean CPF/CNPJ (remove dots and dashes)
        for col in df.columns:
            if "cpf" in col.lower() or "cnpj" in col.lower():
                if df[col].dtype == "object":
                    df[col] = df[col].str.replace(r"[.\-/]", "", regex=True)

        # Clean currency values (R$ format)
        for col in df.columns:
            if "valor" in col.lower() or "preco" in col.lower() or "custo" in col.lower():
                if df[col].dtype == "object":
                    # Remove R$, dots (thousand separator), replace comma with dot
                    df[col] = (
                        df[col]
                        .str.replace("R$", "", regex=False)
                        .str.replace(".", "", regex=False)
                        .str.replace(",", ".", regex=False)
                        .str.strip()
                    )
                    # Convert to float
                    try:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    except:
                        pass

        return df
