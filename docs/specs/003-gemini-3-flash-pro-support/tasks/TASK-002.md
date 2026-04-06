---
id: TASK-002
title: "Add Model Selection Guide section"
spec: docs/specs/003-gemini-3-flash-pro-support/2026-04-06--gemini-3-flash-pro-support.md
lang: general
dependencies: []
---

# TASK-002: Add Model Selection Guide section

**Functional Description**: Add a Model Selection Guide section to the Gemini skill following the Codex pattern, with a table comparing Gemini 3 Flash and Pro characteristics and selection tips.

## Acceptance Criteria

- [x] Model Selection Guide section is added after "Confirm Delegation Scope" step
- [x] Table includes columns: Model | Best For | Characteristics
- [x] Table includes **gemini-3-flash** and **gemini-3-pro** rows
- [x] Selection tips subsection includes practical guidance
- [x] Default model recommendation is explicitly stated
- [x] Format matches Codex skill pattern exactly

## Definition of Ready (DoR)

Before starting this task, ensure:
- [ ] No prerequisite tasks are pending.
- [ ] Codex skill Model Selection Guide section is reviewed for pattern reference.
- [ ] Gemini 3 Flash and Pro characteristics are understood from the spec.
- [ ] Target file is accessible: `plugins/developer-kit-tools/skills/gemini/SKILL.md`

## Technical Context (from Codebase Analysis)

- **Existing Patterns to Follow**: Codex skill Model Selection Guide section with table format and selection tips
- **APIs to Integrate With**: None (documentation-only task)
- **Shared Components**: None
- **Conventions**:
  - Table format: `| Model | Best For | Characteristics |`
  - Bold model names: `**model-name**`
  - Selection tips as bullet points
  - Default recommendation included
  - Section placed after Step 1 in Instructions
- **Architecture Reference**: Python stdlib scripts, local filesystem (not applicable for this doc task)
- **Domain Terms**: Model Selection Guide (Codex pattern), Selection Tips (practical guidance), Default Recommendation (fallback)

## Implementation Details (File names only, no code)

**Files to Modify**:
- `plugins/developer-kit-tools/skills/gemini/SKILL.md` - Add Model Selection Guide section after "Step 1: Confirm Delegation Scope"

**Files to Create**:
- None

## Test Instructions

This section describes **what** to test, not **how** to implement test code.

**1. Mandatory Validation Checks**:
   - `SKILL.md` (Model Selection Guide section):
     - [x] Verify that section exists after "Step 1: Confirm Delegation Scope"
     - [x] Verify that table has 3 columns: Model, Best For, Characteristics
     - [x] Verify that table includes **gemini-3-flash** row with "speed" characteristics
     - [x] Verify that table includes **gemini-3-pro** row with "power" characteristics
     - [x] Verify that selection tips subsection exists
     - [x] Verify that default model recommendation is stated

**2. Consistency Checks**:
   - `SKILL.md` vs Codex `SKILL.md`:
     - [ ] Verify that table format matches Codex exactly
     - [ ] Verify that selection tips format matches Codex
     - [ ] Verify that section placement matches Codex pattern

**3. Content Verification**:
   - [ ] Verify that Gemini 3 Flash description mentions speed, fast iterations, cost-effective
   - [ ] Verify that Gemini 3 Pro description mentions complex reasoning, power, production quality
   - [ ] Verify that selection tips are practical and actionable

**Test Acceptance Criteria**:
   - [ ] All validation checks above are completed and pass.
   - [ ] Model Selection Guide follows Codex pattern exactly.
   - [ ] Content accurately describes Flash vs Pro tradeoffs.

## Definition of Done (DoD)

This task is complete when:
- [x] Model Selection Guide section is added in correct location.
- [x] Table format matches Codex pattern exactly.
- [x] Selection tips provide practical guidance.
- [x] Default model recommendation is included.
- [x] Section structure is consistent with Codex skill.

**Dependencies**: None

**Implementation Command**:
/specs:task-implementation --lang=general --task="docs/specs/003-gemini-3-flash-pro-support/tasks/TASK-002.md"
