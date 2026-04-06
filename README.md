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

Developer Kit is organized as a **modular marketplace** with 12 independent plugins:

```
plugins/
├── developer-kit-core/            # Core agents/commands/skills (required), LRA workflow (general-purpose)
├── developer-kit-specs/           # Specifications-driven development workflow
├── developer-kit-java/            # Java/Spring Boot/LangChain4J/AWS SDK/GraalVM Native Image
├── developer-kit-typescript/      # NestJS/React/React Native/Next.js/Drizzle/Monorepo
├── developer-kit-python/          # Python development/AWS Lambda
├── developer-kit-php/             # PHP/WordPress/AWS Lambda
├── developer-kit-aws/             # AWS CloudFormation/AWS Architecture
├── developer-kit-ai/              # Prompt Engineering/RAG/Chunking
├── developer-kit-devops/          # Docker/GitHub Actions
├── developer-kit-project-management/  # Meetings
├── developer-kit-tools/           # Additional development tools
└── github-spec-kit/               # GitHub specification integration
```

Language plugins (Java, TypeScript, Python, PHP) include **coding rules** (`rules/` directory) that auto-activate via
`globs:` path-scoped matching to enforce naming conventions, project structure, language best practices, and error
handling patterns. They also include **LSP server configurations** (`.lsp.json`) for real-time code intelligence,
diagnostics, and navigation features.

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
| `learn-analyst`              | Codebase analysis and rule discovery   |

**Skills**: `claude-md-management`, `drawio-logical-diagrams`, `github-issue-workflow`, `docs-updater`, `learn`

**Hooks**: `prevent-destructive-commands` (Python 3 PreToolUse hook for blocking dangerous Bash commands)

**Commands**: `/devkit.refactor`, `/devkit.feature-development`,
`/devkit.fix-debugging`, `/devkit.generate-document`, `/devkit.generate-changelog`, `/devkit.github.create-pr`,
`/devkit.github.review-pr`, `/devkit.lra.*` (7 LRA workflow commands), `/devkit.verify-skill`,
`/devkit.generate-security-assessment`

---

### developer-kit-specs

Specifications-driven development workflow for transforming ideas into functional specifications and executable tasks.

| Component             | Description                                                       |
|-----------------------|-------------------------------------------------------------------|
| `brainstorm`          | Full 9-phase specification creation for complex features          |
| `quick-spec`          | Lightweight 4-phase spec for bug fixes and small features         |
| `spec-quality-check`  | Interactive specification content quality assessment              |
| `spec-sync-context`   | Synchronizes technical context (Knowledge Graph, Tasks, Codebase) |
| `spec-to-tasks`       | Converts functional specifications into executable tasks          |
| `spec-sync-with-code` | Synchronizes specification with implementation state              |
| `task-manage`         | Post-generation task management (list, split, add, update)        |
| `task-implementation` | Guided single-task implementation with Knowledge Graph validation |
| `task-tdd`            | Test-Driven implementation of a specific task                     |
| `task-review`         | Verifies implemented tasks meet specifications                    |
| `code-cleanup`        | Professional code cleanup after task review approval              |
| `ralph-loop`          | Guided automation loop for spec-driven development                |

**Skills**: `knowledge-graph` (caching/validation), `ralph-loop` (automation loop), `specs-code-cleanup` (hygiene)

**Hooks**: `task-implementation-review-stop` (stop gate), `drift-guard` (spec-to-code gap monitoring)

**Note**: In specs-driven work, treat `docs/specs/` files as deliverables. If implementation or recommendations clarify or change the intended behavior, update the affected spec artifacts with `/specs:spec-sync-with-code` before concluding the workflow or chat session.

**Commands**: `/specs:brainstorm`, `/specs:quick-spec`, `/specs:spec-quality-check`, `/specs:spec-sync-context`,
`/specs:spec-to-tasks`, `/specs:spec-sync-with-code`, `/specs:task-manage`, `/specs:task-implementation`,
`/specs:task-tdd`, `/specs:task-review`, `/specs:code-cleanup`, `/specs:ralph-loop`

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
- **Integration Testing**: wiremock-standalone-docker (WireMock standalone server via Docker for integration/E2E
  testing)
- **LangChain4J**: ai-services-patterns, mcp-server-patterns, rag-implementation-patterns, spring-boot-integration,
  testing-strategies, tool-function-calling-patterns, vector-stores-configuration, qdrant
- **AWS SDK**: rds-spring-boot-integration, bedrock, core, dynamodb, kms, lambda, messaging, rds, s3, secrets-manager
- **Clean Architecture**: clean-architecture
- **GraalVM**: graalvm-native-image

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`

**LSP Servers**: `java` (jdtls), `kotlin` (kotlin-language-server), `scala` (metals)

---

### developer-kit-typescript

TypeScript/JavaScript full-stack development with NestJS, React, React Native, Next.js, Drizzle ORM, DynamoDB-Toolbox,
Zod validation, and Monorepo tools.

**Agents**: `nestjs-backend-development-expert`, `nestjs-code-review-expert`, `nestjs-database-expert`,
`nestjs-security-expert`, `nestjs-testing-expert`, `nestjs-unit-testing-expert`, `react-frontend-development-expert`,
`react-software-architect-review`, `typescript-refactor-expert`, `typescript-security-expert`,
`typescript-software-architect-review`, `typescript-documentation-expert`, `expo-react-native-development-expert`

**Commands**: `/devkit.typescript.code-review`, `/devkit.react.code-review`, `/devkit.ts.security-review`

**Skills**:

- **Backend**: `nestjs`, `nestjs-best-practices`, `clean-architecture`, `nestjs-drizzle-crud-generator`
- **Authentication**: `better-auth`
- **Frontend**: `react-patterns`, `shadcn-ui`, `tailwind-css-patterns`, `tailwind-design-system`
- **Next.js**: `nextjs-app-router`, `nextjs-authentication`, `nextjs-data-fetching`, `nextjs-performance`,
  `nextjs-deployment`
- **Database & ORM**: `drizzle-orm-patterns`, `dynamodb-toolbox-patterns`, `zod-validation-utilities`
- **Monorepo**: `nx-monorepo`, `turborepo-monorepo`
- **AWS Lambda**: `aws-lambda-typescript-integration`
- **Core**: `typescript-docs`

**Rules**: `naming-conventions`, `project-structure`, `language-best-practices`, `error-handling`,
`nestjs-architecture`, `nestjs-api-design`, `nestjs-security`, `nestjs-testing`,
`react-component-conventions`, `react-data-fetching`, `react-routing-conventions`, `tailwind-styling-conventions`,
`drizzle-orm-conventions`, `shared-dto-conventions`, `nx-monorepo-conventions`, `i18n-conventions`,
`lambda-conventions`, `server-feature-conventions`

**LSP Servers**: `typescript`/`javascript` (typescript-language-server), `eslint` (eslint-language-server), `vue` (
vue-language-server)

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

| Language           | Plugin                     | Components                                 |
|--------------------|----------------------------|--------------------------------------------|
| Core               | `developer-kit-core`       | 4 Skills, 6 Agents, 8 Commands             |
| Specs/SDD Workflow | `developer-kit-specs`      | 1 Skill, 9 Commands                        |
| Java/Spring Boot   | `developer-kit-java`       | 51 Skills, 9 Agents, 11 Commands, 4 Rules  |
| TypeScript/Node.js | `developer-kit-typescript` | 25 Skills, 13 Agents, 3 Commands, 17 Rules |
| Python             | `developer-kit-python`     | 2 Skills, 4 Agents, 4 Rules                |
| PHP/WordPress      | `developer-kit-php`        | 3 Skills, 5 Agents, 4 Rules                |
| AWS CloudFormation | `developer-kit-aws`        | 19 Skills, 3 Agents                        |
| AI/ML              | `developer-kit-ai`         | 3 Skills, 1 Agent, 1 Command               |

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
