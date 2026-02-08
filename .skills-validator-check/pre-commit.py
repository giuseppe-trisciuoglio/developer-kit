#!/usr/bin/env python3
"""
Git pre-commit hook for validating Claude Code components.

This script is called by Git before each commit. It validates all staged
files matching skill/agent/command patterns and blocks the commit if
validation fails.
"""

import subprocess
import sys
from pathlib import Path

# Add validators package to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from validators.cli import ValidationCLI


def main() -> int:
    """Main entry point for pre-commit hook."""
    print("Validating Claude Code components...")

    cli = ValidationCLI()
    exit_code = cli.run()

    if exit_code == 1:
        print("\n" + "=" * 60)
        print("Commit blocked: Please fix validation errors above.")
        print("To bypass (not recommended): git commit --no-verify")
        print("=" * 60)
    elif exit_code == 0:
        print()  # Clean separation

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
