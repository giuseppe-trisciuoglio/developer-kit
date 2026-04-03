---
description: "Provides code cleanup capability to remove technical debt after task review approval. Removes debug logs, temporary comments, optimizes imports, and improves code readability. Use when a task has passed review and needs final cleanup before marking as complete."
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] --task=\"docs/specs/XXX-feature/tasks/TASK-XXX.md\""
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Code Cleanup

Performs post-review code cleanup to remove technical debt, temporary code, and improve code quality before final task completion. This is the final step before marking a task as done.

## Overview

This command cleans up code after it has passed review to ensure:
1. **No Technical Debt**: Remove debug logs, temporary comments, and resolved TODOs
2. **Code Quality**: Optimize imports, improve readability, align with project standards
3. **Documentation**: Verify inline documentation is accurate and complete
4. **Final Polish**: Ensure the code is production-ready

**Input**: `docs/specs/[id]/tasks/TASK-XXX.md` (that has passed review)
**Output**: Cleaned code, updated task status

### Workflow Position

```
Idea → Functional Specification → Tasks → Implementation → Review → Code Cleanup → Done
              (brainstorm)           (spec-to-tasks)       (task-implementation)  (task-review)   (this)         (Done)
```

## Usage

```bash
# Cleanup after review approval
/specs:code-cleanup --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# With language specification
/specs:code-cleanup --lang=typescript --task="docs/specs/001-user-auth/tasks/TASK-002.md"
/specs:code-cleanup --lang=nestjs --task="docs/specs/001-user-auth/tasks/TASK-003.md"
/specs:code-cleanup --lang=react --task="docs/specs/001-user-auth/tasks/TASK-004.md"
/specs:code-cleanup --lang=python --task="docs/specs/001-user-auth/tasks/TASK-005.md"
/specs:code-cleanup --lang=general --task="docs/specs/001-user-auth/tasks/TASK-006.md"
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--lang` | No | Target language/framework: `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `general` |
| `--task` | Yes | Path to the task file (e.g., `docs/specs/001-user-auth/tasks/TASK-001.md`) |

## Current Context

The command will automatically gather context information when needed:
- Current git branch and status
- Recent commits and changes
- Available when the repository has history

---

You are performing final code cleanup after a task has passed review. Follow a systematic approach: identify files to clean, remove technical debt, optimize code, verify documentation, and mark the task as complete.

## Core Principles

- **Clean, not change**: Only remove or reorganize — don't change functionality
- **Preserve behavior**: The code must work exactly the same after cleanup
- **Follow project standards**: Use project's linting/formatting rules
- **Document what you clean**: Keep a record of what was removed/changed
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Task Verification

**Goal**: Verify the task exists and has passed review

**Actions**:

1. Create todo list with all phases
2. Parse `$ARGUMENTS` to extract:
   - `--lang` parameter (language/framework)
   - `--task` parameter (path to task file)

3. Read the task file and verify:
   - Task exists and is readable
   - Task status is `reviewed` or `implemented` (not `completed` yet)
   - Review report exists at `docs/specs/[id]/tasks/TASK-XXX--review.md`
   - Review status is "approved" or passed

4. If task not found:
   - Ask user for correct path via AskUserQuestion
   - Or list available tasks in `docs/specs/*/tasks/`

5. If task hasn't been reviewed:
   - Inform user: "This task hasn't passed review yet. Run `/specs:task-review` first."
   - Stop cleanup process

6. Extract from task file:
   - Task ID and title
   - List of files created/modified (from `provides` section or review report)
   - Reference to specification file

---

## Phase 2: Identify Files to Clean

**Goal**: Determine which files need cleanup

**Actions**:

1. **Check review report for files**:
   - Read `docs/specs/[id]/tasks/TASK-XXX--review.md`
   - Extract list of files created/modified during implementation
   - Look for "Code Files" section or similar

2. **Check task provides section**:
   - Read the `provides` field from task YAML frontmatter
   - Extract file paths from the provides list

3. **Verify files exist**:
   - Check each file exists and is readable
   - If files are missing, note them but continue with available files

4. **Create cleanup file list**:
   - Document all files that will be cleaned
   - Categorize by type (source files, test files, config files)

---

## Phase 3: Technical Debt Removal

**Goal**: Remove temporary code, debug artifacts, and resolved TODOs

**Actions**:

1. **Search for common technical debt patterns** (use Grep):

   **Debug/Logging statements to remove**:
   - `console.log` (JavaScript/TypeScript)
   - `System.out.println` (Java)
   - `print()` / `logger.debug` in production code (Python)
   - `// DEBUG:`, `// TODO:`, `// FIXME:` comments that are resolved
   - Temporary comments like `// temp`, `// hack`, `// workaround`

   **Example search patterns**:
   ```bash
   # JavaScript/TypeScript
   grep -rn "console.log" --include="*.ts" --include="*.tsx" --include="*.js" [files]
   grep -rn "// DEBUG:" --include="*.ts" [files]
   grep -rn "// TODO.*" --include="*.ts" [files]  # Check if TODOs are resolved
   
   # Java
   grep -rn "System.out.println" --include="*.java" [files]
   grep -rn "// DEBUG:" --include="*.java" [files]
   
   # Python
   grep -rn "print(" --include="*.py" [files]
   grep -rn "# DEBUG:" --include="*.py" [files]
   ```

2. **Review each finding**:
   - Not all debug logs need removal (some may be intentional)
   - Check context to determine if it's truly temporary
   - When in doubt, keep it and note it for user review

3. **Remove confirmed technical debt**:
   - Delete `console.log`, `System.out.println`, temporary print statements
   - Remove `// DEBUG:` comments and similar temporary annotations
   - Remove resolved TODOs/FIXMEs (keep unresolved ones)

4. **Document removals**:
   - Keep a list of what was removed and from which files
   - Note any items that were kept intentionally

---

## Phase 4: Import Optimization

**Goal**: Optimize and reorganize imports/statements

**Actions**:

1. **Use language-specific tools when available**:

   | Language | Command |
   |----------|---------|
   | Java | `./mvnw spotless:apply` or IDE organize imports |
   | TypeScript | `npm run lint:fix` or `npx eslint --fix` |
   | Python | `isort .` or `ruff check --fix` |

2. **If no automated tool available, manually organize**:

   **Java imports** (organize in this order):
   ```java
   // 1. java.*
   import java.util.*;
   import java.time.*;
   
   // 2. jakarta.* / javax.*
   import jakarta.persistence.*;
   
   // 3. Third-party libraries
   import org.springframework.*;
   import lombok.*;
   
   // 4. Project imports
   import com.mycompany.myproject.*;
   ```

   **TypeScript imports**:
   ```typescript
   // 1. External libraries
   import { Component } from 'react';
   import { Injectable } from '@nestjs/common';
   
   // 2. Internal absolute imports
   import { UserService } from '@/services/user.service';
   
   // 3. Internal relative imports
   import { User } from './user.entity';
   import { utils } from '../utils';
   ```

3. **Remove unused imports**:
   - Check for imports that are declared but not used
   - Remove them carefully (verify they're truly unused)

4. **Document import changes**:
   - Note which files had imports reorganized
   - Note any unused imports removed

---

## Phase 5: Code Readability Improvements

**Goal**: Improve code readability without changing functionality

**Actions**:

1. **Apply language-specific formatting**:

   | Language | Command |
   |----------|---------|
   | Java | `./mvnw spotless:apply` or `./gradlew spotlessApply` |
   | TypeScript/JavaScript | `npm run format` or `npx prettier --write` |
   | Python | `black .` or `ruff format` |

2. **Manual readability improvements** (if no formatter available):
   - Fix inconsistent indentation
   - Add empty lines between logical sections
   - Break long lines (>120 characters)
   - Fix inconsistent spacing around operators

3. **Check for code smells** (lightweight fixes only):
   - Remove dead code (unreachable code, unused variables)
   - Simplify overly complex expressions (if obvious)
   - Fix obvious naming inconsistencies

4. **Document readability changes**:
   - Note which files were formatted
   - List any manual improvements made

---

## Phase 6: Documentation Verification

**Goal**: Verify and improve inline documentation

**Actions**:

1. **Check class/file headers**:
   - Verify each file has appropriate header documentation
   - Ensure @author, @since tags are present (if project uses them)

2. **Check public API documentation**:
   - Public methods should have JSDoc/Javadoc/docstrings
   - Parameters and return values should be documented
   - Exceptions should be documented

3. **Verify TODO/FIXME comments**:
   - Review remaining TODOs — are they still valid?
   - Ensure TODOs have context (not just "TODO: fix this")
   - Consider creating issues for important TODOs

4. **Update outdated comments**:
   - Remove comments that no longer match the code
   - Update comments that describe changed behavior

5. **Document documentation changes**:
   - Note which files had documentation added/updated
   - List any TODOs that were removed or created

---

## Phase 7: Final Verification

**Goal**: Verify the code still works after cleanup

**Actions**:

1. **Run linters** (if available):
   ```bash
   # Java
   ./mvnw checkstyle:check spotless:check
   
   # TypeScript
   npm run lint
   
   # Python
   ruff check . && black --check .
   ```

2. **Run tests** (if available):
   ```bash
   # Java
   ./mvnw test -q
   
   # TypeScript
   npm test
   
   # Python
   pytest
   ```

3. **Verify no functionality changes**:
   - Check that only formatting/cleanup changes were made
   - No logic changes, no method signature changes
   - If logic changes are needed, stop and inform user

4. **If tests fail**:
   - Stop cleanup process
   - Inform user of failures
   - Do not proceed until issues are resolved

---

## Phase 8: Task Completion

**Goal**: Mark task as cleaned and complete

**Actions**:

1. **Update task file YAML frontmatter**:
   - Set `status: completed`
   - Add `completed_date: YYYY-MM-DD`
   - Add `cleanup_date: YYYY-MM-DD`

2. **Add cleanup summary to task file**:
   ```markdown
   ## Cleanup Summary
   
   **Date**: YYYY-MM-DD
   
   ### Files Cleaned
   - [List of files cleaned]
   
   ### Changes Made
   - Removed debug logs from [files]
   - Optimized imports in [files]
   - Fixed formatting in [files]
   - Updated documentation in [files]
   
   ### Verification
   - [x] Linter checks passed
   - [x] Tests passed
   - [x] No functionality changes
   ```

3. **Mark all todos complete**

4. **Summary**:
   - Task marked as completed
   - Files cleaned: [count]
   - Technical debt items removed: [count]
   - Ready for next task

---

## Integration with Workflow

This command completes the development workflow:

```
/specs:brainstorm
    ↓
[Creates: docs/specs/[id]/YYYY-MM-DD--feature-name.md]
    ↓
/specs:spec-to-tasks --lang=[language] docs/specs/[id]/
    ↓
[Creates: docs/specs/[id]/tasks/TASK-XXX.md]
    ↓
/specs:task-implementation --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Implements task]
    ↓
/specs:task-review --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Approves task after review]
    ↓
/specs:code-cleanup --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
    ↓
[Cleans code, marks task complete]
    ↓
[Done - Proceed to next task]
```

---

## Examples

### Example 1: Cleanup After Spring Boot Task Review

```bash
# Task has passed review
/specs:code-cleanup --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md"

# Cleanup process:
# → Task verified: TASK-001 (status: reviewed)
# → Files to clean: UserController.java, UserService.java, UserRepository.java
# → Removed: 5 debug log statements, 2 resolved TODOs
# → Optimized imports in 3 files
# → Formatted code with Spotless
# → Tests passing
# → Task marked as completed
```

### Example 2: Cleanup TypeScript/React Task

```bash
/specs:code-cleanup --lang=typescript --task="docs/specs/002-dashboard/tasks/TASK-003.md"

# Cleanup process:
# → Task verified: TASK-003 (status: reviewed)
# → Files to clean: Dashboard.tsx, useDashboard.ts, Dashboard.test.tsx
# → Removed: 8 console.log statements
# → Optimized imports with ESLint
# → Formatted with Prettier
# → Task marked as completed
```

---

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Task Verification
[ ] Phase 2: Identify Files to Clean
[ ] Phase 3: Technical Debt Removal
[ ] Phase 4: Import Optimization
[ ] Phase 5: Code Readability Improvements
[ ] Phase 6: Documentation Verification
[ ] Phase 7: Final Verification
[ ] Phase 8: Task Completion
```

Update the status as you progress through each phase.

---

**Note**: This command ensures that code is clean, well-documented, and production-ready before marking a task as complete. It acts as a final quality gate in the development workflow.
