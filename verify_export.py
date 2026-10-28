
import csv
import json
from pathlib import Path

folder = Path("results/export_verification")
json_path = folder / "quantum_routing_experiments.json"
csv_path = folder / "quantum_routing_experiments.csv"

json_records = json.loads(json_path.read_text(encoding="utf-8"))

with csv_path.open(encoding="utf-8-sig", newline="") as f:
    csv_records = list(csv.DictReader(f))

errors = []

if len(json_records) != len(csv_records):
    errors.append(
        f"Record count mismatch: JSON={len(json_records)}, CSV={len(csv_records)}"
    )

for i, (jr, cr) in enumerate(zip(json_records, csv_records), start=1):
    for key, value in jr.items():
        if key not in cr:
            errors.append(f"Row {i}: missing column {key}")
            continue

        actual = cr[key]

        if isinstance(value, list):
            expected = " -> ".join(map(str, value))
        elif value is None:
            expected = ""
        elif isinstance(value, bool):
            if actual.strip().lower() == str(value).lower():
                continue
            expected = str(value).lower()
        else:
            expected = str(value)

        if actual != expected:
            try:
                if float(actual) == float(value):
                    continue
            except (ValueError, TypeError):
                pass
            errors.append(
                f"Row {i}, {key}: JSON={expected!r}, CSV={actual!r}"
            )

print("JSON records:", len(json_records))
print("CSV records:", len(csv_records))
print("Field mismatches:", len(errors))
for error in errors[:20]:
    print("MISMATCH:", error)
print("FINAL:", "PASS" if not errors else "FAIL")
