#!/usr/bin/env python3
import sys
import os
import re
import yaml
import json
from datetime import datetime
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

FIELD_SCHEMA = {
    "id": {"type": str, "required": True},
    "title": {"type": str, "required": True},
    "spec": {"type": str, "required": True},
    "status": {"type": str, "required": True, "values": [
        "pending", "in_progress", "implemented", "reviewed", "completed", "optional", "blocked", "escalated"
    ]},
    "imp-requirements": {"type": list, "required": False},
    "ac-mapping": {"type": list, "required": False},
    "cross-boundary": {"type": bool, "required": False},
    "external-dep-risk": {"type": bool, "required": False},
    "started_date": {"type": str, "required": False},
    "implemented_date": {"type": str, "required": False},
    "reviewed_date": {"type": str, "required": False},
    "completed_date": {"type": str, "required": False},
    "cleanup_date": {"type": str, "required": False},
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

def detect_status_from_body(body: str) -> str:
    """Heuristic to detect status from checkboxes in the body."""
    # Count checkboxes
    total = len(re.findall(r'- \[ \]', body)) + len(re.findall(r'- \[x\]', body))
    checked = len(re.findall(r'- \[x\]', body))
    
    if total == 0:
        return TaskStatus.PENDING
    if checked == 0:
        return TaskStatus.PENDING
    if checked == total:
        return TaskStatus.IMPLEMENTED
    return TaskStatus.IN_PROGRESS

def update_status(filepath: str):
    """Auto-updates the task status based on checkboxes and sets dates."""
    path = Path(filepath)
    frontmatter, error, body = read_task_file(path)
    if error:
        print(f"Error reading task: {error}")
        return

    old_status = frontmatter.get("status")
    new_status = detect_status_from_body(body)
    
    # Don't downgrade from terminal/special states unless explicitly changed
    if old_status in [TaskStatus.REVIEWED, TaskStatus.COMPLETED, TaskStatus.OPTIONAL, TaskStatus.BLOCKED, TaskStatus.ESCALATED]:
        # If all checked, it might be implemented but we keep reviewed/completed
        if new_status == TaskStatus.IMPLEMENTED:
            new_status = old_status
        else:
            # If some unchecked, it moved back to in_progress
            new_status = TaskStatus.IN_PROGRESS

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
                if not isinstance(val, rules["type"]) and val is not None:
                    errors.append(f"Invalid type for {field}: expected {rules['type'].__name__}")
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
