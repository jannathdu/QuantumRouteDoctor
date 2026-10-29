from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
FIGURE_DIR = (
    BASE_DIR
    / "results"
    / "research_reports"
    / "three_algorithm_aoi_fidelity_sensitivity"
    / "figures"
)

CSV_PATH = FIGURE_DIR / "feasibility_summary.csv"

ALGORITHMS = {
    "baseline": "Baseline Routing",
    "memory_aware": "Memory-Aware Routing",
    "temporal": "Temporal Routing",
}


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    data = pd.read_csv(CSV_PATH)

    required = {
        "maximum_aoi",
        "minimum_fidelity",
        "algorithm",
        "scenario_count",
        "feasibility_rate",
        "ci95_lower",
        "ci95_upper",
    }

    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    if data.empty or data[list(required)].isna().any().any():
        raise ValueError("CSV is empty or contains missing required values")

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    fidelity_values = sorted(data["minimum_fidelity"].unique())

    for algorithm, title in ALGORITHMS.items():
        subset = data[data["algorithm"] == algorithm]

        if subset.empty:
            raise ValueError(f"No data found for {algorithm}")

        fig, ax = plt.subplots(figsize=(10, 6))

        for fidelity in fidelity_values:
            group = subset[
                subset["minimum_fidelity"] == fidelity
            ].sort_values("maximum_aoi")

            if group.empty:
                continue

            x = group["maximum_aoi"].to_numpy()
            y = group["feasibility_rate"].to_numpy()
            lower = group["ci95_lower"].to_numpy()
            upper = group["ci95_upper"].to_numpy()

            ax.plot(
                x,
                y,
                marker="o",
                linewidth=2,
                label=f"Minimum fidelity = {fidelity:.1f}",
            )

            ax.fill_between(
                x,
                lower,
                upper,
                alpha=0.12,
            )

        ax.set_title(f"{title}: Feasibility vs. AoI Threshold")
        ax.set_xlabel("Maximum Age of Information (AoI)")
        ax.set_ylabel("Route Feasibility Rate")
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted(subset["maximum_aoi"].unique()))
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()

        output = FIGURE_DIR / f"{algorithm}_feasibility_vs_aoi.png"
        fig.savefig(output, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Saved: {output.relative_to(BASE_DIR)}")

    print("\nGRAPH GENERATION: PASS")


if __name__ == "__main__":
    main()
