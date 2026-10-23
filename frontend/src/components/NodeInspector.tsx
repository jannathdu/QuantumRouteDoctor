type Props = { selectedNode: string | null };
const connections: Record<string, string[]> = { A: ["B", "D"], B: ["A", "C"], C: ["B", "D"], D: ["A", "C"] };
export default function NodeInspector({ selectedNode }: Props) {
if (!selectedNode) return <aside style={{ padding: 20, color: "#94a3b8" }}>Click a quantum node to inspect its connections.</aside>;
const neighbors = connections[selectedNode] ?? [];
const roles: Record<string, string> = { A: "Source", B: "Repeater", C: "Destination", D: "Alternative Repeater" };
return <aside style={{ padding: 20, color: "#e2e8f0", background: "#111c30", borderRadius: 12 }}>
<h2>Node Inspector: {selectedNode}</h2>
<p>Role: {roles[selectedNode] ?? "Unknown"}</p>
<p>Connected Nodes: {neighbors.join(", ") || "None"}</p>
<p>Connection Count: {neighbors.length}</p>
</aside>; }
