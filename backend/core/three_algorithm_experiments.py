"""Paired three-algorithm quantum routing experiments."""

import math

from backend.core.fidelity_routing import find_fidelity_constrained_route
from backend.core.memory_aware_routing import find_memory_aware_route
from backend.core.research_scenarios import generate_research_scenario
from backend.core.route_evaluation import evaluate_route
from backend.core.temporal_routing import find_temporal_route


def run_three_algorithm_experiments(
    seeds,
    aoi_thresholds=(2.0, 4.0, 6.0, 8.0),
    minimum_fidelity_thresholds=(0.5, 0.6, 0.7, 0.8),
    node_count=10,
    link_count=15,
    current_time=10.0,
):
    """Compare three routing algorithms on paired synthetic scenarios."""

    if not isinstance(seeds, (list, tuple)) or not seeds:
        raise ValueError("seeds must be a non-empty list or tuple")

    if any(
        isinstance(seed, bool) or not isinstance(seed, int)
        for seed in seeds
    ):
        raise ValueError("All seeds must be integers")

    if len(set(seeds)) != len(seeds):
        raise ValueError("Duplicate seeds are not allowed")

    if not isinstance(aoi_thresholds, (list, tuple)) or not aoi_thresholds:
        raise ValueError("aoi_thresholds must be non-empty")

    if not isinstance(
        minimum_fidelity_thresholds, (list, tuple)
    ) or not minimum_fidelity_thresholds:
        raise ValueError("minimum_fidelity_thresholds must be non-empty")

    for threshold in aoi_thresholds:
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold)
            or threshold < 0
        ):
            raise ValueError("Invalid AoI threshold")

    for threshold in minimum_fidelity_thresholds:
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold)
            or not 0.25 <= threshold <= 1.0
        ):
            raise ValueError("Invalid fidelity threshold")

    if (
        isinstance(current_time, bool)
        or not isinstance(current_time, (int, float))
        or not math.isfinite(current_time)
        or current_time < 0
    ):
        raise ValueError("Invalid current_time")

    if len(set(aoi_thresholds)) != len(aoi_thresholds):
        raise ValueError("Duplicate AoI thresholds are not allowed")

    if len(set(minimum_fidelity_thresholds)) != len(
        minimum_fidelity_thresholds
    ):
        raise ValueError("Duplicate fidelity thresholds are not allowed")

    records = []

    for seed in seeds:
        # All parameter combinations for a seed use the same network.
        graph = generate_research_scenario(
            node_count=node_count,
            link_count=link_count,
            seed=seed,
            current_time=current_time,
        )

        source = "N0"
        destination = f"N{node_count - 1}"

        for maximum_aoi in aoi_thresholds:
            for minimum_fidelity in minimum_fidelity_thresholds:
                results = {
                    "baseline": find_fidelity_constrained_route(
                        graph,
                        source,
                        destination,
                        minimum_fidelity=minimum_fidelity,
                    ),
                    "memory_aware": find_memory_aware_route(
                        graph,
                        source,
                        destination,
                        minimum_fidelity=minimum_fidelity,
                    ),
                    "temporal": find_temporal_route(
                        graph,
                        source,
                        destination,
                        current_time=current_time,
                        minimum_fidelity=minimum_fidelity,
                        maximum_aoi=maximum_aoi,
                    ),
                }

                for algorithm, result in results.items():
                    evaluation = (
                        evaluate_route(
                            graph,
                            result["route"],
                            current_time=current_time,
                            minimum_fidelity=minimum_fidelity,
                            maximum_aoi=maximum_aoi,
                        )
                        if result is not None
                        else None
                    )

                    records.append({
                        "seed": seed,
                        "node_count": node_count,
                        "link_count": link_count,
                        "source": source,
                        "destination": destination,
                        "algorithm": algorithm,
                        "maximum_aoi": maximum_aoi,
                        "minimum_fidelity": minimum_fidelity,
                        "route_selected": result is not None,
                        "selected_route": (
                            list(result["route"]) if result else None
                        ),
                        "hop_count": (
                            evaluation["hop_count"] if evaluation else None
                        ),
                        "reference_fidelity": (
                            evaluation["reference_fidelity"]
                            if evaluation else None
                        ),
                        "memory_adjusted_fidelity": (
                            evaluation["memory_adjusted_fidelity"]
                            if evaluation else None
                        ),
                        "maximum_link_aoi": (
                            evaluation["maximum_link_aoi"]
                            if evaluation else None
                        ),
                        "fidelity_feasible": (
                            evaluation["fidelity_feasible"]
                            if evaluation else False
                        ),
                        "aoi_feasible": (
                            evaluation["aoi_feasible"]
                            if evaluation else False
                        ),
                        "feasible": (
                            evaluation["feasible"] if evaluation else False
                        ),
                        "current_time": current_time,
                        "data_source": "synthetic_random_connected",
                    })

    return records
