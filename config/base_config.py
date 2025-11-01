"""Configuration models for the RMS optimization framework.

This module centralises all experiment configuration objects.  The
models are implemented with `pydantic` to guarantee validation and
provide convenient serialisation / deserialisation helpers.  Each
configuration block mirrors one portion of the research plan described
in the project charter.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
import yaml


class DataConfig(BaseModel):
    """Configuration for the dataset layer."""

    sources: List[Path] = Field(default_factory=list, description="Input datasets")
    streaming: bool = Field(False, description="Enable streaming data ingestion")
    batch_size: int = Field(1024, ge=1, description="Batch size for streaming pipelines")
    cache_dir: Path = Field(Path("data/cache"))


class AlgorithmConfig(BaseModel):
    """Per-algorithm hyper-parameters and search spaces."""

    name: str = Field(..., description="Primary algorithm identifier")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    search_space: Dict[str, Any] = Field(default_factory=dict)
    seed: int = Field(42, description="Random seed for reproducibility")


class OptimizationConfig(BaseModel):
    """Multi-objective optimisation settings."""

    objectives: List[str] = Field(default_factory=lambda: ["makespan", "energy"])
    weights: Dict[str, float] = Field(default_factory=lambda: {"makespan": 0.5, "energy": 0.5})
    constraints: Dict[str, Any] = Field(default_factory=dict)
    pareto_front_size: int = Field(100, ge=1)

    @validator("weights")
    def validate_weights(cls, value: Dict[str, float]) -> Dict[str, float]:
        if not value:
            raise ValueError("At least one weight must be provided")
        total = sum(value.values())
        if total <= 0:
            raise ValueError("Weights must sum to a positive value")
        return value


class SimulationConfig(BaseModel):
    """Configuration of stochastic simulation parameters."""

    repetitions: int = Field(100, ge=1)
    enable_discrete_event: bool = Field(True)
    enable_monte_carlo: bool = Field(True)
    parallelism: int = Field(1, ge=1, description="Number of parallel workers")


class ValidationConfig(BaseModel):
    """Statistical validation parameters."""

    confidence_level: float = Field(0.95, ge=0.0, le=0.999)
    tests: List[str] = Field(default_factory=lambda: ["friedman", "wilcoxon"])
    replications: int = Field(30, ge=1)


class HardwareConfig(BaseModel):
    """Hardware and runtime resources."""

    use_gpu: bool = Field(False)
    num_cpus: int = Field(4, ge=1)
    memory_gb: int = Field(16, ge=1)


class LoggingConfig(BaseModel):
    """Experiment tracking and logging configuration."""

    experiment_name: str = Field("rms-optimization")
    tracking_uri: Optional[str] = Field(None, description="MLflow or W&B tracking URI")
    log_dir: Path = Field(Path("logs"))
    level: str = Field("INFO")


class ExperimentalConfig(BaseModel):
    """Master configuration object that aggregates all sections."""

    data: DataConfig = Field(default_factory=DataConfig)
    algorithm: AlgorithmConfig = Field(default_factory=lambda: AlgorithmConfig(name="fcfs"))
    optimisation: OptimizationConfig = Field(default_factory=OptimizationConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_file(cls, path: Path) -> "ExperimentalConfig":
        """Load configuration from a YAML or JSON file."""

        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return cls.parse_obj(data)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise configuration to a dictionary."""

        return self.dict()

    def save(self, path: Path) -> None:
        """Persist configuration to disk."""

        with Path(path).open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.to_dict(), handle)


def load_config(path: Optional[Path] = None, overrides: Optional[Dict[str, Any]] = None) -> ExperimentalConfig:
    """Utility wrapper to load and override configuration fields."""

    config = ExperimentalConfig.from_file(path) if path else ExperimentalConfig()
    if overrides:
        config = config.copy(update=overrides)
    return config
