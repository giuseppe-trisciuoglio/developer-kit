"""
Task Frontmatter Parser and Validator

Provides utilities for reading, validating, modifying, and writing
task frontmatter with consistent formatting and schema compliance.
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict

from task_schema import (
    TaskStatus, FIELD_SCHEMA, FIELD_ORDER, STATUS_WORKFLOW,
    validate_status_transition, get_expected_dates_for_status,
    ProvidedItem, ExpectedItem
)


class FrontmatterError(Exception):
    """Exception for frontmatter parsing/validation errors."""
    pass


@dataclass
class TaskFrontmatter:
    """Represents a task frontmatter with all fields."""
    # Required fields
    id: str
    title: str
    spec: str
    lang: str = "general"
    
    # Status and lifecycle
    status: str = "pending"
    started_date: Optional[str] = None
    implemented_date: Optional[str] = None
    reviewed_date: Optional[str] = None
    completed_date: Optional[str] = None
    cleanup_date: Optional[str] = None
    
    # Relationships
    dependencies: List[str] = field(default_factory=list)
    provides: List[Dict[str, Any]] = field(default_factory=list)
    expects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Optional fields
    complexity: Optional[int] = None
    optional: bool = False
    parent_task: Optional[str] = None
    supersedes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Normalize status value after initialization."""
        self.status = self._normalize_status(self.status)
    
    @staticmethod
    def _normalize_status(status: str) -> str:
        """Normalize status to standard values."""
        status_map = {
            "done": "completed",
            "in-progress": "in_progress",
            "in progress": "in_progress",
        }
        normalized = status.lower().strip()
        return status_map.get(normalized, normalized)
    
    def to_dict(self, include_null: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, optionally including null values."""
        result = {}
        for key in FIELD_ORDER:
            if hasattr(self, key):
                value = getattr(self, key)
                if value is not None or include_null:
                    if key == "status":
                        result[key] = value
                    elif isinstance(value, list) and not value:
                        # Skip empty lists unless required
                        if FIELD_SCHEMA.get(key, {}).get("required", False):
                            result[key] = value
                        elif include_null:
                            result[key] = value
                    else:
                        result[key] = value
        return result
    
    def set_status(self, new_status: str, date: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Set task status with validation.
        
        Args:
            new_status: The new status value
            date: Optional date string (defaults to today)
            
        Returns:
            Tuple of (success, error_message)
        """
        normalized_new = self._normalize_status(new_status)
        
        try:
            current = TaskStatus(self.status)
            new = TaskStatus(normalized_new)
        except ValueError as e:
            return False, f"Invalid status: {e}"
        
        # Validate transition
        is_valid, error = validate_status_transition(current, new)
        if not is_valid:
            return False, error
        
        # Set the date for the new status
        today = date or datetime.now().strftime("%Y-%m-%d")
        
        date_field_map = {
            TaskStatus.IN_PROGRESS: "started_date",
            TaskStatus.IMPLEMENTED: "implemented_date",
            TaskStatus.REVIEWED: "reviewed_date",
            TaskStatus.COMPLETED: "completed_date",
        }
        
        if new in date_field_map:
            setattr(self, date_field_map[new], today)
        
        if new == TaskStatus.COMPLETED:
            self.cleanup_date = today
        
        self.status = normalized_new
        return True, None
    
    def validate(self) -> List[str]:
        """
        Validate the frontmatter against the schema.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields
        for field_name, schema in FIELD_SCHEMA.items():
            if schema.get("required", False):
                value = getattr(self, field_name, None)
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Required field '{field_name}' is missing or empty")
        
        # Validate ID format
        if self.id and not re.match(r"^TASK-\d+$", self.id):
            errors.append(f"Invalid ID format '{self.id}': must be TASK-XXX")
        
        # Validate status
        if self.status not in [s.value for s in TaskStatus]:
            errors.append(f"Invalid status '{self.status}': must be one of {[s.value for s in TaskStatus]}")
        
        # Validate date formats
        date_fields = ["started_date", "implemented_date", "reviewed_date", "completed_date", "cleanup_date"]
        for field_name in date_fields:
            value = getattr(self, field_name, None)
            if value and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
                errors.append(f"Invalid date format in '{field_name}': '{value}' (expected YYYY-MM-DD)")
        
        # Note: We don't strictly require dates for validation
        # Dates are suggested based on status workflow but not enforced
        # This allows flexibility for tasks that skip intermediate steps
        
        # Validate dependency format
        for dep in self.dependencies:
            if not re.match(r"^TASK-\d+$", dep):
                errors.append(f"Invalid dependency format '{dep}': must be TASK-XXX")
        
        return errors


def parse_frontmatter(content: str) -> Tuple[Optional[TaskFrontmatter], Optional[str], str]:
    """
    Parse frontmatter from markdown content.
    
    Args:
        content: Full markdown content with YAML frontmatter
        
    Returns:
        Tuple of (frontmatter_object, error_message, body_content)
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return None, "No YAML frontmatter found", content
    
    yaml_content = match.group(1)
    body_content = match.group(2)
    
    try:
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            return None, "Frontmatter is not a valid YAML dictionary", body_content
        
        frontmatter = TaskFrontmatter(
            id=data.get("id", ""),
            title=data.get("title", ""),
            spec=data.get("spec", ""),
            lang=data.get("lang", "general"),
            status=data.get("status", "pending"),
            started_date=data.get("started_date"),
            implemented_date=data.get("implemented_date"),
            reviewed_date=data.get("reviewed_date"),
            completed_date=data.get("completed_date"),
            cleanup_date=data.get("cleanup_date"),
            dependencies=data.get("dependencies", []),
            provides=data.get("provides", []),
            expects=data.get("expects", []),
            complexity=data.get("complexity"),
            optional=data.get("optional", False),
            parent_task=data.get("parent_task"),
            supersedes=data.get("supersedes", []),
        )
        
        return frontmatter, None, body_content
        
    except yaml.YAMLError as e:
        return None, f"YAML parsing error: {e}", body_content


def serialize_frontmatter(frontmatter: TaskFrontmatter, body_content: str) -> str:
    """
    Serialize frontmatter and body to markdown.
    
    Args:
        frontmatter: The frontmatter object
        body_content: The markdown body content
        
    Returns:
        Complete markdown content with YAML frontmatter
    """
    data = frontmatter.to_dict(include_null=False)
    
    # Custom YAML serialization for consistent formatting
    yaml_lines = []
    for key in FIELD_ORDER:
        if key in data:
            value = data[key]
            if value is None:
                continue
            elif isinstance(value, list):
                if not value:
                    yaml_lines.append(f"{key}: []")
                else:
                    yaml_lines.append(f"{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            yaml_lines.append(f"  - file: \"{item.get('file', '')}\"")
                            if 'symbols' in item and item['symbols']:
                                yaml_lines.append(f"    symbols: {item['symbols']}")
                            if 'type' in item:
                                yaml_lines.append(f"    type: \"{item['type']}\"")
                        else:
                            yaml_lines.append(f"  - \"{item}\"")
            elif isinstance(value, str):
                # Quote strings that might be interpreted as other types
                if value in ['true', 'false', 'yes', 'no', 'null', ''] or ':' in value:
                    yaml_lines.append(f'{key}: "{value}"')
                else:
                    yaml_lines.append(f"{key}: {value}")
            elif isinstance(value, bool):
                yaml_lines.append(f"{key}: {str(value).lower()}")
            else:
                yaml_lines.append(f"{key}: {value}")
    
    yaml_str = "\n".join(yaml_lines)
    
    return f"---\n{yaml_str}\n---\n{body_content}"


def read_task_file(filepath: str | Path) -> Tuple[Optional[TaskFrontmatter], Optional[str], str]:
    """
    Read and parse a task file.
    
    Args:
        filepath: Path to the task markdown file
        
    Returns:
        Tuple of (frontmatter_object, error_message, body_content)
    """
    path = Path(filepath)
    if not path.exists():
        return None, f"File not found: {filepath}", ""
    
    content = path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def write_task_file(filepath: str | Path, frontmatter: TaskFrontmatter, body_content: str) -> Optional[str]:
    """
    Write a task file with frontmatter.
    
    Args:
        filepath: Path to the task markdown file
        frontmatter: The frontmatter object
        body_content: The markdown body content
        
    Returns:
        Error message if failed, None if successful
    """
    try:
        path = Path(filepath)
        content = serialize_frontmatter(frontmatter, body_content)
        path.write_text(content, encoding="utf-8")
        return None
    except Exception as e:
        return f"Failed to write file: {e}"


def update_task_status(
    filepath: str | Path,
    new_status: str,
    date: Optional[str] = None,
    validate: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Update the status of a task file.
    
    Args:
        filepath: Path to the task markdown file
        new_status: New status value
        date: Optional date (defaults to today)
        validate: Whether to validate the transition
        
    Returns:
        Tuple of (success, error_message)
    """
    frontmatter, error, body = read_task_file(filepath)
    if error:
        return False, error
    
    if frontmatter is None:
        return False, "Could not parse frontmatter"
    
    success, error = frontmatter.set_status(new_status, date)
    if not success:
        return False, error
    
    if validate:
        errors = frontmatter.validate()
        if errors:
            return False, f"Validation failed: {'; '.join(errors)}"
    
    error = write_task_file(filepath, frontmatter, body)
    if error:
        return False, error
    
    return True, None


def validate_task_file(filepath: str | Path) -> Tuple[bool, List[str]]:
    """
    Validate a task file against the schema.
    
    Args:
        filepath: Path to the task markdown file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    frontmatter, error, _ = read_task_file(filepath)
    
    if error and frontmatter is None:
        return False, [error]
    
    if frontmatter is None:
        return False, ["Could not parse frontmatter"]
    
    errors = frontmatter.validate()
    return len(errors) == 0, errors


def normalize_task_file(filepath: str | Path) -> Tuple[bool, Optional[str]]:
    """
    Normalize a task file - fix inconsistencies and standardize format.
    
    Args:
        filepath: Path to the task markdown file
        
    Returns:
        Tuple of (success, error_message)
    """
    frontmatter, error, body = read_task_file(filepath)
    
    if error and frontmatter is None:
        return False, error
    
    if frontmatter is None:
        return False, "Could not parse frontmatter"
    
    # Re-serialize to normalize format
    error = write_task_file(filepath, frontmatter, body)
    if error:
        return False, error
    
    return True, None
