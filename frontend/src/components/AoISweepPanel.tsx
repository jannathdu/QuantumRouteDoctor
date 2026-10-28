import { useEffect, useRef, useState } from "react";
import {
  fetchAoISweep,
  type AoISweepResponse,
} from "../api/aoiSweep";
import AoISweepChart from "./AoISweepChart";

type Props = {
  nodeIds: string[];
};

export default function AoISweepPanel({ nodeIds }: Props) {
  const [source, setSource] = useState("A");
  const [destination, setDestination] = useState("C");
  const [minimumFidelity, setMinimumFidelity] = useState(0.8);
  const [maximumAoI, setMaximumAoI] = useState(10);

  const [data, setData] = useState<AoISweepResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const controllerRef = useRef<AbortController | null>(null);

  const validNodes =
    nodeIds.includes(source) &&
    nodeIds.includes(destination) &&
    source !== destination;

  function calculate() {
    if (!validNodes) return;

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);
    setData(null);

    fetchAoISweep(
      source,
      destination,
      minimumFidelity,
      maximumAoI,
      10,
      controller.signal
    )
      .then((result) => {
        if (!controller.signal.aborted) setData(result);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error
              ? err.message
              : "AoI sweep request failed"
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
  }

  useEffect(() => {
    if (!nodeIds.includes("A") || !nodeIds.includes("C")) return;

    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);

    fetchAoISweep("A", "C", 0.8, 10, 10, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) setData(result);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error ? err.message : "AoI sweep failed"
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [nodeIds.length]);

  return (
    <section
      style={{
        padding: 20,
        marginTop: 16,
        background: "#0f172a",
        color: "#e2e8f0",
        borderRadius: 12,
      }}
    >
      <h3>Research Visualization: AoI vs Route Feasibility</h3>

      <p>
        Synthetic quantum network simulation showing how
        maximum allowed Age of Information affects routing.
      </p>

      <div style={{ marginBottom: 12 }}>
        <label htmlFor="aoi-source">Source: </label>
        <select
          id="aoi-source"
          value={source}
          onChange={(event) => setSource(event.target.value)}
        >
          {nodeIds.map((id) => (
            <option key={id} value={id}>{id}</option>
          ))}
        </select>

        <label htmlFor="aoi-destination" style={{ marginLeft: 12 }}>
          Destination:
        </label>
        <select
          id="aoi-destination"
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
        >
          {nodeIds.map((id) => (
            <option key={id} value={id}>{id}</option>
          ))}
        </select>
      </div>

      <p>Minimum Fidelity: {minimumFidelity.toFixed(2)}</p>
      <input
        type="range"
        min="0.25"
        max="1"
        step="0.01"
        value={minimumFidelity}
        onChange={(event) =>
          setMinimumFidelity(Number(event.target.value))
        }
      />

      <p>Maximum AoI Sweep Range: 0 to {maximumAoI}</p>
      <input
        type="range"
        min="1"
        max="20"
        step="1"
        value={maximumAoI}
        onChange={(event) =>
          setMaximumAoI(Number(event.target.value))
        }
      />

      <p>
        <button disabled={!validNodes || loading} onClick={calculate}>
          {loading ? "Calculating..." : "Calculate AoI Sweep"}
        </button>
      </p>

      {!validNodes && <p>Select two different valid nodes.</p>}

      {error && (
        <p role="alert" style={{ color: "#f87171" }}>
          Research API Error: {error}
        </p>
      )}

      {data && (
        <>
          <AoISweepChart points={data.points} />

          <h4>AoI Threshold Results</h4>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", textAlign: "left" }}>
              <thead>
                <tr>
                  <th>Maximum AoI</th>
                  <th>Feasible</th>
                  <th>Selected Route</th>
                  <th>Predicted Fidelity</th>
                </tr>
              </thead>
              <tbody>
                {data.points.map((point) => (
                  <tr key={point.maximum_aoi}>
                    <td>{point.maximum_aoi}</td>
                    <td>{point.feasible ? "Yes" : "No"}</td>
                    <td>
                      {point.selected_route?.join(" -> ") ?? "None"}
                    </td>
                    <td>
                      {point.predicted_fidelity?.toFixed(6) ?? "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p style={{ fontSize: 12, opacity: 0.75 }}>
            Data source: {data.data_source}. Synthetic demonstration,
            not experimental measurements.
          </p>
        </>
      )}
    </section>
  );
}
