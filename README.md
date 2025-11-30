# Developer Kit for Claude Code

> A curated collection of reusable skills and agents for automating development tasks in Claude Code — focusing on
> Java/Spring Boot patterns with extensibility to PHP, TypeScript, and Python

**Developer Kit for Claude Code** teaches Claude how to **perform development tasks in a repeatable way** across
multiple languages and frameworks. It includes specialized agents for code review, testing patterns, REST API design,
and AI integration.

**52 Total Skills** — Comprehensive coverage of Spring Boot, testing, AI integration, cloud development, AI
engineering patterns, and documentation generation

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

## ✨ Key Features

**Specialized** — Domain-specific agents for code review, testing, and AI development tailored to Java/Spring Boot

**Composable** — Skills stack together automatically. Claude identifies which skills are needed and uses them in
combination

**Portable** — Use the same skills across Claude.ai, Claude Code CLI, Claude Desktop, and the Claude API

**Efficient** — Skills load on-demand, consuming minimal tokens until they're actively used

## 🏗️ Architecture & Patterns

This kit promotes a **feature-based, DDD-inspired architecture** for Java/Spring Boot projects:

```
feature/
├── domain/              # Domain-pure logic
│   ├── model/           # Spring-free entities
│   ├── repository/      # Domain ports (interfaces)
│   └── service/         # Domain services
├── application/         # Use cases & business logic
│   └── service/         # Application services (@Service)
├── presentation/        # HTTP layer
│   ├─ rest/            # REST controllers & mappers
│   └── dto/             # Immutable DTOs/records
└── infrastructure/      # Technical adapters
    └── persistence/     # JPA repositories & adapters
```

### Core Principles

- ✅ Constructor injection exclusively (never field injection)
- ✅ Java records (16+) preferred for DTOs
- ✅ Repository pattern with domain interfaces
- ✅ Immutability throughout (`final` fields, `@Value`, records)
- ✅ Clean separation: domain ↔ framework

## 🔧 Technology Stack

| Category                | Technology                             | Version             |
|-------------------------|----------------------------------------|---------------------|
| **Java**                | OpenJDK/GraalVM                        | 16+                 |
| **Framework**           | Spring Boot                            | 3.x                 |
| **Testing**             | JUnit 5 (Jupiter) + Mockito + AssertJ  | 5.x / 4.x+          |
| **Integration Testing** | Testcontainers                         | 1.19.0+             |
| **Data**                | Spring Data JPA                        | Jakarta Persistence |
| **Graph Database**      | Spring Data Neo4j                      | 7.x                 |
| **Validation**          | Jakarta Validation                     | 3.0+                |
| **Utilities**           | Lombok                                 | 1.18.30+            |
| **Messaging**           | Spring Cloud Stream                    | 4.x                 |
| **AWS SDK**             | AWS SDK for Java v2                    | 2.20+               |
| **Cloud**               | AWS (RDS Aurora, S3, Lambda, DynamoDB) | Latest              |
| **AI/ML**               | LangChain4J, AWS Bedrock               | Latest              |

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
- **📋 TypeScript** — Node.js, NestJS, Express patterns (planned)
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

- **Questions?** Open an [issue](https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/issues)
- **Contributions?** Submit a [pull request](https://github.com/giuseppe-trisciuoglio/developer-kit-claude-code/pulls)
- **Integration proposals?** Create a discussion or reach out

## 📅 Changelog

For a complete history of changes, please see the dedicated [CHANGELOG.md](CHANGELOG.md) file.

Recent highlights:

- **v1.12.1**: Fixed commands for correct agent selection on execution
- **v1.12.0**: Long-Running Agent (LRA) workflow commands and guide for multi-session project management
- **v1.11.0**: Enhanced development workflow with new commands, agents, and comprehensive documentation updates
- **v1.10.0**: GitHub integration and workflow automation with PR creation and review commands
- **v1.9.0**: Documentation generation commands and educational content expansion

---

**Made with ❤️ for Java/Spring Boot developers using Claude Code**
