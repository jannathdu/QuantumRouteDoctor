import { useEffect, useRef, useState } from "react";
import {
  fetchFidelityDecay,
  type FidelityDecayResponse,
} from "../api/fidelityDecay";
import FidelityDecayChart from "./FidelityDecayChart";

export default function FidelityDecayPanel() {
  const [initialFidelity, setInitialFidelity] = useState(0.95);
  const [decoherenceRate, setDecoherenceRate] = useState(0.03);
  const [maximumTime, setMaximumTime] = useState(20);

  const [data, setData] = useState<FidelityDecayResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const controllerRef = useRef<AbortController | null>(null);

  function calculate(
    fidelity: number,
    rate: number,
    time: number
  ) {
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);
    setData(null);

    fetchFidelityDecay(
      fidelity,
      rate,
      time,
      21,
      controller.signal
    )
      .then((result) => {
        if (!controller.signal.aborted) {
          setData(result);
        }
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          setError(
            err instanceof Error
              ? err.message
              : "Fidelity calculation failed"
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });
  }

  useEffect(() => {
    calculate(0.95, 0.03, 20);

    return () => {
      controllerRef.current?.abort();
    };
  }, []);

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
      <h3>Research Visualization: Fidelity Decay</h3>

      <p>
        Simplified depolarizing-memory model.
        Results are analytical predictions, not measurements.
      </p>

      <div style={{ marginBottom: 14 }}>
        <label htmlFor="initial-fidelity">
          Initial Fidelity: {initialFidelity.toFixed(2)}
        </label>
        <input
          id="initial-fidelity"
          type="range"
          min="0.25"
          max="1"
          step="0.01"
          value={initialFidelity}
          onChange={(event) =>
            setInitialFidelity(Number(event.target.value))
          }
        />
      </div>

      <div style={{ marginBottom: 14 }}>
        <label htmlFor="decoherence-rate">
          Decoherence Rate: {decoherenceRate.toFixed(3)}
        </label>
        <input
          id="decoherence-rate"
          type="range"
          min="0"
          max="0.2"
          step="0.005"
          value={decoherenceRate}
          onChange={(event) =>
            setDecoherenceRate(Number(event.target.value))
          }
        />
      </div>

      <div style={{ marginBottom: 14 }}>
        <label htmlFor="maximum-time">
          Maximum Storage Time: {maximumTime}
        </label>
        <input
          id="maximum-time"
          type="range"
          min="1"
          max="100"
          step="1"
          value={maximumTime}
          onChange={(event) =>
            setMaximumTime(Number(event.target.value))
          }
        />
      </div>

      <button
        disabled={loading}
        onClick={() =>
          calculate(initialFidelity, decoherenceRate, maximumTime)
        }
      >
        {loading ? "Calculating..." : "Calculate Fidelity Decay"}
      </button>

      {error && (
        <p role="alert" style={{ color: "#f87171" }}>
          Research API Error: {error}
        </p>
      )}

      {data && (
        <>
          <FidelityDecayChart points={data.points} />
          <p>
            Initial: {data.points[0].predicted_fidelity.toFixed(4)}
            {" | "}
            Final: {data.points[data.points.length - 1].predicted_fidelity.toFixed(4)}
          </p>
          <p style={{ fontSize: 12, opacity: 0.75 }}>
            Data Source: {data.data_source}
          </p>
        </>
      )}
    </section>
  );
}
