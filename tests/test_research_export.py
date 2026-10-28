"""Automated tests for experimental CSV and JSON export."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from backend.core.research_experiments import run_research_experiments
from backend.core.research_export import (
    EXPERIMENT_FIELDS,
    export_experiment_results,
)


class TestResearchExport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = run_research_experiments(
            seeds=[42, 43, 44],
            node_count=10,
            link_count=15,
            current_time=10.0,
            minimum_fidelity=0.5,
            maximum_aoi=5.0,
        )

    def test_export_creates_both_files(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            self.assertTrue(Path(result["csv_path"]).is_file())
            self.assertTrue(Path(result["json_path"]).is_file())

    def test_export_record_count(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            self.assertEqual(
                result["record_count"],
                len(self.records),
            )

    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            with open(result["json_path"], encoding="utf-8") as file:
                restored = json.load(file)

            self.assertEqual(restored, self.records)

    def test_csv_row_count(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            with open(
                result["csv_path"],
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), len(self.records))

    def test_csv_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            with open(
                result["csv_path"],
                encoding="utf-8",
                newline="",
            ) as file:
                reader = csv.DictReader(file)
                self.assertEqual(reader.fieldnames, EXPERIMENT_FIELDS)

    def test_csv_route_format(self):
        with tempfile.TemporaryDirectory() as directory:
            result = export_experiment_results(self.records, directory)

            with open(
                result["csv_path"],
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

            for row, original in zip(rows, self.records):
                expected = (
                    " -> ".join(original["selected_route"])
                    if original["selected_route"] is not None
                    else ""
                )
                self.assertEqual(row["selected_route"], expected)

    def test_empty_records_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                export_experiment_results([], directory)

    def test_invalid_record_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                export_experiment_results(["invalid"], directory)

    def test_missing_fields_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                export_experiment_results(
                    [{"seed": 42}],
                    directory,
                )

    def test_nested_output_directory_created(self):
        with tempfile.TemporaryDirectory() as directory:
            nested = Path(directory) / "experiment" / "results"

            result = export_experiment_results(self.records, nested)

            self.assertTrue(nested.is_dir())
            self.assertTrue(Path(result["json_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
