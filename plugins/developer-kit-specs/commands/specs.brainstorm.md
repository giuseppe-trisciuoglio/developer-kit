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

## Arguments

| Argument           | Required | Description                                      |
|--------------------|----------|--------------------------------------------------|
| `idea-description` | No       | Description of the idea or feature to brainstorm |

## Current Context

### Basic Usage

```bash
/developer-kit-specs:specs.brainstorm Add user authentication with email and password
```

### With External Input

```bash
/developer-kit-specs:specs.brainstorm @docs/adr/039-architecture-decisions.md
```

### After generating the spec

```bash
/developer-kit-specs:specs.spec-to-tasks docs/specs/001-feature/
```

## Examples

### Basic Usage

```bash
/developer-kit-specs:specs.brainstorm Add user authentication with email and password
```

### With External Input

```bash
/developer-kit-specs:specs.brainstorm @docs/adr/039-architecture-decisions.md
```

### After generating the spec

```bash
/developer-kit-specs:specs.spec-to-tasks docs/specs/001-feature/
```

## Argument Details

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

## Spec Lifecycle: Deliberate Death

Every specification has a limited lifespan. The spec is a living document that serves its purpose during implementation, but once the feature is built and verified, the spec transitions to a historical record.

### The Spec Is Dead, Long Live the Spec

| Phase | Spec State | Purpose |
|-------|------------|---------|
| **Creation** | Living document | Guide implementation decisions |
| **Implementation** | Reference artifact | Answer "what should this do?" |
| **Verification** | Validation checklist | Ensure spec compliance |
| **Completion** | Historical record | Audit trail, knowledge preservation |
| **Post-project** | Archived reference | Future maintenance and onboarding |

**The spec dies when:**
1. Implementation is complete and verified against the spec
2. The feature has been in production without spec-related issues
3. The spec has been superseded by a new version

**The spec is NOT deleted:**
- It becomes `archived/` in the spec folder
- It remains as historical record
- Future changes reference it as "original spec" or "preceding spec"

### Why "Deliberate Death"?

- Prevents spec rot: specs that never die become stale and misleading
- Encourages accurate specs: knowing a spec will be archived sharpens focus
- Supports knowledge transfer: archived specs provide valuable context
- Enables improvement: each spec lifecycle informs better next specs

### Spec Death Protocol

1. **During spec-to-tasks**: Spec is alive, every decision traces back to it
2. **During implementation**: Spec guides, deviations are documented
3. **During task-review**: Spec is validated against, findings trace to spec
4. **During spec-sync-with-code**: Spec is updated to reflect implemented behavior
5. **After completion**: Spec is archived, not deleted

**Archive command** (after feature completion):
```bash
mv docs/specs/[id]/YYYY-MM-DD--feature-name.md \
   docs/specs/[id]/archived/YYYY-MM-DD--feature-name.md
```

Add to `archived/README.md`:
```markdown
## [Date] - [Feature Name] - COMPLETED
- Implementation: complete
- Status: verified against spec
- Superseded by: [link or N/A]
```

---

## Requirement Syntax: EARS Standard

All functional requirements in the generated specification MUST use **EARS syntax** (Easy Approach to Requirements Syntax).

### Syntax Forms

| Form | Pattern | Example |
|------|---------|---------|
| **Event-driven** | `WHEN <event> THEN the system SHALL <action>` | `WHEN the user clicks "Submit" THEN the system SHALL validate the form data` |
| **State-driven** | `WHEN <system state> THEN the system SHALL <action>` | `WHEN the session expires THEN the system SHALL clear user data` |
| **Generic** | `The system SHALL <action>` | `The system SHALL encrypt all stored passwords with bcrypt` |
| **Feature** | `IF <feature> THEN the system SHALL <action>` | `IF multi-factor auth is enabled THEN the system SHALL require second factor` |
| **Negative** | `IF <unwanted condition> THEN the system SHALL <response>` | `IF SQL input detected THEN the system SHALL reject with 400` |

### Mandatory Keywords

- **SHALL** — obligation (use for MUST requirements)
- **WILL** — intention (use for planned features)
- **MAY** — permission (use for optional behaviors)

### Forbidden Words (cause ambiguity)

- "robust", "intuitive", "fast", "scalable", "efficient", "user-friendly"
- Replace with measurable criteria

### Requirement ID Format

- Format: `REQ-XXX` (e.g., `REQ-001`, `REQ-002`)
- Numbering: Sequential per spec
- Placement: Before each requirement text

### Example Good vs Bad

```markdown
# BAD (vague)
"The system must be fast and secure."

# GOOD (EARS)
"The system SHALL encrypt all stored passwords with bcrypt and cost factor ≥12."

# BAD (missing trigger)
"The user receives a confirmation email."

# GOOD (EARS)
"WHEN a purchase is completed THEN the system SHALL send a confirmation email to the customer's registered address."
```

### Validation Checklist

Before Phase 5 generation, verify:
- [ ] Every requirement has REQ-ID prefix
- [ ] Every requirement uses SHALL/WILL/MAY
- [ ] Every requirement has a trigger (WHEN/IF) or is generic
- [ ] No forbidden words present
- [ ] Each requirement is testable (can verify pass/fail)

## Non-Goals Enforcement

Every specification MUST include an explicit **"Non-Goals"** section that lists what the feature does NOT do.

**Purpose**: Prevent AI agent from adding "helpful" features outside the intended scope.

**Rules**:
1. If the feature doesn't include social login → add "No social login providers"
2. If the feature doesn't support real-time → add "No real-time updates or WebSocket support"
3. If there's no admin panel → add "No administrative interface"
4. Always include at least 3 non-goals

**Format**:
```markdown
## Non-Goals

This feature does NOT include:

- **Feature X**: [Brief explanation why excluded]
- **Feature Y**: [Brief explanation why excluded]
- **Feature Z**: [Brief explanation why excluded]
```

**Trigger Pattern**: "The system will NOT do X" or "X is out of scope for this feature"

### Common Non-Goals Templates (use as starting point)

#### Web Application
- No social login (OAuth, Google, GitHub, etc.)
- No multi-language support (English only)
- No real-time updates (no WebSocket, SSE, or polling)
- No offline mode or PWA support
- No mobile app (web-only)

#### Backend/API
- No GraphQL (REST only)
- No async processing (synchronous only)
- No caching layer
- No message queue integration
- No third-party integrations

#### Database/Data
- No data export functionality
- No data import/migration tools
- No backup/restore utilities
- No data archiving

#### Security
- No two-factor authentication
- No role-based access control (RBAC)
- No API key management
- No audit logging

#### Operations
- No monitoring/observability setup
- No CI/CD pipeline setup
- No containerization
- No deployment automation

**Rule**: Start with project-specific exclusions, then add domain-specific ones.

---

## Negative Requirements

Every specification SHOULD include explicit **"Negative Requirements"** that describe behaviors the system must NOT exhibit. These are constraints that prevent common failures, security issues, or anti-patterns.

### Purpose

- **Prevent failures**: Define what the system MUST NOT do to avoid known failure modes
- **Block security issues**: Specify anti-patterns that must never appear (SQL injection, XSS, etc.)
- **Document constraints**: Make implicit exclusions explicit for future maintainers
- **Guide implementation**: Help developers avoid dangerous patterns during implementation

### Negative Requirements vs Non-Goals

| Aspect | Non-Goals | Negative Requirements |
|--------|-----------|----------------------|
| **Focus** | Features NOT included in this spec | Behaviors the system MUST NOT exhibit |
| **Type** | Scope exclusions (what we don't build) | Anti-patterns/prevention (how we don't build it) |
| **Example** | "No social login" | "The system SHALL NOT store passwords in plain text" |
| **Validation** | Is feature X built? | Does behavior Y occur in implementation? |

### Common Categories

**Security Constraints** (OWASP Top 10 based):
- No SQL string concatenation (use parameterized queries)
- No eval() or dynamic code execution
- No hardcoded credentials or secrets
- No user-generated content without sanitization
- No insecure direct object references

**Data Integrity Constraints**:
- No lost updates (optimistic locking or versioning)
- No data loss on concurrent operations
- No state corruption on failure

**Performance Constraints**:
- No N+1 query patterns
- No blocking operations in request handlers
- No unbounded data structures

**Reliability Constraints**:
- No silent failures (errors must be logged)
- No single points of failure without mitigation
- No data inconsistency across services

### Template Format

```markdown
## Negative Requirements

The system SHALL NOT:

### Security
- [Constraint 1 with REQ-ID]
- [Constraint 2 with REQ-ID]

### Data Integrity
- [Constraint 3 with REQ-ID]

### Reliability
- [Constraint 4 with REQ-ID]
```

### EARS Syntax for Negative Requirements

| Pattern | Example |
|---------|---------|
| **Negative** | `IF <unwanted condition> THEN the system SHALL NOT <action>` |
| **Prevention** | `The system SHALL NOT <unsafe behavior>` |

Example:
```markdown
## Negative Requirements

The system SHALL NOT:

### Security
- REQ-NR001: IF user input is used in SQL query THEN the system SHALL NOT concatenate directly; it SHALL use parameterized queries with placeholders
- REQ-NR002: The system SHALL NOT store passwords in plain text; it SHALL use bcrypt with cost factor ≥12

### Data Integrity
- REQ-NR003: The system SHALL NOT allow concurrent updates to overwrite each other without detection; it SHALL implement optimistic locking
```

### Generating Negative Requirements

During Phase 5, identify negative requirements by asking:
1. "What failures could occur if we don't specify this?"
2. "What security issues could happen with this feature?"
3. "What anti-patterns might developers use?"
4. "What race conditions or data corruption could happen?"

### Validation Checklist

- [ ] At least 3 Negative Requirements present
- [ ] Each has REQ-NR prefix and EARS syntax
- [ ] Categories are identified (Security, Data Integrity, Reliability)
- [ ] No contradictions with positive requirements
- [ ] Directly traceable to anti-patterns or known failure modes

---

## [NEEDS CLARIFICATION] Marker Rules

Every specification may include `[NEEDS CLARIFICATION]` markers to identify areas requiring user input. However, to prevent specification bloat and ensure actionable outcomes, markers are **strictly limited to 3 maximum**.

### Why Maximum 3?

- **Focus**: Each marker represents a significant scope decision. Too many markers indicate the spec is not ready.
- **Actionability**: Resolving markers requires user time. More than 3 creates friction.
- **Quality over quantity**: Better to have 3 well-defined markers than 10 vague ones.

### Marker Requirements

| Requirement | Description |
|-------------|-------------|
| **Max 3 markers** | No specification shall have more than 3 [NEEDS CLARIFICATION] markers total |
| **Specific questions** | Each marker must contain a specific, answerable question |
| **Inline placement** | Markers appear inline within requirement text, not as a separate section |
| **Impact prioritization** | Markers are prioritized: scope > security/privacy > user experience > technical |

### When to Use a Marker

Mark with `[NEEDS CLARIFICATION: specific question]` ONLY when ALL of these are true:
1. The choice **significantly impacts feature scope** or user experience
2. **Multiple reasonable interpretations exist** with different implications
3. **No reasonable default exists** for the domain

### When NOT to Use a Marker (Make an Informed Guess Instead)

| Area | Reasonable Default | Do NOT Mark |
|------|-------------------|-------------|
| Data retention | Industry-standard for domain | Guess and document |
| Performance targets | Standard web/mobile expectations | Guess and document |
| Error handling | User-friendly messages + fallbacks | Guess and document |
| Auth method | Session-based or OAuth2 for web | Guess and document |
| Integration patterns | REST/GraphQL for web, function calls for libs | Guess and document |
| UI/UX details | Standard responsive design, standard patterns | Guess and document |
| Input validation | Standard type/range/boundary checks | Guess and document |

### Marker Syntax

```markdown
The system must support [NEEDS CLARIFICATION: which payment providers should be supported at launch?] for processing transactions.
```

The marker is placed **INLINE** within the requirement text. It does not replace the requirement — the requirement still stands with a best-guess default.

### Marker Validation Checklist

Before Phase 5 generation, verify:
- [ ] Maximum 3 markers present in the specification
- [ ] Each marker has a specific question (not vague "needs clarification")
- [ ] Markers are inline within requirement text
- [ ] Markers are prioritized by impact (scope > security > UX > technical)
- [ ] No markers for areas with reasonable defaults

### Marker Enforcement Examples

```markdown
# GOOD: Specific question, high impact
The system SHALL process payments via [NEEDS CLARIFICATION: which payment providers should be supported at launch?] (Stripe, PayPal, or both?)

# BAD: Vague question
The system SHALL support payments via [NEEDS CLARIFICATION: what should we support?] (unspecified)

# BAD: Technical detail (has reasonable default)
The database should use [NEEDS CLARIFICATION: PostgreSQL or MySQL?] for storage.
→ Default: PostgreSQL. Document assumption in Assumptions section.

# BAD: Has reasonable default (REST API)
The system must expose [NEEDS CLARIFICATION: REST or GraphQL?] endpoints.
→ Default: REST. Document assumption in Assumptions section.
```

### Marker Count Validation in Phase 5

After generating the specification:
1. Count all `[NEEDS CLARIFICATION:` occurrences
2. If count > 3: Flag the spec and identify the excess markers
3. For excess markers: Either convert to a best-guess assumption OR defer to a future spec-check session
4. Report final marker count in the completion summary

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
    - **Bug fix** (defect in existing system):
        - Recommend `/developer-kit-specs:specs.change-spec --type=bugfix` for root cause analysis and regression prevention
        - Ask via AskUserQuestion:
            - Options:
                - "Continue with change-spec" (recommended for bug fixes)
                - "Continue with brainstorm" (for new features)
    - **New feature** (any scope): Continue with brainstorm
    - **Modify existing** (delta): Continue with change-spec

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
    - Ask about **exclusions and negative requirements** (what should the system NOT do?)
2. Incorporate any extracted constraints from Phase 0 into your questions
3. If the user provides a lot of information, summarize it to ensure alignment
4. If the user changes the idea significantly, restart the refinement phase

**Negative Requirements Question**:
During Phase 2, ask about exclusions that could become Negative Requirements:
- "Are there security constraints or anti-patterns we must avoid?"
- "Are there known failure modes or race conditions to prevent?"
- "Are there data integrity constraints beyond normal validation?"

---

## Phase 5.3: Non-Goals Definition

**Goal**: Explicitly define what this feature does NOT include

**Actions**:

1. **Review the idea description** and identify:
   - What was explicitly mentioned as out of scope
   - What was mentioned as in scope
   - Common related features that could be assumed

2. **Brainstorm potential Non-Goals** by asking:
   - "What would a developer naturally assume but is NOT in scope?"
   - "What related features could be 'helpful' but are excluded?"
   - "What technical capabilities are related but not required?"

3. **Generate Non-Goals list** (minimum 3):
   - Platform limitations (e.g., "No mobile app", "No offline mode")
   - Feature exclusions (e.g., "No social login", "No real-time sync")
   - Scope boundaries (e.g., "No multi-tenancy", "No plugin system")
   - Technical exclusions (e.g., "No WebSocket", "No GraphQL")

4. **Format each Non-Goal**:
   - Bold the excluded feature name
   - One sentence explaining why it's excluded
   - Connects to business logic when possible

**Output**:
```markdown
## Non-Goals

This feature does NOT include:

- **Social Login**: Only email/password authentication is supported
- **Multi-language Support**: Interface is English only
- **Real-time Updates**: No WebSocket or SSE support
- **Admin Panel**: User management done via database directly
- **Export/Import**: No data migration utilities
```

**Validation**:
- [ ] Minimum 3 Non-Goals present
- [ ] Each Non-Goal has explanation
- [ ] No contradictions with functional requirements
- [ ] Non-Goals are mutually exclusive with requirements

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
    - **Functional Requirements**: Detailed description using EARS syntax (REQ-XXX format)
    - **Acceptance Criteria**: Testable conditions for each requirement
    - **Domain Model**: High-level description of entities and relationships
    - **User Interaction Flow**: Description of how users interact with the feature
    - **Non-Functional Requirements**: Performance, security, and scalability constraints
    - **Non-Goals**: What this feature does NOT include (minimum 3 items with explanations)
    - **Edge Cases & Error Handling**: How the system handles unusual situations
5. **Insert [NEEDS CLARIFICATION] markers** when required (see `[NEEDS CLARIFICATION] Markers` section below)
6. **CRITICAL: Save the original user context**:
   - Save the initial user request and key brainstorming dialogue to `docs/specs/[id]/user-request.md`
   - Save any significant notes, alternative approaches considered, or research findings to `docs/specs/[id]/brainstorming-notes.md`
   - These files provide essential context for subsequent commands like `spec-to-tasks`
7. Ensure the specification is pure WHAT and does not mention HOW (frameworks, patterns, code)
8. Incorporate all extracted constraints from Phase 0 and decisions from Phase 3
8. **Apply EARS syntax** to all functional requirements:
   - Each requirement must have `REQ-XXX` prefix
   - Each requirement must use SHALL/WILL/MAY keywords
   - Event-driven requirements must have WHEN/IF trigger
   - Generic requirements (no trigger) are allowed but minimize them
   - No forbidden words (robust, fast, intuitive, etc.)
9. **Include Non-Goals section** (minimum 3 items with explanations)
10. **Include Negative Requirements section** (security constraints, data integrity, reliability - minimum 3 items with REQ-NR prefix)

---

## Phase 5.5: EARS Validation

**Goal**: Ensure all requirements follow EARS syntax before finalizing the spec

**Actions**:

1. **Parse all requirements** in the generated spec:
   - Extract requirements with `REQ-XXX` pattern
   - Identify requirements that lack REQ-ID

2. **Validate each requirement**:
   - Has REQ-ID prefix?
   - Uses SHALL/WILL/MAY keyword?
   - Has trigger (WHEN/IF) or is generic (no trigger)?
   - Contains forbidden words?

3. **Fix violations**:
   - Add missing REQ-IDs
   - Restructure requirements missing triggers
   - Replace forbidden words with measurable alternatives

4. **Document non-requirements**:
   - Explanatory text (not requirements) should NOT have REQ-ID
   - Notes and rationale are exempt from EARS syntax

5. **Update requirement count**:
   - Report final REQ count in summary
   - Flag if >50% of requirements are generic (may indicate missing triggers)

**Output**: EARS-compliant requirements section with validation report

Example output snippet:

```markdown
## Functional Requirements

### Authentication (4 requirements)

**Context**: User login and session management

| ID | Requirement | Trigger Type |
|----|-------------|--------------|
| REQ-001 | The system SHALL validate credentials against the user database | Event (login attempt) |
| REQ-002 | The system SHALL lock account after 5 failed attempts | Event (failed attempt) |
| REQ-003 | WHEN session expires THEN the system SHALL clear user data | State transition |
| REQ-004 | The system SHALL encrypt all passwords with bcrypt cost ≥12 | Generic |
```

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

**Goal**: Ensure the generated specification is clear, complete, consistent, and EARS-compliant

**Actions**:

1. Read the entire generated specification
2. Check for:
    - Ambiguities or vague language
    - Missing requirements or edge cases
    - Consistency with project conventions
    - Adherence to the WHAT vs. HOW principle
3. **Validate [NEEDS CLARIFICATION] markers**:
   - [ ] Maximum 3 markers present
   - [ ] Each marker has specific, answerable question
   - [ ] Markers are inline within requirement text
   - [ ] No markers for areas with reasonable defaults
4. **Validate Non-Goals section**:
   - [ ] Non-Goals section exists
   - [ ] At least 3 Non-Goals listed
   - [ ] Each Non-Goal has explanation
   - [ ] No contradicting requirements
5. **Validate Negative Requirements section**:
   - [ ] Negative Requirements section exists
   - [ ] At least 3 Negative Requirements listed
   - [ ] Each has REQ-NR prefix
   - [ ] EARS syntax used (SHALL NOT)
   - [ ] Categories identified (Security, Data Integrity, Reliability)
6. **Validate EARS compliance**:
   - [ ] All functional requirements have REQ-ID prefix
   - [ ] All requirements use SHALL/WILL/MAY keywords
   - [ ] Event-driven requirements have clear WHEN/IF triggers
   - [ ] No forbidden words present (robust, fast, intuitive, etc.)
   - [ ] Each requirement is independently testable
   - [ ] Non-requirements (explanatory text) are clearly marked without REQ-ID
6. If issues are found, update the specification accordingly
7. If the user provides feedback, incorporate it into the document
8. **Enforce Spec Death Awareness**: Verify spec is complete and well-defined — a spec that dies before completion becomes technical debt

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
7. **Remind about Spec Lifecycle**: After implementation is complete, run `/specs:spec-sync-with-code` then archive the spec to `archived/` folder. A spec that lives forever becomes stale documentation.

---

## Complete Template with Negative Requirements

When generating a specification, use this complete section structure:

```markdown
## Functional Requirements

[Positive requirements with REQ-XXX prefix using EARS syntax]

## Negative Requirements

The system SHALL NOT:

### Security
- REQ-NR001: [Security constraint - SHALL NOT pattern]
- REQ-NR002: [Another security constraint]

### Data Integrity
- REQ-NR003: [Data integrity constraint]
- REQ-NR004: [Another data integrity constraint]

### Reliability
- REQ-NR005: [Reliability constraint]

## Non-Goals

This feature does NOT include:
- **Feature X**: [Explanation why excluded]
- **Feature Y**: [Explanation why excluded]

## Acceptance Criteria

[Criteria organized by requirement ID]

## Edge Cases & Error Handling

[Describe how system handles unusual situations]

## Domain Model

[High-level entities and relationships]

## User Interaction Flows

[How users interact with the feature]
```

### Negative Requirements Integration Points

| Phase | Where Negative Requirements Appear |
|-------|-------------------------------------|
| Phase 2 (Idea Refinement) | Ask about anti-patterns to prevent |
| Phase 5 (Generation) | Generate Negative Requirements section |
| Phase 5.3 (Non-Goals) | Distinguish from Negative Requirements |
| Phase 6 (Review) | Validate Negative Requirements completeness |
| Phase 6 (Review) | Validate EARS negative syntax (SHALL NOT) |
