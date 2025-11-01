"""Entry point to execute baseline experiments."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from config.base_config import load_config
from core.config import ConfigManager
from data.loader import DataLoader, DataPreprocessor
from experiments.manager import ExperimentManager, export_results
from problems.job_shop import create_job_shop_problem
from reporting.generators import MarkdownReporter
from visualization.plots import bar_performance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RMS optimisation experiments")
    parser.add_argument("--config", type=Path, help="Path to configuration file", required=False)
    parser.add_argument("--output", type=Path, default=Path("results/experiments/baseline.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config) if args.config else load_config()
    manager = ConfigManager(config)

    loader = DataLoader()
    preprocessor = DataPreprocessor()
    data_sources = manager.config.data.sources or [Path("data/synthetic/sample.csv")]
    frames = [loader._load_single(source) for source in data_sources if Path(source).exists()]
    if frames:
        data = preprocessor.transform(pd.concat(frames, ignore_index=True))
    else:
        data = pd.DataFrame()
    problem = create_job_shop_problem(data)

    experiment_manager = ExperimentManager(manager.config)
    results = experiment_manager.run(problem)
    summary = experiment_manager.summarise(results)
    export_results(summary, args.output)

    if not summary.empty:
        bar_performance(summary, "makespan", Path("results/figures/makespan.png"))
        reporter = MarkdownReporter(Path("results/reports/summary.md"))
        reporter.render({"runs": len(summary)}, summary)


if __name__ == "__main__":
    main()
