---
id: TASK-001
title: "Update frontmatter and description"
spec: docs/specs/003-gemini-3-flash-pro-support/2026-04-06--gemini-3-flash-pro-support.md
lang: general
dependencies: []
status: done
reviewed_at: 2026-04-06
completed_at: 2026-04-06
---

# TASK-001: Update frontmatter and description

**Functional Description**: Update the Gemini skill frontmatter to mention Gemini 3.0 Flash and Pro model support, following the Codex skill description pattern.

## Acceptance Criteria

- [x] Frontmatter description mentions Gemini 3.0 Flash and Pro support
- [x] Description follows Codex pattern: capabilities + use cases + trigger phrases
- [x] Trigger phrases include "use gemini 3 flash" and "use gemini 3 pro"
- [x] Description remains under 1024 characters
- [x] Allowed tools field remains unchanged

## Definition of Ready (DoR)

Before starting this task, ensure:
- [ ] No prerequisite tasks are pending.
- [ ] Current Gemini skill frontmatter structure is understood.
- [ ] Codex skill frontmatter pattern is reviewed for consistency.
- [ ] Target file is accessible: `plugins/developer-kit-tools/skills/gemini/SKILL.md`

## Technical Context (from Codebase Analysis)

- **Existing Patterns to Follow**: Codex skill frontmatter structure with dual-purpose description (what it does AND when to use it)
- **APIs to Integrate With**: None (documentation-only task)
- **Shared Components**: None
- **Conventions**:
  - Frontmatter YAML format with `---` delimiters
  - Description pattern: "Provides [capability] for [use case], including [key features]. Use when [specific scenarios]. Triggers on [trigger phrases]."
  - Trigger phrases for discoverability
  - Character limit: 1024 characters for description
- **Architecture Reference**: Python stdlib scripts, local filesystem (not applicable for this doc task)
- **Domain Terms**: Skill (SKILL.md), Frontmatter (YAML metadata), Trigger Phrases (discoverability keywords)

## Implementation Details (File names only, no code)

**Files to Modify**:
- `plugins/developer-kit-tools/skills/gemini/SKILL.md` - Update frontmatter description to include Gemini 3.0 Flash and Pro support

**Files to Create**:
- None

## Test Instructions

This section describes **what** to test, not **how** to implement test code.

**1. Mandatory Validation Checks**:
   - `SKILL.md` (frontmatter section):
     - [ ] Verify that YAML frontmatter is valid (can be parsed)
     - [ ] Verify that description mentions "Gemini 3 Flash" and "Gemini 3 Pro"
     - [ ] Verify that description length is under 1024 characters
     - [ ] Verify that trigger phrases include "use gemini 3 flash" and "use gemini 3 pro"
     - [ ] Verify that allowed-tools field remains `Bash, Read, Write`

**2. Consistency Checks**:
   - `SKILL.md` vs Codex `SKILL.md`:
     - [ ] Verify that description pattern matches Codex format (capabilities + use cases + triggers)
     - [ ] Verify that structure is consistent with Codex skill

**3. Edge Cases and Error Conditions**:
   - [ ] Verify that special characters in description don't break YAML parsing
   - [ ] Verify that description is not truncated or malformed

**Test Acceptance Criteria**:
   - [ ] All validation checks above are completed and pass.
   - [ ] Frontmatter is valid YAML and includes required mentions.

## Definition of Done (DoD)

This task is complete when:
- [ ] Frontmatter description is updated with Gemini 3.0 Flash and Pro support.
- [ ] Description follows Codex pattern with trigger phrases.
- [ ] YAML frontmatter is valid and parseable.
- [ ] Description length is under 1024 characters.
- [ ] Consistency with Codex skill structure is maintained.

**Dependencies**: None

**Implementation Command**:
/specs:task-implementation --lang=general --task="docs/specs/003-gemini-3-flash-pro-support/tasks/TASK-001.md"
