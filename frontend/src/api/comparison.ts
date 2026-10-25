import type { RouteResponse } from "./routes";
import type { TemporalRouteResponse } from "./temporalRoutes";

export type ComparisonResponse = {
  source: string;
  destination: string;
  minimum_fidelity: number;
  maximum_aoi: number;
  current_time: number;
  baseline: RouteResponse;
  temporal: TemporalRouteResponse;
  data_source: string;
};

export async function fetchComparison(
  source = "A",
  destination = "C",
  minimumFidelity = 0.8,
  maximumAoi = 10,
  signal?: AbortSignal
): Promise<ComparisonResponse> {
  const params = new URLSearchParams({
    source,
    destination,
    minimum_fidelity: String(minimumFidelity),
    maximum_aoi: String(maximumAoi),
    current_time: "10",
  });

  const response = await fetch(
    `/api/routes/compare?${params.toString()}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`Comparison API failed: HTTP ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid comparison response");
  }

  const result = data as ComparisonResponse;

  if (
    !result.baseline ||
    !result.temporal ||
    typeof result.baseline.feasible !== "boolean" ||
    typeof result.temporal.feasible !== "boolean"
  ) {
    throw new Error("Invalid comparison results");
  }

  return result;
}
