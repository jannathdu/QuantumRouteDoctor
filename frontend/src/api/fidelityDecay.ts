export type FidelityDecayPoint = {
  storage_time: number;
  predicted_fidelity: number;
};

export type FidelityDecayResponse = {
  model: string;
  initial_fidelity: number;
  decoherence_rate: number;
  maximum_time: number;
  samples: number;
  points: FidelityDecayPoint[];
  data_source: string;
};

export async function fetchFidelityDecay(
  initialFidelity = 0.95,
  decoherenceRate = 0.03,
  maximumTime = 20,
  samples = 21,
  signal?: AbortSignal
): Promise<FidelityDecayResponse> {
  const params = new URLSearchParams({
    initial_fidelity: String(initialFidelity),
    decoherence_rate: String(decoherenceRate),
    maximum_time: String(maximumTime),
    samples: String(samples),
  });

  const response = await fetch(
    `/api/research/fidelity-decay?${params.toString()}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`Fidelity Decay API failed: HTTP ${response.status}`);
  }

  const data: unknown = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid fidelity decay response");
  }

  const result = data as FidelityDecayResponse;

  if (
    result.model !== "simplified_depolarizing_memory" ||
    !Array.isArray(result.points) ||
    result.points.length !== samples ||
    !result.points.every(
      (point) =>
        typeof point.storage_time === "number" &&
        Number.isFinite(point.storage_time) &&
        typeof point.predicted_fidelity === "number" &&
        Number.isFinite(point.predicted_fidelity) &&
        point.predicted_fidelity >= 0 &&
        point.predicted_fidelity <= 1
    )
  ) {
    throw new Error("Invalid fidelity decay data");
  }

  return result;
}
