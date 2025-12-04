---
description: Guided feature development with codebase understanding and architecture focus
argument-hint: [feature-description]
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite
model: inherit
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply, identify and ask about all underspecified details, design elegant architectures, then implement.

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Changes**: !`git diff --name-only HEAD~1`

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific, concrete questions rather than making assumptions. Wait for user answers before proceeding with implementation. Ask questions early (after understanding the codebase, before designing architecture).
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Use TodoWrite**: Track all progress throughout

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
1. Use the Task tool to launch 2-3 devkit-code-explorer subagents in parallel. Each with different prompts:
   - Trace through the code comprehensively and focus on getting a comprehensive understanding of abstractions, architecture and flow of control
   - Target a different aspect of the codebase (eg. similar features, high level understanding, architectural understanding, user experience, etc.)
   - Include a list of 5-10 key files to read

   **Example Task tool usage**:
```
Task(
  description: "Explore similar features",
  prompt: "Find features similar to [feature] and trace through their implementation comprehensively. Focus on understanding patterns, architecture, and integration points.",
  subagent_type: "devkit-code-explorer"
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
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs
3. **Present all questions to the user in a clear, organized list**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:
1. Use the Task tool to launch 2-3 devkit-software-architect subagents in parallel with different focuses:
   - minimal changes (smallest change, maximum reuse)
   - clean architecture (maintainability, elegant abstractions)
   - pragmatic balance (speed + quality)
2. Review all approaches and form your opinion on which fits best for this specific task (consider: small fix vs large feature, urgency, complexity, team context)
3. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**, concrete implementation differences
4. **Ask user which approach they prefer**

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
1. Use the Task tool to launch 3 devkit-code-reviewer subagents in parallel with different focuses:
   - simplicity/DRY/elegance
   - bugs/functional correctness
   - project conventions/abstractions
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
# Simple feature
/devkit.feature-development Add user authentication

# Complex feature with description
/devkit.feature-development Implement real-time notifications using WebSockets

# Integration feature
/devkit.feature-development Add payment processing with Stripe integration

# UI feature
/devkit.feature-development Create dashboard with charts and filters
```

## Integration with Sub-agents

This command leverages three specialized sub-agents using the Task tool:

1. **devkit-code-explorer** - Analyzes existing codebase to understand patterns
2. **devkit-software-architect** - Designs implementation approaches
3. **devkit-code-reviewer** - Reviews implementation for quality

### Usage Pattern
```javascript
// Launch a sub-agent
Task(
  description: "Brief task description",
  prompt: "Detailed prompt for the sub-agent",
  subagent_type: "subagent-name"
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

**Note**: This command follows a systematic approach to ensure high-quality implementations that integrate well with existing codebases and meet user requirements effectively.