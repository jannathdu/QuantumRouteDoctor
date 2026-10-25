export type RouteResponse = {
  source: string;
  destination: string;
  minimum_fidelity: number;
  algorithm: string;
  feasible: boolean;
  selected_route: string[] | null;
  end_to_end_fidelity: number | null;
  hop_count: number | null;
  data_source: string;
};

export async function fetchRoute(
  source = "A",
  destination = "C",
  minimumFidelity = 0.8, signal?: AbortSignal
): Promise<RouteResponse> {
  const params = new URLSearchParams({
    source,
    destination,
    minimum_fidelity: String(minimumFidelity),
  });

  const response = await fetch(`/api/routes?${params.toString()}`, { signal });

  if (!response.ok) {
    throw new Error(`Routing API failed: HTTP ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid routing response");
  }

  const route = data as RouteResponse;

  if (
    typeof route.feasible !== "boolean" ||
    (route.selected_route !== null &&
      (!Array.isArray(route.selected_route) ||
        !route.selected_route.every((node) => typeof node === "string"))) ||
    (route.feasible && (!route.selected_route || route.selected_route.length < 2)) ||
    (!route.feasible && route.selected_route !== null)
  ) {
    throw new Error("Invalid routing result");
  }

  return route;
}
