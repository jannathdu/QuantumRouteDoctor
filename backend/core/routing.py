"""Quantum network routing algorithms."""

import networkx as nx


def calculate_route_metrics(
    network,
    route,
):
    route_fidelity = 1.0
    total_noise = 0.0
    total_age = 0.0

    hop_count = len(route) - 1

    for index in range(hop_count):
        current_node = route[index]
        next_node = route[index + 1]

        link_data = network[current_node][next_node]

        route_fidelity *= link_data["fidelity"]
        total_noise += link_data["noise"]
        total_age += link_data.get("age", 0.0)

    if hop_count > 0:
        average_noise = total_noise / hop_count
        average_age = total_age / hop_count
    else:
        average_noise = 0.0
        average_age = 0.0

    age_freshness = max(
        0.0,
        1.0 - (average_age / 20.0),
    )

    route_health = (
        0.60 * route_fidelity
        + 0.25 * (1.0 - average_noise)
        + 0.15 * age_freshness
    )

    return route_fidelity, total_noise, route_health


def find_safe_route(
    network,
    source_node,
    target_node,
    faulty_edges,
):
    safe_network = network.copy()

    for node_1, node_2 in faulty_edges:
        if safe_network.has_edge(node_1, node_2):
            safe_network.remove_edge(node_1, node_2)

    try:
        all_safe_routes = list(
            nx.all_simple_paths(
                safe_network,
                source=source_node,
                target=target_node,
            )
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

    if not all_safe_routes:
        return None

    best_route = None
    best_health_score = float("-inf")

    for route in all_safe_routes:
        _, _, health_score = calculate_route_metrics(
            network,
            route,
        )

        if health_score > best_health_score:
            best_health_score = health_score
            best_route = route

    return best_route


def compare_all_routes(
    network,
    source_node,
    target_node,
):
    route_results = []

    try:
        all_routes = list(
            nx.all_simple_paths(
                network,
                source=source_node,
                target=target_node,
            )
        )

        for route in all_routes:
            route_fidelity, route_noise, health_score = (
                calculate_route_metrics(
                    network,
                    route,
                )
            )

            hop_count = len(route) - 1
            total_age = 0.0

            for index in range(hop_count):
                current_node = route[index]
                next_node = route[index + 1]

                link_data = network[current_node][next_node]
                total_age += link_data.get("age", 0.0)

            if hop_count > 0:
                average_age = total_age / hop_count
            else:
                average_age = 0.0

            if health_score >= 0.75:
                route_quality = "EXCELLENT"

            elif health_score >= 0.50:
                route_quality = "GOOD"

            else:
                route_quality = "POOR"

            route_results.append(
                {
                    "Route": " → ".join(route),
                    "Hop Count": hop_count,
                    "Fidelity": route_fidelity,
                    "Noise": route_noise,
                    "Average Age (s)": average_age,
                    "Health Score": health_score,
                    "Route Quality": route_quality,
                }
            )

    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    route_results.sort(
        key=lambda item: item["Health Score"],
        reverse=True,
    )

    return route_results


def add_route_safety_status(
    route_results,
    faulty_edges,
):
    faulty_edge_set = {
        frozenset(edge)
        for edge in faulty_edges
    }

    for route_result in route_results:
        route_nodes = route_result["Route"].split(" → ")
        route_is_safe = True

        for index in range(len(route_nodes) - 1):
            route_edge = frozenset(
                {
                    route_nodes[index],
                    route_nodes[index + 1],
                }
            )

            if route_edge in faulty_edge_set:
                route_is_safe = False
                break

        route_result["Safety Status"] = (
            "SAFE" if route_is_safe else "UNSAFE"
        )

    return route_results
