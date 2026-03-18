# Developer Kit Specs

Specifications-driven development workflow for transforming ideas into functional specifications and executable tasks.

## Overview

This plugin provides a complete workflow for:
- **Brainstorming**: Transform ideas into pure functional specifications (WHAT, not HOW)
- **Task Generation**: Convert functional specifications into executable tasks
- **Task Management**: Add, split, update, and manage tasks after generation
- **Task Review**: Verify implemented tasks meet specifications
- **Spec Quality Check**: Review and validate specification content quality
- **Spec Sync Context**: Synchronize technical context (Knowledge Graph, Tasks, Codebase)
- **Spec Sync With Code**: Synchronize functional specification with implementation

## Workflow

```
Idea → Functional Specification → Tasks → Implementation → Review
       (brainstorm)              (spec-to-tasks)          (task-review)
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
- `/specs:task-review --lang=[lang] [task-file]` - Review implemented task

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

# 6. Sync technical context after implementation
/specs:spec-sync-context docs/specs/001-user-auth/ --task=TASK-001

# 7. Review implementation
/specs:task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md

# 8. Sync specification with implementation (if deviations detected)
/specs:spec-sync-with-code docs/specs/001-user-auth/
```

## Skills

### knowledge-graph

Persistent JSON file that stores discoveries from codebase analysis:
- Location: `docs/specs/[ID-feature]/knowledge-graph.json`
- Reduces redundant codebase exploration
- Enables task validation against actual codebase state

## Requirements

This plugin requires the following plugins:
- `developer-kit-core` - For general agents (code-explorer, code-reviewer, refactor-expert, software-architect, debugger)

## License

MIT

## Author

Giuseppe Trisciuoglio <giuseppe.trisciuoglio@gmail.com>
