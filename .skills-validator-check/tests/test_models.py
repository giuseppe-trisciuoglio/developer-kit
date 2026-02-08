"""Tests for validation models."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.models import Severity, ValidationIssue, ValidationResult


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_issue_creation(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            severity=Severity.ERROR,
            file_path=Path("test.md"),
            message="Test error"
        )
        assert issue.severity == Severity.ERROR
        assert issue.file_path == Path("test.md")
        assert issue.message == "Test error"
        assert issue.line_number is None
        assert issue.field_name is None
        assert issue.suggestion is None

    def test_issue_with_all_fields(self):
        """Test creating issue with all fields."""
        issue = ValidationIssue(
            severity=Severity.WARNING,
            file_path=Path("skills/test/SKILL.md"),
            message="Description too long",
            line_number=5,
            field_name="description",
            suggestion="Shorten to 1024 characters"
        )
        assert issue.line_number == 5
        assert issue.field_name == "description"
        assert issue.suggestion == "Shorten to 1024 characters"

    def test_issue_str_with_line_number(self):
        """Test string representation with line number."""
        issue = ValidationIssue(
            severity=Severity.ERROR,
            file_path=Path("test.md"),
            message="Test error",
            line_number=10,
            field_name="name"
        )
        assert "line 10" in str(issue)
        assert "[name]" in str(issue)

    def test_issue_str_without_line_number(self):
        """Test string representation without line number."""
        issue = ValidationIssue(
            severity=Severity.ERROR,
            file_path=Path("test.md"),
            message="Test error"
        )
        assert "frontmatter" in str(issue)

    def test_issue_is_frozen(self):
        """Test that issue is immutable."""
        issue = ValidationIssue(
            severity=Severity.ERROR,
            file_path=Path("test.md"),
            message="Test"
        )
        with pytest.raises(AttributeError):
            issue.message = "Changed"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_result_creation(self):
        """Test creating an empty result."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        assert result.file_path == Path("test.md")
        assert result.component_type == "skill"
        assert result.issues == []
        assert result.is_valid is True

    def test_is_valid_with_no_errors(self):
        """Test is_valid returns True when no errors."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_warning("Warning message")
        assert result.is_valid is True

    def test_is_valid_with_errors(self):
        """Test is_valid returns False when errors exist."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_error("Error message")
        assert result.is_valid is False

    def test_has_errors(self):
        """Test has_errors property."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        assert result.has_errors is False
        result.add_error("Error")
        assert result.has_errors is True

    def test_has_warnings(self):
        """Test has_warnings property."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        assert result.has_warnings is False
        result.add_warning("Warning")
        assert result.has_warnings is True

    def test_errors_property(self):
        """Test errors property filters correctly."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.add_error("Error 2")

        errors = result.errors
        assert len(errors) == 2
        assert all(e.severity == Severity.ERROR for e in errors)

    def test_warnings_property(self):
        """Test warnings property filters correctly."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")

        warnings = result.warnings
        assert len(warnings) == 2
        assert all(w.severity == Severity.WARNING for w in warnings)

    def test_add_issue(self):
        """Test adding a generic issue."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        issue = ValidationIssue(
            severity=Severity.INFO,
            file_path=Path("test.md"),
            message="Info message"
        )
        result.add_issue(issue)
        assert len(result.issues) == 1

    def test_add_error_convenience(self):
        """Test add_error convenience method."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_error(
            message="Error message",
            line_number=5,
            field_name="name",
            suggestion="Fix it"
        )
        assert len(result.issues) == 1
        assert result.issues[0].severity == Severity.ERROR
        assert result.issues[0].line_number == 5
        assert result.issues[0].field_name == "name"

    def test_add_warning_convenience(self):
        """Test add_warning convenience method."""
        result = ValidationResult(
            file_path=Path("test.md"),
            component_type="skill"
        )
        result.add_warning(
            message="Warning message",
            suggestion="Consider fixing"
        )
        assert len(result.issues) == 1
        assert result.issues[0].severity == Severity.WARNING
