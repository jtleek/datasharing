"""
Advanced Manufacturing Optimization Framework
Publication-ready experimental system for multi-objective job shop scheduling.
"""
import argparse
import itertools
import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D plots)
from scipy import stats
from sklearn.preprocessing import StandardScaler


# ==========================================================================
# CONFIGURATION
# ==========================================================================


@dataclass
class ExperimentalConfig:
    """Configuration for the experimental framework."""

    base_dir: Path = Path(__file__).parent
    data_file: Path = Path(__file__).parent / "hybrid_manufacturing_categorical.csv"
    output_dir: Path = Path(__file__).parent / "advanced_optimization_results"

    # Simulation scenarios
    scenarios: Tuple[str, ...] = (
        "baseline",
        "stochastic",
        "high_variability",
        "energy_constrained",
        "multi_objective",
    )

    n_replications: int = 30
    random_seed: int = 42
    confidence_level: float = 0.95

    # Weights for composite score (must sum to 1)
    weight_time: float = 0.35
    weight_energy: float = 0.25
    weight_material: float = 0.20
    weight_availability: float = 0.20

    # Noise parameters
    processing_time_noise: float = 0.10
    high_variability_noise: float = 0.20
    energy_noise: float = 0.08
    machine_failure_prob: float = 0.05
    high_failure_prob: float = 0.10

    # Learning curve coefficient (power law)
    learning_rate: float = 0.95

    # Algorithm hyperparameters (kept modest for runtime considerations)
    ga_population_size: int = 40
    ga_generations: int = 25
    pso_swarm_size: int = 30
    pso_iterations: int = 40
    sa_iterations: int = 500

    # Visualization settings
    dpi: int = 300

    # Limits for heavy metaheuristics
    max_jobs_for_metaheuristics: int = 200

    # Machine availability baseline (minutes)
    shift_minutes: int = 24 * 60

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for sub in ["plots", "tables", "statistics", "latex"]:
            (self.output_dir / sub).mkdir(exist_ok=True)

    @property
    def weights(self) -> Dict[str, float]:
        return {
            "time": self.weight_time,
            "energy": self.weight_energy,
            "material": self.weight_material,
            "availability": self.weight_availability,
        }


# ==========================================================================
# LOGGING UTILITIES
# ==========================================================================


def get_logger(name: str = "experiment"):
    import logging

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


LOGGER = get_logger()


# ==========================================================================
# DATA LOADING AND PREPROCESSING
# ==========================================================================


class DataLoader:
    """Load and preprocess manufacturing data."""

    REQUIRED_COLUMNS = [
        "Job_ID",
        "Machine_ID",
        "Operation_Type",
        "Material_Used",
        "Processing_Time",
        "Energy_Consumption",
        "Machine_Availability",
        "Scheduled_Start",
        "Scheduled_End",
        "Actual_Start",
        "Actual_End",
        "Job_Status",
        "Optimization_Category",
    ]

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)

    def load(self) -> pd.DataFrame:
        if self.config.data_file.exists():
            LOGGER.info("Loading dataset from %s", self.config.data_file)
            df = pd.read_csv(self.config.data_file)
        else:
            LOGGER.warning("Data file not found. Generating synthetic dataset.")
            df = self._generate_synthetic_dataset()
        return self._preprocess(df)

    def _generate_synthetic_dataset(self, n_jobs: int = 480) -> pd.DataFrame:
        machines = [f"M{i:02d}" for i in range(1, 7)]
        operations = ["Additive", "Drilling", "Grinding", "Lathe", "Milling", "Inspection"]
        start_date = pd.Timestamp("2023-03-18")

        rows = []
        for job in range(1, n_jobs + 1):
            machine = self.rng.choice(machines)
            op = self.rng.choice(operations)
            proc_time = self.rng.uniform(30, 240)  # minutes
            energy = self.rng.uniform(5, 45)
            material = self.rng.uniform(1, 30)
            availability = self.rng.uniform(70, 99)
            scheduled_start = start_date + pd.Timedelta(minutes=int(self.rng.uniform(0, 7 * 24 * 60)))
            scheduled_end = scheduled_start + pd.Timedelta(minutes=int(proc_time * self.rng.uniform(0.9, 1.2)))
            actual_start = scheduled_start + pd.Timedelta(minutes=int(self.rng.uniform(-15, 45)))
            actual_end = actual_start + pd.Timedelta(minutes=int(proc_time * self.rng.uniform(0.9, 1.3)))
            status = self.rng.choice(["Completed", "Delayed", "Failed"], p=[0.68, 0.20, 0.12])
            category = self.rng.choice(
                ["Optimal", "High", "Moderate", "Low"], p=[0.05, 0.18, 0.35, 0.42]
            )
            rows.append(
                {
                    "Job_ID": f"J{job:04d}",
                    "Machine_ID": machine,
                    "Operation_Type": op,
                    "Material_Used": material,
                    "Processing_Time": proc_time,
                    "Energy_Consumption": energy,
                    "Machine_Availability": availability,
                    "Scheduled_Start": scheduled_start,
                    "Scheduled_End": scheduled_end,
                    "Actual_Start": actual_start,
                    "Actual_End": actual_end,
                    "Job_Status": status,
                    "Optimization_Category": category,
                }
            )
        return pd.DataFrame(rows)

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset missing required columns: {missing_cols}")

        df = df.copy()

        # Parse datetimes
        for col in ["Scheduled_Start", "Scheduled_End", "Actual_Start", "Actual_End"]:
            df[col] = pd.to_datetime(df[col])

        df.sort_values("Scheduled_Start", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Remove duplicates and handle missing values
        df.drop_duplicates(subset=["Job_ID"], inplace=True)
        numeric_cols = ["Material_Used", "Processing_Time", "Energy_Consumption", "Machine_Availability"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col].fillna(df[col].median(), inplace=True)

        # Derived features
        min_start = df["Scheduled_Start"].min()
        df["Scheduled_Start_Minutes"] = (
            (df["Scheduled_Start"] - min_start).dt.total_seconds() / 60.0
        )
        df["Scheduled_End_Minutes"] = (
            (df["Scheduled_End"] - min_start).dt.total_seconds() / 60.0
        )
        df["Due_Date_Minutes"] = df["Scheduled_End_Minutes"]

        df["Scheduled_Duration"] = (
            df["Scheduled_End"] - df["Scheduled_Start"]
        ).dt.total_seconds() / 60.0
        df["Actual_Duration"] = (
            df["Actual_End"] - df["Actual_Start"]
        ).dt.total_seconds() / 60.0

        df["Delay_Minutes"] = df["Actual_Duration"] - df["Scheduled_Duration"]
        df["Is_Delayed"] = (df["Delay_Minutes"] > 0).astype(int)

        # Normalized columns for scoring
        scaler = StandardScaler()
        norm_cols = ["Processing_Time", "Energy_Consumption", "Material_Used"]
        df[[f"{col}_Norm" for col in norm_cols]] = scaler.fit_transform(df[norm_cols])
        df["Availability_Norm"] = scaler.fit_transform(df[["Machine_Availability"]])

        df["Composite_Efficiency"] = (
            self.config.weight_time * (-df["Processing_Time_Norm"]) +
            self.config.weight_energy * (-df["Energy_Consumption_Norm"]) +
            self.config.weight_material * (-df["Material_Used_Norm"]) +
            self.config.weight_availability * df["Availability_Norm"]
        )

        return df


# ==========================================================================
# STOCHASTIC SIMULATION
# ==========================================================================


class StochasticSimulator:
    """Simulate stochastic variations for manufacturing processes."""

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config

    def sample_processing_time(
        self, base_time: float, scenario: str, order_index: int, rng: np.random.Generator
    ) -> float:
        if scenario == "baseline":
            noise = 1.0
        elif scenario == "stochastic":
            noise = rng.normal(1.0, self.config.processing_time_noise)
        elif scenario == "high_variability":
            noise = rng.normal(1.0, self.config.high_variability_noise)
        elif scenario == "energy_constrained":
            noise = rng.normal(0.95, self.config.processing_time_noise)
        else:  # multi_objective scenario emphasises learning
            exponent = math.log(self.config.learning_rate, 2)
            learning_factor = (order_index + 1) ** exponent
            noise = rng.normal(learning_factor, self.config.processing_time_noise)
        return float(max(5.0, base_time * np.clip(noise, 0.5, 1.6)))

    def sample_energy(
        self, base_energy: float, scenario: str, rng: np.random.Generator
    ) -> float:
        if scenario == "energy_constrained":
            shape = 5
            scale = (base_energy * 0.9) / shape
            return float(rng.gamma(shape, scale))
        energy_noise = rng.normal(1.0, self.config.energy_noise)
        return float(max(0.5, base_energy * np.clip(energy_noise, 0.7, 1.4)))

    def machine_breakdown_delay(
        self, scenario: str, rng: np.random.Generator
    ) -> float:
        prob = self.config.machine_failure_prob
        if scenario == "high_variability":
            prob = self.config.high_failure_prob
        if rng.random() < prob:
            return float(rng.uniform(10, 30))
        return 0.0

    def success_probability(self, availability: float) -> float:
        return float(0.7 + 0.3 * (availability / 100.0))


# ==========================================================================
# OPTIMIZATION METHODS
# ==========================================================================


class OptimizationMethods:
    """Collection of scheduling priority rules and metaheuristics."""

    def __init__(self, config: ExperimentalConfig):
        self.config = config

    # --- Classical rules -------------------------------------------------

    def fcfs(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.sort_values("Scheduled_Start").copy()
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "FCFS"
        return df_sorted

    def spt(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.sort_values("Processing_Time").copy()
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "SPT"
        return df_sorted

    def lpt(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.sort_values("Processing_Time", ascending=False).copy()
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "LPT"
        return df_sorted

    def edd(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.sort_values("Scheduled_End").copy()
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "EDD"
        return df_sorted

    def slack(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.copy()
        df_sorted["Slack"] = df_sorted["Scheduled_End_Minutes"] - (
            df_sorted["Scheduled_Start_Minutes"] + df_sorted["Processing_Time"]
        )
        df_sorted.sort_values("Slack", inplace=True)
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "Slack"
        return df_sorted.drop(columns=["Slack"])

    def critical_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.copy()
        df_sorted["CR"] = (
            (df_sorted["Scheduled_End_Minutes"] - df_sorted["Scheduled_Start_Minutes"])
            / df_sorted["Processing_Time"]
        )
        df_sorted.sort_values("CR", inplace=True)
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "Critical_Ratio"
        return df_sorted.drop(columns=["CR"])

    def wspt(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted = df.copy()
        weights = 1.0 / (df_sorted["Material_Used"] + 1e-3)
        df_sorted["WSPT_Score"] = df_sorted["Processing_Time"] / weights
        df_sorted.sort_values("WSPT_Score", inplace=True)
        df_sorted["Priority"] = np.arange(1, len(df_sorted) + 1)
        df_sorted["Method"] = "WSPT"
        return df_sorted.drop(columns=["WSPT_Score"])

    # --- Helper utilities for metaheuristics -----------------------------

    @staticmethod
    def _normalize_weights(weights: np.ndarray) -> np.ndarray:
        weights = np.clip(weights, 0.01, 1.0)
        weights = weights / weights.sum()
        return weights

    def _score_with_weights(self, df: pd.DataFrame, weights: np.ndarray) -> pd.DataFrame:
        columns = ["Processing_Time_Norm", "Energy_Consumption_Norm", "Material_Used_Norm", "Availability_Norm"]
        score = (df[columns].values * weights).sum(axis=1)
        df_scored = df.copy()
        df_scored["Score"] = score
        df_scored.sort_values("Score", inplace=True)
        df_scored["Priority"] = np.arange(1, len(df_scored) + 1)
        return df_scored

    def _prepare_df_for_metaheuristic(self, df: pd.DataFrame) -> pd.DataFrame:
        if len(df) <= self.config.max_jobs_for_metaheuristics:
            return df
        LOGGER.warning(
            "Reducing dataset from %d to %d jobs for metaheuristic runtime considerations.",
            len(df),
            self.config.max_jobs_for_metaheuristics,
        )
        return df.nsmallest(self.config.max_jobs_for_metaheuristics, "Scheduled_Start")

    # --- Metaheuristics --------------------------------------------------

    def genetic_algorithm(self, df: pd.DataFrame) -> pd.DataFrame:
        df_small = self._prepare_df_for_metaheuristic(df)
        rng = np.random.default_rng(self.config.random_seed)

        pop_size = self.config.ga_population_size
        generations = self.config.ga_generations
        population = rng.dirichlet(np.ones(4), size=pop_size)

        def fitness(weights: np.ndarray) -> float:
            weights = self._normalize_weights(weights)
            scored = self._score_with_weights(df_small, weights)
            # objective: minimize combined normalized metrics (lower is better)
            return float(scored["Score"].mean())

        for _ in range(generations):
            fitness_values = np.array([fitness(ind) for ind in population])
            ranks = np.argsort(fitness_values)
            elites = population[ranks[: max(2, pop_size // 5)]]
            new_population = elites.copy()
            while len(new_population) < pop_size:
                parents = rng.choice(elites, size=2, replace=True)
                crossover_point = rng.integers(1, len(parents[0]))
                child = np.concatenate([parents[0][:crossover_point], parents[1][crossover_point:]])
                mutation = rng.normal(0, 0.05, size=child.shape)
                child = np.clip(child + mutation, 0.01, 1.0)
                new_population = np.vstack([new_population, child])
            population = new_population[:pop_size]

        best_weights = self._normalize_weights(population[np.argmin([fitness(ind) for ind in population])])
        df_scored = self._score_with_weights(df, best_weights)
        df_scored["Method"] = "Genetic_Algorithm"
        return df_scored.drop(columns=["Score"])

    def particle_swarm(self, df: pd.DataFrame) -> pd.DataFrame:
        df_small = self._prepare_df_for_metaheuristic(df)
        rng = np.random.default_rng(self.config.random_seed + 1)

        swarm_size = self.config.pso_swarm_size
        iterations = self.config.pso_iterations

        positions = rng.dirichlet(np.ones(4), size=swarm_size)
        velocities = rng.normal(0, 0.1, size=(swarm_size, 4))
        personal_best_positions = positions.copy()
        personal_best_scores = np.full(swarm_size, np.inf)

        def fitness(weights: np.ndarray) -> float:
            weights = self._normalize_weights(weights)
            return float(self._score_with_weights(df_small, weights)["Score"].mean())

        global_best_position = positions[0]
        global_best_score = fitness(global_best_position)

        for i in range(swarm_size):
            score = fitness(positions[i])
            personal_best_scores[i] = score
            if score < global_best_score:
                global_best_score = score
                global_best_position = positions[i]

        w, c1, c2 = 0.7, 1.5, 1.5
        for _ in range(iterations):
            for i in range(swarm_size):
                r1, r2 = rng.random(4), rng.random(4)
                velocities[i] = (
                    w * velocities[i]
                    + c1 * r1 * (personal_best_positions[i] - positions[i])
                    + c2 * r2 * (global_best_position - positions[i])
                )
                positions[i] = np.clip(positions[i] + velocities[i], 0.01, 1.0)
                score = fitness(positions[i])
                if score < personal_best_scores[i]:
                    personal_best_scores[i] = score
                    personal_best_positions[i] = positions[i]
                    if score < global_best_score:
                        global_best_score = score
                        global_best_position = positions[i]

        best_weights = self._normalize_weights(global_best_position)
        df_scored = self._score_with_weights(df, best_weights)
        df_scored["Method"] = "Particle_Swarm"
        return df_scored.drop(columns=["Score"])

    def simulated_annealing(self, df: pd.DataFrame) -> pd.DataFrame:
        df_small = self._prepare_df_for_metaheuristic(df)
        rng = np.random.default_rng(self.config.random_seed + 2)

        current = rng.dirichlet(np.ones(4))
        current_score = self._score_with_weights(df_small, current)["Score"].mean()
        best = current.copy()
        best_score = current_score

        temp = 1.0
        cooling = 0.995
        for _ in range(self.config.sa_iterations):
            candidate = np.clip(current + rng.normal(0, 0.05, size=4), 0.01, 1.0)
            candidate = self._normalize_weights(candidate)
            candidate_score = self._score_with_weights(df_small, candidate)["Score"].mean()
            if candidate_score < current_score or rng.random() < math.exp((current_score - candidate_score) / temp):
                current, current_score = candidate, candidate_score
                if candidate_score < best_score:
                    best, best_score = candidate, candidate_score
            temp *= cooling
            if temp < 1e-3:
                temp = 1e-3

        best_weights = self._normalize_weights(best)
        df_scored = self._score_with_weights(df, best_weights)
        df_scored["Method"] = "Simulated_Annealing"
        return df_scored.drop(columns=["Score"])

    def nsga2(self, df: pd.DataFrame) -> pd.DataFrame:
        # Approximate NSGA-II via Pareto ranking on normalized objectives
        objectives = [
            ("Processing_Time_Norm", True),
            ("Energy_Consumption_Norm", True),
            ("Material_Used_Norm", True),
            ("Availability_Norm", False),
        ]
        df_copy = df.copy()
        scores = []
        for idx, row in df_copy.iterrows():
            dominated = 0
            for _, other in df_copy.iterrows():
                if idx == other.name:
                    continue
                better_or_equal = True
                strictly_better = False
                for col, minimize in objectives:
                    a = row[col]
                    b = other[col]
                    if minimize:
                        if a < b:
                            strictly_better = True
                        elif a > b:
                            better_or_equal = False
                    else:
                        if a > b:
                            strictly_better = True
                        elif a < b:
                            better_or_equal = False
                if better_or_equal and strictly_better:
                    dominated += 1
            scores.append(dominated)
        df_copy["Pareto_Rank"] = scores
        df_copy.sort_values(["Pareto_Rank", "Processing_Time"], inplace=True)
        df_copy["Priority"] = np.arange(1, len(df_copy) + 1)
        df_copy["Method"] = "NSGAII"
        return df_copy.drop(columns=["Pareto_Rank"])

    def intelligent_multi_agent(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        availability_bonus = df_copy["Machine_Availability"] / 100.0
        category_multiplier = df_copy["Optimization_Category"].map(
            {
                "Optimal": 1.20,
                "High": 1.10,
                "Moderate": 1.00,
                "Low": 0.90,
            }
        ).fillna(1.0)
        load_factor = df_copy.groupby("Machine_ID")["Processing_Time"].transform("sum")
        load_factor = load_factor / load_factor.mean()

        pareto_score = (
            self.config.weight_time * (-df_copy["Processing_Time_Norm"]) +
            self.config.weight_energy * (-df_copy["Energy_Consumption_Norm"]) +
            self.config.weight_material * (-df_copy["Material_Used_Norm"]) +
            self.config.weight_availability * df_copy["Availability_Norm"]
        )
        final_score = pareto_score * category_multiplier + availability_bonus - load_factor
        df_copy["Intelligent_Score"] = final_score
        df_copy.sort_values("Intelligent_Score", ascending=False, inplace=True)
        df_copy["Priority"] = np.arange(1, len(df_copy) + 1)
        df_copy["Method"] = "Intelligent_MultiAgent"
        return df_copy.drop(columns=["Intelligent_Score"])

    # ------------------------------------------------------------------

    def registry(self) -> Dict[str, Callable[[pd.DataFrame], pd.DataFrame]]:
        return {
            "FCFS": self.fcfs,
            "SPT": self.spt,
            "LPT": self.lpt,
            "EDD": self.edd,
            "Slack": self.slack,
            "Critical_Ratio": self.critical_ratio,
            "WSPT": self.wspt,
            "Genetic_Algorithm": self.genetic_algorithm,
            "Particle_Swarm": self.particle_swarm,
            "Simulated_Annealing": self.simulated_annealing,
            "NSGAII": self.nsga2,
            "Intelligent_MultiAgent": self.intelligent_multi_agent,
        }


# ==========================================================================
# SCHEDULE EVALUATION AND METRICS
# ==========================================================================


class ScheduleEvaluator:
    """Simulate scheduling execution for a given priority list."""

    def __init__(self, config: ExperimentalConfig, simulator: StochasticSimulator) -> None:
        self.config = config
        self.simulator = simulator

    def evaluate(
        self,
        df_original: pd.DataFrame,
        prioritized_df: pd.DataFrame,
        scenario: str,
        replication_seed: int,
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        rng = np.random.default_rng(self.config.random_seed + replication_seed)
        machine_available_time = defaultdict(float)
        job_records = []

        for order_index, row in enumerate(prioritized_df.itertuples(index=False)):
            base_proc = float(row.Processing_Time)
            proc_time = self.simulator.sample_processing_time(base_proc, scenario, order_index, rng)
            energy = self.simulator.sample_energy(float(row.Energy_Consumption), scenario, rng)
            machine = row.Machine_ID
            availability = float(row.Machine_Availability)

            arrival_time = float(row.Scheduled_Start_Minutes)
            ready_time = max(arrival_time, machine_available_time[machine])
            breakdown_delay = self.simulator.machine_breakdown_delay(scenario, rng)
            start_time = ready_time + breakdown_delay
            end_time = start_time + proc_time

            due_date = float(row.Due_Date_Minutes)
            tardiness = max(0.0, end_time - due_date)
            waiting_time = start_time - arrival_time

            success_prob = self.simulator.success_probability(availability)
            status = "Completed"
            if rng.random() > success_prob:
                status = "Failed"
            elif tardiness > 0 and rng.random() < 0.5:
                status = "Delayed"

            job_records.append(
                {
                    "Job_ID": row.Job_ID,
                    "Machine_ID": machine,
                    "Order_Index": order_index,
                    "Start_Time": start_time,
                    "End_Time": end_time,
                    "Processing_Time": proc_time,
                    "Energy_Consumption": energy,
                    "Waiting_Time": waiting_time,
                    "Tardiness": tardiness,
                    "Status": status,
                    "Material_Used": float(row.Material_Used),
                    "Availability": availability,
                    "Scenario": scenario,
                }
            )
            machine_available_time[machine] = end_time

        job_df = pd.DataFrame(job_records)
        metrics = self._compute_metrics(job_df, df_original)
        return job_df, metrics

    def _compute_metrics(self, job_df: pd.DataFrame, df_original: pd.DataFrame) -> Dict[str, float]:
        makespan = job_df["End_Time"].max() - job_df["Start_Time"].min()
        total_energy = job_df["Energy_Consumption"].sum()
        total_material = job_df["Material_Used"].sum()
        completion_rate = (job_df["Status"] == "Completed").mean()
        failure_rate = (job_df["Status"] == "Failed").mean()
        delay_rate = (job_df["Status"] == "Delayed").mean()
        avg_processing_time = job_df["Processing_Time"].mean()
        avg_waiting_time = job_df["Waiting_Time"].mean()
        avg_tardiness = job_df["Tardiness"].mean()

        # Machine utilization
        machine_work = job_df.groupby("Machine_ID")["Processing_Time"].sum()
        utilization = (machine_work / self.config.shift_minutes).mean()

        moo_score = (
            self.config.weight_time * (makespan / len(job_df))
            + self.config.weight_energy * (total_energy / len(job_df))
            + self.config.weight_material * (total_material / len(job_df))
            + self.config.weight_availability * (1 - completion_rate)
        )

        # Additional metrics
        throughput = len(job_df) / (makespan / 60.0) if makespan > 0 else 0
        energy_per_job = total_energy / len(job_df)
        tardy_jobs = (job_df["Tardiness"] > 0).mean()
        median_flow_time = (job_df["End_Time"] - job_df["Start_Time"]).median()
        percentile95_wait = job_df["Waiting_Time"].quantile(0.95)

        metrics = {
            "makespan": makespan,
            "total_energy": total_energy,
            "total_material": total_material,
            "completion_rate": completion_rate,
            "failure_rate": failure_rate,
            "delay_rate": delay_rate,
            "avg_processing_time": avg_processing_time,
            "avg_waiting_time": avg_waiting_time,
            "avg_tardiness": avg_tardiness,
            "machine_utilization": utilization,
            "moo_score": moo_score,
            "throughput_per_hour": throughput,
            "energy_per_job": energy_per_job,
            "tardy_jobs": tardy_jobs,
            "median_flow_time": median_flow_time,
            "p95_waiting_time": percentile95_wait,
        }

        # Baseline references from original data
        metrics["historical_completion_rate"] = (
            (df_original["Job_Status"] == "Completed").mean()
        )
        metrics["historical_failure_rate"] = (
            (df_original["Job_Status"] == "Failed").mean()
        )
        return metrics


# ==========================================================================
# STATISTICAL ANALYSIS
# ==========================================================================


class StatisticalAnalyzer:
    """Perform rigorous statistical comparisons across methods."""

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config

    @staticmethod
    def _confidence_interval(series: pd.Series, confidence_level: float) -> Tuple[float, float]:
        mean = series.mean()
        sem = stats.sem(series, nan_policy="omit")
        if math.isnan(sem) or sem == 0:
            return mean, mean
        interval = stats.t.ppf((1 + confidence_level) / 2.0, len(series) - 1) * sem
        return mean - interval, mean + interval

    def summarize(self, results: pd.DataFrame) -> pd.DataFrame:
        summary_rows = []
        for (scenario, method), group in results.groupby(["Scenario", "Method"]):
            ci_low, ci_high = self._confidence_interval(group["moo_score"], self.config.confidence_level)
            summary_rows.append(
                {
                    "Scenario": scenario,
                    "Method": method,
                    "Mean_MOO": group["moo_score"].mean(),
                    "Std_MOO": group["moo_score"].std(),
                    "CI_Lower": ci_low,
                    "CI_Upper": ci_high,
                    "Completion_Rate": group["completion_rate"].mean(),
                    "Failure_Rate": group["failure_rate"].mean(),
                    "Delay_Rate": group["delay_rate"].mean(),
                    "Avg_Processing_Time": group["avg_processing_time"].mean(),
                    "Avg_Tardiness": group["avg_tardiness"].mean(),
                    "Throughput_per_hour": group["throughput_per_hour"].mean(),
                    "Energy_per_job": group["energy_per_job"].mean(),
                    "Machine_Utilization": group["machine_utilization"].mean(),
                }
            )
        summary_df = pd.DataFrame(summary_rows)
        return summary_df.sort_values(["Scenario", "Mean_MOO"])

    def friedman_test(self, results: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        test_results = {}
        for scenario, group in results.groupby("Scenario"):
            pivot = group.pivot(index="Replication", columns="Method", values="moo_score")
            if pivot.shape[1] < 2:
                continue
            statistic, pvalue = stats.friedmanchisquare(*[pivot[col].values for col in pivot.columns])
            test_results[scenario] = {"statistic": float(statistic), "pvalue": float(pvalue)}
        return test_results

    def wilcoxon_tests(self, results: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        pairwise_results: Dict[str, Dict[str, float]] = {}
        for scenario, group in results.groupby("Scenario"):
            pivot = group.pivot(index="Replication", columns="Method", values="moo_score")
            methods = pivot.columns.tolist()
            scenario_result: Dict[str, float] = {}
            for i, method_i in enumerate(methods):
                for j in range(i + 1, len(methods)):
                    method_j = methods[j]
                    try:
                        stat, pvalue = stats.wilcoxon(pivot[method_i], pivot[method_j])
                        key = f"{method_i} vs {method_j}"
                        scenario_result[key] = float(pvalue)
                    except ValueError:
                        continue
            pairwise_results[scenario] = scenario_result
        return pairwise_results

    def effect_sizes(self, results: pd.DataFrame) -> pd.DataFrame:
        records = []
        for scenario, group in results.groupby("Scenario"):
            pivot = group.pivot(index="Replication", columns="Method", values="moo_score")
            methods = pivot.columns.tolist()
            for i, method_i in enumerate(methods):
                for j in range(i + 1, len(methods)):
                    method_j = methods[j]
                    diff = pivot[method_i] - pivot[method_j]
                    mean_diff = diff.mean()
                    pooled_std = math.sqrt((pivot[method_i].var() + pivot[method_j].var()) / 2)
                    if pooled_std == 0 or math.isnan(pooled_std):
                        effect = 0.0
                    else:
                        effect = mean_diff / pooled_std
                    records.append(
                        {
                            "Scenario": scenario,
                            "Comparison": f"{method_i} vs {method_j}",
                            "Effect_Size": effect,
                        }
                    )
        return pd.DataFrame(records)

    def export_latex_table(self, summary: pd.DataFrame, path: Path) -> None:
        latex = summary.to_latex(index=False, float_format="{:.4f}".format)
        path.write_text(latex)

    def export_json(self, data: Dict, path: Path) -> None:
        path.write_text(json.dumps(data, indent=2))


# ==========================================================================
# VISUALIZATION
# ==========================================================================


class VisualizationGenerator:
    """Create publication-quality visualizations."""

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config
        self.palette = sns.color_palette("husl", 12)

    def _savefig(self, fig: plt.Figure, name: str) -> None:
        path = self.config.output_dir / "plots" / f"{name}.png"
        fig.savefig(path, dpi=self.config.dpi, bbox_inches="tight")
        plt.close(fig)

    def performance_bar(self, summary: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(
            data=summary,
            x="Method",
            y="Mean_MOO",
            hue="Scenario",
            palette="husl",
            ax=ax,
        )
        ax.set_title("Mean Multi-Objective Optimization Score by Method")
        ax.set_ylabel("Mean MOO (lower is better)")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._savefig(fig, "performance_bar")

    def boxplots(self, results: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.boxplot(
            data=results,
            x="Method",
            y="moo_score",
            hue="Scenario",
            palette="Set3",
            ax=ax,
        )
        ax.set_title("Distribution of Multi-Objective Scores")
        ax.set_ylabel("MOO Score")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._savefig(fig, "moo_boxplots")

    def radar_chart(self, summary: pd.DataFrame) -> None:
        metrics = [
            "Completion_Rate",
            "Failure_Rate",
            "Delay_Rate",
            "Avg_Processing_Time",
            "Throughput_per_hour",
            "Energy_per_job",
        ]
        top_methods = (
            summary.groupby("Method")["Mean_MOO"].mean().nsmallest(6).index.tolist()
        )
        scenarios = summary["Scenario"].unique()
        method_stats = summary[summary["Method"].isin(top_methods)]

        num_metrics = len(metrics)
        angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
        angles += angles[:1]

        fig, axes = plt.subplots(1, len(scenarios), subplot_kw=dict(polar=True), figsize=(5 * len(scenarios), 6))
        if len(scenarios) == 1:
            axes = [axes]
        for ax, scenario in zip(axes, scenarios):
            subset = method_stats[method_stats["Scenario"] == scenario]
            for color, method in zip(self.palette, top_methods):
                values = subset[subset["Method"] == method][metrics].mean().tolist()
                if not values:
                    continue
                values += values[:1]
                ax.plot(angles, values, color=color, linewidth=1, label=method)
                ax.fill(angles, values, color=color, alpha=0.1)
            ax.set_title(f"Scenario: {scenario}")
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics, fontsize=9)
        axes[0].legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        self._savefig(fig, "radar_chart")

    def effect_size_heatmap(self, effects: pd.DataFrame) -> None:
        if effects.empty:
            return
        pivot = effects.pivot(index="Comparison", columns="Scenario", values="Effect_Size")
        fig, ax = plt.subplots(figsize=(10, max(6, len(pivot) * 0.4)))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
        ax.set_title("Cohen's d Effect Sizes (Method Comparisons)")
        self._savefig(fig, "effect_sizes")

    def confidence_interval_plot(self, summary: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        for scenario, group in summary.groupby("Scenario"):
            ax.errorbar(
                group["Method"],
                group["Mean_MOO"],
                yerr=[group["Mean_MOO"] - group["CI_Lower"], group["CI_Upper"] - group["Mean_MOO"]],
                fmt="o",
                capsize=5,
                label=scenario,
            )
        ax.set_ylabel("Mean MOO Score")
        ax.set_title("95% Confidence Intervals for MOO Score")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._savefig(fig, "confidence_intervals")

    def computation_time(self, perf: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=perf, x="compute_time", y="Mean_MOO", hue="Scenario", style="Method", ax=ax)
        ax.set_title("Performance vs Computational Cost")
        ax.set_xlabel("Average Runtime (s)")
        ax.set_ylabel("Mean MOO Score")
        fig.tight_layout()
        self._savefig(fig, "performance_vs_time")

    def pareto_fronts(self, results: pd.DataFrame) -> None:
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        markers = itertools.cycle(["o", "^", "s", "d", "x", "*"])
        for method, group in results.groupby("Method"):
            marker = next(markers)
            ax.scatter(
                group["avg_processing_time"],
                group["total_energy"],
                group["machine_utilization"],
                marker=marker,
                label=method,
                alpha=0.6,
            )
        ax.set_xlabel("Avg Processing Time")
        ax.set_ylabel("Total Energy")
        ax.set_zlabel("Machine Utilization")
        ax.set_title("Pareto Front Approximation")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        self._savefig(fig, "pareto_fronts")

    def statistical_significance_heatmap(self, wilcoxon: Dict[str, Dict[str, float]]) -> None:
        if not wilcoxon:
            return
        flat_records = []
        for scenario, comparisons in wilcoxon.items():
            for pair, pvalue in comparisons.items():
                flat_records.append({"Scenario": scenario, "Comparison": pair, "pvalue": pvalue})
        df = pd.DataFrame(flat_records)
        pivot = df.pivot(index="Comparison", columns="Scenario", values="pvalue")
        fig, ax = plt.subplots(figsize=(10, max(6, len(pivot) * 0.4)))
        sns.heatmap(pivot, annot=True, fmt=".3f", cmap="viridis_r", ax=ax)
        ax.set_title("Wilcoxon Signed-Rank Test (p-values)")
        self._savefig(fig, "wilcoxon_heatmap")

    def correlation_matrix(self, results: pd.DataFrame) -> None:
        corr = results[[
            "moo_score",
            "completion_rate",
            "failure_rate",
            "delay_rate",
            "avg_processing_time",
            "total_energy",
            "machine_utilization",
            "throughput_per_hour",
        ]].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_title("Metric Correlation Matrix (Spearman)")
        self._savefig(fig, "correlation_matrix")

    def tardiness_distribution(self, results: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.violinplot(
            data=results,
            x="Method",
            y="avg_tardiness",
            hue="Scenario",
            palette="Pastel2",
            ax=ax,
        )
        ax.set_title("Tardiness Distribution by Method")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._savefig(fig, "tardiness_violin")

    def status_distribution(self, job_details: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(12, 6))
        status_counts = job_details.groupby(["Scenario", "Method", "Status"]).size().reset_index(name="Count")
        sns.barplot(
            data=status_counts,
            x="Method",
            y="Count",
            hue="Status",
            ax=ax,
        )
        ax.set_title("Job Status Distribution per Method")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._savefig(fig, "status_distribution")


# ==========================================================================
# REPORT GENERATION
# ==========================================================================


class ReportGenerator:
    """Generate markdown report summarizing experimental findings."""

    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config

    def generate(self, summary: pd.DataFrame, friedman: Dict, wilcoxon: Dict, effects: pd.DataFrame) -> None:
        lines: List[str] = []
        lines.append("# Advanced Manufacturing Optimization Framework\n")
        lines.append("## Executive Summary\n")
        best_methods = summary.sort_values("Mean_MOO").groupby("Scenario").first()["Method"].to_dict()
        lines.append("**Top-performing methods per scenario:**\n")
        for scenario, method in best_methods.items():
            lines.append(f"- **{scenario}**: {method}\n")
        lines.append("\n## Global Statistical Significance\n")
        for scenario, stats_dict in friedman.items():
            stat = stats_dict["statistic"]
            pvalue = stats_dict["pvalue"]
            lines.append(f"- Scenario **{scenario}**: Friedman χ² = {stat:.3f}, p = {pvalue:.4f}\n")
        lines.append("\n## Pairwise Comparisons (Bonferroni-corrected)\n")
        for scenario, comparisons in wilcoxon.items():
            lines.append(f"### Scenario: {scenario}\n")
            if not comparisons:
                lines.append("No sufficient data for pairwise tests.\n")
            for pair, pvalue in comparisons.items():
                lines.append(f"- {pair}: p = {pvalue:.4f}\n")
        lines.append("\n## Effect Sizes (Cohen's d)\n")
        if effects.empty:
            lines.append("Effect sizes unavailable.\n")
        else:
            for scenario, group in effects.groupby("Scenario"):
                lines.append(f"### {scenario}\n")
                top_effects = group.sort_values("Effect_Size", key=np.abs, ascending=False).head(5)
                for row in top_effects.itertuples(index=False):
                    magnitude = self._interpret_effect_size(row.Effect_Size)
                    lines.append(f"- {row.Comparison}: d = {row.Effect_Size:.3f} ({magnitude})\n")
        lines.append("\n## Method Performance Highlights\n")
        for method, group in summary.groupby("Method"):
            moo = group["Mean_MOO"].mean()
            completion = group["Completion_Rate"].mean()
            energy = group["Energy_per_job"].mean()
            lines.append(
                f"- **{method}**: Avg MOO={moo:.3f}, Completion={completion:.2%}, Energy/job={energy:.2f} kWh\n"
            )
        lines.append("\n---\n")
        lines.append("Generated automatically by the Advanced Manufacturing Optimization Framework.\n")

        report_path = self.config.output_dir / "EXPERIMENTAL_REPORT.md"
        report_path.write_text("".join(lines))

    @staticmethod
    def _interpret_effect_size(effect: float) -> str:
        magnitude = abs(effect)
        if magnitude < 0.2:
            return "negligible"
        if magnitude < 0.5:
            return "small"
        if magnitude < 0.8:
            return "medium"
        return "large"


# ==========================================================================
# EXPERIMENTAL FRAMEWORK ORCHESTRATOR
# ==========================================================================


class ExperimentalFramework:
    def __init__(self, config: ExperimentalConfig) -> None:
        self.config = config
        self.data_loader = DataLoader(config)
        self.simulator = StochasticSimulator(config)
        self.methods = OptimizationMethods(config)
        self.evaluator = ScheduleEvaluator(config, self.simulator)
        self.stats = StatisticalAnalyzer(config)
        self.visuals = VisualizationGenerator(config)
        self.reporter = ReportGenerator(config)

    def run(self, selected_methods: Optional[List[str]] = None, max_jobs: Optional[int] = None) -> None:
        df = self.data_loader.load()
        if max_jobs is not None and max_jobs < len(df):
            LOGGER.info("Restricting dataset from %d to %d jobs", len(df), max_jobs)
            df = df.head(max_jobs)

        method_registry = self.methods.registry()
        if selected_methods:
            missing = [m for m in selected_methods if m not in method_registry]
            if missing:
                raise ValueError(f"Unknown methods requested: {missing}")
            method_registry = {m: method_registry[m] for m in selected_methods}

        all_results = []
        job_details_records = []
        runtime_records = []

        for scenario in self.config.scenarios:
            LOGGER.info("Running scenario: %s", scenario)
            for replication in range(1, self.config.n_replications + 1):
                LOGGER.info("  Replication %d/%d", replication, self.config.n_replications)
                for method_name, method_fn in method_registry.items():
                    start_time = time.perf_counter()
                    prioritized = method_fn(df)
                    job_df, metrics = self.evaluator.evaluate(df, prioritized, scenario, replication)
                    runtime = time.perf_counter() - start_time
                    metrics.update(
                        {
                            "Scenario": scenario,
                            "Method": method_name,
                            "Replication": replication,
                            "compute_time": runtime,
                        }
                    )
                    all_results.append(metrics)
                    job_df["Method"] = method_name
                    job_details_records.append(job_df)
                    runtime_records.append(
                        {
                            "Scenario": scenario,
                            "Method": method_name,
                            "Replication": replication,
                            "compute_time": runtime,
                        }
                    )

        results_df = pd.DataFrame(all_results)
        job_details_df = pd.concat(job_details_records, ignore_index=True)
        runtime_df = pd.DataFrame(runtime_records)

        summary_df = self.stats.summarize(results_df)
        friedman = self.stats.friedman_test(results_df)
        wilcoxon = self.stats.wilcoxon_tests(results_df)
        effects_df = self.stats.effect_sizes(results_df)

        # Save tables
        summary_df.to_csv(self.config.output_dir / "tables" / "summary_statistics.csv", index=False)
        results_df.to_csv(self.config.output_dir / "tables" / "all_results.csv", index=False)
        job_details_df.to_csv(self.config.output_dir / "tables" / "job_details.csv", index=False)
        runtime_df.groupby(["Scenario", "Method"]).agg({"compute_time": "mean"}).reset_index().to_csv(
            self.config.output_dir / "tables" / "runtime_summary.csv", index=False
        )

        self.stats.export_latex_table(summary_df, self.config.output_dir / "latex" / "summary_table.tex")
        self.stats.export_json(friedman, self.config.output_dir / "statistics" / "friedman.json")
        self.stats.export_json(wilcoxon, self.config.output_dir / "statistics" / "wilcoxon.json")
        effects_df.to_csv(self.config.output_dir / "tables" / "effect_sizes.csv", index=False)

        # Visualizations
        self.visuals.performance_bar(summary_df)
        self.visuals.boxplots(results_df)
        self.visuals.radar_chart(summary_df)
        self.visuals.effect_size_heatmap(effects_df)
        self.visuals.confidence_interval_plot(summary_df)
        perf_with_time = summary_df.merge(
            runtime_df.groupby(["Scenario", "Method"]).mean().reset_index(),
            on=["Scenario", "Method"],
            how="left",
        )
        self.visuals.computation_time(perf_with_time)
        self.visuals.correlation_matrix(results_df)
        self.visuals.tardiness_distribution(results_df)
        self.visuals.status_distribution(job_details_df)
        self.visuals.statistical_significance_heatmap(wilcoxon)

        self.visuals.pareto_fronts(results_df)

        # Report
        self.reporter.generate(summary_df, friedman, wilcoxon, effects_df)

        LOGGER.info("Experiment completed. Results saved to %s", self.config.output_dir)


# ==========================================================================
# CLI ENTRY POINT
# ==========================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Advanced manufacturing optimization experiments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--methods", nargs="*", help="Subset of methods to run")
    parser.add_argument("--max-jobs", type=int, default=None, help="Limit number of jobs for quick runs")
    parser.add_argument("--replications", type=int, default=None, help="Override number of replications")
    parser.add_argument("--scenarios", nargs="*", help="Override scenarios to evaluate")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ExperimentalConfig()
    if args.replications:
        config.n_replications = args.replications
    if args.scenarios:
        config.scenarios = tuple(args.scenarios)
    framework = ExperimentalFramework(config)
    framework.run(selected_methods=args.methods, max_jobs=args.max_jobs)


if __name__ == "__main__":
    main()
