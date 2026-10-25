import type { ComparisonResponse } from "../api/comparison";

type Props = {
  data: ComparisonResponse | null;
};

export default function ComparisonResults({ data }: Props) {
  if (!data) return null;

  const baseline = data.baseline;
  const temporal = data.temporal;

  const panelStyle = {
    flex: "1 1 250px",
    padding: 16,
    background: "#1e293b",
    borderRadius: 10,
  };

  return (
    <section style={{ padding: 16, background: "#0f172a", color: "#e2e8f0", borderRadius: 12, marginTop: 12 }}>
      <h3>Baseline vs Temporal Comparison</h3>
      <p>Source: {data.source} | Destination: {data.destination}</p>
      <p>Minimum Fidelity: {data.minimum_fidelity.toFixed(3)} | Maximum AoI: {data.maximum_aoi.toFixed(1)}</p>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <div style={panelStyle}>
          <h4>Fidelity-Constrained Baseline</h4>
          <p>Feasible: {baseline.feasible ? "Yes" : "No"}</p>
          <p>Route: {baseline.selected_route?.join(" → ") ?? "None"}</p>
          <p>End-to-End Fidelity: {baseline.end_to_end_fidelity?.toFixed(3) ?? "N/A"}</p>
          <p>Hop Count: {baseline.hop_count ?? "N/A"}</p>
          <p>AoI Constraint: Not applied</p>
        </div>

        <div style={panelStyle}>
          <h4>Temporal-State-Aware Routing</h4>
          <p>Feasible: {temporal.feasible ? "Yes" : "No"}</p>
          <p>Route: {temporal.selected_route?.join(" → ") ?? "None"}</p>
          <p>Predicted Fidelity: {temporal.predicted_fidelity?.toFixed(3) ?? "N/A"}</p>
          <p>Hop Count: {temporal.hop_count ?? "N/A"}</p>
          <p>Maximum Link AoI: {temporal.maximum_link_aoi?.toFixed(1) ?? "N/A"}</p>
        </div>
      </div>

      <p style={{ fontSize: 12, opacity: 0.75 }}>
        Synthetic demonstration: results use different fidelity assumptions and do not establish algorithm superiority.
      </p>
    </section>
  );
}
