---
description: "Provides guided brainstorming capability to transform ideas into pure functional specifications. Use when starting a new feature to define WHAT should be built (not HOW). Output: docs/specs/[id]/YYYY-MM-DD--feature-name.md"
argument-hint: "[ idea-description ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
model: inherit
---

# Brainstorming

Provides guided brainstorming to transform ideas into pure functional specifications (WHAT, not HOW). Focus on business
logic, use cases, and acceptance criteria — no code, frameworks, or technical patterns.

## Overview

This command produces a **functional specification** — a document that describes WHAT the system should do, without HOW
it will be implemented.

The new workflow:

```
Idea → Functional Specification (docs/specs/[id]/) → Tasks (docs/specs/[id]/tasks/) → Implementation
```

**Output**: `docs/specs/[id]/YYYY-MM-DD--feature-name.md`

Preferred naming is `YYYY-MM-DD--feature-name.md`. If the spec folder already uses legacy `*-specs.md` files, keep the existing convention instead of mixing both formats.

Where `[id]` is a unique identifier in format `NNN-feature-name` (e.g., `001-hotel-search-aggregation`).

### What vs. How

| Aspect   | Functional Specification (WHAT)     | Technical Design (HOW)         |
|----------|-------------------------------------|--------------------------------|
| Focus    | Business rules, user behaviors      | Frameworks, patterns, code     |
| Language | Natural language                    | Technical terminology          |
| Examples | "User can reset password via email" | "Use Spring Security with JWT" |
| Output   | `docs/specs/[id]/`                  | `docs/plans/` (deprecated)     |

Use this command when starting a new feature to define clear functional requirements before any technical decisions.

## Usage

```bash
/developer-kit:devkit.brainstorm [idea-description]
```

After generating the functional specification, continue with:

```bash
/developer-kit:devkit.spec-to-tasks docs/specs/[id]/
```

## Arguments

| Argument           | Required | Description                                      |
|--------------------|----------|--------------------------------------------------|
| `idea-description` | No       | Description of the idea or feature to brainstorm |

## Current Context

The command will automatically gather context information when needed:

- Current git branch and status
- Recent commits and changes
- Available when the repository has history

### Argument Details

**idea-description**

- Purpose: Describes the initial idea, feature, or problem to solve
- Format: Free text describing the concept
- Default: If not provided, the command will ask for it interactively
- Examples: "Add user authentication", "Refactor payment module", "Design caching strategy"

---

You are helping a developer transform an idea into a fully formed design. Follow a systematic approach: understand the
project
context, explore the idea through targeted questions, explore existing code, propose alternative approaches, present the
design
incrementally, generate professional documentation, review the document, and recommend the next development command.

## Core Principles

- **Ask only high-signal questions**: Use AskUserQuestion only when the answer materially changes scope, acceptance criteria, or constraints. If the request is already clear, proceed without adding extra checkpoints.
- **Multiple choice preferred**: Easier to answer than open-ended when possible
- **YAGNI ruthlessly**: Remove unnecessary features from all specifications
- **Functional focus ONLY**: Describe WHAT the system should do, never HOW it will be implemented
- **No technical decisions**: Do NOT mention frameworks, libraries, patterns, or code
- **Incremental validation**: Present specification in sections, validate each
- **Professional documentation**: Use specialist agent for high-quality documents
- **Be flexible**: Go back and clarify when something doesn't make sense
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates

---

## Phase 1: Context Discovery

**Goal**: Understand the current project state and the initial idea

**Initial idea**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases
2. Explore the current project state (for context only - do NOT include in specification):
    - Read recent commits to understand what's being worked on
    - Check for existing documentation (README, docs/, existing specs)
    - Look for related features or similar implementations
3. If the idea is unclear, ask the user for:
    - What problem are they trying to solve?
    - What is the high-level goal?
    - Any initial thoughts or constraints?

4. **Determine workflow tier based on idea complexity**:
    - **Quick** (bug fix, small change, <3 files, well-understood solution):
        - Recommend switching to `/developer-kit:devkit.quick-spec` for faster turnaround
        - Ask via AskUserQuestion:
            - Options:
                - "Continue with full brainstorming" (for comprehensive spec)
                - "Switch to quick spec" (recommended for bug fixes/small changes)
    - **Standard** (feature, moderate scope, 3-10 files): Continue with brainstorm
    - **Full** (greenfield, complex, >10 files or multiple modules): Continue with brainstorm + recommend spec-review
      after

---

## Phase 2: Idea Refinement

**Goal**: Deeply understand the idea through structured dialogue

Run this phase only if the initial request still has meaningful ambiguity after Phase 1.

**Actions**:

1. Ask up to 3 tightly related questions to refine the idea
2. Prefer a single AskUserQuestion checkpoint with multiple choice options when possible
3. Focus on understanding:
    - **Purpose**: What is this trying to achieve?
    - **Constraints**: Are there technical, time, or resource constraints?
    - **Success Criteria**: How will we know if this is successful?
    - **Scope**: What is in scope and what is explicitly out of scope?
    - **Users**: Who will use this and how?

**Example structured questions**:

- "What is the primary success metric for this feature?"
- "Which constraint is most important: development time, performance, or maintainability?"
- "Who are the primary users of this feature?"

4. If the idea becomes clear, summarize assumptions and proceed to Phase 3
5. If ambiguity remains after one checkpoint, ask one final focused follow-up and then proceed

---

## Phase 3: Functional Approach Exploration

**Goal**: Present 2-3 different functional approaches with trade-offs (WHAT, not HOW)

**Actions**:

1. Based on the refined idea, develop 2-3 distinct approaches focusing on BEHAVIOR:
    - **Approach A**: Simple/MVP (fastest to implement, may lack some features)
    - **Approach B**: Balanced (good feature set, reasonable complexity) - **typically your recommendation**
    - **Approach C**: Comprehensive (full-featured, more complex)

2. For each approach, describe ONLY functional aspects:
    - User behaviors supported
    - Business rules and constraints
    - Data requirements (what, not how)
    - Integration points (capabilities needed, not technical implementation)
    - Pros (benefits for users/business)
    - Cons (limitations, complexity for users)

3. **CRITICAL**: Do NOT mention any technical details:
    - NO frameworks (Spring, NestJS, React, etc.)
    - NO patterns (Repository, Service, Controller, etc.)
    - NO libraries or dependencies
    - NO code or pseudo-code

4. If there are materially different scope options, use AskUserQuestion to present them:
    - Lead with your recommended option
    - Explain your reasoning
5. If one approach is clearly dominant, select it, record the rationale, and proceed without an extra gate

6. **After approach selection, log the decision**:
    - Create an in-memory note of DEC-001: Approach Selection
    - Record: date, approach chosen, alternatives presented, rationale
    - This will be written to `decision-log.md` in Phase 6

---

## Phase 4: Contextual Codebase Exploration (Optional)

**Goal**: Understand existing codebase for context only — do NOT influence the specification with technical decisions

**NOTE**: This phase is OPTIONAL. Skip if not needed. The functional specification should be technology-agnostic.

**Actions**:

1. Only if the feature needs to integrate with existing systems, use the Task tool to explore:

```
Task(
  description: "Explore codebase for integration context",
  prompt: "Explore the codebase to understand what existing systems, APIs, or data structures the new feature must integrate with.

    Focus on:
    1. Existing APIs or interfaces the feature must use
    2. Shared data structures or models
    3. Existing business rules that apply

    Return:
    - List of integration requirements (capabilities needed, not implementation)
    - Do NOT suggest frameworks, patterns, or technical solutions",
  subagent_type: "developer-kit:general-code-explorer"
)
```

2. Incorporate findings as integration requirements in the specification
3. Do NOT let this influence technical decisions — keep the specification functional

---

## Phase 5: Functional Specification Presentation

**Goal**: Present the functional specification in validated sections

**DO NOT START WITHOUT APPROACH APPROVAL**

**Actions**:

1. Once the approach is selected, present the functional specification in sections of 200-300 words each
2. Incorporate any integration requirements from Phase 4
3. Cover the following areas in separate sections:

   **Section 1: Business Context**
    - What problem does this feature solve?
    - Who are the users and what are their goals?
    - How does this fit into the overall system purpose?

   **Section 2: Functional Requirements**
    - User stories and use cases
    - Business rules and constraints
    - Data requirements (what data, not how to store)
    - External system capabilities needed

   **Section 3: User Interactions**
    - User flows and journeys
    - Alternative paths and edge cases
    - Error scenarios and how users are informed

   **Section 4: Acceptance Criteria**
    - Clear, testable criteria for each user story
    - Success conditions in natural language
    - Edge case handling

   **Section 5: Integration Requirements**
    - What existing systems must integrate with (capabilities, not implementation)
    - Data exchange requirements (not technical protocols)

4. **CRITICAL**: Throughout all sections, NEVER mention:
    - Frameworks, libraries, or tools
    - Technical patterns or architectural styles
    - Code or pseudo-code

5. Validate only at meaningful checkpoints:
    - Default: generate all sections, then present one consolidated review
    - Use AskUserQuestion mid-way only if a section introduces new ambiguity or a major scope decision

6. If no major ambiguity is detected, proceed directly to Phase 6 and collect feedback on the complete draft

---

## Phase 6: Functional Specification Generation

**Goal**: Generate professional functional specification document

**Actions**:

1. Compile all validated specification sections

2. Generate unique spec ID:
    - Count existing folders in `docs/specs/` to determine next sequence number
    - Create slug from feature name (lowercase, hyphenated)
    - Format: `NNN-feature-slug` (e.g., `001-hotel-search-aggregation`)
    - Example: If 5 specs exist, next ID is `006-feature-name`

3. Create spec folder: `docs/specs/[id]/`

4. **CRITICAL: Save the original user request**:
    - Create a file `user-request.md` in `docs/specs/[id]/` containing:
        - The original user input/idea description
        - Any constraints or requirements mentioned
        - This file will be used by `spec-to-tasks` to verify all requirements are captured
    - Example content:
      ```markdown
      # User Request
 
      **Original Input**: [what the user asked for]
 
      **Key Requirements Mentioned**:
      - [requirement 1]
      - [requirement 2]
 
      **Constraints**: [any constraints mentioned]
      ```

5. Use the Task tool to launch the document-generator-expert subagent:

```
Task(
  description: "Generate functional specification",
  prompt: "Generate a professional functional specification document based on the following validated specification:

    **Feature Title**: [title]
    **Date**: [current date]
    **Spec ID**: [id] (e.g., 001-hotel-search-aggregation)

    **Business Context**:
    - Problem solved: [from Section 1]
    - Target users: [from Section 1]
    - System fit: [from Section 1]

    **Functional Requirements**:
    - User stories: [from Section 2]
    - Business rules: [from Section 2]
    - Data requirements: [from Section 2]
    - External capabilities: [from Section 2]

    **User Interactions**:
    - User flows: [from Section 3]
    - Alternative paths: [from Section 3]
    - Error scenarios: [from Section 3]

    **Acceptance Criteria**:
    - Testable criteria: [from Section 4]
    - Success conditions: [from Section 4]
    - Edge cases: [from Section 4]

    **Integration Requirements**:
    - Systems to integrate: [from Section 5]
    - Data exchange: [from Section 5]

    **Out of Scope**: [list]
    **Open Questions**: [list]

    Create a comprehensive, well-formatted functional specification and save it to:
    docs/specs/[id]/YYYY-MM-DD--feature-name.md

    IMPORTANT:
    - This is a FUNCTIONAL specification, NOT a technical design
    - Do NOT mention any frameworks, libraries, or tools
    - Do NOT include code or pseudo-code
    - Focus on WHAT the system should do, not HOW
    - Use professional markdown structure",
  subagent_type: "developer-kit:document-generator-expert"
)
```

6. Wait for the document generator to complete
7. Verify the document was created successfully in `docs/specs/[id]/`
    - If the file was not created or is incomplete:
        - Check the subagent output for errors
        - Re-run Phase 6 with additional guidance if needed
        - Use AskUserQuestion to decide: "Retry generation", "Continue with manual creation", or "Abort"

8. **CRITICAL: Save brainstorming context files for later use by spec-to-tasks**:
    - If you have conversation context or notes about the feature (from the dialogue with user), save them to the spec
      folder
    - Create a file named `brainstorming-notes.md` in `docs/specs/[id]/` with:
        - Key technical decisions discussed
        - Architecture patterns mentioned
        - Any specific technologies or integrations requested
        - Notes about implementation approach
    - This file will be read by `devkit.spec-to-tasks` to ensure technical details are NOT lost

8.5. **Create decision-log.md for decision audit trail**:

- Create a file `decision-log.md` in `docs/specs/[id]/` with the following format:
  ```markdown
  # Decision Log: [Feature Name]
  
  | ID | Date | Task | Decision | Alternatives | Impact | Decided By |
  |----|------|------|----------|--------------|--------|------------|
  
  ## DEC-001: Approach Selection
  - **Date**: [current date YYYY-MM-DD]
  - **Task**: Brainstorming
  - **Phase**: Approach Selection
  - **Context**: Selection of functional approach for feature specification
  - **Decision**: [Approach chosen - A/B/C]
  - **Alternatives Considered**: [Brief description of approaches presented]
  - **Impact**: Specification structure, scope boundaries, acceptance criteria
  - **Decided By**: user selection
  ```
- This file will track all non-trivial decisions made during implementation
- Future phases (task-implementation, task-review) will append entries to this file

9. Update todos

---

## Phase 7: Specification Review

**Goal**: Review the generated functional specification for quality and completeness

**IMPORTANT**: The functional specification should be technology-agnostic (WHAT), but technical details discussed during
brainstorming are preserved separately in `brainstorming-notes.md` for use by `spec-to-tasks`.

**Actions**:

1. Use the Task tool to launch a code-reviewer subagent to review the specification:

```
Task(
  description: "Review functional specification quality",
  prompt: "Review the functional specification at docs/specs/[id]/YYYY-MM-DD--feature-name.md for:

    1. **Completeness**: All required sections are present (Business Context, Functional Requirements, User Interactions, Acceptance Criteria, Integration Requirements, Out of Scope, Open Questions)

    2. **Functional Focus**: Verify the specification is purely functional:
       - NO mention of frameworks, libraries, or tools
       - NO technical patterns or architectural styles
       - NO code or pseudo-code
       - Focuses on WHAT, not HOW

    3. **Quality**: Content is clear, specific, and actionable

    4. **Testability**: Acceptance criteria are clear and testable

    5. **Formatting**: Proper markdown structure, consistent formatting

    6. **Clarity**: Language is professional, concise, and unambiguous

    Provide:
    - Overall assessment (Excellent / Good / Needs Revision)
    - List of any missing sections or content
    - Specific issues found (if any)
    - Any technical details that should be removed
    - Recommendations for improvement (if needed)",
  subagent_type: "developer-kit:general-code-reviewer"
)
```

2. Once the agent returns, synthesize the review findings

3. **Use the AskUserQuestion tool to present the review findings**:

   Present options based on agent assessment:
    - **Option A**: Document is excellent, proceed to next steps
    - **Option B**: Minor revisions needed (agent will specify what)
    - **Option C**: Major revisions needed (regenerate with corrections)

4. If revisions are needed:
    - For minor revisions: Edit the document directly based on agent feedback
    - For major revisions: Re-run Phase 6 with updated instructions from agent
    - Optionally: Re-run Phase 7 with another review if significant changes were made

5. Once approved, mark documentation phase complete

---

## Phase 8: Next Steps Recommendation

**Goal**: Recommend the appropriate next command in the workflow

**Actions**:

1. The functional specification is complete. The next step is to convert it to executable tasks:

   **For converting specification to tasks**: Recommend `/developer-kit:devkit.spec-to-tasks`
    - Use when: Converting functional specification to trackable tasks
    - Arguments: `--lang=[language] docs/specs/[id]/`

2. **Use the AskUserQuestion tool to present the recommendation**:

   Present options:
    - **Option A**: Run spec-review first, then generate tasks (recommended)
    - **Option B**: Skip review and go directly to task generation (warning: may have quality issues)
    - **Option C**: Exit and review the specification manually

3. Include the pre-filled command:

3. Include the pre-filled commands:

```bash
# Recommended: Run spec-review first, then generate tasks
/developer-kit:devkit.spec-review docs/specs/[id]/
/developer-kit:devkit.spec-to-tasks --lang=[java|spring|typescript|nestjs|react|python|general] docs/specs/[id]/

# Alternative: Skip review and generate tasks directly
/developer-kit:devkit.spec-to-tasks --lang=[java|spring|typescript|nestjs|react|python|general] docs/specs/[id]/
```   - The functional specification has been saved at `docs/specs/[id]/YYYY-MM-DD--feature-name.md`
   - The task list will be saved at `docs/specs/[id]/YYYY-MM-DD--feature-name--tasks.md`
   - Individual tasks will be in `docs/specs/[id]/tasks/TASK-XXX.md`

---

## Phase 9: Summary

**Goal**: Document what was accomplished

**Actions**:

1. Mark all todos complete
2. Summarize:
    - **Original Idea**: What was brainstormed
    - **Approach Selected**: Which approach was chosen and why
    - **Integration Context**: Key integration requirements (if any)
    - **Functional Specification Created**: Key aspects of the specification
    - **Spec ID**: `[id]` (e.g., `001-hotel-search-aggregation`)
    - **Document Location**: `docs/specs/[id]/YYYY-MM-DD--feature-name.md`
    - **Specification Review**: Review outcome and any revisions made
    - **Recommended Next Step**: Generate task list with `devkit.spec-to-tasks`

---

## Integration with Development Commands

This brainstorming command produces a **functional specification** that feeds into the new modular workflow:

### New Output Flow

```

/developer-kit:devkit.brainstorm
↓
Phase 4: Optional Codebase Exploration (for integration context only)
↓
Phase 5: Functional Specification Presentation (validated incrementally)
↓
Phase 6: Documentation (document-generator-expert agent)
↓
Phase 7: Specification Review (quality verification)
↓
[Creates: docs/specs/[id]/YYYY-MM-DD--feature-name.md]
↓
[Recommends: devkit.spec-to-tasks]
↓
/developer-kit:devkit.spec-to-tasks --lang=[language] docs/specs/[id]/
↓
[Creates: docs/specs/[id]/YYYY-MM-DD--feature-name--tasks.md]
[Creates: docs/specs/[id]/tasks/TASK-XXX.md]
↓
/developer-kit:devkit.task-implementation --lang=[language] --task="docs/specs/[id]/tasks/TASK-XXX.md"
↓
[Implements single task]

```

### Specification as Reference

The functional specification created by this command serves as:

1. **Reference during implementation**: The development commands can read the specification for context
2. **Communication tool**: Can be shared with team members for review
3. **Documentation**: Becomes part of project's functional specification history
4. **Task generation input**: Used by `devkit.spec-to-tasks` to create executable tasks
5. **Organized storage**: All related files (spec, tasks, individual tasks) are grouped in `docs/specs/[id]/`

### Re-entering Brainstorming

If implementation reveals specification issues, you can re-run `/developer-kit:devkit.brainstorm`:
- The previous specification will be preserved in its folder
- A new specification will be created with the current date
- You can reference the previous specification during the new brainstorming session

## Todo Management

Throughout the process, maintain a todo list like:

```

[ ] Phase 1: Context Discovery
[ ] Phase 2: Idea Refinement
[ ] Phase 3: Functional Approach Exploration
[ ] Phase 4: Contextual Codebase Exploration (Optional)
[ ] Phase 5: Functional Specification Presentation
[ ] Section 1: Business Context
[ ] Section 2: Functional Requirements
[ ] Section 3: User Interactions
[ ] Section 4: Acceptance Criteria
[ ] Section 5: Integration Requirements
[ ] Phase 6: Functional Specification Generation
[ ] Phase 7: Specification Review
[ ] Phase 8: Next Steps Recommendation
[ ] Phase 9: Summary

```

Update the status as you progress through each phase and section.

---

**Note**: This command follows a collaborative, iterative approach with specialist agents to ensure designs are:
- Based on actual codebase exploration (not assumptions)
- Well-thought-out and validated incrementally
- Documented professionally with specialist assistance
- Reviewed for quality before proceeding
- Ready for implementation with clear next steps

--- 

## Examples

### Example 1: Simple Feature Idea

```bash
/developer-kit:devkit.brainstorm Add user authentication with JWT tokens
```

### Example 2: Complex Feature

```bash
/developer-kit:devkit.brainstorm Implement real-time notifications using WebSockets
```

### Example 3: Refactoring

```bash
/developer-kit:devkit.brainstorm Refactor the payment processing module to be more maintainable
```

### Example 4: Bug Fix Design

```bash
/developer-kit:devkit.brainstorm Design a fix for the race condition in order processing
```

### Example 5: Performance Improvement

```bash
/developer-kit:devkit.brainstorm Design a caching strategy to reduce API response times
```

### Example 6: Integration

```bash
/developer-kit:devkit.brainstorm Integrate Stripe payment processing for subscriptions
```

### Example 7: Full Workflow (after brainstorming)

```bash
# Step 1: Brainstorm and generate functional specification
/developer-kit:devkit.brainstorm Design a microservices architecture for the reporting module

# Step 2: Convert specification to tasks
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/001-reporting-module/

# Step 3: Implement specific tasks
/developer-kit:devkit.task-implementation --lang=spring --task="docs/specs/001-reporting-module/tasks/TASK-001.md"
/developer-kit:devkit.task-implementation --lang=spring --task="docs/specs/001-reporting-module/tasks/TASK-002.md"
```

This separates WHAT (functional specification) from HOW (implementation), following the "divide et impera" principle.
