"""Descriptive statistics for paired quantum-routing experiments."""

import math
import statistics


def wilson_interval(successes, total, z=1.959963984540054):
    """Return a two-sided Wilson confidence interval for a proportion."""
    if (
        isinstance(successes, bool)
        or isinstance(total, bool)
        or not isinstance(successes, int)
        or not isinstance(total, int)
        or total <= 0
        or not 0 <= successes <= total
    ):
        raise ValueError("Invalid successes or total")

    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total**2))
        / denominator
    )

    return [max(0.0, center - margin), min(1.0, center + margin)]


def summarize_paired_experiments(records):
    """Summarize correctly paired baseline and temporal experiment records."""
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")

    pairs = {}

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each record must be a dictionary")

        seed = record.get("seed")
        algorithm = record.get("algorithm")

        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("Invalid seed")

        if algorithm not in ("baseline", "temporal"):
            raise ValueError("Unknown algorithm")

        if not isinstance(record.get("feasible"), bool):
            raise ValueError("feasible must be boolean")

        pair = pairs.setdefault(seed, {})

        if algorithm in pair:
            raise ValueError("Duplicate algorithm record for seed")

        pair[algorithm] = record

    if any(set(pair) != {"baseline", "temporal"} for pair in pairs.values()):
        raise ValueError("Each seed must contain both algorithms")

    counts = {
        "both_feasible": 0,
        "baseline_only": 0,
        "temporal_only": 0,
        "neither_feasible": 0,
    }

    summary = {}

    for algorithm in ("baseline", "temporal"):
        selected = [pair[algorithm] for pair in pairs.values()]
        feasible = [record for record in selected if record["feasible"]]

        fidelities = [
            record["memory_adjusted_fidelity"]
            for record in feasible
        ]

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0.25 <= value <= 1.0
            for value in fidelities
        ):
            raise ValueError("Invalid feasible-route fidelity")

        successes = len(feasible)
        total = len(selected)

        summary[algorithm] = {
            "feasible_count": successes,
            "total": total,
            "feasibility_rate": successes / total,
            "feasibility_ci_95": wilson_interval(successes, total),
            "mean_fidelity_given_feasible": (
                statistics.mean(fidelities) if fidelities else None
            ),
        }

    for pair in pairs.values():
        baseline_ok = pair["baseline"]["feasible"]
        temporal_ok = pair["temporal"]["feasible"]

        if baseline_ok and temporal_ok:
            counts["both_feasible"] += 1
        elif baseline_ok:
            counts["baseline_only"] += 1
        elif temporal_ok:
            counts["temporal_only"] += 1
        else:
            counts["neither_feasible"] += 1

    return {
        "scenario_count": len(pairs),
        "algorithms": summary,
        "paired_outcomes": counts,
        "analysis_type": "descriptive_paired_synthetic",
    }
