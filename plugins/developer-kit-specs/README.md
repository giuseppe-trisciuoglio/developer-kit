# Developer Kit Specs

Specifications-driven development workflow for transforming ideas into functional specifications and executable tasks.

## Overview

This plugin provides a complete workflow for:
- **Brainstorming**: Transform ideas into pure functional specifications (WHAT, not HOW)
- **Task Generation**: Convert functional specifications into executable tasks
- **Task Management**: Add, split, update, and manage tasks after generation
- **Task Review**: Verify implemented tasks meet specifications
- **TDD Workflow**: Test-Driven Development integration for task implementation
- **Drift Guard**: Real-time monitoring of specification-to-implementation drift
- **Ralph Loop**: Guided automation loop for full specification lifecycle
- **Code Cleanup**: Remove technical debt and finalize tasks after review approval
- **Automatic stop gate after task implementation**: Forces review, fixes, and spec sync handling before Claude stops
- **Spec Quality Check**: Review and validate specification content quality
- **Spec Sync Context**: Synchronize technical context (Knowledge Graph, Tasks, Codebase)
- **Spec Sync With Code**: Synchronize functional specification with implementation

## Workflow

```
Idea → Functional Specification → Tasks → TDD / Implementation → Review → Code Cleanup → Done
       (brainstorm)              (spec-to-tasks)  (task-tdd)    (task-review)   (code-cleanup)
```

## Specification Maintenance Note

- Treat files in `docs/specs/` as deliverables whenever they are used to drive implementation, not just as background context.
- After `/specs:task-implementation`, complete `/specs:task-review`, fix every finding, and run `/specs:spec-sync-with-code` whenever the implementation changed, clarified, or constrained the intended behavior, decisions, acceptance criteria, or task notes.
- During a normal chat session, if the assistant used an existing spec to guide implementation or recommendations, update the affected spec files before concluding whenever the session changed or clarified what should be built.
- If no spec update is needed, say that explicitly and explain why the current specification already matches the implemented outcome.

Example to include in the CLAUDE.md or AGENTS.md for specification maintenance:

```markdown
## Specification Maintenance Rules

- When work is driven by files in `docs/specs/`, treat the specification as a deliverable, not only as background context.
- After `/specs:task-implementation`, always run `/specs:task-review`, fix every finding, and then run `/specs:spec-sync-with-code` whenever the implementation
  changed, clarified, or constrained the intended behavior, acceptance criteria, decisions, or task notes.
- During normal chat sessions, if specs were used to guide implementation or recommendations, update the affected spec files before concluding whenever the
  session changed or clarified what should be built.
- If no spec update is needed, state that explicitly and explain why the current spec already matches the implemented outcome.
```

## Commands

### Specification Creation

- `/specs:brainstorm [idea-description]` - Full specification creation for complex features
- `/specs:quick-spec [idea-description]` - Quick specification for simple features
- `/specs:spec-quality-check [spec-folder]` - Review specification content quality and completeness
- `/specs:spec-sync-context [spec-folder]` - Synchronize technical context (KG, Tasks, Codebase)

### Task Management

- `/specs:spec-to-tasks [spec-folder]` - Convert specs to executable tasks
- `/specs:task-manage --action=[add|split|update|list]` - Manage tasks after generation
- `/specs:task-implementation --lang=[lang] [task-file]` - Implement a specific task
- `/specs:task-tdd --lang=[lang] [task-file]` - Test-Driven implementation of a task
- `/specs:task-review --lang=[lang] [task-file]` - Review implemented task
- `/specs:code-cleanup --lang=[lang] [task-file]` - Clean up code after review approval

### Automation

- `/specs:ralph-loop` - Guided automation loop for spec-driven development

### Synchronization

- `/specs:spec-sync-with-code [spec-folder]` - Synchronize functional specification with implementation

## Usage Example

```bash
# 1. Create a functional specification
/specs:brainstorm "Add user authentication with JWT tokens"

# 2. Review specification quality (optional)
/specs:spec-quality-check docs/specs/001-user-auth/

# 3. Convert specification to tasks
/specs:spec-to-tasks docs/specs/001-user-auth/

# 4. List all tasks
/specs:task-manage --action=list --spec=docs/specs/001-user-auth/

# 5. Implement a task
/specs:task-implementation --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# Installed hook: Claude cannot stop yet until review/fixes run
/specs:task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# If review reveals spec drift or documentation changes
/specs:spec-sync-with-code docs/specs/001-user-auth/ --after-task=TASK-001

# 6. Sync technical context after implementation
/specs:spec-sync-context docs/specs/001-user-auth/ --task=TASK-001

# 7. Review implementation
/specs:task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# 8. Clean up code after review approval
/specs:code-cleanup --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# 9. Sync specification with implementation (if deviations detected)
/specs:spec-sync-with-code docs/specs/001-user-auth/
```

## Skills

### knowledge-graph

Persistent JSON file that stores discoveries from codebase analysis:
- Location: `docs/specs/[ID-feature]/knowledge-graph.json`
- Reduces redundant codebase exploration
- Enables task validation against actual codebase state

### ralph-loop

Guided automation loop for specification-driven development:
- Orchestrates task implementation, review, and cleanup
- Maintains state across turns for long-running tasks
- Integrates with spec-driven commands for consistent workflow

### specs-code-cleanup

Professional code cleanup after task review approval:
- Removes debug logs and temporary comments
- Optimizes imports and improves readability
- Finalizes code before task completion

## Hooks

### drift-guard

Monitors the consistency between specifications and implementation:
- `drift-init`: Initializes drift monitoring for a specification
- `drift-monitor`: Analyzes implementation changes against functional requirements
- `drift-report`: Generates a report highlighting deviations or missing features

### task-implementation-review-stop

Forces review and fixes after task implementation:
- Prevents the assistant from stopping before running `/specs:task-review`
- Ensures fixes and optional spec synchronization are handled immediately
- Maintains high quality standards for implemented tasks

## Auto-Status Hooks

Task status is automatically managed by Claude Code hooks when you edit task files. No manual installation or script setup required.

### How It Works

When you edit any `TASK-*.md` file, hooks automatically:
1. Detect the file change
2. Analyze checkbox completion
3. Update the `status` field in YAML frontmatter
4. Set appropriate date fields

### Status Transitions

| Your Action | Automatic Status | Date Field Set |
|-------------|------------------|----------------|
| Check acceptance criteria boxes | `pending` → `in_progress` → `implemented` | `started_date`, `implemented_date` |
| Check all DoD boxes | `implemented` → `reviewed` | `reviewed_date` |
| Add Cleanup Summary section | `reviewed` → `completed` | `completed_date`, `cleanup_date` |

### Example Workflow

```bash
# 1. Implement a task
/specs:task-implementation --lang=spring --task="docs/specs/001/tasks/TASK-001.md"

# 2. During implementation, check AC boxes in the task file
# → Status automatically updates to 'implemented'

# 3. Run review
/specs:task-review --task="docs/specs/001/tasks/TASK-001.md"

# 4. Check DoD boxes in the task file
# → Status automatically updates to 'reviewed'

# 5. Run cleanup
/specs:code-cleanup --task="docs/specs/001/tasks/TASK-001.md"

# 6. Add Cleanup Summary section
# → Status automatically updates to 'completed'
```

### Manual Override

If you need to manually set a status (e.g., `blocked`, `superseded`), simply edit the YAML frontmatter:

```yaml
---
id: TASK-001
status: blocked  # Manually set any valid status
---
```

Valid statuses: `pending`, `in_progress`, `implemented`, `reviewed`, `completed`, `superseded`, `optional`, `blocked`

### Hooks Included

| Hook | Trigger | Purpose |
|------|---------|---------|
| `task-auto-status.py` | `Write/Edit` on `TASK-*.md` | Auto-update status based on content |
| `task-validator.py` | `Write/Edit` on `TASK-*.md` | Validate frontmatter structure |
| `drift-*.py` | Various | Monitor spec-to-code drift |

## Requirements

This plugin requires the following plugins:
- `developer-kit-core` - For general agents (code-explorer, code-reviewer, refactor-expert, software-architect, debugger)

## License

MIT

## Author

Giuseppe Trisciuoglio <giuseppe.trisciuoglio@gmail.com>
