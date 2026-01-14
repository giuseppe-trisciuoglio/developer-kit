# Developer Kit for Claude Code

> A curated collection of reusable skills and agents for automating development tasks in Claude Code — focusing on
> Java/Spring Boot patterns with extensibility to PHP, TypeScript, and Python

**Developer Kit for Claude Code** teaches Claude how to **perform development tasks in a repeatable way** across
multiple languages and frameworks. It includes specialized agents for code review, testing patterns, REST API design,
and AI integration.

**56 Total Skills** — Comprehensive coverage of Spring Boot, testing, AI integration, cloud development, AI
engineering patterns, frontend development, backend development (NestJS), and documentation generation

## 🚀 Quick Start

### Claude Code CLI

```bash
/plugin marketplace add giuseppe-trisciuoglio/developer-kit
```

### Claude Desktop

[Enable Skills in Settings](https://claude.ai/settings/capabilities)

## 🛠️ Installation & Setup

### Claude Code CLI

```bash
# Install from marketplace
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# Or install from local directory
/plugin install /path/to/developer-kit
```

### Claude Desktop

1. Go to [Settings > Capabilities](https://claude.ai/settings/capabilities)
2. Enable Skills toggle
3. Browse available skills or upload custom skills
4. Start using in conversations

## 🔌 Multi-CLI Support: Install in Other IDEs & Tools

The Developer Kit now supports installation across multiple AI-powered development environments through a unified Makefile interface.

### Quick Start with Makefile

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit-claude-code

# See all available options
make help

# Install for your specific CLI tool
make install-copilot      # For GitHub Copilot CLI
make install-opencode     # For OpenCode CLI
make install-codex        # For Codex CLI
make install              # Auto-install for all detected CLIs
```

### Supported CLI Tools

#### GitHub Copilot CLI

```bash
# Install agents for Copilot CLI
make install-copilot

# Installation creates:
# ~/.copilot/agents/          # Specialized agents for code review, testing, etc.
```

**Features:**
- **Specialized Agents**: Code review, architecture, security, testing, debugging experts
- **Usage**: `/agent` to select agents or mention in prompts
- **Integration**: Works with Copilot's native agent system

#### OpenCode CLI

```bash
# Install both agents and commands for OpenCode CLI
make install-opencode

# Installation creates:
# ~/.config/opencode/agent/     # Development agents
# ~/.config/opencode/command/  # Custom slash commands
```

**Features:**
- **Development Agents**: Full suite of specialized agents
- **Custom Commands**: From code generation to debugging and security reviews
- **Usage**: `@agent-name` for agents, `/command-name` for commands
- **Discovery**: Tab completion and command discovery

#### Codex CLI

```bash
# Install for Codex CLI
make install-codex

# Installation creates:
# ~/.codex/instructions.md    # Agent context and usage guide
# ~/.codex/prompts/           # Custom prompt commands
```

**Features:**
- **Custom Prompts**: Specialized commands for development workflows
- **Agents Documentation**: Complete agent descriptions and usage
- **Usage**: `/prompts:<name>` to invoke custom commands

### Management Commands

```bash
# Check installation status
make status

# Create backup before installing
make backup

# Remove all Developer Kit installations
make uninstall

# List available components
make list-agents      # Show all 14 agents
make list-commands    # Show all 32 commands
make list-skills      # Show all 50 skills by category
```

### Installation Safety

- **Automatic Backups**: Creates timestamped backups before installation
- **Conflict Resolution**: Preserves existing configurations
- **Rollback Support**: Easy uninstall to restore previous state
- **Version Tracking**: Tracks what's installed from this kit

## 🎯 Local Project Installation

Install skills, agents, and commands directly into your local project for team-based development:

### Interactive Claude Code Installation

```bash
# Clone the repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git
cd developer-kit-claude-code

# Run interactive installer for Claude Code
make install-claude
```

**Interactive Features:**
- ✅ **Environment Validation**: Confirms Claude Code usage
- 🎯 **Category Selection**: Choose specific skill categories
- 🔧 **Custom Selection**: Pick specific agents and commands
- 🛡️ **Conflict Handling**: Decide how to handle existing files
- 📊 **Progress Tracking**: Real-time installation progress
- 📋 **Summary Report**: Complete installation summary

#### Example Installation Flow

```bash
$ make install-claude

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      Claude Code Interactive Developer Kit Installer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ This installer is designed for Claude Code only.

Are you installing for Claude Code? (y/N): y

Step 1: Target Project
Enter the project path (absolute or relative): ~/my-spring-project

Step 2: Select Skill Categories
Available skill categories:
  1) AWS Java Skills (10 skills)
  2) AI Skills (3 skills)
  3) JUnit Test Skills (15 skills)
  4) LangChain4j Skills (8 skills)
  5) Spring Boot Skills (13 skills)
  6) Spring AI Skills (1 skill)
  7) All Skills
  8) None (skip skills)

Select categories (comma-separated, e.g., 1,4,5): 4,5

Step 3: Select Agents
  1) All Agents (14 available)
  2) Select specific agents
  3) None (skip agents)
Choose option [1-3]: 2

Available agents:
   1) java-documentation-specialist
   2) java-refactor-expert
   3) java-security-expert
   ...
Select agents (comma-separated numbers, or type 'all'): 1,3

Step 4: Select Commands
  1) All Commands (32 available)
  2) Select specific commands
  3) None (skip commands)
Choose option [1-3]: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Installation...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installing Skills...
  Category: LangChain4j Skills
    ✓ Installed: langchain4j-ai-services-patterns
    ✓ Installed: langchain4j-mcp-server-patterns
  Category: Spring Boot Skills
    ✓ Installed: spring-boot-actuator
    ✓ Installed: spring-boot-cache
    ...

Installing Selected Agents...
  ✓ Installed: java-documentation-specialist.md
  ✓ Installed: java-security-expert.md

Installing All Commands...
  ✓ Installed: devkit.java.code-review.md
  ✓ Installed: devkit.java.write-unit-tests.md
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Installation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target directory: /Users/you/my-spring-project/.claude/
Files installed:  52
Files skipped:    0

Next Steps:
  1. Navigate to your project: cd /Users/you/my-spring-project
  2. Start Claude Code in the project directory
  3. Your skills, agents, and commands are now available!
```

### What Gets Installed

```
my-project/
├── .claude/
│   ├── skills/                      # Auto-discovered skills
│   │   ├── langchain4j-ai-services-patterns/
│   │   ├── spring-boot-actuator/
│   │   └── ... (selected skills)
│   ├── agents/                      # @agent-name access
│   │   ├── java-documentation-specialist.md
│   │   ├── java-security-expert.md
│   │   └── ... (selected agents)
│   └── commands/                    # /command-name access
│       ├── devkit.java.code-review.md
│       ├── devkit.java.write-unit-tests.md
│       └── ... (selected commands)
```

### Team-Based Development

**For Teams Sharing Projects:**

1. **Install Once**: Use `make install-claude` in the project root
2. **Git Integration**: All `.claude/` files are version-controlled
3. **Team Consistency**: Everyone gets the same tools and patterns
4. **Custom Skills**: Create project-specific skills shared with team

**Benefits:**
- 🔄 **Consistent Tooling**: Team uses same agents, skills, commands
- 📚 **Project Context**: Skills understand your specific project structure
- 🎯 **Domain-Specific**: Tailored to your business domain and patterns
- 🚀 **Quick Onboarding**: New team members get all tools immediately

## 📚 Available Skills

### Spring Boot Skills

| Skill                                                                                                  | Purpose                              | Key Topics                                                           |
|--------------------------------------------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------|
| **[spring-boot-actuator](skills/spring-boot/spring-boot-actuator/SKILL.md)**                           | Production monitoring and metrics    | Health checks, custom endpoints, metrics, startup tracking           |
| **[spring-boot-dependency-injection](skills/spring-boot/spring-boot-dependency-injection/SKILL.md)**   | Constructor injection best practices | DI patterns, testing strategies, anti-patterns                       |
| **[spring-boot-crud-patterns](skills/spring-boot/spring-boot-crud-patterns/SKILL.md)**                 | REST CRUD API design with DDD        | Feature-based architecture, CRUD generator, Lombok, Spring Data      |
| **[spring-boot-event-driven-patterns](skills/spring-boot/spring-boot-event-driven-patterns/SKILL.md)** | Event-driven architecture            | Domain events, Kafka, Spring Cloud Stream, transactional patterns    |
| **[spring-boot-rest-api-standards](skills/spring-boot/spring-boot-rest-api-standards/SKILL.md)**       | REST API design standards            | HTTP semantics, error handling, pagination, security headers         |
| **[spring-boot-test-patterns](skills/spring-boot/spring-boot-test-patterns/SKILL.md)**                 | Integration testing patterns         | Testcontainers, Spring slice tests, database strategies              |
| **[spring-boot-cache](skills/spring-boot/spring-boot-cache/SKILL.md)**                                 | Spring Boot caching patterns         | Cache configuration, eviction strategies, distributed caching        |
| **[spring-boot-saga-pattern](skills/spring-boot/spring-boot-saga-pattern/SKILL.md)**                   | Distributed transaction management   | Saga pattern, choreography, orchestration, compensating transactions |
| **[spring-boot-resilience4j](skills/spring-boot/spring-boot-resilience4j/SKILL.md)**                   | Fault tolerance patterns             | Circuit breaker, retry, rate limiting, bulkhead patterns             |
| **[spring-boot-security-jwt](skills/spring-boot/spring-boot-security-jwt/SKILL.md)**                   | JWT authentication & authorization   | Bearer tokens, OAuth2/OIDC, RBAC, permission-based access control    |
| **[spring-data-jpa](skills/spring-boot/spring-data-jpa/SKILL.md)**                                     | Spring Data JPA best practices       | Query methods, custom repositories, performance optimization         |
| **[spring-data-neo4j](skills/spring-boot/spring-data-neo4j/SKILL.md)**                                 | Neo4j graph database integration     | Graph modeling, Cypher queries, relationships, reactive mode         |
| **[spring-boot-openapi-documentation](skills/spring-boot/spring-boot-openapi-documentation/SKILL.md)** | OpenAPI/Swagger documentation        | API documentation, schema generation, SpringDoc                      |

### JUnit Testing Skills

| Skill                                                                                               | Purpose                          | Key Topics                                        |
|-----------------------------------------------------------------------------------------------------|----------------------------------|---------------------------------------------------|
| **[unit-test-service-layer](skills/junit-test/unit-test-service-layer/SKILL.md)**                   | Service layer unit testing       | Mocking, assertions, test organization            |
| **[unit-test-controller-layer](skills/junit-test/unit-test-controller-layer/SKILL.md)**             | Controller layer testing         | Mock MVC, request/response handling, status codes |
| **[unit-test-parameterized](skills/junit-test/unit-test-parameterized/SKILL.md)**                   | Parameterized tests              | JUnit 5 @ParameterizedTest, multiple scenarios    |
| **[unit-test-exception-handler](skills/junit-test/unit-test-exception-handler/SKILL.md)**           | Exception handling tests         | Custom exceptions, error scenarios                |
| **[unit-test-bean-validation](skills/junit-test/unit-test-bean-validation/SKILL.md)**               | Jakarta Validation testing       | Bean validation constraints, custom validators    |
| **[unit-test-security-authorization](skills/junit-test/unit-test-security-authorization/SKILL.md)** | Spring Security testing          | @WithMockUser, authorization checks, roles        |
| **[unit-test-application-events](skills/junit-test/unit-test-application-events/SKILL.md)**         | Application event testing        | Event publishing, listeners, @EventListener       |
| **[unit-test-scheduled-async](skills/junit-test/unit-test-scheduled-async/SKILL.md)**               | Async and scheduled task testing | @Async, @Scheduled, TestScheduler                 |
| **[unit-test-json-serialization](skills/junit-test/unit-test-json-serialization/SKILL.md)**         | JSON serialization testing       | Jackson, @JsonTest, custom serializers            |
| **[unit-test-config-properties](skills/junit-test/unit-test-config-properties/SKILL.md)**           | Configuration properties testing | @ConfigurationProperties, binding validation      |
| **[unit-test-mapper-converter](skills/junit-test/unit-test-mapper-converter/SKILL.md)**             | Mapper and converter testing     | Entity to DTO, custom converters                  |
| **[unit-test-caching](skills/junit-test/unit-test-caching/SKILL.md)**                               | Caching layer testing            | @Cacheable, cache eviction, hit/miss scenarios    |
| **[unit-test-boundary-conditions](skills/junit-test/unit-test-boundary-conditions/SKILL.md)**       | Boundary condition testing       | Edge cases, limits, null values                   |
| **[unit-test-utility-methods](skills/junit-test/unit-test-utility-methods/SKILL.md)**               | Utility method testing           | Static methods, helpers, common functions         |
| **[unit-test-wiremock-rest-api](skills/junit-test/unit-test-wiremock-rest-api/SKILL.md)**           | REST API mocking with WireMock   | HTTP stubs, response matching, status codes       |

### LangChain4J Skills

| Skill                                                                                                                    | Purpose                            | Key Topics                                              |
|--------------------------------------------------------------------------------------------------------------------------|------------------------------------|---------------------------------------------------------|
| **[langchain4j-spring-boot-integration](skills/langchain4j/langchain4j-spring-boot-integration/SKILL.md)**               | LangChain4J with Spring Boot       | Configuration, bean management, integration patterns    |
| **[langchain4j-rag-implementation-patterns](skills/langchain4j/langchain4j-rag-implementation-patterns/SKILL.md)**       | Retrieval-Augmented Generation     | Vector stores, retrievers, prompt chaining              |
| **[langchain4j-ai-services-patterns](skills/langchain4j/langchain4j-ai-services-patterns/SKILL.md)**                     | AI service design                  | Service patterns, model configuration, error handling   |
| **[langchain4j-mcp-server-patterns](skills/langchain4j/langchain4j-mcp-server-patterns/SKILL.md)**                       | Model Context Protocol servers     | MCP integration, tool exposure, data access             |
| **[langchain4j-tool-function-calling-patterns](skills/langchain4j/langchain4j-tool-function-calling-patterns/SKILL.md)** | Tool and function calling          | Agent patterns, tool definition, function orchestration |
| **[langchain4j-testing-strategies](skills/langchain4j/langchain4j-testing-strategies/SKILL.md)**                         | Testing LangChain4J applications   | Mock models, test containers, integration tests         |
| **[langchain4j-vector-stores-configuration](skills/langchain4j/langchain4j-vector-stores-configuration/SKILL.md)**       | Vector store configuration         | Embeddings, similarity search, provider setup           |
| **[qdrant-java-development](skills/langchain4j/qdrant/SKILL.md)**                                                        | Qdrant vector database integration | Java, Spring Boot, Langchain4j, RAG, vector search      |

### Spring AI Skills

| Skill                                                                                  | Purpose                        | Key Topics                                    |
|----------------------------------------------------------------------------------------|--------------------------------|-----------------------------------------------|
| **[spring-ai-mcp-server-patterns](skills/spring-ai/spring-ai-mcp-server-patterns/SKILL.md)** | Model Context Protocol servers | MCP integration, Spring AI, tool exposure     |

### AWS Java Skills

| Skill                                                                                           | Purpose                                  | Key Topics                                                    |
|-------------------------------------------------------------------------------------------------|------------------------------------------|---------------------------------------------------------------|
| **[aws-rds-spring-boot-integration](skills/aws-java/aws-rds-spring-boot-integration/SKILL.md)** | Aurora RDS configuration with Spring JPA | Cluster setup, connection pooling, read/write split, failover |
| **[aws-sdk-java-v2-core](skills/aws-java/aws-sdk-java-v2-core/SKILL.md)**                       | AWS SDK v2 core patterns                 | Client configuration, credential management, async operations |
| **[aws-sdk-java-v2-s3](skills/aws-java/aws-sdk-java-v2-s3/SKILL.md)**                           | S3 operations with SDK v2                | Bucket operations, object upload/download, presigned URLs     |
| **[aws-sdk-java-v2-dynamodb](skills/aws-java/aws-sdk-java-v2-dynamodb/SKILL.md)**               | DynamoDB operations                      | Table operations, queries, scans, transactions                |
| **[aws-sdk-java-v2-lambda](skills/aws-java/aws-sdk-java-v2-lambda/SKILL.md)**                   | Lambda function development              | Handler patterns, event processing, custom runtimes           |
| **[aws-sdk-java-v2-secrets-manager](skills/aws-java/aws-sdk-java-v2-secrets-manager/SKILL.md)** | Secrets Manager integration              | Secret retrieval, rotation, caching                           |
| **[aws-sdk-java-v2-kms](skills/aws-java/aws-sdk-java-v2-kms/SKILL.md)**                         | KMS encryption operations                | Key management, encryption/decryption, envelope encryption    |
| **[aws-sdk-java-v2-messaging](skills/aws-java/aws-sdk-java-v2-messaging/SKILL.md)**             | SQS/SNS messaging patterns               | Queue operations, topic publishing, message processing        |
| **[aws-sdk-java-v2-rds](skills/aws-java/aws-sdk-java-v2-rds/SKILL.md)**                         | RDS management operations                | Instance management, snapshots, parameter groups              |
| **[aws-sdk-java-v2-bedrock](skills/aws-java/aws-sdk-java-v2-bedrock/SKILL.md)**                 | AWS Bedrock AI integration               | Model invocation, streaming, guardrails                       |

### AI Engineering Skills

| Skill                                                           | Purpose                                 | Key Topics                                               |
|-----------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------|
| **[chunking-strategy](skills/ai/chunking-strategy/SKILL.md)**   | Document chunking for AI systems        | Text splitting strategies, semantic chunking, RAG prep   |
| **[prompt-engineering](skills/ai/prompt-engineering/SKILL.md)** | Advanced prompt design patterns         | CoT, few-shot, system prompts, optimization frameworks   |
| **[rag](skills/ai/rag/SKILL.md)**                               | Retrieval-Augmented Generation patterns | Vector search, document processing, embedding strategies |

### Frontend Development Skills

| Skill                                                                          | Purpose                             | Key Topics                                                    |
|--------------------------------------------------------------------------------|-------------------------------------|---------------------------------------------------------------|
| **[react](skills/react/SKILL.md)**                                              | React development patterns          | Components, hooks, state management, performance optimization |
| **[shadcn-ui](skills/shadcn-ui/SKILL.md)**                                      | Modern UI component library         | Component design, theming, accessibility, Tailwind CSS       |
| **[tailwind-css](skills/tailwind-css/SKILL.md)**                                | Utility-first CSS framework         | Responsive design, utility classes, custom components         |
| **[typescript-docs](skills/typescript-docs/SKILL.md)**                         | TypeScript documentation patterns   | Type definitions, API docs, JSDoc, TSDoc                     |

### Backend Development Skills

| Skill                                                             | Purpose                       | Key Topics                                                    |
|-------------------------------------------------------------------|-------------------------------|---------------------------------------------------------------|
| **[nestjs](skills/nestjs/SKILL.md)**                             | NestJS framework patterns     | Controllers, providers, modules, authentication, Drizzle ORM  |

## 🤖 Available Agents

| Agent                                                                                          | Specialization                 | Best For                                                            |
|------------------------------------------------------------------------------------------------|--------------------------------|---------------------------------------------------------------------|
| **[spring-boot-code-review-specialist](agents/spring-boot-code-review-specialist.md)**         | Spring Boot code review        | Architecture, patterns, security review                             |
| **[spring-boot-code-review-expert](agents/spring-boot-code-review-expert.md)**                 | Expert Spring Boot code review | Advanced code analysis, security, performance review                |
| **[spring-boot-backend-development-expert](agents/spring-boot-backend-development-expert.md)** | Backend development            | Implementation, testing, optimization                               |
| **[langchain4j-ai-development-expert](agents/langchain4j-ai-development-expert.md)**           | AI integration                 | LangChain4J implementation, RAG, agents                             |
| **[spring-boot-unit-testing-expert](agents/spring-boot-unit-testing-expert.md)**               | Unit testing                   | Test patterns, Mockito, test organization                           |
| **[java-refactor-expert](agents/java-refactor-expert.md)**                                     | Java Refactoring               | Complex class refactoring, DDD alignment, legacy code modernization |
| **[java-software-architect-review](agents/java-software-architect-review.md)**                 | Software architecture review   | High-level architecture, design patterns, scalability               |
| **[java-security-expert](agents/java-security-expert.md)**                                     | Java security analysis         | Security vulnerabilities, OWASP, secure coding practices            |
| **[java-documentation-specialist](agents/java-documentation-specialist.md)**                   | Java project documentation     | API docs, architecture guides, technical documentation generation   |
| **[java-tutorial-engineer](agents/java-tutorial-engineer.md)**                                 | Java/Spring Boot tutorials     | Educational content, hands-on learning, step-by-step guides         |
| **[prompt-engineering-expert](agents/prompt-engineering-expert.md)**                           | Prompt engineering             | LLM prompt optimization, CoT, few-shot patterns                     |
| **[general-debugger](agents/general-debugger.md)**                                             | Debugging and root cause analysis| Error troubleshooting, test failures, performance issues             |
| **[react-frontend-development-expert](agents/react-frontend-development-expert.md)**           | React frontend development     | Component architecture, hooks, state management, performance       |
| **[expo-react-native-development-expert](agents/expo-react-native-development-expert.md)** | Expo & React Native mobile development | Expo SDK 54, React Native 0.81.5, TypeScript, navigation, performance |
| **[nestjs-backend-development-expert](agents/nestjs-backend-development-expert.md)**           | NestJS backend development     | API development, microservices, authentication, testing             |
| **[nestjs-code-review-expert](agents/nestjs-code-review-expert.md)**                           | NestJS code review             | Architecture review, security, performance, best practices         |
| **[nestjs-unit-testing-expert](agents/nestjs-unit-testing-expert.md)**                         | NestJS testing                 | Unit tests, integration tests, e2e testing with Jest                |
| **[nestjs-database-expert](agents/nestjs-database-expert.md)**                                 | NestJS database patterns       | TypeORM, Drizzle ORM, database design, migrations                  |
| **[nestjs-security-expert](agents/nestjs-security-expert.md)**                                 | NestJS security analysis       | Authentication, authorization, JWT, OAuth2, security best practices |
| **[typescript-documentation-expert](agents/typescript-documentation-expert.md)**               | TypeScript documentation        | API documentation, type definitions, code examples                  |
| **[typescript-refactor-expert](agents/typescript-refactor-expert.md)**                         | TypeScript refactoring         | Modern patterns, performance optimization, code cleanup            |
| **[typescript-security-expert](agents/typescript-security-expert.md)**                         | TypeScript security analysis   | OWASP Top 10, npm audit, secure coding practices                    |
| **[typescript-software-architect-review](agents/typescript-software-architect-review.md)**     | TypeScript architecture review | Design patterns, scalability, module organization                  |
| **[react-software-architect-review](agents/react-software-architect-review.md)**               | React architecture review      | Component patterns, state management, performance, accessibility   |
| **[aws-architecture-review-expert](agents/aws-architecture-review-expert.md)**                 | AWS architecture & CloudFormation review | Well-Architected Framework, security, cost optimization, IaC quality |
| **[aws-cloudformation-devops-expert](agents/aws-cloudformation-devops-expert.md)**             | AWS DevOps & CloudFormation    | Nested stacks, cross-stack refs, custom resources, CI/CD integration |
| **[aws-solution-architect-expert](agents/aws-solution-architect-expert.md)**                   | AWS Solution Architecture      | Multi-region deployments, high availability, cost optimization, security |
| **[general-refactor-expert](agents/general-refactor-expert.md)**                               | Code refactoring               | Code quality, maintainability, SOLID patterns, best practices       |
| **[general-code-explorer](agents/general-code-explorer.md)**                                   | Code exploration and analysis  | Understanding codebases, tracing implementations                    |
| **[general-code-reviewer](agents/general-code-reviewer.md)**                                   | General code review            | Code quality, best practices, maintainability                      |
| **[general-software-architect](agents/general-software-architect.md)**                         | Software architecture design   | System design, patterns, technology selection                      |

## ✨ Key Features

**Specialized** — Domain-specific agents for code review, testing, AI development, and full-stack development covering Java/Spring Boot, TypeScript/Node.js, React, NestJS, with specialized security and database expertise

**Composable** — Skills stack together automatically. Claude identifies which skills are needed and uses them in
combination

**Portable** — Use the same skills across Claude.ai, Claude Code CLI, Claude Desktop, and the Claude API

**Efficient** — Skills load on-demand, consuming minimal tokens until they're actively used

## 🎯 Use Cases

**Code Review & Architecture** — Automated Spring Boot code reviews, architecture validation, security analysis

**REST API Design** — Standardized API development with proper HTTP semantics, error handling, pagination

**Testing Strategies** — Unit test patterns, integration testing with Testcontainers, test organization

**AI Integration** — LangChain4J implementation guidance, RAG patterns, agent development, MCP server creation

**Event-Driven Architecture** — Domain events, event sourcing patterns, Kafka integration, transactional consistency

**AWS Cloud Development** — RDS Aurora configuration, S3 operations, Lambda functions, DynamoDB, Secrets Manager, KMS
encryption

## 📖 How to Use

### For Individual Contributors

1. Install the skill/agent in Claude Code
2. Describe your development task
3. Claude will automatically load relevant skills and provide guidance

### For Teams

1. Clone or fork this repository
2. Customize skills for your team's standards
3. Deploy via `/plugin install /path/to/developer-kit-claude-code`
4. Share the plugin marketplace link with your team

## 🔧 Custom Commands

This kit includes specialized commands for workflow orchestration, verification, skill validation, and Java development
automation:

### Project Workflow Commands

| Command                                   | Purpose                                    | Use Case                                                                                 |
|-------------------------------------------|--------------------------------------------|------------------------------------------------------------------------------------------|
| **`/devkit.generate-changelog`**          | Generate project changelog                 | Create and maintain CHANGELOG.md for any project type with Git integration               |
| **`/devkit.write-a-minute-of-a-meeting`** | Generate meeting minutes from transcripts  | Create professional meeting summaries and action items from meeting transcripts or notes |
| **`/devkit.prompt-optimize`**             | Optimize prompts for better AI performance | Enhance prompt engineering for improved Claude responses and task execution              |

### GitHub Commands

| Command                        | Purpose                        | Use Case                                                                                    |
|--------------------------------|--------------------------------|---------------------------------------------------------------------------------------------|
| **`/devkit.github.create-pr`** | Create GitHub pull request     | Create branch, commit changes, and submit PR with automated description and commit messages |
| **`/devkit.github.review-pr`** | Comprehensive GitHub PR review | Perform code quality, security, performance, architecture, and testing review of a PR       |

### Security Commands

| Command                                    | Purpose                               | Use Case                                                                                          |
|--------------------------------------------|---------------------------------------|---------------------------------------------------------------------------------------------------|
| **`/devkit.java.security-review`**         | Java enterprise security audit        | Comprehensive security review for Spring Boot and Jakarta EE applications (OWASP, CVEs, configs)  |
| **`/devkit.ts.security-review`**           | TypeScript/Node.js security audit     | Security review for TypeScript applications (Next.js, NestJS, Express) with OWASP Top 10 analysis |
| **`/devkit.generate-security-assessment`** | Generate security assessment document | Create comprehensive security assessment documentation after security audits (English by default) |

### GitHub Spec Kit Commands

| Command                          | Purpose                                        | Use Case                                                                             |
|----------------------------------|------------------------------------------------|--------------------------------------------------------------------------------------|
| **`/speckit.check-integration`** | Verify task integration with existing codebase | Run AFTER `/speckit.tasks` to detect duplication and integration opportunities       |
| **`/speckit.optimize`**          | Optimize execution plan for parallelization    | Run AFTER check-integration to plan subagent delegation and resource allocation      |
| **`/speckit.verify`**            | Comprehensive implementation verification      | Run AFTER `/speckit.implement` to validate all requirements, tests, and code quality |

### Java Development Commands

| Command                                    | Purpose                                       | Use Case                                                                                            |
|--------------------------------------------|-----------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **`/devkit.java.generate-crud`**           | Generate CRUD implementation for domain class | Create complete REST API with controllers, services, DTOs using spring-boot-crud-patterns           |
| **`/devkit.java.generate-docs`**           | Generate Java project documentation           | Create comprehensive API docs, architecture guides, Javadoc, and technical documentation            |
| **`/devkit.java.write-unit-tests`**        | Generate comprehensive JUnit 5 unit tests     | Create unit tests with Mockito, AssertJ for Java classes                                            |
| **`/devkit.java.write-integration-tests`** | Generate Spring Boot integration tests        | Create Testcontainers-based tests for complete workflow testing                                     |
| **`/devkit.java.code-review`**             | Perform comprehensive Java code review        | Review code quality, architecture, security, and performance                                        |
| **`/devkit.java.security-review`**         | Security-focused code review                  | Identify vulnerabilities, OWASP compliance, secure coding practices                                 |
| **`/devkit.java.architect-review`**        | High-level architecture review                | Validate design patterns, scalability, and architectural decisions                                  |
| **`/devkit.java.refactor-class`**          | Intelligent refactoring assistant             | Refactor complex Java classes with Clean Architecture, DDD patterns, and Spring Boot best practices |
| **`/devkit.generate-refactoring-tasks`**   | Generate step-by-step refactoring plan        | Create detailed, actionable refactoring tasks for complex Java classes                              |
| **`/devkit.java.dependency-audit`**        | Comprehensive dependency audit                | Scan vulnerabilities, verify licenses, and get update recommendations                               |
| **`/devkit.java.upgrade-dependencies`**    | Safe dependency upgrade strategies            | Upgrade dependencies with compatibility testing and rollback procedures                             |

### Project Workflow Commands

| Command                                   | Purpose                                   | Use Case                                                                                 |
|-------------------------------------------|-------------------------------------------|------------------------------------------------------------------------------------------|
| **`/devkit.generate-changelog`**          | Generate project changelog                | Create and maintain CHANGELOG.md for any project type with multi-language support        |
| **`/devkit.write-a-minute-of-a-meeting`** | Generate meeting minutes from transcripts | Create professional meeting summaries and action items from meeting transcripts or notes |
| **`/devkit.prompt-optimize`**             | Optimize prompts for AI performance       | Enhance prompt engineering and save optimized prompt to `optimized-prompt.md`            |

### Skill Development Commands

| Command                    | Purpose                                 | Use Case                                                                  |
|----------------------------|-----------------------------------------|---------------------------------------------------------------------------|
| **`/devkit.verify-skill`** | Validate skill against DevKit standards | Verify a skill's compliance with requirements, format, and best practices |

### Long-Running Agent (LRA) Commands

Commands for managing complex projects that span multiple context windows, based
on [Anthropic's research on long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

| Command                         | Purpose                       | Use Case                                                                           |
|---------------------------------|-------------------------------|------------------------------------------------------------------------------------|
| **`/devkit.lra.init`**          | Initialize LRA environment    | Set up feature list, progress tracking, and init script for multi-session projects |
| **`/devkit.lra.start-session`** | Start a new coding session    | Read progress, check health, select next feature at the beginning of each session  |
| **`/devkit.lra.add-feature`**   | Add feature to the list       | Add new requirements discovered during development                                 |
| **`/devkit.lra.mark-feature`**  | Mark feature as passed/failed | Update feature status after implementation and testing                             |
| **`/devkit.lra.checkpoint`**    | Create session checkpoint     | Commit changes, update progress log, ensure clean state at session end             |
| **`/devkit.lra.status`**        | View project status           | Display progress metrics, priorities, and recent activity                          |
| **`/devkit.lra.recover`**       | Recover from broken state     | Diagnose issues, revert if needed, restore working state                           |

**LRA Workflow:**

```
/devkit.lra.init [project-description]     ← First time setup
    ↓
/devkit.lra.start-session                  ← Start of every session
    ↓
... implement ONE feature ...
    ↓
/devkit.lra.mark-feature [id] passed       ← After testing
    ↓
/devkit.lra.checkpoint [summary]           ← End of every session
```

📖 **[Complete LRA Workflow Guide](docs/guide-lra-workflow.md)** — Detailed documentation with examples and best
practices.

### GitHub Spec Kit Workflow

```
/speckit.tasks
    ↓
/speckit.check-integration    ← Detect existing code & integration opportunities
    ↓
/speckit.optimize             ← Plan parallelization & subagent assignment
    ↓
/speckit.implement            ← Execute with optimization
    ↓
/speckit.verify               ← Verify completeness & quality
```

### Spec Kit Command Details

**`/speckit.check-integration`**

- Analyzes tasks.md for codebase integration opportunities
- Detects duplication risks and existing implementations
- Verifies architectural alignment
- **Output**: Integration analysis report (READ-ONLY)
- **Timing**: After task generation, before optimization

**`/speckit.optimize`**

- Builds dependency graph and identifies parallelization opportunities
- Allocates tasks to specialized subagents
- Generates phased execution plan with validation checkpoints
- **Output**: Optimization report with phase execution matrix (READ-ONLY)
- **Timing**: After integration check, before implementation

**`/speckit.verify`**

- Validates all tasks completed
- Confirms requirements coverage
- Runs test suites and checks coverage metrics
- Audits code quality, security, and performance
- Generates verification-report.md
- **Output**: verification-report.md (PASS/FAIL)
- **Timing**: After implementation execution

### Developer Kit Command Details

**`/devkit.verify-skill`**

- Validates skill compliance with DevKit standards and official Skills documentation
- Checks SKILL.md frontmatter (name, description, allowed-tools, etc.)
- Verifies file structure and syntax (no YAML errors, valid paths)
- Validates content quality (clear triggers, instructions, examples)
- Confirms all referenced files exist in skill directory
- **Usage**: `/devkit.verify-skill skill-name`
- **Output**: Comprehensive validation report with PASS/FAIL status
- **Best for**: Skill authors before submitting PRs or publishing

**`/devkit.java.refactor-class`**

- Intelligent refactoring assistant for complex Java classes
- Applies Clean Architecture, DDD patterns, and Spring Boot best practices
- Supports multiple refactoring scopes: cleanup, architecture, performance, security, testing, comprehensive
- Includes safety checks, backup strategies, and incremental refactoring process
- **Usage**: `/devkit.java.refactor-class [class-file-path] [refactoring-scope] [options]`
- **Scopes**: `cleanup`, `architecture`, `performance`, `security`, `testing`, `comprehensive`
- **Options**: `dry-run`, `backup`, `validate-only`
- **Output**: Refactored code with detailed summary of changes and quality metrics
- **Best for**: Improving code quality, maintainability, and architectural alignment

## 🌍 Language Roadmap

- **✅ Java/Spring Boot** — Comprehensive patterns and agents
- **✅ TypeScript/Node.js** — React, NestJS, Express patterns, modern frontend development
- **📋 Python** — Django, FastAPI patterns (planned)
- **📋 PHP** — Laravel, Symfony patterns (planned)

## 🤝 Contributing

### Adding a New Skill

1. Create `skills/<domain>/<skill-name>/SKILL.md`
    - For Spring Boot: `skills/spring-boot/spring-boot-*/SKILL.md`
    - For JUnit Testing: `skills/junit-test/unit-test-*/SKILL.md`
    - For LangChain4J: `skills/langchain4j/langchain4j-*/SKILL.md`
    - For AWS Java: `skills/aws-java/aws-*/SKILL.md`
2. Include YAML frontmatter (name, description, language)
3. Add practical examples and best practices
4. Document dependencies and commands
5. Add supporting files (examples.md, references.md) if needed
6. Update marketplace.json with new skill path
7. Submit a PR with description and examples

### Adding a New Domain

1. Create `skills/<new-domain>/` directory
2. Add domain-specific skills following the pattern
3. Create corresponding agent if needed
4. Follow existing structure for consistency
5. Update README.md with new domain section
6. Update marketplace.json with new paths

See [CONTRIBUTING guidelines](CONTRIBUTING.md) for detailed instructions.

## 🔒 Security & Best Practices

⚠️ **Important**: Skills can execute code in Claude's environment. Review all custom skills before deploying.

**Best Practices**

- Only install skills from trusted sources
- Review SKILL.md and all scripts before enabling
- Keep skills version-controlled with git
- Audit regularly for updates and changes
- Test in non-production environments first

## 📘 Complete Guides

Comprehensive documentation for all Developer Kit components:

### Skills Guides

- **[Spring Boot Skills Guide](docs/guide-skills-spring-boot.md)** - Complete guide to Spring Boot patterns including
  dependency injection, actuator, caching, data persistence, REST APIs, resilience patterns, and testing strategies
- **[JUnit Testing Skills Guide](docs/guide-skills-junit-test.md)** - Comprehensive testing patterns for controller,
  service, data, external integrations, infrastructure, and advanced testing scenarios
- **[LangChain4j Skills Guide](docs/guide-skills-langchain4j.md)** - Building AI-powered applications with core
  integration, AI services, RAG implementation, vector stores, and MCP server patterns
- **[AWS Java SDK Skills Guide](docs/guide-skills-aws-java.md)** - Cloud development with AWS services including core
  SDK setup, storage (S3), databases (DynamoDB, RDS), compute (Lambda), messaging (SQS/SNS), and security services
- **[Frontend Skills Guide](docs/guide-skills-frontend.md)** - Best practices and reusable patterns for modern frontend development (React, Vue, Angular, testing, performance, accessibility)
- **[NestJS Skills Guide](docs/guide-skills-nestjs.md)** - Comprehensive NestJS framework patterns including modules, controllers, providers, authentication, security, database integration with Drizzle ORM, and testing strategies

### Component Guides

- **[Agents Guide](docs/guide-agents.md)** - Complete documentation for specialized agents including Java development,
  testing & quality, AI & LangChain4j, documentation, and engineering agents
- **[Commands Guide](docs/guide-commands.md)** - Comprehensive command reference for Java/Spring Boot development,
  testing, DevKit management, and utility commands with practical workflows
- **[LRA Workflow Guide](docs/guide-lra-workflow.md)** - Long-Running Agent workflow for multi-session projects based on
  Anthropic's research on effective agent harnesses

## 📚 Resources

### Official Documentation

- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills) — Claude support article
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) — Setup guide
- [Claude Developer Platform](https://docs.claude.com/) — Official docs
- [Skills API Documentation](https://docs.claude.com/en/api/skills) — API reference

### Related Projects

- [anthropics/skills](https://github.com/anthropics/skills) — Official Anthropic skills repository
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) — Community skills collection
- [obra/superpowers](https://github.com/obra/superpowers) — Battle-tested skills library

## 📝 License

This project is licensed under the [LICENSE](LICENSE) file in the repository root. See that file for details.

## 📞 Support

- **Questions?** Open an [issue](https://github.com/giuseppe-trisciuoglio/developer-kit/issues)
- **Contributions?** Submit a [pull request](https://github.com/giuseppe-trisciuoglio/developer-kit/pulls)
- **Integration proposals?** Create a discussion or reach out

## 📅 Changelog

For a complete history of changes, please see the dedicated [CHANGELOG.md](CHANGELOG.md) file.

Recent highlights:

- **v1.22.0**:
  - New AWS Cloud Architects agents (4 new specialized agents):
    - `aws-architecture-review-expert`: AWS architecture and CloudFormation reviewer with Well-Architected Framework compliance
    - `aws-cloudformation-devops-expert`: CloudFormation templates and Infrastructure as Code (IaC) specialist
    - `aws-solution-architect-expert`: AWS Solution Architect for scalable cloud architectures and enterprise-grade solutions
    - `general-refactor-expert`: Code refactoring specialist applying clean code principles and SOLID patterns
- **v1.20.0**:
  - New `react-software-architect-review` agent for React frontend architecture reviews
  - Specialized in React 19, component design patterns, state management strategies, and performance optimization
  - Updated workflow commands (`/devkit.feature-development`, `/devkit.fix-debugging`, `/devkit.refactor`) to use new React architect agent
- **v1.18.0**:
  - New `expo-react-native-development-expert` agent for cross-platform mobile development with Expo SDK 54, React Native 0.81.5, and TypeScript
  - Expert mobile app development patterns including navigation, performance optimization, testing with Jest, and Expo deployment workflows
- **v1.17.1**:
  - Fixed TypeScript/React support in `/devkit.feature-development` and `/devkit.fix-debugging` commands
  - Improved language detection for frontend development tasks
- **v1.17.0**:
  - **New Frontend Development Skills**: Added 4 comprehensive skills for modern frontend development
    - **react**: React development patterns, hooks, state management, performance optimization
    - **shadcn-ui**: Modern UI component library with Radix UI primitives and Tailwind CSS
    - **tailwind-css**: Utility-first CSS framework for rapid UI development
    - **typescript-docs**: TypeScript documentation patterns and type definition best practices
  - **New TypeScript & Frontend Agents**: Added 8 specialized agents for full-stack TypeScript development
    - **react-frontend-development-expert**: React architecture, hooks, state management, performance
    - **nestjs-backend-development-expert**: NestJS modules, microservices, authentication, APIs
    - **nestjs-code-review-expert**: NestJS security, performance, architecture review
    - **nestjs-unit-testing-expert**: Unit, integration, and e2e testing with Jest
    - **nestjs-database-expert**: TypeORM, Drizzle ORM, database design, migrations
    - **nestjs-security-expert**: Authentication, authorization, JWT, OAuth2, security best practices
    - **typescript-documentation-expert**: JSDoc/TSDoc, API documentation, type definitions
    - **typescript-refactor-expert**: Modern patterns, performance optimization, legacy migration
    - **typescript-security-expert**: OWASP Top 10, npm audit, secure coding practices
    - **typescript-software-architect-review**: Design patterns, scalability, module organization
  - **Updated Documentation**: Complete frontend skills guide and expanded agents documentation
  - **Expanded Support**: Now covering full-stack development with Java/Spring Boot, TypeScript/Node.js, React, and NestJS
- **v1.16.1**:
  - Documentation updates and minor bug fixes
  - Improved skill organization and categorization
  - Updated agent descriptions for better discoverability
- **v1.15.0**:
  - **New comprehensive Makefile with multi-CLI support** for GitHub Copilot CLI, OpenCode CLI, and Codex CLI
  - **Interactive Claude Code installer** (`make install-claude`) with category-based skill selection, conflict handling, and project-specific installation
  - Support for team-based development with version-controlled `.claude/` configurations
  - Enhanced installation management with backup, status, and uninstall capabilities
- **v1.14.0**:
  - New spring-boot-security-jwt skill with JWT authentication patterns, OAuth2/OIDC integration, and permission-based access control
  - New spring-ai-mcp-server-patterns for Model Context Protocol integration
  - Enhanced `/devkit.feature-development` command with AskUserQuestion tool and improved agent fallback order
- **v1.13.0**: New `/devkit.feature-development` command with systematic 9-phase approach for guided feature development, including three new general-purpose agents (explorer, architect, reviewer) with Task tool integration and fallback mechanism
- **v1.12.1**: Fixed commands for correct agent selection on execution
- **v1.12.0**: Long-Running Agent (LRA) workflow commands and guide for multi-session project management
- **v1.11.0**: Enhanced development workflow with new commands, agents, and comprehensive documentation updates
- **v1.10.0**: GitHub integration and workflow automation with PR creation and review commands
- **v1.9.0**: Documentation generation commands and educational content expansion

---

**Made with ❤️ for Java/Spring Boot developers using Claude Code**
