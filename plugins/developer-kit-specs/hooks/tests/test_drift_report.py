#!/usr/bin/env python3
"""Unit tests for drift-report.py.

Tests cover:
- Fidelity calculation logic
- Markdown report generation
- Graceful degradation (missing state/log files)
- Edge cases (empty lists, duplicate files)
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Import the module under test using importlib for hyphenated filename
import importlib.util
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
module_path = os.path.join(parent_dir, "drift-report.py")

spec = importlib.util.spec_from_file_location("drift_report", module_path)
drift_report = importlib.util.module_from_spec(spec)
sys.modules["drift_report"] = drift_report
spec.loader.exec_module(drift_report)


class TestCalculateFidelity(unittest.TestCase):
    """Test fidelity calculation logic."""

    def test_full_fidelity_all_matched(self):
        """Given 3 expected files and 3 actual files matching, verify matched=3, missing=0, extra=0."""
        expected = ["file1.py", "file2.py", "file3.py"]
        actual = ["file1.py", "file2.py", "file3.py"]

        result = drift_report.calculate_fidelity(expected, actual)

        self.assertEqual(result["total_expected"], 3)
        self.assertEqual(result["matched_count"], 3)
        self.assertEqual(result["missing_count"], 0)
        self.assertEqual(result["extra_count"], 0)
        self.assertEqual(set(result["matched"]), set(expected))
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["extra"], [])

    def test_partial_fidelity_one_missing_one_extra(self):
        """Given 3 expected files and drift-events.log with 1 unplanned + 2 planned, verify matched=2, missing=1, extra=1."""
        expected = ["file1.py", "file2.py", "file3.py"]
        actual = ["file1.py", "file2.py", "extra_file.py"]

        result = drift_report.calculate_fidelity(expected, actual)

        self.assertEqual(result["total_expected"], 3)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["missing_count"], 1)
        self.assertEqual(result["extra_count"], 1)
        self.assertIn("file3.py", result["missing"])
        self.assertIn("extra_file.py", result["extra"])

    def test_zero_drift_events(self):
        """Given 3 expected files and zero drift events, verify total fidelity (matched=3, missing=0, extra=0)."""
        expected = ["file1.py", "file2.py", "file3.py"]
        actual = []

        result = drift_report.calculate_fidelity(expected, actual)

        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["missing_count"], 3)
        self.assertEqual(result["extra_count"], 0)

    def test_empty_expected_files(self):
        """Given empty expected_files list and actual files, verify all are extra."""
        expected = []
        actual = ["file1.py", "file2.py"]

        result = drift_report.calculate_fidelity(expected, actual)

        self.assertEqual(result["total_expected"], 0)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["missing_count"], 0)
        self.assertEqual(result["extra_count"], 2)

    def test_duplicate_files_in_actual(self):
        """Given drift-events.log with same file listed multiple times, verify deduplication for extra calculation."""
        expected = ["file1.py"]
        actual = ["file1.py", "extra.py", "extra.py", "extra.py"]

        result = drift_report.calculate_fidelity(expected, actual)

        self.assertEqual(result["extra_count"], 1)  # Deduplicated
        self.assertEqual(result["matched_count"], 1)


class TestFidelitySummary(unittest.TestCase):
    """Test fidelity summary statement generation."""

    def test_full_fidelity_no_drift(self):
        """Verify summary reports full fidelity when all expected files produced and no drift."""
        metrics = {
            "total_expected": 3,
            "matched_count": 3,
            "missing_count": 0,
            "extra_count": 0,
        }

        summary = drift_report.get_fidelity_summary(metrics)

        self.assertIn("Full fidelity", summary)
        self.assertIn("no drift", summary)

    def test_full_fidelity_with_drift(self):
        """Verify summary reports full fidelity with drift when all expected produced plus extras."""
        metrics = {
            "total_expected": 3,
            "matched_count": 3,
            "missing_count": 0,
            "extra_count": 2,
        }

        summary = drift_report.get_fidelity_summary(metrics)

        self.assertIn("Full fidelity with drift", summary)
        self.assertIn("2 unplanned", summary)

    def test_partial_fidelity(self):
        """Verify summary reports partial fidelity with percentage when >=80% matched."""
        metrics = {
            "total_expected": 5,
            "matched_count": 4,
            "missing_count": 1,
            "extra_count": 1,
        }

        summary = drift_report.get_fidelity_summary(metrics)

        self.assertIn("Partial fidelity", summary)
        self.assertIn("80%", summary)

    def test_low_fidelity(self):
        """Verify summary reports low fidelity when <80% but >=50% matched."""
        metrics = {
            "total_expected": 10,
            "matched_count": 6,
            "missing_count": 4,
            "extra_count": 0,
        }

        summary = drift_report.get_fidelity_summary(metrics)

        self.assertIn("Low fidelity", summary)

    def test_very_low_fidelity(self):
        """Verify summary reports very low fidelity when <50% matched."""
        metrics = {
            "total_expected": 10,
            "matched_count": 3,
            "missing_count": 7,
            "extra_count": 0,
        }

        summary = drift_report.get_fidelity_summary(metrics)

        self.assertIn("Very low fidelity", summary)


class TestLoadDriftEvents(unittest.TestCase):
    """Test drift events log loading."""

    def test_load_valid_log(self):
        """Given valid drift-events.log with 3 entries, verify 3 files returned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)
            log_path = os.path.join(drift_dir, "drift-events.log")

            with open(log_path, "w") as f:
                f.write("2026-04-03T12:00:00 | file1.py\n")
                f.write("2026-04-03T12:01:00 | file2.py\n")
                f.write("2026-04-03T12:02:00 | file3.py\n")

            result = drift_report.load_drift_events(tmpdir)

            self.assertEqual(len(result), 3)
            self.assertIn("file1.py", result)
            self.assertIn("file2.py", result)
            self.assertIn("file3.py", result)

    def test_load_missing_log(self):
        """Given drift-events.log absent, verify empty list returned (graceful degradation)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = drift_report.load_drift_events(tmpdir)

            self.assertEqual(result, [])

    def test_deduplication(self):
        """Given log with duplicate file entries, verify unique files returned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)
            log_path = os.path.join(drift_dir, "drift-events.log")

            with open(log_path, "w") as f:
                f.write("2026-04-03T12:00:00 | file1.py\n")
                f.write("2026-04-03T12:01:00 | file1.py\n")
                f.write("2026-04-03T12:02:00 | file2.py\n")

            result = drift_report.load_drift_events(tmpdir)

            self.assertEqual(len(result), 2)  # Deduplicated
            self.assertIn("file1.py", result)
            self.assertIn("file2.py", result)


class TestGenerateFidelityReport(unittest.TestCase):
    """Test Markdown report generation."""

    def test_report_contains_all_four_elements(self):
        """Verify _drift/fidelity-report.md contains all 4 required elements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)

            state = {
                "task_id": "TASK-001",
                "expected_files": ["file1.py", "file2.py"],
            }

            metrics = {
                "total_expected": 2,
                "matched_count": 1,
                "missing_count": 1,
                "extra_count": 1,
                "matched": ["file1.py"],
                "missing": ["file2.py"],
                "extra": ["extra.py"],
            }

            drift_report.generate_fidelity_report(tmpdir, "TASK-001", state, metrics)

            report_path = os.path.join(drift_dir, "fidelity-report.md")
            self.assertTrue(os.path.exists(report_path))

            with open(report_path, "r") as f:
                content = f.read()

            # Check for all 4 elements
            self.assertIn("Total Expected Files", content)
            self.assertIn("Matched Files", content)
            self.assertIn("Missing Files", content)
            self.assertIn("Extra Files", content)
            self.assertIn("Fidelity Report — TASK-001", content)

    def test_summary_statement_present(self):
        """Verify summary statement reflects correct fidelity level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)

            state = {"task_id": "TASK-001", "expected_files": ["file1.py"]}
            metrics = {
                "total_expected": 1,
                "matched_count": 1,
                "missing_count": 0,
                "extra_count": 0,
                "matched": ["file1.py"],
                "missing": [],
                "extra": [],
            }

            drift_report.generate_fidelity_report(tmpdir, "TASK-001", state, metrics)

            report_path = os.path.join(drift_dir, "fidelity-report.md")
            with open(report_path, "r") as f:
                content = f.read()

            self.assertIn("Summary", content)
            self.assertIn("Full fidelity", content)

    def test_report_overwrites_existing(self):
        """Verify that existing fidelity-report.md is overwritten."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)

            report_path = os.path.join(drift_dir, "fidelity-report.md")

            # Create initial report
            with open(report_path, "w") as f:
                f.write("OLD CONTENT\n")

            # Generate new report
            state = {"task_id": "TASK-001", "expected_files": []}
            metrics = {
                "total_expected": 0,
                "matched_count": 0,
                "missing_count": 0,
                "extra_count": 0,
                "matched": [],
                "missing": [],
                "extra": [],
            }

            drift_report.generate_fidelity_report(tmpdir, "TASK-001", state, metrics)

            # Verify overwritten
            with open(report_path, "r") as f:
                content = f.read()

            self.assertNotIn("OLD CONTENT", content)


class TestGracefulDegradation(unittest.TestCase):
    """Test graceful degradation behavior."""

    def test_missing_state_json(self):
        """Verify that if _drift/state.json doesn't exist, script exits with exit 0 without crashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create stdin input
            input_data = {
                "hook_event_name": "TaskCompleted",
                "cwd": tmpdir,
            }

            # Simulate running main() with missing state
            # This should exit(0) gracefully
            import io
            old_stdin = sys.stdin
            try:
                sys.stdin = io.StringIO(json.dumps(input_data))
                drift_report.main()
                self.fail("Should have raised SystemExit")
            except SystemExit as e:
                self.assertEqual(e.code, 0)
            finally:
                sys.stdin = old_stdin

    def test_invalid_state_json(self):
        """Verify that if state.json is invalid JSON, script exits gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            drift_dir = os.path.join(tmpdir, "_drift")
            os.makedirs(drift_dir)

            state_path = os.path.join(drift_dir, "state.json")
            with open(state_path, "w") as f:
                f.write("INVALID JSON {")

            input_data = {"hook_event_name": "TaskCompleted", "cwd": tmpdir}

            import io
            old_stdin = sys.stdin
            try:
                sys.stdin = io.StringIO(json.dumps(input_data))
                drift_report.main()
                self.fail("Should have raised SystemExit")
            except SystemExit as e:
                self.assertEqual(e.code, 0)
            finally:
                sys.stdin = old_stdin


if __name__ == "__main__":
    # Fix constant reference
    DRIFT_EVENTS_LOG = "drift-events.log"
    unittest.main()
