---
description: Optimize task workflow by analyzing dependencies, parallelization opportunities, and subagent delegation strategy for tasks.md
argument-hint: [optional-strategy]
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

**Goal**: Analyze tasks.md to optimize the implementation workflow by identifying parallelization opportunities, task dependencies, resource requirements, and generating an optimized execution plan with subagent delegation strategy. This command prepares tasks.md for efficient execution via `/speckit.implement`.

**When to run**: After `/speckit.check-integration` completes, BEFORE `/speckit.implement` executes tasks.

**Critical Principle**: This command NEVER modifies tasks.md or code files. It only analyzes and reports optimization recommendations. Output is a READ-ONLY optimization report.

## Execution Steps

### 1. Setup & Prerequisites

Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse JSON for:
- FEATURE_DIR (absolute path)
- TASKS file path
- AVAILABLE_DOCS list

For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

Abort if tasks.md is missing with error: "No tasks.md found. Run `/speckit.tasks` first."

### 2. Load Optimization Context

**Required files**:
- tasks.md: Complete task list with phases, IDs, descriptions, and parallelization markers [P]
- plan.md: Tech stack, architecture, team structure
- spec.md: Feature requirements and complexity assessment

**Optional files** (load if present):
- data-model.md: Data dependencies between tasks
- contracts/: API contract dependencies
- research.md: Technical constraints and decisions

**Codebase scan**:
- Identify project structure and complexity
- Map existing test patterns (unit, integration, e2e)
- Assess resource requirements (memory, CPU, external services)
- List available subagent types from available configuration

### 3. Parse Tasks Structure

Extract task information:

```
For each task in tasks.md:
- Task ID: Extract [ID] (e.g., T001, T126)
- Parallelization marker: Extract [P] if present
- Phase: Which phase/group task belongs to
- Description: Full task description
- Dependencies: Infer from description or explicit phase ordering
- Complexity: Assess as LOW/MEDIUM/HIGH/CRITICAL based on:
  * Lines of code expected
  * Test coverage required
  * External dependencies (databases, APIs)
  * Integration points
```

### 4. Dependency Analysis

**Build dependency graph**:

```
Task → Task Dependencies Analysis:

CRITICAL (blocking):
- Phase 1 → Phase 2 (Phase 2 blocked until Phase 1 complete)
- Phase 2 → Phase 3+ (Phase 3+ blocked until Phase 2 complete)
- Within-phase: Tasks without [P] marker may have implicit dependencies

IMPLICIT DEPENDENCIES:
- T002 (pom.xml) → T018 (configuration properties)
- Configuration tasks → Infrastructure implementation
- Domain models → Repository implementations
- Service implementations → Test infrastructure
```

**Output**:
```
DEPENDENCY ANALYSIS

Blocking Dependencies (Sequential):
- Phase 1 → Phase 2: [BLOCKING] Phase 1 must complete before Phase 2 starts
- Phase 2 → User Stories: [BLOCKING] Foundational layer required for all user story work

Critical Internal Dependencies:
- [Task A] → [Task B]: [Reason] (Must complete A before starting B)
- [Task X] → [Task Y/Z]: [Reason] (Task X blocks multiple dependents)

Independent Task Groups (Can parallelize):
- Group [N]: Tasks [ID, ID, ID] - All marked [P], no internal dependencies
  * Estimated parallel execution time: [minutes]
  * Resource requirement: [CPU/Memory profile]
```

### 5. Parallelization Opportunities

**Identify parallelizable task groups**:

```
PARALLELIZATION STRATEGY

Within-Phase Parallelization:
- [P] marked tasks: Can run simultaneously (different files, no dependencies)
- Grouped by agent type for efficient team allocation

Potential Parallelization:
- Tasks that could be parallelized with refactoring
- Risks: List any hidden dependencies or integration points
- Recommendation: Whether to parallelize or keep sequential

Sequential Requirements:
- Tasks that MUST run serially (blocking relationships)
- Reasons: Dependency chains, shared state, integration points
```

### 6. Subagent Assignment Strategy

**Analyze workload distribution**:

```
SUBAGENT DELEGATION ANALYSIS

Task Distribution by Complexity:
- CRITICAL tasks: [Count] (needs expert/experienced subagent)
- HIGH tasks: [Count] (needs intermediate subagent)
- MEDIUM tasks: [Count] (can distribute across team)
- LOW tasks: [Count] (can batch or auto-run)

Required Subagent Types:
- spring-boot-backend-development-expert: [Task IDs] - [Time estimate]
- spring-boot-test-expert: [Task IDs] - [Time estimate]
- [Other specialists]: [Task IDs] - [Time estimate]

Resource Constraints:
- Concurrent subagents available: [N]
- Time per subagent batch: [minutes]
- Memory per subagent: [MB estimate]
```

### 7. Execution Phases & Timeline

**Generate optimized execution plan**:

```
OPTIMIZED EXECUTION PLAN

Phase 1: Setup (Shared Infrastructure)
├─ Batch 1.1 [PARALLEL] (5-10 min):
│  ├─ Agent: spring-boot-backend-development-expert
│  │  └─ T001: Create DDD aggregate structure
│  │     • Resource: MEDIUM
│  │     • Depends on: None
│  │     • Blocks: T002, T003, T126
│  │
│  ├─ Agent: spring-boot-test-expert
│  │  └─ T004: Setup Testcontainers
│  │     • Resource: MEDIUM
│  │     • Depends on: None
│  │     • Blocks: All test tasks
│
├─ Batch 1.2 [PARALLEL] (10-15 min):
│  ├─ Agent: spring-boot-backend-development-expert
│  │  ├─ T002: Add dependencies to pom.xml
│  │  │  • Resource: MEDIUM
│  │  │  • Depends on: T001
│  │  │  • Blocks: T003, Configuration
│  │  ├─ T003: Configure application.yml
│  │  │  • Resource: MEDIUM
│  │  │  • Depends on: T001, T002
│  │  │  • Blocks: Runtime configuration tasks
│  │  └─ T126: Create CodeContextProperties
│  │     • Resource: MEDIUM
│  │     • Depends on: T001, T003
│  │     • Blocks: T127, T128
│  │
│  └─ Agent: spring-boot-backend-development-expert
│     ├─ T127: ThreadPoolConfiguration service
│     │  • Resource: HIGH
│     │  • Depends on: T126
│     │  • Blocks: T128
│     ├─ T128: Async task execution config
│     │  • Resource: HIGH
│     │  • Depends on: T127
│     │  • Blocks: Async operations
│     ├─ T156: BatchEmbeddingConfiguration
│     │  • Resource: HIGH
│     │  • Depends on: T003
│     │  • Blocks: T157, T158, T159
│     ├─ T157: Adaptive batch sizing service
│     │  • Resource: HIGH
│     │  • Depends on: T156
│     │  • Blocks: T159
│     ├─ T158: Batch monitoring & metrics
│     │  • Resource: MEDIUM
│     │  • Depends on: T156
│     │  • Blocks: None
│     └─ T159: Batch optimization tests
│        • Resource: HIGH
│        • Depends on: T156, T157, T158
│        • Blocks: None

Phase 1 Validation Checkpoint:
├─ Execute: mvn clean compile
├─ Execute: mvn clean test-compile
├─ Execute: mvn test
└─ Status: [READY/BLOCKED]

Estimated Total Duration Phase 1:
- Sequential path (critical path): [X] minutes
- With optimal parallelization: [Y] minutes (Z% reduction)
- Wall-clock time (assuming N concurrent subagents): [W] minutes
```

### 8. Resource Estimation

**Calculate resource requirements**:

```
RESOURCE REQUIREMENTS ANALYSIS

Memory Usage Profile:
- Setup Phase: [MB]
- Per parallel subagent: [MB]
- Testing infrastructure: [MB]
- Total peak: [MB]

CPU Requirements:
- Compilation tasks: MEDIUM (can share)
- Test execution: HIGH (parallel benefit significant)
- Code generation: MEDIUM

External Dependencies:
- Docker/Testcontainers: [Yes/No] → Startup time [minutes]
- Database services: [Services listed] → Availability window [minutes]
- API mock servers: [Services listed] → Setup time [minutes]

Network Bandwidth:
- Dependency download: [MB]
- Docker image pulls: [MB]
- Artifact uploads: [MB]
```

### 9. Risk Assessment

**Identify optimization risks**:

```
RISK ASSESSMENT

High-Risk Dependencies:
- [Risk]: Task A depends on Task B completing and compiling
  * Mitigation: Run immediate validation after B completes
  * Impact if fails: Cascading failure to all dependent tasks

Integration Points:
- [Point]: Configuration tasks must synchronize state
  * Mitigation: Validate configuration after each phase batch
  * Impact if fails: Runtime errors in downstream phases

Parallelization Risks:
- [Risk]: Tasks T002 and T003 both modify configuration
  * Mitigation: Enforce sequential ordering (already done with [P] marker)
  * Impact if fails: Configuration conflicts, merge issues
```

### 10. Optimization Recommendations

**Generate specific recommendations**:

```
OPTIMIZATION RECOMMENDATIONS

Priority 1: Critical Path Optimization
1. **Parallelize Setup Phase Batches**
   - Current: [X] minutes (assuming sequential)
   - Optimized: [Y] minutes (batches: B1.1 → B1.2)
   - Savings: [Z]% with [N] concurrent subagents
   - Implementation: Assign T002/T003/T126 to Batch 1.2 (after T001)

2. **Pre-compile Dependency Resolution**
   - Recommendation: Run `mvn dependency:resolve` once
   - Benefit: Avoid repeated downloads in parallel builds
   - Timing: Before starting any compilation tasks

Priority 2: Subagent Utilization
1. **Dedicate Specialists by Phase**
   - Phase 1.1: 1x backend-expert (T001), 1x test-expert (T004)
   - Phase 1.2: 1x backend-expert (T002-T159 cohort)
   - Benefit: Specialized focus, reduced context-switching

2. **Batch Similar Tasks**
   - Group T126/T127/T128: Configuration & threading (coherent scope)
   - Group T156/T157/T158/T159: Batch optimization (coherent scope)
   - Benefit: Reduced cognitive load, better error handling

Priority 3: Checkpoint Strategy
1. **Insert Compilation Checkpoints**
   - After T001: Run `mvn clean compile` (validate structure)
   - After T002/T003: Run `mvn clean compile` (validate config)
   - After T004: Run `mvn test-compile` (validate test setup)
   - Benefit: Catch errors early before downstream tasks start

2. **Test Validation Sequence**
   - Phase 1 complete → Run `mvn test` immediately
   - Blocks: All user story work until Phase 1 tests pass
   - Benefit: Prevent cascading test failures

Priority 4: Error Recovery
1. **Graceful Failure Handling**
   - If Phase 1.1 fails: Halt all Phase 1.2+ tasks
   - If Phase 1 compilation fails: Stop parallel execution, investigate sequentially
   - Recovery: Re-run failed task batch after fix

2. **Subagent Reassignment**
   - If subagent crashes: Reassign task to backup subagent
   - Track completion: Mark task [X] only after validation passes
   - Retry policy: 2 attempts per task before manual escalation
```

### 11. Execution Phase Table

Generate an aggregated phase view (no time column) that groups tasks by phase, highlights the responsible subagent, and captures the validation check for each phase:

```
PHASE EXECUTION MATRIX
══════════════════════════════════════════════════════════════════════════════

 Phase │ Execution Mode │ Subagent            │ Tasks (Grouped)                     │ Check Action
───────┼────────────────┼─────────────────────┼──────────────────────────────────────┼──────────────────────────────
 1.1   │ Parallel       │ Backend Expert      │ [T001] DDD Structure                │ mvn clean compile
       │                │                     │ [T004] Testcontainers Setup         │
───────┼────────────────┼─────────────────────┼──────────────────────────────────────┼──────────────────────────────
 1.2A  │ Parallel       │ Backend Expert      │ [T002] Dependencies                 │ mvn clean compile
       │                │                     │ [T003] app.yml                      │
       │                │                     │ [T126] Properties                   │
───────┼────────────────┼─────────────────────┼──────────────────────────────────────┼──────────────────────────────
 1.2B  │ Parallel       │ Backend Expert      │ [T127] ThreadPool Config            │ mvn clean test-compile
       │                │                     │ [T128] Async Execution              │
       │                │                     │ [T158] Batch Monitoring             │
       │                │                     │ [T159] Optimization Tests           │
───────┼────────────────┼─────────────────────┼──────────────────────────────────────┼──────────────────────────────
 1.3   │ Sequential     │ Test Expert         │ [T160] Contract Validation          │ mvn test
       │                │                     │ [T161] Performance Smoke            │
───────┼────────────────┼─────────────────────┼──────────────────────────────────────┼──────────────────────────────
 Done  │ —              │ Lead Agent          │ Phase 1 sign-off                    │ ✅ READY

LEGEND:
[Tnnn] = Task ID
Parallel = may run alongside other phases; Sequential = must run one after another
Every phase includes an explicit validation command
Check Action uses mvn/gradle/cli commands or equivalent verification step
```

---

### 12. Output to User

**Produce a concise optimization report** that leads with the phase table:

1. **Minimal Summary**: One sentence (max two) highlighting the primary optimization gain or risk reminder.
2. **Phase Execution Matrix**: Present the table from Step 11 exactly once; this is the focal artifact.
3. **Supporting Sections** (only if needed): Keep Dependency Analysis, Parallelization Opportunities, Subagent Strategy, Resource Estimation, Risk Assessment, Recommendations, and Next Steps succinct—use bullets and avoid repetition. Skip sections that add no new signal.

Ensure the report keeps the table front-and-center and avoids reintroducing time-based columns.

```
RECOMMENDED NEXT STEPS

1. ✅ VALIDATE THIS PLAN
   - Review the phase matrix above for feasibility
   - Confirm subagent availability: [N] concurrent agents
   - Confirm resource availability: [MB] peak memory
   - Estimate actual duration: [minutes] (add 20% buffer)

2. 📋 PREPARE EXECUTION
   - Ensure tasks.md is up-to-date with all task IDs, [P] markers
   - Verify pom.xml, application.yml, test configuration exist
   - Have CI/CD integration ready for compilation checkpoints

3. ⚡ EXECUTE WITH OPTIMIZATION
   - Use `/speckit.implement` with --optimize flag to follow this plan
   - Monitor Phase 1.1 completion before starting Phase 1.2
   - Watch compilation checkpoints - halt if any fail
   - Validate tests pass at end of Phase 1

4. 📊 TRACK PROGRESS
   - Record actual vs estimated effort for each phase
   - Document any blockers or task failures
   - Use data for refining future optimizations

5. 🚀 PROCEED TO NEXT PHASE
   - After Phase 1 validation passes: Proceed to Phase 2
   - Use same optimization strategy for subsequent phases
   - Adjust subagent assignments based on Phase 1 learnings
```

---

## Optimization Principles

### What This Command Does

✅ **DOES**:
- Analyze task.md for dependencies and parallelization
- Calculate resource requirements
- Identify optimal subagent allocation strategy
- Build a phase-oriented execution plan with batching guidance
- Provide checkpoint/validation strategy
- Quantify optimization benefits (time savings, resource efficiency)
- Recommend risk mitigation approaches

❌ **DOES NOT**:
- Modify tasks.md or any files (READ-ONLY)
- Execute tasks or modify code
- Make final execution decisions (user validates)
- Guarantee timing (provides estimates only)
- Automate subagent assignment (recommends strategy)

### Analysis Quality Standards

**Evidence-Based**:
- Every timeline estimate based on task complexity assessment
- Dependency analysis grounded in task descriptions
- Resource calculations from typical Spring Boot patterns

**Actionable**:
- Specific subagent type recommendations
- Concrete batching strategy with timing
- Checkpoint strategy with validation steps

**Risk-Calibrated**:
- Identify critical path dependencies
- Highlight parallelization risks
- Provide mitigation strategies

### Token Efficiency

**Progressive analysis**:
- Load tasks on-demand
- Analyze phase-by-phase
- Summarize large dependency graphs
- Focus on high-impact optimizations

**Compact reporting**:
- Use tables for timeline visualization
- Group related findings
- Provide executive summary
- Link to detailed analysis

## Validation

Before outputting report, verify:

- [ ] All task IDs from tasks.md extracted correctly
- [ ] Dependency analysis covers all blocking relationships
- [ ] Timeline accounts for compilation/validation checkpoints
- [ ] Subagent allocation realistic (not over-subscribing)
- [ ] Resource estimates reasonable for Spring Boot stack
- [ ] Risk assessment identifies critical paths
- [ ] Recommendations are specific and implementable
- [ ] Report is concise yet complete (token-efficient)

## Context

$ARGUMENTS

## Execution Instructions

**Agent Selection**: To execute this task, use the following approach:
- Primary: Use `general-purpose` agent with appropriate domain expertise
- Or use specialized agent if available for the specific task type
