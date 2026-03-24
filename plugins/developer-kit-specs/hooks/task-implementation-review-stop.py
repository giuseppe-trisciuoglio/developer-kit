#!/usr/bin/env python3
"""Stop hook enforcing review after /specs:task-implementation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


TASK_IMPLEMENTATION_PATTERN = re.compile(
    r"/specs:task-implementation\b(?P<args>[^\n\r]*)",
    re.IGNORECASE,
)
TASK_REVIEW_PATTERN = re.compile(
    r"/specs:task-review\b(?P<args>[^\n\r]*)",
    re.IGNORECASE,
)
SPEC_SYNC_PATTERN = re.compile(
    r"/specs:spec-sync-with-code\b(?P<args>[^\n\r]*)",
    re.IGNORECASE,
)
TASK_FILE_PATTERN = re.compile(
    r"docs/specs/[^\s\"']+/tasks/TASK-[^\s\"']+\.md",
    re.IGNORECASE,
)
LANG_PATTERN = re.compile(r"--lang=(?P<lang>[a-z-]+)", re.IGNORECASE)


def load_input() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def load_transcript(transcript_path: str) -> str:
    if not transcript_path:
        return ""

    try:
        return Path(transcript_path).expanduser().read_text(encoding="utf-8")
    except OSError:
        return ""


def extract_task_file(args_text: str) -> str | None:
    match = TASK_FILE_PATTERN.search(args_text)
    return match.group(0) if match else None


def extract_lang(args_text: str) -> str | None:
    match = LANG_PATTERN.search(args_text)
    return match.group("lang").lower() if match else None


def has_explicit_no_sync_needed(last_message: str) -> bool:
    lowered = last_message.lower()
    phrases = (
        "no spec update",
        "no specification update",
        "no spec sync",
        "no specification sync",
        "no documentation update",
        "specification is already aligned",
        "spec is already aligned",
        "no spec changes needed",
        "no specification changes needed",
    )
    return any(phrase in lowered for phrase in phrases)


def build_reason(task_file: str | None, lang: str | None) -> str:
    review_command = "/specs:task-review"
    if lang:
        review_command += f" --lang={lang}"
    if task_file:
        review_command += f" {task_file}"

    sync_command = "/specs:spec-sync-with-code"
    if task_file:
        spec_folder = task_file.split("/tasks/")[0]
        task_id = Path(task_file).stem
        sync_command += f" {spec_folder} --after-task={task_id}"

    return (
        "The latest `/specs:task-implementation` cannot stop yet. "
        "CRITICAL — context preservation: before proceeding, run `/compact` to free context space. "
        "If `/compact` is unavailable or context is still large, delegate the entire review workflow "
        "to a subagent via the Task tool (agent_type: 'general-purpose') passing it all the context "
        "it needs (task file path, spec folder, language) so it can perform the review independently. "
        f"The review workflow: run `{review_command}`, fix every review finding, rerun verification, "
        "then if the implementation changed or clarified the specification update the spec with "
        f"`{sync_command}`. If no spec update is needed, state that explicitly before stopping."
    )


def main() -> int:
    payload = load_input()
    if payload.get("hook_event_name") != "Stop":
        return 0

    if payload.get("stop_hook_active"):
        return 0

    transcript = load_transcript(payload.get("transcript_path", ""))
    if not transcript:
        return 0

    impl_matches = list(TASK_IMPLEMENTATION_PATTERN.finditer(transcript))
    if not impl_matches:
        return 0

    latest_impl = impl_matches[-1]
    impl_tail = transcript[latest_impl.end():]
    impl_args = latest_impl.group("args") or ""
    task_file = extract_task_file(impl_args)
    lang = extract_lang(impl_args)

    review_matches = list(TASK_REVIEW_PATTERN.finditer(impl_tail))
    if task_file:
        review_matches = [
            match for match in review_matches if task_file in (match.group("args") or "")
        ]

    if not review_matches:
        print(json.dumps({"decision": "block", "reason": build_reason(task_file, lang)}))
        return 0

    after_review = impl_tail[review_matches[-1].end():]
    if SPEC_SYNC_PATTERN.search(after_review):
        return 0

    last_message = payload.get("last_assistant_message") or ""
    if has_explicit_no_sync_needed(last_message):
        return 0

    print(json.dumps({"decision": "block", "reason": build_reason(task_file, lang)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
