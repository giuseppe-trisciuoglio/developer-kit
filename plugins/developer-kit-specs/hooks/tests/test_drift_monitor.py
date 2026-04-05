#!/usr/bin/env python3
"""Unit tests for drift-monitor.py.

Tests cover:
- Path comparison logic (exact match, case-sensitive)
- Alert generation and format
- Deduplication via alerted_files
- Drift event logging
- Graceful degradation (missing state.json)
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import drift_monitor module directly
# Note: Using exec to load module since it's a script
import importlib.util
spec = importlib.util.spec_from_file_location("drift_monitor", os.path.join(parent_dir, "drift-monitor.py"))
drift_monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift_monitor)

# Use module functions
is_expected_file = drift_monitor.is_expected_file
is_already_alerted = drift_monitor.is_already_alerted
find_state_file = drift_monitor.find_state_file
load_state = drift_monitor.load_state
update_alerted_files = drift_monitor.update_alerted_files
log_drift_event = drift_monitor.log_drift_event
emit_alert = drift_monitor.emit_alert


# ─── Test Fixtures ────────────────────────────────────────────────────────────


def create_temp_state(expected_files=None, alerted_files=None):
    """Create a temporary state.json for testing.

    Returns tuple: (temp_dir, state_path)
    """
    temp_dir = tempfile.mkdtemp()
    drift_dir = os.path.join(temp_dir, "_drift")
    os.makedirs(drift_dir)

    state = {
        "task_id": "TASK-001",
        "task_file": "docs/specs/001-drift-guard/tasks/TASK-001.md",
        "expected_files": expected_files or [],
        "initialized_at": "2026-04-03T10:00:00Z",
    }

    if alerted_files is not None:
        state["alerted_files"] = alerted_files

    state_path = os.path.join(drift_dir, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    return temp_dir, state_path


# ─── Path Comparison Tests ────────────────────────────────────────────────────


def test_expected_file_exact_match():
    """Test that exact match produces silent exit."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/main.py", "src/utils.py", "tests/test_main.py"]
    )
    state = load_state(state_path)

    # Test exact match
    assert is_expected_file("src/main.py", state) is True
    assert is_expected_file("src/utils.py", state) is True
    assert is_expected_file("tests/test_main.py", state) is True

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_expected_file_exact_match passed")


def test_expected_file_not_in_list():
    """Test that unplanned file triggers alert."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/main.py", "src/utils.py"]
    )
    state = load_state(state_path)

    # Test file not in list
    assert is_expected_file("src/unplanned.py", state) is False
    assert is_expected_file("README.md", state) is False
    assert is_expected_file("config.yaml", state) is False

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_expected_file_not_in_list passed")


def test_case_sensitive_comparison():
    """Test that comparison is case-sensitive."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/Foo.py", "src/Bar.py"]
    )
    state = load_state(state_path)

    # Test case sensitivity
    assert is_expected_file("src/Foo.py", state) is True
    assert is_expected_file("src/foo.py", state) is False
    assert is_expected_file("src/FOO.py", state) is False

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_case_sensitive_comparison passed")


# ─── Alert Deduplication Tests ───────────────────────────────────────────────


def test_alert_deduplication():
    """Test that duplicate alerts are prevented."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/main.py"],
        alerted_files=["src/unplanned1.py"]
    )
    state = load_state(state_path)

    # Test already alerted
    assert is_already_alerted("src/unplanned1.py", state) is True
    assert is_already_alerted("src/unplanned2.py", state) is False

    # Add new alerted file
    update_alerted_files(state_path, "src/unplanned2.py")
    state = load_state(state_path)

    assert is_already_alerted("src/unplanned2.py", state) is True

    # Verify no duplicate entries
    assert state["alerted_files"].count("src/unplanned2.py") == 1

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_alert_deduplication passed")


def test_alert_format(capsys):
    """Test that alert contains required elements."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/main.py", "src/utils.py", "tests/test.py"],
        alerted_files=[]
    )
    state = load_state(state_path)

    # Capture stdout
    emit_alert("src/unplanned.py", state)
    captured = capsys.readouterr()

    output = captured.out

    # Check required elements
    assert "[Drift Guard] Unplanned file detected: src/unplanned.py" in output
    assert "[Drift Guard] Active task: TASK-001" in output
    assert "[Drift Guard] Expected files (partial):" in output
    assert "src/main.py" in output

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_alert_format passed")


# ─── Drift Event Log Tests ───────────────────────────────────────────────────


def test_drift_event_logging():
    """Test that drift events are logged to file."""
    temp_dir, state_path = create_temp_state()

    spec_folder = temp_dir
    log_drift_event(spec_folder, "src/unplanned1.py")
    log_drift_event(spec_folder, "src/unplanned2.py")

    log_path = os.path.join(temp_dir, "_drift", "drift-events.log")

    # Verify log exists and contains entries
    assert os.path.exists(log_path)

    with open(log_path, "r") as f:
        content = f.read()

    assert "src/unplanned1.py" in content
    assert "src/unplanned2.py" in content
    assert "|" in content  # Timestamp separator

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_drift_event_logging passed")


def test_drift_event_log_append():
    """Test that log is appended, not overwritten."""
    temp_dir, state_path = create_temp_state()

    spec_folder = temp_dir
    log_drift_event(spec_folder, "src/file1.py")

    # Read initial size
    log_path = os.path.join(temp_dir, "_drift", "drift-events.log")
    with open(log_path, "r") as f:
        initial_content = f.read()

    log_drift_event(spec_folder, "src/file2.py")

    # Verify append
    with open(log_path, "r") as f:
        new_content = f.read()

    assert len(new_content) > len(initial_content)
    assert "src/file1.py" in new_content
    assert "src/file2.py" in new_content

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_drift_event_log_append passed")


# ─── Graceful Degradation Tests ──────────────────────────────────────────────


def test_missing_state_file():
    """Test that missing state.json causes silent exit."""
    state = load_state("/nonexistent/path/state.json")
    assert state is None
    print("✓ test_missing_state_file passed")


def test_malformed_state_file():
    """Test that malformed JSON causes silent exit."""
    temp_dir = tempfile.mkdtemp()
    drift_dir = os.path.join(temp_dir, "_drift")
    os.makedirs(drift_dir)

    # Create malformed JSON
    state_path = os.path.join(drift_dir, "state.json")
    with open(state_path, "w") as f:
        f.write("{ invalid json }")

    state = load_state(state_path)
    assert state is None

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_malformed_state_file passed")


# ─── Edge Cases Tests ────────────────────────────────────────────────────────


def test_empty_expected_files():
    """Test behavior with empty expected_files list."""
    temp_dir, state_path = create_temp_state(expected_files=[])
    state = load_state(state_path)

    # Any file should be considered unplanned
    assert is_expected_file("any_file.py", state) is False
    assert is_expected_file("README.md", state) is False

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_empty_expected_files passed")


def test_special_characters_in_path():
    """Test handling of file paths with special characters."""
    temp_dir, state_path = create_temp_state(
        expected_files=["src/file with spaces.py", "src/file(with)parens.py"]
    )
    state = load_state(state_path)

    # Test exact match with special characters
    assert is_expected_file("src/file with spaces.py", state) is True
    assert is_expected_file("src/file(with)parens.py", state) is True
    assert is_expected_file("src/file_without_spaces.py", state) is False

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("✓ test_special_characters_in_path passed")


# ─── Test Runner ────────────────────────────────────────────────────────────


def run_all_tests():
    """Run all tests and report results."""
    print("Running drift-monitor.py tests...")
    print("=" * 60)

    tests = [
        test_expected_file_exact_match,
        test_expected_file_not_in_list,
        test_case_sensitive_comparison,
        test_alert_deduplication,
        test_drift_event_logging,
        test_drift_event_log_append,
        test_missing_state_file,
        test_malformed_state_file,
        test_empty_expected_files,
        test_special_characters_in_path,
    ]

    # Filter out capsys tests for now (needs pytest)
    filtered_tests = [t for t in tests if "capsys" not in t.__code__.co_varnames]

    passed = 0
    failed = 0

    for test in filtered_tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
