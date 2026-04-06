---
id: TASK-003
title: "Update existing examples"
spec: docs/specs/003-gemini-3-flash-pro-support/2026-04-06--gemini-3-flash-pro-support.md
lang: general
dependencies: [TASK-001, TASK-002]
status: completed
reviewed_at: 2026-04-06T09:55:31Z
completed_date: 2026-04-06
cleanup_date: 2026-04-06
---

# TASK-003: Update existing examples

**Functional Description**: Replace all existing `gemini-2.5-pro` model references in the Examples section with appropriate `gemini-3-flash` or `gemini-3-pro` models based on task complexity.

## Acceptance Criteria

- [ ] All `gemini-2.5-pro` references are removed from Examples section
- [ ] Quick/analysis examples use `gemini-3-flash`
- [ ] Complex/production examples use `gemini-3-pro`
- [ ] Example commands remain functional and correct
- [ ] At least 3 examples are updated (from current 3 examples)

## Definition of Ready (DoR)

Before starting this task, ensure:
- [ ] TASK-001 is completed (frontmatter updated).
- [ ] TASK-002 is completed (Model Selection Guide provides context for model choices).
- [ ] Current examples in SKILL.md are reviewed.
- [ ] Model selection criteria are understood from TASK-002.
- [ ] Target file is accessible: `plugins/developer-kit-tools/skills/gemini/SKILL.md`

## Technical Context (from Codebase Analysis)

- **Existing Patterns to Follow**: Codex skill examples with model-specific usage patterns
- **APIs to Integrate With**: Gemini CLI with `-m, --model` flag
- **Shared Components**: None
- **Conventions**:
  - Example format: `gemini -p "<prompt>" -m <model-id>`
  - Model selection based on task complexity
  - Quick tasks: `gemini-3-flash`
  - Complex tasks: `gemini-3-pro`
  - Include approval mode where appropriate
- **Architecture Reference**: Python stdlib scripts, local filesystem (not applicable for this doc task)
- **Domain Terms**: Examples section, Model Selection Criteria (from TASK-002), Task Complexity (quick vs complex)

## Implementation Details (File names only, no code)

**Files to Modify**:
- `plugins/developer-kit-tools/skills/gemini/SKILL.md` - Update Examples section to replace gemini-2.5-pro with gemini-3-flash or gemini-3-pro

**Files to Create**:
- None

## Test Instructions

This section describes **what** to test, not **how** to implement test code.

**1. Mandatory Validation Checks**:
   - `SKILL.md` (Examples section):
     - [ ] Verify that NO `gemini-2.5-pro` references exist
     - [ ] Verify that quick/analysis examples use `gemini-3-flash`
     - [ ] Verify that complex/production examples use `gemini-3-pro`
     - [ ] Verify that all example commands are syntactically correct
     - [ ] Verify that at least 3 examples exist

**2. Model Selection Validation**:
   - Example 1 (Large codebase security review):
     - [ ] Verify model choice aligns with task complexity
     - [ ] If analysis-heavy: should use `gemini-3-flash` for speed
   - Example 2 (Documentation synthesis):
     - [ ] Verify model choice aligns with task complexity
     - [ ] If production-quality output: should use `gemini-3-pro`
   - Example 3 (Structured output):
     - [ ] Verify model choice aligns with task complexity
     - [ ] If quick automation: should use `gemini-3-flash`

**3. Consistency Checks**:
   - Examples vs Model Selection Guide (from TASK-002):
     - [ ] Verify that model choices in examples match selection guide criteria
     - [ ] Verify that practical guidance is consistent

**Test Acceptance Criteria**:
   - [ ] All validation checks above are completed and pass.
   - [ ] No gemini-2.5-pro references remain.
   - [ ] Model choices are appropriate for task complexity.

## Definition of Done (DoD)

This task is complete when:
- [ ] All `gemini-2.5-pro` references are removed from Examples section.
- [ ] Model choices align with task complexity (Flash for quick, Pro for complex).
- [ ] Example commands remain functional and correct.
- [ ] Model choices are consistent with Model Selection Guide.
- [ ] At least 3 examples exist with appropriate model assignments.

**Dependencies**: TASK-001, TASK-002

**Implementation Command**:
/specs:task-implementation --lang=general --task="docs/specs/003-gemini-3-flash-pro-support/tasks/TASK-003.md"

## Cleanup Summary

- Files cleaned:
  - plugins/developer-kit-tools/skills/gemini/SKILL.md — Examples updated to use `gemini-3-flash` and `gemini-3-pro`; removed all `gemini-2.5-pro` references.
- Changes made:
  - Replaced model identifiers in Examples section; verified command syntax.
- Verification:
  - Review report: tasks/TASK-003--review.md (PASS).
  - Repository search confirms no occurrences of `gemini-2.5-pro`.
- Notes:
  - No code changes required beyond documentation updates.
- Completed by: Copilot CLI
- Completed date: 2026-04-06
