# Developer Kit Core Agent Guide

Overview of all agents available in the Developer Kit Core plugin and across all Developer Kit plugins.

---

## Developer Kit Core Agents

**Plugin:** `developer-kit-core`

General-purpose agents for code analysis, review, refactoring, architecture, debugging, documentation, and pattern learning. These agents work across all programming languages and frameworks.

| Agent | Purpose | Tools | Model |
|-------|---------|-------|-------|
| `general-code-explorer` | Deep codebase analysis by tracing execution paths, mapping architecture layers, understanding patterns, documenting dependencies | Read, Write, Edit, Glob, Grep, Bash | haiku |
| `general-code-reviewer` | Code review for bugs, logic errors, security, quality — reports only issues with confidence >= 80% | Read, Write, Edit, Glob, Grep, Bash | sonnet |
| `general-refactor-expert` | Code refactoring with clean code principles, SOLID patterns, language-specific best practices | Read, Write, Edit, Glob, Grep, Bash | sonnet |
| `general-software-architect` | Feature architecture design — analyzes existing patterns, delivers implementation blueprints with files, components, data flows | Read, Write, Edit, Glob, Grep, Bash | sonnet |
| `general-debugger` | Root cause analysis — traces execution paths, analyzes stack traces, identifies failure points, proposes targeted fixes | Read, Write, Edit, Glob, Grep, Bash | sonnet |
| `document-generator-expert` | Professional document generation (assessments, specs, analysis reports, process docs) with multi-language support | Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion | sonnet |
| `learn-analyst` | Forensic code analysis to extract development patterns, conventions, architectural rules — produces structured JSON reports | Read, Glob, Grep, Bash | sonnet |

### When to Use Core Agents

- **Cross-language tasks** — Core agents work with any language/framework
- **Architecture planning** — Use `general-software-architect` for feature design
- **Code review** — Use `general-code-reviewer` for any codebase
- **Debugging** — Use `general-debugger` for root cause analysis
- **Documentation** — Use `document-generator-expert` for technical docs
- **Pattern learning** — Use `learn` skill to extract project conventions

---

## Language-Specific Plugins

### Java Plugin Agents

**Plugin:** `developer-kit-java`

| Agent | Purpose |
|-------|---------|
| `spring-boot-backend-development-expert` | Spring Boot backend development |
| `spring-boot-code-review-expert` | Spring Boot code quality and best practices |
| `spring-boot-unit-testing-expert` | JUnit and Spring Boot testing |
| `java-refactor-expert` | Java code refactoring |
| `java-security-expert` | Java security vulnerability assessment |
| `java-software-architect-review` | Java architecture design review |
| `java-documentation-specialist` | Java documentation generation |
| `java-tutorial-engineer` | Java learning and tutorials |
| `langchain4j-ai-development-expert` | LangChain4J AI integration |

**See:** [Java Agent Guide](../developer-kit-java/docs/guide-agents.md)

---

### TypeScript Plugin Agents

**Plugin:** `developer-kit-typescript`

| Agent | Purpose |
|-------|---------|
| `nestjs-backend-development-expert` | NestJS backend development |
| `nestjs-code-review-expert` | NestJS code quality review |
| `nestjs-database-expert` | NestJS database integration |
| `nestjs-security-expert` | NestJS security implementation |
| `nestjs-testing-expert` | NestJS testing strategies |
| `nestjs-unit-testing-expert` | NestJS unit testing |
| `react-frontend-development-expert` | React frontend development |
| `react-software-architect-review` | React architecture review |
| `typescript-refactor-expert` | TypeScript refactoring |
| `typescript-security-expert` | TypeScript security assessment |
| `typescript-software-architect-review` | TypeScript architecture review |
| `typescript-documentation-expert` | TypeScript documentation |
| `expo-react-native-development-expert` | React Native with Expo |

**See:** [TypeScript Agent Guide](../developer-kit-typescript/docs/guide-agents.md)

---

### Python Plugin Agents

**Plugin:** `developer-kit-python`

| Agent | Purpose |
|-------|---------|
| `python-code-review-expert` | Python code quality review |
| `python-refactor-expert` | Python refactoring (PEP standards) |
| `python-security-expert` | Python security assessment |
| `python-software-architect-expert` | Python architecture design |

**See:** [Python Agent Guide](../developer-kit-python/docs/guide-agents.md)

---

### PHP Plugin Agents

**Plugin:** `developer-kit-php`

| Agent | Purpose |
|-------|---------|
| `php-code-review-expert` | PHP code quality review |
| `php-refactor-expert` | PHP refactoring |
| `php-security-expert` | PHP security assessment |
| `php-software-architect-expert` | PHP architecture design |
| `wordpress-development-expert` | WordPress development |

**See:** [PHP Agent Guide](../developer-kit-php/docs/guide-agents.md)

---

### AWS Plugin Agents

**Plugin:** `developer-kit-aws`

| Agent | Purpose |
|-------|---------|
| `aws-solution-architect-expert` | AWS solution architecture design |
| `aws-architecture-review-expert` | AWS architecture review (Well-Architected Framework) |
| `aws-cloudformation-devops-expert` | CloudFormation IaC and DevOps automation |

**See:** [AWS Agent Guide](../developer-kit-aws/docs/guide-agents.md)

---

### AI Plugin Agents

**Plugin:** `developer-kit-ai`

| Agent | Purpose |
|-------|---------|
| `prompt-engineering-expert` | Prompt optimization and pattern design |

**See:** [AI Agent Guide](../developer-kit-ai/docs/guide-agents.md)

---

### DevOps Plugin Agents

**Plugin:** `developer-kit-devops`

| Agent | Purpose |
|-------|---------|
| `general-docker-expert` | Docker containerization and orchestration |
| `github-actions-pipeline-expert` | GitHub Actions CI/CD pipeline development |

**See:** [DevOps Agent Guide](../developer-kit-devops/docs/guide-agents.md)

---

## Agent Selection Guide

| Task | Recommended Agent | Plugin |
|------|-------------------|--------|
| Understand codebase | `general-code-explorer` | Core |
| Review code quality | `{language}-code-review-expert` | Language-specific |
| Design architecture | `{language}-software-architect` | Language-specific |
| Debug issues | `general-debugger` | Core |
| Refactor code | `{language}-refactor-expert` | Language-specific |
| Generate docs | `document-generator-expert` | Core |
| Security review | `{language}-security-expert` | Language-specific |
| Write tests | `{framework}-testing-expert` | Framework-specific |
| AWS architecture | `aws-solution-architect-expert` | AWS |
| Prompt engineering | `prompt-engineering-expert` | AI |
| Extract project patterns | `learn` (skill) + `learn-analyst` (agent) | Core |
| Docker/containers | `general-docker-expert` | DevOps |
| CI/CD pipelines | `github-actions-pipeline-expert` | DevOps |

---

## Common Workflows

### Code Review Workflow

1. Select appropriate reviewer agent based on language/framework
2. Provide context: files to review, specific concerns
3. Review findings: agent returns prioritized issues
4. Address critical and high-priority items
5. Re-review to validate fixes

### Architecture Design Workflow

1. Use `general-software-architect` to design feature architecture
2. Review with language-specific architect if needed
3. Implement based on architecture blueprint
4. Validate with `general-code-reviewer`

### Pattern Learning Workflow

1. Invoke `/learn` skill
2. Skill orchestrates `learn-analyst` agent for forensic analysis
3. Review findings (top 3 by impact score)
4. Approve rules to persist to `.claude/rules/`

---

## See Also

- [Command Guide](./guide-commands.md) — All available commands
- [LRA Workflow Guide](./guide-lra-workflow.md) — Long-running agent session management
- [Installation Guide](./installation.md) — Installation instructions
