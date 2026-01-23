# Complete Guide to Developer Kit Agents

This guide provides comprehensive documentation for all 36 specialized agents available in the Developer Kit, organized by development domain with descriptions, use cases, and integration patterns.

---

## Table of Contents

1. [General Purpose Agents](#general-purpose-agents)
2. [Java/Spring Boot Development Agents](#javaspring-boot-development-agents)
3. [TypeScript/Node.js Development Agents](#typescriptnodejs-development-agents)
4. [NestJS Backend Development Agents](#nestjs-backend-development-agents)
5. [React/Frontend Development Agents](#reactfrontend-development-agents)
6. [Python Development Agents](#python-development-agents)
7. [AWS Architecture & DevOps Agents](#aws-architecture--devops-agents)
8. [AI & LangChain4J Agents](#ai--langchain4j-agents)
9. [Documentation & Specialized Agents](#documentation--specialized-agents)
10. [Agent Usage Guidelines](#agent-usage-guidelines)

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

### `general-code-explorer`

**File**: `agents/general-code-explorer.md`

**Purpose**: Deeply analyzes existing codebase features by tracing execution paths, mapping architecture layers, understanding patterns and abstractions, and documenting dependencies.

**When to use:**
- Understanding existing features before modification
- Mapping codebase architecture and patterns
- Tracing data flow through complex systems
- Documenting legacy code implementations
- Analyzing performance bottlenecks in execution paths
- Creating technical documentation from code analysis

**Key Capabilities:**
- Feature discovery and entry point identification
- Complete execution flow tracing with data transformations
- Architecture layer mapping
- Pattern and abstraction identification
- Dependency analysis (internal and external)
- Cross-cutting concerns documentation

---

### `general-code-reviewer`

**File**: `agents/general-code-reviewer.md`

**Purpose**: Reviews code for bugs, logic errors, security vulnerabilities, and quality issues using confidence-based filtering to report only high-priority issues that truly matter.

**When to use:**
- Code quality assurance before commits
- Pull request reviews
- Identifying critical bugs and security issues
- Performance bottleneck detection
- Architectural anti-pattern identification
- Best practices compliance verification

**Key Capabilities:**
- Bug detection (logic errors, null handling, race conditions)
- Security vulnerability assessment
- Performance and scalability analysis
- Code quality evaluation (DRY, SOLID, complexity)
- Confidence-based issue filtering

---

### `general-debugger`

**File**: `agents/general-debugger.md`

**Purpose**: Expert debugger for root cause analysis. Traces execution paths, analyzes stack traces, identifies failure points, and proposes targeted fixes with minimal changes.

**When to use:**
- Debugging errors and unexpected behavior
- Test failure analysis
- Stack trace interpretation
- Root cause identification
- Performance issue diagnosis

**Key Capabilities:**
- Execution path tracing
- Failure point identification
- Minimal targeted fixes
- Stack trace analysis

---

### `general-software-architect`

**File**: `agents/general-software-architect.md`

**Purpose**: Designs comprehensive feature architectures by analyzing existing codebase patterns and providing detailed implementation blueprints with specific files, components, data flows, and build sequences.

**When to use:**
- Designing new features from scratch
- Major refactoring initiatives
- System integration planning
- Performance optimization strategies
- Technology stack decisions
- Architectural debt assessment

**Key Capabilities:**
- Codebase pattern analysis
- Complete architecture design
- Component design with interfaces
- Data flow mapping
- Build sequence planning
- Trade-off analysis

---

### `general-refactor-expert`

**File**: `agents/general-refactor-expert.md`

**Purpose**: Expert code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and language-specific best practices.

**When to use:**
- Code quality improvements
- Refactoring after feature implementation
- Legacy code modernization
- Technical debt reduction
- Performance optimization
- Best practices alignment

**Key Capabilities:**
- Code quality improvement
- SOLID principles application
- Design pattern implementation
- Performance optimization
- Readability enhancement

---

## Java/Spring Boot Development Agents

### `spring-boot-backend-development-expert`

**File**: `agents/spring-boot-backend-development-expert.md`

**Purpose**: Expert Spring Boot backend developer specializing in feature implementation, architecture, and best practices.

**When to use:**
- Spring Boot development tasks
- REST API implementation
- Backend architecture decisions
- Feature implementation guidance
- Spring framework best practices

---

### `spring-boot-code-review-expert`

**File**: `agents/spring-boot-code-review-expert.md`

**Purpose**: Expert Spring Boot code reviewer specializing in Java best practices, patterns, and architectural issues. Reviews code for quality, maintainability, and adherence to Spring Boot conventions.

**When to use:**
- Spring Boot code review
- Pull request assessment
- Architecture validation
- Best practices verification
- Code quality improvement

---

### `spring-boot-unit-testing-expert`

**File**: `agents/spring-boot-unit-testing-expert.md`

**Purpose**: Expert in unit testing with Spring Test, JUnit 5, and Mockito for Spring Boot applications. Specializes in comprehensive test strategies, test architecture, and testing best practices.

**When to use:**
- Writing Spring Boot unit tests
- Test coverage improvement
- Testing strategy review
- Test architecture design
- Mockito and JUnit 5 patterns

---

### `java-software-architect-review`

**File**: `agents/java-software-architect-review.md`

**Purpose**: Expert Java software architect specializing in Clean Architecture, Domain-Driven Design (DDD), and Spring Boot patterns. Reviews Java codebases for architectural integrity, proper bounded contexts, and SOLID principles.

**When to use:**
- Java architectural decisions
- DDD modeling and implementation
- Clean Architecture reviews
- Architectural refactoring
- System design validation

---

### `java-refactor-expert`

**File**: `agents/java-refactor-expert.md`

**Purpose**: Expert Java and Spring Boot code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and Spring Boot best practices.

**When to use:**
- Java code refactoring
- Spring Boot code quality improvements
- Legacy Java modernization
- Design pattern application
- Performance optimization

---

### `java-security-expert`

**File**: `agents/java-security-expert.md`

**Purpose**: Expert security auditor specializing in DevSecOps, comprehensive cybersecurity, and compliance frameworks. Masters vulnerability assessment, threat modeling, secure authentication (OAuth2/OIDC), OWASP standards, cloud security, and security automation.

**When to use:**
- Java/Spring Boot security audits
- Vulnerability assessment
- DevSecOps implementation
- Compliance framework integration (GDPR, HIPAA, SOC2)
- Incident response planning
- Authentication/authorization design

---

### `java-documentation-specialist`

**File**: `agents/java-documentation-specialist.md`

**Purpose**: Expert Java documentation specialist creating comprehensive technical documentation from Spring Boot codebases. Analyzes architecture, design patterns, and implementation details to produce complete project documentation.

**When to use:**
- Java project documentation
- API documentation generation
- Architecture guide creation
- Technical manual writing
- Design pattern documentation
- System documentation

---

### `java-tutorial-engineer`

**File**: `agents/java-tutorial-engineer.md`

**Purpose**: Expert Java tutorial engineer specializing in Spring Boot and LangChain4j educational content. Creates step-by-step tutorials and hands-on learning experiences for Java developers.

**When to use:**
- Onboarding guides
- Feature tutorials
- Concept explanations
- Learning paths
- Educational content creation
- Knowledge base articles

---

## TypeScript/Node.js Development Agents

### `typescript-refactor-expert`

**File**: `agents/typescript-refactor-expert.md`

**Purpose**: Expert TypeScript and modern JavaScript code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and TypeScript best practices.

**When to use:**
- TypeScript code refactoring
- Modern JavaScript patterns
- Type safety improvements
- Code quality enhancement
- Legacy code modernization
- Performance optimization

---

### `typescript-security-expert`

**File**: `agents/typescript-security-expert.md`

**Purpose**: Expert security auditor specializing in TypeScript/Node.js application security, DevSecOps, and comprehensive cybersecurity. Masters vulnerability assessment, threat modeling, secure authentication (JWT/OAuth2), OWASP standards, and TypeScript-specific security patterns.

**When to use:**
- TypeScript/Node.js security audits
- Express, NestJS, Next.js security review
- Vulnerability assessment
- DevSecOps integration
- Authentication design
- OWASP compliance

---

### `typescript-documentation-expert`

**File**: `agents/typescript-documentation-expert.md`

**Purpose**: Expert TypeScript documentation specialist creating comprehensive technical documentation for TypeScript projects. Analyzes architecture, design patterns, and implementation details to produce complete project documentation.

**When to use:**
- TypeScript project documentation
- API documentation
- Architecture guides
- ADR (Architecture Decision Record) creation
- Technical manuals
- Design documentation

---

### `typescript-software-architect-review`

**File**: `agents/typescript-software-architect-review.md`

**Purpose**: Expert TypeScript software architect specializing in Clean Architecture, Domain-Driven Design (DDD), Node.js patterns, and modern TypeScript frameworks. Reviews TypeScript codebases for architectural integrity.

**When to use:**
- TypeScript architectural decisions
- Node.js system design
- DDD implementation
- Express/Fastify/NestJS architecture
- System design validation
- Architectural refactoring

---

## NestJS Backend Development Agents

### `nestjs-backend-development-expert`

**File**: `agents/nestjs-backend-development-expert.md`

**Purpose**: Expert NestJS backend developer specializing in feature implementation, architecture, and best practices.

**When to use:**
- NestJS development tasks
- REST API implementation
- Backend architecture decisions
- Feature implementation
- NestJS best practices

---

### `nestjs-code-review-expert`

**File**: `agents/nestjs-code-review-expert.md`

**Purpose**: Expert NestJS code reviewer specializing in TypeScript best practices, NestJS patterns, and architectural issues. Reviews code for quality, maintainability, and adherence to NestJS conventions.

**When to use:**
- NestJS code review
- Pull request assessment
- Architecture validation
- Best practices verification
- NestJS pattern compliance

---

### `nestjs-unit-testing-expert`

**File**: `agents/nestjs-unit-testing-expert.md`

**Purpose**: Expert in unit testing with NestJS, Jest, and testing utilities for TypeScript applications. Specializes in comprehensive test strategies, test architecture, and testing best practices.

**When to use:**
- NestJS unit testing
- Jest configuration
- Test coverage improvement
- Testing strategy design
- Mock and fixture creation

---

### `nestjs-database-expert`

**File**: `agents/nestjs-database-expert.md`

**Purpose**: NestJS database specialist with expertise in Drizzle ORM setup, schema design, migrations, queries, transactions, and database operations.

**When to use:**
- NestJS database development
- Drizzle ORM setup and configuration
- Database schema design
- Migration creation
- Query optimization
- Transaction management

---

### `nestjs-security-expert`

**File**: `agents/nestjs-security-expert.md`

**Purpose**: NestJS security specialist focusing on authentication, authorization, JWT implementation, guards, security middleware, and security best practices.

**When to use:**
- NestJS authentication implementation
- Authorization setup
- JWT configuration
- Guard and middleware creation
- OAuth/SSO implementation
- Security vulnerability fixes

---

### `nestjs-testing-expert`

**File**: `agents/nestjs-testing-expert.md`

**Purpose**: NestJS testing specialist focusing on unit tests, integration tests, end-to-end tests, test database setup, mocking strategies, and testing best practices.

**When to use:**
- NestJS test infrastructure setup
- Integration test creation
- End-to-end test development
- Test database configuration
- Mocking strategies
- Testing best practices

---

## React/Frontend Development Agents

### `react-frontend-development-expert`

**File**: `agents/react-frontend-development-expert.md`

**Purpose**: Expert React frontend developer specializing in React 19, Vite, TypeScript, Tailwind CSS, and shadcn/ui. Builds modern, responsive, and accessible React applications.

**When to use:**
- React component development
- Frontend feature implementation
- State management design
- UI/UX implementation
- React 19 patterns
- Vite configuration

---

### `react-software-architect-review`

**File**: `agents/react-software-architect-review.md`

**Purpose**: Expert React software architect specializing in frontend architecture, component design patterns, state management strategies, and performance optimization. Reviews React codebases for architectural integrity across React 19, Next.js, and Remix.

**When to use:**
- React architectural decisions
- Component design patterns
- State management architecture
- Frontend performance optimization
- Scalable UI architecture
- Design system creation

---

### `expo-react-native-development-expert`

**File**: `agents/expo-react-native-development-expert.md`

**Purpose**: Expert Expo and React Native mobile developer specializing in cross-platform mobile app development with Expo SDK 54, React Native 0.81, React 19.1, TypeScript, and modern mobile UI patterns.

**When to use:**
- Expo/React Native development
- Cross-platform mobile apps
- Native module integration
- Mobile UI implementation
- Navigation setup
- Performance optimization for mobile
- iOS/Android deployment

---

## Python Development Agents

### `python-code-review-expert`

**File**: `agents/python-code-review-expert.md`

**Purpose**: Expert Python code reviewer specializing in code quality, security, performance, and Pythonic best practices. Reviews Python codebases using confidence-based filtering.

**When to use:**
- Python code review
- Pull request assessment
- Code quality improvement
- Security vulnerability detection
- Performance analysis
- Best practices verification

---

### `python-refactor-expert`

**File**: `agents/python-refactor-expert.md`

**Purpose**: Expert Python code refactoring specialist. Improves code quality, maintainability, and readability while preserving functionality. Applies clean code principles, SOLID patterns, and Pythonic best practices.

**When to use:**
- Python code refactoring
- Code quality improvement
- Pythonic pattern adoption
- Legacy Python modernization
- Design pattern application
- Performance optimization

---

### `python-security-expert`

**File**: `agents/python-security-expert.md`

**Purpose**: Expert security auditor specializing in Python application security, DevSecOps, and compliance frameworks. Masters vulnerability assessment, threat modeling, secure authentication (OAuth2/JWT), OWASP standards, and security automation.

**When to use:**
- Python security audits
- Vulnerability assessment
- DevSecOps integration
- Compliance implementation (GDPR, HIPAA)
- Authentication design
- Security automation

---

### `python-software-architect-expert`

**File**: `agents/python-software-architect-expert.md`

**Purpose**: Expert Python software architect specializing in Clean Architecture, Domain-Driven Design (DDD), and modern Python patterns. Reviews Python codebases for architectural integrity, proper module organization, and SOLID principles.

**When to use:**
- Python architectural decisions
- DDD implementation
- Clean Architecture design
- System design and planning
- Module organization
- Architectural refactoring

---

## AWS Architecture & DevOps Agents

### `aws-architecture-review-expert`

**File**: `agents/aws-architecture-review-expert.md`

**Purpose**: AWS architecture reviewer specializing in Well-Architected Framework, security, cost optimization, and Infrastructure as Code quality assessment.

**When to use:**
- AWS architecture review
- Well-Architected Framework compliance
- Cost optimization analysis
- Security best practices
- CloudFormation/IaC quality review
- Multi-region deployment planning

---

### `aws-cloudformation-devops-expert`

**File**: `agents/aws-cloudformation-devops-expert.md`

**Purpose**: Expert AWS DevOps engineer specializing in CloudFormation templates, Infrastructure as Code (IaC), and AWS deployment automation. Masters nested stacks, cross-stack references, custom resources, and CI/CD pipeline integration.

**When to use:**
- CloudFormation template development
- IaC best practices
- AWS infrastructure automation
- Nested stacks and cross-stack references
- Custom resources creation
- CI/CD pipeline integration
- Infrastructure testing

---

### `aws-solution-architect-expert`

**File**: `agents/aws-solution-architect-expert.md`

**Purpose**: Expert AWS Solution Architect specializing in scalable cloud architectures, Well-Architected Framework, and enterprise-grade AWS solutions. Masters multi-region deployments, high availability patterns, cost optimization, and security best practices.

**When to use:**
- AWS solution architecture
- Cloud migration strategies
- Multi-region deployment design
- High availability architecture
- Cost optimization
- Disaster recovery planning
- Enterprise-grade solution design

---

## AI & LangChain4J Agents

### `langchain4j-ai-development-expert`

**File**: `agents/langchain4j-ai-development-expert.md`

**Purpose**: Expert LangChain4j developer for building AI applications, RAG systems, ChatBots, and MCP servers. Specializes in AI services, vector stores, embeddings, and model integration patterns.

**When to use:**
- LangChain4j development
- RAG (Retrieval-Augmented Generation) implementation
- AI service design
- ChatBot development
- Vector store integration
- MCP server creation
- Model integration

---

### `prompt-engineering-expert`

**File**: `agents/prompt-engineering-expert.md`

**Purpose**: Expert prompt engineer specializing in advanced prompting techniques, LLM optimization, and AI system design. Masters chain-of-thought, constitutional AI, and production prompt strategies.

**When to use:**
- Prompt creation and optimization
- LLM behavior fine-tuning
- Chain-of-thought design
- AI system design
- Document/code analysis prompts
- Production prompt strategies
- Prompt testing and iteration

---

## Documentation & Specialized Agents

### `document-generator-expert`

**File**: `agents/document-generator-expert.md`

**Purpose**: Expert document generator specializing in creating professional technical and business documents. Produces comprehensive assessments, feature specifications, analysis reports, process documentation, and custom documents.

**When to use:**
- Technical documentation
- Security assessment documents
- Feature specification writing
- Process documentation
- Technical analysis reports
- Custom document generation
- Multi-language support (English, Italian, Spanish, French, German, Portuguese)

---

## Agent Usage Guidelines

### How to Use Agents

Agents can be invoked in multiple ways depending on your development environment:

#### In Claude Code

```
@agent-name [description or task]
```

Example:
```
@spring-boot-code-review-expert Review this controller for security issues
```

#### Using Task Tool (Programmatic)

```javascript
Task(
  description: "Review Spring Boot security",
  prompt: "Review the payment processing controller for authentication and authorization vulnerabilities",
  subagent_type: "developer-kit:spring-boot-code-review-expert"
)
```

#### In Commands

Commands automatically delegate to the appropriate agent based on the task:

```bash
/devkit.java.code-review full src/main/java
/devkit.java.security-review src/
/devkit.feature-development
```

### Best Practices

1. **Choose the Right Agent**: Select agents that match your specific domain and task
2. **Provide Context**: Give detailed descriptions of what you want analyzed
3. **Be Specific**: More specific requests lead to better results
4. **Review Output**: Always review agent recommendations before applying
5. **Combine Agents**: Use multiple agents for comprehensive analysis (e.g., code-explorer → architect → code-reviewer)
6. **Leverage Specialization**: Use domain-specific agents (Spring Boot, React, Python) for better expertise

### Agent Selection Guide

| Task | Recommended Agent |
|------|---|
| Understand existing code | `code-explorer` |
| Design new architecture | `software-architect` |
| Review code quality | `code-reviewer` or domain-specific reviewer |
| Debug errors | `debugger` |
| Refactor code | Domain-specific `refactor-expert` |
| Security audit | Domain-specific `security-expert` |
| Create documentation | `documentation-specialist` or `document-generator-expert` |
| Mobile development | `expo-react-native-development-expert` |
| AI/LangChain4j | `langchain4j-ai-development-expert` |
| Prompt optimization | `prompt-engineering-expert` |

---

## Common Workflows

### Code Review Workflow

1. **Explore**: Use `code-explorer` to understand current implementation
2. **Review**: Use domain-specific `code-review-expert` to identify issues
3. **Debug**: Use `debugger` if there are failures
4. **Refactor**: Use domain-specific `refactor-expert` to improve quality
5. **Architect**: Use `software-architect` for major redesigns

### Feature Development Workflow

1. **Architect**: Use `software-architect` to design the feature
2. **Implement**: Use domain-specific development expert
3. **Test**: Use domain-specific testing expert
4. **Review**: Use domain-specific code reviewer
5. **Document**: Use documentation specialist

### Security Review Workflow

1. **Audit**: Use domain-specific `security-expert`
2. **Assess**: Review findings and impact
3. **Fix**: Use domain-specific development expert
4. **Re-audit**: Confirm fixes with security expert

---

**Note**: For frontend-specific skills and patterns, see the [Frontend Skills Guide](guide-skills-frontend.md)
