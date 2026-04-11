# Developer Kit Core Command Guide

Complete reference for all 16 commands available in the Developer Kit Core plugin.

---

## Command Overview

Commands are reusable workflows that guide Claude through specific procedures with mandatory confirmation gates. They support multi-phase workflows with user checkpoints.

### Invocation

```bash
/developer-kit:devkit.<command-name> [arguments]
```

---

## Core Workflow Commands

### devkit.feature-development

**Purpose:** Guided feature implementation with architecture focus

**Arguments:** `[--lang=...] [feature-description]`

**Workflow:** 7-phase process with mandatory user confirmation gates:
1. Feature analysis and scoping
2. Architecture design
3. Implementation planning
4. Code generation
5. Testing
6. Verification
7. Documentation

**Example:**
```bash
/developer-kit:devkit.feature-development "Add user authentication with JWT tokens"
```

---

### devkit.refactor

**Purpose:** Guided code refactoring with deep codebase understanding

**Arguments:** `[--lang=...] [--scope=...] [refactor-description]`

**Features:**
- Compatibility options (backward, forward)
- Comprehensive verification
- Multi-phase workflow

**Example:**
```bash
/developer-kit:devkit.refactor --lang=java "Refactor UserService to use dependency injection"
```

---

### devkit.fix-debugging

**Purpose:** Guided bug fixing with systematic root cause analysis

**Arguments:** `[--lang=...] [issue-description]`

**Workflow:** 8-phase systematic debugging:
1. Issue reproduction
2. Log analysis
3. Stack trace examination
4. Root cause identification
5. Fix design
6. Implementation
7. Verification
8. Regression prevention

**Example:**
```bash
/developer-kit:devkit.fix-debugging "Login fails with 500 error on POST /api/auth/login"
```

---

### devkit.verify-skill

**Purpose:** Validates a skill against DevKit standards

**Arguments:** `[skill-name]`

**Checks:**
- Required fields (name, description)
- Template structure compliance
- Dependency validation

**Example:**
```bash
/developer-kit:devkit.verify-skill spring-boot-actuator
```

---

## Documentation Generation Commands

### devkit.generate-document

**Purpose:** Generate professional documents

**Document Types:**
- Assessments
- Feature specifications
- Analysis reports
- Process documentation
- Custom documents

**Features:**
- Multi-language support (en, it, es, fr, de, pt)
- Professional formatting
- Structured output

**Example:**
```bash
/developer-kit:devkit.generate-document --type=assessment "Security Assessment for API"
```

---

### devkit.generate-changelog

**Purpose:** Generate and manage project changelog

**Standards:**
- [Keep a Changelog](https://keepachangelog.com/) format
- Git integration for automatic change detection
- Semantic versioning guidance

**Example:**
```bash
/developer-kit:devkit.generate-changelog
```

---

### devkit.generate-security-assessment

**Purpose:** Generate comprehensive security assessment document

**Use Case:** After completing a security audit

**Output:**
- Executive summary
- Vulnerability findings
- Risk assessment
- Remediation recommendations

**Example:**
```bash
/developer-kit:devkit.generate-security-assessment
```

---

## GitHub Integration Commands

### devkit.github.create-pr

**Purpose:** Create GitHub pull request with branch creation and commits

**Features:**
- Automatic branch naming (`feature/`, `fix/`, `refactor/`)
- Detailed PR description from changes
- Commit message guidance
- Base branch detection

**Example:**
```bash
/developer-kit:devkit.github.create-pr
```

---

### devkit.github.review-pr

**Purpose:** Comprehensive PR review

**Areas Covered:**
- Code quality
- Security vulnerabilities
- Best practices
- Performance concerns
- Documentation completeness

**Example:**
```bash
/developer-kit:devkit.github.review-pr https://github.com/org/repo/pull/123
```

---

## Long-Running Agent (LRA) Workflow Commands

LRA commands manage multi-session development for projects spanning hours or days.

### devkit.lra.init

**Purpose:** Initialize LRA environment for a new project

**Creates:**
- `.lra/feature-list.json` — All features with status
- `.lra/progress.txt` — Session log
- `.lra/init.sh` — Environment setup script

**Example:**
```bash
/developer-kit:devkit.lra.init "Build chat app with user auth and AI responses"
```

---

### devkit.lra.add-feature

**Purpose:** Add a new feature to the feature list

**Arguments:** `[category] [priority] [description]`

**Categories:** `core`, `ui`, `api`, `database`, `auth`, `testing`, `other`

**Priorities:** `critical`, `high`, `medium`, `low`

**Example:**
```bash
/developer-kit:devkit.lra.add-feature api high "Add user preferences endpoint"
```

---

### devkit.lra.start-session

**Purpose:** Start a new coding session with full context restoration

**Protocol:**
1. Load progress and features
2. Check git status and health
3. Select next feature
4. Display implementation approach

**Example:**
```bash
/developer-kit:devkit.lra.start-session
```

---

### devkit.lra.checkpoint

**Purpose:** Create session checkpoint with git commit and progress update

**Actions:**
1. Stage all changes
2. Create git commit
3. Update progress log
4. Tag session milestone

**Example:**
```bash
/developer-kit:devkit.lra.checkpoint "Implemented user registration with validation"
```

---

### devkit.lra.mark-feature

**Purpose:** Mark feature as completed or failed

**Arguments:** `[feature-id] [passed|failed]`

**Example:**
```bash
/developer-kit:devkit.lra.mark-feature F001 passed
/developer-kit:devkit.lra.mark-feature F002 failed
```

---

### devkit.lra.status

**Purpose:** Display current project status and progress

**Output:**
- Total features (completed/pending)
- Completion percentage
- Recent commits
- Active feature details
- Next features to implement

**Example:**
```bash
/developer-kit:devkit.lra.status
```

---

### devkit.lra.recover

**Purpose:** Recover from broken state with diagnostics

**Options:**
- `--diagnose` — Analyze issues without changes
- `--revert` — Revert to last known good state

**Example:**
```bash
/developer-kit:devkit.lra.recover --diagnose
/developer-kit:devkit.lra.recover --revert
```

---

## Command Selection Guide

| Task | Command | Plugin |
|------|---------|--------|
| Implement new feature | `/developer-kit:devkit.feature-development` | Core |
| Refactor existing code | `/developer-kit:devkit.refactor` | Core |
| Debug and fix issue | `/developer-kit:devkit.fix-debugging` | Core |
| Validate a skill | `/developer-kit:devkit.verify-skill` | Core |
| Generate professional doc | `/developer-kit:devkit.generate-document` | Core |
| Update changelog | `/developer-kit:devkit.generate-changelog` | Core |
| Security assessment | `/developer-kit:devkit.generate-security-assessment` | Core |
| Create PR | `/developer-kit:devkit.github.create-pr` | Core |
| Review PR | `/developer-kit:devkit.github.review-pr` | Core |
| Start LRA project | `/developer-kit:devkit.lra.init` | Core |
| Add LRA feature | `/developer-kit:devkit.lra.add-feature` | Core |
| Start coding session | `/developer-kit:devkit.lra.start-session` | Core |
| Checkpoint progress | `/developer-kit:devkit.lra.checkpoint` | Core |
| Mark feature done | `/developer-kit:devkit.lra.mark-feature` | Core |
| Check project status | `/developer-kit:devkit.lra.status` | Core |
| Recover from broken state | `/developer-kit:devkit.lra.recover` | Core |

---

## Language Support

Commands support `--lang` parameter to use specialized language-specific agents:

| Language | Agents Used |
|----------|-------------|
| Java/Spring Boot | `spring-boot-backend-development-expert`, `java-software-architect-review` |
| TypeScript | `typescript-software-architect-review`, `nestjs-code-review-expert` |
| NestJS | `nestjs-backend-development-expert`, `nestjs-code-review-expert` |
| React | `react-frontend-development-expert`, `react-software-architect-review` |
| Python | `python-software-architect-expert`, `python-code-review-expert` |
| AWS | `aws-solution-architect-expert`, `aws-cloudformation-devops-expert` |
| General | `general-code-explorer`, `general-software-architect` |

---

## See Also

- [Agent Guide](./guide-agents.md) — All available agents
- [LRA Workflow Guide](./guide-lra-workflow.md) — Complete LRA documentation
- [Installation Guide](./installation.md) — Installation instructions
