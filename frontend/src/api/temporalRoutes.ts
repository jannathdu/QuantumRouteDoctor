export type TemporalRouteResponse = {
  source: string;
  destination: string;
  current_time: number;
  minimum_fidelity: number;
  maximum_aoi: number;
  algorithm: string;
  feasible: boolean;
  selected_route: string[] | null;
  predicted_fidelity: number | null;
  maximum_link_aoi: number | null;
  hop_count: number | null;
  data_source: string;
};

export async function fetchTemporalRoute(
  source = "A",
  destination = "C",
  minimumFidelity = 0.8,
  maximumAoi = 10,
  currentTime = 10,
  signal?: AbortSignal
): Promise<TemporalRouteResponse> {
  const params = new URLSearchParams({
    source,
    destination,
    minimum_fidelity: String(minimumFidelity),
    maximum_aoi: String(maximumAoi),
    current_time: String(currentTime),
  });

  const response = await fetch(
    `/api/routes/temporal?${params.toString()}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`Temporal Routing API failed: HTTP ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid temporal routing response");
  }

  const result = data as TemporalRouteResponse;

  if (
    typeof result.feasible !== "boolean" ||
    (result.selected_route !== null &&
      (!Array.isArray(result.selected_route) ||
        !result.selected_route.every((node) => typeof node === "string"))) ||
    (result.feasible &&
      (!result.selected_route || result.selected_route.length < 2)) ||
    (!result.feasible && result.selected_route !== null)
  ) {
    throw new Error("Invalid temporal routing result");
  }

  return result;
}
