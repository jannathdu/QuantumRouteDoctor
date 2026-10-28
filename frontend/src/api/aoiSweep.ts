export type AoISweepPoint = {
  maximum_aoi: number;
  feasible: boolean;
  selected_route: string[] | null;
  predicted_fidelity: number | null;
  hop_count: number | null;
};

export type AoISweepResponse = {
  source: string;
  destination: string;
  minimum_fidelity: number;
  current_time: number;
  maximum_aoi: number;
  points: AoISweepPoint[];
  data_source: string;
};

export async function fetchAoISweep(
  source = "A",
  destination = "C",
  minimumFidelity = 0.8,
  maximumAoi = 10,
  currentTime = 10,
  signal?: AbortSignal
): Promise<AoISweepResponse> {
  const params = new URLSearchParams({
    source,
    destination,
    minimum_fidelity: String(minimumFidelity),
    maximum_aoi: String(maximumAoi),
    current_time: String(currentTime),
  });

  const response = await fetch(
    `/api/research/aoi-sweep?${params.toString()}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`AoI Sweep API failed: HTTP ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid AoI sweep response");
  }

  const result = data as AoISweepResponse;

  if (
    result.data_source !== "synthetic_demo" ||
    !Array.isArray(result.points) ||
    result.points.length !== maximumAoi + 1 ||
    !result.points.every((point, index) =>
      point.maximum_aoi === index &&
      typeof point.feasible === "boolean" &&
      (
        point.feasible
          ? Array.isArray(point.selected_route) &&
            typeof point.predicted_fidelity === "number" &&
            Number.isFinite(point.predicted_fidelity) &&
            point.predicted_fidelity >= 0.25 &&
            point.predicted_fidelity <= 1
          : point.selected_route === null &&
            point.predicted_fidelity === null
      )
    )
  ) {
    throw new Error("Invalid AoI sweep data");
  }

  return result;
}
