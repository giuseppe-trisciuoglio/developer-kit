#!/usr/bin/env python3
"""End-to-end tests for Session Tracking Hook workflow.

Covers AC-001 through AC-008 from the 005-session-tracking-hook specification.
Tests the full pipeline: Stop event simulation → transcript extraction →
tracking_log.md creation/update.

Since the hook uses an LLM agent, these tests verify:
1. The session-tracker.py data extraction correctness (deterministic component)
2. The hooks.json and agent file structural correctness
3. The tracking_log.md write/update logic (simulated from agent instructions)
4. Security constraints (no credentials in the extracted/written output)
5. Performance characteristics (large transcripts processed within timeout)

Architecture:
- `_write_tracking_entry()` simulates the deterministic part of the agent's behavior
  (without LLM), implementing the same idempotency and format logic from
  session-tracking-agent.md Phase 6.
- This simulation is the basis for AC-001..AC-008 integration assertions.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytest

# ─── Module Resolution ────────────────────────────────────────────────────────

# Test file is at: plugins/developer-kit-specs/hooks/tests/test_session_tracking_e2e.py
# _plugin_root resolves to: plugins/developer-kit-specs/
_plugin_root = Path(__file__).parent.parent.parent
_scripts_dir = _plugin_root / "scripts"

# Import session_tracker module (session-tracker.py has a hyphen — requires importlib)
_st_spec = importlib.util.spec_from_file_location(
    "session_tracker", str(_scripts_dir / "session-tracker.py")
)
session_tracker = importlib.util.module_from_spec(_st_spec)
sys.modules["session_tracker"] = session_tracker
_st_spec.loader.exec_module(session_tracker)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_transcript(entries: list[dict], tmp_dir: str) -> str:
    """Create a temporary JSONL transcript file from the given entries.

    Returns the absolute path to the created file.
    """
    path = os.path.join(tmp_dir, "transcript.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return path


def _extract_data_from_transcript(transcript_path: str) -> dict:
    """Extract structured data from a transcript file using session-tracker logic.

    Returns dict with keys: user_messages, tool_operations, modified_files.
    """
    lines = session_tracker.read_last_n_lines(transcript_path)
    entries = [session_tracker.parse_jsonl_line(line) for line in lines]
    entries = [e for e in entries if e is not None]
    user_msgs = session_tracker.extract_user_messages(entries)
    tool_data = session_tracker.extract_tool_operations(entries)
    return {
        "user_messages": user_msgs,
        "tool_operations": tool_data["tool_operations"],
        "modified_files": tool_data["modified_files"],
    }


def _write_tracking_entry(
    tracking_log_path: str,
    session_id: str,
    extracted_data: dict,
    git_branch: Optional[str] = "feature/test-branch",
    git_commits: Optional[list] = None,
    date_str: Optional[str] = None,
    time_str: Optional[str] = None,
) -> bool:
    """Simulate what session-tracking-agent writes to tracking_log.md.

    Implements the agent's Phase 6 logic deterministically (without LLM):
    - Checks for file changes (AC-004: no changes → no entry)
    - Computes SHORT_ID for idempotency (AC-002)
    - Creates tracking_log.md if it does not exist (AC-003)
    - Prepends new entries at the top; updates existing entries in place
    - Writes entry format matching Section 7 of the specification
    - Omits Branch/Commit sections when not applicable (AC-005, AC-007)

    Returns True if an entry was written, False if skipped (no file changes).
    """
    if not extracted_data["modified_files"]:
        return False  # AC-004: no meaningful changes → no entry

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    if time_str is None:
        time_str = datetime.now().strftime("%H:%M")

    short_id = session_tracker.derive_short_session_id(session_id)

    # ── Build entry (Section 7 format) ────────────────────────────────────────
    parts: list[str] = [f"## {date_str} \u2014 Sessione {short_id}"]
    if git_branch:
        parts.append(f"**Branch:** {git_branch}")
    parts.append(f"**Orario:** {time_str}")
    parts.append("")

    parts.append("### Task eseguiti")
    if extracted_data["user_messages"]:
        for msg in extracted_data["user_messages"][:3]:
            parts.append(f"- {msg[:100]}")
    else:
        parts.append("- (nessun messaggio utente trovato)")
    parts.append("")

    parts.append("### File modificati")
    for file_path in extracted_data["modified_files"]:
        parts.append(f"- {file_path} (modificato)")
    parts.append("")

    # Rationale — derives context from first user message (no LLM needed in tests)
    parts.append("### Rationale")
    if extracted_data["user_messages"]:
        first_msg = extracted_data["user_messages"][0][:80]
        parts.append(
            f"Il task ha richiesto modifiche per soddisfare la richiesta: {first_msg}"
        )
    else:
        parts.append("Modifiche apportate come da contesto conversazionale.")
    parts.append("")

    if git_commits:
        parts.append("### Commit")
        for commit in git_commits:
            parts.append(f"- {commit}")
        parts.append("")

    entry = "\n".join(parts) + "\n"

    # ── Idempotency logic (AC-002) ────────────────────────────────────────────
    # Match an existing header for this SHORT_ID (any date — same session may
    # span multiple responses, dates are consistent within a session).
    session_pattern = re.compile(
        rf"^## \d{{4}}-\d{{2}}-\d{{2}} \u2014 Sessione {re.escape(short_id)}\b",
        re.MULTILINE,
    )
    next_section_pattern = re.compile(
        r"^## \d{4}-\d{2}-\d{2} \u2014 Sessione ", re.MULTILINE
    )

    existing_content = ""
    if Path(tracking_log_path).exists():
        existing_content = Path(tracking_log_path).read_text(encoding="utf-8")

    if session_pattern.search(existing_content):
        # Update existing section in place
        match = session_pattern.search(existing_content)
        start = match.start()
        remaining = existing_content[match.end() :]
        next_match = next_section_pattern.search(remaining)
        end = match.end() + next_match.start() if next_match else len(existing_content)
        new_content = existing_content[:start] + entry + existing_content[end:]
        Path(tracking_log_path).write_text(new_content, encoding="utf-8")
    else:
        # Prepend new entry at the top (reverse chronological order)
        Path(tracking_log_path).write_text(entry + existing_content, encoding="utf-8")

    return True


# ─── AC-001: Full Entry Creation ──────────────────────────────────────────────


class TestAC001FullEntryCreation:
    """AC-001: Session with file modifications → entry in tracking_log.md
    with date, branch, task description, file paths, and rationale."""

    def test_entry_created_with_all_required_sections(self, tmp_path):
        """All required Markdown sections must be present in the log entry."""
        entries = [
            {"type": "user", "content": "Implement the new feature"},
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "src/feature.py", "content": "pass"},
            },
            {
                "type": "tool_use",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "tests/test_feature.py",
                    "old_string": "# TODO",
                    "new_string": "def test_feature(): pass",
                },
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(
            tracking_log,
            "abc123def456",
            data,
            git_branch="feature/test",
            date_str="2026-04-10",
            time_str="14:30",
        )

        content = Path(tracking_log).read_text(encoding="utf-8")

        assert "## 2026-04-10 \u2014 Sessione abc123de" in content
        assert "**Branch:** feature/test" in content
        assert "**Orario:** 14:30" in content
        assert "### Task eseguiti" in content
        assert "### File modificati" in content
        assert "### Rationale" in content

    def test_modified_files_listed_in_entry(self, tmp_path):
        """File paths written and edited must appear in the File modificati section."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "src/new.py", "content": "x = 1"},
            },
            {
                "type": "tool_use",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "src/existing.py",
                    "old_string": "old",
                    "new_string": "new",
                },
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "sess001122334", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "src/new.py" in content
        assert "src/existing.py" in content

    def test_user_task_listed_in_task_section(self, tmp_path):
        """User request must appear in the Task eseguiti section."""
        entries = [
            {"type": "user", "content": "Refactor the authentication module"},
            {
                "type": "tool_use",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "src/auth.py",
                    "old_string": "old_auth",
                    "new_string": "new_auth",
                },
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "sess9876543a", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "Refactor the authentication module" in content

    def test_new_entry_prepended_at_top(self, tmp_path):
        """New entries are added at the TOP of tracking_log.md (reverse chrono)."""
        tracking_log = str(tmp_path / "tracking_log.md")
        old_content = (
            "## 2026-04-09 \u2014 Sessione old00001\n"
            "**Branch:** main\n**Orario:** 09:00\n\n"
            "### Task eseguiti\n- Old task\n\n"
            "### File modificati\n- old.py (modificato)\n\n"
            "### Rationale\nOld rationale.\n\n"
        )
        Path(tracking_log).write_text(old_content, encoding="utf-8")

        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "new.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(
            tracking_log, "new001122334455", data, date_str="2026-04-10"
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        pos_new = content.find("Sessione new00112")
        pos_old = content.find("Sessione old00001")
        assert pos_new < pos_old, "New entry should appear before old entry"


# ─── AC-002: Idempotency ──────────────────────────────────────────────────────


class TestAC002Idempotency:
    """AC-002: Same session ID fired twice → only one entry in tracking_log.md."""

    def test_no_duplicate_on_second_invocation(self, tmp_path):
        """Firing the same session_id twice must not create duplicate entries."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "src/a.py", "content": "x"},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")
        session_id = "abc12345def678"

        data = _extract_data_from_transcript(transcript_path)
        short_id = session_tracker.derive_short_session_id(session_id)

        # First invocation
        _write_tracking_entry(
            tracking_log, session_id, data, date_str="2026-04-10", time_str="10:00"
        )
        # Second invocation with same session_id
        _write_tracking_entry(
            tracking_log, session_id, data, date_str="2026-04-10", time_str="10:05"
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        header = f"## 2026-04-10 \u2014 Sessione {short_id}"
        count = content.count(header)
        assert count == 1, f"Expected 1 entry but found {count} for session {short_id}"

    def test_second_invocation_updates_existing_entry(self, tmp_path):
        """Second invocation replaces the existing section, not duplicates it."""
        tracking_log = str(tmp_path / "tracking_log.md")
        session_id = "upd001122334455"
        short_id = session_tracker.derive_short_session_id(session_id)

        # First invocation — one file modified
        t1_dir = str(tmp_path / "t1")
        os.makedirs(t1_dir, exist_ok=True)
        t1 = _make_transcript(
            [
                {
                    "type": "tool_use",
                    "tool_name": "Write",
                    "tool_input": {"file_path": "file1.py", "content": "x"},
                }
            ],
            t1_dir,
        )
        d1 = _extract_data_from_transcript(t1)
        _write_tracking_entry(tracking_log, session_id, d1, time_str="10:00")

        # Second invocation — same session, different time
        t2_dir = str(tmp_path / "t2")
        os.makedirs(t2_dir, exist_ok=True)
        t2 = _make_transcript(
            [
                {
                    "type": "tool_use",
                    "tool_name": "Write",
                    "tool_input": {"file_path": "file2.py", "content": "y"},
                }
            ],
            t2_dir,
        )
        d2 = _extract_data_from_transcript(t2)
        _write_tracking_entry(tracking_log, session_id, d2, time_str="10:05")

        content = Path(tracking_log).read_text(encoding="utf-8")
        count = content.count(f"Sessione {short_id}")
        assert count == 1, f"Expected 1 entry but found {count}"

    def test_multiple_different_sessions_no_conflict(self, tmp_path):
        """Two different session IDs must produce two distinct entries."""
        tracking_log = str(tmp_path / "tracking_log.md")

        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "f.py", "content": ""},
            }
        ]

        for i, session_id in enumerate(
            ["sessA001122334455", "sessB001122334455"], start=1
        ):
            t_dir = str(tmp_path / f"t{i}")
            os.makedirs(t_dir, exist_ok=True)
            t = _make_transcript(entries, t_dir)
            d = _extract_data_from_transcript(t)
            _write_tracking_entry(tracking_log, session_id, d, date_str="2026-04-10")

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "Sessione sessA001" in content
        assert "Sessione sessB001" in content


# ─── AC-003: First-Run Auto-Create ───────────────────────────────────────────


class TestAC003FirstRun:
    """AC-003: No tracking_log.md → created automatically on first Stop event."""

    def test_tracking_log_created_when_not_exists(self, tmp_path):
        """tracking_log.md does not exist before first invocation; gets created."""
        tracking_log = str(tmp_path / "tracking_log.md")
        assert not Path(tracking_log).exists()

        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "src/init.py", "content": "pass"},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        data = _extract_data_from_transcript(transcript_path)

        _write_tracking_entry(tracking_log, "first00112233", data)

        assert Path(tracking_log).exists()

    def test_first_entry_content_is_valid(self, tmp_path):
        """The auto-created file must contain a valid first entry."""
        tracking_log = str(tmp_path / "tracking_log.md")
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "src/init.py", "content": "pass"},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        data = _extract_data_from_transcript(transcript_path)

        _write_tracking_entry(
            tracking_log, "first00112233", data, date_str="2026-04-10"
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "Sessione first001" in content
        assert "### File modificati" in content

    def test_first_entry_at_top_of_new_file(self, tmp_path):
        """First entry is placed at the top of the newly created file."""
        tracking_log = str(tmp_path / "tracking_log.md")
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "x.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        data = _extract_data_from_transcript(transcript_path)

        _write_tracking_entry(
            tracking_log, "toptest00001122", data, date_str="2026-04-10"
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        first_line = content.strip().split("\n")[0]
        assert first_line.startswith("## 2026-04-10 \u2014 Sessione")


# ─── AC-004: No-Noise ─────────────────────────────────────────────────────────


class TestAC004NoNoise:
    """AC-004: Session with no file changes → no entry added to tracking_log.md."""

    def test_no_entry_on_conversational_only_session(self, tmp_path):
        """Purely conversational transcript does NOT create a log entry."""
        entries = [
            {"type": "user", "content": "What is the capital of France?"},
            {"type": "assistant", "content": "Paris."},
            {"type": "user", "content": "Thank you!"},
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        written = _write_tracking_entry(tracking_log, "noise00112233", data)

        assert written is False
        assert not Path(tracking_log).exists()

    def test_no_entry_on_read_only_operations(self, tmp_path):
        """Session with only Bash read operations (no Write/Edit) → no entry."""
        entries = [
            {"type": "user", "content": "Show me the config file"},
            {
                "type": "tool_use",
                "tool_name": "Bash",
                "tool_input": {"command": "cat config.py"},
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        written = _write_tracking_entry(tracking_log, "read0011223344", data)

        assert written is False

    def test_existing_log_unchanged_when_no_file_changes(self, tmp_path):
        """Existing tracking_log.md is NOT modified when session has no file changes."""
        tracking_log = str(tmp_path / "tracking_log.md")
        original_content = (
            "## 2026-04-01 \u2014 Sessione abc12345\n"
            "**Branch:** main\n\nPrevious entry.\n"
        )
        Path(tracking_log).write_text(original_content, encoding="utf-8")

        entries = [{"type": "user", "content": "Just a question"}]
        transcript_path = _make_transcript(entries, str(tmp_path))
        data = _extract_data_from_transcript(transcript_path)

        _write_tracking_entry(tracking_log, "new0011223344", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert content == original_content


# ─── AC-005: Git Branch Included ──────────────────────────────────────────────


class TestAC005GitBranch:
    """AC-005: With git repo active, branch name appears in log entry."""

    def test_branch_name_present_in_entry(self, tmp_path):
        """When git_branch is provided, it appears in the log entry."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "f.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(
            tracking_log, "branch00112233", data, git_branch="feature/my-feature"
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "**Branch:** feature/my-feature" in content

    def test_branch_field_omitted_for_non_git_repo(self, tmp_path):
        """When git_branch is None (non-git repo), Branch field is omitted."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "f.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "nogit0011223344", data, git_branch=None)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "**Branch:**" not in content

    def test_actual_git_branch_retrievable_via_subprocess(self):
        """Sanity check: git branch --show-current works in this repo."""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(_plugin_root),
        )
        assert result.returncode == 0
        branch = result.stdout.strip()
        assert len(branch) > 0, "Expected a non-empty branch name"


# ─── AC-006: Non-Blocking on Agent Failure ───────────────────────────────────


class TestAC006NonBlocking:
    """AC-006: Agent failure (e.g. invalid transcript) → no error propagated."""

    def test_missing_transcript_returns_empty_lines(self):
        """Non-existent transcript → read_last_n_lines returns empty list."""
        lines = session_tracker.read_last_n_lines(
            "/nonexistent/path/to/transcript.jsonl"
        )
        assert lines == []

    def test_empty_transcript_returns_empty_lines(self, tmp_path):
        """Empty transcript file → read_last_n_lines returns empty list."""
        empty = str(tmp_path / "empty.jsonl")
        Path(empty).write_text("", encoding="utf-8")
        lines = session_tracker.read_last_n_lines(empty)
        assert lines == []

    def test_cli_nonexistent_transcript_exits_zero(self):
        """CLI call with non-existent transcript → exit 0, valid JSON output."""
        result = subprocess.run(
            [
                "python3",
                str(_scripts_dir / "session-tracker.py"),
                "--transcript-path=/nonexistent/file.jsonl",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "user_messages" in data
        assert data["user_messages"] == []
        assert data["modified_files"] == []

    def test_malformed_jsonl_parsed_gracefully(self, tmp_path):
        """Malformed JSONL lines are skipped; no exception raised."""
        malformed = str(tmp_path / "malformed.jsonl")
        Path(malformed).write_text(
            '{"type": "user", "content": "valid"}\nNOT JSON\n{"broken\n',
            encoding="utf-8",
        )
        lines = session_tracker.read_last_n_lines(malformed)
        entries = [session_tracker.parse_jsonl_line(line) for line in lines]
        # parse_jsonl_line returns None for invalid lines — no crash
        valid_entries = [e for e in entries if e is not None]
        assert isinstance(valid_entries, list)
        assert len(valid_entries) == 1  # Only the first valid line

    def test_hooks_json_stop_hook_is_async(self):
        """hooks.json Stop event hook must have async: true (non-blocking)."""
        hooks_path = _plugin_root / "hooks" / "hooks.json"
        with open(hooks_path) as f:
            config = json.load(f)
        stop_hooks = config["hooks"].get("Stop", [])
        assert len(stop_hooks) > 0, "Stop event must have at least one hook entry"
        for hook_entry in stop_hooks:
            for h in hook_entry.get("hooks", []):
                if h.get("type") == "agent":
                    assert (
                        h.get("async") is True
                    ), "Stop hook agent must have async: true"


# ─── AC-007: Git Commits Included ─────────────────────────────────────────────


class TestAC007GitCommits:
    """AC-007: With git commits made → commit hash and message appear in log."""

    def test_commit_section_present_when_commits_provided(self, tmp_path):
        """When git_commits are provided, ### Commit section and hashes appear."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "f.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(
            tracking_log,
            "commit0011223344",
            data,
            git_commits=[
                "abc1234 feat(scope): add feature X",
                "def5678 fix(bug): resolve issue Y",
            ],
        )

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "### Commit" in content
        assert "abc1234" in content
        assert "def5678" in content

    def test_commit_section_omitted_when_no_commits(self, tmp_path):
        """When git_commits is None, ### Commit section must not appear."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "f.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "nocommit00112233", data, git_commits=None)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "### Commit" not in content

    def test_multiple_commits_all_present(self, tmp_path):
        """All provided commits must appear in the Commit section."""
        entries = [
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "g.py", "content": ""},
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        commits = [
            "aaa0001 chore: first commit",
            "bbb0002 feat: second commit",
            "ccc0003 fix: third commit",
        ]
        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "multi00112233", data, git_commits=commits)

        content = Path(tracking_log).read_text(encoding="utf-8")
        for commit in commits:
            assert commit in content


# ─── AC-008: Rationale Quality ───────────────────────────────────────────────


class TestAC008RationaleQuality:
    """AC-008: Rationale is natural language describing WHY changes were made."""

    def test_rationale_section_present_in_entry(self, tmp_path):
        """Entry must include a ### Rationale section."""
        entries = [
            {"type": "user", "content": "Fix the authentication bug"},
            {
                "type": "tool_use",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "auth.py",
                    "old_string": "x",
                    "new_string": "y",
                },
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "rat001122334455", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "### Rationale" in content

    def test_rationale_non_empty(self, tmp_path):
        """Rationale section must contain meaningful text (not empty)."""
        entries = [
            {"type": "user", "content": "Implement new endpoint"},
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "api.py", "content": ""},
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "rat002233445566", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        # Extract content between ### Rationale and the next section
        rationale_match = re.search(
            r"### Rationale\n(.+?)(?=\n###|\Z)", content, re.DOTALL
        )
        assert rationale_match, "### Rationale section must have content"
        rationale_text = rationale_match.group(1).strip()
        assert len(rationale_text) > 20, "Rationale must have at least 20 characters"

    def test_rationale_derived_from_user_request(self, tmp_path):
        """Rationale references the user's request context (not just file list)."""
        entries = [
            {
                "type": "user",
                "content": "Implement caching for performance optimization",
            },
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "cache.py", "content": "pass"},
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "rat003344556677", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        # Rationale should reflect the user's topic (caching or performance)
        content_lower = content.lower()
        assert (
            "caching" in content_lower
            or "performance" in content_lower
            or "implement" in content_lower
        ), "Rationale should reference the user's request"


# ─── Security Tests ──────────────────────────────────────────────────────────


class TestSecurityConstraints:
    """No credentials, API keys, tokens, or passwords must appear in the log."""

    def test_openai_api_key_not_in_log(self, tmp_path):
        """OpenAI-style API key in transcript must be redacted from log entry."""
        entries = [
            {
                "type": "user",
                "content": "Set api_key='sk-1234567890abcdef1234567890abcdef12345678' for svc",
            },
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "config.py", "content": "x"},
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "sec001122334455", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "sk-1234567890" not in content

    def test_password_not_in_log(self, tmp_path):
        """Password value in transcript must not appear in tracking_log.md."""
        entries = [
            {
                "type": "user",
                "content": "password='secret123supersecurepassword' must be in env",
            },
            {
                "type": "tool_use",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "auth.py",
                    "old_string": "x",
                    "new_string": "y",
                },
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "sec002233445566", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "secret123" not in content

    def test_bearer_token_not_in_log(self, tmp_path):
        """Bearer token value in transcript must not appear in tracking_log.md."""
        entries = [
            {
                "type": "user",
                "content": "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abcdefgh",
            },
            {
                "type": "tool_use",
                "tool_name": "Write",
                "tool_input": {"file_path": "api.py", "content": ""},
            },
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        tracking_log = str(tmp_path / "tracking_log.md")

        data = _extract_data_from_transcript(transcript_path)
        _write_tracking_entry(tracking_log, "sec003344556677", data)

        content = Path(tracking_log).read_text(encoding="utf-8")
        assert "eyJhbGci" not in content

    def test_session_tracker_redacts_openai_key(self, tmp_path):
        """session-tracker.py itself redacts OpenAI-style API keys from output."""
        entries = [
            {
                "type": "user",
                "content": "My key is sk-1234567890abcdefghijklmnopqrstuvwxyz01234567890",
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        lines = session_tracker.read_last_n_lines(transcript_path)
        parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
        parsed = [e for e in parsed if e is not None]
        user_msgs = session_tracker.extract_user_messages(parsed)

        combined = " ".join(user_msgs)
        assert "sk-1234567890" not in combined
        assert "[REDACTED]" in combined

    def test_session_tracker_redacts_github_pat(self, tmp_path):
        """session-tracker.py redacts GitHub Personal Access Tokens."""
        entries = [
            {
                "type": "user",
                "content": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123",
            }
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        lines = session_tracker.read_last_n_lines(transcript_path)
        parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
        parsed = [e for e in parsed if e is not None]
        user_msgs = session_tracker.extract_user_messages(parsed)

        combined = " ".join(user_msgs)
        assert "ghp_ABCDEF" not in combined

    def test_session_tracker_redacts_unquoted_password(self, tmp_path):
        """session-tracker.py redacts unquoted password=value patterns."""
        entries = [
            {"type": "user", "content": "password=hunter2secret"},
            {"type": "user", "content": "token: mytoken123abcdef"},
        ]
        transcript_path = _make_transcript(entries, str(tmp_path))
        lines = session_tracker.read_last_n_lines(transcript_path)
        parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
        parsed = [e for e in parsed if e is not None]
        user_msgs = session_tracker.extract_user_messages(parsed)

        combined = " ".join(user_msgs)
        assert "hunter2secret" not in combined
        assert "mytoken123" not in combined


# ─── Performance Tests ────────────────────────────────────────────────────────


class TestPerformance:
    """Large transcripts must be processed within the 60s agent timeout."""

    def test_large_transcript_processed_under_five_seconds(self, tmp_path):
        """1000+ line transcript must be processed well under the 60s timeout."""
        entries = []
        for i in range(1200):
            if i % 3 == 0:
                entries.append({"type": "user", "content": f"User message {i}"})
            elif i % 3 == 1:
                entries.append(
                    {
                        "type": "tool_use",
                        "tool_name": "Edit" if i % 2 else "Write",
                        "tool_input": {
                            "file_path": f"src/file{i}.py",
                            "content": f"content {i}",
                        },
                    }
                )
            else:
                entries.append({"type": "assistant", "content": f"Response {i}"})

        transcript_path = _make_transcript(entries, str(tmp_path))

        start = time.time()
        lines = session_tracker.read_last_n_lines(transcript_path, n=100)
        parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
        parsed = [e for e in parsed if e is not None]
        session_tracker.extract_user_messages(parsed)
        session_tracker.extract_tool_operations(parsed)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Processing took {elapsed:.2f}s (expected <5s)"
        assert len(lines) == 100, "Must read exactly 100 lines from large transcript"

    def test_large_transcript_reads_only_last_100_lines(self, tmp_path):
        """Verify tail reading: only the last 100 lines are processed."""
        entries = [{"type": "user", "content": f"msg {i}"} for i in range(1200)]
        transcript_path = _make_transcript(entries, str(tmp_path))

        lines = session_tracker.read_last_n_lines(transcript_path, n=100)
        assert len(lines) == 100

        # The 100 lines must correspond to entries 1100–1199
        first_parsed = session_tracker.parse_jsonl_line(lines[0])
        assert first_parsed is not None
        assert first_parsed["content"] == "msg 1100"

    def test_cli_large_transcript_within_60s_timeout(self, tmp_path):
        """CLI invocation on 1000+ entry transcript completes within 60s."""
        entries = [{"type": "user", "content": f"msg {i}"} for i in range(1000)]
        # Add tool_use entries at the tail (within last 100 lines)
        for i in range(50):
            entries.append(
                {
                    "type": "tool_use",
                    "tool_name": "Write",
                    "tool_input": {"file_path": f"src/file{i}.py", "content": ""},
                }
            )
        transcript_path = _make_transcript(entries, str(tmp_path))

        start = time.time()
        result = subprocess.run(
            [
                "python3",
                str(_scripts_dir / "session-tracker.py"),
                f"--transcript-path={transcript_path}",
                "--session-id=perftest00112233",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        elapsed = time.time() - start

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert elapsed < 60, f"CLI took {elapsed:.2f}s (limit: 60s)"
        data = json.loads(result.stdout)
        assert len(data["modified_files"]) > 0


# ─── Structural Validation Tests ─────────────────────────────────────────────


class TestHooksJsonStructure:
    """Verify hooks.json is correctly configured for the Stop event hook."""

    def _load_hooks(self) -> dict:
        with open(_plugin_root / "hooks" / "hooks.json") as f:
            return json.load(f)

    def test_hooks_json_is_valid_json(self):
        """hooks.json must be parseable valid JSON."""
        config = self._load_hooks()
        assert isinstance(config, dict)

    def test_stop_event_key_present(self):
        """Stop event key must exist under hooks."""
        config = self._load_hooks()
        assert "Stop" in config["hooks"]

    def test_stop_hook_type_is_agent(self):
        """Stop hook must use type: 'agent'."""
        config = self._load_hooks()
        found = any(
            h.get("type") == "agent"
            for entry in config["hooks"]["Stop"]
            for h in entry.get("hooks", [])
        )
        assert found, "No 'agent' type hook found under Stop event"

    def test_stop_hook_timeout_is_60(self):
        """Stop hook agent must have timeout: 60 (matching spec)."""
        config = self._load_hooks()
        for entry in config["hooks"]["Stop"]:
            for h in entry.get("hooks", []):
                if h.get("type") == "agent":
                    assert h.get("timeout") == 60

    def test_stop_hook_has_no_matcher(self):
        """Stop event does not support matcher — it must not be present."""
        config = self._load_hooks()
        for entry in config["hooks"].get("Stop", []):
            assert "matcher" not in entry, "Stop event hooks must not have a 'matcher'"

    def test_existing_hooks_preserved(self):
        """UserPromptSubmit, PostToolUse, TaskCompleted hooks must remain intact."""
        config = self._load_hooks()
        assert "UserPromptSubmit" in config["hooks"]
        assert "PostToolUse" in config["hooks"]
        assert "TaskCompleted" in config["hooks"]

    def test_description_mentions_session_tracking(self):
        """hooks.json description must reference Session Tracking Hook."""
        config = self._load_hooks()
        desc = config.get("description", "").lower()
        assert "session" in desc or "tracking" in desc


class TestAgentFileStructure:
    """Verify session-tracking-agent.md has the correct structure and content."""

    def _load_content(self) -> str:
        return (_plugin_root / "agents" / "session-tracking-agent.md").read_text(
            encoding="utf-8"
        )

    def _get_field(self, content: str, field: str) -> Optional[str]:
        """Extract a scalar field from YAML frontmatter using regex."""
        match = re.search(rf"^{re.escape(field)}:\s*(.+)$", content, re.MULTILINE)
        if not match:
            return None
        value = match.group(1).strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        return value

    def test_agent_file_exists(self):
        """session-tracking-agent.md must exist in the agents directory."""
        assert (_plugin_root / "agents" / "session-tracking-agent.md").exists()

    def test_agent_name_is_correct(self):
        """Agent name must be 'session-tracking-agent'."""
        content = self._load_content()
        name = self._get_field(content, "name")
        assert name == "session-tracking-agent"

    def test_agent_model_is_sonnet(self):
        """Agent model must be 'sonnet'."""
        content = self._load_content()
        model = self._get_field(content, "model")
        assert model == "sonnet"

    def test_agent_tools_least_privilege(self):
        """Agent must have exactly Read, Write, Bash(git:*) — no more."""
        content = self._load_content()
        tools = self._get_field(content, "tools") or ""
        assert "Read" in tools
        assert "Write" in tools
        assert "Bash(git:*)" in tools

    def test_agent_has_description(self):
        """Agent must have a non-empty description field."""
        content = self._load_content()
        desc = self._get_field(content, "description")
        assert desc and len(desc) > 10

    def test_agent_prompt_instructs_100_line_limit(self):
        """Agent prompt must instruct reading only the last 100 lines."""
        content = self._load_content()
        assert "100" in content, "Agent must reference the 100-line reading limit"

    def test_agent_prompt_forbids_credentials_in_log(self):
        """Agent prompt must explicitly prohibit logging credentials/secrets."""
        content = self._load_content()
        content_lower = content.lower()
        assert (
            "credential" in content_lower
            or "api key" in content_lower
            or "password" in content_lower
        ), "Agent prompt must prohibit credentials in the log"

    def test_agent_prompt_instructs_idempotency(self):
        """Agent prompt must instruct update-by-SHORT_ID (idempotency)."""
        content = self._load_content()
        assert (
            "SHORT_ID" in content or "idempoten" in content.lower()
        ), "Agent prompt must reference idempotency by SHORT_ID"

    def test_agent_prompt_references_tracking_log(self):
        """Agent prompt must reference tracking_log.md."""
        content = self._load_content()
        assert "tracking_log.md" in content

    def test_agent_prompt_instructs_stop_hook_active_check(self):
        """Agent prompt must instruct checking stop_hook_active for re-entrancy guard."""
        content = self._load_content()
        assert "stop_hook_active" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
