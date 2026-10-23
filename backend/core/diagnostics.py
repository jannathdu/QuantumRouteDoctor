def scan_faulty_links(
    network,
    fidelity_threshold,
    noise_threshold,
):
    faulty_edges = []

    for node_1, node_2, data in network.edges(data=True):
        fidelity = data["fidelity"]
        noise = data["noise"]

        if (
            fidelity < fidelity_threshold
            or noise > noise_threshold
        ):
            faulty_edges.append((node_1, node_2))

    return faulty_edges


def create_link_diagnosis(
    network,
    fidelity_threshold,
    noise_threshold,
):
    diagnosis_results = []

    for node_1, node_2, data in network.edges(data=True):
        fidelity = data["fidelity"]
        noise = data["noise"]

        reasons = []

        fidelity_gap = max(
            0.0,
            fidelity_threshold - fidelity,
        )

        noise_gap = max(
            0.0,
            noise - noise_threshold,
        )

        severity_score = fidelity_gap + noise_gap

        if fidelity < fidelity_threshold:
            reasons.append("Low fidelity")

        if noise > noise_threshold:
            reasons.append("High noise")

        if reasons:
            status = "FAULTY"
            reason = " and ".join(reasons)

            if severity_score >= 0.15:
                severity = "HIGH"
                recommendation = (
                    "Disable this link temporarily and reroute traffic."
                )
            elif severity_score >= 0.05:
                severity = "MEDIUM"
                recommendation = (
                    "Monitor the link and prefer an alternative route."
                )
            else:
                severity = "LOW"
                recommendation = "Continue monitoring this link."
        else:
            status = "HEALTHY"
            reason = "Link values are within safe limits"
            severity = "NONE"
            recommendation = "No action is required."

        diagnosis_results.append(
            {
                "Link": f"{node_1} → {node_2}",
                "Fidelity": round(fidelity, 3),
                "Noise": round(noise, 3),
                "Status": status,
                "Severity": severity,
                "Reason": reason,
                "Recommended Action": recommendation,
            }
        )

    return diagnosis_results
