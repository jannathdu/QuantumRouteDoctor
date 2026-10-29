"""Memory-aware quantum routing baseline without an AoI constraint."""

import math
import networkx as nx

from backend.models.entanglement import multi_hop_fidelity
from backend.models.temporal_fidelity import predict_memory_fidelity


def find_memory_aware_route(
    network,
    source,
    target,
    minimum_fidelity=0.8,
):
    """Select the highest memory-adjusted-fidelity feasible route.

    Unlike temporal routing, this baseline does not reject routes
    based on the age of information (AoI).
    """
    if (
        isinstance(minimum_fidelity, bool)
        or not isinstance(minimum_fidelity, (int, float))
        or not math.isfinite(minimum_fidelity)
        or not 0.25 <= minimum_fidelity <= 1.0
    ):
        raise ValueError("Invalid minimum_fidelity")

    if source not in network or target not in network:
        raise ValueError("Source or target node does not exist")

    if source == target:
        raise ValueError("Source and target must be different nodes")

    best = None

    for path in nx.all_simple_paths(network, source, target):
        fidelities = []

        for u, v in zip(path, path[1:]):
            link = network[u][v]

            fidelity = predict_memory_fidelity(
                link["fidelity"],
                link.get("storage_time", 0.0),
                link.get("decoherence_rate", 0.0),
            )
            fidelities.append(fidelity)

        end_fidelity = multi_hop_fidelity(fidelities)

        if end_fidelity < minimum_fidelity:
            continue

        candidate = {
            "route": path,
            "predicted_fidelity": end_fidelity,
            "hop_count": len(path) - 1,
        }

        if best is None or (
            end_fidelity > best["predicted_fidelity"]
            or (
                end_fidelity == best["predicted_fidelity"]
                and len(path) < len(best["route"])
            )
        ):
            best = candidate

    return best
