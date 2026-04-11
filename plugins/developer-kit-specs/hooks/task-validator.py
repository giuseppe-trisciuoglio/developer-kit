#!/usr/bin/env python3
"""
Task Validator Hook

Validates task frontmatter structure and reports issues.
Runs before task modifications to catch problems early.

Usage:
    python3 task-validator.py <task-file-path>
    
Returns:
    0 if valid or minor issues (warnings only)
    1 if critical validation errors found
"""

import sys
import os
import re
from pathlib import Path

# Ensure hooks directory is in path for imports
_HOOKS_DIR = Path(__file__).parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

try:
    from task_frontmatter import read_task_file, validate_task_file
    from task_schema import FIELD_SCHEMA, TaskStatus
except ImportError as e:
    print(f"⚠️  Error importing task modules: {e}", file=sys.stderr)
    sys.exit(0)


def get_target_file() -> str:
    """Get the target file path from arguments or environment."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get('CLAUDE_CHANGED_FILE', '')


def is_task_file(filepath: str) -> bool:
    """Check if file is a task file."""
    return bool(re.match(r'TASK-\d+\.md$', os.path.basename(filepath)))


def validate_task(filepath: str) -> tuple[bool, list[str]]:
    """
    Validate a task file and return results.
    
    Returns:
        Tuple of (is_valid, list_of_messages)
    """
    path = Path(filepath)
    
    if not path.exists():
        return False, [f"File not found: {filepath}"]
    
    # Use the existing validation function
    is_valid, errors = validate_task_file(path)
    
    # Additional custom validations
    messages = list(errors) if errors else []
    
    # Read file for deeper analysis
    frontmatter, error, body = read_task_file(path)
    if error or not frontmatter:
        messages.append(f"Cannot parse frontmatter: {error}")
        return False, messages
    
    # Check for required sections
    required_sections = [
        ('Acceptance Criteria', r'## Acceptance Criteria'),
        ('Definition of Done', r'## Definition of Done'),
    ]
    
    for section_name, pattern in required_sections:
        if not re.search(pattern, body, re.IGNORECASE):
            messages.append(f"Missing recommended section: {section_name}")
    
    # Check for orphan checkboxes (not in a list)
    orphan_checkboxes = re.findall(r'^(?!\s*-)\s*\[([ x])\]', body, re.MULTILINE)
    if orphan_checkboxes:
        messages.append(f"Found {len(orphan_checkboxes)} checkbox(es) not in a list (use '- [ ]' format)")
    
    # Check date consistency
    date_fields = ['started_date', 'implemented_date', 'reviewed_date', 'completed_date']
    dates = {f: getattr(frontmatter, f) for f in date_fields if getattr(frontmatter, f)}
    
    if dates:
        date_values = list(dates.values())
        # Check chronological order
        sorted_dates = sorted(date_values)
        if date_values != sorted_dates:
            messages.append(f"Date inconsistency: dates should be in chronological order")
    
    # Status-specific checks
    status = frontmatter.status
    
    if status in ['in_progress', 'implemented', 'reviewed', 'completed']:
        if not frontmatter.started_date:
            messages.append(f"Status '{status}' should have started_date set")
    
    if status in ['implemented', 'reviewed', 'completed']:
        if not frontmatter.implemented_date:
            messages.append(f"Status '{status}' should have implemented_date set")
    
    if status in ['reviewed', 'completed']:
        if not frontmatter.reviewed_date:
            messages.append(f"Status '{status}' should have reviewed_date set")
    
    if status == 'completed':
        if not frontmatter.completed_date:
            messages.append(f"Status 'completed' should have completed_date set")
        if not frontmatter.cleanup_date:
            messages.append(f"Status 'completed' should have cleanup_date set")
    
    return len(messages) == 0, messages


def main() -> int:
    """Main entry point."""
    filepath = get_target_file()
    
    if not filepath:
        return 0
    
    if not is_task_file(filepath):
        return 0
    
    try:
        is_valid, messages = validate_task(filepath)
        
        if messages:
            # Separate warnings from errors
            errors = [m for m in messages if m.startswith(('Required', 'Invalid', 'Cannot'))]
            warnings = [m for m in messages if m not in errors]
            
            filename = Path(filepath).name
            
            if errors:
                print(f"❌ {filename} - Validation errors:", file=sys.stderr)
                for error in errors:
                    print(f"   - {error}", file=sys.stderr)
            
            if warnings:
                print(f"⚠️  {filename} - Recommendations:", file=sys.stderr)
                for warning in warnings[:5]:  # Limit warnings
                    print(f"   - {warning}", file=sys.stderr)
                if len(warnings) > 5:
                    print(f"   ... and {len(warnings) - 5} more", file=sys.stderr)
        
        # Return 0 to not block Claude, but log issues
        return 0
        
    except Exception as e:
        print(f"⚠️  Validator error: {e}", file=sys.stderr)
        return 0


if __name__ == '__main__':
    sys.exit(main())
