import json
import math
from pathlib import Path

BASE = Path("results/research_reports")
SOURCE_PATH = BASE / "quantum_routing_combined_aoi_fidelity_sensitivity.json"
REPORT_PATH = BASE / "quantum_routing_combined_statistical_inference.json"


def close(a, b, tol=1e-10):
    return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol)


def exact_mcnemar(baseline_only, temporal_only):
    n = baseline_only + temporal_only
    if n == 0:
        return 1.0

    k = min(baseline_only, temporal_only)
    return min(
        1.0,
        2.0 * math.fsum(
            math.comb(n, i) * (0.5 ** n)
            for i in range(k + 1)
        ),
    )


def main():
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    source_results = source.get("results", [])
    report_results = report.get("results", [])
    report_map = {
        (r["maximum_aoi"], r["minimum_fidelity"]): r
        for r in report_results
    }

    errors = []
    print("AoI | Fidelity | Pairs | Difference | McNemar | Holm | CI")

    for item in source_results:
        key = (item["maximum_aoi"], item["minimum_fidelity"])
        saved = report_map.get(key)

        if saved is None:
            errors.append(f"Missing report combination: {key}")
            continue

        pairs = {}
        duplicate = False

        for row in item["records"]:
            pair = pairs.setdefault(row["seed"], {})
            algorithm = row["algorithm"]

            if algorithm in pair:
                duplicate = True
            pair[algorithm] = row["feasible"]

        if duplicate:
            errors.append(f"Duplicate algorithm record: {key}")
            continue

        if len(pairs) != 100 or any(
            set(pair) != {"baseline", "temporal"}
            for pair in pairs.values()
        ):
            errors.append(f"Incomplete scenario pairs: {key}")
            continue

        counts = {
            "both_feasible": 0,
            "baseline_only": 0,
            "temporal_only": 0,
            "neither_feasible": 0,
        }

        for pair in pairs.values():
            b = pair["baseline"]
            t = pair["temporal"]

            if b and t:
                counts["both_feasible"] += 1
            elif b:
                counts["baseline_only"] += 1
            elif t:
                counts["temporal_only"] += 1
            else:
                counts["neither_feasible"] += 1

        baseline_rate = sum(
            p["baseline"] for p in pairs.values()
        ) / len(pairs)
        temporal_rate = sum(
            p["temporal"] for p in pairs.values()
        ) / len(pairs)
        difference = temporal_rate - baseline_rate

        p_value = exact_mcnemar(
            counts["baseline_only"],
            counts["temporal_only"],
        )

        summary = item["paired_inference"]
        inference_ok = (
            counts == summary["paired_outcomes"]
            and close(
                difference,
                summary["paired_feasibility_difference"],
            )
            and close(p_value, summary["mcnemar"]["p_value"])
            and close(p_value, saved["mcnemar_p_value"])
            and close(
                difference,
                saved["paired_difference"],
            )
            and close(
                baseline_rate,
                saved["baseline_feasibility_rate"],
            )
            and close(
                temporal_rate,
                saved["temporal_feasibility_rate"],
            )
        )

        holm_ok = (
            "holm_adjusted_p_value" in saved
            and isinstance(
                saved.get("significant_after_holm_0_05"), bool
            )
        )

        ci = saved.get("bootstrap_95_ci")
        ci_ok = (
            isinstance(ci, list)
            and len(ci) == 2
            and all(
                isinstance(x, (int, float)) and math.isfinite(x)
                for x in ci
            )
            and -1 <= ci[0] <= ci[1] <= 1
        )

        if not inference_ok:
            errors.append(f"Paired inference mismatch: {key}")
        if not holm_ok:
            errors.append(f"Holm fields missing or invalid: {key}")
        if not ci_ok:
            errors.append(f"Invalid stored CI: {key}")

        ci_status = "VALID" if ci_ok else "INVALID"
        print(
            f"{key[0]:.1f} | {key[1]:.1f} | 100 | "
            f"{difference:+.3f} | "
            f'{"PASS" if inference_ok else "FAIL"} | '
            f'{"FIELDS OK" if holm_ok else "REVIEW"} | {ci_status}'
        )

    if len(source_results) != 16 or len(report_results) != 16:
        errors.append("Expected exactly 16 combinations in both reports")

    print("\nCombinations:", len(source_results))
    print("Errors:", len(errors))
    for error in errors:
        print("ERROR:", error)

    print(
        "FINAL:",
        "PASS" if not errors else "REVIEW REQUIRED",
    )


if __name__ == "__main__":
    main()
