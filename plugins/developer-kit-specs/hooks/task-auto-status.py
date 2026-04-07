#!/usr/bin/env python3
"""
Task Auto-Status Hook

Automatically updates task frontmatter status when TASK-*.md files are modified.
Analyzes content to infer appropriate status based on checkbox completion.

Usage:
    python3 task-auto-status.py <task-file-path>
    
Environment:
    CLAUDE_CHANGED_FILE - Alternative way to pass the file path
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Ensure hooks directory is in path for imports
_HOOKS_DIR = Path(__file__).parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

try:
    from task_frontmatter import read_task_file, write_task_file, TaskFrontmatter
    from task_schema import TaskStatus, validate_status_transition
except ImportError as e:
    print(f"⚠️  Error importing task modules: {e}", file=sys.stderr)
    sys.exit(0)  # Silent fail - don't block Claude


def get_changed_file() -> str:
    """Get the changed file path from arguments or environment."""
    # Command line argument
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Environment variable
    return os.environ.get('CLAUDE_CHANGED_FILE', '')


def is_task_file(filepath: str) -> bool:
    """Check if file is a task file (TASK-*.md)."""
    return bool(re.match(r'TASK-\d+\.md$', os.path.basename(filepath)))


def analyze_content(frontmatter: TaskFrontmatter, body: str) -> tuple[str, str]:
    """
    Analyze task content to determine appropriate status.
    
    Returns:
        Tuple of (new_status, reason)
    """
    current_status = frontmatter.status
    
    # Count checkbox states in different sections
    sections = parse_sections(body)
    
    # Acceptance Criteria section
    ac_section = sections.get('acceptance criteria', '')
    ac_checkboxes = re.findall(r'- \[([ x])\]', ac_section)
    ac_checked = sum(1 for cb in ac_checkboxes if cb == 'x')
    ac_total = len(ac_checkboxes)
    ac_complete = ac_total > 0 and ac_checked == ac_total
    
    # Definition of Done section
    dod_section = sections.get('definition of done', '') + sections.get('dod', '')
    dod_checkboxes = re.findall(r'- \[([ x])\]', dod_section)
    dod_checked = sum(1 for cb in dod_checkboxes if cb == 'x')
    dod_total = len(dod_checkboxes)
    dod_complete = dod_total > 0 and dod_checked == dod_total
    
    # Implementation section presence
    has_implementation = bool(re.search(
        r'## (Implementation Details|Files to Create|Technical Context)',
        body, re.IGNORECASE
    ))
    
    # Cleanup Summary section (marks completion)
    has_cleanup_summary = '## Cleanup Summary' in body or '## Cleanup' in body
    
    # Review section
    has_review = '## Review' in body or '## Code Review' in body
    review_section = sections.get('review', '') + sections.get('code review', '')
    review_checkboxes = re.findall(r'- \[([ x])\]', review_section)
    review_complete = review_checkboxes and all(cb == 'x' for cb in review_checkboxes)
    
    # State machine transitions
    if current_status == 'pending':
        if has_implementation or ac_checked > 0:
            return 'in_progress', f'Work started ({ac_checked}/{ac_total} AC items)'
    
    if current_status == 'in_progress':
        if ac_complete and ac_total > 0:
            return 'implemented', 'All acceptance criteria met'
    
    if current_status == 'implemented':
        if dod_complete and dod_total > 0:
            return 'reviewed', 'Definition of Done complete'
        if review_complete:
            return 'reviewed', 'Review checklist complete'
    
    if current_status == 'reviewed':
        if has_cleanup_summary:
            return 'completed', 'Cleanup summary present'
    
    if current_status == 'blocked':
        # Auto-unblock if progress is detected
        if ac_checked > 0:
            return 'in_progress', 'Progress detected, unblocking'
    
    return '', ''  # No change needed


def parse_sections(body: str) -> dict[str, str]:
    """Parse markdown body into sections."""
    sections = {}
    current_section = 'header'
    current_content = []
    
    for line in body.split('\n'):
        # Check for section header
        section_match = re.match(r'^##+\s+(.+)$', line, re.IGNORECASE)
        if section_match:
            # Save previous section
            if current_content:
                sections[current_section.lower()] = '\n'.join(current_content)
            # Start new section
            current_section = section_match.group(1).strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section.lower()] = '\n'.join(current_content)
    
    return sections


def update_task_status(filepath: str) -> bool:
    """
    Update task status based on content analysis.
    
    Returns:
        True if status was updated, False otherwise
    """
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️  File not found: {filepath}", file=sys.stderr)
        return False
    
    # Read task
    frontmatter, error, body = read_task_file(path)
    if error or not frontmatter:
        print(f"⚠️  Error reading {path.name}: {error}", file=sys.stderr)
        return False
    
    # Analyze content for new status
    new_status, reason = analyze_content(frontmatter, body)
    
    if not new_status or new_status == frontmatter.status:
        return False  # No update needed
    
    # Validate transition
    try:
        current_enum = TaskStatus(frontmatter.status)
        new_enum = TaskStatus(new_status)
    except ValueError:
        print(f"⚠️  Invalid status value in {path.name}", file=sys.stderr)
        return False
    
    is_valid, error = validate_status_transition(current_enum, new_enum)
    if not is_valid:
        print(f"⚠️  Cannot update {path.name}: {error}", file=sys.stderr)
        return False
    
    # Update status
    success, error = frontmatter.set_status(new_status)
    if not success:
        print(f"⚠️  Failed to update {path.name}: {error}", file=sys.stderr)
        return False
    
    # Write updated file
    error = write_task_file(path, frontmatter, body)
    if error:
        print(f"⚠️  Error writing {path.name}: {error}", file=sys.stderr)
        return False
    
    print(f"✅ Auto-updated {path.name}: {frontmatter.status} → {new_status} ({reason})")
    return True


def main() -> int:
    """Main entry point."""
    filepath = get_changed_file()
    
    if not filepath:
        print("⚠️  No file path provided", file=sys.stderr)
        return 0  # Silent fail
    
    if not is_task_file(filepath):
        return 0  # Not a task file, ignore silently
    
    try:
        updated = update_task_status(filepath)
        return 0 if updated else 0  # Always return 0 to not block Claude
    except Exception as e:
        print(f"⚠️  Unexpected error in task-auto-status: {e}", file=sys.stderr)
        return 0  # Silent fail


if __name__ == '__main__':
    sys.exit(main())
