export type NetworkNode = { id: string };
export type NetworkLink = { source: string; target: string; fidelity: number; noise: number; age: number };
export type NetworkResponse = { nodes: NetworkNode[]; links: NetworkLink[]; data_source: string };
export async function fetchNetwork(): Promise<NetworkResponse> {
  const response = await fetch("/api/network");
  if (!response.ok) throw new Error(`Network API failed: HTTP ${response.status}`);
  const data: unknown = await response.json();
  if (!data || typeof data !== "object" || !("nodes" in data) || !("links" in data)) throw new Error("Invalid network response");
  const network = data as NetworkResponse;
  if (!Array.isArray(network.nodes) || !Array.isArray(network.links)) throw new Error("Invalid network topology");
  return network;
}
