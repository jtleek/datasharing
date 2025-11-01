# 🎓 Advanced Manufacturing Optimization Framework

Publication-ready experimental system for multi-objective job shop scheduling.

## 📋 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Theoretical Foundation](#-theoretical-foundation)
4. [Implemented Methods](#-implemented-methods)
5. [Installation](#-installation)
6. [Quick Start](#-quick-start)
7. [Detailed Usage](#-detailed-usage)
8. [Output Description](#-output-description)
9. [Statistical Validation](#-statistical-validation)
10. [Publication Guidelines](#-publication-guidelines)
11. [Contributing](#-contributing)

## 🎯 Overview
The framework delivers a rigorous experimental platform for benchmarking optimization strategies in hybrid manufacturing. It is engineered to satisfy Q1 journal standards with stochastic simulation, statistical validation, and reproducible pipelines.

**Target applications**
- Hybrid manufacturing scheduling (job-shop, flow-shop, flexible cells)
- Operations research experimentation with multi-objective objectives
- Industry 4.0/5.0 digital twins and decision-support systems
- Academic benchmarking of heuristics and metaheuristics

## ⭐ Key Features
| Dimension | Description |
| --- | --- |
| Scientific rigor | 30 replications, 95% CIs, Friedman + Wilcoxon tests, Cohen's *d*, reproducible seeds |
| Algorithm portfolio | 12 methods (7 dispatching rules, 3 metaheuristics, 2 advanced multi-objective approaches) |
| Simulation realism | Processing variability, energy uncertainty, machine breakdowns, learning effects |
| Outputs | Publication-grade figures (300 DPI), LaTeX tables, CSV exports, markdown report |
| Extensibility | Modular design for adding new methods, metrics, or scenarios |

## 📚 Theoretical Foundation
The framework optimizes a four-objective vector \((Z_1, Z_2, Z_3, Z_4)\) representing makespan, energy, material usage, and machine underutilization. Aggregation uses a weighted sum with configurable weights defaulting to \((0.35, 0.25, 0.20, 0.20)\).

Stochastic simulation includes:
- **Processing time variability**: \(T \sim \mathcal{N}(T_0, 0.1 T_0)\) with adaptive learning in the multi-objective scenario.
- **Energy consumption**: Gamma-distributed deviations with tighter constraints under energy-constrained runs.
- **Machine breakdowns**: Poisson probability per job with downtime samples from \(\mathcal{U}(10,30)\) minutes.
- **Learning curves**: Power-law learning with exponent derived from a 5% improvement every doubling of jobs.
- **Quality success**: Availability-dependent Bernoulli trials blending equipment reliability with schedule decisions.

## 🧮 Implemented Methods
### Classical Dispatching Rules
- **FCFS** (First Come First Served)
- **SPT** (Shortest Processing Time)
- **LPT** (Longest Processing Time)
- **EDD** (Earliest Due Date)
- **Slack Time** (minimum slack priority)
- **Critical Ratio**
- **WSPT** (Weighted Shortest Processing Time)

### Metaheuristics and Multi-objective Strategies
- **Genetic Algorithm** (Dirichlet-weight evolution with elitism and mutation)
- **Particle Swarm Optimization** (continuous weight exploration with inertia/cognitive/social terms)
- **Simulated Annealing** (stochastic weight adaptation with exponential cooling)
- **NSGA-II Approximation** (fast Pareto ranking on normalized objectives)
- **Intelligent Multi-Agent Optimizer** (Pareto score + efficiency boosts + machine load balancing)

## 💻 Installation
```bash
# optional virtual environment recommended
pip install pandas numpy matplotlib seaborn scipy scikit-learn
```
The script auto-generates a synthetic dataset when `hybrid_manufacturing_categorical.csv` is absent.

## 🚀 Quick Start
```bash
python advanced_manufacturing_optimization.py \
    --methods FCFS SPT Intelligent_MultiAgent \
    --replications 10 \
    --scenarios baseline stochastic \
    --max-jobs 120
```
Outputs are written to `advanced_optimization_results/` with plots, tables, LaTeX exports, and a comprehensive markdown report.

## 🔧 Detailed Usage
- `--methods`: optional list of method identifiers from the registry.
- `--replications`: override the default 30 replications.
- `--scenarios`: subset of scenarios (`baseline`, `stochastic`, `high_variability`, `energy_constrained`, `multi_objective`).
- `--max-jobs`: truncate the dataset for exploratory runs.

To register a custom method, extend `OptimizationMethods.registry()` with a callable returning a prioritized DataFrame.

## 📊 Output Description
- `tables/summary_statistics.csv`: aggregate metrics with 95% confidence intervals.
- `tables/all_results.csv`: full replication-level data (50+ metrics).
- `tables/effect_sizes.csv`: Cohen's *d* for every pairwise comparison.
- `plots/*.png`: bar charts, box plots, radar charts, correlation heatmaps, Pareto fronts, status distributions, etc.
- `latex/summary_table.tex`: publication-ready LaTeX table.
- `statistics/*.json`: Friedman and Wilcoxon outcomes.
- `EXPERIMENTAL_REPORT.md`: auto-generated executive summary.

## 📈 Statistical Validation
- **Global hypothesis**: Friedman test for each scenario.
- **Pairwise**: Wilcoxon signed-rank with Bonferroni correction.
- **Effect size**: Cohen's *d* classification (negligible/small/medium/large).
- **Power**: ≥0.8 for medium effects with 30 replications.

## 📝 Publication Guidelines
Provide a detailed methodology, cite classical dispatching references (Conway et al. 1967; Jackson 1955; Baker & Trietsch 2013) and metaheuristic sources (Goldberg 1989; Kennedy & Eberhart 1995; Kirkpatrick et al. 1983; Deb et al. 2002). Include generated figures (300 DPI) and LaTeX tables directly in manuscripts (IEEE/ACM compatible).

## 🤝 Contributing
1. Fork the repository.
2. Implement the enhancement with thorough docstrings.
3. Add tests or validation scripts if feasible.
4. Update this guide or the generated report if the methodology evolves.
5. Submit a pull request describing experimental impacts.

---
*This documentation complements the automated report produced by the framework and captures the rationale behind the experimental design.*
