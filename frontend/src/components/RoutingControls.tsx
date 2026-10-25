import { useState } from "react";

type Props = {
  nodeIds: string[];
  onCalculate: (source: string, destination: string, minimumFidelity: number, algorithm: "baseline" | "temporal", maximumAoi: number) => void;
};

export default function RoutingControls({ nodeIds, onCalculate }: Props) {
  const [source, setSource] = useState("A");
  const [destination, setDestination] = useState("C");
  const [minimumFidelity, setMinimumFidelity] = useState(0.8);
  const [algorithm, setAlgorithm] = useState<"baseline" | "temporal">("baseline");
  const [maximumAoi, setMaximumAoi] = useState(10);

  const validNodes = nodeIds.includes(source) && nodeIds.includes(destination);
  const canCalculate = validNodes && source !== destination;

  return (
    <section style={{ padding: 16, background: "#0f172a", color: "#e2e8f0", borderRadius: 12, marginTop: 12 }}>
      <h3>Quantum Routing Controls</h3>
      <div style={{ marginBottom: 12 }}>
        <label htmlFor="routing-algorithm">Routing Algorithm: </label>
        <select
          id="routing-algorithm"
          value={algorithm}
          onChange={(event) =>
            setAlgorithm(event.target.value as "baseline" | "temporal")
          }
        >
          <option value="baseline">Fidelity-Constrained Baseline</option>
          <option value="temporal">Temporal-State-Aware Routing</option>
        </select>
      </div>

      <label>Source Node: </label>
      <select value={source} onChange={(event) => setSource(event.target.value)}>
        {nodeIds.map((id) => <option key={id} value={id}>{id}</option>)}
      </select>

      <label style={{ marginLeft: 12 }}>Destination Node: </label>
      <select value={destination} onChange={(event) => setDestination(event.target.value)}>
        {nodeIds.map((id) => <option key={id} value={id}>{id}</option>)}
      </select>

            {algorithm === "temporal" && (
        <div style={{ marginTop: 12 }}>
          <label htmlFor="maximum-aoi">
            Maximum AoI: {maximumAoi.toFixed(1)}
          </label>
          <input
            id="maximum-aoi"
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={maximumAoi}
            onChange={(event) => setMaximumAoi(Number(event.target.value))}
          />
        </div>
      )}
      <p>Minimum Fidelity: {minimumFidelity.toFixed(2)}</p>
      <input
        type="range"
        min="0.25"
        max="1"
        step="0.01"
        value={minimumFidelity}
        onChange={(event) => setMinimumFidelity(Number(event.target.value))}
      />

      <p>
        <button
          disabled={!canCalculate}
          onClick={() => onCalculate(source, destination, minimumFidelity, algorithm, maximumAoi)}
        >
          Calculate Route
        </button>
      </p>

      {!canCalculate && <p>Choose two different valid nodes.</p>}
    </section>
  );
}
