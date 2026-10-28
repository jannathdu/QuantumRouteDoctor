import json
import math
from pathlib import Path

source_path = Path(
    "results/research_reports/"
    "quantum_routing_combined_aoi_fidelity_sensitivity.json"
)
inference_path = Path(
    "results/research_reports/"
    "quantum_routing_combined_statistical_inference.json"
)

source = json.loads(source_path.read_text(encoding="utf-8"))
inference = json.loads(inference_path.read_text(encoding="utf-8"))

def exact_mcnemar(baseline_only, temporal_only):
    n = baseline_only + temporal_only
    if n == 0:
        return 1.0
    k = min(baseline_only, temporal_only)
    return min(
        1.0,
        2.0 * sum(
            math.comb(n, i) * (0.5 ** n)
            for i in range(k + 1)
        ),
    )

def close(a, b, tol=1e-10):
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol)

source_results = source["results"]
inference_results = inference["results"]

if len(source_results) != 16 or len(inference_results) != 16:
    raise SystemExit(
        "FAIL: Expected exactly 16 source and inference combinations"
    )

errors = []

print("AoI | Fidelity | Pairs | Difference | McNemar p | Check")

for s, r in zip(source_results, inference_results):
    if (
        s["maximum_aoi"] != r["maximum_aoi"]
        or s["minimum_fidelity"] != r["minimum_fidelity"]
    ):
        errors.append("Parameter combination order mismatch")
        continue

    records = s["records"]
    paired = {}

    for row in records:
        paired.setdefault(row["seed"], {})[row["algorithm"]] = row["feasible"]

    if len(paired) != 100 or any(
        set(pair) != {"baseline", "temporal"}
        for pair in paired.values()
    ):
        errors.append(
            f"Incomplete pairs: AoI={s['maximum_aoi']}, "
            f"Fidelity={s['minimum_fidelity']}"
        )
        continue

    outcomes = {
        "both_feasible": 0,
        "baseline_only": 0,
        "temporal_only": 0,
        "neither_feasible": 0,
    }

    for pair in paired.values():
        b, t = pair["baseline"], pair["temporal"]
        if b and t:
            outcomes["both_feasible"] += 1
        elif b:
            outcomes["baseline_only"] += 1
        elif t:
            outcomes["temporal_only"] += 1
        else:
            outcomes["neither_feasible"] += 1

    difference = (
        sum(p["temporal"] for p in paired.values())
        - sum(p["baseline"] for p in paired.values())
    ) / 100

    p_value = exact_mcnemar(
        outcomes["baseline_only"],
        outcomes["temporal_only"],
    )

    summary = s["paired_inference"]
    checks = (
        outcomes == summary["paired_outcomes"]
        and close(difference, summary["paired_feasibility_difference"])
        and close(p_value, summary["mcnemar"]["p_value"])
        and close(p_value, r["mcnemar_p_value"])
    )

    if not checks:
        errors.append(
            f"Mismatch: AoI={s['maximum_aoi']}, "
            f"Fidelity={s['minimum_fidelity']}"
        )

    print(
        f'{s["maximum_aoi"]:>3} | '
        f'{s["minimum_fidelity"]:.1f} | '
        f'{len(paired):>5} | {difference:+.3f} | '
        f'{p_value:.10g} | {"PASS" if checks else "FAIL"}'
    )

print("Source combinations:", len(source_results))
print("Inference combinations:", len(inference_results))
print("Errors:", len(errors))

for error in errors:
    print("ERROR:", error)

print(
    "FINAL:",
    "PASS" if len(source_results) == 16
    and len(inference_results) == 16
    and not errors else "FAIL"
)
