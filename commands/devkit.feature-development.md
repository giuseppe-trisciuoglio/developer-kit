---
description: Guided feature development with codebase understanding and architecture focus
argument-hint: [ --lang=java|spring|typescript|nestjs|react|general ] [ feature-description ]
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply,
identify and ask about all underspecified details, design elegant architectures, then implement.

## Language/Framework Selection

Parse $ARGUMENTS to detect the optional `--lang` parameter:

- `--lang=spring` or `--lang=java`: Use Java/Spring Boot specialized agents
- `--lang=typescript` or `--lang=ts`: Use TypeScript specialized agents
- `--lang=nestjs`: Use NestJS specialized agents
- `--lang=react`: Use React frontend specialized agents
- `--lang=aws`: Use AWS specialized agents (architecture, CloudFormation, IaC)
- `--lang=general` or no flag: Use general-purpose agents (default)

**Agent Mapping by Language:**

| Phase        | General (default)             | Java/Spring Boot (`--lang=spring` or `--lang=java`) | TypeScript (`--lang=typescript` or `--lang=ts`)      | NestJS (`--lang=nestjs`)                             | React (`--lang=react`)                          | AWS (`--lang=aws`)                             |
|--------------|-------------------------------|-----------------------------------------------------|------------------------------------------------------|------------------------------------------------------|-------------------------------------------------|------------------------------------------------|
| Exploration  | `developer-kit:code-explorer` | `developer-kit:code-explorer`                       | `developer-kit:code-explorer`                        | `developer-kit:code-explorer`                        | `developer-kit:code-explorer`                   | `developer-kit:code-explorer`                  |
| Architecture | `developer-kit:software-architect`     | `developer-kit:java-software-architect-review`      | `developer-kit:typescript-software-architect-review` | `developer-kit:typescript-software-architect-review` | `developer-kit:react-software-architect-review` | `developer-kit:aws-solution-architect-expert`  |
| Code Review  | `developer-kit:code-reviewer` | `developer-kit:spring-boot-code-review-expert`      | `developer-kit:general-code-reviewer`                | `developer-kit:nestjs-code-review-expert`            | `developer-kit:general-code-reviewer`           | `developer-kit:aws-architecture-review-expert` |

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Changes**: !`git diff --name-only HEAD~1`

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific,
  concrete questions rather than making assumptions. Wait for user answers before proceeding with implementation. Ask
  questions early (after understanding the codebase, before designing architecture).
- **Structured user interaction**: Use the AskUserQuestion tool in all phases where you need to ask structured questions
  to the user (Phase 3: Clarifying Questions, Phase 4: Architecture Design, and whenever multiple choice questions are
  presented).
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to
  read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates or implementation timelines at any phase

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

**Initial request**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases
2. If feature unclear, ask user for:
    - What problem are they solving?
    - What should the feature do?
    - Any constraints or requirements?
3. Summarize understanding and confirm with user

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
  subagent_type: "developer-kit:code-explorer"
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

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:

1. Review the codebase findings and original feature request
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design
   preferences, backward compatibility, performance needs
3. **Use the AskUserQuestion tool to present all questions to the user in a clear, organized format**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:

1. Use the Task tool to launch a single pragmatic architect subagent (select agent based on `--lang` parameter) focused
   on a balanced, pragmatic approach (speed + quality).
2. Review the pragmatic approach and form your recommendation based on task context (consider: small fix vs large
   feature, urgency, complexity, team context).
3. Present to user: brief summary of the pragmatic approach, trade-offs, and concrete implementation differences.
4. **Use the AskUserQuestion tool to ask user whether they approve the pragmatic approach or want an alternative**

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

## Usage Examples

```bash
# Simple feature (general agents)
/devkit.feature-development Add user authentication

# Java/Spring Boot feature
/devkit.feature-development --lang=spring Add REST API for user management

# Java feature with specialized agents
/devkit.feature-development --lang=java Implement caching layer for products

# Complex feature with description
/devkit.feature-development Implement real-time notifications using WebSockets

# Integration feature
/devkit.feature-development --lang=spring Add payment processing with Stripe integration

# TypeScript feature
/devkit.feature-development --lang=typescript Add GraphQL resolver for user queries

# NestJS feature
/devkit.feature-development --lang=nestjs Implement authentication module with JWT

# React frontend feature
/devkit.feature-development --lang=react Create dashboard with charts and user filters

# AWS infrastructure feature
/devkit.feature-development --lang=aws Design multi-region high availability architecture

# AWS CloudFormation feature
/devkit.feature-development --lang=aws Create ECS Fargate infrastructure with auto scaling

# Explicit general agents
/devkit.feature-development --lang=general Create dashboard with charts and filters
```

## Integration with Sub-agents

This command leverages three specialized sub-agents using the Task tool.

## Execution Instructions

**Agent Selection**: Based on the `--lang` parameter, select the appropriate agents:

### General Agents (default, or `--lang=general`)

- **Code Explorer**: `developer-kit:code-explorer`
- **Software Architect**: `developer-kit:software-architect`
- **Code Reviewer**: `developer-kit:code-reviewer`

### Java/Spring Boot Agents (`--lang=spring` or `--lang=java`)

- **Code Explorer**: `developer-kit:spring-boot-backend-development-expert`
- **Software Architect**: `developer-kit:java-software-architect-review`
- **Code Reviewer**: `developer-kit:spring-boot-code-review-expert`

### TypeScript Agents (`--lang=typescript` or `--lang=ts`)

- **Code Explorer**: `developer-kit:general-code-explorer`
- **Software Architect**: `developer-kit:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### NestJS Agents (`--lang=nestjs`)

- **Code Explorer**: `developer-kit:nestjs-backend-development-expert`
- **Software Architect**: `developer-kit:typescript-software-architect-review`
- **Code Reviewer**: `developer-kit:nestjs-code-review-expert`

### React Agents (`--lang=react`)

- **Code Explorer**: `developer-kit:react-frontend-development-expert`
- **Software Architect**: `developer-kit:react-software-architect-review`
- **Code Reviewer**: `developer-kit:general-code-reviewer`

### AWS Agents (`--lang=aws`)

- **Code Explorer**: `developer-kit:aws-solution-architect-expert`
- **Software Architect**: `developer-kit:aws-solution-architect-expert`
- **Code Reviewer**: `developer-kit:aws-architecture-review-expert`
- **CloudFormation Expert**: `developer-kit:aws-cloudformation-devops-expert`

**Fallback**: If specialized agents are not available, fall back to `general-purpose` agent.

### Usage Pattern

```
// General agents (default)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:code-explorer"
)

// Java/Spring Boot agents (when --lang=spring or --lang=java)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:spring-boot-backend-development-expert"
)

// TypeScript agents (when --lang=typescript or --lang=ts)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:typescript-software-architect-review"
)

// NestJS agents (when --lang=nestjs)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:nestjs-backend-development-expert"
)

// React agents (when --lang=react)
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "developer-kit:react-frontend-development-expert"
)

// AWS agents (when --lang=aws)
Task(
    description:"Design AWS architecture",
    prompt:"Design scalable cloud architecture for the feature",
    subagent_type:"developer-kit:aws-solution-architect-expert"
)

Task(
    description:"Create CloudFormation templates",
    prompt:"Create IaC templates for the infrastructure",
    subagent_type:"developer-kit:aws-cloudformation-devops-expert"
)

Task(
    description:"Review AWS architecture",
    prompt:"Review architecture against Well-Architected Framework",
    subagent_type:"developer-kit:aws-architecture-review-expert"
)
```

### Important Notes

- Sub-agents are automatically discovered from `/Users/giuseppe/project/GT/developer-kit/agents/`
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

**Note**: This command follows a systematic approach to ensure high-quality implementations that integrate well with
existing codebases and meet user requirements effectively.