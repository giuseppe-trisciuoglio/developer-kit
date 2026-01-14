---
description: Guided code refactoring with deep codebase understanding, compatibility options, and comprehensive verification
argument-hint: [ --lang=java|spring|typescript|nestjs|react|general ] [ --scope=file|module|feature ] [ refactor-description ]
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Code Refactoring

You are helping a developer refactor existing code. Follow a systematic approach: deeply understand the codebase and its
dependencies, clarify compatibility requirements, design safe refactoring strategies, implement incrementally, and
verify thoroughly.

## Language/Framework Selection

Parse $ARGUMENTS to detect the optional `--lang` parameter:

- `--lang=spring` or `--lang=java`: Use Java/Spring Boot specialized agents
- `--lang=typescript` or `--lang=ts`: Use TypeScript specialized agents
- `--lang=nestjs`: Use NestJS specialized agents
- `--lang=react`: Use React frontend specialized agents
- `--lang=aws`: Use AWS specialized agents (architecture, CloudFormation, IaC)
- `--lang=general` or no flag: Use general-purpose agents (default)

## Scope Selection

Parse $ARGUMENTS to detect the optional `--scope` parameter:

- `--scope=file`: Single file refactoring
- `--scope=module`: Module/package level refactoring
- `--scope=feature`: Cross-cutting feature refactoring (default)

**Agent Mapping by Language:**

| Phase               | General (default)                  | Java/Spring Boot (`--lang=spring` or `--lang=java`)    | TypeScript (`--lang=typescript` or `--lang=ts`)      | NestJS (`--lang=nestjs`)                             | React (`--lang=react`)                            | AWS (`--lang=aws`)                             |
|---------------------|------------------------------------|--------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|---------------------------------------------------|------------------------------------------------|
| Deep Exploration    | `developer-kit:code-explorer`      | `developer-kit:spring-boot-backend-development-expert` | `developer-kit:code-explorer`                        | `developer-kit:nestjs-backend-development-expert`    | `developer-kit:react-frontend-development-expert` | `developer-kit:aws-solution-architect-expert`  |
| Refactoring Expert  | `developer-kit:refactor-expert`    | `developer-kit:java-refactor-expert`                   | `developer-kit:typescript-refactor-expert`           | `developer-kit:typescript-refactor-expert`           | `developer-kit:typescript-refactor-expert`        | `developer-kit:refactor-expert`                |
| Architecture Review | `developer-kit:software-architect` | `developer-kit:java-software-architect-review`         | `developer-kit:typescript-software-architect-review` | `developer-kit:typescript-software-architect-review` | `developer-kit:react-software-architect-review`   | `developer-kit:aws-solution-architect-expert`  |
| Code Review         | `developer-kit:code-reviewer`      | `developer-kit:spring-boot-code-review-expert`         | `developer-kit:code-reviewer`                        | `developer-kit:nestjs-code-review-expert`            | `developer-kit:code-reviewer`                     | `developer-kit:aws-architecture-review-expert` |

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Changes**: !`git diff --name-only HEAD~1`

## Core Principles

- **Backward compatibility first**: Always clarify if breaking changes are acceptable before proceeding
- **Deep understanding required**: Refactoring requires comprehensive knowledge of dependencies, usages, and side
  effects
- **Incremental changes**: Prefer small, verifiable changes over large rewrites
- **Test coverage awareness**: Understand existing test coverage before modifying code
- **Structured user interaction**: Use the AskUserQuestion tool for all decision points
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Refactoring Discovery

**Goal**: Understand what needs to be refactored and why

**Initial request**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases
2. Parse the refactoring request to understand:
    - Which code area needs refactoring?
    - What is the motivation? (code smell, performance, maintainability, readability, design pattern)
    - What is the expected outcome?
3. If unclear, ask user for clarification

---

## Phase 2: Compatibility Requirements

**Goal**: Establish compatibility constraints before any exploration

**CRITICAL**: This phase determines the entire refactoring strategy. DO NOT SKIP.

**Actions**:

1. **Use the AskUserQuestion tool to ask the user about compatibility requirements**:

   Present these options clearly:

   **Breaking Changes Policy:**
    - **A) Strictly Backward Compatible**: No breaking changes allowed. All public APIs, method signatures, return
      types, and behaviors must remain unchanged. Existing clients/consumers must continue working without
      modifications.
    - **B) Breaking Changes Allowed**: Breaking changes are acceptable. Can modify public APIs, change method
      signatures, remove deprecated code, and restructure interfaces. Consumers may need updates.
    - **C) Internal Only**: Refactoring internal/private implementation only. Public API remains unchanged, but internal
      structure can be completely redesigned.

   **Additional Questions:**
    - Are there external consumers of this code (other services, libraries, APIs)?
    - Is there a deprecation strategy needed for phased migration?
    - Are there specific contracts (interfaces, DTOs, database schemas) that must be preserved?

2. Document the compatibility decision clearly in the todo list
3. This decision will guide all subsequent phases

---

## Phase 3: Deep Codebase Exploration

**Goal**: Build comprehensive understanding of the code to be refactored and ALL its dependencies

**CRITICAL**: Refactoring requires deeper exploration than feature development. You must understand:

- All usages of the code to be refactored
- All dependencies (incoming and outgoing)
- Test coverage and test patterns
- Integration points with other modules

**Actions**:

### Step 3.1: Code Structure Analysis

1. Use the Task tool to launch an explorer subagent to map the code structure:

```
Task(
  description: "Map code structure for refactoring",
  prompt: "Analyze [code area] comprehensively:
    1. Map all classes, interfaces, and their relationships
    2. Identify all public APIs and their signatures
    3. Find all dependencies (what this code uses)
    4. Document any design patterns currently in use
    5. Return a prioritized list of files to read for deep understanding",
  subagent_type: "[appropriate explorer agent]"
)
```

### Step 3.2: Usage and Dependency Analysis

2. Use the Task tool to launch a second exploration focused on usages:

```
Task(
  description: "Find all usages and consumers",
  prompt: "Find ALL usages of [code to refactor]:
    1. Search for all import statements referencing this code
    2. Find all method calls to public APIs
    3. Identify all classes extending or implementing interfaces from this code
    4. Look for reflection-based usages (especially in Spring/DI contexts)
    5. Check for configuration references (XML, YAML, properties)
    6. Return a complete list of dependent files",
  subagent_type: "[appropriate explorer agent]"
)
```

### Step 3.3: Test Coverage Analysis

3. Use the Task tool to analyze test coverage:

```
Task(
  description: "Analyze test coverage",
  prompt: "Analyze test coverage for [code to refactor]:
    1. Find all unit tests covering this code
    2. Find all integration tests involving this code
    3. Identify test patterns and conventions used
    4. Note any untested code paths
    5. Return list of test files to read",
  subagent_type: "[appropriate explorer agent]"
)
```

4. Read ALL files identified by agents to build complete understanding
5. Create a dependency graph summary showing:
    - Code to be refactored
    - Direct consumers (files that import/use this code)
    - Indirect consumers (files that use the consumers)
    - Test files

---

## Phase 4: Refactoring Strategy

**Goal**: Design the refactoring approach based on compatibility requirements

**Actions**:

1. Use the Task tool to launch a refactoring expert subagent:

```
Task(
  description: "Design refactoring strategy",
  prompt: "Design a refactoring strategy for [code area] with these constraints:
    - Compatibility: [backward compatible / breaking changes allowed / internal only]
    - Current issues: [identified problems]
    - Target state: [desired outcome]
    
    Provide:
    1. Recommended refactoring pattern (Extract, Rename, Move, Replace, etc.)
    2. Step-by-step implementation plan
    3. Risk assessment for each step
    4. Rollback strategy if issues arise
    5. Migration guide if breaking changes are involved",
  subagent_type: "[appropriate refactor agent]"
)
```

2. If breaking changes are allowed, also design a deprecation/migration strategy
3. Present the strategy to user with clear trade-offs
4. **Use the AskUserQuestion tool to get user approval before proceeding**

---

## Phase 5: Pre-Refactoring Verification

**Goal**: Ensure the codebase is in a known-good state before making changes

**Actions**:

1. Run existing tests to establish baseline:
    - Unit tests for the affected code
    - Integration tests if applicable
    - Record any pre-existing failures (do not fix them)

2. Create a verification checklist based on compatibility requirements:
    - For backward compatible: List all public API signatures that must be preserved
    - For breaking changes: Document all breaking changes for communication
    - For internal only: Confirm public API boundaries

3. Document the current behavior that must be preserved or intentionally changed

---

## Phase 6: Implementation

**Goal**: Execute the refactoring incrementally

**DO NOT START WITHOUT USER APPROVAL FROM PHASE 4**

**Actions**:

1. Implement changes in small, verifiable increments:
    - Each increment should be independently testable
    - Commit logical units of work mentally (describe what would be committed)

2. Follow the implementation order from the strategy:
    - Start with the least risky changes
    - Build up to more significant modifications
    - Keep public APIs stable until internal refactoring is complete (for backward compatible)

3. Update todos after each significant change

4. For backward compatible refactoring:
    - Use adapter patterns if needed
    - Add deprecation annotations to old methods before removing
    - Ensure all existing tests still pass

5. For breaking changes:
    - Update all identified consumers
    - Update all affected tests
    - Document migration steps

---

## Phase 7: Comprehensive Verification

**Goal**: Thoroughly verify the refactoring preserves behavior and improves quality

**CRITICAL**: This is an extended verification phase with multiple checks.

### Step 7.1: Automated Test Verification

1. Run ALL tests that were passing before:
    - Unit tests for refactored code
    - Unit tests for dependent code
    - Integration tests

2. Compare results with pre-refactoring baseline:
    - All previously passing tests must still pass
    - No new test failures introduced

### Step 7.2: Static Analysis Verification

1. Run linters and static analysis tools:
    - Check for new warnings or errors
    - Verify code style compliance
    - Check for common issues (null safety, type safety, etc.)

### Step 7.3: Code Review Verification

1. Use the Task tool to launch a code reviewer subagent:

```
Task(
  description: "Review refactored code",
  prompt: "Review the refactored code in [files] focusing on:
    1. Does the refactoring achieve its stated goal?
    2. Is the new code simpler and more maintainable?
    3. Are there any regressions in code quality?
    4. Does it follow project conventions?
    5. Are there any missed opportunities for improvement?
    6. Specific for backward compatible: Are all public APIs preserved correctly?
    7. Specific for breaking changes: Are all consumers properly updated?",
  subagent_type: "[appropriate code review agent]"
)
```

### Step 7.4: Architecture Verification (for module/feature scope)

2. Use the Task tool to launch an architecture reviewer:

```
Task(
  description: "Verify architectural integrity",
  prompt: "Verify the architectural integrity after refactoring:
    1. Are module boundaries respected?
    2. Is the dependency direction correct?
    3. Are SOLID principles followed?
    4. Is the abstraction level appropriate?
    5. Any circular dependencies introduced?",
  subagent_type: "[appropriate architect agent]"
)
```

### Step 7.5: Manual Verification Points

3. Present to user for manual verification:
    - List of all changed files
    - Summary of behavioral changes (if any)
    - Any areas requiring manual testing

4. **Use the AskUserQuestion tool to ask user to confirm verification or report issues**

---

## Phase 8: Issue Resolution

**Goal**: Address any issues found during verification

**Actions**:

1. If issues were found:
    - Categorize by severity (blocking, important, minor)
    - Propose fixes for each issue
    - **Use the AskUserQuestion tool to ask user which issues to fix now vs later**

2. Implement approved fixes
3. Re-run verification for fixed areas
4. Repeat until all blocking issues are resolved

---

## Phase 9: Summary and Documentation

**Goal**: Document the refactoring for future reference

**Actions**:

1. Mark all todos complete
2. Provide comprehensive summary:
    - **What was refactored**: Original state and final state
    - **Why**: The motivation and benefits achieved
    - **Breaking changes** (if any): List of API changes, migration steps
    - **Files modified**: Complete list with change descriptions
    - **Tests updated**: New or modified tests
    - **Verification results**: All checks passed
    - **Recommendations**: Follow-up refactoring opportunities

3. If breaking changes were made, provide:
    - Migration guide for consumers
    - Deprecation timeline if applicable
    - Communication template for stakeholders

---

## Usage Examples

```bash
# Simple file refactoring (general agents)
/devkit.refactor --scope=file Extract utility methods from UserService

# Java/Spring Boot module refactoring
/devkit.refactor --lang=spring --scope=module Refactor repository layer to use specification pattern

# Breaking change refactoring with explicit scope
/devkit.refactor --lang=java Restructure payment module API for v2

# TypeScript refactoring
/devkit.refactor --lang=typescript Convert callbacks to async/await in data layer

# NestJS refactoring
/devkit.refactor --lang=nestjs Refactor authentication to use guards instead of middleware

# React component refactoring
/devkit.refactor --lang=react Extract shared hooks from dashboard components

# AWS infrastructure refactoring
/devkit.refactor --lang=aws Refactor monolithic CloudFormation template into nested stacks

# AWS architecture modernization
/devkit.refactor --lang=aws Migrate from EC2-based to serverless architecture

# Internal implementation refactoring
/devkit.refactor --scope=file Improve performance of search algorithm in SearchService
```

## Integration with Sub-agents

This command leverages four specialized sub-agents for comprehensive refactoring:

## Execution Instructions

**Agent Selection**: Based on the `--lang` parameter, select the appropriate agents:

### General Agents (default, or `--lang=general`)

- **Code Explorer**: `developer-kit:code-explorer`
- **Refactoring Expert**: `developer-kit:code-reviewer`
- **Software Architect**: `developer-kit:software-architect`
- **Code Reviewer**: `developer-kit:code-reviewer`

### Java/Spring Boot Agents (`--lang=spring` or `--lang=java`)

- **Code Explorer**: `developer-kit:spring-boot-backend-development-expert`
- **Refactoring Expert**: `developer-kit:java-refactor-expert`
- **Software Architect**: `developer-kit:java-software-architect-review`
- **Code Reviewer**: `developer-kit:spring-boot-code-review-expert`

### TypeScript Agents (`--lang=typescript` or `--lang=ts`)

- **Code Explorer**: `developer-kit:code-explorer`
- **Refactoring Expert**: `developer-kit:typescript-refactor-expert`
- **Software Architect**: `developer-kit:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:code-reviewer`

### NestJS Agents (`--lang=nestjs`)

- **Code Explorer**: `developer-kit:nestjs-backend-development-expert`
- **Refactoring Expert**: `developer-kit:typescript-refactor-expert`
- **Software Architect**: `developer-kit:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:nestjs-code-review-expert`

### React Agents (`--lang=react`)

- **Code Explorer**: `developer-kit:react-frontend-development-expert`
- **Refactoring Expert**: `developer-kit:typescript-refactor-expert`
- **Software Architect**: `developer-kit:react-software-architect-review`
- **Code Reviewer**: `developer-kit:code-reviewer`

### AWS Agents (`--lang=aws`)

- **Code Explorer**: `developer-kit:aws-solution-architect-expert`
- **Refactoring Expert**: `developer-kit:aws-cloudformation-devops-expert`
- **Software Architect**: `developer-kit:aws-solution-architect-expert`
- **Code Reviewer**: `developer-kit:aws-architecture-review-expert`

**Fallback**: If specialized agents are not available, fall back to `general-purpose` agent.

### Usage Pattern

```
// Exploration with multiple agents in parallel
Task(
  description: "Map code structure",
  prompt: "Analyze [code area] for refactoring...",
  subagent_type: "developer-kit:code-explorer"
)

Task(
  description: "Find all usages",
  prompt: "Find ALL usages of [code to refactor]...",
  subagent_type: "developer-kit:code-explorer"
)

// Sequential refactoring design
Task(
  description: "Design refactoring strategy",
  prompt: "Design a refactoring strategy...",
  subagent_type: "developer-kit:java-refactor-expert"
)

// Verification with multiple perspectives
Task(
  description: "Review refactored code",
  prompt: "Review the refactored code...",
  subagent_type: "developer-kit:spring-boot-code-review-expert"
)

Task(
  description: "Verify architectural integrity",
  prompt: "Verify the architectural integrity...",
  subagent_type: "developer-kit:java-software-architect-review"
)

// AWS agents (when --lang=aws)
Task(
  description: "Analyze AWS architecture for refactoring",
  prompt: "Analyze the current AWS architecture and identify refactoring opportunities",
  subagent_type: "developer-kit:aws-solution-architect-expert"
)

Task(
  description: "Refactor CloudFormation templates",
  prompt: "Design and implement refactored CloudFormation templates with modular structure",
  subagent_type: "developer-kit:aws-cloudformation-devops-expert"
)

Task(
  description: "Review refactored AWS architecture",
  prompt: "Review the refactored architecture against Well-Architected Framework",
  subagent_type: "developer-kit:aws-architecture-review-expert"
)
```

### Important Notes

- Sub-agents are automatically discovered from project agents directory
- Each sub-agent operates with its own context window
- Multiple sub-agents can be launched in parallel for exploration
- The main Claude maintains control and coordination of the overall process
- Refactoring requires more thorough exploration than feature development

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Refactoring Discovery
[ ] Phase 2: Compatibility Requirements
[ ] Phase 3: Deep Codebase Exploration
    [ ] Step 3.1: Code Structure Analysis
    [ ] Step 3.2: Usage and Dependency Analysis
    [ ] Step 3.3: Test Coverage Analysis
[ ] Phase 4: Refactoring Strategy
[ ] Phase 5: Pre-Refactoring Verification
[ ] Phase 6: Implementation
[ ] Phase 7: Comprehensive Verification
    [ ] Step 7.1: Automated Test Verification
    [ ] Step 7.2: Static Analysis Verification
    [ ] Step 7.3: Code Review Verification
    [ ] Step 7.4: Architecture Verification
    [ ] Step 7.5: Manual Verification Points
[ ] Phase 8: Issue Resolution
[ ] Phase 9: Summary and Documentation
```

Update the status as you progress through each phase.

---

**Note**: This command follows a rigorous approach to ensure safe, high-quality refactoring that respects compatibility
requirements and thoroughly verifies all changes.
