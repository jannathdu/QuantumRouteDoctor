import networkx as nx


def create_quantum_network(
    ab_fidelity,
    ab_noise,
    bc_fidelity,
    bc_noise,
    ad_fidelity,
    ad_noise,
    dc_fidelity,
    dc_noise,
    ab_age=2.0,
    bc_age=5.0,
    ad_age=1.0,
    dc_age=3.0,
):
    network = nx.Graph()

    network.add_nodes_from(["A", "B", "C", "D"])

    network.add_edge(
        "A",
        "B",
        fidelity=ab_fidelity,
        noise=ab_noise,
        age=ab_age,
    )

    network.add_edge(
        "B",
        "C",
        fidelity=bc_fidelity,
        noise=bc_noise,
        age=bc_age,
    )

    network.add_edge(
        "A",
        "D",
        fidelity=ad_fidelity,
        noise=ad_noise,
        age=ad_age,
    )

    network.add_edge(
        "D",
        "C",
        fidelity=dc_fidelity,
        noise=dc_noise,
        age=dc_age,
    )

    return network
