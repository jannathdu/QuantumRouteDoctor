import type { NetworkResponse } from "../api/network";
type Props = { data: NetworkResponse | null; loading: boolean; error: string | null };
export default function NetworkStatus({ data, loading, error }: Props) {
  if (loading) return <p>Connecting to Python backend...</p>;
  if (error) return <p style={{ color: "#f87171" }}>Backend connection failed: {error}</p>;
  if (!data) return <p>No network data available.</p>;
  return <section style={{ padding: 16, background: "#111c30", borderRadius: 12, color: "#e2e8f0" }}>
    <strong style={{ color: "#34d399" }}>Backend Connected</strong>
    <p>Nodes: {data.nodes.length} | Links: {data.links.length}</p>
    <p>Data Source: {data.data_source}</p>
  </section>;
}
