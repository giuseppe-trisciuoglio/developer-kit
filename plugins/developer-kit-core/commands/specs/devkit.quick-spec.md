---
description: "Lightweight spec for bug fixes and small features. Use when the change is
  well-understood and doesn't need full brainstorming. Skips idea refinement and approach
  exploration. Output: docs/specs/[id]/YYYY-MM-DD--feature-name.md (minimal format)"
argument-hint: "[ description ]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, TodoWrite
model: inherit
---

# Quick Spec

Lightweight specification generation for bug fixes and small features. Use when the change is well-understood and doesn't require the full brainstorming workflow.

## Overview

The full brainstorming workflow (`devkit.brainstorm`) is comprehensive but can be overkill for:
- Bug fixes with clear solutions
- Small features with well-defined scope
- Changes affecting 1-3 files
- Straightforward additions to existing functionality

**Quick Spec** provides a streamlined 4-phase workflow vs. the 9-phase brainstorming workflow.

### Workflow Comparison

| Aspect | Quick Spec (this) | Full Brainstorming |
|--------|------------------|-------------------|
| Phases | 4 | 9 |
| Idea refinement | Single question | Multiple GATE phases |
| Approach exploration | Skipped | 2-3 approaches presented |
| Context exploration | Simple git log check | Optional subagent exploration |
| Document generation | Direct (no subagent) | Document-generator subagent |
| Output format | Minimal spec | Full functional spec |

### When to Use Quick Spec

✅ **Use Quick Spec when:**
- Bug fix with obvious solution
- Small addition to existing feature
- Change affects ≤3 files
- Well-understood technical context
- Time pressure for quick turnaround

❌ **Use full brainstorming when:**
- New feature from scratch
- Complex business logic
- Multiple stakeholders involved
- Significant architecture decisions
- Requirements are vague or evolving

## Usage

```bash
# Quick spec for a bug fix
/developer-kit:devkit.quick-spec Fix race condition in order processing

# Quick spec for small feature
/developer-kit:devkit.quick-spec Add password reset link expiration

# Quick spec with language hint
/developer-kit:devkit.quick-spec --lang=spring Add API rate limiting
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `description` | No | Description of the bug fix or small feature |
| `--lang` | No | Target language/framework hint |

---

## Core Principles

- **Direct and efficient**: Skip unnecessary exploration for straightforward changes
- **Still structured**: Maintain spec quality even in minimal format
- **Evidence-based**: Use git history and codebase analysis
- **User confirmation**: Still validate key aspects with user
- **Proper next steps**: Recommend appropriate workflow continuation

---

## Phase 1: Quick Context

**Goal**: Gather essential context rapidly

**Actions**:

1. Create todo list with all phases
2. Parse $ARGUMENTS for description and optional `--lang`
3. Quick codebase exploration:
   - Check recent git log (last 10-20 commits) for relevant context
   - Identify affected files (grep for relevant terms if needed)
   - Check if related feature exists
4. If description unclear, ask:
   - What is the problem/feature?
   - What files are affected?

---

## Phase 2: Problem + Solution Checkpoint

**Goal**: Define and validate the approach in one step

**Actions**:

1. **Define the problem**: Summarize what needs fixing/adding

2. **Propose the solution**: Brief technical approach

3. If the problem/solution pair is non-obvious, use AskUserQuestion to confirm:
   ```
   Problem: [brief description]
   Solution: [brief technical approach]
   Affected Files: [list 1-3 files]

   Options:
   - "Approve and generate spec"
   - "Refine approach"
   - "Switch to full brainstorming"
   ```

4. If the change is straightforward and low-risk, proceed directly to Phase 3 after summarizing the chosen approach

---

## Phase 3: Generate Minimal Spec

**Goal**: Create lightweight specification directly

**Actions**:

1. Generate unique spec ID (same as brainstorming):
   - Count existing folders in `docs/specs/`
   - Create slug from feature name
   - Format: `NNN-feature-slug`

2. Create spec folder: `docs/specs/[id]/`

3. **Create user-request.md**:
   ```markdown
   # User Request

   **Original Input**: [description]

   **Type**: Bug Fix / Small Feature

   **Affected Files**: [list]
   ```

4. **Create minimal spec file** (`YYYY-MM-DD--feature-name.md`):
   ```markdown
   # [Feature Name] - Quick Spec

   **Type**: Bug Fix / Small Feature
   **Date**: [current date]
   **Status**: Draft

   ## Problem

   [One paragraph description of the issue or feature]

   ## Solution

   [One paragraph technical approach]

   ## Acceptance Criteria

   - [ ] [Criterion 1]
   - [ ] [Criterion 2]
   - [ ] [Criterion 3] (max 4 criteria for quick specs)

   ## Affected Files

   - [File path 1] - [change description]
   - [File path 2] - [change description]
   - [File path 3] - [change description]

   ## Out of Scope

   - [Any explicitly excluded items]
   ```

5. Create `decision-log.md` with DEC-001:
   ```markdown
   # Decision Log: [Feature Name]

   | ID | Date | Task | Decision | Alternatives | Impact | Decided By |
   |----|------|------|----------|--------------|--------|------------|

   ## DEC-001: Quick Spec Approach
   - **Date**: [current date]
   - **Task**: Quick Spec Generation
   - **Phase**: Approach Selection
   - **Context**: [Why quick spec was chosen]
   - **Decision**: Use minimal spec format
   - **Alternatives Considered**: Full brainstorming (not needed for this scope)
   - **Impact**: Streamlined documentation, faster turnaround
   - **Decided By**: user
   ```

---

## Phase 4: Next Step Recommendation

**Goal**: Guide user to appropriate next command

**Actions**:

1. Analyze acceptance criteria count:
   - **1-2 criteria**: Recommend direct implementation
   - **3-4 criteria**: Recommend task generation
   - **5+ criteria**: Suggest reconsidering if this should be a quick spec

2. **Use AskUserQuestion tool to present recommendation**:
   ```
   Based on acceptance criteria count (N), recommend:

   Options:
   - "Generate task list" (recommended for 3+ criteria)
   - "Implement directly" (for 1-2 criteria, skip tasks)
   - "Switch to full spec" (if criteria > 4, reconsider scope)
   ```

3. Include pre-filled commands:
   ```bash
   # For task generation:
   /developer-kit:devkit.spec-to-tasks --lang=[language] docs/specs/[id]/

   # For direct implementation:
   /developer-kit:devkit.feature-development --lang=[language] "Quick implement: [brief description]"
   ```

---

## Phase 5: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
   - **Type**: Bug Fix / Small Feature
   - **Problem/Solution**: Brief description
   - **Acceptance Criteria**: N criteria defined
   - **Affected Files**: List of files
   - **Spec Created**: `docs/specs/[id]/YYYY-MM-DD--feature-name.md`
   - **Decision Log**: `docs/specs/[id]/decision-log.md`
   - **Recommended Next Step**: Based on criteria count

---

## Examples

### Example 1: Bug Fix

```bash
/developer-kit:devkit.quick-spec Fix memory leak in user session cleanup
```

Output:
- Type: Bug Fix
- Affected Files: `src/main/java/com/example/SessionCleanup.java`
- Acceptance Criteria: 2 criteria
- Next Step: Direct implementation

### Example 2: Small Feature

```bash
/developer-kit:devkit.quick-spec Add request timeout configuration
```

Output:
- Type: Small Feature
- Affected Files: 2 files
- Acceptance Criteria: 3 criteria
- Next Step: Generate task list

### Example 3: With Language

```bash
/developer-kit:devkit.quick-spec --lang=python Add logging to payment service
```

---

## Todo Management

Maintain todo list:

```
[ ] Phase 1: Quick Context
[ ] Phase 2: Problem + Solution
[ ] Phase 3: Generate Minimal Spec
[ ] Phase 4: Next Step Recommendation
[ ] Phase 5: Summary
```

---

## Comparison with Full Brainstorming

| Aspect | Quick Spec | Full Brainstorming |
|--------|-----------|-------------------|
| **Time to complete** | ~5-10 minutes | ~15-30 minutes |
| **GATE phases** | 1 (Phase 2) | 5 (Phases 2, 3, 4, 5, 8) |
| **Approach exploration** | None (user confirms directly) | 2-3 approaches presented |
| **Context gathering** | Git log + file check | Optional subagent exploration |
| **Document generation** | Direct write | Document-generator subagent |
| **Spec format** | Minimal (key sections only) | Comprehensive (all sections) |
| **Decision log** | DEC-001 (approach only) | Multiple entries accumulated |
| **Best for** | Bug fixes, small changes | New features, complex logic |

---

## When to Upgrade to Full Brainstorming

**Signals to suggest full brainstorming instead of quick spec:**

1. **Requirements unclear**: User can't describe problem/solution clearly
2. **Multiple stakeholders**: Different perspectives needed
3. **Architecture impact**: Change affects system design
4. **Large scope**: Affects >5 files or multiple modules
5. **Business complexity**: Requires business rule analysis
6. **User uncertainty**: User says "I'm not sure, let me think..."

**How to switch:**
- During Phase 2 (Problem + Solution), if issues detected:
  - Add option "Switch to full brainstorming" to AskUserQuestion
  - If chosen, invoke `/developer-kit:devkit.brainstorm [original description]`
  - Delete partial quick-spec artifacts

---

## Notes

- Quick Spec maintains quality while being efficient
- Decision-log.md still created for audit trail consistency
- User can still request full brainstorming if needed
- Spec format is minimal but structured for consistency
- Integration with rest of SDD workflow is maintained
