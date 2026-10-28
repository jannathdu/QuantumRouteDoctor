"""Deterministic time-step evolution of temporal quantum-link states."""

import math

from backend.models.temporal_fidelity import (
    calculate_aoi,
    predict_memory_fidelity,
)


def evolve_network_state(
    network,
    current_time,
    next_time,
    refreshed_links=None,
):
    """Return a new graph with evolved AoI and quantum memory state.

    A measurement refresh updates controller information only.
    It does not reset the quantum memory storage time.

    The input graph is assumed to represent the state at current_time.
    """
    for name, value in (
        ("current_time", current_time),
        ("next_time", next_time),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"Invalid {name}")

    if next_time < current_time:
        raise ValueError("next_time cannot precede current_time")

    delta_time = next_time - current_time
    result = network.copy()

    refreshes = set()

    for link in refreshed_links or []:
        if not isinstance(link, (tuple, list)) or len(link) != 2:
            raise ValueError("Each refreshed link must contain two nodes")

        source, target = link

        if not network.has_edge(source, target):
            raise ValueError("Unknown refreshed link")

        refreshes.add(frozenset((source, target)))

    for source, target, data in result.edges(data=True):
        required = (
            "fidelity",
            "measurement_time",
            "storage_time",
            "decoherence_rate",
        )

        if any(name not in data for name in required):
            raise ValueError("Missing temporal link attributes")

        measurement_time = data["measurement_time"]
        storage_time = data["storage_time"]
        rate = data["decoherence_rate"]
        fidelity = data["fidelity"]

        values = (measurement_time, storage_time, rate, fidelity)

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in values
        ):
            raise ValueError("Invalid temporal link attributes")

        if not 0.25 <= fidelity <= 1.0:
            raise ValueError("Fidelity must be between 0.25 and 1.0")

        if storage_time < 0 or rate < 0:
            raise ValueError("Invalid storage time or decoherence rate")

        calculate_aoi(current_time, measurement_time)

        if frozenset((source, target)) in refreshes:
            data["measurement_time"] = next_time

        updated_storage_time = storage_time + delta_time

        data["storage_time"] = updated_storage_time
        data["aoi"] = calculate_aoi(
            next_time,
            data["measurement_time"],
        )

        data["predicted_memory_fidelity"] = predict_memory_fidelity(
            fidelity,
            updated_storage_time,
            rate,
        )

    return result
