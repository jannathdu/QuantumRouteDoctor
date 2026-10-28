import type { FidelityDecayPoint } from "../api/fidelityDecay";

type Props = {
  points: FidelityDecayPoint[];
};

export default function FidelityDecayChart({ points }: Props) {
  if (points.length < 2) {
    return <p>No fidelity decay data available.</p>;
  }

  const width = 700;
  const height = 320;
  const margin = { left: 55, right: 20, top: 20, bottom: 45 };

  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const maxTime = Math.max(
    1,
    ...points.map((point) => point.storage_time)
  );

  const scaleX = (time: number) =>
    margin.left + (time / maxTime) * chartWidth;

  const scaleY = (fidelity: number) =>
    margin.top + (1 - fidelity) * chartHeight;

  const path = points
    .map((point, index) =>
      `${index === 0 ? "M" : "L"} ${scaleX(point.storage_time)} ${scaleY(point.predicted_fidelity)}`
    )
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Predicted fidelity versus quantum memory storage time"
      style={{ width: "100%", maxWidth: 800 }}
    >
      {[0, 0.25, 0.5, 0.75, 1].map((value) => (
        <g key={value}>
          <line
            x1={margin.left}
            y1={scaleY(value)}
            x2={width - margin.right}
            y2={scaleY(value)}
            stroke="#334155"
            strokeDasharray="4 4"
          />
          <text
            x={margin.left - 10}
            y={scaleY(value) + 4}
            fill="#cbd5e1"
            fontSize="12"
            textAnchor="end"
          >
            {value.toFixed(2)}
          </text>
        </g>
      ))}

      <line
        x1={margin.left}
        y1={margin.top}
        x2={margin.left}
        y2={height - margin.bottom}
        stroke="#94a3b8"
      />

      <line
        x1={margin.left}
        y1={height - margin.bottom}
        x2={width - margin.right}
        y2={height - margin.bottom}
        stroke="#94a3b8"
      />

      <path
        d={path}
        fill="none"
        stroke="#34d399"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      <text
        x={width / 2}
        y={height - 8}
        textAnchor="middle"
        fill="#e2e8f0"
        fontSize="14"
      >
        Storage Time (simulation units)
      </text>

      <text
        x="15"
        y={height / 2}
        transform={`rotate(-90 15 ${height / 2})`}
        textAnchor="middle"
        fill="#e2e8f0"
        fontSize="14"
      >
        Predicted Fidelity
      </text>
    </svg>
  );
}
