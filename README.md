# Developer Kit for Claude Code

[![Security Scan](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml)
[![Plugin Validation](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml)

> A modular plugin system of reusable skills, agents, and commands for automating development tasks in Claude Code

**Listed on:**
- [context7](https://context7.com/giuseppe-trisciuoglio/developer-kit?tab=skills) — Skills marketplace
- [skills.sh](https://skills.sh/giuseppe-trisciuoglio/developer-kit) — AI skills directory

**Developer Kit for Claude Code** teaches Claude how to **perform development tasks in a repeatable way** across
multiple languages and frameworks. Built as a modular marketplace, you can install only the plugins you need.

## Quick Start

```bash
# Install from marketplace (recommended)
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# Or install from local directory
/plugin install /path/to/developer-kit
```

**Claude Desktop**: [Enable Skills in Settings](https://claude.ai/settings/capabilities)

---

## Architecture

Developer Kit is organized as a **modular marketplace** with 11 independent plugins:

```
plugins/
├── developer-kit-core/            # Core agents/commands/skills (required)
├── developer-kit-java/            # Java/Spring Boot/LangChain4J/AWS SDK/GraalVM Native Image
├── developer-kit-typescript/      # NestJS/React/React Native/Next.js/Drizzle/Monorepo
├── developer-kit-python/          # Python development/AWS Lambda
├── developer-kit-php/             # PHP/WordPress/AWS Lambda
├── developer-kit-aws/             # AWS CloudFormation/AWS Architecture
├── developer-kit-ai/              # Prompt Engineering/RAG/Chunking
├── developer-kit-devops/          # Docker/GitHub Actions
├── developer-kit-project-management/  # LRA workflow/Meetings
├── developer-kit-tools/           # Additional development tools and MCP integrations
└── github-spec-kit/               # GitHub specification integration
```

Current marketplace totals: **116 skills**, **43 agents**, and **44 commands** across the 11 plugin manifests.

Language plugins (Java, TypeScript, Python, PHP) include **coding rules** (`rules/` directory) that auto-activate via `globs:` path-scoped matching to enforce naming conventions, project structure, language best practices, and error handling patterns. They also include **LSP server configurations** (`.lsp.json`) for real-time code intelligence, diagnostics, and navigation features.

---

## Workflow

The Developer Kit follows a systematic development workflow that ensures high-quality, well-documented features from idea to implementation:

### 1. Brainstorming Phase

**Command:** `/devkit.brainstorm [idea-description]`

Start here when you have a new feature idea. This command guides you to create a **functional specification** (WHAT the system should do, not HOW):

- **Idea Refinement**: Deep exploration through structured dialogue
- **Use Case Definition**: Define user behaviors and business rules
- **Acceptance Criteria**: Establish testable conditions for completion
- **Specification Review**: Validate with user

**Output**: Functional specification saved to `docs/specs/YYYY-MM-DD--feature-name.md`

**Example:**
```bash
/devkit.brainstorm Add user authentication with JWT tokens
```

**Next step:** After specification, continue with `/devkit.spec-to-tasks`

### 2. Specification to Tasks Phase

**Command:** `/devkit.spec-to-tasks [--lang=java|spring|typescript|nestjs|react|python|general] [spec-file]`

Converts the functional specification into atomic, executable tasks:

- **Task Decomposition**: Break down specification into actionable tasks
- **Dependency Mapping**: Identify task dependencies
- **Acceptance Criteria**: Each task has clear completion criteria
- **Implementation Commands**: Pre-filled commands for execution
- **Complexity Scoring**: Automatic calculation of task complexity (0-100+ scale)
- **Strong Constraint**: Tasks with score ≥ 51 MUST be split before implementation

**Output**: Task list saved to `docs/specs/[id]/tasks/TASK-XXX.md` with complexity scores

**Example:**
```bash
/devkit.spec-to-tasks docs/specs/001-user-auth/
/devkit.spec-to-tasks --lang=spring docs/specs/001-user-auth/
```

**Next step:** Review task complexity and manage tasks with `/devkit.task-manage`

### 2.5. Task Management Phase (NEW)

**Command:** `/devkit.task-manage --action=[list|split|add|mark-optional|update|regenerate-index] [options]`

Manage tasks after generation to ensure they're appropriately sized and prioritized:

- **List Tasks**: View all tasks with complexity scores and recommendations
- **Split Complex Tasks**: Automatically split tasks with score ≥ 51 into smaller tasks
- **Add New Tasks**: Dynamically add tasks to existing specifications
- **Mark Optional**: Prioritize MVP by marking non-critical tasks as optional
- **Update Tasks**: Modify requirements or acceptance criteria
- **Regenerate Index**: Update task list after modifications

**Complexity Scoring:**
- Simple (0-30 ✅): OK as single task
- Moderate (31-50 ⚠️): Consider splitting
- Complex (51+ ❌): MUST split before implementation

**Examples:**
```bash
# List all tasks with complexity scores
/devkit.task-manage --action=list --spec=docs/specs/001-user-auth/

# Split a complex task
/devkit.task-manage --action=split --task=docs/specs/001-user-auth/tasks/TASK-007.md

# Mark task as optional for MVP
/devkit.task-manage --action=mark-optional --task=docs/specs/001-user-auth/tasks/TASK-010.md

# Add a new task
/devkit.task-manage --action=add --spec=docs/specs/001-user-auth/2026-03-07--user-auth.md --lang=spring
```

**Output**: Updated task files and regenerated task list index

**Next step:** Execute tasks with `/devkit.feature-development`

### 3. Feature Development Phase

**Command:** `/devkit.feature-development [--lang=spring|typescript|nestjs|react|python|general] [feature-description | "Task: task-name"]`

Use this command to implement features. Supports two modes:

**Mode 1 - Feature Development:** Implement entire features
- **Discovery**: Understand what needs to be built
- **Codebase Exploration**: Deep understanding of existing code patterns
- **Clarifying Questions**: Fill gaps and resolve ambiguities
- **Architecture Design**: Design implementation with trade-offs
- **Implementation**: Build the feature following conventions
- **Quality Review**: Ensure code quality and correctness
- **Summary**: Document what was accomplished

**Mode 2 - Task Execution:** Execute specific tasks from a task list (use "Task:" prefix)
- Reads task details from `docs/tasks/YYYY-MM-DD--*--tasks.md`
- Focuses on specific task implementation
- Updates task progress in the task list

**Language/Framework Support:**
- `--lang=spring` or `--lang=java`: Java/Spring Boot development
- `--lang=typescript` or `--lang=ts`: TypeScript/Node.js development
- `--lang=nestjs`: NestJS backend development
- `--lang=react`: React frontend development
- `--lang=python` or `--lang=py`: Python development
- `--lang=aws`: AWS infrastructure and CloudFormation
- `--lang=general` or no flag: General-purpose development

**Examples:**
```bash
# Feature Development Mode
/devkit.feature-development --lang=spring Add REST API for user management

# Task Execution Mode
/devkit.feature-development --lang=spring "Task: User login endpoint"
```

### 4. Code Review & Debug Phase

After implementation, use these specialized commands for quality assurance:

**Task Review:** `/devkit.task-review [--lang=...] [task-file]`
- Verify task implementation meets specifications
- Validate acceptance criteria
- Check specification compliance
- Perform language-specific code review
- Generate comprehensive review reports

**Code Review:** `/devkit.refactor [--lang=...] [refactoring-description]`
- Improve code structure, maintainability, and design
- Reduce technical debt
- Apply best practices and patterns

**Fix & Debug:** `/devkit.fix-debugging [--lang=...] [issue-description]`
- Systematic root cause analysis
- Minimal, focused fixes
- Verification and regression prevention

**Example:**
```bash
/devkit.task-review --lang=spring docs/specs/001-user-auth/tasks/TASK-001.md
/devkit.fix-debugging --lang=spring Bean injection failing in OrderService
/devkit.refactor --lang=typescript Simplify the authentication flow
```

### Complete Workflow Diagram

```
                         +--------------------------------------+
                         |                IDEA                  |
                         +--------------------------------------+
                                          |
                    +----------------------+----------------------+
                    |                                             |
                    +                                             +
     +-------------------------+                +-------------------------+
     |   Full Brainstorming    |                |      Quick Spec        |
     |      (9 phases)        |                |      (4 phases)        |
     +-------------------------+                +-------------------------+
                    |                                             |
                    +----------------------+----------------------+
                                           +
                         +--------------------------------------+
                         |  docs/specs/[id]/YYYY-MM-DD--name   |
                         +--------------------------------------+
                                          |
                    +----------------------+----------------------+
                    |                                             |
                    +                                             +
     +-------------------------+                +-------------------------+
     |    devkit.spec-review   |                |   devkit.spec-quality   |
     |   (interactive, max 5   |                |   (Knowledge Graph      |
     |        questions)        |                |       sync)             |
     +-------------------------+                +-------------------------+
                    |                                             |
                    +----------------------+----------------------+
                                           +
                         +--------------------------------------+
                         |       devkit.spec-to-tasks            |
                         |   (generates task list)              |
                         +--------------------------------------+
                                          |
                    +----------------------+----------------------+
                    |                                             |
                    +                                             +
     +-------------------------+                +-------------------------+
     |   devkit.task-manage    |                |   devkit.task-review    |
     |    (list/split/add)     |                |                         |
     +-------------------------+                +-------------------------+
                    |
                    +
                         +--------------------------------------+
                         |  docs/specs/[id]/tasks/TASK-XXX.md   |
                         +--------------------------------------+
                                          |
                    +----------------------+----------------------+
                    |                                             |
                    +                                             +
     +-------------------------+                +-------------------------+
     | devkit.task-implement.  |                | devkit.spec-sync       |
     |      (11 steps)          |<--------------+ (when deviations       |
     |                         |                |       detected)         |
     | - Git state check       |                +-------------------------+
     | - KG validation         |                              |
     | - Contract validation   |                              |
     | - Implementation        |                              |
     | - Verification          |                              |
     | - Auto-update KG        |                              |
     +-------------------------+                              |
                    |                                          |
                    +------------------------------------------+
                                           +
                         +--------------------------------------+
                         |           IMPLEMENTATION              |
                         +--------------------------------------+
```

### Alternative Paths

**For Bug Fixes (using Quick Spec):**
```
Bug Report -> /devkit.quick-spec -> /devkit.task-implementation -> Verification
```

**For Refactoring:**
```
Code Issue -> /devkit.brainstorm (optional) -> /devkit.refactor -> Improved code
```

**For Quick Features (using Quick Spec):**
```
Simple Feature -> /devkit.quick-spec -> Direct implementation or tasks
```

---

## Available Plugins

### developer-kit-core (Required)

Core agents, commands, and skills used by all other plugins.

| Component                    | Description                            |
|------------------------------|----------------------------------------|
| `general-code-explorer`      | Deep codebase exploration and analysis |
| `general-code-reviewer`      | Code quality and security review       |
| `general-refactor-expert`    | Code refactoring specialist            |
| `general-software-architect` | Feature architecture design            |
| `general-debugger`           | Root cause analysis and debugging      |
| `document-generator-expert`  | Professional document generation       |

**Skills**: `adr-drafting`, `memory-md-management`, `docs-updater`, `drawio-logical-diagrams`, `github-issue-workflow`, `knowledge-graph`

**Hooks**: `prevent-destructive-commands` (Python 3 PreToolUse hook for blocking dangerous Bash commands)

**Commands**: `/devkit.brainstorm`, `/devkit.quick-spec`, `/devkit.spec-to-tasks`, `/devkit.spec-quality`, `/devkit.spec-review`, `/devkit.spec-sync`,
`/devkit.task-manage`, `/devkit.task-review`, `/devkit.task-implementation`, `/devkit.refactor`, `/devkit.feature-development`,
`/devkit.fix-debugging`, `/devkit.generate-document`, `/devkit.generate-changelog`, `/devkit.github.create-pr`,
`/devkit.github.review-pr`, `/devkit.lra.*` (7 LRA workflow commands), `/devkit.verify-skill`,
`/devkit.generate-security-assessment`

---

### developer-kit-java

Comprehensive Java development toolkit with Spring Boot, testing, LangChain4J, AWS SDK, and GraalVM Native Image.

**Agents**: `spring-boot-backend-development-expert`, `spring-boot-code-review-expert`,
`spring-boot-unit-testing-expert`, `java-refactor-expert`, `java-security-expert`, `java-software-architect-review`,
`java-documentation-specialist`, `java-tutorial-engineer`, `langchain4j-ai-development-expert`

**Commands**: `/devkit.java.code-review`, `/devkit.java.generate-crud`, `/devkit.java.refactor-class`,
`/devkit.java.architect-review`, `/devkit.java.dependency-audit`, `/devkit.java.generate-docs`,
`/devkit.java.security-review`, `/devkit.java.upgrade-dependencies`, `/devkit.java.write-unit-tests`,
`/devkit.java.write-integration-tests`, `/devkit.java.generate-refactoring-tasks`

**Skills**:

- **Spring Boot**: actuator, cache, crud-patterns, dependency-injection, event-driven-patterns, openapi-documentation,
  rest-api-standards, saga-pattern, security-jwt, test-patterns, resilience4j, project-creator
- **Spring Data**: jpa, neo4j
- **Spring AI**: mcp-server-patterns
- **JUnit Testing**: application-events, bean-validation, boundary-conditions, caching, config-properties,
  controller-layer, exception-handler, json-serialization, mapper-converter, parameterized, scheduled-async,
  security-authorization, service-layer, utility-methods, wiremock-rest-api
- **Integration Testing**: wiremock-standalone-docker (WireMock standalone server via Docker for integration/E2E testing)
- **LangChain4J**: ai-services-patterns, mcp-server-patterns, rag-implementation-patterns, spring-boot-integration,
  testing-strategies, tool-function-calling-patterns, vector-stores-configuration, qdrant
- **AWS SDK**: rds-spring-boot-integration, bedrock, core, dynamodb, kms, lambda, messaging, rds, s3, secrets-manager
- **Clean Architecture**: clean-architecture
- **GraalVM**: graalvm-native-image

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`

**LSP Servers**: `java` (jdtls), `kotlin` (kotlin-language-server), `scala` (metals)

---

### developer-kit-typescript

TypeScript/JavaScript full-stack development with NestJS, React, React Native, Next.js, Drizzle ORM, DynamoDB-Toolbox, Zod validation, AWS CDK, and Monorepo tools.

**Agents**: `nestjs-backend-development-expert`, `nestjs-code-review-expert`, `nestjs-database-expert`,
`nestjs-security-expert`, `nestjs-testing-expert`, `nestjs-unit-testing-expert`, `react-frontend-development-expert`,
`react-software-architect-review`, `typescript-refactor-expert`, `typescript-security-expert`,
`typescript-software-architect-review`, `typescript-documentation-expert`, `expo-react-native-development-expert`

**Commands**: `/devkit.typescript.code-review`, `/devkit.react.code-review`, `/devkit.ts.security-review`

**Skills**:
- **Backend**: `nestjs`, `nestjs-best-practices`, `clean-architecture`, `nestjs-drizzle-crud-generator`
- **Authentication**: `better-auth`
- **Frontend**: `react-patterns`, `shadcn-ui`, `tailwind-css-patterns`, `tailwind-design-system`
- **Next.js**: `nextjs-app-router`, `nextjs-authentication`, `nextjs-data-fetching`, `nextjs-performance`, `nextjs-deployment`
- **Database & ORM**: `drizzle-orm-patterns`, `dynamodb-toolbox-patterns`, `zod-validation-utilities`
- **Monorepo**: `nx-monorepo`, `turborepo-monorepo`
- **AWS**: `aws-lambda-typescript-integration`, `aws-cdk`
- **Core**: `typescript-docs`

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`,
`nestjs-architecture`, `nestjs-api-design`, `nestjs-security`, `nestjs-testing`,
`react-component-conventions`, `react-data-fetching`, `react-routing-conventions`, `tailwind-styling-conventions`,
`drizzle-orm-conventions`, `shared-dto-conventions`, `nx-monorepo-conventions`, `i18n-conventions`,
`lambda-conventions`, `server-feature-conventions`

**LSP Servers**: `typescript`/`javascript` (typescript-language-server), `eslint` (eslint-language-server), `vue` (vue-language-server)

---

### developer-kit-python

Python development capabilities for Django, Flask, and FastAPI projects.

**Agents**: `python-code-review-expert`, `python-refactor-expert`, `python-security-expert`,
`python-software-architect-expert`

**Skills**: `clean-architecture`, `aws-lambda-python-integration`

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`

**LSP Servers**: `python` (pyright-langserver)

---

### developer-kit-php

PHP and WordPress development capabilities.

**Agents**: `php-code-review-expert`, `php-refactor-expert`, `php-security-expert`, `php-software-architect-expert`,
`wordpress-development-expert`

**Skills**: `wordpress-sage-theme` (Sage theme development), `clean-architecture`, `aws-lambda-php-integration`

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`

**LSP Servers**: `php` (intelephense)

---

### developer-kit-aws

AWS infrastructure and CloudFormation expertise for Infrastructure as Code.

**Agents**: `aws-solution-architect-expert`, `aws-cloudformation-devops-expert`, `aws-architecture-review-expert`

**Skills**:
- **CloudFormation** (15): `vpc`, `ec2`, `lambda`, `iam`, `s3`, `rds`, `dynamodb`, `ecs`, `auto-scaling`, `cloudwatch`,
  `cloudfront`, `security`, `elasticache`, `bedrock`, `task-ecs-deploy-gh`
- **General AWS** (4): `aws-sam-bootstrap`, `aws-drawio-architecture-diagrams`, `aws-cli-beast`, `aws-cost-optimization`

---

### developer-kit-ai

AI/ML capabilities including prompt engineering, RAG, and chunking strategies.

**Agents**: `prompt-engineering-expert`

**Commands**: `/devkit.prompt-optimize`

**Skills**: `prompt-engineering`, `chunking-strategy`, `rag`

---

### developer-kit-devops

DevOps and containerization expertise.

**Agents**: `github-actions-pipeline-expert`, `general-docker-expert`

---

### developer-kit-project-management

Project management and workflow commands.

**Commands**: `/devkit.write-a-minute-of-a-meeting`

---

### developer-kit-tools

Additional development tools and integrations.

**Skills**:
- `notebooklm` (Google NotebookLM integration)
- `copilot-cli` (GitHub Copilot CLI delegation with multi-model support)
- `gemini` (Gemini CLI delegation for large-context analysis)
- `codex` (OpenAI Codex CLI delegation for complex development tasks using GPT-5.3-codex models)
- `sonarqube-mcp` (SonarQube MCP integration with plugin-provided MCP server configuration)

**MCP Servers**: `sonarqube-mcp` via `.mcp.json`

---

### github-spec-kit

GitHub specification integration and verification.

**Commands**: `/speckit.check-integration`, `/speckit.optimize`, `/speckit.verify`

---

## Key Features

- **Modular** — Install only the plugins you need for your tech stack
- **Specialized** — Domain-specific agents for code review, testing, AI development, and full-stack development
- **Composable** — Skills stack together automatically based on task context
- **Portable** — Use across Claude.ai, Claude Code CLI, Claude Desktop, and Claude API
- **Efficient** — Skills load on-demand, consuming minimal tokens until actively used

---

## Language Support

Component counts below reflect the current plugin manifests in this repository.

| Language           | Plugin                     | Components                                  |
|--------------------|----------------------------|---------------------------------------------|
| Core               | `developer-kit-core`       | 6 Skills, 6 Agents, 25 Commands             |
| Java/Spring Boot   | `developer-kit-java`       | 52 Skills, 9 Agents, 11 Commands, 4 Rules  |
| TypeScript/Node.js | `developer-kit-typescript` | 26 Skills, 13 Agents, 3 Commands, 19 Rules |
| Python             | `developer-kit-python`     | 2 Skills, 4 Agents, 4 Rules                 |
| PHP/WordPress      | `developer-kit-php`        | 3 Skills, 5 Agents, 4 Rules                 |
| AWS CloudFormation | `developer-kit-aws`        | 19 Skills, 3 Agents                         |
| AI/ML              | `developer-kit-ai`         | 3 Skills, 1 Agent, 1 Command                |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on adding skills, agents, and commands.

---

## Security

Skills can execute code. Review all custom skills before deploying.

- Only install from trusted sources
- Review SKILL.md before enabling
- Test in non-production environments first

---

## License

See [LICENSE](LICENSE) file.

---

## Support

- **Questions?** [Open an issue](https://github.com/giuseppe-trisciuoglio/developer-kit/issues)
- **Contributions?** [Submit a PR](https://github.com/giuseppe-trisciuoglio/developer-kit/pulls)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete history.

---

**Made with care for Developers using Claude Code**
**Also works with OpenCode, Github Copilot CLI and Codex**
