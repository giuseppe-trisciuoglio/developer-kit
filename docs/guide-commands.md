# Complete Guide to Developer Kit Commands

This guide documents all 35 commands available in the Developer Kit, organized by category with brief descriptions, usage, and practical examples. See individual command files for complete details.

---

## Table of Contents

1. [Java Development Commands](#java-development-commands)
2. [TypeScript Commands](#typescript-commands)
3. [GitHub Commands](#github-commands)
4. [Security Commands](#security-commands)
5. [Documentation Commands](#documentation-commands)
6. [Workflow Commands](#workflow-commands)
7. [LRA (Long-Running Agent) Commands](#lra-long-running-agent-commands)
8. [Spec Kit Commands](#spec-kit-commands)
9. [Skill Management Commands](#skill-management-commands)
10. [Common Workflows](#common-workflows)

---

## Java Development Commands

### `/devkit.java.code-review`

**File**: `commands/devkit.java.code-review.md`

**Purpose**: Comprehensive code review of Java/Spring Boot applications for architecture, security, performance, and best practices.

**Usage:**
```bash
/devkit.java.code-review [full|security|performance|architecture|testing|best-practices] [path] [options]
```

**Common use cases:**
- Before creating a pull request
- After completing a feature
- Verifying code quality
- Refactoring critical components

---

### `/devkit.java.architect-review`

**File**: `commands/devkit.java.architect-review.md`

**Purpose**: High-level architecture review of Java codebases focusing on design patterns, scalability, and architectural decisions.

**Usage:**
```bash
/devkit.java.architect-review [path]
```

---

### `/devkit.java.security-review`

**File**: `commands/devkit.java.security-review.md`

**Purpose**: Security-focused audit for Spring Boot and Jakarta EE applications covering OWASP, CVEs, and configurations.

**Usage:**
```bash
/devkit.java.security-review [path]
```

---

### `/devkit.java.write-unit-tests`

**File**: `commands/devkit.java.write-unit-tests.md`

**Purpose**: Generate comprehensive JUnit 5 unit tests with Mockito and AssertJ patterns.

**Usage:**
```bash
/devkit.java.write-unit-tests [class-path]
```

---

### `/devkit.java.write-integration-tests`

**File**: `commands/devkit.java.write-integration-tests.md`

**Purpose**: Generate Spring Boot integration tests using Testcontainers for complete workflow testing.

**Usage:**
```bash
/devkit.java.write-integration-tests [test-scope]
```

---

### `/devkit.java.generate-crud`

**File**: `commands/devkit.java.generate-crud.md`

**Purpose**: Generate complete CRUD implementation (controllers, services, DTOs) from a domain class.

**Usage:**
```bash
/devkit.java.generate-crud [class-path]
```

---

### `/devkit.java.generate-docs`

**File**: `commands/devkit.java.generate-docs.md`

**Purpose**: Generate comprehensive API documentation, architecture guides, and technical manuals.

**Usage:**
```bash
/devkit.java.generate-docs [project-path]
```

---

### `/devkit.java.refactor-class`

**File**: `commands/devkit.java.refactor-class.md`

**Purpose**: Intelligent refactoring with Clean Architecture, DDD patterns, and Spring Boot best practices.

**Usage:**
```bash
/devkit.java.refactor-class [class-path] [cleanup|architecture|performance|security|testing|comprehensive]
```

---

### `/devkit.java.dependency-audit`

**File**: `commands/devkit.java.dependency-audit.md`

**Purpose**: Comprehensive dependency audit for vulnerabilities, licenses, and update recommendations.

**Usage:**
```bash
/devkit.java.dependency-audit [project-path]
```

---

### `/devkit.java.upgrade-dependencies`

**File**: `commands/devkit.java.upgrade-dependencies.md`

**Purpose**: Safe dependency upgrade strategies with compatibility testing and rollback procedures.

**Usage:**
```bash
/devkit.java.upgrade-dependencies [project-path]
```

---

## TypeScript Commands

### `/devkit.typescript.code-review`

**File**: `commands/devkit.typescript.code-review.md`

**Purpose**: Comprehensive code review of TypeScript codebases for quality, patterns, and best practices.

**Usage:**
```bash
/devkit.typescript.code-review [full|security|performance|architecture] [path]
```

---

### `/devkit.ts.security-review`

**File**: `commands/devkit.ts.security-review.md`

**Purpose**: Security audit for TypeScript/Node.js applications (Next.js, NestJS, Express) with OWASP Top 10 analysis.

**Usage:**
```bash
/devkit.ts.security-review [path]
```

---

## GitHub Commands

### `/devkit.github.create-pr`

**File**: `commands/devkit.github.create-pr.md`

**Purpose**: Create GitHub pull requests with automated branch creation, commits, and description.

**Usage:**
```bash
/devkit.github.create-pr [pr-description]
```

**Features:**
- Automatic branch creation
- Git commit management
- Automated PR description
- Automated commit messages

---

### `/devkit.github.review-pr`

**File**: `commands/devkit.github.review-pr.md`

**Purpose**: Comprehensive GitHub PR review covering code quality, security, performance, and testing.

**Usage:**
```bash
/devkit.github.review-pr [pr-number|pr-url]
```

---

## Security Commands

### `/devkit.generate-security-assessment`

**File**: `commands/devkit.generate-security-assessment.md`

**Purpose**: Generate comprehensive security assessment documentation (multi-language support).

**Usage:**
```bash
/devkit.generate-security-assessment [language] [output-file]
```

**Supported languages:**
- English
- Italian
- Spanish
- French
- German
- Portuguese

---

## Documentation Commands

### `/devkit.generate-document`

**File**: `commands/devkit.generate-document.md`

**Purpose**: Generate professional technical and business documents with multi-language support.

**Usage:**
```bash
/devkit.generate-document [assessment|feature|analysis|process|custom] [output-file]
```

**Document types:**
- Assessment documents
- Feature specifications
- Technical analysis
- Process documentation
- Custom documents

---

### `/devkit.generate-changelog`

**File**: `commands/devkit.generate-changelog.md`

**Purpose**: Generate or update CHANGELOG.md with git integration for any project type.

**Usage:**
```bash
/devkit.generate-changelog [project-path] [version]
```

---

### `/devkit.write-a-minute-of-a-meeting`

**File**: `commands/devkit.write-a-minute-of-a-meeting.md`

**Purpose**: Generate professional meeting minutes and action items from transcripts or notes.

**Usage:**
```bash
/devkit.write-a-minute-of-a-meeting [meeting-transcript-or-notes]
```

---

### `/devkit.generate-refactoring-tasks`

**File**: `commands/devkit.generate-refactoring-tasks.md`

**Purpose**: Generate detailed, step-by-step refactoring plan for complex Java classes.

**Usage:**
```bash
/devkit.generate-refactoring-tasks [class-path] [complexity-level]
```

---

## Workflow Commands

### `/devkit.feature-development`

**File**: `commands/devkit.feature-development.md`

**Purpose**: Systematic 9-phase approach for guided feature development with specialist agents.

**Usage:**
```bash
/devkit.feature-development [feature-description]
```

**Phases:**
1. Analysis
2. Architecture
3. Implementation planning
4. Implementation
5. Testing
6. Code review
7. Documentation
8. Integration verification
9. Completion

---

### `/devkit.fix-debugging`

**File**: `commands/devkit.fix-debugging.md`

**Purpose**: Structured debugging workflow for identifying and fixing errors.

**Usage:**
```bash
/devkit.fix-debugging [error-description|stack-trace]
```

---

### `/devkit.refactor`

**File**: `commands/devkit.refactor.md`

**Purpose**: Guided code refactoring workflow with quality improvements.

**Usage:**
```bash
/devkit.refactor [file-path] [refactoring-scope]
```

---

### `/devkit.brainstorm`

**File**: `commands/devkit.brainstorm.md`

**Purpose**: Transform ideas into fully formed designs through structured dialogue, codebase exploration, and specialist agent collaboration.

**Usage:**
```bash
/devkit.brainstorm [idea-description]
```

**Phases:**
1. Context Discovery
2. Idea Refinement (one question at a time)
3. Approach Exploration (2-3 alternatives with trade-offs)
4. Codebase Exploration (uses `general-code-explorer` agent)
5. Design Presentation (incremental validation)
6. Documentation Generation (uses `document-generator-expert` agent)
7. Document Review (uses `general-code-reviewer` agent)
8. Next Steps Recommendation
9. Summary

**Output:**
- Design document saved to `docs/plans/YYYY-MM-DD--design.md`
- Automatic recommendation for next development command with pre-filled arguments
- Codebase analysis ensures design aligns with existing patterns

---

### `/devkit.prompt-optimize`

**File**: `commands/devkit.prompt-optimize.md`

**Purpose**: Optimize prompts for better AI performance and save results to `optimized-prompt.md`.

**Usage:**
```bash
/devkit.prompt-optimize [prompt-to-optimize]
```

---

## LRA (Long-Running Agent) Commands

Long-Running Agent commands manage complex projects spanning multiple context windows based on [Anthropic's research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

### `/devkit.lra.init`

**File**: `commands/devkit.lra.init.md`

**Purpose**: Initialize LRA environment for multi-session project management.

**Usage:**
```bash
/devkit.lra.init [project-description]
```

**Creates:**
- Feature list
- Progress tracking
- Init script

---

### `/devkit.lra.start-session`

**File**: `commands/devkit.lra.start-session.md`

**Purpose**: Start a new coding session with progress status and feature selection.

**Usage:**
```bash
/devkit.lra.start-session
```

---

### `/devkit.lra.add-feature`

**File**: `commands/devkit.lra.add-feature.md`

**Purpose**: Add new feature to the project list during development.

**Usage:**
```bash
/devkit.lra.add-feature [feature-description]
```

---

### `/devkit.lra.mark-feature`

**File**: `commands/devkit.lra.mark-feature.md`

**Purpose**: Mark feature as passed or failed after implementation and testing.

**Usage:**
```bash
/devkit.lra.mark-feature [feature-id] [passed|failed]
```

---

### `/devkit.lra.checkpoint`

**File**: `commands/devkit.lra.checkpoint.md`

**Purpose**: Create session checkpoint with commits and progress updates.

**Usage:**
```bash
/devkit.lra.checkpoint [summary-message]
```

---

### `/devkit.lra.status`

**File**: `commands/devkit.lra.status.md`

**Purpose**: Display project status, progress metrics, and recent activity.

**Usage:**
```bash
/devkit.lra.status
```

---

### `/devkit.lra.recover`

**File**: `commands/devkit.lra.recover.md`

**Purpose**: Recover from broken state with diagnostics and restoration.

**Usage:**
```bash
/devkit.lra.recover [--diagnose|--revert]
```

---

## Spec Kit Commands

Spec Kit commands provide comprehensive project planning and verification.

### `/speckit.check-integration`

**File**: `commands/speckit.check-integration.md`

**Purpose**: Verify task integration with existing codebase. Detect duplication and integration opportunities.

**Usage:**
```bash
/speckit.check-integration
```

**Run after**: `/speckit.tasks`

---

### `/speckit.optimize`

**File**: `commands/speckit.optimize.md`

**Purpose**: Optimize execution plan for parallelization and subagent assignment.

**Usage:**
```bash
/speckit.optimize
```

**Run after**: `/speckit.check-integration`

---

### `/speckit.verify`

**File**: `commands/speckit.verify.md`

**Purpose**: Comprehensive implementation verification covering requirements, tests, and code quality.

**Usage:**
```bash
/speckit.verify
```

**Run after**: `/speckit.implement`

---

## Skill Management Commands

### `/devkit.verify-skill`

**File**: `commands/devkit.verify-skill.md`

**Purpose**: Validate skill compliance with DevKit standards, format, and best practices.

**Usage:**
```bash
/devkit.verify-skill [skill-name]
```

**Checks:**
- SKILL.md frontmatter
- File structure and syntax
- Content quality
- Referenced files existence

---

## Common Workflows

### Code Review Workflow

```
1. /devkit.java.code-review full [path]         # Initial review
2. /devkit.java.security-review [path]          # Security audit
3. /devkit.java.architect-review [path]         # Architecture check
4. /devkit.github.review-pr [pr-number]         # PR review
```

### Feature Development Workflow

```
# Optional: Start with brainstorming for new ideas
1. /devkit.brainstorm [idea-description]
   (Creates design document, recommends next command)

# Then proceed with implementation
2. /devkit.feature-development [feature-description]
   (Guides through 9 phases: analysis → architecture → implementation → testing → review → documentation → completion)
```

### Refactoring Workflow

```
1. /devkit.java.code-review full [path]
2. /devkit.generate-refactoring-tasks [class]
3. /devkit.java.refactor-class [class] comprehensive
4. /devkit.java.write-unit-tests [refactored-class]
5. /devkit.java.code-review full [path]
```

### Security Audit Workflow

```
1. /devkit.java.security-review [path]
2. /devkit.ts.security-review [path]
3. /devkit.generate-security-assessment [language] [output-file]
```

### LRA Multi-Session Workflow

```
Session 1:
  1. /devkit.lra.init [project-description]
  2. /devkit.lra.start-session
  3. ... implement feature 1 ...
  4. /devkit.lra.mark-feature feature-1 passed
  5. /devkit.lra.checkpoint "Session 1 complete"

Session 2:
  1. /devkit.lra.start-session
  2. ... implement feature 2 ...
  3. /devkit.lra.mark-feature feature-2 passed
  4. /devkit.lra.checkpoint "Session 2 complete"
```

### Spec Kit Workflow

```
1. /speckit.tasks
2. /speckit.check-integration
3. /speckit.optimize
4. /speckit.implement
5. /speckit.verify
```

---

## Quick Reference

| Command | Category | Purpose |
|---------|----------|---------|
| `/devkit.java.code-review` | Java | Code quality review |
| `/devkit.java.security-review` | Java | Security audit |
| `/devkit.java.write-unit-tests` | Java | Generate unit tests |
| `/devkit.java.generate-crud` | Java | Generate CRUD code |
| `/devkit.typescript.code-review` | TypeScript | Code quality review |
| `/devkit.ts.security-review` | TypeScript | Security audit |
| `/devkit.github.create-pr` | GitHub | Create pull request |
| `/devkit.github.review-pr` | GitHub | Review pull request |
| `/devkit.feature-development` | Workflow | Guided feature development |
| `/devkit.fix-debugging` | Workflow | Debug errors |
| `/devkit.refactor` | Workflow | Code refactoring |
| `/devkit.lra.init` | LRA | Initialize project |
| `/devkit.lra.start-session` | LRA | Start session |
| `/devkit.lra.checkpoint` | LRA | Save session progress |
| `/speckit.check-integration` | Spec Kit | Check integration |
| `/speckit.optimize` | Spec Kit | Optimize plan |
| `/speckit.verify` | Spec Kit | Verify completion |
| `/devkit.generate-document` | Documentation | Create documents |
| `/devkit.generate-changelog` | Documentation | Update changelog |
| `/devkit.brainstorm` | Workflow | Design brainstorming |
| `/devkit.verify-skill` | Skill Mgmt | Validate skill |

---

## Using Commands in Claude Code

### Direct Invocation

```bash
/devkit.java.code-review full src/main/java
/devkit.feature-development "User authentication system"
/devkit.lra.start-session
```

### Within Conversations

Include command references in your prompt:

```
I need to review my Spring Boot service. Can you run /devkit.java.code-review security?
```

### Combining Commands

Use command outputs as input for subsequent commands:

```bash
1. /devkit.java.code-review full
2. Review the output
3. /devkit.java.refactor-class [identified-class] comprehensive
4. /devkit.java.write-unit-tests [refactored-class]
```

---

**Note**: For complete details on each command, see the individual command files in `commands/` directory.
