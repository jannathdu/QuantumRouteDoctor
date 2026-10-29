"""Descriptive and paired statistics for three routing algorithms."""

from collections import defaultdict

from backend.core.research_statistics import wilson_interval


ALGORITHMS = ("baseline", "memory_aware", "temporal")


def summarize_three_algorithm_experiments(records):
    """Summarize feasibility and paired outcomes per parameter combination."""

    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")

    groups = defaultdict(dict)

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each record must be a dictionary")

        required = {
            "seed",
            "algorithm",
            "maximum_aoi",
            "minimum_fidelity",
            "feasible",
            "route_selected",
            "memory_adjusted_fidelity",
        }
        if not required.issubset(record):
            raise ValueError("Experiment record is missing required fields")

        algorithm = record["algorithm"]
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        if not isinstance(record["feasible"], bool):
            raise ValueError("feasible must be boolean")

        key = (
            record["seed"],
            record["maximum_aoi"],
            record["minimum_fidelity"],
        )
        if algorithm in groups[key]:
            raise ValueError("Duplicate algorithm record for scenario")

        groups[key][algorithm] = record

    for algorithms in groups.values():
        if set(algorithms) != set(ALGORITHMS):
            raise ValueError("Every scenario must contain all three algorithms")

    summary_groups = defaultdict(list)

    for key, algorithms in groups.items():
        _, maximum_aoi, minimum_fidelity = key
        summary_groups[(maximum_aoi, minimum_fidelity)].append(algorithms)

    results = []

    for (maximum_aoi, minimum_fidelity), scenarios in sorted(
        summary_groups.items()
    ):
        algorithm_summary = {}

        for algorithm in ALGORITHMS:
            selected = [scenario[algorithm] for scenario in scenarios]
            successes = sum(record["feasible"] for record in selected)
            total = len(selected)

            algorithm_summary[algorithm] = {
                "feasible_count": successes,
                "scenario_count": total,
                "feasibility_rate": successes / total,
                "feasibility_ci_95": wilson_interval(successes, total),
                "route_selection_rate": sum(
                    record["route_selected"] for record in selected
                ) / total,
            }

        paired = {}

        for first_index, first in enumerate(ALGORITHMS):
            for second in ALGORITHMS[first_index + 1:]:
                both = 0
                first_only = 0
                second_only = 0
                neither = 0

                for scenario in scenarios:
                    first_ok = scenario[first]["feasible"]
                    second_ok = scenario[second]["feasible"]

                    if first_ok and second_ok:
                        both += 1
                    elif first_ok:
                        first_only += 1
                    elif second_ok:
                        second_only += 1
                    else:
                        neither += 1

                paired[f"{first}_vs_{second}"] = {
                    "both_feasible": both,
                    f"{first}_only": first_only,
                    f"{second}_only": second_only,
                    "neither_feasible": neither,
                    "feasibility_rate_difference": (
                        algorithm_summary[second]["feasibility_rate"]
                        - algorithm_summary[first]["feasibility_rate"]
                    ),
                }

        results.append({
            "maximum_aoi": maximum_aoi,
            "minimum_fidelity": minimum_fidelity,
            "scenario_count": len(scenarios),
            "algorithms": algorithm_summary,
            "paired_comparisons": paired,
            "data_source": "synthetic_paired_experiments",
        })

    return {
        "parameter_combinations": len(results),
        "scenario_count": len(groups),
        "algorithms": list(ALGORITHMS),
        "results": results,
        "analysis_type": "descriptive_paired_three_algorithm",
    }
