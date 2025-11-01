"""Helper functions to work with experiment configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from config.base_config import ExperimentalConfig, load_config


class ConfigManager:
    """High level API to manage experiment configuration."""

    def __init__(self, config: Optional[ExperimentalConfig] = None) -> None:
        self._config = config or ExperimentalConfig()

    @property
    def config(self) -> ExperimentalConfig:
        return self._config

    @classmethod
    def from_file(cls, path: Path) -> "ConfigManager":
        return cls(load_config(path))

    def override(self, updates: Dict[str, Any]) -> None:
        self._config = self._config.copy(update=updates)
