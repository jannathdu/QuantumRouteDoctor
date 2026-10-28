"""Deterministic synthetic quantum link-state simulator."""

import math

import networkx as nx


def simulate_dynamic_links(
    network: nx.Graph,
    current_time: float,
    noise_amplitude: float = 0.05,
    noise_frequency: float = 0.1,
    failed_links=None,
):
    """Return a copied graph with updated noise, fidelity, and link failures.

    This is a synthetic demonstration model, not a calibrated physical
    quantum-channel model.
    """
    for name, value in (
        ("current_time", current_time),
        ("noise_amplitude", noise_amplitude),
        ("noise_frequency", noise_frequency),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"Invalid {name}")

    if noise_amplitude < 0 or noise_amplitude > 1:
        raise ValueError("noise_amplitude must be between 0 and 1")

    if noise_frequency < 0:
        raise ValueError("noise_frequency cannot be negative")

    result = network.copy()

    failures = set()
    for link in failed_links or []:
        if len(link) != 2:
            raise ValueError("Each failed link must have two endpoints")
        u, v = link
        if not network.has_edge(u, v):
            raise ValueError(f"Unknown failed link: {u}-{v}")
        failures.add(frozenset((u, v)))

    for index, (u, v, data) in enumerate(result.edges(data=True)):
        if frozenset((u, v)) in failures:
            continue

        baseline_noise = data["noise"]
        initial_fidelity = data["fidelity"]

        if not (
            0 <= baseline_noise <= 1
            and 0.25 <= initial_fidelity <= 1
        ):
            raise ValueError(f"Invalid link state: {u}-{v}")

        phase = float(index)
        variation = noise_amplitude * math.sin(
            noise_frequency * current_time + phase
        )

        updated_noise = max(
            0.0,
            min(1.0, baseline_noise + variation),
        )

        updated_fidelity = 0.25 + (
            initial_fidelity - 0.25
        ) * (1.0 - updated_noise)

        data["noise"] = updated_noise
        data["fidelity"] = updated_fidelity
        data["available"] = True

    for u, v in result.edges():
        if frozenset((u, v)) in failures:
            result[u][v]["available"] = False

    result.remove_edges_from(
        (u, v)
        for u, v, data in list(result.edges(data=True))
        if not data.get("available", True)
    )

    return result
