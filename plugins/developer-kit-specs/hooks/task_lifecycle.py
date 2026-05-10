#!/usr/bin/env python3
import sys
import os
import re
import yaml
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# --- Constants & Schema ---

class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    REVIEWED = "reviewed"
    COMPLETED = "completed"
    OPTIONAL = "optional"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    SUPERSEDED = "superseded"

FIELD_SCHEMA = {
    "id": {"type": str, "required": True},
    "title": {"type": str, "required": True},
    "spec": {"type": str, "required": True},
    "status": {"type": str, "required": True, "values": [
        "pending", "in_progress", "implemented", "reviewed", "completed", "optional", "blocked", "escalated", "superseded"
    ]},
    "imp-requirements": {"type": list, "required": False},
    "ac-mapping": {"type": list, "required": False},
    "cross-boundary": {"type": bool, "required": False},
    "external-dep-risk": {"type": bool, "required": False},
    "started_date": {"type": (str, date), "required": False},
    "implemented_date": {"type": (str, date), "required": False},
    "reviewed_date": {"type": (str, date), "required": False},
    "completed_date": {"type": (str, date), "required": False},
    "cleanup_date": {"type": (str, date), "required": False},
}

# --- Core Functions ---

def read_task_file(path: Path) -> Tuple[Optional[Dict], Optional[str], str]:
    """Reads a task file and returns (frontmatter, error, body)."""
    if not path.exists():
        return None, f"File not found: {path}", ""
    
    try:
        content = path.read_text()
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, "Invalid frontmatter format", content
        
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter, None, parts[2]
    except Exception as e:
        return None, str(e), ""

def write_task_file(path: Path, frontmatter: Dict, body: str):
    """Writes a task file with updated frontmatter."""
    content = "---\n" + yaml.dump(frontmatter, sort_keys=False) + "---\n" + body
    path.write_text(content)

def _all_dod_complete(body: str) -> bool:
    """Check whether all Definition of Done checkboxes are checked."""
    # Extract the Definition of Done section
    dod_match = re.search(r'## Definition of Done(.*?)(?=\n## |\Z)', body, re.DOTALL)
    if not dod_match:
        return False
    dod_section = dod_match.group(1)
    unchecked = len(re.findall(r'- \[ \]', dod_section))
    return unchecked == 0


def detect_status_from_body(body: str, old_status: Optional[str] = None) -> str:
    """Heuristic to detect status from checkboxes and DoD in the body.

    Progression when all checkboxes are checked:
        pending/in_progress -> implemented
        implemented -> reviewed  (when DoD is also complete)
        reviewed -> completed   (when cleanup_date is set, i.e. cleanup ran)
    """
    # Count checkboxes
    total = len(re.findall(r'- \[ \]', body)) + len(re.findall(r'- \[x\]', body))
    checked = len(re.findall(r'- \[x\]', body))
    all_checked = (total > 0 and checked == total)

    if not all_checked:
        if checked == 0:
            return TaskStatus.PENDING
        # An implemented task with incomplete DoD should not be demoted
        if old_status == TaskStatus.IMPLEMENTED:
            return TaskStatus.IMPLEMENTED
        return TaskStatus.IN_PROGRESS

    # All checkboxes checked — determine promotion level
    if old_status == TaskStatus.REVIEWED:
        # reviewed -> completed only if cleanup already ran
        return TaskStatus.REVIEWED
    if old_status == TaskStatus.IMPLEMENTED and _all_dod_complete(body):
        return TaskStatus.REVIEWED
    return TaskStatus.IMPLEMENTED

def update_status(filepath: str):
    """Auto-updates the task status based on checkboxes and sets dates."""
    path = Path(filepath)
    frontmatter, error, body = read_task_file(path)
    if error:
        print(f"Error reading task: {error}")
        return

    old_status = frontmatter.get("status")
    new_status = detect_status_from_body(body, old_status=old_status)

    # Preserve terminal states — completed tasks must never be demoted
    if old_status == TaskStatus.COMPLETED:
        new_status = old_status
    # Preserve special states that are managed externally
    elif old_status in [TaskStatus.BLOCKED, TaskStatus.OPTIONAL, TaskStatus.ESCALATED, TaskStatus.SUPERSEDED]:
        new_status = old_status

    if old_status != new_status:
        frontmatter["status"] = new_status
        print(f"Status updated: {old_status} -> {new_status}")

        # Auto-set dates
        today = datetime.now().strftime("%Y-%m-%d")
        if new_status == TaskStatus.IN_PROGRESS and not frontmatter.get("started_date"):
            frontmatter["started_date"] = today
        elif new_status == TaskStatus.IMPLEMENTED and not frontmatter.get("implemented_date"):
            frontmatter["implemented_date"] = today
            if not frontmatter.get("started_date"):
                frontmatter["started_date"] = today
        elif new_status == TaskStatus.REVIEWED and not frontmatter.get("reviewed_date"):
            frontmatter["reviewed_date"] = today
        elif new_status == TaskStatus.COMPLETED and not frontmatter.get("completed_date"):
            frontmatter["completed_date"] = today

        write_task_file(path, frontmatter, body)

def validate_task(filepath: str) -> bool:
    """Validates task frontmatter and structure."""
    path = Path(filepath)
    frontmatter, error, body = read_task_file(path)
    
    errors = []
    if error:
        errors.append(f"Frontmatter error: {error}")
    else:
        for field, rules in FIELD_SCHEMA.items():
            if rules.get("required") and field not in frontmatter:
                errors.append(f"Missing required field: {field}")
            elif field in frontmatter:
                val = frontmatter[field]
                expected = rules["type"]
                if isinstance(expected, tuple):
                    if not isinstance(val, expected) and val is not None:
                        errors.append(f"Invalid type for {field}: expected one of {', '.join(t.__name__ for t in expected)}")
                elif not isinstance(val, expected) and val is not None:
                    errors.append(f"Invalid type for {field}: expected {expected.__name__}")
                if "values" in rules and val not in rules["values"]:
                    errors.append(f"Invalid value for {field}: {val}")

    # Check for required sections in body
    if "## Acceptance Criteria" not in body:
        errors.append("Missing section: ## Acceptance Criteria")
    if "## Definition of Done" not in body:
        errors.append("Missing section: ## Definition of Done")

    if errors:
        print(f"Validation failed for {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False
    
    print(f"Validation passed for {filepath}")
    return True

# --- CLI Entry Point ---

def main():
    if len(sys.argv) < 3:
        print("Usage: task_lifecycle.py [auto-status|validate] [file]")
        sys.exit(1)

    action = sys.argv[1]
    filepath = sys.argv[2]

    if action == "auto-status":
        update_status(filepath)
    elif action == "validate":
        if not validate_task(filepath):
            sys.exit(1)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
