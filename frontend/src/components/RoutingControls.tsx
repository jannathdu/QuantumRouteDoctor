import { useState } from "react";

type Props = {
  nodeIds: string[];
  onCalculate: (source: string, destination: string, minimumFidelity: number) => void;
};

export default function RoutingControls({ nodeIds, onCalculate }: Props) {
  const [source, setSource] = useState("A");
  const [destination, setDestination] = useState("C");
  const [minimumFidelity, setMinimumFidelity] = useState(0.8);

  const validNodes = nodeIds.includes(source) && nodeIds.includes(destination);
  const canCalculate = validNodes && source !== destination;

  return (
    <section style={{ padding: 16, background: "#0f172a", color: "#e2e8f0", borderRadius: 12, marginTop: 12 }}>
      <h3>Quantum Routing Controls</h3>

      <label>Source Node: </label>
      <select value={source} onChange={(event) => setSource(event.target.value)}>
        {nodeIds.map((id) => <option key={id} value={id}>{id}</option>)}
      </select>

      <label style={{ marginLeft: 12 }}>Destination Node: </label>
      <select value={destination} onChange={(event) => setDestination(event.target.value)}>
        {nodeIds.map((id) => <option key={id} value={id}>{id}</option>)}
      </select>

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
          onClick={() => onCalculate(source, destination, minimumFidelity)}
        >
          Calculate Route
        </button>
      </p>

      {!canCalculate && <p>Choose two different valid nodes.</p>}
    </section>
  );
}
