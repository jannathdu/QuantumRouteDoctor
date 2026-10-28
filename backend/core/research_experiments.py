"""Reproducible comparisons of baseline and temporal routing."""

import math

from backend.core.research_scenarios import generate_research_scenario
from backend.core.fidelity_routing import find_fidelity_constrained_route
from backend.core.temporal_routing import find_temporal_route
from backend.core.route_evaluation import evaluate_route


def run_research_experiments(
    seeds,
    node_count=10,
    link_count=15,
    current_time=10.0,
    minimum_fidelity=0.5,
    maximum_aoi=5.0,
):
    """Run both algorithms on paired synthetic network scenarios."""

    if not isinstance(seeds, (list, tuple)) or not seeds:
        raise ValueError("seeds must be a non-empty list or tuple")

    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        raise ValueError("All seeds must be integers")

    if len(set(seeds)) != len(seeds):
        raise ValueError("Duplicate seeds are not allowed")

    if (
        isinstance(minimum_fidelity, bool)
        or not isinstance(minimum_fidelity, (int, float))
        or not math.isfinite(minimum_fidelity)
        or not 0.25 <= minimum_fidelity <= 1.0
    ):
        raise ValueError("Invalid minimum_fidelity")

    if (
        isinstance(maximum_aoi, bool)
        or not isinstance(maximum_aoi, (int, float))
        or not math.isfinite(maximum_aoi)
        or maximum_aoi < 0
    ):
        raise ValueError("Invalid maximum_aoi")

    records = []

    for seed in seeds:
        graph = generate_research_scenario(
            node_count=node_count,
            link_count=link_count,
            seed=seed,
            current_time=current_time,
        )

        source = "N0"
        destination = f"N{node_count - 1}"

        baseline = find_fidelity_constrained_route(
            graph,
            source,
            destination,
            minimum_fidelity=minimum_fidelity,
        )

        temporal = find_temporal_route(
            graph,
            source,
            destination,
            current_time=current_time,
            minimum_fidelity=minimum_fidelity,
            maximum_aoi=maximum_aoi,
        )

        for algorithm, result in (
            ("baseline", baseline),
            ("temporal", temporal),
        ):
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
                "route_selected": result is not None,
                "selected_route": result["route"] if result else None,
                "hop_count": evaluation["hop_count"] if evaluation else None,
                "memory_adjusted_fidelity": (
                    evaluation["memory_adjusted_fidelity"]
                    if evaluation else None
                ),
                "maximum_link_aoi": (
                    evaluation["maximum_link_aoi"]
                    if evaluation else None
                ),
                "feasible": evaluation["feasible"] if evaluation else False,
                "minimum_fidelity": minimum_fidelity,
                "maximum_aoi": maximum_aoi,
                "current_time": current_time,
                "data_source": "synthetic_random_connected",
            })

    return records
