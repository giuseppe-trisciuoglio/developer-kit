# Complete Guide to Developer Kit Agents

This guide provides comprehensive documentation for all specialized agents (subagents) available in the Developer Kit, organized by category with detailed explanations, use cases, and practical examples.

---

## Table of Contents

1. [General Purpose Agents](#general-purpose-agents)
2. [Java Development Agents](#java-development-agents)
3. [Testing & Quality Agents](#testing--quality-agents)
4. [AI & LangChain4j Agents](#ai--langchain4j-agents)
5. [Documentation & Engineering Agents](#documentation--engineering-agents)
6. [Agent Usage Guidelines](#agent-usage-guidelines)
7. [Complete Workflow Examples](#complete-workflow-examples)

---

## Overview

Agents are specialized AI assistants with dedicated context windows, custom prompts, and specific tool access. They enable efficient problem-solving by delegating task-specific work to focused experts.

### Key Benefits

- **Context Preservation**: Each agent operates independently, keeping main conversation focused
- **Specialized Expertise**: Fine-tuned with detailed instructions for specific domains
- **Reusability**: Available across projects and shareable with team
- **Flexible Permissions**: Each agent can have different tool restrictions
- **Autonomous Selection**: Claude automatically selects appropriate agent based on task

### Agent Locations

- **Project agents**: `.claude/agents/` (team-shared via git, highest priority)
- **User agents**: `~/.claude/agents/` (personal, available across projects)
- **Plugin agents**: Bundled with installed plugins

---

## General Purpose Agents

### `explorer`

**Description**: Expert code analyst specializing in tracing and understanding feature implementations across codebases, mapping execution paths, architecture layers, and documenting dependencies.

**When to use:**
- Understanding existing features before modification
- Mapping codebase architecture and patterns
- Tracing data flow through complex systems
- Documenting implementation details for team members
- Onboarding new developers to a project
- Reverse engineering legacy code

**Model**: Inherit (uses same model as main conversation)

**Key Capabilities:**
- Feature discovery and entry point identification
- Complete execution flow tracing
- Architecture layer mapping (presentation → business → data)
- Pattern and abstraction identification
- Dependency analysis (internal and external)
- Cross-cutting concerns documentation (auth, logging, caching)

**Tools Available**: Read, Write, Edit, Glob, Grep, Bash

**Example Usage:**
```javascript
Task(
  description: "Analyze user authentication feature",
  prompt: "Trace through the user authentication feature comprehensively. Map all components, data flow, and integration points.",
  subagent_type: "developer-kit:explorer"
)
```

**Output Provides:**
- Entry points with file:line references
- Step-by-step execution flow with data transformations
- Key components and their responsibilities
- Architecture insights and patterns
- Dependencies and integration points
- Critical files list for understanding

---

### `architect`

**Description**: Senior software architect who delivers comprehensive, actionable architecture blueprints by deeply understanding codebases and making confident architectural decisions.

**When to use:**
- Designing new features from scratch
- Major refactoring initiatives
- System integration planning
- Performance optimization strategies
- Technology stack decisions
- Architectural debt assessment

**Model**: Sonnet (recommended for architectural reasoning)

**Key Capabilities:**
- Codebase pattern analysis and convention extraction
- Complete architecture design with specific implementations
- Component design with interfaces and dependencies
- Data flow mapping from entry points to outputs
- Build sequence planning with phased implementation
- Trade-off analysis and decision rationale

**Tools Available**: Read, Write, Edit, Glob, Grep, Bash

**Example Usage:**
```javascript
Task(
  description: "Design real-time notifications architecture",
  prompt: "Design complete architecture for real-time notifications. Consider scalability, reliability, and integration with existing systems.",
  subagent_type: "developer-kit:architect"
)
```

**Output Provides:**
- Patterns & conventions found with file references
- Architecture decision with clear rationale
- Component design with file paths and responsibilities
- Implementation map with specific files to create/modify
- Data flow documentation
- Build sequence with prioritized checklist

---

### `code-reviewer`

**Description**: Expert code reviewer specializing in modern software development with high precision to minimize false positives, focusing only on issues that truly matter.

**When to use:**
- Code quality assurance before commits
- Pull request reviews
- Identifying critical bugs and security issues
- Performance bottleneck detection
- Architectural anti-pattern identification
- Best practices compliance verification

**Model**: Inherit (uses same model as main conversation)

**Key Capabilities:**
- Bug detection (logic errors, null handling, race conditions)
- Security vulnerability assessment (OWASP Top 10)
- Performance and scalability analysis
- Code quality evaluation (DRY, SOLID, complexity)
- Project guidelines compliance
- Confidence-based issue filtering (≥80% confidence)

**Tools Available**: Read, Write, Edit, Glob, Grep, Bash

**Confidence Scoring:**
- **100%**: Absolutely certain, will happen frequently
- **75%**: Highly confident, very likely real issue
- **50%**: Moderately confident, real but might be nitpicky
- **25%**: Somewhat confident, might be false positive
- **0%**: Not confident, false positive or pre-existing
- **Only reports ≥80% confidence issues**

**Example Usage:**
```javascript
Task(
  description: "Review payment processing code",
  prompt: "Review the payment processing implementation for bugs, security vulnerabilities, and performance issues.",
  subagent_type: "developer-kit:code-reviewer"
)
```

**Output Provides:**
- Issues grouped by severity (Critical, High, Medium)
- Confidence scores for each issue
- Specific file paths and line numbers
- Concrete fix suggestions
- Project guideline references

---

## Java Development Agents

### `java-software-architect-review`

**Description**: Expert Java software architect specializing in Clean Architecture, Domain-Driven Design (DDD), and Spring Boot patterns.

**When to use:**
- Major refactoring initiatives
- Architecture quality assessment
- Identifying architectural debt
- Reviewing adherence to DDD principles
- Evaluating Clean Architecture layering
- Microservices design validation

**Model**: Sonnet

**Key Capabilities:**

1. **Clean Architecture Expertise**
   - Hexagonal Architecture patterns
   - Proper layer separation (domain → application → infrastructure → presentation)
   - SOLID principles application
   - Dependency Injection patterns
   - Feature-based organization

2. **Domain-Driven Design (DDD)**
   - Bounded contexts and context mapping
   - Aggregates and entities design
   - Domain events with Spring
   - Value objects with Java records
   - Repositories and domain services
   - Ubiquitous language enforcement
   - Anti-corruption layers

3. **Spring Boot Architecture**
   - Feature-based architecture patterns
   - Configuration management best practices
   - Bean lifecycle and scoping
   - AOP patterns for cross-cutting concerns
   - Transaction management strategies
   - Exception handling patterns
   - Jakarta Bean Validation integration

4. **Microservices & Distributed Systems**
   - Spring Cloud architecture
   - Event sourcing implementations
   - CQRS patterns
   - Saga pattern for distributed transactions
   - API Gateway patterns
   - Distributed tracing
   - Message-driven architecture

**Skills Integration**: Automatically invokes 40+ Spring Boot, testing, LangChain4j, and AWS skills for comprehensive architectural reviews.

**Example Interactions:**

```bash
# Review package structure for Clean Architecture
"Review this Spring Boot package structure for proper Clean Architecture layering"

# DDD patterns evaluation
"Assess if this JPA entity design follows DDD aggregate patterns and bounded contexts"

# Spring Security architecture
"Evaluate this Spring Security configuration for proper separation of concerns"

# Microservices domain events
"Review this microservice's domain events implementation with Spring ApplicationEvent"

# Transaction boundaries
"Evaluate our transaction boundaries with @Transactional for aggregate consistency"
```

**Output Includes:**
- Assessment of current architecture quality (1-10 scale)
- Specific violations of Clean Architecture or DDD principles
- Concrete refactoring recommendations with code examples
- Risk assessment of proposed changes
- Next steps for implementation priority

---

### `spring-boot-backend-development-expert`

**Description**: Expert Spring Boot backend developer specializing in feature implementation, architecture, and best practices.

**When to use:**
- Implementing new Spring Boot features
- REST API development
- Database integration
- Backend architecture decisions
- Performance optimization
- Security implementation

**Model**: Sonnet

**Key Capabilities:**

1. **Feature Implementation**
   - REST APIs with proper HTTP methods and status codes
   - CRUD operations following best practices
   - Service layer design with business logic
   - Repository pattern implementation
   - DTO patterns with Java records

2. **Spring Boot Best Practices**
   - Constructor injection exclusively
   - Profile-based configuration management
   - Proper bean scoping and lifecycle
   - Exception handling with @ControllerAdvice
   - Validation with Jakarta Bean Validation

3. **Database & Persistence**
   - Spring Data JPA with repository pattern
   - Entity design with relationships
   - Transaction boundaries with @Transactional
   - Database migrations with Flyway/Liquibase
   - Multi-tenancy patterns

4. **Testing Strategy**
   - Unit tests with JUnit 5 and Mockito
   - Integration tests with Testcontainers
   - Slice tests (@WebMvcTest, @DataJpaTest)
   - Comprehensive test coverage

5. **Security Implementation**
   - Spring Security with JWT authentication
   - CORS configuration
   - Input validation and sanitization
   - Method-level security with @PreAuthorize

**Skills Integration**: Automatically invokes 33+ Spring Boot, testing, and AWS skills for complete backend development.

**Example Interactions:**

```bash
# REST API implementation
"Implement a REST API for user management with CRUD operations"

# Database integration
"Create a Spring Data JPA repository with custom queries for orders"

# Security implementation
"Add JWT authentication to this Spring Boot application"

# Performance optimization
"Implement caching strategy for this service layer"

# AWS integration
"Integrate S3 file storage for user profile pictures"
```

**Output Includes:**
- Complete implementation following Spring Boot best practices
- Comprehensive test coverage (unit + integration)
- Error handling and validation
- Performance considerations
- Security implications
- Documentation examples

---

### `java-security-expert`

**Description**: Expert security auditor specializing in DevSecOps, comprehensive cybersecurity, and compliance frameworks.

**When to use:**
- Security audits and vulnerability assessments
- Compliance requirements (GDPR, HIPAA, SOC2)
- DevSecOps integration
- Authentication/authorization implementation
- Threat modeling
- Incident response planning

**Model**: Sonnet

**Key Capabilities:**

1. **Authentication & Authorization**
   - OAuth and OpenID Connect
   - JWT security best practices
   - Zero-trust architecture
   - Multi-factor authentication
   - Authorization patterns (RBAC, ABAC, ReBAC)
   - API security (scopes, keys, rate limiting)

2. **OWASP & Vulnerability Management**
   - OWASP Top 10 compliance
   - Application Security Verification Standard (ASVS)
   - Vulnerability assessment and penetration testing
   - Threat modeling (STRIDE, PASTA)
   - Risk assessment and CVSS scoring

3. **Application Security Testing**
   - Static analysis (SAST) with SonarQube
   - Dynamic analysis (DAST) with OWASP ZAP
   - Interactive testing (IAST)
   - Dependency scanning with Snyk
   - Container security scanning

4. **DevSecOps & Security Automation**
   - Security pipeline integration
   - Shift-left security practices
   - Security as Code with OPA
   - Container and Kubernetes security
   - Supply chain security (SLSA, SBOM)

5. **Cloud & Infrastructure Security**
   - Cloud security posture management
   - Infrastructure as Code security
   - Network security and access controls
   - Data protection and encryption
   - Secrets management

**Skills Integration**: Automatically invokes Spring Boot security and AWS skills for comprehensive security audits.

**Example Interactions:**

```bash
# Complete security audit
"Perform a comprehensive security audit of this Spring Boot application"

# OWASP compliance check
"Review this code for OWASP Top 10 vulnerabilities"

# Authentication implementation
"Implement OAuth2 authentication with Spring Security"

# DevSecOps integration
"Set up security scanning in our CI/CD pipeline"

# Compliance assessment
"Assess our application for GDPR compliance"
```

**Output Includes:**
- Security assessment score (1-10)
- Critical vulnerabilities requiring immediate attention
- High-priority security improvements
- Compliance status and gaps
- Specific implementation guidance
- Monitoring and maintenance recommendations

**Security Finding Priorities:**
- **Critical (P0)**: Remote code execution, authentication bypass, data exposure
- **High (P1)**: Outdated CVEs, insecure configurations, missing security headers
- **Medium (P2)**: Logging gaps, insufficient validation, access control improvements
- **Low (P3)**: Documentation, code style security, additional testing

---

## Testing & Quality Agents

### `spring-boot-code-review-expert`

**Description**: Expert Spring Boot code reviewer specializing in Java best practices, patterns, and architectural issues.

**When to use:**
- After implementing new features
- Before creating pull requests
- During refactoring initiatives
- When improving code quality
- For adherence to Spring Boot conventions

**Model**: Sonnet

**Key Capabilities:**

1. **Spring Boot Patterns Review**
   - Constructor injection with @RequiredArgsConstructor
   - Proper configuration classes
   - Correct Spring annotation usage
   - Service layer patterns
   - Profile-based configuration

2. **Java Code Quality**
   - Idiomatic Java usage
   - Effective use of `final` and immutability
   - Proper `Optional` usage
   - Java 16+ records or Lombok
   - Stream API usage

3. **Architecture & Design Patterns**
   - Feature-based vs layer-based organization
   - SOLID principles adherence
   - Repository pattern implementation
   - Service layer responsibilities
   - Clean Architecture layering

4. **REST API Standards**
   - Correct HTTP methods
   - Proper status code usage
   - RESTful naming conventions
   - Error handling and response formatting
   - OpenAPI/Swagger documentation

5. **Error Handling**
   - ResponseStatusException usage
   - Global exception handler integration
   - Proper status codes
   - Meaningful error messages
   - Logging and monitoring

**Skills Integration**: Automatically invokes 23+ Spring Boot and testing skills for comprehensive code reviews.

**Example Interactions:**

```bash
# Complete code review
"Review this Spring Boot service for best practices and code quality"

# Architecture review
"Assess this package structure for proper layer separation"

# REST API review
"Review these controller endpoints for RESTful design"

# Security review
"Check this code for security vulnerabilities and best practices"

# Testing review
"Review the test coverage and quality for this service"
```

**Output Includes:**
- Overall assessment (quality score 1-10)
- Critical issues that must be fixed
- Warning areas that should be improved
- Suggestions for enhancement
- Specific code examples for improvements
- Testing recommendations

**Review Priorities:**
- **Critical (Must Fix)**: Security vulnerabilities, null pointer exceptions, memory leaks, thread safety violations, broken business logic
- **Warnings (Should Fix)**: SOLID violations, poor naming, missing tests, performance anti-patterns, inconsistent error handling
- **Suggestions (Consider)**: Readability improvements, additional logging, documentation, modern Java features, architectural refinements

---

### `spring-boot-unit-testing-expert`

**Description**: Expert in unit testing with Spring Test, JUnit 5, and Mockito for Spring Boot applications.

**When to use:**
- Writing unit tests for new code
- Improving test coverage
- Reviewing testing strategies
- Implementing test best practices
- Test architecture design

**Model**: Sonnet

**Key Capabilities:**

1. **JUnit 5 Best Practices**
   - Test naming conventions
   - Parameterized testing with @ParameterizedTest
   - Test lifecycle management
   - Test tagging and filtering
   - AssertJ assertions
   - Dynamic tests and templates

2. **Mockito Testing Strategies**
   - Mock creation and configuration
   - Spy usage for partial mocking
   - Argument captors
   - Behavior vs state verification
   - Strict vs lenient mocking
   - Mock cleanup patterns

3. **Spring Test Integration**
   - `@SpringBootTest` configuration
   - `@WebMvcTest` for controllers
   - `@DataJpaTest` for repositories
   - `@JsonTest` for JSON serialization
   - Test slices and context optimization
   - `@TestPropertySource` and profiles

4. **Test Architecture & Design**
   - Given-When-Then structure
   - Test data builders and factories
   - Fixture management
   - Test isolation and independence
   - Test inheritance and shared config
   - Naming conventions and organization

5. **Advanced Testing Patterns**
   - Service layer unit testing
   - Controller testing with MockMvc
   - Repository testing with in-memory databases
   - Exception handling testing
   - Performance and timeout testing
   - Parameterized testing

**Skills Integration**: Automatically invokes 19+ JUnit and Spring Boot testing skills for comprehensive test implementation.

**Example Interactions:**

```bash
# Generate unit tests
"Write comprehensive unit tests for this UserService class"

# Controller testing
"Create MockMvc tests for this REST controller"

# Repository testing
"Write @DataJpaTest tests for this JPA repository"

# Exception testing
"Add tests for exception handling in this service"

# Parameterized tests
"Create parameterized tests for input validation"
```

**Output Includes:**
- Comprehensive test suite covering all scenarios
- Proper test structure and organization
- Clear test documentation and comments
- Performance considerations
- Maintenance guidelines

**Test Implementation Process:**
1. **Test Planning**: Identify scenarios and edge cases
2. **Test Implementation**: Setup, execution, assertion, cleanup
3. **Quality Assurance**: Coverage, isolation, assertions, performance

---

## AI & LangChain4j Agents

### `langchain4j-ai-development-expert`

**Description**: Expert LangChain4j developer for building AI applications, RAG systems, ChatBots, and MCP servers.

**When to use:**
- Building AI-powered applications
- Implementing RAG (Retrieval-Augmented Generation) systems
- Creating chatbots and conversational AI
- Developing MCP (Model Context Protocol) servers
- Integrating AI services with Spring Boot
- Vector store configuration

**Model**: Sonnet

**Key Capabilities:**

1. **LangChain4j Core Patterns**
   - AI Services with declarative interfaces
   - Chat model integration (OpenAI, Anthropic, HuggingFace)
   - Embedding models and vector stores
   - Memory management and conversation context
   - Tool/function calling patterns
   - Streaming and real-time interactions

2. **RAG (Retrieval-Augmented Generation) Systems**
   - Document ingestion and preprocessing pipelines
   - Text segmentation and chunking strategies
   - Vector store selection and configuration
   - Embedding model optimization
   - Retrieval strategies and similarity search
   - Context injection and prompt engineering

3. **ChatBot Development**
   - Conversation flow design
   - Context management and memory persistence
   - Multi-turn conversation handling
   - Intent recognition and routing
   - Response streaming
   - Personality customization

4. **MCP (Model Context Protocol) Servers**
   - MCP server implementation patterns
   - Tool and resource definitions
   - Protocol compliance and message handling
   - Integration with LangChain4j applications
   - Error handling and fallbacks
   - Performance optimization

5. **Integration & Architecture**
   - Spring Boot integration with LangChain4j
   - Database integration for embeddings
   - External API integration and tool calling
   - Observability, monitoring, and logging
   - Performance optimization and scaling
   - Security considerations

**Skills Integration**: Automatically invokes 10+ LangChain4j, vector database, and AWS skills for complete AI development.

**Example Interactions:**

```bash
# AI service creation
"Create an AI service interface for document question answering"

# RAG implementation
"Implement a RAG system with vector store for document retrieval"

# ChatBot development
"Build a customer support chatbot with conversation memory"

# MCP server
"Create an MCP server with custom tools for document processing"

# Spring Boot integration
"Integrate LangChain4j AI services into this Spring Boot application"
```

**Output Includes:**
- Complete AI service implementation with proper interfaces
- RAG pipeline configuration and optimization
- Vector store setup and indexing strategies
- Testing strategies for AI components
- Performance monitoring and optimization guidelines
- Security and compliance considerations

**Implementation Process:**
1. **Requirements Analysis**: Use case definition, model selection, architecture design
2. **Implementation**: AI service development, RAG pipeline, vector store setup
3. **Testing & Optimization**: AI testing, performance tuning, monitoring setup

---

### `prompt-engineering-expert`

**Description**: Expert prompt engineer specializing in advanced prompting techniques, LLM optimization, and AI system design.

**When to use:**
- Creating optimized prompts for LLMs
- Improving prompt quality and consistency
- Reducing token usage and costs
- Document/code analysis prompts
- Multi-agent system design
- Production prompt preparation

**Model**: Sonnet

**Key Capabilities:**

1. **Advanced Prompting Techniques**
   - Chain-of-Thought (CoT) reasoning
   - Constitutional AI principles
   - Few-Shot Learning examples
   - Meta-Prompting patterns
   - Self-Consistency techniques
   - Program-Aided Language Models

2. **Document & Information Retrieval**
   - Document analysis and extraction
   - Semantic search patterns
   - Cross-reference analysis
   - Intelligent summarization
   - Knowledge extraction
   - Legal & technical analysis

3. **Code Comprehension & Analysis**
   - Architecture analysis prompts
   - Security review prompts
   - Documentation generation
   - Test case generation
   - Refactoring suggestions
   - Performance analysis

4. **Multi-Agent Systems**
   - Role definition and personas
   - Collaboration protocols
   - Workflow orchestration
   - Memory management
   - Conflict resolution
   - Performance monitoring

5. **Production Optimization**
   - Token efficiency optimization
   - Response time reduction
   - A/B testing frameworks
   - Performance monitoring
   - Scalability design
   - Error handling

6. **Model-Specific Optimization**
   - Anthropic Claude (Constitutional AI, XML)
   - OpenAI GPT (Function calling, JSON mode)
   - Open Source Models (Special tokens)
   - Multimodal Models (Vision-language)

**Skills Integration**: Automatically invokes 7+ LangChain4j AI skills for prompt optimization.

**Example Interactions:**

```bash
# Prompt optimization
"Optimize this prompt for better consistency and reduced token usage"

# Document analysis prompt
"Create a prompt for extracting key information from technical specifications"

# Code analysis prompt
"Design a prompt for security vulnerability detection in Java code"

# Multi-agent design
"Create role definitions and collaboration protocols for a multi-agent system"

# Production optimization
"Optimize these prompts for production deployment with cost constraints"
```

**Output Includes:**
- **The Complete Prompt**: Full text ready for immediate use
- **Implementation Notes**: Techniques used and design rationale
- **Testing & Evaluation**: Test cases and success metrics
- **Usage Guidelines**: When and how to use effectively
- **Performance Optimization**: Cost and efficiency considerations

**Critical Requirements:**
- Complete prompt text in clearly marked section
- Clear instructions with step-by-step guidance
- Output format specification and examples
- Error handling and edge case coverage
- Safety considerations and ethical guidelines

---

## Documentation & Engineering Agents

### `java-documentation-specialist`

**Description**: Expert Java documentation specialist creating comprehensive technical documentation from Spring Boot codebases.

**When to use:**
- System documentation creation
- Architecture guides
- API documentation
- Technical deep-dives
- Project onboarding documentation
- Release documentation

**Model**: Sonnet

**Key Capabilities:**

1. **Java & Spring Boot Documentation**
   - Spring Boot applications comprehensive docs
   - JPA & Database documentation
   - REST API documentation with OpenAPI
   - Spring Security documentation
   - Configuration management docs

2. **Modern Java Documentation**
   - Java 16+ features (records, pattern matching)
   - Immutability patterns
   - Stream API documentation
   - Optional usage documentation
   - Exception handling patterns

3. **Architecture Documentation**
   - Clean Architecture layer separation
   - DDD bounded contexts and aggregates
   - Microservices architecture
   - Hexagonal architecture
   - SOLID principles documentation

4. **API & Integration Documentation**
   - REST API design documentation
   - OpenAPI/Swagger specifications
   - Spring MVC patterns
   - Integration patterns
   - Message queue documentation

5. **Database & Persistence Documentation**
   - JPA entity documentation
   - Spring Data JPA patterns
   - Database schema documentation
   - Transaction management
   - Database testing patterns

**Skills Integration**: Automatically invokes 40+ Spring Boot, testing, LangChain4j, and AWS skills for complete documentation.

**Example Interactions:**

```bash
# API documentation
"Generate comprehensive API documentation for this Spring Boot REST service"

# Architecture documentation
"Create architecture documentation for our microservices-based Java application"

# Security documentation
"Document our Spring Security implementation with authentication flows"

# Database documentation
"Generate database schema and JPA entity relationship documentation"

# Deployment documentation
"Create deployment documentation including Docker, Kubernetes, and CI/CD"
```

**Documentation Deliverables:**

1. **Project Overview & Architecture**
   - Executive summary
   - System architecture diagrams
   - Architecture Decision Records (ADRs)
   - Technology choices and rationale

2. **API Documentation**
   - OpenAPI specification
   - Endpoint reference with examples
   - Data models with validation rules
   - Authentication guide

3. **Developer Documentation**
   - Setup guide
   - Code organization and standards
   - Database schema and migrations
   - Testing guide

4. **Operations Documentation**
   - Deployment guide
   - Monitoring & health checks
   - Security procedures
   - Performance tuning

---

### `java-tutorial-engineer`

**Description**: Expert Java tutorial engineer specializing in Spring Boot and LangChain4j educational content.

**When to use:**
- Creating onboarding guides
- Feature tutorials
- Concept explanations
- Learning path development
- Hands-on training materials
- Educational content creation

**Model**: Sonnet

**Key Capabilities:**

1. **Java Fundamentals Tutorials**
   - Java basics (OOP, collections, exceptions)
   - Modern Java features (records, streams, pattern matching)
   - Concurrency basics
   - File I/O and resource management

2. **Spring Boot Tutorial Mastery**
   - Getting started tutorials
   - Dependency injection patterns
   - Web development with @RestController
   - Data persistence with JPA
   - Configuration management
   - Testing strategies
   - Actuator monitoring

3. **LangChain4j AI Tutorial Specialization**
   - AI Services creation
   - Chat memory management
   - Prompt engineering
   - RAG implementation
   - Tool integration
   - Vector stores setup
   - Model integration

4. **Advanced Java Topics**
   - Microservices tutorials
   - Security with Spring Security
   - Performance optimization
   - Cloud integration
   - Event-driven architecture
   - API documentation

**Tutorial Structure Patterns:**

- **Beginner Tutorials** (15-45 minutes): Quick starts with step-by-step guidance
- **Intermediate Tutorials** (1-3 hours): Comprehensive guides with modules
- **Advanced Tutorials** (4+ hours): Enterprise-grade applications with best practices
- **Workshop Series** (Multi-day): Complete learning paths with capstone projects

**Skills Integration**: Automatically invokes 40+ Spring Boot, testing, LangChain4j, and AWS skills for tutorial creation.

**Example Interactions:**

```bash
# Beginner tutorial
"Create a tutorial for building your first Spring Boot REST API"

# Intermediate tutorial
"Write a tutorial on implementing RAG with LangChain4j and Spring Boot"

# Advanced tutorial
"Create an enterprise-grade tutorial for microservices with Spring Cloud"

# Workshop series
"Design a 4-day workshop on AI-powered applications with Spring Boot"

# Feature tutorial
"Create a hands-on tutorial for implementing JWT authentication"
```

**Pedagogical Principles:**
1. **Progressive Learning**: Foundation first, build complexity gradually
2. **Hands-On Approach**: Code-first with practical examples
3. **Multi-Level Support**: Beginner, intermediate, advanced paths
4. **Real-World Examples**: Practical scenarios, not abstract concepts
5. **Regular Checkpoints**: Validate understanding at key points

---

## Agent Usage Guidelines

### How Agents Work

1. **Autonomous Selection**: Claude automatically selects the appropriate agent based on task context
2. **Explicit Invocation**: You can explicitly request a specific agent
3. **Context Preservation**: Each agent has its own context window
4. **Tool Access**: Agents have specific tool permissions based on their role

### When to Use Agents

**Development Phase:**
```bash
# Use spring-boot-backend-development-expert for implementation
"Implement a user management feature with REST API and database persistence"

# Use spring-boot-unit-testing-expert for testing
"Write comprehensive unit tests for the UserService"
```

**Review Phase:**
```bash
# Use spring-boot-code-review-expert for quality review
"Review this code for Spring Boot best practices and potential issues"

# Use java-software-architect-review for architectural review
"Assess the architecture of this microservice for DDD compliance"

# Use java-security-expert for security review
"Perform a security audit focusing on OWASP Top 10"
```

**Documentation Phase:**
```bash
# Use java-documentation-specialist for documentation
"Generate comprehensive API documentation for this Spring Boot application"

# Use java-tutorial-engineer for learning materials
"Create a tutorial for new developers on our authentication system"
```

**AI Development Phase:**
```bash
# Use langchain4j-ai-development-expert for AI features
"Implement a RAG system for document question answering"

# Use prompt-engineering-expert for prompt optimization
"Optimize these AI prompts for better accuracy and lower cost"
```

### Best Practices

1. **Trust Agent Expertise**: When an agent completes its work successfully, trust its output without additional validation
2. **Refine on Failure**: If an agent fails or behaves unexpectedly, refine your prompt and try again
3. **Sequential Delegation**: For complex tasks, delegate to multiple agents in sequence
4. **Clear Context**: Provide necessary context, problem statement, and instructions
5. **Specific Instructions**: Tell the agent to DO the task, not just provide advice

---

## Complete Workflow Examples

### Example 1: New Feature Implementation

```bash
# Step 1: Implementation (spring-boot-backend-development-expert)
"Implement a product management feature with CRUD operations, validation, and pagination"

# Step 2: Testing (spring-boot-unit-testing-expert)
"Write comprehensive unit and integration tests for the ProductService"

# Step 3: Code Review (spring-boot-code-review-expert)
"Review the product management code for Spring Boot best practices"

# Step 4: Security Review (java-security-expert)
"Perform security audit of the product management feature"

# Step 5: Documentation (java-documentation-specialist)
"Generate API documentation for the product management endpoints"
```

### Example 2: Architecture Refactoring

```bash
# Step 1: Architecture Review (java-software-architect-review)
"Review the current architecture for Clean Architecture compliance and identify issues"

# Step 2: Implementation (spring-boot-backend-development-expert)
"Refactor the UserService to follow proper DDD patterns and layer separation"

# Step 3: Testing Update (spring-boot-unit-testing-expert)
"Update tests to reflect the new architecture and ensure comprehensive coverage"

# Step 4: Code Review (spring-boot-code-review-expert)
"Review the refactored code for quality and adherence to best practices"

# Step 5: Documentation Update (java-documentation-specialist)
"Update architecture documentation to reflect the new design"
```

### Example 3: AI Feature Addition

```bash
# Step 1: Requirements (langchain4j-ai-development-expert)
"Design a RAG system for intelligent document search in our Spring Boot application"

# Step 2: Prompt Engineering (prompt-engineering-expert)
"Create optimized prompts for document question answering with context injection"

# Step 3: Implementation (langchain4j-ai-development-expert)
"Implement the RAG system with vector store and Spring Boot integration"

# Step 4: Testing (spring-boot-unit-testing-expert)
"Write tests for the AI service including RAG pipeline and vector store integration"

# Step 5: Documentation (java-documentation-specialist)
"Generate documentation for the AI-powered search feature"

# Step 6: Tutorial (java-tutorial-engineer)
"Create a tutorial for developers on how to use and extend the AI search feature"
```

### Example 4: Security Hardening

```bash
# Step 1: Security Audit (java-security-expert)
"Perform comprehensive security audit covering OWASP Top 10 and DevSecOps practices"

# Step 2: Implementation (spring-boot-backend-development-expert)
"Implement security fixes including input validation, JWT improvements, and CORS configuration"

# Step 3: Security Review (java-security-expert)
"Verify all security fixes have been properly implemented"

# Step 4: Testing (spring-boot-unit-testing-expert)
"Add security-focused tests for authentication, authorization, and input validation"

# Step 5: Documentation (java-documentation-specialist)
"Update security documentation with new authentication flows and best practices"
```

---

## References

- [Contributing Guide](../CONTRIBUTING.md)
- [README](../README.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-08  
