import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from datetime import datetime
import base64
from pathlib import Path


# =========================================================
# 1. NETWORK CREATION
# =========================================================
def create_quantum_network(
    ab_fidelity,
    ab_noise,
    bc_fidelity,
    bc_noise,
    ad_fidelity,
    ad_noise,
    dc_fidelity,
    dc_noise,
):
    network = nx.Graph()

    network.add_nodes_from(["A", "B", "C", "D"])

    network.add_edge(
        "A",
        "B",
        fidelity=ab_fidelity,
        noise=ab_noise,
    )

    network.add_edge(
        "B",
        "C",
        fidelity=bc_fidelity,
        noise=bc_noise,
    )

    network.add_edge(
        "A",
        "D",
        fidelity=ad_fidelity,
        noise=ad_noise,
    )

    network.add_edge(
        "D",
        "C",
        fidelity=dc_fidelity,
        noise=dc_noise,
    )

    return network


# =========================================================
# 2. LINK DIAGNOSIS
# =========================================================
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


# =========================================================
# 3. ROUTE CALCULATION
# =========================================================
def calculate_route_metrics(
    network,
    route,
):
    route_fidelity = 1.0
    total_noise = 0.0

    hop_count = len(route) - 1

    for index in range(hop_count):
        current_node = route[index]
        next_node = route[index + 1]

        link_data = network[current_node][next_node]

        route_fidelity *= link_data["fidelity"]
        total_noise += link_data["noise"]

    if hop_count > 0:
        average_noise = total_noise / hop_count
    else:
        average_noise = 0.0

    route_health = (
        0.70 * route_fidelity
        + 0.30 * (1.0 - average_noise)
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

            if health_score >= 0.75:
                route_quality = "EXCELLENT"

            elif health_score >= 0.50:
                route_quality = "GOOD"

            else:
                route_quality = "POOR"

            route_results.append(
                {
                    "Route": " → ".join(route),
                    "Hop Count": len(route) - 1,
                    "Fidelity": route_fidelity,
                    "Noise": route_noise,
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


# =========================================================
# 4. TABLE STYLING
# =========================================================
def color_safety_status(value):
    if value == "SAFE":
        return "background-color: lightgreen; color: black;"

    if value == "UNSAFE":
        return "background-color: lightcoral; color: black;"

    return ""


def color_route_quality(value):
    if value == "EXCELLENT":
        return "background-color: lightgreen; color: black;"

    if value == "GOOD":
        return "background-color: khaki; color: black;"

    if value == "POOR":
        return "background-color: lightcoral; color: black;"

    return ""
def calculate_fault_severity(
    fidelity,
    noise,
):

    if fidelity < 0.75 or noise > 0.30:

        return "HIGH"

    elif fidelity < 0.90 or noise > 0.15:

        return "MEDIUM"

    else:

        return "LOW"
    
def rank_routes(routes):

    ranked_routes = sorted(
        routes,
        key=lambda route: route["Health Score"],
        reverse=True
    )

    return ranked_routes

def generate_professional_text_report(
    faulty_edges,
    diagnosis_text,
    ranked_routes,
):
    report_id = datetime.now().strftime(
        "QRD-%Y%m%d-%H%M%S"
    )

    logo_base64 = get_logo_base64()
    report_lines = []

    report_lines.append(
        "QUANTUMROUTE DOCTOR"
    )

    report_lines.append(
        "Professional Quantum Network Diagnosis Report"
    )

    report_lines.append(
        "=" * 60
    )

    report_lines.append("")

    report_lines.append(
        "1. NETWORK DIAGNOSIS"
    )

    report_lines.append(
        "-" * 60
    )

    for text in diagnosis_text:
        clean_text = str(text).strip()
        report_lines.append(clean_text)

    report_lines.append("")

    report_lines.append(
        "2. FAULT SUMMARY"
    )

    report_lines.append(
        "-" * 60
    )
    report_lines.append(
        f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    report_lines.append(
        f"Report ID: {report_id}"
    )

    if faulty_edges:

        for edge in faulty_edges:
            report_lines.append(
                f"Faulty Link: {edge[0]} -> {edge[1]}"
            )

    else:

        report_lines.append(
            "No faulty link detected."
        )

    report_lines.append("")

    report_lines.append(
        "3. ROUTE RANKING"
    )

    report_lines.append(
        "-" * 60
    )

    for rank, route in enumerate(
    ranked_routes,
    start=1
):

        safety_status = route["Safety Status"]
        route_quality = route["Route Quality"]

        if safety_status == "SAFE":
            safety_style = (
                "background-color: #dcfce7; "
                "color: #166534; "
                "font-weight: bold;"
            )
        else:
            safety_style = (
                "background-color: #fee2e2; "
                "color: #991b1b; "
                "font-weight: bold;"
            )

        if route_quality == "EXCELLENT":
            quality_style = (
                "background-color: #dcfce7; "
                "color: #166534; "
                "font-weight: bold;"
            )

        elif route_quality == "GOOD":
            quality_style = (
                "background-color: #fef3c7; "
                "color: #92400e; "
                "font-weight: bold;"
            )

        else:
            quality_style = (
                "background-color: #fee2e2; "
                "color: #991b1b; "
                "font-weight: bold;"
            )

    
        report_lines.append(
            f"Rank {rank}"
        )

        report_lines.append(
            f"Route: {route['Route']}"
        )

        report_lines.append(
            f"Health Score: {route['Health Score']:.3f}"
        )

        report_lines.append(
            f"Fidelity: {route['Fidelity']:.3f}"
        )

        report_lines.append(
            f"Noise: {route['Noise']:.3f}"
        )

        report_lines.append(
            f"Safety Status: {route['Safety Status']}"
        )

        report_lines.append(
            f"Route Quality: {route['Route Quality']}"
        )

        report_lines.append("")

    if ranked_routes:

        best_route = ranked_routes[0]

        report_lines.append(
            "4. FINAL ROUTING DECISION"
        )

        report_lines.append(
            "-" * 60
        )

        report_lines.append(
            f"Recommended Route: {best_route['Route']}"
        )

        report_lines.append(
            f"Decision: {best_route['Safety Status']}"
        )

        report_lines.append(
            f"Quality: {best_route['Route Quality']}"
        )

    report_lines.append("")

    report_lines.append(
        "=" * 60
    )

    report_lines.append(
        "Generated by QuantumRoute Doctor"
    )

    return "\n".join(report_lines)

def get_logo_base64():

    logo_path = Path(__file__).parent / "quantumroute_doctor_logo.jpg"

    if not logo_path.exists():
        return None

    with open(logo_path, "rb") as logo_file:
        encoded_logo = base64.b64encode(
            logo_file.read()
        ).decode("utf-8")

    return encoded_logo
def generate_professional_html_report(
    faulty_edges,
    diagnosis_text,
    ranked_routes,
):
    logo_base64 = get_logo_base64()

    if logo_base64:
        logo_html = f"""
        <img
            src="data:image/jpeg;base64,{logo_base64}"
            alt="QuantumRoute Doctor Logo"
            class="report-logo"
        >
        """
    else:
        logo_html = ""

    diagnosis_html = ""
    diagnosis_html = ""

    for text in diagnosis_text:
        diagnosis_html += (
            f"<p>{str(text).strip()}</p>"
        )

    fault_html = ""

    if faulty_edges:

        for edge in faulty_edges:
            fault_html += (
                f"<li>{edge[0]} → {edge[1]}</li>"
            )

    else:

        fault_html = "<li>No faulty link detected.</li>"

    ranking_html = ""

    for rank, route in enumerate(
    ranked_routes,
    start=1
):

        safety_status = route["Safety Status"]
        route_quality = route["Route Quality"]

        if safety_status == "SAFE":
            safety_style = (
                "background-color: #dcfce7; "
                "color: #166534; "
                "font-weight: bold;"
            )
        else:
            safety_style = (
                "background-color: #fee2e2; "
                "color: #991b1b; "
                "font-weight: bold;"
            )

        if route_quality == "EXCELLENT":
            quality_style = (
                "background-color: #dcfce7; "
                "color: #166534; "
                "font-weight: bold;"
            )

        elif route_quality == "GOOD":
            quality_style = (
                "background-color: #fef3c7; "
                "color: #92400e; "
                "font-weight: bold;"
            )

        else:
            quality_style = (
                "background-color: #fee2e2; "
                "color: #991b1b; "
                "font-weight: bold;"
            )

        ranking_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{route["Route"]}</td>
            <td>{route["Health Score"]:.3f}</td>
            <td>{route["Fidelity"]:.3f}</td>
            <td>{route["Noise"]:.3f}</td>
            <td style="{safety_style}">{safety_status}</td>
            <td style="{quality_style}">{route_quality}</td>
        </tr>
        """

    best_route = ranked_routes[0]

    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <title>
            QuantumRoute Doctor Report
        </title>

        <style>
                    .report-logo {{
                display: block;
                width: 120px;
                height: auto;
                margin: 0 auto 12px auto;
                border-radius: 10px;

            }}
            .print-button {{
                display: block;
                margin: 0 auto 20px auto;
                padding: 10px 18px;
                background-color: #1565c0;
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 15px;
                cursor: pointer;
            }}

            .print-button:hover {{
                background-color: #0d47a1;
            }}

            @media print {{
                .print-button {{
                    display: none;
                }}

                body {{
                    background-color: white;
                    margin: 0;
                }}

                .report-container {{
                    box-shadow: none;
                    max-width: 100%;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f4f7fb;
                color: #1f2937;
            }}

            .report-container {{
                max-width: 1000px;
                margin: auto;
                background-color: white;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.10);
            }}

            h1 {{
                color: #1565c0;
                text-align: center;
            }}

            h2 {{
                color: #0d47a1;
                border-bottom: 2px solid #90caf9;
                padding-bottom: 6px;
            }}

            .generated-time {{
                text-align: center;
                color: #6b7280;
            }}

            .decision {{
                padding: 16px;
                background-color: #e8f5e9;
                border-left: 6px solid #2e7d32;
                border-radius: 6px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            th,
            td {{
                border: 1px solid #d1d5db;
                padding: 10px;
                text-align: center;
            }}

            th {{
                background-color: #1565c0;
                color: white;
            }}

            tr:nth-child(even) {{
                background-color: #f3f4f6;
            }}

            .footer {{
                margin-top: 35px;
                text-align: center;
                color: #6b7280;
            }}
        </style>

    </head>

    <body>

        <div class="report-container">
            <button
                class="print-button"
                onclick="window.print()"
            >
                Print / Save as PDF
            </button>
            {logo_html}

            <h1>
                QuantumRoute Doctor
            </h1>

            <p class="generated-time">
                Professional Quantum Network Diagnosis Report
                <br>
                Generated At:
                {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>

            <h2>
                1. Network Diagnosis
            </h2>

            {diagnosis_html}

            <h2>
                2. Fault Summary
            </h2>

            <ul>
                {fault_html}
            </ul>

            <h2>
                3. Route Ranking
            </h2>

            <table>

                <tr>
                    <th>Rank</th>
                    <th>Route</th>
                    <th>Health Score</th>
                    <th>Fidelity</th>
                    <th>Noise</th>
                    <th>Safety</th>
                    <th>Quality</th>
                </tr>

                {ranking_html}

            </table>

            <h2>
                4. Final Routing Decision
            </h2>

            <div class="decision">

                <strong>
                    Recommended Route:
                </strong>

                {best_route["Route"]}

                <br><br>

                <strong>
                    Safety Status:
                </strong>

                {best_route["Safety Status"]}

                <br><br>

                <strong>
                    Route Quality:
                </strong>

                {best_route["Route Quality"]}

                <br><br>

                <strong>
                    Health Score:
                </strong>

                {best_route["Health Score"]:.3f}

            </div>

            <p class="footer">
                Generated by QuantumRoute Doctor
            </p>

        </div>

    </body>
    </html>
    """

    return html_report
  
def generate_diagnosis_explanation(
    faulty_edges,
    safe_route,
    network,
):

    explanation = []

    if faulty_edges:

        explanation.append(
            "⚠ Fault detected in network:"
        )

        for edge in faulty_edges:

            fidelity = network.edges[edge]["fidelity"]
            noise = network.edges[edge]["noise"]

            severity = calculate_fault_severity(
                fidelity,
                noise
            )

            explanation.append(
                f"""
Link {edge[0]} → {edge[1]}

Fidelity: {fidelity:.2f}

Noise: {noise:.2f}

Fault Severity: {severity}
"""
            )


            if fidelity < 0.85:

                explanation.append(
                    "Problem: Low fidelity"
                )


            if noise > 0.25:

                explanation.append(
                    "Problem: High noise"
                )


    else:

        explanation.append(
            "✓ No faulty link detected."
        )


    if safe_route:

        explanation.append(
            "Recommended route: "
            + " → ".join(safe_route)
        )


    return explanation

def explain_best_route(
    best_route,
    faulty_edges,
):

    reasons = []

    reasons.append(
        "Highest health score among all available routes."
    )

    route_nodes = best_route["Route"].split(" → ")

    route_edges = list(
        zip(
            route_nodes,
            route_nodes[1:]
        )
    )

    contains_faulty_link = any(
        edge in faulty_edges
        or (edge[1], edge[0]) in faulty_edges
        for edge in route_edges
    )

    if contains_faulty_link:
        reasons.append(
            "This route contains at least one faulty link."
        )
    else:
        reasons.append(
            "This route does not contain any faulty link."
        )

    if best_route["Safety Status"] == "SAFE":
        reasons.append(
            "The route is classified as SAFE."
        )

    reasons.append(
        f"Route quality is {best_route['Route Quality']}."
    )

    return reasons

#===================================================
# 5. NETWORK VISUALIZATION
# =========================================================
def create_network_figure(
    network,
    safe_route,
    faulty_edges,
):

    figure, axis = plt.subplots(
        figsize=(8, 6)
    )

    position = nx.spring_layout(
        network,
        seed=42,
    )

    # Node colors
    node_colors = []

    for node in network.nodes():

        if any(node in edge for edge in faulty_edges):
            node_colors.append("red")
        else:
            node_colors.append("lightgreen")


    # Draw network
    nx.draw(
        network,
        position,
        ax=axis,
        with_labels=True,
        node_size=1800,
        font_size=12,
        node_color=node_colors,
    )


    # Safe route highlight
    if safe_route and len(safe_route) > 1:

        safe_edges = list(
            zip(
                safe_route,
                safe_route[1:]
            )
        )

        nx.draw_networkx_edges(
            network,
            position,
            ax=axis,
            edgelist=safe_edges,
            width=5,
            edge_color="blue",
        )


    # Faulty edge highlight
    if faulty_edges:

        nx.draw_networkx_edges(
            network,
            position,
            ax=axis,
            edgelist=faulty_edges,
            width=4,
            style="dashed",
            edge_color="red",
        )


    # Edge labels
    edge_labels = {}

    for node_1, node_2, data in network.edges(data=True):

        edge_labels[
            (node_1, node_2)
        ] = (
            f"F={data['fidelity']:.2f}\n"
            f"N={data['noise']:.2f}"
        )


    nx.draw_networkx_edge_labels(
        network,
        position,
        ax=axis,
        edge_labels=edge_labels,
        font_size=9,
    )


    axis.set_title(
        "Quantum Network Health Map",
        fontsize=14,
    )

    axis.axis("off")


    return figure

# ==================================================
# 6. STREAMLIT PAGE
# ==================================================

st.set_page_config(
    page_title="QuantumRoute Doctor",
    page_icon="⚛️",
    layout="wide"
)

# =========================================================
# 6. STREAMLIT PAGE
# =========================================================
st.set_page_config(
    page_title="QuantumRoute Doctor",
    page_icon="🩺",
    layout="wide",
)

st.sidebar.header("Diagnostic Settings")
if "diagnosis_history" not in st.session_state:
    st.session_state["diagnosis_history"] = []

if st.sidebar.button(
    "Reset Link Parameters",
    key="reset_link_parameters"
):
    st.session_state["ab_fidelity_slider"] = 0.90
    st.session_state["ab_noise_slider"] = 0.20
    st.session_state["bc_fidelity_slider"] = 0.85
    st.session_state["bc_noise_slider"] = 0.30
    st.session_state["ad_fidelity_slider"] = 0.95
    st.session_state["ad_noise_slider"] = 0.10
    st.session_state["dc_fidelity_slider"] = 0.92
    st.session_state["dc_noise_slider"] = 0.15

    if st.sidebar.button(
    "Clear Diagnosis History",
    key="clear_diagnosis_history_button",
):
        st.session_state["diagnosis_history"] = []
        st.rerun()

fault_link = st.sidebar.selectbox(
    "Select Link for Fault Simulation",
    ["A-B", "B-C", "A-D", "D-C"],
    key="fault_link_selectbox"
)
fault_level = st.sidebar.selectbox(
    "Fault Severity Level",
    [
        "Mild",
        "Medium",
        "Severe"
    ],
    key="fault_level_selectbox"
)


fault_values = {
    "Mild": (0.82, 0.28),
    "Medium": (0.70, 0.40),
    "Severe": (0.60, 0.50)
}


simulate_fault = st.sidebar.button(
    "Simulate Selected Link Fault",
    key="simulate_selected_fault_button"
)

if simulate_fault:

    link_slider_keys = {
        "A-B": (
            "ab_fidelity_slider",
            "ab_noise_slider"
        ),

        "B-C": (
            "bc_fidelity_slider",
            "bc_noise_slider"
        ),

        "A-D": (
            "ad_fidelity_slider",
            "ad_noise_slider"
        ),

        "D-C": (
            "dc_fidelity_slider",
            "dc_noise_slider"
        )
    }


    fidelity_key, noise_key = link_slider_keys[fault_link]


    fault_values = {
        "Mild": (0.82, 0.28),
        "Medium": (0.70, 0.40),
        "Severe": (0.60, 0.50)
    }


    fault_fidelity, fault_noise = fault_values[fault_level]


    st.session_state[fidelity_key] = fault_fidelity
    st.session_state[noise_key] = fault_noise



    st.session_state["diagnosis_history"].append(
        {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Event": "Fault Simulated",
            "Link": fault_link,
            "Severity": fault_level
        }
    )

    st.rerun()

restore_selected_link = st.sidebar.button(
    "Restore Selected Link",
    key="restore_selected_link_button"
)

if restore_selected_link:

    default_link_values = {
        "A-B": (
            "ab_fidelity_slider",
            0.90,
            "ab_noise_slider",
            0.20
        ),

        "B-C": (
            "bc_fidelity_slider",
            0.85,
            "bc_noise_slider",
            0.30
        ),

        "A-D": (
            "ad_fidelity_slider",
            0.95,
            "ad_noise_slider",
            0.10
        ),

        "D-C": (
            "dc_fidelity_slider",
            0.92,
            "dc_noise_slider",
            0.15
        )
    }


    (
        fidelity_key,
        default_fidelity,
        noise_key,
        default_noise
    ) = default_link_values[fault_link]


    st.session_state[fidelity_key] = default_fidelity
    st.session_state[noise_key] = default_noise


    st.session_state["diagnosis_history"].append(
        {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Event": "Link Restored",
            "Link": fault_link,
            "Severity": "Normal"
        }
    )


    st.rerun()
st.sidebar.subheader("Link Parameters")

st.sidebar.markdown("### Link A → B")

ab_fidelity = st.sidebar.slider(
    "A-B Fidelity",
    min_value=0.00,
    max_value=1.00,
    value=0.90,
    step=0.01,
    key="ab_fidelity_slider",
)

ab_noise = st.sidebar.slider(
    "A-B Noise",
    min_value=0.00,
    max_value=1.00,
    value=0.20,
    step=0.01,
    key="ab_noise_slider",
)

st.sidebar.markdown("### Link B → C")

bc_fidelity = st.sidebar.slider(
    "B-C Fidelity",
    min_value=0.00,
    max_value=1.00,
    value=0.85,
    step=0.01,
    key="bc_fidelity_slider",
)

bc_noise = st.sidebar.slider(
    "B-C Noise",
    min_value=0.00,
    max_value=1.00,
    value=0.30,
    step=0.01,
    key="bc_noise_slider",
)

st.sidebar.markdown("### Link A → D")

ad_fidelity = st.sidebar.slider(
    "A-D Fidelity",
    min_value=0.00,
    max_value=1.00,
    value=0.95,
    step=0.01,
    key="ad_fidelity_slider",
)

ad_noise = st.sidebar.slider(
    "A-D Noise",
    min_value=0.00,
    max_value=1.00,
    value=0.10,
    step=0.01,
    key="ad_noise_slider",
)

st.sidebar.markdown("### Link D → C")

dc_fidelity = st.sidebar.slider(
    "D-C Fidelity",
    min_value=0.00,
    max_value=1.00,
    value=0.92,
    step=0.01,
    key="dc_fidelity_slider",
)

dc_noise = st.sidebar.slider(
    "D-C Noise",
    min_value=0.00,
    max_value=1.00,
    value=0.15,
    step=0.01,
    key="dc_noise_slider",
)

st.sidebar.divider()

fidelity_threshold = st.sidebar.slider(
    "Minimum Fidelity",
    min_value=0.50,
    max_value=1.00,
    value=0.88,
    step=0.01,
    key="fidelity_threshold_slider",
)

noise_threshold = st.sidebar.slider(
    "Maximum Noise",
    min_value=0.00,
    max_value=1.00,
    value=0.25,
    step=0.01,
    key="noise_threshold_slider",
)

source_node = st.sidebar.selectbox(
    "Source Node",
    ["A", "B", "C", "D"],
    index=0,
    key="source_node_selectbox",
)

target_node = st.sidebar.selectbox(
    "Target Node",
    ["A", "B", "C", "D"],
    index=2,
    key="target_node_selectbox",
)

if source_node == target_node:
    st.error(
        "Source Node and Target Node cannot be the same."
    )

    st.stop()

header_column_1, header_column_2 = st.columns(
    [1, 4]
)

with header_column_1:
    st.image(
        "quantumroute_doctor_logo.jpg",
        width=130
    )

with header_column_2:
    st.title(
        "QuantumRoute Doctor"
    )

    st.write(
        "A diagnostic and smart routing support system "
        "for quantum networks."
    )

quantum_network = create_quantum_network(
    ab_fidelity,
    ab_noise,
    bc_fidelity,
    bc_noise,
    ad_fidelity,
    ad_noise,
    dc_fidelity,
    dc_noise,
)

faulty_edges = scan_faulty_links(
    quantum_network,
    fidelity_threshold,
    noise_threshold,
)

if source_node == target_node:
    safe_route = None
else:
    safe_route = find_safe_route(
        quantum_network,
        source_node,
        target_node,
        faulty_edges,
    )


# =========================================================
# 7. NETWORK SUMMARY
# =========================================================
st.subheader("Network Summary")

summary_column_1, summary_column_2 = st.columns(2)

summary_column_1.metric(
    "Total Nodes",
    quantum_network.number_of_nodes(),
)

summary_column_2.metric(
    "Total Links",
    quantum_network.number_of_edges(),
)


# =========================================================
# 8. NETWORK DIAGNOSIS
# =========================================================
st.subheader("Network Diagnosis")

if faulty_edges:
    st.error(
        f"Faulty links detected: {faulty_edges}"
    )
else:
    st.success(
        "No faulty links detected."
    )

link_diagnosis = create_link_diagnosis(
    quantum_network,
    fidelity_threshold,
    noise_threshold,
)

st.write("Detailed link diagnosis:")

diagnosis_dataframe = pd.DataFrame(
    link_diagnosis
)

st.dataframe(
    diagnosis_dataframe,
    use_container_width=True,
    hide_index=True,
)

diagnosis_csv = diagnosis_dataframe.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Diagnostic Report",
    data=diagnosis_csv,
    file_name="quantum_network_diagnosis.csv",
    mime="text/csv",
    key="download_diagnostic_report",
)


# =========================================================
# 9. OVERALL NETWORK HEALTH
# =========================================================
healthy_count = sum(
    1
    for item in link_diagnosis
    if item["Status"] == "HEALTHY"
)

faulty_count = sum(
    1
    for item in link_diagnosis
    if item["Status"] == "FAULTY"
)

total_links = len(link_diagnosis)

if total_links > 0:
    network_health_percentage = (
        healthy_count / total_links
    ) * 100
else:
    network_health_percentage = 0.0
st.subheader("🩺 Network Diagnosis Report")

diagnosis_text = generate_diagnosis_explanation(
    faulty_edges,
    safe_route,
    quantum_network,
)


for text in diagnosis_text:

    if "Fault detected" in text:
        st.error(text)

    elif "Problem" in text:
        st.warning(text)

    elif "Recommended route" in text:
        st.success(text)

    else:
        st.write(text)

st.subheader("Overall Network Health")

health_column_1, health_column_2, health_column_3 = (
    st.columns(3)
)

health_column_1.metric(
    "Healthy Links",
    healthy_count,
)

health_column_2.metric(
    "Faulty Links",
    faulty_count,
)

health_column_3.metric(
    "Network Health",
    f"{network_health_percentage:.1f}%",
)

if network_health_percentage >= 80:
    st.success(
        "Network Status: GOOD — Most links are operating safely."
    )
elif network_health_percentage >= 50:
    st.warning(
        "Network Status: WARNING — Some links require attention."
    )
else:
    st.error(
        "Network Status: CRITICAL — "
        "Immediate network repair is recommended."
    )


# =========================================================
# 10. ROUTE RECOMMENDATION
# =========================================================
st.subheader("Route Recommendation")

if source_node == target_node:
    st.warning(
        "Source node and target node must be different."
    )

elif safe_route:
    route_fidelity, route_noise, health_score = (
        calculate_route_metrics(
            quantum_network,
            safe_route,
        )
    )

    route_text = " → ".join(safe_route)

    st.success(
        f"Recommended safe route: {route_text}"
    )

    route_column_1, route_column_2, route_column_3 = (
        st.columns(3)
    )

    route_column_1.metric(
        "Route Fidelity",
        f"{route_fidelity:.3f}",
    )

    route_column_2.metric(
        "Route Noise",
        f"{route_noise:.3f}",
    )

    route_column_3.metric(
        "Health Score",
        f"{health_score:.3f}",
    )

else:
    st.error(
        "No safe route is available between "
        "the selected source and target nodes."
    )
st.subheader("Diagnosis History")

if st.session_state["diagnosis_history"]:

    history_dataframe = pd.DataFrame(
        st.session_state["diagnosis_history"]
    )

    st.dataframe(
        history_dataframe,
        use_container_width=True
    )

else:

    st.info(
        "No diagnosis history available."
    )

# =========================================================
# 11. ALL ROUTE COMPARISON
# =========================================================
st.subheader("All Route Comparison")

if source_node != target_node:
    route_results = compare_all_routes(
        quantum_network,
        source_node,
        target_node,
    )

    if not route_results:
        st.warning(
            "No route exists between the selected source and target nodes."
        )
        st.stop()

    route_results = add_route_safety_status(
        route_results,
        faulty_edges,
    )

    safe_route_count = sum(
        1
        for route_result in route_results
        if route_result["Safety Status"] == "SAFE"
    )

    unsafe_route_count = sum(
        1
        for route_result in route_results
        if route_result["Safety Status"] == "UNSAFE"
    )

    count_column_1, count_column_2 = st.columns(2)

    count_column_1.metric(
        "Safe Routes",
        safe_route_count,
    )

    count_column_2.metric(
        "Unsafe Routes",
        unsafe_route_count,
    )

    if route_results:
        best_route = route_results[0]

        st.success(
            f"Best route by health score: "
            f"{best_route['Route']}"
        )

        st.write("Recommendation reason:")

        st.write(
            f"This route has the highest health score "
            f"({best_route['Health Score']}) "
            f"among all available routes."
        )

        best_route_nodes = best_route["Route"].split(" → ")

        if safe_route and best_route_nodes == safe_route:
            st.info(
                "The best route is also the recommended safe route."
            )
        else:
            st.warning(
                "The highest-health route is different from "
                "the recommended safe route."
            )
ranked_routes = rank_routes(
    route_results
)

best_route = ranked_routes[0]

best_route_reasons = explain_best_route(
    best_route,
    faulty_edges,
)
st.subheader("🧠 Why This Route Was Selected")

for reason in best_route_reasons:
    st.success(
        "✓ " + reason
    )

st.subheader("📊 Best Route Summary")

summary_column_1, summary_column_2, summary_column_3, summary_column_4 = st.columns(4)

with summary_column_1:
    st.metric(
        "Selected Route",
        best_route["Route"]
    )

with summary_column_2:
    st.metric(
        "Health Score",
        f"{best_route['Health Score']:.3f}"
    )

with summary_column_3:
    st.metric(
        "Fidelity",
        f"{best_route['Fidelity']:.3f}"
    )

with summary_column_4:
    st.metric(
        "Noise",
        f"{best_route['Noise']:.3f}"
    )
    st.subheader("🚦 Routing Decision")

if best_route["Safety Status"] == "SAFE":

    if best_route["Route Quality"] == "EXCELLENT":
        st.success(
            "Approved: This route is safe and has excellent quality."
        )

    elif best_route["Route Quality"] == "GOOD":
        st.success(
            "Approved: This route is safe and has acceptable quality."
        )

    else:
        st.warning(
            "Caution: This route is safe, but its quality is low."
        )

else:

    st.error(
        "Rejected: The best available route contains a faulty link."
    )
report_file_id = datetime.now().strftime(
    "QRD-%Y%m%d-%H%M%S"
)

professional_text_report = generate_professional_text_report(
    faulty_edges,
    diagnosis_text,
    ranked_routes,
)

st.subheader("📄 Export Professional Report")

st.download_button(
    label="Download Professional TXT Report",
    data=professional_text_report,
    file_name=f"quantumroute_doctor_{report_file_id}.txt",
    mime="text/plain",
    key="download_professional_text_report",
)
professional_html_report = generate_professional_html_report(
    faulty_edges,
    diagnosis_text,
    ranked_routes,
)

st.download_button(
    label="Download Professional HTML Report",
    data=professional_html_report,
    file_name=f"quantumroute_doctor_{report_file_id}.html",
    mime="text/html",
    key="download_professional_html_report",
)

st.subheader("🏆 Route Ranking")


for index, route in enumerate(
    ranked_routes,
    start=1
):

    st.write(
    f"""
### Rank {index}

Route:
{route['Route']}

Health Score:
{route['Health Score']:.3f}

Safety:
{route['Safety Status']}

Quality:
{route['Route Quality']}
"""
)

route_dataframe = pd.DataFrame(
            route_results
        )

styled_route_table = (
            route_dataframe.style
            .map(
                color_route_quality,
                subset=["Route Quality"],
            )
            .map(
                color_safety_status,
                subset=["Safety Status"],
            )
        )
st.dataframe(
                styled_route_table,
                use_container_width=True,
                hide_index=True,
            )

route_csv = route_dataframe.to_csv(
            index=False
        ).encode("utf-8")

st.download_button(
            label="Download Route Comparison",
            data=route_csv,
            file_name="quantum_route_comparison.csv",
            mime="text/csv",
            key="download_route_comparison",
        )


# ==========================================
# 12. NETWORK VISUALIZATION
# ==========================================

diagnosis_text = generate_diagnosis_explanation(
    faulty_edges,
    safe_route,
    quantum_network,
)

st.subheader("Quantum Network Visualization")

network_figure = create_network_figure(
    quantum_network,
    safe_route,
    faulty_edges,
)

st.pyplot(
    network_figure,
    use_container_width=True,
)

plt.close(network_figure)