---
description: Provides guided bug fixing and debugging capability with systematic root cause analysis. Use when encountering bugs, errors, or unexpected behavior.
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] [ issue-description or error-message ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Fix & Debugging
## Overview

You are helping a developer fix a bug or debug an issue. Follow a systematic approach: understand the problem, trace the
root cause, design a minimal fix, then implement and verify.

## Usage

```bash
/developer-kit:devkit.fix-debugging [--lang=java|spring|typescript|nestjs|react|python|general] [issue-description or error-message]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Current Context

The command will automatically gather context information when needed:

- Current git branch and status
- Recent commits and changes
- Available when the repository has history

## Execution Instructions

**Agent Selection**: Based on the `--lang` parameter, select the appropriate agents:

## Integration with Sub-agents

This command leverages specialized sub-agents using the Task tool.

## Language/Framework Selection

Parse $ARGUMENTS to detect the optional `--lang` parameter:

- `--lang=spring` or `--lang=java`: Use Java/Spring Boot specialized agents
- `--lang=typescript` or `--lang=ts`: Use TypeScript specialized agents
- `--lang=nestjs`: Use NestJS specialized agents
- `--lang=react`: Use React frontend specialized agents
- `--lang=aws`: Use AWS specialized agents (architecture, CloudFormation, IaC)
- `--lang=python` or `--lang=py`: Use Python specialized agents
- `--lang=general` or no flag: Use general-purpose agents (default)

**Agent Mapping by Language:**

| Phase       | General (default)                          | Java/Spring Boot (`--lang=spring` or `--lang=java`) | TypeScript (`--lang=typescript` or `--lang=ts`)                 | NestJS (`--lang=nestjs`)                                        | React (`--lang=react`)                                     | AWS (`--lang=aws`)                                 | Python (`--lang=python` or `--lang=py`)                 |
|-------------|--------------------------------------------|-----------------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------|---------------------------------------------------------|
| Debugger    | `developer-kit:general-debugger`           | `developer-kit:general-debugger`                    | `developer-kit:general-debugger`                                | `developer-kit:general-debugger`                                | `developer-kit:general-debugger`                           | `developer-kit:general-debugger`                   | `developer-kit:general-debugger`                        |
| Architect   | `developer-kit:general-software-architect` | `developer-kit-java:java-software-architect-review` | `developer-kit-typescript:typescript-software-architect-review` | `developer-kit-typescript:typescript-software-architect-review` | `developer-kit-typescript:react-software-architect-review` | `developer-kit-aws:aws-solution-architect-expert`  | `developer-kit-python:python-software-architect-expert` |
| Code Review | `developer-kit:general-code-reviewer`      | `developer-kit-java:spring-boot-code-review-expert` | `developer-kit-typescript:general-code-reviewer`                | `developer-kit-typescript:nestjs-code-review-expert`            | `developer-kit-typescript:general-code-reviewer`           | `developer-kit-aws:aws-architecture-review-expert` | `developer-kit-python:python-code-review-expert`        |

## Core Principles

- **Understand before fixing**: Never fix what you don't understand
- **Find root cause**: Symptoms can be deceiving - trace back to the real issue
- **Minimal changes**: Fix only what's broken, avoid scope creep
- **Verify completely**: Confirm the fix works and doesn't break other things
- **Use TodoWrite**: Track all progress throughout
- **Structured user interaction**: Use the AskUserQuestion tool in all phases where you need to ask structured questions
  to the user (Phase 1: Problem Capture, Phase 3: Root Cause Analysis, Phase 4: Fix Design, Phase 7: Verification).
  Always use AskUserQuestion for clarifications, confirmations, and decisions rather than plain text questions.
- **No time estimates**: DO NOT provide or request time estimates or implementation timelines at any phase

---

## Phase 1: Problem Capture

**Goal**: Understand exactly what's wrong

**Initial issue**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases
2. Gather problem details:
    - What is the exact error message or unexpected behavior?
    - When did this start happening?
    - Can you reproduce it consistently?
    - What are the reproduction steps?
    - Any recent changes that might be related?
3. **Use the AskUserQuestion tool to gather all missing information in a clear, organized format**:
    - Error messages, logs, or stack traces
    - Steps to reproduce
    - Expected vs actual behavior
    - Environment details (local, staging, production)
4. **Wait for user answers before proceeding to evidence collection**

---

## Phase 2: Evidence Collection

**Goal**: Gather all relevant information about the failure

**Actions**:

1. Use the Task tool to launch 2-3 general-debugger subagents in parallel with different focuses:
    - Analyze stack traces and error messages
    - Trace execution paths related to the failure
    - Check recent git changes that might have introduced the bug

   **Example Task tool usage**:

```
Task(
  description: "Analyze error and trace execution path",
  prompt: "Analyze this error: [error description]. Trace the execution path from entry point to failure. Identify the exact failure point and potential causes.",
  subagent_type: "general-debugger"
)
```

**Example agent prompts**:

- "Analyze this stack trace: [trace]. Identify the root cause and exact failure point"
- "Trace the execution flow for [feature/function] and identify where it deviates from expected behavior"
- "Check recent git changes (last 5-10 commits) for changes that could have caused [issue]"
- "Analyze the data flow for [operation] and identify where data becomes corrupted/invalid"

2. Once agents return, read all identified critical files
3. Compile evidence summary with key findings

---

## Phase 3: Root Cause Analysis

**Goal**: Identify the exact root cause of the issue

**CRITICAL**: Do not proceed to fixing until root cause is confirmed.

**Actions**:

1. Use the Task tool to launch 2 general-debugger subagents with analysis focus:
    - Deep dive into the most likely failure point
    - Verify hypothesis with code analysis

2. Synthesize findings into root cause statement:
    - **What**: Exact condition causing the failure
    - **Where**: File and line where the bug originates
    - **Why**: Underlying reason this happens
    - **When**: Conditions that trigger the bug

3. **Use the AskUserQuestion tool to confirm root cause with user before proceeding**
4. **Wait for user confirmation before moving to Fix Design**

---

## Phase 4: Fix Design

**Goal**: Design the minimal, safest fix

**DO NOT PROCEED WITHOUT ROOT CAUSE CONFIRMATION**

**Actions**:

1. Use the Task tool to launch 2-3 general-software-architect subagents in parallel with different approaches:
    - Minimal surgical fix (smallest possible change)
    - Defensive fix (adds guards and validation)
    - Comprehensive fix (addresses similar issues elsewhere)

2. Review approaches considering:
    - Risk of regression
    - Side effects on other code
    - Test coverage implications

3. Present to user:
    - Brief summary of each approach
    - Trade-offs and risks
    - **Your recommendation with reasoning**

4. **Use the AskUserQuestion tool to ask user which approach they prefer**
5. **Wait for user response before proceeding to implementation**

---

## Phase 5: Implementation

**Goal**: Implement the fix

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:

1. Wait for explicit user approval
2. Re-read all affected files to ensure current state
3. Implement fix following chosen approach
4. Make minimal, focused changes
5. Add or update comments explaining the fix if non-obvious
6. Update todos as you progress

---

## Phase 6: Build & Test

**Goal**: Ensure the code compiles and all tests pass

**Actions**:

1. **Compile/Build** the project:
    - Run the appropriate build command for the project
    - Maven: `mvn compile` or `mvn package -DskipTests`
    - Gradle: `./gradlew build -x test` or `./gradlew compileJava`
    - npm: `npm run build`
    - Other: Use project-specific build command

2. **Fix any compilation errors** before proceeding

3. **Run tests**:
    - Run unit tests for affected components first
    - Run full test suite if quick tests pass
    - Maven: `mvn test` or `mvn verify`
    - Gradle: `./gradlew test`
    - npm: `npm test`

4. **If tests fail**:
    - Analyze failure: Is it related to our fix or pre-existing?
    - If related to fix: Return to Phase 5 and adjust
    - If pre-existing: Document and proceed (not our scope)

5. **Confirm all green** before proceeding to verification

---

## Phase 7: Verification & Review

**Goal**: Confirm the fix is correct and doesn't introduce regressions

**Actions**:

1. Use the Task tool to launch 2 general-code-reviewer subagents:
    - Review fix for correctness and potential regressions
    - Check for similar issues that might need the same fix

2. **Use the AskUserQuestion tool to confirm with user**:
    - Does the fix resolve the original issue?
    - Any unexpected behavior observed?
    - Should we add tests to prevent regression?

3. **Wait for user feedback before finalizing**

3. If regression tests needed:
    - Propose test cases that would catch this bug
    - **Use AskUserQuestion to ask if user wants to implement the tests**
    - Implement tests if user approves
    - Run tests again to confirm new tests pass

---

## Phase 8: Summary

**Goal**: Document what was fixed and learned

**Actions**:

1. Mark all todos complete
2. Summarize:
    - **Problem**: What was broken
    - **Root Cause**: Why it was broken
    - **Fix**: What was changed
    - **Files Modified**: List of changes
    - **Tests Added**: If any
    - **Prevention**: How to avoid similar issues

---

### General Agents (default, or `--lang=general`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit:general-software-architect`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### Java/Spring Boot Agents (`--lang=spring` or `--lang=java`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit-java:java-software-architect-review`
- **Code Reviewer**: `developer-kit-java:spring-boot-code-review-expert`

### TypeScript Agents (`--lang=typescript` or `--lang=ts`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit-typescript:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### NestJS Agents (`--lang=nestjs`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit-typescript:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit-typescript:nestjs-code-review-expert`

### React Agents (`--lang=react`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit-typescript:react-software-architect-review`
- **Code Reviewer**: `developer-kit-typescript:general-code-reviewer`

### Python Agents (`--lang=python` or `--lang=py`)

- **Debugger**: `developer-kit:general-debugger`
- **Software Architect**: `developer-kit-python:python-software-architect-expert`
- **Code Reviewer**: `developer-kit-python:python-code-review-expert`
- **Security Expert**: `developer-kit-python:python-security-expert`

### AWS Agents (`--lang=aws`)

- **Debugger**: `developer-kit-aws:aws-architecture-review-expert`
- **Software Architect**: `developer-kit-aws:aws-solution-architect-expert`
- **Code Reviewer**: `developer-kit-aws:aws-architecture-review-expert`
- **CloudFormation Expert**: `developer-kit-aws:aws-cloudformation-devops-expert`

**Fallback**: If specialized agents are not available, fall back to `general-purpose` agent.

1. **general-debugger** - Analyzes errors, traces execution, finds root cause
2. **general-software-architect** / **java-software-architect-review** / **typescript-software-architect-review** -
   Designs fix approaches with trade-offs
3. **general-code-reviewer** / **spring-boot-code-review-expert** / **nestjs-code-review-expert** - Reviews fix for
   quality and regressions

### Agent Selection Pattern

```
// General agents (default)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:general-debugger"
)

// Java/Spring Boot agents (when --lang=spring or --lang=java)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-java:java-software-architect-review"
)

// TypeScript agents (when --lang=typescript or --lang=ts)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-typescript:typescript-software-architect-review"
)

// NestJS agents (when --lang=nestjs)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-typescript:nestjs-code-review-expert"
)

// React agents (when --lang=react)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-typescript:react-frontend-development-expert"
)

// Python agents (when --lang=python or --lang=py)
Task(
  description: "Analyze Python error and trace execution",
  prompt: "Analyze this Python error and identify the root cause",
  subagent_type: "developer-kit:general-debugger"
)

Task(
  description: "Review Python architecture",
  prompt: "Review the Python architecture using Clean Architecture and DDD principles",
  subagent_type: "developer-kit-python:python-software-architect-expert"
)

Task(
  description: "Review Python code quality",
  prompt: "Review Python code for quality, Pythonic patterns, and best practices",
  subagent_type: "developer-kit-python:python-code-review-expert"
)

// AWS agents (when --lang=aws)
Task(
  description: "Debug AWS infrastructure issue",
  prompt: "Analyze CloudFormation template and AWS resources to identify the root cause",
  subagent_type: "developer-kit-aws:aws-architecture-review-expert"
)

Task(
  description: "Fix CloudFormation template",
  prompt: "Review and fix the CloudFormation template issues",
  subagent_type: "developer-kit-aws:aws-cloudformation-devops-expert"
)

Task(
  description: "Redesign AWS architecture",
  prompt: "Propose architectural fixes following AWS best practices",
  subagent_type: "developer-kit-aws:aws-solution-architect-expert"
)
```

### Important Notes

- Each sub-agent operates with its own context window
- Multiple sub-agents can be launched in parallel for different perspectives
- The main Claude maintains control and coordination of the overall process

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Problem Capture
[ ] Phase 2: Evidence Collection
[ ] Phase 3: Root Cause Analysis
[ ] Phase 4: Fix Design
[ ] Phase 5: Implementation
[ ] Phase 6: Build & Test
[ ] Phase 7: Verification & Review
[ ] Phase 8: Summary
```

Update the status as you progress through each phase.

---

## Quick Debug Mode

For simple issues, you can skip some phases:

**When to use quick mode**:

- Error message clearly points to the issue
- Recent, obvious change caused the bug
- Simple typo or configuration error

**Quick mode flow**:

1. Phase 1: Problem Capture (simplified)
2. Phase 3: Root Cause Analysis (focused)
3. Phase 5: Implementation
4. Phase 6: Build & Test
5. Phase 8: Summary

Tell the user: "This appears to be a straightforward issue. Would you like to proceed with quick debug mode?"

---

**Note**: This command follows a systematic debugging approach to ensure bugs are fixed correctly the first time, with
minimal risk of regression.

---

## Examples

```bash
# With error message (general agents)
/developer-kit:devkit.fix-debugging NullPointerException in UserService.getUserProfile()

# With bug description
/developer-kit:devkit.fix-debugging Users are seeing stale data after profile update

# Java/Spring Boot debugging
/developer-kit:devkit.fix-debugging --lang=spring Bean injection failing in OrderService

# TypeScript debugging
/developer-kit:devkit.fix-debugging --lang=typescript Type error in async handler

# NestJS debugging
/developer-kit:devkit.fix-debugging --lang=nestjs Dependency injection circular reference in AuthModule

# React debugging
/developer-kit:devkit.fix-debugging --lang=react Component not re-rendering after state update

# Python debugging
/developer-kit:devkit.fix-debugging --lang=python TypeError in async FastAPI endpoint handler

# Python debugging
/developer-kit:devkit.fix-debugging --lang=py Import circular dependency in Django models

# AWS infrastructure debugging
/developer-kit:devkit.fix-debugging --lang=aws CloudFormation stack creation failing with IAM error

# AWS architecture issues
/developer-kit:devkit.fix-debugging --lang=aws Lambda function timeout causing API Gateway 504 errors

# With test failure
/developer-kit:devkit.fix-debugging Test UserServiceTest.testGetProfile is failing intermittently

# With performance issue
/developer-kit:devkit.fix-debugging API response time increased from 50ms to 2s after last deploy

# With production issue
/developer-kit:devkit.fix-debugging Production errors: "Connection pool exhausted" every 2 hours
```
