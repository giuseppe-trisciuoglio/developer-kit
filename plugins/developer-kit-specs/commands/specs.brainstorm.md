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
Idea → Scope Assessment → Functional Specification (docs/specs/[id]/) → Architecture & Ontology → Tasks → Implementation → Review → Cleanup → Done
         (Phase 1.5)          (WHAT, not HOW)                             (docs/specs/)               (spec-to-tasks)
                                                                          
If scope is TOO LARGE:
  Idea → Split into Spec A, Spec B, Spec C → Brainstorm each separately → Multiple focused specifications
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
/developer-kit-specs:specs.brainstorm [idea-description]
```

After generating the functional specification, continue with:

```bash
/developer-kit-specs:specs.spec-to-tasks docs/specs/[id]/
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
- **ADR constraint preservation**: When the input is an ADR, RFC, or technical analysis document, the architectural decisions it contains are treated as **immutable constraints** for the functional specification. If the brainstorming process identifies a need to override an ADR decision, the override MUST be explicitly documented in `decision-log.md` with a DEC entry referencing the original ADR.
- **Incremental validation**: Present specification in sections, validate each
- **Professional documentation**: Use specialist agent for high-quality documents
- **Be flexible**: Go back and clarify when something doesn't make sense
- **Use TodoWrite**: Track all progress throughout
- **No time estimates**: DO NOT provide or request time estimates
- **Scope awareness**: Validate idea scope early; if too large, guide user to split into multiple focused specifications

---

## Phase 0: Input Mode Detection & ADR Discovery

**Goal**: Determine whether the input is a free-form idea, an ADR/RFC, or a structured analysis document. If the input is a structured document, extract architectural decisions as constraints before proceeding.

**Context**: The `$ARGUMENTS` parameter may contain:
- A free-text idea (e.g., "Add user authentication with JWT tokens")
- A path to an existing document (e.g., `@docs/adr/039-git-worktree-management.md`)
- A reference to a file containing architectural decisions, RFC, or analysis

**Actions**:

1. **Detect input mode**:
   - If `$ARGUMENTS` contains a file path pattern (starts with `/`, `./`, `docs/`, or `@docs/`): **Structured Document Mode**
   - If `$ARGUMENTS` is free text describing a feature: **Free-Form Idea Mode**
   - If `$ARGUMENTS` is empty: Ask user for input and detect mode from their response

2. **If Structured Document Mode**:
   - Read the referenced document
   - Extract all **architectural decisions** documented in the file:
     - Configuration values, defaults, and file paths
     - CLI flags and command structures proposed
     - Integration patterns with existing systems
     - Error handling and edge-case strategies
     - Directory structures and documentation conventions
   - Create a `constraints` list in memory with the extracted decisions
   - **Do NOT re-evaluate these decisions** — they are the architectural foundation. The functional specification must work within them.
   - If a decision in the ADR contradicts project conventions (e.g., architecture.md, ontology.md), flag it as a conflict, not as a candidate for change

3. **If Free-Form Idea Mode**:
   - Proceed directly to Phase 1 — no constraints to extract
   - The brainstorming will discover all decisions collaboratively

4. **Decision override protocol**:
   - If during brainstorming you identify that an ADR decision should be overridden:
     - Create a DEC entry in `decision-log.md` with:
       - Reference to the original ADR (e.g., "Overrides ADR-039, Section 3: Configuration")
       - Justification for the override
       - Impact on the specification
     - Only then modify the constraint
   - Without a DEC entry, ADR constraints remain immutable

5. **Summarize constraints** (Structured Document Mode only):
   - After extraction, produce a brief summary:
   ```
   Input Mode: Structured Document (ADR-039)
   Constraints extracted:
   - Config: worktreeBasePath (default: ../<repo-name>-worktrees)
   - CLI: No explicit flags mentioned
   - Integration: ADR-038 branch creation
   - Behavior: Worktree creation + manual cleanup command
   Override DEC entries: None / DEC-XXX
   ```

---

## Phase 1: Context Discovery

**Goal**: Understand the current project state and the initial idea, within the bounds of any extracted constraints

**Initial idea**: $ARGUMENTS

**Actions**:

1. Create todo list with all phases (including Phase 0 if Structured Document Mode)
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
        - Recommend switching to `/developer-kit-specs:specs.quick-spec` for faster turnaround
        - Ask via AskUserQuestion:
            - Options:
                - "Continue with full brainstorming" (for comprehensive spec)
                - "Switch to quick spec" (recommended for bug fixes/small changes)
    - **Standard** (feature, moderate scope, 3-10 files): Continue with brainstorm
    - **Full** (greenfield, complex, >10 files or multiple modules): Continue with brainstorm + recommend spec-check
      after

---

## Phase 1.5: Complexity Assessment & Scope Validation

**Goal**: Assess idea complexity early and guide user to split if scope is too large for a single specification

**Actions**:

1. **Estimate implementation scope** based on the idea description and context from Phase 1:
   - Count distinct user stories / use cases mentioned
   - Identify separate functional domains or bounded contexts
   - Note integration points with external systems
   - Assess data model complexity (entities, relationships)
   - Evaluate user interaction complexity (flows, edge cases)

2. **Classify scope size** using these indicators:

   **Small Scope** (proceed normally - will generate 3-8 tasks):
   - Single user story or use case
   - One functional domain
   - 0-2 integration points
   - Simple data model (1-3 entities)
   - Straightforward user flow
   - Examples: "Add password reset", "Implement search filter", "Add user profile photo upload"

   **Medium Scope** (proceed normally - will generate 8-15 tasks):
   - 2-4 user stories
   - One focused functional domain
   - 2-4 integration points
   - Moderate data model (4-8 entities)
   - Multiple user flows but related
   - Examples: "User authentication with roles", "Product catalog with categories"

   **Large Scope** (WARNING - will likely generate >15 tasks - see step 3):
   - 5+ user stories
   - Multiple functional domains or bounded contexts
   - 5+ integration points
   - Complex data model (9+ entities)
   - Multiple independent user flows
   - Examples: "Full E-commerce system", "Multi-provider travel aggregator", "Complete CRM system"

3. **If scope is classified as LARGE**:
   - **Inform the user**: "This idea has a very large scope. To ensure high-quality implementation and maintainable code, I recommend splitting it into smaller, focused specifications."
   - **Propose a split strategy**: Suggest 2-3 smaller specifications that cover the original idea incrementally.
     - Example split:
       - Spec 1: Core domain and data model
       - Spec 2: Primary user flows and API
       - Spec 3: Advanced features and integrations
   - **Use AskUserQuestion** to offer options:
     - Options:
       - "Split the idea into the suggested specifications" (recommended)
       - "Focus only on one part of the idea" (ask which one)
       - "Continue with a single large specification" (not recommended - warn about task count limit)
   - If user chooses to split: Focus the current brainstorming session on the FIRST part of the split.
   - If user chooses to focus on one part: Focus the current session on that part.
   - If user chooses to continue: Proceed with a warning that `spec-to-tasks` will reject the spec if it exceeds 15 tasks.

---

## Phase 2: Idea Refinement

**Goal**: Clarify the requirements and constraints through a dialogue with the developer

**Actions**:

1. Ask up to 3 targeted questions to refine the idea:
    - Focus on ambiguities or missing information
    - Ask about edge cases or specific behaviors
    - Ask about integration with existing features
2. Incorporate any extracted constraints from Phase 0 into your questions
3. If the user provides a lot of information, summarize it to ensure alignment
4. If the user changes the idea significantly, restart the refinement phase

---

## Phase 5: Specification Generation

**Goal**: Generate a comprehensive functional specification document

**Actions**:

1. Define the specification ID and folder: `docs/specs/[id]/`
2. Generate the main specification file: `docs/specs/[id]/YYYY-MM-DD--feature-name.md`
3. Use a professional, academic style (refer to specialist agent if available)
4. Include the following sections:
    - **Overview**: High-level description and goals
    - **User Stories**: Functional requirements from the user's perspective
    - **Functional Requirements**: Detailed description of what the system should do
    - **Acceptance Criteria**: Testable conditions for each requirement
    - **Domain Model**: High-level description of entities and relationships
    - **User Interaction Flow**: Description of how users interact with the feature
    - **Non-Functional Requirements**: Performance, security, and scalability constraints
    - **Edge Cases & Error Handling**: How the system handles unusual situations
5. **Insert [NEEDS CLARIFICATION] markers** when required (see `[NEEDS CLARIFICATION] Markers` section below)
6. **CRITICAL: Save the original user context**:
   - Save the initial user request and key brainstorming dialogue to `docs/specs/[id]/user-request.md`
   - Save any significant notes, alternative approaches considered, or research findings to `docs/specs/[id]/brainstorming-notes.md`
   - These files provide essential context for subsequent commands like `spec-to-tasks`
7. Ensure the specification is pure WHAT and does not mention HOW (frameworks, patterns, code)
8. Incorporate all extracted constraints from Phase 0 and decisions from Phase 3

---

---

### [NEEDS CLARIFICATION] Markers

When writing the specification, mark unclear aspects that require user input. This creates a bidirectional link with `specs.spec-check` which resolves these markers.

**When to use a marker**:

Mark with `[NEEDS CLARIFICATION: specific question]` ONLY when ALL of these are true:
1. The choice **significantly impacts feature scope** or user experience
2. **Multiple reasonable interpretations exist** with different implications
3. **No reasonable default exists** for the domain

**When NOT to use a marker** (make an informed guess instead):

| Area | Reasonable Default | Do NOT mark |
|------|-------------------|-------------|
| Data retention | Industry-standard for domain | Guess and document |
| Performance targets | Standard web/mobile expectations | Guess and document |
| Error handling | User-friendly messages + fallbacks | Guess and document |
| Auth method | Session-based or OAuth2 for web | Guess and document |
| Integration patterns | REST/GraphQL for web, function calls for libs | Guess and document |
| UI/UX details | Standard responsive design, standard patterns | Guess and document |
| Input validation | Standard type/range/boundary checks | Guess and document |

**Marker syntax**:

```markdown
The system must support [NEEDS CLARIFICATION: which payment providers should be supported at launch?] for processing transactions.
```

The marker is placed INLINE within the requirement text. It does not replace the requirement — the requirement still stands with a best-guess default. The marker flags the uncertainty.

**Rules**:

- **Maximum 3 markers total** across the entire specification
- **Prioritize by impact**: scope > security/privacy > user experience > technical details
- Each marker must contain a **specific question** (not a vague "needs clarification")
- The surrounding requirement text should still be meaningful with the default assumption
- Do NOT create a separate "Needs Clarification" section — markers are inline

**Examples of good markers**:

```markdown
# Good: specific, scope-impacting
The system must process refunds [NEEDS CLARIFICATION: should refunds be automatic or require manual approval?] within 5 business days.

# Good: security-impacting
User data must be retained [NEEDS CLARIFICATION: what is the data retention period required by GDPR/compliance?] according to regulatory requirements.

# Good: UX-impacting with multiple interpretations
Search results should be sorted [NEEDS CLARIFICATION: by relevance, recency, price, or user-selectable?] by default.
```

**Examples of bad markers** (should be guessed instead):

```markdown
# Bad: has reasonable default (REST API)
The system must expose [NEEDS CLARIFICATION: REST or GraphQL?] endpoints.
→ Default: REST. Document assumption in Assumptions section.

# Bad: too vague
The system must be [NEEDS CLARIFICATION: fast?] for all users.
→ Bad marker. Make it measurable: "The system must respond to user actions within 2 seconds."

# Bad: implementation detail (not scope-level)
The database should use [NEEDS CLARIFICATION: PostgreSQL or MySQL?] for storage.
→ This is an implementation decision, not a spec-level ambiguity. Don't mark.
```

**After spec generation**:

If any markers were placed, include a note in the completion summary:
```
Specification created with 2 [NEEDS CLARIFICATION] markers:
  1. "Which payment providers should be supported?"
  2. "Should guest checkout be allowed?"

Next: Run /developer-kit-specs:specs.spec-check to resolve.
```

## Phase 6: Specification Review

**Goal**: Ensure the generated specification is clear, complete, and consistent

**Actions**:

1. Read the entire generated specification
2. Check for:
    - Ambiguities or vague language
    - Missing requirements or edge cases
    - Consistency with project conventions
    - Adherence to the WHAT vs. HOW principle
3. Verify that [NEEDS CLARIFICATION] markers follow the rules (max 3, specific questions, inline)
4. If issues are found, update the specification accordingly
5. If the user provides feedback, incorporate it into the document

---

## Phase 7: Next Steps Recommendation

**Goal**: Guide the developer to the next phase of the workflow

**Actions**:

1. Summarize the generated specification
2. If [NEEDS CLARIFICATION] markers exist: list them in the summary
3. Provide the command to generate tasks: `/developer-kit-specs:specs.spec-to-tasks docs/specs/[id]/`
4. If the specification is complex or has markers, recommend running `/developer-kit-specs:specs.spec-check docs/specs/[id]/` first
5. Report: spec file path + marker count + next step (spec-check)
6. Log completion of the brainstorming workflow
