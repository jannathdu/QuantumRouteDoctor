"""Reproducible paired bootstrap confidence intervals."""

import math
import random

from backend.core.research_statistics import summarize_paired_experiments


def paired_bootstrap_feasibility_ci(
    records,
    confidence_level=0.95,
    bootstrap_samples=10000,
    random_seed=2026,
):
    """Percentile bootstrap CI for temporal minus baseline feasibility."""

    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0 and 1")

    if (
        isinstance(bootstrap_samples, bool)
        or not isinstance(bootstrap_samples, int)
        or bootstrap_samples < 2
    ):
        raise ValueError("bootstrap_samples must be an integer >= 2")

    if isinstance(random_seed, bool) or not isinstance(random_seed, int):
        raise ValueError("random_seed must be an integer")

    summary = summarize_paired_experiments(records)
    outcomes = summary["paired_outcomes"]
    n = summary["scenario_count"]

    # Paired differences: temporal feasibility minus baseline feasibility.
    differences = (
        [0] * outcomes["both_feasible"]
        + [-1] * outcomes["baseline_only"]
        + [1] * outcomes["temporal_only"]
        + [0] * outcomes["neither_feasible"]
    )

    observed_difference = math.fsum(differences) / n

    rng = random.Random(random_seed)
    bootstrap_estimates = []

    for _ in range(bootstrap_samples):
        estimate = (
            math.fsum(rng.choices(differences, k=n)) / n
        )
        bootstrap_estimates.append(estimate)

    bootstrap_estimates.sort()

    alpha = 1.0 - confidence_level

    def percentile(probability):
        position = probability * (bootstrap_samples - 1)
        lower = math.floor(position)
        upper = math.ceil(position)
        fraction = position - lower

        return (
            bootstrap_estimates[lower] * (1.0 - fraction)
            + bootstrap_estimates[upper] * fraction
        )

    return {
        "scenario_count": n,
        "observed_difference": observed_difference,
        "confidence_level": confidence_level,
        "confidence_interval": [
            percentile(alpha / 2.0),
            percentile(1.0 - alpha / 2.0),
        ],
        "bootstrap_samples": bootstrap_samples,
        "random_seed": random_seed,
        "method": "paired_percentile_bootstrap",
    }
