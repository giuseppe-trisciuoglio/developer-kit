"""
Console output formatting for validation results.
"""

import sys
from typing import List

from .models import ValidationResult, ValidationIssue, Severity


class ColorCode:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


class ConsoleReporter:
    """Formats and outputs validation results to console."""

    SEVERITY_COLORS = {
        Severity.ERROR: ColorCode.RED,
        Severity.WARNING: ColorCode.YELLOW,
        Severity.INFO: ColorCode.BLUE,
    }

    UNICODE_SEVERITY_SYMBOLS = {
        Severity.ERROR: "\u2717",  # ✗
        Severity.WARNING: "\u26a0",  # ⚠
        Severity.INFO: "\u2139",  # ℹ
    }

    ASCII_SEVERITY_SYMBOLS = {
        Severity.ERROR: "x",
        Severity.WARNING: "!",
        Severity.INFO: "i",
    }

    def __init__(self, use_colors: bool = True, verbose: bool = False, quiet: bool = False):
        """
        Initialize the reporter.

        Args:
            use_colors: Whether to use ANSI colors (auto-disabled if not a TTY)
            verbose: Whether to show verbose output including successful validations
            quiet: Whether to suppress warnings (show only errors)
        """
        self.use_colors = use_colors and sys.stdout.isatty()
        self.output_encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        self.supports_unicode = self._supports_unicode(self.output_encoding)
        self.verbose = verbose
        self.quiet = quiet

    def _color(self, color: str, text: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_colors:
            return f"{color}{text}{ColorCode.RESET}"
        return text

    def _supports_unicode(self, encoding: str) -> bool:
        """Check whether the output stream encoding can emit Unicode safely."""
        try:
            "\u2713".encode(encoding)
            return True
        except (LookupError, UnicodeEncodeError):
            return False

    def _emit(self, text: str = "") -> None:
        """Print text using a safe fallback for ASCII-only streams."""
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode(self.output_encoding, errors="replace").decode(self.output_encoding)
            print(safe_text)

    def _symbol(self, severity: Severity) -> str:
        """Return the best symbol for the current terminal encoding."""
        if self.supports_unicode:
            return self.UNICODE_SEVERITY_SYMBOLS.get(severity, "?")
        return self.ASCII_SEVERITY_SYMBOLS.get(severity, "?")

    def _success_symbol(self) -> str:
        """Return the success symbol for the current terminal encoding."""
        return "\u2713" if self.supports_unicode else "v"

    def _arrow(self) -> str:
        """Return the suggestion arrow for the current terminal encoding."""
        return "\u2192" if self.supports_unicode else "->"

    def _separator(self) -> str:
        """Return the section separator for the current terminal encoding."""
        return ("\u2500" * 60) if self.supports_unicode else ("-" * 60)

    def report(self, results: List[ValidationResult]) -> int:
        """
        Report all validation results and return exit code.

        Args:
            results: List of validation results

        Returns:
            Exit code: 0 if no errors, 1 if any errors
        """
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        files_with_issues = sum(1 for r in results if r.issues)
        files_valid = sum(1 for r in results if r.is_valid)

        # Report each file
        for result in results:
            self._report_result(result)

        # Print summary
        self._report_summary(
            total_files=len(results),
            files_valid=files_valid,
            total_errors=total_errors,
            total_warnings=total_warnings
        )

        return 1 if total_errors > 0 else 0

    def _report_result(self, result: ValidationResult) -> None:
        """Report a single validation result."""
        # Skip files with no issues unless verbose
        if not result.issues and not self.verbose:
            return

        # Header with status
        if result.is_valid:
            status = self._color(ColorCode.GREEN, self._success_symbol())
        else:
            status = self._color(ColorCode.RED, self._symbol(Severity.ERROR))

        # Print file header
        self._emit(f"\n{status} {result.file_path} ({result.component_type})")

        # Print issues
        for issue in result.issues:
            self._report_issue(issue)

    def _report_issue(self, issue: ValidationIssue) -> None:
        """Report a single validation issue."""
        # Skip warnings in quiet mode
        if self.quiet and issue.severity == Severity.WARNING:
            return

        color = self.SEVERITY_COLORS.get(issue.severity, "")
        symbol = self._symbol(issue.severity)

        # Build location string
        location = f"line {issue.line_number}" if issue.line_number else "frontmatter"
        field_info = f"[{issue.field_name}]" if issue.field_name else ""

        # Format the issue line
        colored_symbol = self._color(color, symbol)
        self._emit(f"  {colored_symbol} {location}{field_info}: {issue.message}")

        # Print suggestion if available
        if issue.suggestion:
            arrow = self._color(ColorCode.BLUE, self._arrow())
            self._emit(f"    {arrow} {issue.suggestion}")

    def _report_summary(
        self,
        total_files: int,
        files_valid: int,
        total_errors: int,
        total_warnings: int
    ) -> None:
        """Print final summary."""
        self._emit(f"\n{self._separator()}")

        if total_errors == 0 and total_warnings == 0:
            message = f"{self._success_symbol()} All {total_files} file(s) validated successfully"
            self._emit(self._color(ColorCode.GREEN, message))
        elif total_errors == 0:
            message = f"{self._success_symbol()} {files_valid}/{total_files} file(s) valid with {total_warnings} warning(s)"
            self._emit(self._color(ColorCode.YELLOW, message))
        else:
            parts = []
            if total_errors:
                parts.append(f"{total_errors} error(s)")
            if total_warnings:
                parts.append(f"{total_warnings} warning(s)")
            message = f"{self._symbol(Severity.ERROR)} Validation failed: {', '.join(parts)}"
            self._emit(self._color(ColorCode.RED, message))


class JsonReporter:
    """Formats validation results as JSON for programmatic consumption."""

    def report(self, results: List[ValidationResult]) -> int:
        """
        Report all validation results as JSON and return exit code.

        Args:
            results: List of validation results

        Returns:
            Exit code: 0 if no errors, 1 if any errors
        """
        import json

        output = {
            "summary": {
                "total_files": len(results),
                "files_valid": sum(1 for r in results if r.is_valid),
                "total_errors": sum(len(r.errors) for r in results),
                "total_warnings": sum(len(r.warnings) for r in results),
            },
            "results": [
                {
                    "file": str(r.file_path),
                    "component_type": r.component_type,
                    "is_valid": r.is_valid,
                    "issues": [
                        {
                            "severity": i.severity.value,
                            "message": i.message,
                            "line_number": i.line_number,
                            "field": i.field_name,
                            "suggestion": i.suggestion,
                        }
                        for i in r.issues
                    ]
                }
                for r in results
            ]
        }

        print(json.dumps(output, indent=2))

        return 1 if output["summary"]["total_errors"] > 0 else 0
