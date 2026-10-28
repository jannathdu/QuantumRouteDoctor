"""Exact paired feasibility inference for quantum routing experiments."""

import math

from backend.core.research_statistics import summarize_paired_experiments


def mcnemar_exact_test(baseline_only, temporal_only):
    """Two-sided exact McNemar test using the binomial distribution."""
    for name, value in (
        ("baseline_only", baseline_only),
        ("temporal_only", temporal_only),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid {name}")

    discordant = baseline_only + temporal_only

    if discordant == 0:
        return {
            "discordant_pairs": 0,
            "p_value": 1.0,
            "method": "exact_mcnemar_two_sided",
        }

    smaller = min(baseline_only, temporal_only)

    tail_probability = math.fsum(
        math.comb(discordant, k) * (0.5 ** discordant)
        for k in range(smaller + 1)
    )

    p_value = min(1.0, 2.0 * tail_probability)

    return {
        "discordant_pairs": discordant,
        "p_value": p_value,
        "method": "exact_mcnemar_two_sided",
    }


def analyze_paired_feasibility(records):
    """Return paired feasibility difference and exact McNemar result."""
    summary = summarize_paired_experiments(records)

    baseline = summary["algorithms"]["baseline"]
    temporal = summary["algorithms"]["temporal"]
    outcomes = summary["paired_outcomes"]

    difference = (
        temporal["feasibility_rate"]
        - baseline["feasibility_rate"]
    )

    test = mcnemar_exact_test(
        outcomes["baseline_only"],
        outcomes["temporal_only"],
    )

    return {
        "scenario_count": summary["scenario_count"],
        "baseline_feasibility_rate": baseline["feasibility_rate"],
        "temporal_feasibility_rate": temporal["feasibility_rate"],
        "paired_feasibility_difference": difference,
        "paired_outcomes": outcomes,
        "mcnemar": test,
        "statistically_significant_at_0_05": test["p_value"] < 0.05,
        "data_source": "synthetic_paired_experiments",
    }
