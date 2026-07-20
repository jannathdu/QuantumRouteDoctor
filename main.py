import networkx as nx
import matplotlib.pyplot as plt

FIDELITY_THRESHOLD = 0.88
NOISE_THRESHOLD = 0.25

def create_quantum_network():
    network = nx.Graph()

    network.add_nodes_from(["A", "B", "C", "D"])

    network.add_edge("A", "B", fidelity=0.90, noise=0.20)
    network.add_edge("B", "C", fidelity=0.85, noise=0.30)
    network.add_edge("A", "D", fidelity=0.95, noise=0.10)
    network.add_edge("D", "C", fidelity=0.92, noise=0.15)

    return network


def scan_faulty_links(network):
    faulty_edges = []

    print("\nAutomatic network health scan:")

    for node_1, node_2, data in network.edges(data=True):
        fidelity = data["fidelity"]
        noise = data["noise"]

        if fidelity < FIDELITY_THRESHOLD or noise > NOISE_THRESHOLD:
            print(f"{node_1}-{node_2}: FAULTY")
            faulty_edges.append((node_1, node_2))
        else:
            print(f"{node_1}-{node_2}: HEALTHY")

    return faulty_edges


def find_safe_route(network, faulty_edges, source, target):
    safe_network = network.copy()

    for faulty_edge in faulty_edges:
        safe_network.remove_edge(*faulty_edge)

    print("Safe network links:", list(safe_network.edges))

    try:
        safe_route = nx.shortest_path(
            safe_network,
            source=source,
            target=target
        )

        print("Safe alternative route:", safe_route)
        return safe_route

    except nx.NetworkXNoPath:
        print(f"No safe route is available from {source} to {target}.")
        return []


def calculate_route_metrics(network, route):
    route_fidelity = 1.0
    route_noise = 0.0

    for index in range(len(route) - 1):
        current_node = route[index]
        next_node = route[index + 1]

        link_data = network[current_node][next_node]

        route_fidelity *= link_data["fidelity"]
        route_noise += link_data["noise"]

    route_health = route_fidelity - route_noise

    return route_fidelity, route_noise, route_health


def draw_network(network, safe_route, faulty_edges):
    position = nx.spring_layout(network)

    nx.draw(
        network,
        position,
        with_labels=True
    )

    if safe_route:
        recommended_edges = list(zip(safe_route, safe_route[1:]))
    else:
        recommended_edges = []

    nx.draw_networkx_edges(
        network,
        position,
        edgelist=recommended_edges,
        width=4
    )

    nx.draw_networkx_edges(
        network,
        position,
        edgelist=faulty_edges,
        width=4,
        style="dashed"
    )

    edge_labels = {
        (node_1, node_2): (
            f"F={data['fidelity']}, N={data['noise']}"
        )
        for node_1, node_2, data in network.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        network,
        position,
        edge_labels=edge_labels
    )

    plt.show()


def print_report(
    network,
    faulty_edges,
    safe_route,
    safe_fidelity,
    safe_noise,
    safe_health
):
    print("\nQuantumRoute Doctor Report")
    print("--------------------------")
    print("Total nodes:", network.number_of_nodes())
    print("Total links:", network.number_of_edges())
    print("Fidelity threshold:", FIDELITY_THRESHOLD)
    print("Noise threshold:", NOISE_THRESHOLD)
    print("Faulty links:", faulty_edges)

    if safe_route:
        print("Recommended safe route:", safe_route)
        print("Safe route fidelity:", safe_fidelity)
        print("Safe route noise:", safe_noise)
        print("Safe route health score:", safe_health)
    else:
        print("Recommended safe route: None")


def main():
    quantum_network = create_quantum_network()

    print("Total nodes:", quantum_network.number_of_nodes())
    print("Node list:", list(quantum_network.nodes))
    print("Total links:", quantum_network.number_of_edges())
    print("Link list:", list(quantum_network.edges))
    print(
        "Links with data:",
        list(quantum_network.edges(data=True))
    )

    all_routes = list(
        nx.all_simple_paths(
            quantum_network,
            source="A",
            target="C"
        )
    )

    print("All routes from A to C:", all_routes)

    for route in all_routes:
        fidelity, noise, health = calculate_route_metrics(
            quantum_network,
            route
        )

        print("\nRoute:", route)
        print("Fidelity:", fidelity)
        print("Noise:", noise)
        print("Health score:", health)

    faulty_edges = scan_faulty_links(quantum_network)

    print("Faulty link list:", faulty_edges)

    safe_route = find_safe_route(
        quantum_network,
        faulty_edges,
        "A",
        "C"
    )

    safe_fidelity = 0.0
    safe_noise = 0.0
    safe_health = 0.0

    if safe_route:
        safe_fidelity, safe_noise, safe_health = (
            calculate_route_metrics(
                quantum_network,
                safe_route
            )
        )

    print_report(
        quantum_network,
        faulty_edges,
        safe_route,
        safe_fidelity,
        safe_noise,
        safe_health
    )

    draw_network(
        quantum_network,
        safe_route,
        faulty_edges
    )


if __name__ == "__main__":
    main()