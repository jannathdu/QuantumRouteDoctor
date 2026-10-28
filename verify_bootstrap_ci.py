import json
import math
import random
from pathlib import Path

base = Path("results/research_reports")
source_path = base / "quantum_routing_combined_aoi_fidelity_sensitivity.json"
report_path = base / "quantum_routing_combined_statistical_inference.json"

source = json.loads(source_path.read_text(encoding="utf-8"))
report = json.loads(report_path.read_text(encoding="utf-8"))

if len(source["results"]) != 16 or len(report["results"]) != 16:
    raise SystemExit("FAIL: Expected exactly 16 combinations")

report_map = {
    (r["maximum_aoi"], r["minimum_fidelity"]): r
    for r in report["results"]
}

rng = random.Random(report["method"]["bootstrap_random_seed"])
errors = []

print("AoI | Fidelity | Stored CI | Recomputed CI | Check")

for item in source["results"]:
    key = (item["maximum_aoi"], item["minimum_fidelity"])
    stored = report_map.get(key)

    if stored is None:
        errors.append(f"Missing combination: {key}")
        continue

    pairs = {}
    for row in item["records"]:
        pair = pairs.setdefault(row["seed"], {})
        if row["algorithm"] in pair:
            errors.append(f"Duplicate record: {key}, seed={row['seed']}")
        pair[row["algorithm"]] = row["feasible"]

    if len(pairs) != 100 or any(
        set(pair) != {"baseline", "temporal"}
        for pair in pairs.values()
    ):
        errors.append(f"Incomplete pairs: {key}")
        continue

    differences = [
        int(pair["temporal"]) - int(pair["baseline"])
        for _, pair in sorted(pairs.items())
    ]
    n = len(differences)

    estimates = sorted(
        math.fsum(rng.choices(differences, k=n)) / n
        for _ in range(report["method"]["bootstrap_resamples"])
    )

    def percentile(q):
        pos = q * (len(estimates) - 1)
        lo, hi = math.floor(pos), math.ceil(pos)
        fraction = pos - lo
        return (
            estimates[lo] * (1 - fraction)
            + estimates[hi] * fraction
        )

    ci = [percentile(0.025), percentile(0.975)]
    saved_ci = stored["bootstrap_95_ci"]
    match = all(
        math.isclose(a, b, abs_tol=1e-12)
        for a, b in zip(ci, saved_ci)
    )

    if not match:
        print("  NOTE: CI discrepancy retained for review; report unchanged.")
        errors.append(
            f"CI mismatch at AoI={key[0]}, fidelity={key[1]}: "
            f"stored={saved_ci}, recomputed={ci}"
        )

    print(
        f"{key[0]:.1f} | {key[1]:.1f} | "
        f"{saved_ci} | {ci} | {'PASS' if match else 'REVIEW'}"
    )

print("Errors:", len(errors))
for error in errors:
    print("ERROR:", error)

print("FINAL:", "PASS" if not errors else "REVIEW REQUIRED")
