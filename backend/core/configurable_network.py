"""Validated configurable quantum network topology builder."""

import math
import networkx as nx


def create_configurable_network(nodes, links):
    """Build an undirected network from nodes and link specifications."""
    if not isinstance(nodes, (list, tuple)) or len(nodes) < 2:
        raise ValueError("nodes must contain at least two entries")

    if not all(isinstance(node, str) and node.strip() for node in nodes):
        raise ValueError("node identifiers must be non-empty strings")

    if len(set(nodes)) != len(nodes):
        raise ValueError("duplicate node identifiers are not allowed")

    if not isinstance(links, (list, tuple)):
        raise ValueError("links must be a list or tuple")

    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    for index, link in enumerate(links):
        if not isinstance(link, dict):
            raise ValueError(f"link {index} must be a dictionary")

        try:
            source = link["source"]
            target = link["target"]
            fidelity = link["fidelity"]
            noise = link["noise"]
        except KeyError as exc:
            raise ValueError(f"link {index} missing {exc.args[0]}") from exc

        if source not in graph or target not in graph:
            raise ValueError(f"link {index} references unknown nodes")

        if source == target:
            raise ValueError("self-links are not allowed")

        if graph.has_edge(source, target):
            raise ValueError("duplicate undirected link")

        for name, value in (("fidelity", fidelity), ("noise", noise)):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0.0 <= value <= 1.0
            ):
                raise ValueError(f"link {index} has invalid {name}")

        attributes = {"fidelity": float(fidelity), "noise": float(noise)}

        for name in (
            "measurement_time",
            "storage_time",
            "decoherence_rate",
        ):
            if name in link:
                value = link[name]

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise ValueError(f"link {index} has invalid {name}")

                if name != "measurement_time" and value < 0:
                    raise ValueError(f"link {index} has negative {name}")

                attributes[name] = float(value)

        graph.add_edge(source, target, **attributes)

    return graph
