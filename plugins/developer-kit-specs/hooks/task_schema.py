"""
Task Frontmatter Schema Definition

Defines the standard schema for task frontmatter with validation rules,
default values, and field ordering.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class TaskStatus(str, Enum):
    """Standard task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    REVIEWED = "reviewed"
    COMPLETED = "completed"
    SUPERSEDED = "superseded"
    OPTIONAL = "optional"
    BLOCKED = "blocked"


@dataclass
class ProvidedItem:
    """Represents a 'provides' item in task frontmatter."""
    file: str
    symbols: List[str] = field(default_factory=list)
    type: str = "component"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "symbols": self.symbols,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvidedItem":
        return cls(
            file=data.get("file", ""),
            symbols=data.get("symbols", []),
            type=data.get("type", "component")
        )


@dataclass
class ExpectedItem:
    """Represents an 'expects' item in task frontmatter."""
    file: str
    symbols: List[str] = field(default_factory=list)
    type: str = "component"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "symbols": self.symbols,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpectedItem":
        return cls(
            file=data.get("file", ""),
            symbols=data.get("symbols", []),
            type=data.get("type", "component")
        )


# Schema field definitions with their properties
FIELD_SCHEMA = {
    # Required fields
    "id": {"required": True, "type": str, "pattern": r"^TASK-\d+$"},
    "title": {"required": True, "type": str, "min_length": 1},
    "spec": {"required": True, "type": str, "min_length": 1},
    "lang": {"required": True, "type": str, "default": "general"},
    
    # Status and lifecycle dates
    "status": {
        "required": False,
        "type": str,
        "allowed_values": [s.value for s in TaskStatus],
        "default": "pending"
    },
    "started_date": {"required": False, "type": str, "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    "implemented_date": {"required": False, "type": str, "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    "reviewed_date": {"required": False, "type": str, "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    "completed_date": {"required": False, "type": str, "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    "cleanup_date": {"required": False, "type": str, "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    
    # Relationships
    "dependencies": {"required": False, "type": list, "default": []},
    "provides": {"required": False, "type": list, "default": []},
    "expects": {"required": False, "type": list, "default": []},
    
    # Optional fields for complex tasks
    "complexity": {"required": False, "type": int},
    "optional": {"required": False, "type": bool, "default": False},
    "parent_task": {"required": False, "type": str, "pattern": r"^TASK-\d+$"},
    "supersedes": {"required": False, "type": list, "default": []},
}

# Standard field order for YAML serialization
FIELD_ORDER = [
    "id",
    "title",
    "spec",
    "lang",
    "status",
    "started_date",
    "implemented_date",
    "reviewed_date",
    "completed_date",
    "cleanup_date",
    "dependencies",
    "provides",
    "expects",
    "complexity",
    "optional",
    "parent_task",
    "supersedes",
]

# Status transitions and dates that SHOULD be set (not strictly required)
# Each status indicates which dates are typically expected but we allow flexibility
STATUS_WORKFLOW = {
    TaskStatus.PENDING: {"next": [TaskStatus.IN_PROGRESS, TaskStatus.IMPLEMENTED], "dates": []},
    TaskStatus.IN_PROGRESS: {
        "next": [TaskStatus.IMPLEMENTED, TaskStatus.BLOCKED],
        "suggested_dates": ["started_date"]
    },
    TaskStatus.IMPLEMENTED: {
        "next": [TaskStatus.REVIEWED],
        "suggested_dates": ["started_date", "implemented_date"]
    },
    TaskStatus.REVIEWED: {
        "next": [TaskStatus.COMPLETED],
        "suggested_dates": ["started_date", "implemented_date", "reviewed_date"]
    },
    TaskStatus.COMPLETED: {
        "next": [TaskStatus.SUPERSEDED],
        "suggested_dates": ["implemented_date", "reviewed_date", "completed_date", "cleanup_date"]
    },
    TaskStatus.SUPERSEDED: {"next": [], "suggested_dates": []},
    TaskStatus.OPTIONAL: {"next": [], "suggested_dates": []},
    TaskStatus.BLOCKED: {
        "next": [TaskStatus.IN_PROGRESS],
        "suggested_dates": ["started_date"]
    },
}


def get_expected_dates_for_status(status: TaskStatus) -> List[str]:
    """Get the list of dates suggested for a given status."""
    return STATUS_WORKFLOW.get(status, {}).get("suggested_dates", [])


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> tuple[bool, Optional[str]]:
    """
    Validate if a status transition is allowed.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if current == new:
        return True, None
    
    allowed_next = STATUS_WORKFLOW.get(current, {}).get("next", [])
    if new in allowed_next:
        return True, None
    
    allowed_names = [s.value for s in allowed_next]
    return False, f"Cannot transition from '{current.value}' to '{new.value}'. " \
                  f"Allowed transitions: {allowed_names}"
