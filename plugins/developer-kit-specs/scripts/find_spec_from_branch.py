#!/usr/bin/env python3
"""
Find the spec folder matching the current git branch.

Convention: spec folders are named <id>-<branch> or match the branch name directly.
Example: branch "develop" → finds "docs/specs/xxx-develop/" or "docs/specs/develop/"
"""
import subprocess
import sys
import os
from pathlib import Path

def get_current_branch():
    try:
        output = subprocess.check_output(['git', 'branch', '--show-current'], stderr=subprocess.STDOUT)
        branch = output.decode().strip()
        if not branch:
            return None, "detached HEAD"
        return branch, None
    except subprocess.CalledProcessError as e:
        return None, e.output.decode()

def find_spec_folder(branch):
    specs_dir = Path("docs/specs")
    if not specs_dir.exists():
        return None, f"docs/specs/ does not exist"

    # Try exact match first: docs/specs/<branch>/
    exact = specs_dir / branch
    if exact.is_dir():
        return str(exact), None

    # Try pattern <id>-<branch>/
    for d in specs_dir.iterdir():
        if d.is_dir() and d.name.endswith(f"-{branch}"):
            return str(d), None
        if d.is_dir() and d.name == branch:
            return str(d), None

    return None, f"No spec folder found for branch '{branch}'"

def main():
    branch, error = get_current_branch()
    if error:
        sys.stderr.write(f"Error: {error}\n")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--branch-only":
        print(branch)
        return

    spec_folder, find_error = find_spec_folder(branch)
    if find_error:
        sys.stderr.write(f"Warning: {find_error}\n")
        sys.exit(1)

    print(spec_folder)

if __name__ == "__main__":
    main()
