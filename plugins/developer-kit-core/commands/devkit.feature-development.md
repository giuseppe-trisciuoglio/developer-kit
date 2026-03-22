---
description: Provides guided feature development capability with codebase understanding and architecture focus. Use when implementing a new feature from scratch.
argument-hint: "[ --lang=java|spring|typescript|nestjs|react|python|general ] [ feature-description ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Feature Development

## Overview

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply,
identify and ask about all underspecified details, design elegant architectures, then implement.

## Usage

```bash
/developer-kit:devkit.feature-development [--lang=java|spring|typescript|nestjs|react|python|general] [feature-description]
```

## Arguments

| Argument     | Description                              |
|--------------|------------------------------------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Current Context

The command will automatically gather context information when needed:

- Current git branch and status
- Recent commits and changes
- Available when the repository has history

## Execution Instructions

**Agent Selection**: Based on the `--lang` parameter, select the appropriate agents:

## Integration with Sub-agents

This command leverages three specialized sub-agents using the Task tool.

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

| Phase        | General (default)                          | Java/Spring Boot (`--lang=spring` or `--lang=java`) | TypeScript (`--lang=typescript` or `--lang=ts`)                 | NestJS (`--lang=nestjs`)                                        | React (`--lang=react`)                                     | AWS (`--lang=aws`)                                 | Python (`--lang=python` or `--lang=py`)                 |
|--------------|--------------------------------------------|-----------------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------|---------------------------------------------------------|
| Exploration  | `developer-kit:general-code-explorer`      | `developer-kit-java:spring-boot-backend-development-expert` | `developer-kit:general-code-explorer`                           | `developer-kit:nestjs-backend-development-expert`               | `developer-kit:react-frontend-development-expert`          | `developer-kit:aws-solution-architect-expert`      | `developer-kit:general-code-explorer`                   |
| Architecture | `developer-kit:general-software-architect` | `developer-kit-java:java-software-architect-review` | `developer-kit-typescript:typescript-software-architect-review` | `developer-kit-typescript:typescript-software-architect-review` | `developer-kit-typescript:react-software-architect-review` | `developer-kit-aws:aws-solution-architect-expert`  | `developer-kit-python:python-software-architect-expert` |
| Code Review  | `developer-kit:general-code-reviewer`      | `developer-kit-java:spring-boot-code-review-expert` | `developer-kit-typescript:general-code-reviewer`                | `developer-kit-typescript:nestjs-code-review-expert`            | `developer-kit-typescript:general-code-reviewer`           | `developer-kit-aws:aws-architecture-review-expert` | `developer-kit-python:python-code-review-expert`        |

## Core Principles

- **Ask clarifying questions — NEVER SKIP**: Phases marked with **[GATE]** MANDATORY STOP POINT are hard gates. You MUST call
  the AskUserQuestion tool and wait for the user's response before proceeding. Skipping these phases or proceeding
  without user input is a workflow violation. Identify all ambiguities, edge cases, and underspecified behaviors. Ask
  specific, concrete questions rather than making assumptions.
- **Structured user interaction**: You MUST use the AskUserQuestion tool in all phases where you need to ask structured
  questions to the user (Phase 3: Clarifying Questions, Phase 4: Architecture Design, and whenever multiple choice
  questions are presented).
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to
  read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates or implementation timelines at any phase

---

## Workflow: Feature Development (7 Phases)

This command implements a new feature following a systematic 7-phase workflow:
- Phase 1: Discovery
- Phase 2: Codebase Exploration
- Phase 3: Clarifying Questions
- Phase 4: Architecture Design
- Phase 5: Implementation
- Phase 6: Quality Review
- Phase 7: Summary

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

**Initial request**: $ARGUMENTS

**Actions**:

1. **Check for uncommitted changes FIRST** (before anything else):
   - Run `git status --porcelain` to check for uncommitted changes
   - If there are untracked files, staged changes, or unstaged modifications:
     - Present the user with the specific changes found
     - Ask via AskUserQuestion: "You have uncommitted changes. Please commit them before starting feature development. Do you want to proceed anyway (not recommended) or commit first?"
     - If user chooses to commit first, stop and wait for them to run `git commit`
     - If user proceeds anyway, document the uncommitted state and continue at user's risk
   - Only proceed with the workflow if no uncommitted changes exist OR user explicitly accepts the risk
2. **Run lint and tests** (after git check passes):
   - Detect available lint/test commands by checking `package.json` (scripts), `Makefile`, `pom.xml`, `build.gradle`, `pyproject.toml`, `composer.json`, etc.
   - Run lint first (e.g., `npm run lint`, `make lint`, `./mvnw checkstyle:check`, `ruff check .`), then tests (e.g., `npm test`, `make test`, `./mvnw test -q`, `pytest`, `php artisan test`)
   - If lint or tests fail:
     - Show the failing output to the user
     - Ask via AskUserQuestion: "Lint/tests are failing. It is recommended to fix them before starting feature development to avoid compounding issues. Do you want to fix them first (recommended) or proceed anyway?"
     - If user chooses to fix first, stop and wait
     - If user proceeds anyway, document the failures and continue at user's risk
   - If no recognizable lint/test commands are found, skip this step and note it
   - Only proceed if lint/tests pass OR user explicitly accepts the risk
3. Create todo list with all phases
4. For Feature Mode: If feature unclear, ask user for:
    - What problem are they solving?
    - What should the feature do?
    - Any constraints or requirements?
5. Summarize understanding and confirm with user

---

## Phase 1.5: Pre-load Knowledge Graph

**Goal**: Check if existing feature has cached analysis to inform implementation

**Prerequisite**: Phase 1 (Discovery) completed

**Actions**:

1. **Ask user about existing specifications**:
   - "Is this feature related to an existing specification in docs/specs/?"
   - If yes, get spec folder path from user

2. **If spec folder provided**:
   - Check for `knowledge-graph.json` in the spec folder
   - If KG exists:
     - Read and summarize key findings:
       - Patterns used in related feature
       - Components available for reuse
       - Integration points established
       - Conventions to follow
     - Present summary to user:
       ```
       Found related specification '[spec-id]' with cached analysis:
       - X architectural patterns
       - Y existing components
       - Z integration points

       Use these patterns for consistency with existing code?
       ```
     - If user chooses to use KG:
       - Load KG patterns, components, APIs into context
       - Use these patterns in Phase 4 (Architecture Design)
       - Note: "Following patterns from existing [feature-name] implementation"
     - If user chooses not to use KG:
       - Proceed with fresh exploration in Phase 2

3. **If no spec folder or KG doesn't exist**:
   - Proceed to Phase 2 (Codebase Exploration) without KG context
   - Note: "No cached analysis found, will explore codebase fresh"

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

**Actions**:

1. Use the Task tool to launch a single explorer subagent (select agent based on `--lang` parameter) to comprehensively
   trace through the code and provide a prioritized list of key files to read.

   **Example Task tool usage**:

```
Task(
  description: "Explore similar features",
  prompt: "Find features similar to [feature] and trace through their implementation comprehensively. Focus on understanding patterns, architecture, and integration points.",
  subagent_type: "developer-kit:general-code-explorer"
)
```

**Example agent prompts**:

- "Find features similar to [feature] and trace through their implementation comprehensively"
- "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
- "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
- "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

2. Once the agents return, read all files identified by agents to build deep understanding
3. Present comprehensive summary of findings and patterns discovered

---

## Phase 2.5: Update Knowledge Graph (Optional)

**Goal**: Persist new discoveries from exploration into Knowledge Graph

**Prerequisite**: Phase 2 (Codebase Exploration) completed AND user provided spec folder in Phase 1.5

**Actions**:

1. **Check if spec folder was provided** in Phase 1.5:
   - If no spec folder, skip this phase
   - If spec folder provided, proceed

2. **Extract new findings from agent exploration**:
   - Patterns discovered that weren't in KG
   - New components identified
   - New integration points found
   - Updates to existing patterns/conventions

3. **Update Knowledge Graph** using the skill:
   - Call: `/knowledge-graph update [spec-folder] [update-object] "feature-development explorer agent"`
   - Map agent findings to KG schema sections
   - Skill will merge new findings into existing KG

4. **Log update**:
   ```
   Knowledge Graph updated with exploration findings:
   - X new patterns documented
   - Y new components catalogued
   - Z integration points mapped

   Updated: docs/specs/[ID]/knowledge-graph.json
   ```

5. **If write fails**:
   - Log warning but continue (non-blocking)
   - Note: "Failed to update Knowledge Graph, continuing without caching"

**Note**: This phase is optional and only executes if user provided a spec folder in Phase 1.5.

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

****[GATE]** MANDATORY STOP POINT — DO NOT SKIP THIS PHASE UNDER ANY CIRCUMSTANCES.**

This is the most important phase of the entire workflow. You MUST stop here and ask questions before proceeding.
Proceeding to Phase 4 without completing this phase is a workflow violation.

**Actions**:

1. Review the codebase findings and original feature request
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design
   preferences, backward compatibility, performance needs
3. **You MUST call the AskUserQuestion tool to present all questions to the user in a clear, organized format**
4. ****[GATE]** STOP: Wait for the user's answers. Do NOT proceed to Phase 4 until the user has responded.**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation before
proceeding.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:

1. Use the Task tool to launch a single pragmatic architect subagent (select agent based on `--lang` parameter) focused
   on a balanced, pragmatic approach (speed + quality).
2. Review the pragmatic approach and form your recommendation based on task context (consider: small fix vs large
   feature, urgency, complexity, team context).
3. Present to user: brief summary of the pragmatic approach, trade-offs, and concrete implementation differences.
4. **You MUST call the AskUserQuestion tool to ask user whether they approve the pragmatic approach or want an alternative**
5. ****[GATE]** STOP: Wait for the user's approval. Do NOT proceed to Phase 5 until the user has responded.**

---

## Phase 5: Implementation

**Goal**: Build the feature

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:

1. Wait for explicit user approval
2. Read all relevant files identified in previous phases
3. Implement following chosen architecture
4. Follow codebase conventions strictly
5. Write clean, well-documented code
6. Update todos as you progress

---

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct

**Actions**:

1. Use the Task tool to launch a single code-reviewer subagent (select agent based on `--lang` parameter) focused on a
   balanced review covering simplicity, correctness, and conventions.
2. Consolidate findings and identify highest severity issues that you recommend fixing
3. **Present findings to user and ask what they want to do** (fix now, fix later, or proceed as-is)
4. Address issues based on user decision

---

## Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
    - What was built
    - Key decisions made
    - Files modified
    - Suggested next steps

---

## Sub-agents Reference

### General Agents (default, or `--lang=general`)

- **Code Explorer**: `developer-kit:general-code-explorer`
- **Software Architect**: `developer-kit:general-software-architect`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### Java/Spring Boot Agents (`--lang=spring` or `--lang=java`)

- **Code Explorer**: `developer-kit-java:spring-boot-backend-development-expert`
- **Software Architect**: `developer-kit-java:java-software-architect-review`
- **Code Reviewer**: `developer-kit-java:spring-boot-code-review-expert`

### TypeScript Agents (`--lang=typescript` or `--lang=ts`)

- **Code Explorer**: `developer-kit:general-code-explorer`
- **Software Architect**: `developer-kit-typescript:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### NestJS Agents (`--lang=nestjs`)

- **Code Explorer**: `developer-kit:nestjs-backend-development-expert`
- **Software Architect**: `developer-kit:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit-typescript:nestjs-code-review-expert`

### React Agents (`--lang=react`)

- **Code Explorer**: `developer-kit:react-frontend-development-expert`
- **Software Architect**: `developer-kit:react-software-architect-review`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### Python Agents (`--lang=python` or `--lang=py`)

- **Code Explorer**: `developer-kit:general-code-explorer`
- **Software Architect**: `developer-kit-python:python-software-architect-expert`
- **Code Reviewer**: `developer-kit-python:python-code-review-expert`
- **Security Expert**: `developer-kit-python:python-security-expert`

### AWS Agents (`--lang=aws`)

- **Code Explorer**: `developer-kit:aws-solution-architect-expert`
- **Software Architect**: `developer-kit-aws:aws-solution-architect-expert`
- **Code Reviewer**: `developer-kit-aws:aws-architecture-review-expert`
- **CloudFormation Expert**: `developer-kit-aws:aws-cloudformation-devops-expert`

**Fallback**: If specialized agents are not available, fall back to `general-purpose` agent.

### Agent Selection Pattern

```
// General agents (default)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:general-code-explorer"
)

// Java/Spring Boot agents (when --lang=spring or --lang=java)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-java:spring-boot-backend-development-expert"
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
  subagent_type: "developer-kit-typescript:nestjs-backend-development-expert"
)

// React agents (when --lang=react)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit-typescript:react-frontend-development-expert"
)

// Python agents (when --lang=python or --lang=py)
Task(
  description: "Explore Python codebase",
  prompt: "Explore the Python codebase and identify patterns, architecture, and key files",
  subagent_type: "developer-kit:general-code-explorer"
)

Task(
  description: "Design Python architecture",
  prompt: "Design architecture using Clean Architecture, DDD, and Python best practices",
  subagent_type: "developer-kit-python:python-software-architect-expert"
)

Task(
  description: "Review Python code",
  prompt: "Review Python code for quality, Pythonic patterns, and adherence to PEP standards",
  subagent_type: "developer-kit-python:python-code-review-expert"
)

// AWS agents (when --lang=aws)
Task(
    description:"Design AWS architecture",
    prompt:"Design scalable cloud architecture for the feature",
    subagent_type:"developer-kit-aws:aws-solution-architect-expert"
)

Task(
    description:"Create CloudFormation templates",
    prompt:"Create IaC templates for the infrastructure",
    subagent_type:"developer-kit-aws:aws-cloudformation-devops-expert"
)

Task(
    description:"Review AWS architecture",
    prompt:"Review architecture against Well-Architected Framework",
    subagent_type:"developer-kit-aws:aws-architecture-review-expert"
)
```

### Important Notes

- Each sub-agent operates with its own context window
- Multiple sub-agents can be launched in parallel for different perspectives
- The main Claude maintains control and coordination of the overall process

Each agent is launched with specific prompts tailored to the phase of development.

## Todo Management

Throughout the process, maintain a todo list like:

```
[ ] Phase 1: Discovery
[ ] Phase 2: Codebase Exploration
[ ] Phase 3: Clarifying Questions
[ ] Phase 4: Architecture Design
[ ] Phase 5: Implementation
[ ] Phase 6: Quality Review
[ ] Phase 7: Summary
```

Update the status as you progress through each phase.

---

## Decision Logging Protocol

Throughout the workflow, whenever a non-trivial choice is made between alternatives, append a DEC entry to `docs/specs/[id]/decision-log.md`.

### When to log decisions:

**Feature Mode Phase 4 (Architecture Design)**: After user approves an architecture approach, log:
- DEC-NNN: Architecture Approach
- Date, Phase, Context, Decision (approach chosen), Alternatives considered, Impact

### Decision Log Format:

```markdown
## DEC-NNN: [Decision Title]
- **Date**: YYYY-MM-DD
- **Task**: Feature Development
- **Phase**: [Phase name]
- **Context**: [Why this decision was necessary]
- **Decision**: [What was decided]
- **Alternatives Considered**: [What was rejected and why]
- **Impact**: [Files/components affected]
- **Decided By**: user / AI recommendation accepted
```

### How to find spec folder:

- In Feature Mode: Ask user or infer from $ARGUMENTS context
- If no decision-log.md exists, create it with header table

---

## Examples

```bash
# Simple feature (general agents)
/developer-kit:devkit.feature-development Add user authentication

# Java/Spring Boot feature
/developer-kit:devkit.feature-development --lang=spring Add REST API for user management

# Java feature with specialized agents
/developer-kit:devkit.feature-development --lang=java Implement caching layer for products

# Complex feature with description
/developer-kit:devkit.feature-development Implement real-time notifications using WebSockets

# Integration feature
/developer-kit:devkit.feature-development --lang=spring Add payment processing with Stripe integration

# TypeScript feature
/developer-kit:devkit.feature-development --lang=typescript Add GraphQL resolver for user queries

# NestJS feature
/developer-kit:devkit.feature-development --lang=nestjs Implement authentication module with JWT

# React frontend feature
/developer-kit:devkit.feature-development --lang=react Create dashboard with charts and user filters

# Python feature
/developer-kit:devkit.feature-development --lang=python Implement REST API with FastAPI and SQLAlchemy

# Python feature with specialized agents
/developer-kit:devkit.feature-development --lang=py Add async task queue with Celery integration

# AWS infrastructure feature
/developer-kit:devkit.feature-development --lang=aws Design multi-region high availability architecture

# AWS CloudFormation feature
/developer-kit:devkit.feature-development --lang=aws Create ECS Fargate infrastructure with auto scaling

# Explicit general agents
/developer-kit:devkit.feature-development --lang=general Create dashboard with charts and filters
```