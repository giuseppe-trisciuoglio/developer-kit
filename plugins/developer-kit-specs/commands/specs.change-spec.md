---
description: "Creates a Change Specification for delta/iterations and bug fixes. Use when modifying existing systems or documenting bug fixes. Output: docs/specs/[id]/changes/YYYY-MM-DD--change-name.md"
argument-hint: "[ --type=delta|bugfix ] [ --spec=docs/specs/XXX-feature ] [ --title=\"change description\" ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, TodoWrite
model: inherit
---

# Change Specification

## Overview

Creates a structured Change Specification document for:
1. **Delta specifications** — iteration changes, new features in existing system
2. **Bug fix specifications** — defect corrections with root cause analysis

## When to Use

- **Delta**: Adding new feature to existing system, modifying existing behavior
- **Bug Fix**: Documenting a bug fix with before/after/unchanged behavior

Do NOT use for new features from scratch → use `specs.brainstorm`

## Usage

```bash
# Create delta specification
/developer-kit-specs:specs.change-spec --type=delta --spec=docs/specs/001-feature/ --title="Add payment retry logic"

# Short form
/developer-kit-specs:specs.change-spec delta Add payment retry logic

# Create bug fix specification
/developer-kit-specs:specs.change-spec --type=bugfix --spec=docs/specs/001-feature/ --title="Fix race condition in checkout"

# Short form
/developer-kit-specs:specs.change-spec bugfix Fix race condition in checkout
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--type` | Yes | Change type: delta or bugfix |
| `--spec` | No | Path to spec folder (e.g., docs/specs/XXX-feature) |
| `--title` | No | Change description/title |

## Argument Parsing

1. Run the shared argument parser:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```
   Read JSON output and extract:
   - `type` → "delta" or "bugfix" (required)
   - `spec` → spec folder path
   - `title` → change description
   - `flags` → boolean flags

2. If `type` is not provided, ask the user to choose between delta and bugfix

3. If `spec` is null, auto-detect from git branch

4. Validate required parameters (type is mandatory)

## Workflow Position

```
brainstorm → spec-to-tasks → implementation → review
     ↓
change-spec (when modifying existing feature)
     ↓
task-implementation (from change spec)
     ↓
task-review
```

## Core Principles

- **Delta-focused**: Only document WHAT changes, not the entire system
- **Minimal**: No need to restate unchanged behavior (except in bug fix)
- **Audit trail**: Changes are versioned with date
- **Root cause for bugs**: Not just symptom, but WHY the bug exists
- **Unchanged Behavior**: MANDATORY section for bug fixes to prevent regressions

---

## Phase 1: Mode Detection & Argument Parsing

**Goal**: Determine the mode (delta or bugfix) and gather required arguments

**Actions**:

1. Run argument parser:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/parse_args.py" "$ARGUMENTS"
   ```

2. Extract and validate parameters:
   - `type`: Must be "delta" or "bugfix"
   - `spec`: Path to parent specification folder
   - `title`: Change description

3. If `type` is missing:
   - Use AskUserQuestion to determine mode:
     - "Is this a delta (new feature/iteration) or a bug fix?"
     - Options: "Delta", "Bug Fix"

4. If `spec` is missing:
   - Auto-detect from git branch (parse branch name for spec ID)
   - If auto-detection fails, ask user for the spec path

5. If `title` is missing:
   - Ask user: "What is the change description?"

6. Create todo list with relevant phases based on mode

---

## Phase 2: Discovery

**Goal**: Gather context about the existing system and the change

**Actions**:

1. **For Delta mode**:
   - Read the existing specification (from `--spec` path)
   - Identify the current state of the affected components
   - Ask the user what is changing:
     - What's new?
     - What's modified?
     - What's removed?

2. **For Bug Fix mode**:
   - Ask user for:
     - Brief description of the bug
     - Steps to reproduce (if known)
     - Expected behavior
     - Actual behavior
   - Investigate codebase:
     - Find the problematic code
     - Identify root cause (not just symptom)
   - Check git history for related changes

3. Create a summary of what you discovered

---

## Phase 3: Delta Classification (Delta Mode Only)

**Goal**: Classify changes into ADDED/MODIFIED/REMOVED

**Actions**:

For each change, classify it:

| Classification | Meaning | Example |
|---------------|---------|---------|
| **ADDED** | New functionality | "Add payment retry logic" |
| **MODIFIED** | Changed from old to new | "Session timeout: 30min → 60min" |
| **REMOVED** | Deprecated/removed | "Remove legacy OAuth endpoint" |

For each classified change, ask the user:
- What requirements does this change need?
- What acceptance criteria define success?
- What components are affected?

---

## Phase 4: Root Cause Analysis (Bug Fix Mode Only)

**Goal**: Understand WHY the bug exists, not just the symptom

**Actions**:

1. Trace the execution path that causes the bug

2. Identify the specific code responsible

3. Determine WHY this code is wrong:
   - Logic error?
   - Missing validation?
   - Race condition?
   - Wrong assumption?
   - Edge case not handled?
   - Type error?
   - Concurrency issue?

4. Document the root cause clearly with:
   - **Location**: File, class, method, line numbers
   - **Root Cause**: Why this bug exists
   - **Why It Happened**: The chain of events that caused the bug

5. **IMPORTANT**: The root cause is critical — document it thoroughly to prevent recurrence

---

## Phase 5: Document Generation

**Goal**: Create the change specification document

**Actions**:

1. Determine the output path:
   ```
   docs/specs/[id]/changes/YYYY-MM-DD--change-name.md  (Delta)
   docs/specs/[id]/changes/YYYY-MM-DD--bugfix--short-name.md  (Bug Fix)
   ```

2. Create the changes directory if it doesn't exist:
   ```bash
   mkdir -p docs/specs/[id]/changes
   ```

3. Generate the document based on mode:

### Delta Document Template

Read the Delta template using this lookup order:
1. `${CLAUDE_PLUGIN_ROOT}/templates/change-specification-delta.md`
2. `templates/change-specification-delta.md` inside the installed skill folder when this command is packaged for a non-Claude coding agent.
Fill in the gathered information and save to the output path.

The template defines these sections:
- Summary and Change Summary table
- ADDED / MODIFIED / REMOVED sections (each with Requirements and Acceptance Criteria)
- Affected Components, Testing Strategy, Rollback Plan

<details>
<summary>Legacy template reference (deprecated — primary template path: ${CLAUDE_PLUGIN_ROOT}/templates/change-specification-delta.md; fallback: templates/change-specification-delta.md on skill folder)</summary>

```markdown
# Change Specification: [Title]

**Type**: Delta
**Date**: YYYY-MM-DD
**Status**: Draft
**Parent Spec**: [link to parent spec]

### Summary

[Brief description of why this change is needed]

### Change Summary

| Classification | Count |
|---------------|-------|
| ADDED | N |
| MODIFIED | N |
| REMOVED | N |

## ADDED

### [Feature/Requirement Name]

**Description**: [What is being added]

**Requirements**:
- REQ-CHG-001: [EARS formatted requirement]
- REQ-CHG-002: [EARS formatted requirement]

**Acceptance Criteria**:
- [ ] [AC-001]
- [ ] [AC-002]

**Impact**: [What other components are affected]

---

## MODIFIED

### [Component/Feature Name]

**Previous Behavior**: [Old implementation description]

**New Behavior**: [New implementation description]

**Requirements**:
- REQ-CHG-003: [EARS formatted requirement]

**Acceptance Criteria**:
- [ ] [AC-003]

**Impact**:
- Affected: [list components]
- Breaking: [YES/NO - if YES, detail migration path]

---

## REMOVED

### [Feature/Component Name]

**Reason**: [Why this is being removed]

**Migration Path**: [How to transition away from this]

**Cutover Date**: [When this will be fully removed]

**Impact**: [What breaks]

---

## Affected Components

| Component | Change Type | Risk |
|-----------|-------------|------|
| [Component] | ADDED/MODIFIED/REMOVED | HIGH/MEDIUM/LOW |

## Testing Strategy

- Unit tests for new functionality
- Regression tests for modified functionality
- Cleanup tests for removed functionality

## Rollback Plan

[How to revert if needed]
```

</details>

### Bug Fix Document Template

Read the Bug Fix template using this lookup order:
1. `${CLAUDE_PLUGIN_ROOT}/templates/bug-fix-specification.md`
2. `commands/templates/bug-fix-specification.md`
3. `templates/bug-fix-specification.md` inside the installed skill folder when this command is packaged for a non-Claude coding agent.
Fill in the gathered information and save to the output path.

The template defines these sections:
- Bug Summary (title, component, severity, reproduction steps)
- Current Behavior vs Expected Behavior
- Root Cause Analysis
- Unchanged Behavior (regression prevention)
- Solution Approach, Acceptance Criteria, Risk Assessment

<details>
<summary>Legacy template reference (deprecated — primary template path: ${CLAUDE_PLUGIN_ROOT}/templates/bug-fix-specification.md; fallback: commands/templates/bug-fix-specification.md)</summary>

```markdown
# Bug Fix Specification: [Short Name]

**Type**: Bug Fix
**Date**: YYYY-MM-DD
**Status**: Draft
**Severity**: CRITICAL/HIGH/MEDIUM/LOW
**Parent Spec**: [link to parent spec]

### Bug Summary

- **Title**: [Concise bug description]
- **Component**: [Affected component]
- **Severity**: [CRITICAL/HIGH/MEDIUM/LOW]
- **Reported By**: [Reporter/Discovered by]
- **Report Date**: [YYYY-MM-DD]

### Current Behavior (Incorrect)

[Detailed description of how the system currently behaves]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step N]

**Expected Behavior**: [How the system SHOULD behave]

### Root Cause Analysis

**Location**: [File, class, method]

**Root Cause**: [Why this bug exists]

**Category**:
- [ ] Logic Error
- [ ] Missing Validation
- [ ] Race Condition
- [ ] Type Error
- [ ] Concurrency Issue
- [ ] Edge Case Not Handled
- [ ] Configuration Issue
- [ ] Wrong Assumption

**Code Location**:
```
[File path]:[line numbers]
[Relevant code snippet]
```

**Why It Happened**: [One paragraph explaining the chain of events that caused the bug]

---

## Expected Behavior (After Fix)

[Detailed description of how the system will behave after the fix]

---

## Unchanged Behavior (CRITICAL)

**This section documents what MUST remain the same to prevent regressions.**

The following behaviors MUST NOT change:
- [ ] [Behavior 1 - e.g., "Login page still requires password"]
- [ ] [Behavior 2 - e.g., "API response format unchanged"]
- [ ] [Behavior 3 - e.g., "User session still expires after 30 minutes"]

**Reason**: These behaviors are used by other components and changing them would break integration.

### Functional Invariants

- [ ] [Core behavior that must remain identical]

### API Contracts

- [ ] [Response format, status codes, headers must remain unchanged]

### Data Integrity

- [ ] [Validation rules, constraints, data relationships]

### Integration Points

- [ ] [How it interacts with other systems - must preserve interfaces]

### Performance

- [ ] [Response time, throughput expectations]

---

## Solution Approach

**Implementation Strategy**: [Brief approach]

**Changes Required**:
- [File 1]: [Change description]
- [File 2]: [Change description]

**Test Plan**:
1. Verify bug is fixed (reproduce and confirm)
2. Verify unchanged behaviors are preserved
3. Run regression tests

---

## Acceptance Criteria

- [ ] Bug is fixed (steps to reproduce now work correctly)
- [ ] No regression in unchanged behaviors
- [ ] Unit tests added for the edge case
- [ ] Integration tests pass

## Risk Assessment

- **Risk of Fix**: [LOW/MEDIUM/HIGH]
- **Risk of Regression**: [LOW/MEDIUM/HIGH]
- **Affected Components**: [List]
- **Migration Impact**: [None/Backward Compatible/Breaking]

## Related

- [Parent spec or feature]
- [Related bugs (if any)]
- [ADR or technical decisions (if any)]
```

</details>

---

## Phase 6: Task Generation

**Goal**: Create implementation tasks from the change specification

**Actions**:

1. **For Delta mode**:
   - For each ADDED item, create tasks similar to spec-to-tasks workflow
   - For each MODIFIED item, create tasks with regression testing
   - For each REMOVED item, create cleanup/deprecation tasks

2. **For Bug Fix mode**:
   - Create task for the fix
   - Add regression testing tasks
   - Add "unchanged behavior verification" tasks

3. Save tasks to:
   ```
   docs/specs/[id]/changes/YYYY-MM-DD--change-name/TASK-CHG-001.md
   ```

---

## Phase 7: Summary

**Goal**: Report completion with all relevant information

**Actions**:

1. Report file location
2. **For Delta**: List ADDED/MODIFIED/REMOVED counts
3. **For Bug Fix**: List severity, affected components, and root cause summary
4. Provide next steps:
   - Run `spec-to-tasks` if tasks are needed
   - Run `specs.sync` after implementation
   - Archive the change spec after merge

---

## Unchanged Behavior Template (For Bug Fix)

**This section is MANDATORY for all bug fix specifications. Skipping it risks regressions.**

```markdown
## Unchanged Behavior

The following behaviors MUST remain identical after the fix:

### Functional Invariants
- [ ] [Core behavior that must not change - e.g., "Authentication still required for protected endpoints"]

### API Contracts
- [ ] [Response format must remain unchanged - e.g., "JSON structure with {data, metadata} keys"]
- [ ] [Status codes - e.g., "200 for success, 400 for bad request, 401 for unauthorized"]

### Data Integrity
- [ ] [Validation rules - e.g., "Email must still be validated before processing"]
- [ ] [Constraints - e.g., "Unique constraint on user_id still enforced"]

### Integration Points
- [ ] [External APIs - e.g., "Payment provider webhook interface unchanged"]
- [ ] [Internal services - e.g., "OrderService interface unchanged"]

### Performance
- [ ] [Response time - e.g., "API response < 200ms"]
- [ ] [Throughput - e.g., "Handle 1000 concurrent requests"]
```

---

## File Naming Convention

```
docs/specs/[id]/changes/
├── YYYY-MM-DD--change-name.md          # Delta
└── YYYY-MM-DD--bugfix--short-name.md   # Bug Fix
```

### Naming Rules

- Date format: YYYY-MM-DD (creation date)
- Change name: kebab-case, descriptive
- Bug fix prefix: `bugfix--`
- No spaces in filenames

---

## Archive Strategy

After the change is merged:

1. Move to `changes/archived/`:
   ```bash
   mv docs/specs/[id]/changes/YYYY-MM-DD--change-name.md \
      docs/specs/[id]/changes/archived/YYYY-MM-DD--change-name.md
   ```

2. Update parent spec with reference to change

3. Update `decision-log.md` with change decision:
   ```
   DEC-[N]: [Decision summary]
   Date: YYYY-MM-DD
   Type: Delta/Bug Fix
   ```

---

## Integration Points

### With brainstorm

Change-spec can be used after brainstorm when requirements evolve:
```
brainstorm → spec-to-tasks → implementation
                    ↓
              change-spec (if requirements change)
                    ↓
              task-implementation
```

### With brainstorm

Brainstorm generates new features; change-spec modifies existing ones.

### With specs.sync

After implementing changes from a change-spec:
```
change-spec → task-implementation → task-review → specs.sync
```

---

## Error Handling

### Missing Type

If `type` is not provided and user doesn't choose:
```
Error: Change type is required.
Please specify --type=delta or --type=bugfix
```

### Invalid Spec Path

If the specified spec folder doesn't exist:
```
Error: Spec folder not found: docs/specs/001-feature/
Please verify the path or create the specification first with brainstorm
```

### Document Already Exists

If a change spec with the same name already exists:
```
Warning: Change specification already exists: docs/specs/001-feature/changes/2024-03-15--change-name.md
Options:
  1. Overwrite existing
  2. Use different title
  3. Cancel
```

---

## Todo Management

Create a todo list at the start with all relevant phases:

```
[ ] Phase 1: Mode Detection & Argument Parsing
[ ] Phase 2: Discovery
[ ] Phase 3: Delta Classification (Delta) / Root Cause Analysis (Bug Fix)
[ ] Phase 4: Document Generation
[ ] Phase 5: Task Generation
[ ] Phase 6: Summary
```

---

## Examples

### Delta Example

**Input:**
```bash
/developer-kit-specs:specs.change-spec --type=delta --spec=docs/specs/001-feature/ --title="Add multi-currency support"
```

**Output file:** `docs/specs/001-feature/changes/2024-03-15--add-multi-currency-support.md`

**Content:**
- ADDED: Multi-currency support module
- MODIFIED: Payment processing to handle currency conversion
- REMOVED: Single currency assumption in pricing

---

### Bug Fix Example

**Input:**
```bash
/developer-kit-specs:specs.change-spec --type=bugfix --spec=docs/specs/001-feature/ --title="Fix session timeout calculation"
```

**Output file:** `docs/specs/001-feature/changes/2024-03-15--bugfix--session-timeout.md`

**Content:**
- Root Cause: Integer overflow in session duration calculation
- Current Behavior: Sessions timeout after 49.7 days instead of 30 days
- Expected Behavior: Sessions timeout exactly after 30 days (2592000 seconds)
- Unchanged Behavior: Session validation logic, authentication flow, session storage

---

## Checklist

Before completing, verify:

- [ ] Document follows correct template (Delta or Bug Fix)
- [ ] All required sections are present
- [ ] Bug Fix has "Unchanged Behavior" section (MANDATORY)
- [ ] Root cause is documented (not just symptoms)
- [ ] Acceptance criteria are testable
- [ ] File naming follows convention
- [ ] Tasks generated if requested

---

**Status**: Ready for implementation
**Priority**: HIGH
**Related**: A4 (Technical Plan), A12 (Unchanged Behavior marker)