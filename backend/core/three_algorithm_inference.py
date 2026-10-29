"""Pairwise exact McNemar tests with global Holm correction."""

import math


def exact_mcnemar_p_value(first_only, second_only):
    """Calculate a two-sided exact McNemar p-value."""
    for name, value in (
        ("first_only", first_only),
        ("second_only", second_only),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise ValueError(f"Invalid {name}")

    discordant = first_only + second_only

    if discordant == 0:
        return 1.0

    smaller = min(first_only, second_only)
    tail = math.fsum(
        math.comb(discordant, k) * (0.5 ** discordant)
        for k in range(smaller + 1)
    )
    return min(1.0, 2.0 * tail)


def holm_adjust(p_values):
    """Return Holm-Bonferroni adjusted p-values in input order."""
    if not isinstance(p_values, (list, tuple)) or not p_values:
        raise ValueError("p_values must be a non-empty list or tuple")

    for value in p_values:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError("Every p-value must be finite and in [0, 1]")

    count = len(p_values)
    ordered = sorted(range(count), key=lambda index: p_values[index])
    adjusted = [0.0] * count
    running_max = 0.0

    for rank, index in enumerate(ordered):
        candidate = min(1.0, (count - rank) * p_values[index])
        running_max = max(running_max, candidate)
        adjusted[index] = running_max

    return adjusted


def analyze_three_algorithm_inference(summary, alpha=0.05):
    """Test all pairwise comparisons with global Holm correction."""
    if (
        isinstance(alpha, bool)
        or not isinstance(alpha, (int, float))
        or not math.isfinite(alpha)
        or not 0.0 < alpha < 1.0
    ):
        raise ValueError("alpha must be between 0 and 1")

    if not isinstance(summary, dict):
        raise ValueError("Invalid three-algorithm summary")

    results = summary.get("results")
    if not isinstance(results, list) or not results:
        raise ValueError("Summary must contain non-empty results")

    comparisons = []
    expected_pairs = {
        "baseline_vs_memory_aware",
        "baseline_vs_temporal",
        "memory_aware_vs_temporal",
    }

    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Each result must be a dictionary")

        pairs = result.get("paired_comparisons")
        if not isinstance(pairs, dict) or set(pairs) != expected_pairs:
            raise ValueError("Missing or unexpected pairwise comparisons")

        for pair_name in sorted(expected_pairs):
            counts = pairs[pair_name]
            if not isinstance(counts, dict):
                raise ValueError(f"Invalid counts for {pair_name}")

            first, second = pair_name.split("_vs_", 1)
            first_only = counts.get(f"{first}_only")
            second_only = counts.get(f"{second}_only")

            p_value = exact_mcnemar_p_value(first_only, second_only)

            comparisons.append({
                "maximum_aoi": result["maximum_aoi"],
                "minimum_fidelity": result["minimum_fidelity"],
                "comparison": pair_name,
                "first_only": first_only,
                "second_only": second_only,
                "discordant_pairs": first_only + second_only,
                "p_value": p_value,
            })

    expected_count = len(results) * 3
    if len(comparisons) != expected_count:
        raise ValueError("Unexpected pairwise comparison count")

    adjusted = holm_adjust(
        [item["p_value"] for item in comparisons]
    )

    for item, adjusted_p in zip(comparisons, adjusted):
        item["holm_adjusted_p_value"] = adjusted_p
        item["significant_after_holm"] = adjusted_p < alpha

    return {
        "analysis_type": "paired_exact_mcnemar",
        "correction": "global_holm_bonferroni",
        "alpha": alpha,
        "family_size": len(comparisons),
        "parameter_combinations": len(results),
        "comparisons": comparisons,
        "data_source": "synthetic_paired_experiments",
    }
