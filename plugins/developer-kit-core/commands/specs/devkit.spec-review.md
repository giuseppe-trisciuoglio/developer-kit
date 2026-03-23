---
description: "Provides interactive specification quality review by asking targeted questions (max 5) to identify ambiguities, gaps, and improvement areas. Integrates responses directly into the specification. Complementary to spec-quality which handles technical synchronization."
argument-hint: "[ spec-folder | spec-file ]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite
model: inherit
---

# Spec Review - Quality Assessment

Evaluates the quality of a functional specification by identifying ambiguities, gaps, and improvement areas through an interactive clarification process.

## Overview

This command addresses the **content quality** of specifications, integrating with `devkit.spec-quality` which handles technical synchronization:

| Command | Focus |
|---------|-------|
| **devkit.spec-review** | Content quality: completeness, clarity, traceability, coverage |
| **devkit.spec-quality** | Technical synchronization: Knowledge Graph, tasks, codebase |

### Workflow Position

```
Idea → Specification → Spec Review (this) → Tasks → Implementation
           ↓              ↓
        Clarify        Improve Quality
```

### Dimensions of Quality

The command evaluates four main dimensions:

1. **Completeness and Clarity**
   - Vague expressions ("robust", "intuitive", "fast")
   - Terms not defined in glossary
   - Internal contradictions
   - Missing or incomplete sections

2. **Requirements Traceability**
   - User request → specification alignment
   - Requirements → tasks coverage (if tasks exist)
   - Clear origin for each requirement

3. **Acceptance Criteria**
   - Presence of testable criteria
   - Measurability of criteria
   - Coverage of key functionalities

4. **Edge Cases Coverage**
   - Edge cases identified
   - Error handling documented
   - Explicit constraints and limitations

## Usage

```bash
# Basic usage - review a spec folder
/developer-kit:devkit.spec-review docs/specs/001-hotel-search-aggregation/

# Review a specific spec file
/developer-kit:devkit.spec-review docs/specs/001-hotel-search-aggregation/2026-03-07--hotel-search.md

# Review from current directory (auto-detect)
/developer-kit:devkit.spec-review
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `spec-path` | No | Path to spec folder or file (default: auto-detect from CWD) |

## Core Principles

- **Maximum 5 questions**: Focus on the most impactful ambiguities
- **One question at a time**: Interactive presentation with recommendation
- **Immediate integration**: Responses are integrated into the specification progressively
- **Recommendation based on best practices**: For each question, suggests the best option
- **Non-destructive**: Preserves existing content, only adds clarifications
- **Final report**: Summary of resolved, deferred, and outstanding areas

---

## Phase 1: Discovery

**Goal**: Identify the specification to review and gather context

**Actions**:

1. Create todo list with all phases
2. Parse $ARGUMENTS to extract the specification path
3. Determine the specification folder:
   - If a file is provided: use the parent directory
   - If a folder is provided: use it directly
   - If no argument: auto-detect from current working directory
4. Verify the folder exists
5. Identify relevant files:
   - `YYYY-MM-DD--feature-name.md` - Functional specification (preferred)
   - `*-specs.md` - Functional specification (legacy fallback)
   - `user-request.md` - Original user request (for traceability)
   - `brainstorming-notes.md` - Brainstorming notes (secondary)
   - `tasks/` - Existing tasks (for coverage verification)
   - `knowledge-graph.json` - Technical context (optional)

---

## Phase 2: Spec Loading

**Goal**: Load and analyze the specification to identify improvement areas

**Actions**:

1. Resolve and read the specification file using the same priority as `devkit.spec-to-tasks`:
   - preferred `YYYY-MM-DD--feature-name.md`
   - legacy `*-specs.md`
   - otherwise the only dated spec-like markdown file in the folder
2. If present, also read:
   - `user-request.md` to verify traceability
   - Existing tasks to verify coverage
3. Perform a **structured Quality Scan** using this taxonomy:

### Quality Scan Taxonomy

For each category, mark the status: **Clear**, **Partial**, or **Missing**

#### Completeness and Clarity
- [ ] User goals and success criteria defined
- [ ] Explicit out-of-scope statements
- [ ] Differentiated roles/user personas
- [ ] Glossary of terms
- [ ] Explicit assumptions

#### Domain and Data Model
- [ ] Entities, attributes, relationships
- [ ] Identity and uniqueness rules
- [ ] State transitions/lifecycle
- [ ] Volume/data assumptions

#### Interaction and UX Flow
- [ ] Critical user paths
- [ ] Error/empty/loading states
- [ ] Accessibility/localization notes

#### Non-Functional Quality
- [ ] Performance (latency/throughput targets)
- [ ] Scalability (limits, horizontal/vertical)
- [ ] Reliability (uptime, recovery)
- [ ] Observability (logging, metrics, tracing)
- [ ] Security (authN/Z, data protection)
- [ ] Compliance (regulatory constraints)

#### Integrations and Dependencies
- [ ] External services/APIs and failure modes
- [ ] Data import/export formats
- [ ] Assumptions on protocols/versioning

#### Edge Cases and Error Handling
- [ ] Negative scenarios identified
- [ ] Rate limiting/throttling
- [ ] Conflict resolution (e.g., concurrent modifications)

#### Constraints and Trade-offs
- [ ] Explicit technical constraints
- [ ] Documented trade-offs
- [ ] Rejected alternatives and reasons

#### Terminology and Consistency
- [ ] Defined canonical terms
- [ ] No confusing synonyms
- [ ] Consistent term usage

#### Completion Criteria
- [ ] Testable acceptance criteria
- [ ] Measurable Definition of Done
- [ ] Requirements → acceptance traceability

#### Placeholders and TODOs
- [ ] Resolved TODO markers
- [ ] Quantified vague adjectives
- [ ] Documented pending decisions

---

## Phase 3: Question Prioritization

**Goal**: Generate a prioritized queue of clarification questions

**Actions**:

1. For each category with Partial or Missing status, generate a potential question
2. Apply constraints:
   - **Maximum 5 questions total**
   - Each question must be answerable with:
     - **Multi-choice** (2-5 mutually exclusive options), OR
     - **Short answer** (max 5 words)
   - Only include questions that impact: architecture, data modeling, task decomposition, test design, UX, operational readiness, compliance
   - Exclude: stylistic preferences, implementation details, already answered questions
3. Order by impact × uncertainty (heuristic)
4. Balance category coverage

---

## Phase 4: Sequential Questioning Loop

**Goal**: Present questions one at a time and integrate responses

**Actions**:

1. **For each question in the queue**:
   - Present **EXACTLY ONE question** at a time

2. **For multi-choice questions**:
   - Analyze all options and determine the most suitable one
   - Present the **prominent recommendation** with reasoning
   - Format as Markdown table

   ```
   **Recommended:** Option [X] - <1-2 sentence reasoning>

   | Option | Description |
   |--------|-------------|
   | A | <Option A Description> |
   | B | <Option B Description> |
   | C | <Option C Description> |
   | Short | Provide a different short answer (<=5 words) |

   You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.
   ```

3. **For short-answer questions**:
   - Provide the **suggested answer** based on best practices
   ```
   **Suggested:** <proposed answer> - <brief reasoning>

   Format: Short answer (<=5 words). You can accept the suggestion by saying "yes" or "suggested", or provide your own answer.
   ```

4. **After the user responds**:
   - If "yes"/"recommended"/"suggested": use the recommendation
   - Otherwise: validate the response is appropriate
   - If ambiguous: ask for disambiguation (doesn't count as a new question)
   - Once satisfactory: proceed to the next question

5. **Immediate integration after each response**:
   - Create `## Clarifications` section if it doesn't exist (after overview)
   - Add `### Session YYYY-MM-DD` subsection
   - Append bullet: `- Q: <question> → A: <answer>`
   - Apply the clarification to the appropriate section
   - Save the file

6. **Stop conditions**:
   - All critical ambiguities resolved
   - User signals completion ("done", "good", "no more")
   - Reached 5 questions

---

## Phase 5: Clarification Integration

**Goal**: Integrate each clarification into the appropriate specification section

**Mapping clarification → section**:

| Ambiguity Type | Target Section |
|----------------|----------------|
| Functional ambiguity | Add/update Functional Requirements |
| Role/actor distinction | Update User Stories or Actors |
| Data entity form | Update Data Model |
| Non-functional constraint | Add/modify Non-Functional Requirements |
| Edge case/negative flow | Add to Edge Cases / Error Handling |
| Inconsistent terminology | Normalize term, add "(formerly X)" |
| Placeholder/TODO | Resolve or quantify |

**Integration rules**:
- Preserve existing formatting
- Don't reorder unrelated sections
- Maintain heading hierarchy
- If clarification invalidates a previous statement: replace, don't duplicate
- Keep each clarification minimal and testable

---

## Phase 6: Validation

**Goal**: Validate integration after each write

**Checks**:
- [ ] Clarifications session contains exactly one bullet per response
- [ ] Total questions ≤ 5
- [ ] No vague placeholders remaining from responses
- [ ] No remaining contradictions
- [ ] Valid Markdown structure
- [ ] Consistent terms across sections

---

## Phase 7: Report Generation

**Goal**: Generate final completion report

**Actions**:

1. Generate summary with:
   - Number of questions asked and answered
   - Path of updated specification
   - Sections touched
   - Coverage summary table

2. **Coverage summary table**:

   | Category | Status | Notes |
   |----------|--------|-------|
   | Completeness and Clarity | Resolved/Clear/Deferred/Outstanding | ... |
   | Requirements Traceability | Resolved/Clear/Deferred/Outstanding | ... |
   | Acceptance Criteria | Resolved/Clear/Deferred/Outstanding | ... |
   | Edge Cases Coverage | Resolved/Clear/Deferred/Outstanding | ... |

3. **Status definitions**:
   - **Resolved**: Was Partial/Missing, has been addressed
   - **Clear**: Already sufficient at start
   - **Exceeded question quota or better for planning**
   - **Outstanding**: Still Partial/Missing but low impact

4. Recommend next steps:
   - If Outstanding/Deferred: consider running `/developer-kit:devkit.spec-review` after planning
   - If all Clear: proceed to `/developer-kit:devkit.spec-to-tasks`

---

## Error Handling

### Specification not found
```
Error: Specification not found at [path]
Verify that the path contains a resolvable spec file (`YYYY-MM-DD--feature-name.md` or legacy `*-specs.md`)
```

### No ambiguities detected
```
No critical ambiguities detected worth formal clarification.
The specification is complete and clear.
Proceed with: /developer-kit:devkit.spec-to-tasks [spec-folder]
```

### File write failed
```
Warning: Unable to write to [file]: [error]
The clarification has been recorded in memory but not persisted.
```

---

## Examples

### Example 1: Spec with performance ambiguity

```bash
/developer-kit:devkit.spec-review docs/specs/003-notification-system/
```

**Interactive flow**:

```
Analyzing spec: docs/specs/003-notification-system/2026-03-10--notification-specs.md

Quality Scan Results:
- Completeness and Clarity: Partial (missing "real-time" definition)
- Requirements Traceability: Clear
- Acceptance Criteria: Partial
- Edge Cases Coverage: Missing

[1/5] Question 1 of 5

**Recommended:** Option B - "Real-time" in notification systems typically means < 5 seconds for user-facing notifications. This is a standard industry benchmark.

| Option | Description |
|--------|-------------|
| A | < 1 second for all notifications |
| B | < 5 seconds for user-facing, < 30s for background |
| C | < 10 seconds for all notifications |
| Short | Provide different answer (<=5 words) |

You can reply with "A", "B", "C", "yes" for recommendation, or your own answer.
```

### Example 2: Already complete spec

```bash
/developer-kit:devkit.spec-review docs/specs/001-hotel-search-aggregation/
```

**Output**:

```
Analyzing spec: docs/specs/001-hotel-search-aggregation/2026-03-07--hotel-search-specs.md

Quality Scan Results:
- Completeness and Clarity: Clear
- Requirements Traceability: Clear
- Acceptance Criteria: Clear
- Edge Cases Coverage: Clear

No critical ambiguities detected worth formal clarification.
The specification is well-formed and ready for task generation.

Next step: /developer-kit:devkit.spec-to-tasks docs/specs/001-hotel-search-aggregation/
```

---

## Integration with Other Commands

### Before devkit.spec-to-tasks

Run `spec-review` to ensure the specification is complete before generating tasks:

```bash
# Step 1: Review and improve spec quality
/developer-kit:devkit.spec-review docs/specs/005-checkout-flow/

# Step 2: Generate tasks from improved spec
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/005-checkout-flow/
```

### After devkit.brainstorm

Run `spec-review` to validate the specification generated from brainstorming:

```bash
# Step 1: Generate spec from idea
/developer-kit:devkit.brainstorm "Implement user authentication with JWT"

# Step 2: Review the generated spec
/developer-kit:devkit.spec-review docs/specs/002-user-auth/

# Step 3: Proceed to tasks
/developer-kit:devkit.spec-to-tasks --lang=spring docs/specs/002-user-auth/
```

### With devkit.spec-quality

The two commands are complementary:

```bash
# spec-review: improve content quality
/developer-kit:devkit.spec-review docs/specs/003-api-gateway/

# spec-quality: sync technical context
/developer-kit:devkit.spec-quality docs/specs/003-api-gateway/

# spec-to-tasks: generate tasks with high quality context
/developer-kit:devkit.spec-to-tasks --lang=nestjs docs/specs/003-api-gateway/
```

---

## Todo Management

During execution, maintain the todo list:

```
[ ] Phase 1: Discovery
[ ] Phase 2: Spec Loading
[ ] Phase 3: Question Prioritization
[ ] Phase 4: Sequential Questioning (0/5 questions)
[ ] Phase 5: Clarification Integration
[ ] Phase 6: Validation
[ ] Phase 7: Report Generation
```

Update status progressively.

---

## Notes

- This command is **idempotent**: can be run multiple times
- Clarification sessions are tracked with dates
- Recommendations are based on industry-standard best practices
- The command doesn't modify the general structure of the specification, only adds clarifications
- For heavier structural changes, use `/developer-kit:devkit.brainstorm` to regenerate
