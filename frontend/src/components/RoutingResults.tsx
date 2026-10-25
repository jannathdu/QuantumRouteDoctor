import type { RouteResponse } from "../api/routes";

type Props = {
  route: RouteResponse | null;
};

export default function RoutingResults({ route }: Props) {
  if (!route) {
    return <aside><h3>Routing Results</h3><p>Loading route...</p></aside>;
  }

  return (
    <aside style={{ padding: 16, background: "#0f172a", color: "#e2e8f0", borderRadius: 12, marginTop: 12 }}>
      <h3>Routing Results</h3>
      <p>Algorithm: {route.algorithm}</p>
      <p>Source: {route.source}</p>
      <p>Destination: {route.destination}</p>
      <p>Minimum Fidelity: {route.minimum_fidelity.toFixed(3)}</p>
      <p>Feasible: {route.feasible ? "Yes" : "No"}</p>
      <p>Selected Route: {route.selected_route?.join(" → ") ?? "None"}</p>
      <p>End-to-End Fidelity: {route.end_to_end_fidelity?.toFixed(3) ?? "N/A"}</p>
      <p>Hop Count: {route.hop_count ?? "N/A"}</p>
      <p>Data Source: {route.data_source}</p>
    </aside>
  );
}
