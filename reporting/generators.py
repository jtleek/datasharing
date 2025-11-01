"""Automated reporting utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


class MarkdownReporter:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def render(self, metrics: Dict[str, float], table: pd.DataFrame) -> Path:
        lines = ["# Experiment Summary", "", "## Aggregate Metrics"]
        for key, value in metrics.items():
            lines.append(f"- **{key}**: {value:.3f}")
        lines.append("\n## Detailed Results")
        lines.append(table.to_markdown(index=False))
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text("\n".join(lines), encoding="utf-8")
        return self.output_path
