import json
from pathlib import Path

from backend.core.three_algorithm_inference import (
    analyze_three_algorithm_inference,
)

base = Path("results/research_reports/three_algorithm_aoi_fidelity_sensitivity")
summary_path = base / "three_algorithm_summary.json"
output_path = base / "three_algorithm_statistical_inference.json"

if not summary_path.exists():
    raise FileNotFoundError(f"Summary not found: {summary_path}")

summary = json.loads(summary_path.read_text(encoding="utf-8"))

if len(summary.get("results", [])) != 16:
    raise ValueError("Expected exactly 16 parameter combinations")

inference = analyze_three_algorithm_inference(summary, alpha=0.05)

if inference["family_size"] != 48:
    raise ValueError(
        f"Expected 48 pairwise tests, got {inference['family_size']}"
    )

output_path.write_text(
    json.dumps(inference, indent=2, ensure_ascii=False, allow_nan=False),
    encoding="utf-8",
)

print("=== INFERENCE REPORT GENERATED ===")
print("Parameter combinations:", inference["parameter_combinations"])
print("Pairwise tests:", inference["family_size"])
print("Correction:", inference["correction"])
print("Alpha:", inference["alpha"])
print("Significant after Holm:", sum(
    item["significant_after_holm"]
    for item in inference["comparisons"]
))
print("Report:", output_path)

print("\n=== PAIRWISE RESULTS ===")
for item in inference["comparisons"]:
    print(
        f"AoI={item['maximum_aoi']:.1f}, "
        f"Fidelity={item['minimum_fidelity']:.1f}, "
        f"{item['comparison']}: "
        f"p={item['p_value']:.8g}, "
        f"Holm p={item['holm_adjusted_p_value']:.8g}, "
        f"significant={item['significant_after_holm']}"
    )

print("\nFINAL: PASS")
