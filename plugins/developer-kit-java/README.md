# Developer Kit Java

Comprehensive Java development toolkit with Spring Boot, testing, LangChain4J, and AWS integration.

## Overview

The `developer-kit-java` plugin provides extensive support for Java development, including Spring Boot applications, unit/integration testing with JUnit, LangChain4J for AI applications, and AWS SDK integration.

## Agents

- **spring-boot-backend-development-expert** - Spring Boot development
- **spring-boot-code-review-expert** - Spring Boot code review
- **spring-boot-unit-testing-expert** - Spring Boot testing
- **java-refactor-expert** - Java-specific refactoring
- **java-security-expert** - Java security best practices
- **java-software-architect-review** - Java architecture review
- **java-documentation-specialist** - Java documentation
- **java-tutorial-engineer** - Java learning resources
- **langchain4j-ai-development-expert** - LangChain4J integration

## Commands

- `devkit.java.code-review` - Comprehensive Java code review
- `devkit.java.generate-crud` - Generate CRUD operations
- `devkit.java.refactor-class` - Refactor Java classes
- `devkit.java.architect-review` - Architecture review
- `devkit.java.dependency-audit` - Dependency analysis
- `devkit.java.generate-docs` - Generate documentation
- `devkit.java.security-review` - Security review
- `devkit.java.upgrade-dependencies` - Upgrade dependencies
- `devkit.java.write-unit-tests` - Generate unit tests
- `devkit.java.write-integration-tests` - Generate integration tests
- `devkit.java.generate-refactoring-tasks.md` - Generate refactoring tasks from bounded context

## Skills

### Spring Boot
- Spring Boot Actuator, Cache, CRUD Patterns, Dependency Injection
- Event-Driven Patterns, OpenAPI Documentation, REST API Standards
- Saga Pattern, Security JWT, Test Patterns, Resilience4j
- **spring-boot-project-creator** - Project generation from specification

### Architecture
- **clean-architecture** - Clean Architecture, Hexagonal Architecture, and DDD patterns for Java 21+ Spring Boot 3.5+

### Spring Data
- Spring Data JPA, Spring Data Neo4j

### Spring AI
- **spring-ai-mcp-server-patterns** - Model Context Protocol server implementation

### JUnit Testing
- Unit test patterns for all layers and scenarios

### LangChain4J
- AI Services, MCP Server, RAG Implementation, Spring Boot Integration
- Testing Strategies, Tool Function Calling, Vector Stores Configuration
- **qdrant** - Qdrant vector database integration

### AWS Java SDK
- RDS, Bedrock, DynamoDB, KMS, Lambda, Messaging, S3, Secrets Manager

### AWS Lambda Integration
- **aws-lambda-java-integration** - AWS Lambda integration patterns for Java with Micronaut Framework and Raw Java handlers

### GraalVM Native Image
- **graalvm-native-image** - Build native executables from Java applications, optimize cold start times, configure Maven/Gradle native build tools, resolve reflection and resource issues

## Dependencies

- `developer-kit` (required)
- `developer-kit-ai` (for LangChain4J skills)

