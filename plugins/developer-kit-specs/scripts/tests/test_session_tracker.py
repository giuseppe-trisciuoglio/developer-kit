#!/usr/bin/env python3
"""Unit and integration tests for session-tracker.py.

Tests cover:
- Transcript JSONL parsing and data extraction
- User message extraction (last 10, redacted)
- Tool operation counting (Write, Edit, Delete)
- Modified file path extraction (including delete paths)
- Efficient tail reading (last 100 lines only)
- Secret redaction from output
- Edge cases: missing file, empty file, malformed JSONL
"""

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

# Import the module under test
scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "session_tracker", os.path.join(scripts_dir, "session-tracker.py")
)
session_tracker = importlib.util.module_from_spec(spec)
sys.modules["session_tracker"] = session_tracker
spec.loader.exec_module(session_tracker)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_transcript(entries: list[dict]) -> str:
    """Create a temporary JSONL file from entries and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
    for entry in entries:
        tmp.write(json.dumps(entry) + "\n")
    tmp.close()
    return tmp.name


def _cleanup(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


# ─── Unit Tests: Transcript Reading ──────────────────────────────────────────


class TestReadLastNLines:
    """Test efficient tail reading of transcript files."""

    def test_reads_last_n_lines_efficiently(self):
        """Only last N lines are returned, not the full file."""
        lines = [{"line": i} for i in range(200)]
        path = _make_transcript(lines)
        try:
            result = session_tracker.read_last_n_lines(path, n=100)
            assert len(result) == 100
            # Should be the last 100 lines (100-199)
            first = json.loads(result[0])
            assert first["line"] == 100
            last = json.loads(result[-1])
            assert last["line"] == 199
        finally:
            _cleanup(path)

    def test_returns_all_if_fewer_than_n(self):
        """If file has fewer lines than N, return all."""
        lines = [{"line": i} for i in range(50)]
        path = _make_transcript(lines)
        try:
            result = session_tracker.read_last_n_lines(path, n=100)
            assert len(result) == 50
        finally:
            _cleanup(path)

    def test_missing_file_returns_empty(self):
        """Missing file returns empty list."""
        result = session_tracker.read_last_n_lines("/nonexistent/path.jsonl")
        assert result == []

    def test_empty_file_returns_empty(self):
        """Empty file returns empty list."""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        tmp.close()
        try:
            result = session_tracker.read_last_n_lines(tmp.name)
            assert result == []
        finally:
            _cleanup(tmp.name)


# ─── Unit Tests: User Message Extraction ─────────────────────────────────────


class TestExtractUserMessages:
    """Test user message extraction and redaction."""

    def test_extracts_user_messages(self):
        entries = [
            {"type": "user", "content": "Hello"},
            {"type": "assistant", "content": "Hi"},
            {"type": "user", "content": "Fix bug"},
        ]
        result = session_tracker.extract_user_messages(entries)
        assert len(result) == 2
        assert "Hello" in result[0]
        assert "Fix bug" in result[1]

    def test_limits_to_last_10(self):
        entries = [{"type": "user", "content": f"msg{i}"} for i in range(20)]
        result = session_tracker.extract_user_messages(entries)
        assert len(result) == 10
        assert "msg10" in result[0]

    def test_redacts_secrets(self):
        entries = [
            {"type": "user", "content": "api_key='sk-abc123def456ghi789jkl012mno345'"},
        ]
        result = session_tracker.extract_user_messages(entries)
        assert "sk-abc123" not in result[0]
        assert "[REDACTED]" in result[0]

    def test_handles_message_dict_format(self):
        entries = [
            {"type": "user", "message": {"role": "user", "content": "nested msg"}},
        ]
        result = session_tracker.extract_user_messages(entries)
        assert len(result) == 1
        assert "nested msg" in result[0]

    def test_handles_content_block_format(self):
        entries = [
            {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "block msg"}]}},
        ]
        result = session_tracker.extract_user_messages(entries)
        assert len(result) == 1
        assert "block msg" in result[0]


# ─── Unit Tests: Tool Operation Extraction ───────────────────────────────────


class TestExtractToolOperations:
    """Test tool operation counting and file path extraction."""

    def test_counts_write_operations(self):
        entries = [
            {"type": "tool_use", "tool_name": "Write", "tool_input": {"file_path": "/tmp/a.py", "content": "x"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Write"] == 1
        assert "/tmp/a.py" in result["modified_files"]

    def test_counts_edit_operations(self):
        entries = [
            {"type": "tool_use", "tool_name": "Edit", "tool_input": {"file_path": "/tmp/b.py", "old_string": "x", "new_string": "y"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Edit"] == 1
        assert "/tmp/b.py" in result["modified_files"]

    def test_counts_delete_operations_with_path(self):
        """Delete operations should count AND capture file path."""
        entries = [
            {"type": "tool_use", "tool_name": "Bash", "tool_input": {"command": "rm -rf /tmp/old.py"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Delete"] == 1
        assert "/tmp/old.py" in result["modified_files"]

    def test_delete_git_rm_captures_path(self):
        """git rm should also capture the deleted file path."""
        entries = [
            {"type": "tool_use", "tool_name": "Bash", "tool_input": {"command": "git rm src/old.java"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Delete"] == 1
        assert "src/old.java" in result["modified_files"]

    def test_delete_rmdir_captures_path(self):
        """rmdir should capture the directory path."""
        entries = [
            {"type": "tool_use", "tool_name": "Bash", "tool_input": {"command": "rmdir build/"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Delete"] == 1
        assert "build/" in result["modified_files"]

    def test_non_delete_bash_not_counted(self):
        """Bash commands without delete patterns should not count as Delete."""
        entries = [
            {"type": "tool_use", "tool_name": "Bash", "tool_input": {"command": "npm test"}},
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Delete"] == 0
        assert result["modified_files"] == []

    def test_assistant_tool_use_blocks(self):
        """Tool use blocks inside assistant messages should be parsed."""
        entries = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/c.py", "content": "z"}},
                    ],
                },
            },
        ]
        result = session_tracker.extract_tool_operations(entries)
        assert result["tool_operations"]["Write"] == 1
        assert "/tmp/c.py" in result["modified_files"]

    def test_empty_entries_returns_zeros(self):
        result = session_tracker.extract_tool_operations([])
        assert result["tool_operations"]["Write"] == 0
        assert result["tool_operations"]["Edit"] == 0
        assert result["tool_operations"]["Delete"] == 0
        assert result["modified_files"] == []


# ─── Unit Tests: Secret Redaction ────────────────────────────────────────────


class TestRedactSecrets:
    """Test that credentials are never output."""

    def test_redacts_api_key(self):
        text = 'api_key = "sk-abc123def456ghi789jkl012mno345pqr678"'
        result = session_tracker.redact_secrets(text)
        assert "sk-abc123" not in result
        assert "[REDACTED]" in result

    def test_redacts_password(self):
        text = 'password = "supersecret123"'
        result = session_tracker.redact_secrets(text)
        assert "supersecret123" not in result

    def test_redacts_bearer_token(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abc"
        result = session_tracker.redact_secrets(text)
        assert "eyJhbGci" not in result
        assert "[REDACTED]" in result

    def test_redacts_github_pat(self):
        text = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123"
        result = session_tracker.redact_secrets(text)
        assert "ghp_ABCD" not in result

    def test_preserves_normal_text(self):
        text = "This is a normal message about fixing a bug"
        result = session_tracker.redact_secrets(text)
        assert result == text


# ─── Unit Tests: Session ID ──────────────────────────────────────────────────


class TestDeriveShortSessionId:
    """Test session ID shortening."""

    def test_shortens_long_id(self):
        result = session_tracker.derive_short_session_id("abc123def456ghi789")
        assert result == "abc123de"

    def test_short_id_unchanged(self):
        result = session_tracker.derive_short_session_id("short")
        assert result == "short"

    def test_none_returns_none(self):
        result = session_tracker.derive_short_session_id(None)
        assert result is None


# ─── Integration Tests: End-to-End ───────────────────────────────────────────


class TestEndToEnd:
    """Integration tests with full transcript processing."""

    def test_full_transcript_processing(self):
        """Test with a realistic transcript containing all operation types."""
        entries = [
            {"type": "user", "content": "Create a new file"},
            {"type": "tool_use", "tool_name": "Write", "tool_input": {"file_path": "src/main.py", "content": "print('hello')"}},
            {"type": "user", "content": "Now edit it"},
            {"type": "tool_use", "tool_name": "Edit", "tool_input": {"file_path": "src/main.py", "old_string": "hello", "new_string": "world"}},
            {"type": "user", "content": "Remove old file"},
            {"type": "tool_use", "tool_name": "Bash", "tool_input": {"command": "rm -f src/old.py"}},
            {"type": "user", "content": "My api_key='sk-secret123456789abcdef012345'"},
        ]
        path = _make_transcript(entries)
        try:
            lines = session_tracker.read_last_n_lines(path)
            parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
            parsed = [p for p in parsed if p is not None]

            user_msgs = session_tracker.extract_user_messages(parsed)
            tool_data = session_tracker.extract_tool_operations(parsed)

            # User messages
            assert len(user_msgs) == 4

            # Secret redacted in user message
            secret_msg = [m for m in user_msgs if "api_key" in m][0]
            assert "sk-secret" not in secret_msg
            assert "[REDACTED]" in secret_msg

            # Tool operations
            assert tool_data["tool_operations"]["Write"] == 1
            assert tool_data["tool_operations"]["Edit"] == 1
            assert tool_data["tool_operations"]["Delete"] == 1

            # Modified files include write, edit, AND delete paths
            assert "src/main.py" in tool_data["modified_files"]
            assert "src/old.py" in tool_data["modified_files"]
        finally:
            _cleanup(path)

    def test_large_transcript_only_last_100(self):
        """Transcript with >100 lines should only read last 100."""
        entries = []
        for i in range(200):
            entries.append({"type": "user", "content": f"message {i}"})

        path = _make_transcript(entries)
        try:
            lines = session_tracker.read_last_n_lines(path, n=100)
            assert len(lines) == 100
            parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
            parsed = [p for p in parsed if p is not None]
            user_msgs = session_tracker.extract_user_messages(parsed)
            # Should only see messages from last 100 lines (100-199)
            assert len(user_msgs) == 10  # capped at 10
            assert "message 190" in user_msgs[0]
        finally:
            _cleanup(path)

    def test_transcript_with_secrets_redacted(self):
        """Secrets in transcript should be redacted in output."""
        entries = [
            {"type": "user", "content": "password = 'hunter2password1234567890ab'"},
            {"type": "user", "content": "token='ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123'"},
            {"type": "tool_use", "tool_name": "Write", "tool_input": {"file_path": "/tmp/cfg.py", "content": "key='sk-longkey123456789abcdef0123456789'"}},
        ]
        path = _make_transcript(entries)
        try:
            lines = session_tracker.read_last_n_lines(path)
            parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
            parsed = [p for p in parsed if p is not None]
            user_msgs = session_tracker.extract_user_messages(parsed)

            combined = " ".join(user_msgs)
            assert "hunter2" not in combined
            assert "ghp_ABCD" not in combined
        finally:
            _cleanup(path)

    def test_malformed_jsonl_handled_gracefully(self):
        """Malformed lines should be skipped gracefully."""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
        tmp.write('{"type": "user", "content": "valid"}\n')
        tmp.write('NOT JSON\n')
        tmp.write('{"type": "user", "content": "also valid"}\n')
        tmp.write('\n')
        tmp.write('{"broken\n')
        tmp.close()
        try:
            lines = session_tracker.read_last_n_lines(tmp.name)
            parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
            parsed = [p for p in parsed if p is not None]
            user_msgs = session_tracker.extract_user_messages(parsed)
            assert len(user_msgs) == 2
        finally:
            _cleanup(tmp.name)

    def test_only_user_messages_no_tools(self):
        """Transcript with only user messages should reflect zero operations."""
        entries = [
            {"type": "user", "content": "Hello"},
            {"type": "user", "content": "World"},
        ]
        path = _make_transcript(entries)
        try:
            lines = session_tracker.read_last_n_lines(path)
            parsed = [session_tracker.parse_jsonl_line(l) for l in lines]
            parsed = [p for p in parsed if p is not None]
            tool_data = session_tracker.extract_tool_operations(parsed)
            assert tool_data["tool_operations"]["Write"] == 0
            assert tool_data["tool_operations"]["Edit"] == 0
            assert tool_data["tool_operations"]["Delete"] == 0
            assert tool_data["modified_files"] == []
        finally:
            _cleanup(path)


# ─── CLI Integration Tests ───────────────────────────────────────────────────


class TestCLI:
    """Test CLI argument handling."""

    def test_cli_with_transcript_path(self):
        """CLI should accept --transcript-path and output JSON."""
        entries = [{"type": "user", "content": "hello"}]
        path = _make_transcript(entries)
        try:
            with patch("sys.argv", ["session-tracker.py", f"--transcript-path={path}"]):
                import io
                from contextlib import redirect_stdout
                f = io.StringIO()
                with redirect_stdout(f):
                    with pytest.raises(SystemExit) as exc_info:
                        session_tracker.main()
                    assert exc_info.value.code == 0
                output = f.getvalue()
                data = json.loads(output)
                assert "user_messages" in data
                assert "tool_operations" in data
                assert "modified_files" in data
                assert len(data["user_messages"]) == 1
        finally:
            _cleanup(path)

    def test_cli_missing_file_outputs_default(self):
        """CLI with missing file should output default JSON and exit 0."""
        with patch("sys.argv", ["session-tracker.py", "--transcript-path=/nonexistent/file.jsonl"]):
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                with pytest.raises(SystemExit) as exc_info:
                    session_tracker.main()
                assert exc_info.value.code == 0
            output = f.getvalue()
            data = json.loads(output)
            assert data["user_messages"] == []
            assert data["tool_operations"]["Write"] == 0
            assert data["modified_files"] == []

    def test_cli_with_session_id(self):
        """CLI should derive short session ID."""
        entries = [{"type": "user", "content": "test"}]
        path = _make_transcript(entries)
        try:
            with patch("sys.argv", ["session-tracker.py", f"--transcript-path={path}", "--session-id=longid123456789"]):
                import io
                from contextlib import redirect_stdout
                f = io.StringIO()
                with redirect_stdout(f):
                    with pytest.raises(SystemExit) as exc_info:
                        session_tracker.main()
                    assert exc_info.value.code == 0
                output = f.getvalue()
                data = json.loads(output)
                assert data["session_id_short"] == "longid12"
        finally:
            _cleanup(path)
