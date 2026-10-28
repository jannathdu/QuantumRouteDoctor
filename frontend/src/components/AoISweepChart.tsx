import type { AoISweepPoint } from "../api/aoiSweep";

type Props = {
  points: AoISweepPoint[];
};

export default function AoISweepChart({ points }: Props) {
  if (points.length === 0) {
    return <p>No AoI sweep data available.</p>;
  }

  const width = 700;
  const height = 320;
  const margin = { left: 55, right: 20, top: 25, bottom: 55 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const maxAoI = Math.max(1, ...points.map((p) => p.maximum_aoi));

  const scaleX = (aoi: number) =>
    margin.left + (aoi / maxAoI) * chartWidth;

  const scaleY = (value: number) =>
    margin.top + (1 - value) * chartHeight;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Route feasibility across maximum Age of Information thresholds"
      style={{ width: "100%", maxWidth: 800 }}
    >
      {[0, 1].map((value) => (
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
            textAnchor="end"
            fontSize="12"
            fill="#cbd5e1"
          >
            {value === 1 ? "Feasible" : "Infeasible"}
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

      {points.map((point, index) => {
        const previous = points[index - 1];

        return (
          <g key={point.maximum_aoi}>
            {previous && (
              <line
                x1={scaleX(previous.maximum_aoi)}
                y1={scaleY(previous.feasible ? 1 : 0)}
                x2={scaleX(point.maximum_aoi)}
                y2={scaleY(previous.feasible ? 1 : 0)}
                stroke="#34d399"
                strokeWidth="2"
              />
            )}
            {previous && previous.feasible !== point.feasible && (
              <line
                x1={scaleX(point.maximum_aoi)}
                y1={scaleY(previous.feasible ? 1 : 0)}
                x2={scaleX(point.maximum_aoi)}
                y2={scaleY(point.feasible ? 1 : 0)}
                stroke="#34d399"
                strokeWidth="2"
              />
            )}
            <circle
              cx={scaleX(point.maximum_aoi)}
              cy={scaleY(point.feasible ? 1 : 0)}
              r="5"
              fill={point.feasible ? "#34d399" : "#f87171"}
            />
            <text
              x={scaleX(point.maximum_aoi)}
              y={height - margin.bottom + 18}
              fontSize="11"
              textAnchor="middle"
              fill="#cbd5e1"
            >
              {point.maximum_aoi}
            </text>
          </g>
        );
      })}

      <text
        x={width / 2}
        y={height - 8}
        textAnchor="middle"
        fontSize="14"
        fill="#e2e8f0"
      >
        Maximum Allowed AoI
      </text>
    </svg>
  );
}
