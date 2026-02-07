# Java Plugin Agents Guide

This guide provides comprehensive documentation for all Java and Spring Boot specialized agents available in the Developer Kit Java Plugin.

---

## Table of Contents

1. [Overview](#overview)
2. [Spring Boot Development Agents](#spring-boot-development-agents)
3. [Java Development Agents](#java-development-agents)
4. [LangChain4J AI Agents](#langchain4j-ai-agents)
5. [Agent Usage Guidelines](#agent-usage-guidelines)
6. [See Also](#see-also)

---

## Overview

The Java Plugin provides specialized agents for Java, Spring Boot, LangChain4J, and AWS SDK development. These agents have deep expertise in their respective domains and can help with development, code review, testing, security, and architecture.

### Available Agents

- **Spring Boot Agents**: 3 specialized agents for Spring Boot development
- **Java Development Agents**: 5 specialized agents for general Java development
- **LangChain4J Agents**: 1 specialized agent for AI integration with LangChain4J

---

## Spring Boot Development Agents

### `spring-boot-backend-development-expert`

**File**: `agents/spring-boot-backend-development-expert.md`

**Purpose**: Spring Boot backend development specialist for building production-ready applications with best practices.

**When to use:**
- Building new Spring Boot features
- Implementing REST APIs, services, and repositories
- Configuring Spring Boot applications
- Working with Spring Data JPA, Security, or other Spring projects
- Implementing business logic in layered architecture

**Key Capabilities:**
- Controller, Service, Repository pattern implementation
- Spring Boot configuration and properties
- REST API development with proper HTTP semantics
- Exception handling and validation
- Dependency injection and component design

---

### `spring-boot-code-review-expert`

**File**: `agents/spring-boot-code-review-expert.md`

**Purpose**: Spring Boot code quality and best practices review with framework-specific patterns.

**When to use:**
- Reviewing Spring Boot code before commits
- Ensuring Spring Boot best practices compliance
- Identifying framework-specific anti-patterns
- Validating configuration and component design
- Reviewing Spring Boot integration code

**Key Capabilities:**
- Spring Boot specific code quality assessment
- Framework pattern validation (MVC, Security, Data)
- Configuration review (@ConfigurationProperties, @Value)
- Component design and dependency injection review
- Spring Boot-specific best practices

---

### `spring-boot-unit-testing-expert`

**File**: `agents/spring-boot-unit-testing-expert.md`

**Purpose**: JUnit and Spring Boot testing strategies for comprehensive test coverage.

**When to use:**
- Writing unit tests for Spring Boot components
- Designing test strategies for Spring applications
- Mocking dependencies with Mockito
- Testing Spring configurations
- Integration testing with @SpringBootTest

**Key Capabilities:**
- JUnit 5 test design for Spring Boot
- Mockito mocking strategies
- Spring Boot test annotations and slices
- Test coverage optimization
- Testing Controllers, Services, Repositories

---

## Java Development Agents

### `java-refactor-expert`

**File**: `agents/java-refactor-expert.md`

**Purpose**: Java code refactoring with clean code principles, SOLID patterns, and Java best practices.

**When to use:**
- Refactoring legacy Java code
- Applying clean code principles
- Implementing design patterns
- Reducing code complexity
- Improving code maintainability

**Key Capabilities:**
- Clean Code principles application
- SOLID pattern implementation
- Code complexity reduction
- Design pattern identification and application
- Java 8+ features utilization

---

### `java-security-expert`

**File**: `agents/java-security-expert.md`

**Purpose**: Java security vulnerability assessment covering OWASP, CVEs, and configuration security.

**When to use:**
- Security auditing Java applications
- Identifying OWASP Top 10 vulnerabilities
- Reviewing authentication and authorization
- Checking for sensitive data exposure
- Validating cryptographic practices

**Key Capabilities:**
- OWASP vulnerability detection
- Authentication and authorization review
- Cryptographic practice validation
- Dependency vulnerability scanning (CVEs)
- Configuration security assessment

---

### `java-software-architect-review`

**File**: `agents/java-software-architect-review.md`

**Purpose**: Java architecture design review focusing on patterns, scalability, and architectural decisions.

**When to use:**
- Reviewing Java application architecture
- Evaluating design pattern usage
- Assessing scalability and performance
- Validating architectural decisions
- Planning refactoring of architecture

**Key Capabilities:**
- Architecture pattern review (layered, hexagonal, etc.)
- Design pattern assessment
- Scalability and performance evaluation
- Architectural decision validation
- Refactoring recommendations

---

### `java-documentation-specialist`

**File**: `agents/java-documentation-specialist.md`

**Purpose**: Java documentation generation for APIs, architecture guides, and technical manuals.

**When to use:**
- Generating API documentation from code
- Creating architecture documentation
- Writing technical guides
- Documenting design decisions
- Creating user manuals for Java applications

**Key Capabilities:**
- Javadoc generation and enhancement
- Architecture documentation creation
- API guide generation
- Technical manual writing
- Design decision documentation (ADR)

---

### `java-tutorial-engineer`

**File**: `agents/java-tutorial-engineer.md`

**Purpose**: Java learning and tutorial creation for effective knowledge transfer.

**When to use:**
- Creating Java tutorials and guides
- Explaining Java concepts to team members
- Designing learning paths for Java development
- Writing educational content about Java
- Creating onboarding materials

**Key Capabilities:**
- Tutorial design and structure
- Concept explanation simplification
- Learning path creation
- Practical example development
- Assessment and exercise creation

---

## LangChain4J AI Agents

### `langchain4j-ai-development-expert`

**File**: `agents/langchain4j-ai-development-expert.md`

**Purpose**: LangChain4J AI integration patterns for building AI-powered Java applications.

**When to use:**
- Integrating AI models with LangChain4J
- Building AI-powered features in Java
- Implementing RAG (Retrieval-Augmented Generation)
- Working with vector stores and embeddings
- Creating AI agents and tools

**Key Capabilities:**
- LangChain4J framework integration
- AI service patterns implementation
- RAG system development
- Vector store configuration (Qdrant, etc.)
- Tool/function calling implementation
- Prompt engineering for Java applications

---

## Agent Usage Guidelines

### When to Use Java Plugin Agents

Java Plugin agents are most effective for:
- **Spring Boot Development**: Building backend services, REST APIs, microservices
- **Code Quality**: Reviewing and refactoring Java code
- **Testing**: Writing comprehensive unit and integration tests
- **Security**: Auditing Java applications for vulnerabilities
- **Architecture**: Designing and reviewing Java application architecture
- **AI Integration**: Building AI-powered features with LangChain4J

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the spring-boot-code-review-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

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

## See Also

- [Java Commands Guide](./guide-commands.md) - Java plugin commands
- [Spring Boot Skills Guide](./guide-skills-spring-boot.md) - Spring Boot skills
- [JUnit Test Skills Guide](./guide-skills-junit-test.md) - JUnit testing skills
- [LangChain4J Skills Guide](./guide-skills-langchain4j.md) - LangChain4J skills
- [AWS Java Skills Guide](./guide-skills-aws-java.md) - AWS Java SDK skills
- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
