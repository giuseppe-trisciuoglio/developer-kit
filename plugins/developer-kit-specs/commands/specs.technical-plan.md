---
description: "Creates a Technical Plan document that captures architectural decisions, stack, and implementation phases. Use after specs.brainstorm to document HOW the feature will be built."
argument-hint: "[ --spec=docs/specs/XXX-feature ] [ --from-spec ]"
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, TodoWrite
model: inherit
---

# Technical Plan

Creates a Technical Plan document that captures:
1. **Architecture Decisions**: Why choices were made
2. **Technology Stack**: Libraries, versions, alternatives considered
3. **Implementation Phases**: How the feature will be built
4. **Risks & Mitigations**: What could go wrong

## Overview

After `specs.brainstorm` generates the functional specification, use this command to document:
- **Stack choices** with exact versions
- **Architecture patterns** to follow
- **Implementation phases** / milestones
- **Performance targets** with metrics
- **Risks** and how to detect them

## Usage

```bash
# Create from existing spec
/developer-kit-specs:specs.technical-plan --spec=docs/specs/001-feature/

# Create with custom focus
/developer-kit-specs:specs.technical-plan docs/specs/001-feature/
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--spec` | No | Path to spec folder |
| `--from-spec` | No | Generate from spec (implied if spec path provided) |

## Examples

### Basic Usage

```bash
/developer-kit-specs:specs.technical-plan --spec=docs/specs/001-feature/
```

### With Custom Focus

```bash
/developer-kit-specs:specs.technical-plan docs/specs/001-feature/
```

## Workflow Position

```
brainstorm → technical-plan (this) → spec-to-tasks → implementation → review
       ↓
   [WHEN ARCHITECTURAL DECISIONS ARE NEEDED]
```

## Core Principles

- **Concrete over Abstract**: "Node 20.11 LTS" not "Node ≥18"
- **Decision with Rationale**: Why this choice over alternatives
- **Version Pinning**: Every dependency has exact version
- **Risks First**: What could go wrong before how to build it
- **Performance as Requirements**: Metrics are not optional

---

## Phase 1: Specification Analysis

**Goal**: Load the functional specification and extract technical implications

**Actions**:

1. **Create todo list** for the technical planning process:
   ```
   [ ] Phase 1: Specification Analysis
   [ ] Phase 2: Technology Stack Definition
   [ ] Phase 3: Architecture Decisions
   [ ] Phase 4: Implementation Phases
   [ ] Phase 5: Performance Requirements
   [ ] Phase 6: Risk Assessment
   [ ] Phase 7: File Structure
   [ ] Phase 8: Summary
   ```

2. **Parse the spec path** from `$ARGUMENTS`:
   - If `--spec=` flag present, extract the path
   - If plain path provided, use as-is
   - If no path provided, ask user for spec location

3. **Read the functional specification** from the specified path:
   - Identify the main spec file (`YYYY-MM-DD--feature-name.md`)
   - Read user-request.md for original intent
   - Read brainstorming-notes.md for context

4. **Identify technical implications** from the spec:
   - What types of components are needed?
   - What external integrations are required?
   - What data models must be supported?
   - What performance expectations are stated?
   - What security considerations exist?

5. **List technical concerns** that need decisions:
   - Create a working list of decisions to make
   - Group by category (stack, architecture, risk)
   - Prioritize by implementation order

---

## Phase 2: Technology Stack Definition

**Goal**: Document the technology choices with versions

**Actions**:

1. **Check for existing architecture**:
   - Look for `docs/architecture.md`
   - Look for `docs/specs/architecture.md`
   - If exists, inherit existing stack choices
   - Add new libraries only if needed for this feature

2. **Ask user for stack components** (or derive from existing architecture):
   - Language + version
   - Runtime + version
   - Framework + version
   - Key libraries with exact versions
   - Database choices (if applicable)
   - Infrastructure components (if applicable)

3. **For each choice, document**:
   - What the technology is
   - Why this choice over alternatives
   - Exact version (no ranges, no "latest")
   - Any constraints or requirements

4. **Use AskUserQuestion** for ambiguous choices:
   - Present 2-3 options with trade-offs
   - Ask for preference with context
   - Document the decision and rationale

5. **Generate Technology Stack table**:

```markdown
## Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|--------|-----------|
| Language | [e.g., TypeScript] | [e.g., 5.4.2] | [Why this over alternatives] |
| Runtime | [e.g., Node.js] | [e.g., 20.11 LTS] | [Performance/stability reasons] |
| Framework | [e.g., NestJS] | [e.g., 10.3.0] | [Why NestJS over Express/Fastify] |
| ORM | [e.g., Drizzle] | [e.g., 0.29.4] | [Type-safety over Prisma] |
| API | [e.g., REST] | [OpenAPI 3.0] | [Simplicity over GraphQL] |
| Auth | [e.g., JWT] | [e.g., passport-jwt 7.0.0] | [Stateless over session] |
| Validation | [e.g., Zod] | [e.g., 3.22.4] | [Type inference over class-validator] |
| Testing | [e.g., Jest] | [e.g., 29.7.0] | [Ecosystem integration] |
```

6. **Document Forbidden Technologies**:

```markdown
## Forbidden Technologies

| Technology | Reason Not Used | Alternative Chosen |
|-----------|-----------------|-------------------|
| MongoDB | [Reason: e.g., ACID compliance needed] | PostgreSQL |
| GraphQL | [Reason: e.g., over-engineering for simple API] | REST |
| Mongoose | [Reason: e.g., prefer type-safe ORM] | Drizzle |
```

7. **Update todo**: Mark Phase 2 complete

---

## Phase 3: Architecture Decisions

**Goal**: Document key architectural choices with full context

**Actions**:

1. **Identify 3-5 key decisions** that shape implementation:
   - Focus on decisions with trade-offs
   - Avoid obvious or constrained choices
   - Prioritize decisions that affect multiple components

2. **Check for existing ADRs**:
   - Look in `docs/architecture/adr/` for existing decisions
   - Reference existing ADRs instead of duplicating
   - Note any conflicts with existing decisions

3. **For each decision, document**:

```markdown
### AD-001: [Decision Title]

**Context**: [What situation required this decision]

**Decision**: [What was decided]

**Alternatives Considered**:
1. [Alternative 1] — **Pros**: [Upside] / **Cons**: [Downside]
2. [Alternative 2] — **Pros**: [Upside] / **Cons**: [Downside]
3. [Alternative 3] — **Pros**: [Upside] / **Cons**: [Downside]

**Consequences**:
- **Positive**: [What improves with this choice]
- **Negative**: [What we accept or work around]
- **Risks**: [What could go wrong]

**Related ADR**: [Link to existing ADR if applicable]
**Applied In**: [Which implementation phases]
```

4. **Decision categories** (choose appropriate):
   - **Data Architecture**: Database selection, schema design, caching strategy
   - **API Design**: REST vs GraphQL, versioning, pagination
   - **Authentication**: JWT vs session, OAuth providers, token management
   - **Error Handling**: Exception strategy, error codes, logging
   - **Component Structure**: Monolith vs microservices, module boundaries
   - **Integration**: External APIs, event systems, message queues

5. **Use AskUserQuestion** for major decisions:
   - Present the decision context clearly
   - Show alternatives with trade-offs
   - Ask for preference, not validation

6. **Update todo**: Mark Phase 3 complete

---

## Phase 4: Implementation Phases

**Goal**: Define how the feature will be built, step by step

**Actions**:

1. **Break down into 2-4 phases** based on complexity:
   - Foundation phase (setup, infrastructure)
   - Core feature phase (main functionality)
   - Integration phase (external systems)
   - Polish phase (performance, security, docs)

2. **For each phase, document**:

```markdown
### Phase 1: [Phase Name]
**Goal**: [What this phase accomplishes]

**Entry Criteria**: [What must be true before starting]
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

**Milestones**:
- [ ] [Milestone 1: description]
- [ ] [Milestone 2: description]
- [ ] [Milestone 3: description]

**Key Deliverables**:
- [File/Document]: [Description]
- [Component]: [Description]

**Dependencies**: [What this phase depends on]
**Blocked By**: [Any blocking dependencies]

**Risks**:
- [Risk]: [Mitigation strategy]

---
```

3. **Define dependencies between phases**:
   - Visual dependency chain
   - Critical path identification
   - Parallel work possibilities

4. **For each milestone, link to tasks** (if tasks exist):
   - Reference task files: `tasks/TASK-XXX.md`
   - Or reference task summary

5. **Document phase handoff criteria**:
   - What constitutes "complete"
   - What review/verification is needed
   - Who signs off

6. **Update todo**: Mark Phase 4 complete

---

## Phase 5: Performance Requirements

**Goal**: Define measurable performance targets

**Actions**:

1. **Review spec for performance expectations**:
   - Extract any stated performance goals
   - Note any latency requirements
   - Identify throughput expectations

2. **Define quantitative targets**:

```markdown
## Performance Requirements

### Response Time

| Endpoint/Operation | Target | Measurement | Notes |
|-------------------|--------|-------------|-------|
| [API endpoint] | [p95 < XXXms] | [APM tool] | [Context] |
| [Background job] | [< Xs] | [Job metrics] | [Context] |
| [Page load] | [< Xs] | [Real user monitoring] | [Context] |

### Throughput

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Requests per second | [e.g., 1000 req/s] | [Load test] |
| Concurrent users | [e.g., 500] | [Load test] |
| Data processing | [e.g., 10K records/min] | [Batch metrics] |

### Resource Usage

| Resource | Target | Measurement |
|----------|--------|-------------|
| Memory per instance | [< 100MB] | [Monitoring] |
| CPU utilization | [< 70%] | [System metrics] |
| Database connections | [< 20] | [Connection pool metrics] |
| Cold start time | [< 3s] | [Lambda/container metrics] |

### Data & Storage

| Metric | Target | Notes |
|--------|--------|-------|
| Database query count | [< 10 per request] | [Query logging] |
| Cache hit rate | [> 90%] | [Cache metrics] |
| Storage growth | [predictable] | [Capacity planning] |
```

3. **Document Load Testing Strategy**:

```markdown
### Load Testing Strategy

**Baseline Load**:
- Expected normal traffic: [X requests/minute]
- Peak hours: [Time ranges]
- Geographic distribution: [Regions]

**Load Test Scenarios**:
1. **Steady State**: [X users, Y requests/min, duration Z]
2. **Peak Load**: [X users, Y requests/min, duration Z]
3. **Stress Test**: [Scale until failure, measure breaking point]
4. **Spike**: [Sudden increase from baseline to X]

**Acceptance Criteria**:
- All response times under target at baseline
- [X%] of requests under target at peak
- System recovers gracefully after stress
```

4. **Define monitoring and alerting**:

```markdown
### Monitoring & Alerting

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| Response time p95 | > [target] | Page on-call |
| Error rate | > 1% | Page on-call |
| Memory usage | > 80% | Warning to team |
| CPU usage | > 90% | Page on-call |

**Tools**:
- [APM tool]: [metrics collected]
- [Log aggregation]: [events captured]
- [Uptime monitoring]: [checks performed]
```

5. **Update todo**: Mark Phase 5 complete

---

## Phase 6: Risk Assessment

**Goal**: Identify what could go wrong and how to detect it

**Actions**:

1. **Brainstorm potential risks**:
   - Technical risks (complexity, dependencies)
   - Operational risks (maintenance, monitoring)
   - External risks (third-party, compliance)
   - Schedule risks (blockers, unknowns)

2. **Assess each risk** (Likelihood x Impact):

```markdown
## Risk Assessment

| Risk | Likelihood | Impact | Overall | Mitigation | Detection |
|------|------------|--------|---------|------------|-----------|
| [Risk description] | HIGH/MEDIUM/LOW | HIGH/MEDIUM/LOW | HIGH/MEDIUM/LOW | [Strategy] | [How we know] |
| [Risk description] | MEDIUM | HIGH | HIGH | [Strategy] | [How we know] |
```

3. **For HIGH and MEDIUM risks, document response protocol**:

```markdown
### Risk: [Risk Name]

**Trigger**: [What indicates this risk is occurring]

**Detection**:
- [Metric/monitor that indicates problem]
- [Alert threshold]

**Response Protocol**:
1. **Detect**: [How we know there's a problem]
2. **Triage**: [Who is alerted, how fast]
3. **Mitigate**: [Immediate action to reduce impact]
4. **Resolve**: [Permanent fix to prevent recurrence]

**Playbook**:
```bash
# Diagnostic commands
[command 1]
[command 2]

# Mitigation actions
[action 1]
[action 2]
```
```

4. **Categorize risks**:

   - **Technical Risks**: Code complexity, integration challenges, performance unknowns
   - **Dependency Risks**: Third-party APIs, external services, library maturity
   - **Data Risks**: Migration complexity, data integrity, volume handling
   - **Security Risks**: Authentication, authorization, data protection
   - **Operational Risks**: Monitoring gaps, deployment complexity, rollback difficulty

5. **Create risk summary**:

```markdown
### Risk Summary

**Critical Risks** (require immediate mitigation):
- [Risk 1]
- [Risk 2]

**High Risks** (mitigation planned):
- [Risk 3]
- [Risk 4]

**Medium Risks** (monitor closely):
- [Risk 5]

**Low Risks** (acceptable):
- [Risk 6]
```

6. **Update todo**: Mark Phase 6 complete

---

## Phase 7: File Structure

**Goal**: Define the project organization

**Actions**:

1. **Review existing project structure**:
   - Look for established patterns
   - Check `src/` or `app/` organization
   - Identify existing conventions

2. **Define structure for this feature**:

```markdown
## Project Structure

```
src/
├── controllers/           # API endpoint handlers
│   └── [Feature]Controller.ts
├── services/              # Business logic layer
│   └── [Feature]Service.ts
├── repositories/          # Data access layer
│   └── [Feature]Repository.ts
├── models/                # Domain entities
│   └── [Entity].ts
├── dto/                   # Data transfer objects
│   ├── Create[Feature].ts
│   ├── Update[Feature].ts
│   └── [Feature]Response.ts
├── errors/                # Custom exceptions
│   ├── [Feature]NotFoundError.ts
│   ├── [Feature]ValidationError.ts
│   └── index.ts
├── validators/           # Input validation schemas
│   └── [feature].validator.ts
├── mappers/               # Entity <-> DTO mapping
│   └── [Feature]Mapper.ts
├── configuration/         # Feature-specific config
│   └── [feature].config.ts
└── index.ts               # Module exports

tests/
├── unit/
│   ├── services/
│   │   └── [Feature]Service.test.ts
│   └── repositories/
│       └── [Feature]Repository.test.ts
└── integration/
    └── [feature].integration.test.ts

docs/
└── specs/
    └── [id]/
        └── technical-plan.md  # This document
```

3. **Document naming conventions**:
   - File naming: kebab-case vs camelCase
   - Class naming: PascalCase
   - Test file naming: `.test.ts` suffix

4. **Define module boundaries**:
   - What can import what
   - Cross-module communication patterns
   - Shared utilities location

5. **Document rules**:

```markdown
### Structure Rules

1. **Business logic lives in `src/` only**
   - No business logic in controllers
   - Services contain all business rules

2. **Test files mirror source structure**
   - `tests/unit/services/[Name]Service.test.ts`
   - Same path as source, test suffix

3. **One class per file**
   - `[Feature]Service.ts` contains one class
   - `[Feature]Controller.ts` contains one class

4. **DTOs at boundary**
   - Input validation in controller
   - Response mapping in controller
   - Service returns domain objects

5. **No circular dependencies**
   - Import only from adjacent layers
   - Use dependency injection
```

6. **Update todo**: Mark Phase 7 complete

---

## Phase 8: Summary

**Goal**: Report completion and integration points

**Actions**:

1. **Verify all phases completed**:
   - Check todo list
   - Ensure all tables generated
   - Confirm all decisions documented

2. **Generate completion summary**:

```markdown
---

## Technical Plan Summary

**Feature**: [Feature name]
**Spec**: [Link to functional spec]
**Created**: YYYY-MM-DD
**Status**: Draft

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [AD-001] | [Choice] | [Brief rationale] |
| [AD-002] | [Choice] | [Brief rationale] |

### Implementation Phases

| Phase | Goal | Dependencies |
|-------|------|--------------|
| Phase 1 | [Name] | None |
| Phase 2 | [Name] | Phase 1 |
| Phase 3 | [Name] | Phase 2 |
| Phase 4 | [Name] | Phase 3 |

### Performance Targets

| Metric | Target |
|--------|--------|
| Response Time (p95) | [Target] |
| Throughput | [Target] |
| Memory | [Target] |

### Top Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | HIGH | HIGH | [Strategy] |
| [Risk 2] | MEDIUM | HIGH | [Strategy] |

---

## Next Steps

1. Run `/developer-kit-specs:specs.spec-to-tasks [spec-folder]` to generate implementation tasks
2. Execute tasks in phase order
3. After implementation, run `/developer-kit-specs:specs.spec-sync-with-code [spec-folder]`

### File Output

**Technical Plan**: `docs/specs/[id]/YYYY-MM-DD--technical-plan.md`
**Spec Folder**: `docs/specs/[id]/`
```

3. **Confirm output location** and report to user

4. **Update todo**: Mark Phase 8 complete

---

## Complete Technical Plan Template

Below is the full template for reference:

```markdown
# Technical Plan: [Feature Name]

**Spec**: [Link to functional spec]
**Created**: YYYY-MM-DD
**Status**: Draft

---

## Technology Stack

[Stack table with versions and rationale]

### Forbidden Technologies

[Table of what we're NOT using and why]

---

## Architecture Decisions

### AD-001: [Decision Title]

**Context**: [What required this decision]

**Decision**: [What was decided]

**Alternatives Considered**:
1. [Alternative 1] — **Pros**: [Upside] / **Cons**: [Downside]
2. [Alternative 2] — **Pros**: [Upside] / **Cons**: [Downside]

**Consequences**:
- **Positive**: [What improves]
- **Negative**: [What we accept]
- **Risks**: [What could go wrong]

**Related ADR**: [Link to existing ADR if any]

---

### AD-002: [Decision Title]
[...continue for each decision]

---

## Implementation Phases

### Phase 1: [Phase Name]
**Goal**: [What this phase accomplishes]

**Milestones**:
- [ ] [Milestone 1]
- [ ] [Milestone 2]

**Dependencies**: [What this phase depends on]

---

### Phase 2: [Phase Name]
**Goal**: [What this phase accomplishes]

**Milestones**:
- [ ] [Milestone 1]
- [ ] [Milestone 2]

**Dependencies**: Phase 1 must be complete

---

### Phase 3: [Phase Name]
**Goal**: [What this phase accomplishes]

**Milestones**:
- [ ] [Milestone 1]
- [ ] [Milestone 2]

**Dependencies**: Phase 2 must be complete

---

### Phase 4: [Phase Name]
**Goal**: [What this phase accomplishes]

**Milestones**:
- [ ] [Milestone 1]
- [ ] [Milestone 2]

**Dependencies**: Phase 3 must be complete

---

## Performance Requirements

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Response Time (p95) | < 200ms | APM tool |
| Throughput | 1000 req/s | Load test |
| Memory Usage | < 100MB per instance | Monitoring |
| Database Queries | < 10 per request | Query logging |
| Cold Start | < 3s | Lambda metrics |

### Load Testing Strategy

- **Baseline**: [Expected normal load]
- **Peak**: [Expected peak load]
- **Stress**: [Breaking point]

### Monitoring

- [Tool] for [metric]
- Alert when [threshold] exceeded

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Detection |
|------|------------|--------|------------|-----------|
| Database connection exhaustion | MEDIUM | HIGH | Connection pooling | Metrics on pool size |
| Memory leak | LOW | HIGH | Heap profiling | Memory monitoring |
| Third-party API failure | MEDIUM | MEDIUM | Retry + circuit breaker | Error rate spike |
| Performance degradation | MEDIUM | MEDIUM | Load testing | APM alerts |

### Risk Response Protocol

1. **Detect**: [How we know there's a problem]
2. **Triage**: [Who is alerted, how fast]
3. **Mitigate**: [Immediate action]
4. **Resolve**: [Permanent fix]

---

## Project Structure

```
src/
├── controllers/        # API endpoints
├── services/           # Business logic
├── repositories/       # Data access
├── models/             # Domain entities
├── dto/                # Data transfer objects
├── errors/             # Custom exceptions
└── index.ts            # Module exports

tests/
├── unit/               # Unit tests
└── integration/        # Integration tests
```

### Structure Rules

- Follow existing structure conventions
- No files outside `src/` for business logic
- Test files mirror source structure

---

## Compliance Checklist

- [ ] All dependencies have exact versions
- [ ] All decisions have rationale
- [ ] All risks have mitigation plans
- [ ] Performance targets are measurable
- [ ] Structure follows project conventions
```

---

## Integration with Other Commands

### With brainstorm

```
brainstorm → technical-plan → spec-to-tasks
```

After brainstorm completes, run technical-plan to document HOW.

### With constitution

If `docs/specs/architecture.md` exists, inherit stack choices:
- Use existing language/framework
- Add new libraries only if needed
- Reference existing patterns
- Avoid contradicting existing decisions

### With spec-to-tasks

Technical Plan informs task generation:
- Tasks grouped by phase
- Phase dependencies become task dependencies
- Architecture decisions become implementation constraints
- Performance targets become acceptance criteria

### With spec-check

After technical-plan is complete:
- Run `specs.spec-check` to verify specification quality
- Resolve any [NEEDS CLARIFICATION] markers
- Ensure technical plan aligns with functional spec

---

## Todo Tracking

Throughout the command, use TodoWrite to track progress:

```
[ ] Phase 1: Specification Analysis
[ ] Phase 2: Technology Stack Definition
[ ] Phase 3: Architecture Decisions
[ ] Phase 4: Implementation Phases
[ ] Phase 5: Performance Requirements
[ ] Phase 6: Risk Assessment
[ ] Phase 7: File Structure
[ ] Phase 8: Summary
```

Mark each phase complete after generating the corresponding section.

---

## Example

```bash
/developer-kit-specs:specs.technical-plan --spec=docs/specs/001-user-auth/
```

**Output**:

```markdown
# Technical Plan: User Authentication

**Spec**: docs/specs/001-user-auth/2024-03-07--user-auth.md
**Created**: 2024-03-15
**Status**: Draft

## Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|--------|-----------|
| Language | TypeScript | 5.4.2 | Type safety |
| Runtime | Node.js | 20.11 LTS | Stability |
| Framework | NestJS | 10.3.0 | Dependency injection |
| Auth | passport-jwt | 7.0.0 | Industry standard |
| Validation | class-validator | 0.14.0 | Decorator-based validation |

## Forbidden Technologies

| Technology | Reason Not Used | Alternative |
|-----------|-----------------|-------------|
| Sessions | Scalability issues | JWT stateless |
| MongoDB | ACID compliance needed | PostgreSQL |

## Architecture Decisions

### AD-001: Stateless JWT Authentication

**Context**: Authentication must scale horizontally

**Decision**: Use JWT tokens with refresh token rotation

**Alternatives**:
1. Session-based — **Pros**: Simple / **Cons**: Scales poorly
2. OAuth2 with external provider — **Pros**: Managed / **Cons**: External dependency

**Consequences**:
- **Positive**: Horizontal scaling, no session storage
- **Negative**: Token revocation complexity
- **Risks**: Token leakage, clock skew

[... continues with all sections ...]
```

---

## Error Handling

If the specified spec folder does not exist:
- Ask user for valid spec path
- Offer to list available specs in `docs/specs/`

If spec file is malformed or missing required sections:
- Warn user and continue with available content
- Document what's missing in the technical plan

If architecture.md conflicts with user decisions:
- Present the conflict
- Ask user to resolve before proceeding
- Document the resolution in the technical plan

---

## Tips

1. **Be specific with versions**: "Express 4.18.2" not "Express 4.x"
2. **Explain rationale**: "Why this over alternatives" is crucial
3. **Risks before implementation**: What could go wrong first
4. **Link to existing ADRs**: Don't duplicate, reference
5. **Metrics over feelings**: "Response < 200ms" not "fast"
6. **Concrete over abstract**: Real file paths, real class names
7. **One phase at a time**: Complete each before moving to next