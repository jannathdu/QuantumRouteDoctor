"""Reproducible synthetic quantum-network research scenarios."""

import math
import random

from backend.core.configurable_network import create_configurable_network


def generate_research_scenario(
    node_count=10,
    link_count=15,
    seed=42,
    current_time=10.0,
):
    """Generate a connected synthetic quantum network using a fixed seed."""

    if isinstance(node_count, bool) or not isinstance(node_count, int):
        raise ValueError("node_count must be an integer")

    if isinstance(link_count, bool) or not isinstance(link_count, int):
        raise ValueError("link_count must be an integer")

    if node_count < 2:
        raise ValueError("node_count must be at least 2")

    maximum_links = node_count * (node_count - 1) // 2

    if not node_count - 1 <= link_count <= maximum_links:
        raise ValueError("Invalid link_count for a connected network")

    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    if (
        isinstance(current_time, bool)
        or not isinstance(current_time, (int, float))
        or not math.isfinite(current_time)
        or current_time < 0
    ):
        raise ValueError("Invalid current_time")

    rng = random.Random(seed)

    nodes = [f"N{i}" for i in range(node_count)]

    shuffled = nodes.copy()
    rng.shuffle(shuffled)

    edges = set()

    # Build a random spanning tree to guarantee connectivity.
    for index in range(1, node_count):
        parent = rng.randrange(index)
        pair = tuple(sorted((shuffled[index], shuffled[parent])))
        edges.add(pair)

    # Add additional randomly selected undirected links.
    candidates = [
        tuple(sorted((nodes[i], nodes[j])))
        for i in range(node_count)
        for j in range(i + 1, node_count)
        if tuple(sorted((nodes[i], nodes[j]))) not in edges
    ]

    rng.shuffle(candidates)

    additional = link_count - len(edges)

    edges.update(candidates[:additional])

    links = []

    for source, target in sorted(edges):
        fidelity = rng.uniform(0.85, 0.99)
        noise = rng.uniform(0.01, 0.15)
        aoi = rng.uniform(0.0, min(10.0, current_time))
        storage_time = rng.uniform(0.0, 5.0)
        decoherence_rate = rng.uniform(0.005, 0.05)

        links.append({
            "source": source,
            "target": target,
            "fidelity": fidelity,
            "noise": noise,
            "measurement_time": current_time - aoi,
            "storage_time": storage_time,
            "decoherence_rate": decoherence_rate,
        })

    graph = create_configurable_network(nodes, links)

    graph.graph["seed"] = seed
    graph.graph["scenario_type"] = "synthetic_random_connected"
    graph.graph["current_time"] = float(current_time)

    return graph

