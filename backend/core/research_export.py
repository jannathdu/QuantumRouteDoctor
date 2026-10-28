"""CSV and JSON export for reproducible quantum routing experiments."""

import csv
import json
from pathlib import Path


EXPERIMENT_FIELDS = [
    "seed",
    "node_count",
    "link_count",
    "source",
    "destination",
    "algorithm",
    "route_selected",
    "selected_route",
    "hop_count",
    "memory_adjusted_fidelity",
    "maximum_link_aoi",
    "feasible",
    "minimum_fidelity",
    "maximum_aoi",
    "current_time",
    "data_source",
]


def export_experiment_results(records, output_directory):
    """Export the same experiment records to CSV and JSON files."""

    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")

    if not all(isinstance(record, dict) for record in records):
        raise ValueError("Each record must be a dictionary")

    for index, record in enumerate(records):
        missing = set(EXPERIMENT_FIELDS) - set(record)
        if missing:
            raise ValueError(
                f"Record {index} missing fields: {sorted(missing)}"
            )

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)

    csv_path = directory / "quantum_routing_experiments.csv"
    json_path = directory / "quantum_routing_experiments.json"

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=EXPERIMENT_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()

        for record in records:
            row = dict(record)
            row["selected_route"] = (
                " -> ".join(record["selected_route"])
                if record["selected_route"] is not None
                else ""
            )
            writer.writerow(row)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

    return {
        "csv_path": str(csv_path),
        "json_path": str(json_path),
        "record_count": len(records),
    }
