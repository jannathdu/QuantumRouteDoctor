import math
import networkx as nx
from backend.models.temporal_fidelity import calculate_aoi, predict_memory_fidelity
from backend.models.entanglement import multi_hop_fidelity

def find_temporal_route(network, source, target, current_time, minimum_fidelity=0.8, maximum_aoi=10.0):
    if not math.isfinite(current_time):
        raise ValueError('Invalid current time')
    if not 0.25 <= minimum_fidelity <= 1.0:
        raise ValueError('Invalid minimum fidelity')
    if not math.isfinite(maximum_aoi) or maximum_aoi < 0:
        raise ValueError('Invalid maximum AoI')
    if source not in network or target not in network or source == target:
        raise ValueError('Invalid source or target')

    best = None
    for path in nx.all_simple_paths(network, source, target):
        fidelities = []
        ages = []
        feasible = True
        for u, v in zip(path, path[1:]):
            link = network[u][v]
            age = calculate_aoi(current_time, link["measurement_time"])
            if age > maximum_aoi:
                feasible = False
                break
            fidelity = predict_memory_fidelity(
                link["fidelity"],
                link["storage_time"],
                link["decoherence_rate"],
            )
            if fidelity < 0.25:
                feasible = False
                break
            fidelities.append(fidelity)
            ages.append(age)
        if not feasible:
            continue
        end_fidelity = multi_hop_fidelity(fidelities)
        if end_fidelity < minimum_fidelity:
            continue
        candidate = {
            "route": path,
            "predicted_fidelity": end_fidelity,
            "maximum_link_aoi": max(ages),
            "hop_count": len(path) - 1,
        }
        if best is None or (
            end_fidelity > best["predicted_fidelity"]
            or (end_fidelity == best["predicted_fidelity"]
                and len(path) < len(best["route"]))
        ):
            best = candidate
    return best
