# Project Management Plugin Commands Guide

This guide documents all commands available in the Developer Kit Project Management Plugin.

---

## Overview

The Project Management Plugin provides specialized commands for project documentation and workflow management.

### Available Commands

- **Documentation**: 1 command for meeting documentation

---

## Commands

### `/developer-kit-project-management:devkit.write-a-minute-of-a-meeting`

**Purpose**: Generate professional meeting minutes (MOM) from meeting notes or discussions.

**Usage:**
```bash
/developer-kit-project-management:devkit.write-a-minute-of-a-meeting
```

**Common use cases:**
- Documenting project meetings
- Creating meeting summaries
- Tracking action items
- Recording decisions made

**Examples:**
```bash
# Generate meeting minutes
/developer-kit-project-management:devkit.write-a-minute-of-a-meeting

# The command will prompt for:
# - Meeting attendees
# - Agenda items
# - Discussion points
# - Decisions made
# - Action items with owners
```

---

## Command Usage Guidelines

### How to Invoke Commands

Commands are invoked using the slash syntax in Claude Code:

```bash
/developer-kit-project-management:{command-name} [arguments]
```

### Best Practices

1. **Prepare meeting notes**: Have your meeting notes ready
2. **Identify attendees**: List who attended the meeting
3. **Track action items**: Ensure action items have owners and deadlines
4. **Review output**: Verify accuracy before sharing

---

## See Also

- [Core Command Guide](../developer-kit-core/docs/guide-commands.md) - All commands across plugins
- [LRA Workflow Guide](../developer-kit-core/docs/guide-lra-workflow.md) - Long-running agent workflow
