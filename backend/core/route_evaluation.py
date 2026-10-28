"""Shared evaluation metrics for quantum routing experiments."""

import math

from backend.models.entanglement import multi_hop_fidelity
from backend.models.temporal_fidelity import (
    calculate_aoi,
    predict_memory_fidelity,
)


def evaluate_route(
    network,
    route,
    current_time,
    minimum_fidelity=0.8,
    maximum_aoi=10.0,
):
    """Evaluate a given route using consistent link-state assumptions."""
    if (
        isinstance(current_time, bool)
        or not isinstance(current_time, (int, float))
        or not math.isfinite(current_time)
    ):
        raise ValueError("Invalid current_time")

    if not 0.25 <= minimum_fidelity <= 1.0:
        raise ValueError("Invalid minimum_fidelity")

    if (
        not isinstance(maximum_aoi, (int, float))
        or isinstance(maximum_aoi, bool)
        or not math.isfinite(maximum_aoi)
        or maximum_aoi < 0
    ):
        raise ValueError("Invalid maximum_aoi")

    if not isinstance(route, (list, tuple)) or len(route) < 2:
        raise ValueError("Route must contain at least two nodes")

    if len(set(route)) != len(route):
        raise ValueError("Route cannot contain repeated nodes")

    reference_fidelities = []
    adjusted_fidelities = []
    ages = []

    for source, target in zip(route, route[1:]):
        if not network.has_edge(source, target):
            raise ValueError("Route contains a missing link")

        link = network[source][target]

        fidelity = link["fidelity"]
        reference_fidelities.append(fidelity)

        storage_time = link.get("storage_time", 0.0)
        decoherence_rate = link.get("decoherence_rate", 0.0)

        adjusted = predict_memory_fidelity(
            fidelity,
            storage_time,
            decoherence_rate,
        )

        adjusted_fidelities.append(adjusted)

        measurement_time = link.get(
            "measurement_time",
            current_time,
        )

        ages.append(
            calculate_aoi(current_time, measurement_time)
        )

    reference_fidelity = multi_hop_fidelity(reference_fidelities)
    adjusted_fidelity = multi_hop_fidelity(adjusted_fidelities)
    maximum_link_aoi = max(ages)

    fidelity_feasible = adjusted_fidelity >= minimum_fidelity
    aoi_feasible = maximum_link_aoi <= maximum_aoi

    return {
        "route": list(route),
        "hop_count": len(route) - 1,
        "reference_fidelity": reference_fidelity,
        "memory_adjusted_fidelity": adjusted_fidelity,
        "maximum_link_aoi": maximum_link_aoi,
        "fidelity_feasible": fidelity_feasible,
        "aoi_feasible": aoi_feasible,
        "feasible": fidelity_feasible and aoi_feasible,
        "evaluation_model": "werner_swap_with_memory_decay",
    }
