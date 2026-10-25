"""Reproducible temporal demo network for research prototyping."""

from backend.core.network import create_quantum_network


def create_temporal_demo_network(current_time=10.0):
    """Add simulated timestamps and quantum-memory parameters."""
    graph = create_quantum_network(
        0.95, 0.05,
        0.94, 0.06,
        0.92, 0.08,
        0.91, 0.09,
    )

    temporal_parameters = {
        ("A", "B"): (2.0, 1.0, 0.01),
        ("A", "D"): (1.0, 1.0, 0.02),
        ("B", "C"): (5.0, 2.0, 0.03),
        ("C", "D"): (3.0, 1.0, 0.02),
    }

    for (source, target), (aoi, storage_time, rate) in temporal_parameters.items():
        link = graph[source][target]
        link["measurement_time"] = current_time - aoi
        link["storage_time"] = storage_time
        link["decoherence_rate"] = rate

    return graph
