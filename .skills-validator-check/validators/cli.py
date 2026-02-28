"""
CLI entry point for the validation system.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Support both direct execution and package import
if __name__ == "__main__" or __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from validators.config import VERSION
    from validators.models import ValidationResult
    from validators.reporter import ConsoleReporter, JsonReporter
    from validators.validators import ValidatorFactory
else:
    from .config import VERSION
    from .models import ValidationResult
    from .reporter import ConsoleReporter, JsonReporter
    from .validators import ValidatorFactory


class ValidationCLI:
    """Main entry point for the validation system."""

    def __init__(self):
        self.repo_root = self._find_repo_root()

    def _find_repo_root(self) -> Path:
        """Find the repository root directory."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"Warning: git command failed: {e.stderr.strip() if e.stderr else 'unknown error'}", file=sys.stderr)
            return Path.cwd()
        except FileNotFoundError:
            print("Warning: git not found, using current directory as repo root", file=sys.stderr)
            return Path.cwd()

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Execute validation and return exit code.

        Args:
            args: Command line arguments (uses sys.argv if None)

        Returns:
            Exit code: 0 = success, 1 = validation errors, 2 = system error
        """
        parser = self._create_parser()
        parsed = parser.parse_args(args)

        try:
            # Get files to validate
            if parsed.files:
                files = [Path(f) for f in parsed.files]
            elif parsed.all:
                files = self._find_all_component_files()
            else:
                files = self._get_staged_files()

            if not files:
                print("No files to validate.")
                return 0

            # Filter to component files only
            component_files = self._filter_component_files(files)

            if not component_files:
                print("No Claude Code components to validate.")
                return 0

            # Validate each file
            results: List[ValidationResult] = []
            for file_path in component_files:
                result = self._validate_file(file_path)
                if result:
                    results.append(result)

            # Report results
            if parsed.format == "json":
                reporter = JsonReporter()
            else:
                reporter = ConsoleReporter(
                    use_colors=parsed.format != "plain",
                    verbose=parsed.verbose,
                    quiet=parsed.quiet
                )

            return reporter.report(results)

        except Exception as e:
            print(f"System error: {e}", file=sys.stderr)
            if parsed.verbose:
                import traceback
                traceback.print_exc()
            return 2

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            prog="claude-validator",
            description="Validate Claude Code components (Skills, Agents, Commands)",
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {VERSION}"
        )

        parser.add_argument(
            "--files",
            nargs="+",
            help="Specific files to validate"
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="Validate all component files in the repository"
        )

        parser.add_argument(
            "--format",
            choices=["console", "plain", "json"],
            default="console",
            help="Output format (default: console with colors)"
        )

        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Show verbose output including valid files"
        )

        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            help="Show only errors (suppress warnings)"
        )

        return parser

    def _get_staged_files(self) -> List[Path]:
        """Get list of staged files from Git."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )

            output = result.stdout.strip()
            if not output:
                return []

            files = []
            for line in output.split("\n"):
                files.append(self.repo_root / line)
            return files

        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to get staged files: {e.stderr.strip() if e.stderr else 'unknown error'}", file=sys.stderr)
            return []

    def _find_all_component_files(self) -> List[Path]:
        """Find all component files in the repository."""
        files = []

        # Root-level components (legacy structure)
        skills_dir = self.repo_root / "skills"
        if skills_dir.exists():
            files.extend(skills_dir.glob("**/SKILL.md"))

        agents_dir = self.repo_root / "agents"
        if agents_dir.exists():
            files.extend(agents_dir.glob("*.md"))

        commands_dir = self.repo_root / ".claude" / "commands"
        if commands_dir.exists():
            files.extend(commands_dir.glob("*.md"))

        # Root-level commands directory (non-.claude)
        root_commands_dir = self.repo_root / "commands"
        if root_commands_dir.exists():
            files.extend(root_commands_dir.glob("*.md"))

        # Plugin-based components (new multi-plugin structure)
        plugins_dir = self.repo_root / "plugins"
        if plugins_dir.exists():
            for plugin_dir in plugins_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue

                # Plugin skills
                plugin_skills = plugin_dir / "skills"
                if plugin_skills.exists():
                    files.extend(plugin_skills.glob("**/SKILL.md"))

                # Plugin agents
                plugin_agents = plugin_dir / "agents"
                if plugin_agents.exists():
                    files.extend(plugin_agents.glob("*.md"))

                # Plugin commands
                plugin_commands = plugin_dir / "commands"
                if plugin_commands.exists():
                    files.extend(plugin_commands.glob("**/*.md"))

                # Plugin rules
                plugin_rules = plugin_dir / "rules"
                if plugin_rules.exists():
                    files.extend(plugin_rules.glob("*.md"))

                # Plugin.json files
                plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
                if plugin_json.exists():
                    files.append(plugin_json)

        return sorted(files)

    def _filter_component_files(self, files: List[Path]) -> List[Path]:
        """Filter to only include component files."""
        component_files = []
        for file_path in files:
            validator = ValidatorFactory.get_validator(file_path)
            if validator is not None:
                component_files.append(file_path)
        return component_files

    def _validate_file(self, file_path: Path) -> Optional[ValidationResult]:
        """Validate a single file."""
        validator = ValidatorFactory.get_validator(file_path)
        if validator is None:
            return None
        return validator.validate(file_path)


def main() -> int:
    """Main entry point."""
    cli = ValidationCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
