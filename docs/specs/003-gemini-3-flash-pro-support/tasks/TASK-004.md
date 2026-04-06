---
id: TASK-004
title: "Add Flash-specific examples"
spec: docs/specs/003-gemini-3-flash-pro-support/2026-04-06--gemini-3-flash-pro-support.md
lang: general
dependencies: [TASK-002]
---

# TASK-004: Add Flash-specific examples

**Functional Description**: Add at least 3 new examples specifically demonstrating Gemini 3 Flash usage for speed-focused tasks (quick iterations, boilerplate generation, cost-effective analysis).

## Acceptance Criteria

- [x] At least 3 new examples added for `gemini-3-flash`
- [x] Examples demonstrate speed-focused use cases (quick iterations, boilerplate, cost-effective tasks)
- [x] Examples follow Codex skill pattern structure
- [x] Examples are distinct and not duplicating existing examples
- [x] Each example includes model flag `-m gemini-3-flash`
- [x] Examples are practical and realistic for CLI usage

**Implementation Note:** Added three Flash-specific examples to `plugins/developer-kit-tools/skills/gemini/SKILL.md` and committed the change (commit: d1e2c02).
## Definition of Ready (DoR)

Before starting this task, ensure:
- [x] TASK-002 is completed (Model Selection Guide provides Flash characteristics reference).
- [ ] Codex skill examples are reviewed for pattern reference.
- [ ] Gemini 3 Flash characteristics are understood (speed, fast iterations, cost-effective).
- [ ] Target file is accessible: `plugins/developer-kit-tools/skills/gemini/SKILL.md`

## Technical Context (from Codebase Analysis)

- **Existing Patterns to Follow**: Codex skill examples with practical use cases and command patterns
- **APIs to Integrate With**: Gemini CLI with `-m gemini-3-flash` flag
- **Shared Components**: None
- **Conventions**:
  - Example format: `### Example N: [Descriptive title]` followed by code block
  - Command pattern: `gemini -p "<prompt>" -m gemini-3-flash [additional flags]`
  - Include approval mode where appropriate: `--approval-mode plan` for analysis
  - Practical, realistic prompts
  - Clear use case titles
- **Architecture Reference**: Python stdlib scripts, local filesystem (not applicable for this doc task)
- **Domain Terms**: Flash (speed-focused), Quick Iterations (fast prototyping), Cost-effective (efficiency)

## Implementation Details (File names only, no code)

**Files to Modify**:
- `plugins/developer-kit-tools/skills/gemini/SKILL.md` - Add at least 3 new Flash-specific examples to Examples section

**Files to Create**:
- None

## Test Instructions

This section describes **what** to test, not **how** to implement test code.

**1. Mandatory Validation Checks**:
   - `SKILL.md` (Examples section - Flash examples):
     - [ ] Verify that at least 3 NEW examples are added (not counting updates to existing examples)
     - [ ] Verify that all Flash examples include `-m gemini-3-flash` flag
     - [ ] Verify that examples demonstrate speed-focused use cases
     - [ ] Verify that examples follow Codex pattern structure (### Example N: title + code block)
     - [ ] Verify that examples are distinct and not duplicative

**2. Content Verification**:
   - Example 1 (Quick boilerplate generation):
     - [ ] Verify that use case is speed-focused (e.g., "generate boilerplate code")
     - [ ] Verify that prompt emphasizes speed/efficiency
     - [ ] Verify that model flag is `-m gemini-3-flash`
   - Example 2 (Cost-effective analysis):
     - [ ] Verify that use case is cost-effective (e.g., "quick security scan")
     - [ ] Verify that prompt emphasizes efficiency
     - [ ] Verify that approval mode is appropriate (e.g., `--approval-mode plan`)
   - Example 3 (Fast iteration):
     - [ ] Verify that use case is fast iteration (e.g., "prototype this feature")
     - [ ] Verify that prompt emphasizes iteration speed
     - [ ] Verify that command includes appropriate flags

**3. Consistency Checks**:
   - Examples vs Model Selection Guide (from TASK-002):
     - [ ] Verify that Flash examples align with "speed, fast iterations, cost-effective" characteristics
     - [ ] Verify that practical use cases match selection tips

**Test Acceptance Criteria**:
   - [ ] All validation checks above are completed and pass.
   - [ ] At least 3 new Flash-specific examples exist.
   - [ ] Examples demonstrate appropriate Flash use cases.

## Definition of Done (DoD)

This task is complete when:
- [x] At least 3 new Flash-specific examples are added.
- [x] Examples demonstrate speed-focused use cases (boilerplate, cost-effective, fast iterations).
- [x] Examples follow Codex pattern structure exactly.
- [x] All examples include `-m gemini-3-flash` flag.
- [x] Examples align with Model Selection Guide characteristics.

**Dependencies**: TASK-002

**Implementation Command**:
/specs:task-implementation --lang=general --task="docs/specs/003-gemini-3-flash-pro-support/tasks/TASK-004.md"
