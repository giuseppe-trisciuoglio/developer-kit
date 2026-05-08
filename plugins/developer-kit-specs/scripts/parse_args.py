#!/usr/bin/env python3
"""
Argument parser for developer-kit-specs commands.
Reads arguments from argv[1] or stdin, outputs JSON with extracted parameters.

Usage (from command markdown):
    python3 scripts/parse_args.py "$ARGUMENTS"

Usage (from hooks):
    python3 scripts/parse_args.py --task="docs/specs/001/feature/tasks/TASK-001.md"

Output: JSON to stdout
{
    "task":       "path/to/TASK-001.md or null",
    "spec":       "path/to/spec-folder or null",
    "lang":       "spring or null",
    "action":     "add or null",
    "flags":      ["dry-run", "kg-only"],
    "positional": ["docs/specs/001-feature/"],
    "raw":        "original arguments string"
}
"""

import re, sys, json

VALID_LANGS = {"java", "spring", "typescript", "ts", "nestjs", "react",
               "python", "py", "php", "general"}


def parse_args(arguments: str) -> dict:
    """Parse $ARGUMENTS string into structured dict."""
    result = {
        "task": None,
        "spec": None,
        "lang": None,
        "action": None,
        "flags": [],
        "positional": [],
        "raw": arguments,
    }

    # --- Task reference (--task=...) ---
    task_match = re.search(r'--task=([^\s]+)', arguments)
    if task_match:
        val = task_match.group(1).strip('"\'')
        # Format 1: full path (contains / or \)
        if '/' in val or '\\' in val:
            result["task"] = val
        # Format 2: task ID (no path separator)
        else:
            result["task_id"] = val

    # --- Spec folder (--spec=...) ---
    spec_match = re.search(r'--spec=([^\s]+)', arguments)
    if spec_match:
        result["spec"] = spec_match.group(1).strip('"\'')

    # Derive task path from spec + task_id if needed
    if result.get("task_id") and result["spec"] and not result["task"]:
        result["task"] = f"{result['spec']}/tasks/{result['task_id']}.md"
        del result["task_id"]
    elif result.get("task_id") and not result["spec"]:
        pass # keep task_id if needed, but we don't have it in the initial result dict

    # --- Language (--lang=...) ---
    lang_match = re.search(r'--lang=([^\s]+)', arguments)
    if lang_match:
        lang = lang_match.group(1).lower()
        if lang == "ts":
            lang = "typescript"
        if lang == "py":
            lang = "python"
        if lang in VALID_LANGS:
            result["lang"] = lang

    # --- Action (--action=...) ---
    action_match = re.search(r'--action=([^\s]+)', arguments)
    if action_match:
        result["action"] = action_match.group(1).lower()

    # --- Boolean flags (--flag-name) ---
    KNOWN_FLAGS = {"dry-run", "kg-only", "code-only", "update-kg-only",
                   "no-confirm", "background", "quick", "validate"}
    for flag in KNOWN_FLAGS:
        if re.search(rf'--{re.escape(flag)}(?:\s|$|=)', arguments):
            result["flags"].append(flag)

    # --- Positional arguments (first path-like token) ---
    pos_match = re.match(r'^([^\s-][^\s]*(?:/|\\))', arguments.strip())
    if pos_match:
        result["positional"].append(pos_match.group(1).rstrip('/\\'))

    return result


def main():
    if len(sys.argv) > 1:
        arguments = sys.argv[1]
    else:
        arguments = sys.stdin.read().strip()

    result = parse_args(arguments)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
