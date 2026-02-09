"""
Data models for validation results.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Severity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a single validation issue found in a file."""
    severity: Severity
    file_path: Path
    message: str
    line_number: Optional[int] = None
    field_name: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        location = f"line {self.line_number}" if self.line_number else "frontmatter"
        field_info = f" [{self.field_name}]" if self.field_name else ""
        return f"{location}{field_info}: {self.message}"


@dataclass
class ValidationResult:
    """Aggregates validation results for a single file."""
    file_path: Path
    component_type: str
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Returns True if no errors were found."""
        return not self.has_errors

    @property
    def has_errors(self) -> bool:
        """Returns True if any error-level issues exist."""
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Returns True if any warning-level issues exist."""
        return any(i.severity == Severity.WARNING for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        """Returns only error-level issues."""
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Returns only warning-level issues."""
        return [i for i in self.issues if i.severity == Severity.WARNING]

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add an issue to the result."""
        self.issues.append(issue)

    def add_error(
        self,
        message: str,
        line_number: Optional[int] = None,
        field_name: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> None:
        """Convenience method to add an error."""
        self.add_issue(ValidationIssue(
            severity=Severity.ERROR,
            file_path=self.file_path,
            message=message,
            line_number=line_number,
            field_name=field_name,
            suggestion=suggestion
        ))

    def add_warning(
        self,
        message: str,
        line_number: Optional[int] = None,
        field_name: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> None:
        """Convenience method to add a warning."""
        self.add_issue(ValidationIssue(
            severity=Severity.WARNING,
            file_path=self.file_path,
            message=message,
            line_number=line_number,
            field_name=field_name,
            suggestion=suggestion
        ))
