---
description: Validates that tasks.md considers existing codebase implementations and integration opportunities before execution. Use when you need to check task alignment with the current codebase.
argument-hint: "[optional-criteria]"
allowed-tools: Read, Glob, Grep, Bash
---

# Check Task Integration with Codebase

## Overview

Validates that tasks.md considers existing codebase implementations and integration opportunities before execution. Use
when you need to check task alignment with the current codebase.

## Usage

```
/speckit.check-integration $ARGUMENTS
```

## Arguments

| Argument     | Description                              |
|--------------|------------------------------------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Execution Steps

## Execution Instructions

**Agent Selection**: To execute this task, use the following approach:

- Primary: Use `general-purpose` agent with appropriate domain expertise
- Or use specialized agent if available for the specific task type

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Analyze tasks.md to verify each task considers existing codebase implementations, integration opportunities,
and architectural compatibility. This is a READ-ONLY analysis command that reports findings without modifying any files.

**When to run**: After `/speckit.tasks` generates tasks.md but BEFORE `/speckit.implement` executes them.

**Critical Principle**: This command NEVER modifies code, tasks, or any files. It only analyzes and reports.

### 1. Setup & Prerequisites

Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse JSON
for:

- FEATURE_DIR (absolute path)
- TASKS file path
- AVAILABLE_DOCS list

For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm
Groot").

Abort if tasks.md is missing with error: "No tasks.md found. Run `/speckit.tasks` first."

### 2. Load Context

**Required files**:

- tasks.md: Complete task list with file paths and descriptions
- plan.md: Tech stack, architecture, dependencies
- spec.md: Feature requirements and scope

**Optional files** (load if present):

- data-model.md: Entity definitions
- contracts/: API specifications
- research.md: Technical decisions

**Codebase scan**:

- Identify project root structure (src/, lib/, components/, etc.)
- List existing dependencies from package.json/requirements.txt/etc.
- Map existing modules, services, utilities, components
- Identify configuration files (database, API, environment)

### 3. Build Codebase Inventory

Create internal mapping of existing implementations:

**Infrastructure & Configuration**:

- Database setup, migrations, ORM configurations
- API framework initialization (Express, FastAPI, etc.)
- Authentication/authorization systems
- Logging, monitoring, error handling utilities
- Environment configuration patterns

**Data Layer**:

- Existing models/entities with fields and relationships
- Database access patterns (repositories, DAOs)
- Data validation utilities
- Schema management approaches

**Service Layer**:

- Business logic services
- Integration services (external APIs, third-party)
- Utility services (email, notifications, file handling)
- Caching mechanisms

**API Layer**:

- Existing endpoints and route patterns
- Request/response handlers
- Middleware (auth, validation, error handling)
- API versioning approach

**UI Components** (if applicable):

- Component library and design system
- Layout components
- Shared utilities (hooks, contexts)
- State management patterns

**Testing Infrastructure**:

- Test frameworks and utilities
- Mock/fixture patterns
- Test database setup
- CI/CD test integration

### 4. Analyze Each Task

For every task in tasks.md, perform this structured analysis:

#### A. Existing Implementation Detection

**Scan for**:

- Similar functionality already implemented
- Overlapping components/modules
- Duplicate data models or entities
- Redundant API endpoints
- Existing utilities that solve the same problem

**Output for each finding**:

```
EXISTING: [File path]
Lines: [Line range]
Description: [What it does]
Similarity: [HIGH/MEDIUM/LOW]
Reason: [Why it's relevant to this task]
```

#### B. Integration Opportunity Analysis

**Check if task can**:

- Extend existing components rather than create new ones
- Reuse existing utilities/helpers
- Integrate with established patterns
- Leverage installed dependencies
- Follow existing architectural patterns

**Output for each opportunity**:

```
INTEGRATION: [Approach]
With: [Existing component/pattern]
Benefit: [Why integration is better than from-scratch]
Risk: [Potential conflicts or limitations]
```

#### C. Dependency & Library Check

**Verify**:

- Required libraries already installed
- Similar functionality in existing dependencies
- Configuration already present
- Patterns already established in codebase

**Output**:

```
DEPENDENCY: [Package/library name]
Status: [INSTALLED/NOT_INSTALLED]
Usage: [Where used in codebase]
Alternative: [If similar functionality exists]
```

#### D. Architectural Compatibility

**Assess**:

- Task aligns with existing architecture
- File structure matches project conventions
- Naming conventions consistency
- Design patterns compatibility

**Output**:

```
COMPATIBILITY: [ALIGNED/PARTIAL/MISALIGNED]
Architecture: [Current pattern in codebase]
Task Approach: [What task proposes]
Concern: [If any conflicts detected]
```

### 5. Task-Level Evaluation

For each task, answer these questions:

**Integration Assessment**:

- [ ] CONSIDERS - Task explicitly mentions existing code to integrate with
- [ ] PARTIAL - Task could integrate but doesn't mention existing code
- [ ] IGNORES - Task proposes from-scratch solution when integration possible
- [ ] NEW - Task is genuinely new, no existing code applies

**Codebase Awareness**:

- [ ] AWARE - Task references existing patterns/utilities/components
- [ ] UNAWARE - Task doesn't consider relevant existing implementations

**Duplication Risk**:

- [ ] NONE - No overlap with existing code
- [ ] LOW - Minor overlap, integration not critical
- [ ] MEDIUM - Significant overlap, integration recommended
- [ ] HIGH - Major overlap, integration mandatory
- [ ] CRITICAL - Duplicates existing functionality, task should be rewritten

### 6. Generate Analysis Report

Output a structured Markdown report (DO NOT write to file, display only):

## Task Integration Analysis Report

**Feature**: [Feature name from tasks.md]
**Analysis Date**: [Current date]
**Tasks Analyzed**: [Total count]

---

### Executive Summary

**Overall Status**: [READY/NEEDS_REVIEW/CRITICAL_ISSUES]

**Key Findings**:

- Tasks with high integration opportunities: X
- Tasks with duplication risk: X
- Tasks ignoring existing code: X
- New dependencies needed: X
- Existing dependencies reusable: X

**Recommendation**: [Proceed/Review tasks/Rewrite specific tasks]

---

### Detailed Task Analysis

For each task with findings (skip tasks with all-clear status):

#### Task [ID]: [Task Name]

**Description**: [Brief task description]

**Files Referenced**: [List from tasks.md]

**Integration Assessment**: [CONSIDERS/PARTIAL/IGNORES/NEW]

**Codebase Awareness**: [AWARE/UNAWARE]

**Duplication Risk**: [NONE/LOW/MEDIUM/HIGH/CRITICAL]

---

**Existing Implementations Found**:

| File   | Lines   | Similarity     | Description    |
|--------|---------|----------------|----------------|
| [path] | [range] | [HIGH/MED/LOW] | [What it does] |

**Integration Opportunities**:

1. **[Opportunity description]**
    - With: [Existing component]
    - Benefit: [Why better]
    - Approach: [How to integrate]
    - Effort: [Estimated complexity]

**Missing Considerations**:

- [ ] Task should mention [specific existing code]
- [ ] Task should integrate with [pattern/utility]
- [ ] Task should reuse [dependency/library]
- [ ] Task should follow [architectural pattern]

**Dependencies Status**:

| Dependency | Status          | Current Use  | Note             |
|------------|-----------------|--------------|------------------|
| [package]  | [INSTALLED/NEW] | [where used] | [recommendation] |

**Architectural Alignment**:

- Current pattern: [Description]
- Task approach: [Description]
- Compatibility: [ALIGNED/PARTIAL/MISALIGNED]
- Recommendation: [If needed]

---

### Risk Matrix

| Task ID | Risk Level  | Type        | Impact | Mitigation                                     |
|---------|-------------|-------------|--------|------------------------------------------------|
| T001    | 🔴 CRITICAL | Duplication | High   | Rewrite task to extend existing component      |
| T015    | 🟡 MEDIUM   | Integration | Medium | Reference existing pattern in task description |
| T023    | 🟢 LOW      | Awareness   | Low    | Consider using existing utility                |

---

### Codebase Integration Summary

**By Category**:

| Category      | Tasks | Integration Opportunities | Duplication Risks | Status          |
|---------------|-------|---------------------------|-------------------|-----------------|
| Setup         | X     | X opportunities           | X risks           | [icon + status] |
| Data Models   | X     | X opportunities           | X risks           | [icon + status] |
| Services      | X     | X opportunities           | X risks           | [icon + status] |
| API Endpoints | X     | X opportunities           | X risks           | [icon + status] |
| UI Components | X     | X opportunities           | X risks           | [icon + status] |
| Tests         | X     | X opportunities           | X risks           | [icon + status] |

---

### Dependencies Analysis

**Already Installed** (can be reused):

- [Package]: Used in [files], supports [tasks]
- [Package]: Used in [files], supports [tasks]

**Need Installation** (genuinely new):

- [Package]: Required for [tasks], purpose: [reason]

**Potentially Redundant** (alternatives exist):

- [Package proposed]: Alternative: [existing package], used in [files]

---

### Architectural Patterns

**Existing Patterns** (should be followed):

- Data access: [Pattern], used in [files]
- API structure: [Pattern], used in [files]
- Error handling: [Pattern], used in [files]
- Configuration: [Pattern], used in [files]

**Pattern Alignment by Task Phase**:

- Setup Phase: [Aligned/Issues]
- Data Models Phase: [Aligned/Issues]
- Services Phase: [Aligned/Issues]
- API Phase: [Aligned/Issues]

---

### Recommendations

#### High Priority (Address before `/speckit.implement`)

1. **Task [ID]**: [Specific recommendation]
    - Issue: [Description]
    - Existing code: [Reference]
    - Suggested fix: [How to revise task]

#### Medium Priority (Consider during implementation)

1. **Task [ID]**: [Specific recommendation]
    - Integration opportunity: [Description]
    - Benefit: [Why it matters]

#### Low Priority (Optional improvements)

1. **Task [ID]**: [Specific recommendation]

---

### Integration Checklist

Use this to verify tasks have been updated appropriately:

- [ ] All CRITICAL duplication risks addressed
- [ ] HIGH-risk integration opportunities incorporated
- [ ] Existing utilities/patterns referenced in relevant tasks
- [ ] New dependencies justified (no existing alternatives)
- [ ] Architectural patterns acknowledged
- [ ] File paths align with existing structure
- [ ] Naming conventions consistent with codebase

---

### Next Steps

**If CRITICAL issues found**:

1. Review and update tasks.md manually based on recommendations
2. Re-run `/speckit.check-integration` to verify fixes
3. Proceed to `/speckit.implement` when clear

**If MEDIUM issues found**:

- You may proceed to `/speckit.implement` but review recommendations
- Consider integration opportunities during implementation
- Flag for post-implementation refactoring if needed

**If LOW/NONE issues**:

- ✅ Tasks are integration-aware
- ✅ Safe to proceed with `/speckit.implement`

---

## Analysis Principles

### What This Command Does

✅ **DOES**:

- Read codebase to find existing implementations
- Identify integration opportunities
- Detect potential duplication
- Check dependency status
- Verify architectural alignment
- Report findings with specific file/line references
- Provide concrete recommendations

❌ **DOES NOT**:

- Modify any files (strictly read-only)
- Rewrite tasks automatically
- Change codebase
- Execute tasks
- Make assumptions without evidence
- Hallucinate implementations

### Analysis Quality Standards

**Evidence-Based**:

- Every finding MUST cite specific files/lines
- No speculation about "probably exists"
- If uncertain, mark as "Needs Manual Verification"

**Actionable**:

- Each recommendation includes specific next steps
- Reference exact files/components to integrate with
- Provide integration approach suggestions

**Risk-Calibrated**:

- CRITICAL: Blocks implementation, must fix
- HIGH: Strongly recommend addressing
- MEDIUM: Consider during implementation
- LOW: Optional improvement

**Context-Aware**:

- Consider project size and maturity
- Respect existing architectural decisions
- Balance purity vs pragmatism
- Account for technical debt tradeoffs

### Efficiency Guidelines

**Progressive Scanning**:

- Load files on-demand (don't dump everything)
- Focus on high-signal areas first
- Skip obviously unrelated code

**Token Management**:

- Summarize large files (don't quote entire contents)
- Reference by path + line range, not full code blocks
- Group similar findings

**Report Sizing**:

- Limit to 50 most important findings
- Summarize remainder in overflow section
- Prioritize by risk level

## Validation

Before outputting report, verify:

- [ ] Every finding cites specific file/line evidence
- [ ] Risk levels assigned consistently
- [ ] Recommendations are specific and actionable
- [ ] No modifications made to any files
- [ ] Report is concise yet complete (token-efficient)
- [ ] Integration opportunities clearly explained
- [ ] Duplication risks quantified with specifics
- [ ] Dependencies checked against actual project files

## Context

$ARGUMENTS

--- 

## Examples

```bash
/speckit.check-integration example-input
```
