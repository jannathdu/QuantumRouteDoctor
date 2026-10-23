"""Fidelity-constrained quantum routing baseline."""

import networkx as nx
from backend.models.entanglement import multi_hop_fidelity


def find_fidelity_constrained_route(network, source, target, minimum_fidelity=0.8):
    """Select the highest-fidelity route meeting a minimum threshold."""
    if not 0.25 <= minimum_fidelity <= 1.0:
        raise ValueError("minimum_fidelity must be between 0.25 and 1.0")

    if source not in network or target not in network:
        raise ValueError("Source or target node does not exist")

    if source == target:
        raise ValueError("Source and target must be different nodes")

    best_route = None
    best_fidelity = -1.0

    for route in nx.all_simple_paths(network, source, target):
        fidelities = [
            network[route[i]][route[i + 1]]["fidelity"]
            for i in range(len(route) - 1)
        ]
        fidelity = multi_hop_fidelity(fidelities)

        if fidelity < minimum_fidelity:
            continue

        if fidelity > best_fidelity or (
            fidelity == best_fidelity
            and best_route is not None
            and len(route) < len(best_route)
        ):
            best_route = route
            best_fidelity = fidelity

    if best_route is None:
        return None

    return {
        "route": best_route,
        "end_to_end_fidelity": best_fidelity,
        "hop_count": len(best_route) - 1,
    }
