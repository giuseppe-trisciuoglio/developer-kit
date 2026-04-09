# Developer Kit Java Plugin

Comprehensive toolkit for Java, Spring Boot, LangChain4J, and AWS SDK development with Claude Code.

---

## Available Documentation

### Skills Guides

| Guide | Description |
|-------|-------------|
| [Spring Boot Skills](./guide-skills-spring-boot.md) | REST APIs, Security, Caching, Testing, Actuator |
| [JUnit Test Skills](./guide-skills-junit-test.md) | Unit and integration testing patterns |
| [LangChain4J Skills](./guide-skills-langchain4j.md) | AI integration, RAG, Vector stores |
| [AWS Java Skills](./guide-skills-aws-java.md) | S3, DynamoDB, Lambda, Bedrock, RDS |
| [Architecture Skills](./guide-skills-architecture.md) | Clean Architecture and DDD patterns |
| [GraalVM Native Image](./guide-skills-graalvm-native-image.md) | Native executable builds |

### Component Guides

| Guide | Description |
|-------|-------------|
| [Agent Guide](./guide-agents.md) | 9 specialized agents for development tasks |
| [Command Guide](./guide-commands.md) | 11 commands for code generation and review |

---

## Plugin Overview

The Developer Kit Java Plugin provides a complete development environment for Java-based projects:

| Component | Count | Description |
|-----------|-------|-------------|
| **Agents** | 9 | Specialized experts for Spring Boot, security, testing, AI |
| **Commands** | 11 | Slash commands for code review, generation, refactoring |
| **Skills** | 52 | Domain-specific patterns for Spring Boot, JUnit, LangChain4J, AWS |
| **Rules** | 4 | Code quality rules for Java best practices |

---

## Technology Coverage

### Spring Boot Development
- REST APIs with proper HTTP semantics and validation
- Service layer design with dependency injection
- Spring Data JPA with custom queries and optimizations
- JWT authentication and OAuth2/OIDC integration
- Caching, resilience (Resilience4j), and monitoring (Actuator)
- Event-driven architecture with Kafka
- OpenAPI documentation with SpringDoc

### Testing
- JUnit 5 unit tests with Mockito and AssertJ
- Spring Boot integration tests with Testcontainers
- Parameterized tests for multiple scenarios
- Testing strategies for all layers (controllers, services, repositories)
- WireMock for external API mocking

### AI Integration
- LangChain4J framework for AI-powered applications
- RAG (Retrieval-Augmented Generation) implementation
- Vector stores (Qdrant) with similarity search
- Tool/function calling for AI agents
- Spring AI MCP server patterns
- AWS Bedrock for AI/ML workloads

### AWS Integration
- AWS SDK for Java v2 (non-blocking)
- S3 operations, DynamoDB, Lambda functions
- RDS Aurora with Spring Data JPA
- Secrets Manager, KMS encryption
- SQS/SNS messaging

### Architecture
- Clean Architecture and Hexagonal Architecture
- Domain-Driven Design tactical patterns
- GraalVM native images for optimized deployment

---

## Plugin Structure

```
developer-kit-java/
├── agents/                    # 9 specialized agents
│   ├── spring-boot-*.md       # Spring Boot experts
│   ├── java-*.md              # Java generalists
│   └── langchain4j-*.md        # AI integration
├── commands/                   # 11 slash commands (/developer-kit-java:devkit.java.*)
│   ├── devkit.java.code-review.md
│   ├── devkit.java.generate-crud.md
│   ├── devkit.java.write-unit-tests.md
│   └── ...
├── skills/                    # 52 skills organized by domain
│   ├── spring-boot-*/         # 14 Spring Boot skills
│   ├── unit-test-*/          # 15 JUnit testing skills
│   ├── langchain4j-*/         # 9 LangChain4J skills
│   ├── aws-sdk-java-v2-*/     # 10 AWS SDK skills
│   ├── clean-architecture/
│   └── graalvm-native-image/
├── rules/                     # 4 code quality rules
│   ├── error-handling.md
│   ├── language-best-practices.md
│   ├── naming-conventions.md
│   └── project-structure.md
├── docs/                     # This documentation
├── .lsp.json                # Java LSP configuration (jdtls)
├── CLAUDE.md                 # Plugin guidance for Claude Code
└── README.md                 # This file
```

---

## Quick Start

### 1. Explore Available Components

```bash
# List all available commands
/developer-kit-java:devkit.java.*

# Explore specific skills
/use spring-boot-crud-patterns
/use unit-test-service-layer
/use langchain4j-rag-implementation-patterns
```

### 2. Try Common Workflows

**Build a REST API:**
```bash
/developer-kit-java:devkit.java.generate-crud src/main/java/model/Product.java
/developer-kit-java:devkit.java.write-unit-tests src/main/java/service/ProductService.java
/developer-kit-java:devkit.java.code-review full
```

**Security Audit:**
```bash
/developer-kit-java:devkit.java.security-review
/developer-kit-java:devkit.java.dependency-audit
```

### 3. Learn Skills Patterns

See individual skill guides for detailed patterns and examples:
- [Spring Boot Skills](./guide-skills-spring-boot.md) - Complete API development
- [JUnit Test Skills](./guide-skills-junit-test.md) - Comprehensive testing
- [LangChain4J Skills](./guide-skills-langchain4j.md) - AI integration
- [AWS Java Skills](./guide-skills-aws-java.md) - Cloud development

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Build Spring Boot feature | `spring-boot-backend-development-expert` |
| Review Spring Boot code | `spring-boot-code-review-expert` |
| Write Spring Boot tests | `spring-boot-unit-testing-expert` |
| Refactor Java code | `java-refactor-expert` |
| Security audit | `java-security-expert` |
| Architecture review | `java-software-architect-review` |
| Generate documentation | `java-documentation-specialist` |
| Create tutorials | `java-tutorial-engineer` |
| Integrate AI with LangChain4J | `langchain4j-ai-development-expert` |

---

## Key Features

### Development Productivity
- Code generation for CRUD operations, tests, and documentation
- Intelligent refactoring with Clean Architecture principles
- Comprehensive code review covering architecture, security, and best practices
- Dependency management with vulnerability scanning

### Quality Assurance
- 15 specialized JUnit testing skills covering all layers
- Integration testing with Testcontainers for real databases
- Security audit following OWASP guidelines
- Code quality rules enforced automatically

### Modern Java Stack
- Java 17+ with records, sealed classes, and pattern matching
- Spring Boot 3.x with modern patterns
- Non-blocking AWS SDK v2
- GraalVM native images for fast startup

---

## See Also

### Related Plugins

| Plugin | Documentation |
|--------|--------------|
| Core Plugin | [developer-kit-core/docs/](../../developer-kit-core/docs/) |
| TypeScript | [developer-kit-typescript/docs/](../../developer-kit-typescript/docs/) |
| AWS | [developer-kit-aws/docs/](../../developer-kit-aws/docs/) |

### External Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [LangChain4J Documentation](https://docs.langchain4j.dev/)
- [AWS SDK for Java](https://docs.aws.amazon.com/sdk-for-java/)
- [JUnit 5 Documentation](https://junit.org/junit5/docs/current/user-guide/)

---

## Version Information

- **Plugin Version**: 2.7.2
- **Minimum Java**: 17+
- **Recommended Java**: 21+
- **Spring Boot**: 3.x/4.x
- **LangChain4J**: Latest stable
- **AWS SDK for Java**: 2.x

---

## Contributing

For component creation guidelines, see the [Contributing Guide](../../CONTRIBUTING.md).

### Validation

Before committing changes, run validation:

```bash
python ../../.skills-validator-check/validators/cli.py --all
```
