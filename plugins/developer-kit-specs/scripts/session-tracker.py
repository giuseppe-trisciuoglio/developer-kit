#!/usr/bin/env python3
"""Session Tracker - Extract structured data from Claude Code transcript JSONL.

Reads the last 100 lines of a Claude Code transcript JSONL file and extracts:
- User messages (last 10)
- Tool operation counts (Edit, Write, Delete)
- Modified file paths

All credentials, API keys, and tokens are redacted from output.
Exits 0 on all paths (graceful degradation).

Usage:
    python3 session-tracker.py --transcript-path=/path/to/transcript.jsonl
    python3 session-tracker.py --transcript-path=/path/to/transcript.jsonl --session-id=abc123def456

Output: JSON to stdout
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# ─── Constants ──────────────────────────────────────────────────────────────

MAX_LINES = 100
MAX_USER_MESSAGES = 10

# File-related tool names that produce file_path in their input
FILE_TOOL_NAMES = {"Edit", "Write"}

# Patterns indicating file deletion in Bash commands
DELETE_PATTERNS = re.compile(r"\b(rm\s|rmdir\s|git\s+rm\s)", re.IGNORECASE)

# Pattern to extract file path from rm/rmdir/git rm commands
_DELETE_PATH_PATTERN = re.compile(
    r"(?:\brm\b|\brmdir\b|\bgit\s+rm\b)"
    r"(?:\s+-\w+)*"  # optional flags like -rf, -r, --cached
    r"(?:\s+--\s*)?"  # optional --
    r"\s+"
    r"([^\s;|&]+)",  # capture the file path
    re.IGNORECASE,
)

# ─── Secret Redaction ───────────────────────────────────────────────────────

_SECRET_PATTERNS: list[re.Pattern] = [
    # key=value / key:value patterns with quotes
    re.compile(
        r"""(api[_-]?key|password|passwd|token|secret|credential|auth[_-]?token|access[_-]?key|private[_-]?key)\s*[:=]\s*["']"""
        r"""[A-Za-z0-9\-._~+/!@#$%^&*()]+=*["']""",
        re.IGNORECASE,
    ),
    # Unquoted key=value / key: value patterns (no surrounding quotes)
    re.compile(
        r"""(api[_-]?key|password|passwd|token|secret|credential|auth[_-]?token|access[_-]?key|private[_-]?key)\s*[:=]\s*(?!["'])[^\s"',;\n]{4,}""",
        re.IGNORECASE,
    ),
    # Bearer tokens
    re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    # Common key formats — capture prefix so the key value itself is redacted
    re.compile(r"(sk-)[a-zA-Z0-9]{20,}"),  # OpenAI-style
    re.compile(r"(ghp_)[a-zA-Z0-9]{36,}"),  # GitHub PAT
    re.compile(r"(glpat-)[a-zA-Z0-9\-]{20,}"),  # GitLab PAT
    re.compile(r"(AKIA)[0-9A-Z]{16}"),  # AWS access key ID
    re.compile(
        r"(-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----)[\s\S]*?(-----END[^\n-]*)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----)[^\n]*", re.IGNORECASE
    ),  # Partial PEM (no END)
]


def redact_secrets(text: str) -> str:
    """Remove credentials, API keys, and tokens from text."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text


# ─── Transcript Reading ────────────────────────────────────────────────────


def read_last_n_lines(file_path: str, n: int = MAX_LINES) -> list[str]:
    """Read last N lines from a file by seeking from the end.

    Only reads the tail portion of the file needed, never iterates
    the full content from start to finish.
    Returns empty list on any error.
    """
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return []

        file_size = path.stat().st_size
        if file_size == 0:
            return []

        with open(path, "rb") as f:
            # Read backwards in blocks until we have enough newlines
            block_size = 8192
            newline_count = 0
            position = file_size
            chunks: list[bytes] = []

            while newline_count <= n and position > 0:
                read_size = min(block_size, position)
                position -= read_size
                f.seek(position)
                chunk = f.read(read_size)
                chunks.insert(0, chunk)
                newline_count += chunk.count(b"\n")

            # Decode collected chunks
            content = b"".join(chunks).decode("utf-8", errors="replace")
            all_lines = content.splitlines()

            # If we didn't read from position 0, the first line is partial
            if position > 0 and all_lines:
                all_lines = all_lines[1:]

            # Return the last N lines
            return all_lines[-n:] if len(all_lines) > n else all_lines
    except (OSError, IOError):
        return []


def parse_jsonl_line(line: str) -> dict[str, Any] | None:
    """Parse a single JSONL line. Returns None on any parse failure."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None


# ─── User Message Extraction ───────────────────────────────────────────────


def _extract_text_from_content(raw: Any) -> str:
    """Extract text from various content formats (string, list of blocks)."""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts: list[str] = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts)
    if isinstance(raw, dict):
        return raw.get("text", "")
    return ""


def extract_user_messages(entries: list[dict]) -> list[str]:
    """Extract user messages from transcript entries (last 10)."""
    messages: list[str] = []
    for entry in entries:
        entry_type = entry.get("type", "")
        role = entry.get("role", "")
        msg_role = (
            entry.get("message", {}).get("role", "")
            if isinstance(entry.get("message"), dict)
            else ""
        )

        is_user = (
            entry_type == "user"
            or role == "user"
            or msg_role == "user"
            or entry_type == "human"
        )
        if not is_user:
            continue

        # Content can be in entry.content or entry.message.content
        raw_content = (
            entry.get("message", {}).get("content")
            if isinstance(entry.get("message"), dict)
            else None
        )
        if raw_content is None:
            raw_content = entry.get("content")

        text = _extract_text_from_content(raw_content).strip()
        if text:
            messages.append(redact_secrets(text))

    return messages[-MAX_USER_MESSAGES:]


# ─── Tool Operation Extraction ─────────────────────────────────────────────


def _process_tool_entry(
    tool_name: str,
    tool_input: dict[str, Any],
    tool_counts: Counter,
    file_paths: set[str],
) -> None:
    """Process a single tool operation and update counters/paths."""
    if tool_name in FILE_TOOL_NAMES:
        tool_counts[tool_name] += 1
        fp = tool_input.get("file_path", "")
        if fp:
            file_paths.add(fp)
    elif tool_name == "Bash":
        cmd = tool_input.get("command", "")
        if cmd and DELETE_PATTERNS.search(cmd):
            tool_counts["Delete"] += 1
            # Extract deleted file path
            match = _DELETE_PATH_PATTERN.search(cmd)
            if match:
                deleted_path = match.group(1).strip("'\"")
                if deleted_path:
                    file_paths.add(deleted_path)


def extract_tool_operations(entries: list[dict]) -> dict[str, Any]:
    """Extract tool operation counts and modified file paths."""
    tool_counts: Counter = Counter()
    file_paths: set[str] = set()

    for entry in entries:
        entry_type = entry.get("type", "")

        # Direct tool_use entries
        if entry_type == "tool_use" or entry.get("tool_name"):
            tool_name = entry.get("tool_name") or entry.get("name") or ""
            tool_input = entry.get("tool_input") or entry.get("input") or {}
            if tool_name:
                _process_tool_entry(tool_name, tool_input, tool_counts, file_paths)

        # Assistant messages with tool_use blocks in content
        elif entry_type == "assistant" and isinstance(entry.get("message"), dict):
            content = entry["message"].get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_name = block.get("name", "")
                        tool_input = block.get("input", {})
                        if tool_name:
                            _process_tool_entry(
                                tool_name, tool_input, tool_counts, file_paths
                            )

    return {
        "tool_operations": {
            "Write": tool_counts.get("Write", 0),
            "Edit": tool_counts.get("Edit", 0),
            "Delete": tool_counts.get("Delete", 0),
        },
        "modified_files": sorted(file_paths),
    }


# ─── Session ID ─────────────────────────────────────────────────────────────


def derive_short_session_id(session_id: str | None) -> str | None:
    """Derive short session ID (first 8 characters)."""
    if not session_id:
        return None
    return session_id[:8] if len(session_id) >= 8 else session_id


# ─── Output ─────────────────────────────────────────────────────────────────


def build_result(
    session_id: str | None,
    user_messages: list[str],
    tool_data: dict[str, Any],
) -> dict[str, Any]:
    """Build the final JSON result."""
    return {
        "session_id_short": derive_short_session_id(session_id),
        "user_messages": user_messages,
        "tool_operations": tool_data["tool_operations"],
        "modified_files": tool_data["modified_files"],
    }


def output_json(result: dict[str, Any]) -> None:
    """Write result as JSON to stdout."""
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ─── Entry Point ─────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured data from Claude Code transcript JSONL",
    )
    parser.add_argument(
        "--transcript-path",
        required=True,
        help="Path to transcript JSONL file",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Session ID (used to derive short ID, first 8 chars)",
    )
    args = parser.parse_args()

    # Read last N lines of transcript
    lines = read_last_n_lines(args.transcript_path)

    if not lines:
        # No lines read: output empty/default result
        result = build_result(
            session_id=args.session_id,
            user_messages=[],
            tool_data={
                "tool_operations": {"Write": 0, "Edit": 0, "Delete": 0},
                "modified_files": [],
            },
        )
        output_json(result)
        sys.exit(0)

    # Parse JSONL entries
    entries: list[dict] = []
    for line in lines:
        parsed = parse_jsonl_line(line)
        if parsed is not None:
            entries.append(parsed)

    # Extract structured data
    user_messages = extract_user_messages(entries)
    tool_data = extract_tool_operations(entries)

    result = build_result(
        session_id=args.session_id,
        user_messages=user_messages,
        tool_data=tool_data,
    )

    output_json(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
