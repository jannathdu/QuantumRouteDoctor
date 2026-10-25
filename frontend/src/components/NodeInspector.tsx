import type { NetworkResponse } from "../api/network";
type Props = { selectedNode: string | null; networkData: NetworkResponse | null };
export default function NodeInspector({ selectedNode, networkData }: Props) {
if (!selectedNode) return <aside style={{ padding: 20, color: "#94a3b8" }}>Click a quantum node to inspect its connections.</aside>;
const connectedLinks = (networkData?.links ?? []).filter((link) => link.source === selectedNode || link.target === selectedNode);
const neighbors = [...new Set(connectedLinks.map((link) => link.source === selectedNode ? link.target : link.source))]; const roles: Record<string, string> = { A: "Source", B: "Repeater", C: "Destination", D: "Alternative Repeater" };
return <aside style={{ padding: 20, color: "#e2e8f0", background: "#111c30", borderRadius: 12 }}>
<h2>Node Inspector: {selectedNode}</h2>
<p>Role: {roles[selectedNode] ?? "Unknown"}</p>
<p>Connected Nodes: {neighbors.join(", ") || "None"}</p>
<p>Connection Count: {neighbors.length}</p><h3>Connected Link Diagnostics</h3>{connectedLinks.map((link) => <div key={`${link.source}-${link.target}`} style={{ padding: 10, marginBottom: 8, background: "#1e293b", borderRadius: 8 }}><strong>{link.source} - {link.target}</strong><p>Noise: {link.noise.toFixed(3)}</p></div>)}
</aside>; }
