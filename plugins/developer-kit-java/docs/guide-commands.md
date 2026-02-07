# Java Plugin Commands Guide

This guide documents all commands available in the Developer Kit Java Plugin, organized by category with brief descriptions, usage, and practical examples.

---

## Table of Contents

1. [Overview](#overview)
2. [Code Review Commands](#code-review-commands)
3. [Testing Commands](#testing-commands)
4. [Code Generation Commands](#code-generation-commands)
5. [Refactoring Commands](#refactoring-commands)
6. [Documentation Commands](#documentation-commands)
7. [Security Commands](#security-commands)
8. [Dependency Management Commands](#dependency-management-commands)
9. [Command Usage Guidelines](#command-usage-guidelines)
10. [See Also](#see-also)

---

## Overview

The Java Plugin provides specialized commands for Java and Spring Boot development, including code review, testing, code generation, refactoring, documentation, security auditing, and dependency management.

### Available Commands

- **Code Review**: 2 commands for comprehensive code and architecture review
- **Testing**: 2 commands for unit and integration test generation
- **Code Generation**: 2 commands for CRUD and documentation generation
- **Refactoring**: 2 commands for class refactoring and task generation
- **Security**: 1 command for security auditing
- **Dependency Management**: 2 commands for dependency audit and upgrades

---

## Code Review Commands

### `/developer-kit-java:devkit.java.code-review`

**Purpose**: Comprehensive code review of Java/Spring Boot applications for architecture, security, performance, and best practices.

**Usage:**
```bash
/developer-kit-java:devkit.java.code-review [full|security|performance|architecture|testing|best-practices] [path] [options]
```

**Common use cases:**
- Before creating a pull request
- After completing a feature
- Verifying code quality
- Refactoring critical components

**Examples:**
```bash
# Full review of current directory
/developer-kit-java:devkit.java.code-review full

# Security-focused review
/developer-kit-java:devkit.java.code-review security src/main/java

# Performance review of specific package
/developer-kit-java:devkit.java.code-review performance src/main/java/service
```

---

### `/developer-kit-java:devkit.java.architect-review`

**Purpose**: High-level architecture review of Java codebases focusing on design patterns, scalability, and architectural decisions.

**Usage:**
```bash
/developer-kit-java:devkit.java.architect-review [path]
```

**Common use cases:**
- Reviewing application architecture
- Validating design patterns
- Assessing scalability
- Planning refactoring efforts

**Examples:**
```bash
# Review architecture of entire project
/developer-kit-java:devkit.java.architect-review

# Review specific module
/developer-kit-java:devkit.java.architect-review src/main/java/com/example/orders
```

---

## Testing Commands

### `/developer-kit-java:devkit.java.write-unit-tests`

**Purpose**: Generate comprehensive JUnit 5 unit tests with Mockito and AssertJ patterns.

**Usage:**
```bash
/developer-kit-java:devkit.java.write-unit-tests [class-path]
```

**Common use cases:**
- Adding test coverage to new classes
- Improving existing test coverage
- Testing edge cases and boundary conditions
- Creating test doubles with Mockito

**Examples:**
```bash
# Generate tests for specific class
/developer-kit-java:devkit.java.write-unit-tests src/main/java/service/UserService.java

# Generate tests for all classes in package
/developer-kit-java:devkit.java.write-unit-tests src/main/java/repository
```

---

### `/developer-kit-java:devkit.java.write-integration-tests`

**Purpose**: Generate Spring Boot integration tests using Testcontainers for complete workflow testing.

**Usage:**
```bash
/developer-kit-java:devkit.java.write-integration-tests [test-scope]
```

**Common use cases:**
- Testing complete workflows
- Integration testing with real databases
- API endpoint testing
- Testing Spring configurations

**Examples:**
```bash
# Generate integration tests for controllers
/developer-kit-java:devkit.java.write-integration-tests controllers

# Generate integration tests for repositories
/developer-kit-java:devkit.java.write-integration-tests repositories
```

---

## Code Generation Commands

### `/developer-kit-java:devkit.java.generate-crud`

**Purpose**: Generate complete CRUD implementation (controllers, services, DTOs) from a domain class.

**Usage:**
```bash
/developer-kit-java:devkit.java.generate-crud [class-path]
```

**Common use cases:**
- Rapid CRUD development
- Scaffold REST endpoints
- Generate service layer
- Create DTOs and mappers

**Examples:**
```bash
# Generate CRUD for entity
/developer-kit-java:devkit.java.generate-crud src/main/java/model/Product.java

# Generate CRUD with custom options
/developer-kit-java:devkit.java.generate-crud src/main/java/model/Order.java --with-validation --with-audit
```

---

### `/developer-kit-java:devkit.java.generate-docs`

**Purpose**: Generate comprehensive API documentation, architecture guides, and technical manuals.

**Usage:**
```bash
/developer-kit-java:devkit.java.generate-docs [project-path]
```

**Common use cases:**
- API documentation from controllers
- Architecture documentation
- Technical manual generation
- Design documentation

**Examples:**
```bash
# Generate documentation for entire project
/developer-kit-java:devkit.java.generate-docs

# Generate API documentation
/developer-kit-java:devkit.java.generate-docs --type=api

# Generate architecture guide
/developer-kit-java:devkit.java.generate-docs --type=architecture
```

---

## Refactoring Commands

### `/developer-kit-java:devkit.java.refactor-class`

**Purpose**: Intelligent refactoring with Clean Architecture, DDD patterns, and Spring Boot best practices.

**Usage:**
```bash
/developer-kit-java:devkit.java.refactor-class [class-path] [cleanup|architecture|performance|security|testing|comprehensive]
```

**Common use cases:**
- Refactoring legacy code
- Applying clean code principles
- Implementing design patterns
- Improving testability

**Examples:**
```bash
# Comprehensive refactoring
/developer-kit-java:devkit.java.refactor-class src/main/java/service/LegacyService.java comprehensive

# Architecture-focused refactoring
/developer-kit-java:devkit.java.refactor-class src/main/java/controller/OrderController.java architecture

# Cleanup refactoring
/developer-kit-java:devkit.java.refactor-class src/main/java/util/DateUtil.java cleanup
```

---

### `/developer-kit-java:devkit.java.generate-refactoring-tasks`

**Purpose**: Generate a prioritized list of refactoring tasks for codebase improvement.

**Usage:**
```bash
/developer-kit-java:devkit.java.generate-refactoring-tasks [path]
```

**Common use cases:**
- Planning refactoring efforts
- Identifying technical debt
- Prioritizing improvements
- Creating refactoring roadmap

**Examples:**
```bash
# Generate tasks for entire project
/developer-kit-java:devkit.java.generate-refactoring-tasks

# Generate tasks for specific package
/developer-kit-java:devkit.java.generate-refactoring-tasks src/main/java/service
```

---

## Documentation Commands

Documentation commands are covered under code generation. See `/developer-kit-java:devkit.java.generate-docs` above.

---

## Security Commands

### `/developer-kit-java:devkit.java.security-review`

**Purpose**: Security-focused audit for Spring Boot and Jakarta EE applications covering OWASP, CVEs, and configurations.

**Usage:**
```bash
/developer-kit-java:devkit.java.security-review [path]
```

**Common use cases:**
- Security auditing before deployment
- Identifying OWASP vulnerabilities
- Checking for CVEs in dependencies
- Reviewing authentication/authorization

**Examples:**
```bash
# Full security review
/developer-kit-java:devkit.java.security-review

# Security review of specific package
/developer-kit-java:devkit.java.security-review src/main/java/security
```

---

## Dependency Management Commands

### `/developer-kit-java:devkit.java.dependency-audit`

**Purpose**: Comprehensive dependency audit for vulnerabilities, licenses, and update recommendations.

**Usage:**
```bash
/developer-kit-java:devkit.java.dependency-audit [project-path]
```

**Common use cases:**
- Checking for vulnerable dependencies
- License compliance verification
- Identifying outdated dependencies
- Dependency health assessment

**Examples:**
```bash
# Audit all dependencies
/developer-kit-java:devkit.java.dependency-audit

# Audit with severity filter
/developer-kit-java:devkit.java.dependency-audit --severity=critical,high
```

---

### `/developer-kit-java:devkit.java.upgrade-dependencies`

**Purpose**: Upgrade dependencies with compatibility checks and conflict resolution.

**Usage:**
```bash
/developer-kit-java:devkit.java.upgrade-dependencies [options]
```

**Common use cases:**
- Upgrading Spring Boot version
- Updating security patches
- Keeping dependencies current
- Resolving dependency conflicts

**Examples:**
```bash
# Upgrade all dependencies
/developer-kit-java:devkit.java.upgrade-dependencies

# Upgrade specific dependency
/developer-kit-java:devkit.java.upgrade-dependencies --artifact=spring-boot

# Dry run to see changes
/developer-kit-java:devkit.java.upgrade-dependencies --dry-run
```

---

## Command Usage Guidelines

### How to Invoke Commands

Commands are invoked using the slash syntax in Claude Code:

```bash
/developer-kit-java:devkit.java.{command-name} [arguments]
```

### Best Practices

1. **Read command docs first**: Each command has detailed documentation
2. **Provide clear context**: Give commands the information they need
3. **Review output**: Commands generate suggestions you should review
4. **Iterate**: Use command output as starting point, refine as needed
5. **Test thoroughly**: Especially for refactoring and dependency upgrades

---

## Common Workflows

### Feature Development Workflow

```bash
# 1. Generate CRUD for new entity
/developer-kit-java:devkit.java.generate-crud src/main/java/model/Product.java

# 2. Generate unit tests
/developer-kit-java:devkit.java.write-unit-tests src/main/java/service/ProductService.java

# 3. Generate integration tests
/developer-kit-java:devkit.java.write-integration-tests controllers

# 4. Review implementation
/developer-kit-java:devkit.java.code-review full src/main/java/product/

# 5. Security review
/developer-kit-java:devkit.java.security-review src/main/java/product/
```

### Code Review Workflow

```bash
# 1. Run comprehensive review
/developer-kit-java:devkit.java.code-review full

# 2. Run architecture review
/developer-kit-java:devkit.java.architect-review

# 3. Run security review
/developer-kit-java:devkit.java.security-review

# 4. Address critical issues

# 5. Re-review
/developer-kit-java:devkit.java.code-review full
```

### Refactoring Workflow

```bash
# 1. Generate refactoring tasks
/developer-kit-java:devkit.java.generate-refactoring-tasks

# 2. Review and prioritize tasks

# 3. Refactor specific classes
/developer-kit-java:devkit.java.refactor-class src/main/java/service/LegacyService.java comprehensive

# 4. Update tests
/developer-kit-java:devkit.java.write-unit-tests src/main/java/service/RefactoredService.java

# 5. Review refactored code
/developer-kit-java:devkit.java.code-review architecture
```

### Dependency Management Workflow

```bash
# 1. Audit dependencies
/developer-kit-java:devkit.java.dependency-audit

# 2. Review vulnerabilities and licenses

# 3. Plan upgrades

# 4. Upgrade dependencies
/developer-kit-java:devkit.java.upgrade-dependencies --dry-run

# 5. Test after upgrade
# Run full test suite

# 6. Re-audit
/developer-kit-java:devkit.java.dependency-audit
```

---

## Command Selection Guide

| Task | Recommended Command |
|------|---------------------|
| Review code quality | `/developer-kit-java:devkit.java.code-review` |
| Review architecture | `/developer-kit-java:devkit.java.architect-review` |
| Security audit | `/developer-kit-java:devkit.java.security-review` |
| Write unit tests | `/developer-kit-java:devkit.java.write-unit-tests` |
| Write integration tests | `/developer-kit-java:devkit.java.write-integration-tests` |
| Generate CRUD | `/developer-kit-java:devkit.java.generate-crud` |
| Generate documentation | `/developer-kit-java:devkit.java.generate-docs` |
| Refactor class | `/developer-kit-java:devkit.java.refactor-class` |
| Plan refactoring | `/developer-kit-java:devkit.java.generate-refactoring-tasks` |
| Audit dependencies | `/developer-kit-java:devkit.java.dependency-audit` |
| Upgrade dependencies | `/developer-kit-java:devkit.java.upgrade-dependencies` |

---

## See Also

- [Java Agents Guide](./guide-agents.md) - Java plugin agents
- [Spring Boot Skills Guide](./guide-skills-spring-boot.md) - Spring Boot skills
- [JUnit Test Skills Guide](./guide-skills-junit-test.md) - JUnit testing skills
- [LangChain4J Skills Guide](./guide-skills-langchain4j.md) - LangChain4J skills
- [AWS Java Skills Guide](./guide-skills-aws-java.md) - AWS Java SDK skills
- [Core Command Guide](../developer-kit-core/docs/guide-commands.md) - All commands across plugins
