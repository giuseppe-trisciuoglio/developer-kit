---
allowed-tools: Read, Bash, Grep, Glob
argument-hint: [package-path] [focus-area]
description: Comprehensive architectural review for Java applications focusing on Clean Architecture, DDD, and Spring Boot patterns
---

# Java Architectural Review

Perform a comprehensive architectural review of a Java application, focusing on Clean Architecture principles, Domain-Driven Design patterns, and Spring Boot best practices.

## Context

- Project structure: !`find . -name "*.java" -type f | head -20`
- Build system: !`ls -la | grep -E "(pom\.xml|build\.gradle|build\.gradle\.kts)"`
- Package structure: !`find . -name "*.java" -type f | grep -E "src/main/java" | head -10`
- Spring Boot configuration: !`find . -name "application*.yml" -o -name "application*.properties"`

## Review Focus Areas

$1 specifies the package path to review (optional - defaults to entire codebase):
- Examples: "com.example.users", "src/main/java/com/example/users", "users/"

$2 specifies the focus area (optional):
- `clean-architecture` - Clean Architecture layer separation
- `ddd` - Domain-Driven Design patterns
- `spring-boot` - Spring Boot specific patterns
- `security` - Security architecture
- `performance` - Performance and scalability
- `testing` - Test architecture
- `microservices` - Microservices architecture
- `all` - Complete architectural review (default)

## Architectural Review Checklist

### Clean Architecture Assessment
- **Layer Separation**: Verify proper dependency direction (domain � application � infrastructure � presentation)
- **Package Structure**: Feature-based organization with clear boundaries
- **Dependency Rules**: Check for violations of dependency inversion principle
- **Domain Purity**: Ensure domain layer has no framework dependencies
- **Interface Segregation**: Clean API design between layers

### Domain-Driven Design Evaluation
- **Bounded Contexts**: Proper context mapping and integration
- **Aggregates**: Correct aggregate root design and consistency boundaries
- **Value Objects**: Immutable value objects with Java records
- **Domain Events**: Event-driven domain modeling with Spring
- **Repositories**: Domain repositories with infrastructure adapters
- **Ubiquitous Language**: Consistent terminology across code

### Spring Boot Architecture Review
- **Dependency Injection**: Constructor injection patterns, no field injection
- **Configuration Management**: @ConfigurationProperties and profiles
- **Bean Lifecycle**: Proper scoping and lifecycle management
- **Exception Handling**: Global exception handling with @ControllerAdvice
- **Validation**: Jakarta Bean Validation integration
- **Actuator Integration**: Production-ready monitoring

### SOLID Principles Compliance
- **Single Responsibility**: Classes have one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Proper inheritance hierarchies
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Analysis Process

1. **Examine Package Structure**: Analyze the overall organization and layering
2. **Review Dependencies**: Check for proper dependency direction and coupling
3. **Assess Patterns**: Evaluate implementation of architectural patterns
4. **Identify Violations**: Find architectural debt and anti-patterns
5. **Review Spring Boot Usage**: Ensure proper framework utilization
6. **Evaluate Testability**: Assess how architecture supports testing
7. **Consider Scalability**: Review performance and scaling implications

## Your Task

Based on the context and focus area, provide a comprehensive architectural review including:

### Architecture Assessment (1-10 scale)
- Overall architectural quality score
- Specific pattern compliance scores
- Maintainability and extensibility assessment

### Identified Issues
- **Critical Issues**: Architectural violations that must be fixed
- **Warnings**: Areas that should be improved
- **Suggestions**: Optional enhancements for better architecture

### Specific Recommendations
- Concrete refactoring steps with code examples
- Priority ordering of changes (High/Medium/Low)
- Risk assessment for proposed changes
- Estimated effort for each recommendation

### Architecture Improvement Plan
- Short-term fixes (critical issues)
- Medium-term improvements (warnings)
- Long-term architectural enhancements (suggestions)

Focus on practical, actionable advice that improves the application's architecture while considering the team's current context and constraints.

## Execution Instructions

**Agent Selection**: To execute this architectural review, use the following agent with fallback:
- Primary: `java-software-architect-review`
- If not available: Use `developer-kit:java-software-architect-review` or fallback to `general-purpose` agent with `spring-boot-crud-patterns` skill

