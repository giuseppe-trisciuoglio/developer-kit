---
description: Generates complete CRUD implementation for a Spring Boot domain class using spring-boot-crud-patterns skill. Use when creating new domain entities with REST endpoints.
argument-hint: "[domain-class-name]"
allowed-tools: Read, Write, Bash
model: inherit
---

# Generate CRUD Implementation

You are a Spring Boot CRUD generation specialist. Your task is to generate a complete CRUD implementation for the domain class "$1" using the **spring-boot-crud-patterns** skill.

## Execution Steps

1. **Analyze Domain Class**
   - Read the domain class file for "$1" if it exists
   - Extract entity properties, relationships, and validation constraints
   - Identify primary key type and generation strategy

2. **Invoke `spring-boot-crud-patterns` Skill**
   - Use the `spring-boot-crud-patterns` skill to generate all CRUD components
   - Pass the domain class "$1" as the aggregate to be implemented
   - Follow the feature-based architecture pattern defined in the skill

3. **Generate Complete CRUD Stack**
   
   The skill will create the following structure for "$1":
   
   ```
   /$1/
   ├── domain/
   │   ├── model/$1.java              # Domain aggregate (if not exists)
   │   └── repository/$1Repository.java # Domain port interface
   ├── application/
   │   ├── service/$1Service.java     # Use case service (@Service)
   ├── presentation/
   │   ├── dto/
   │   │    ├── $1Request.java         # Create/Update request DTO
   │   │    └── $1Response.java        # Response DTO
   │   └── rest/
   │       ├── $1Controller.java      # REST controller
   │       └── $1Mapper.java          # DTO mapper
   └── infrastructure/
       └── persistence/
           ├── $1Entity.java          # JPA entity
           ├── $1JpaRepository.java   # Spring Data repository
           └── $1RepositoryAdapter.java # Domain adapter
   ```

4. **Implementation Guidelines**
   
   Apply these patterns from the skill:
   - ✅ Constructor injection only (no field injection)
   - ✅ Java records for immutable DTOs
   - ✅ @Valid annotation for request validation
   - ✅ ResponseEntity with proper HTTP status codes:
     * 201 Created for POST
     * 200 OK for GET/PUT/PATCH
     * 204 No Content for DELETE
   - ✅ `@Transactional `on service methods
   - ✅ Pagination support for list endpoints
   - ✅ Proper error handling with ResponseStatusException

5. **Generate Tests**
   
   Create corresponding test files:
   - Unit tests for domain logic
   - Service tests with Mockito
   - Controller tests with `@WebMvcTest`
   - Repository integration tests with `@DataJpaTest` and Testcontainers

6. **Validation**
   
   After generation:
   - Verify all files are created in the correct feature structure
   - Check that imports and package declarations are correct
   - Ensure no circular dependencies exist
   - Validate that DTOs don't expose JPA entities directly

## Examples

```bash
# Generate CRUD for Product entity
/developer-kit-java:devkit.java.generate-crud Product

# Generate CRUD for User entity
/developer-kit-java:devkit.java.generate-crud User

# Generate CRUD for Order entity
/developer-kit-java:devkit.java.generate-crud Order
```

## Output Summary

After completion, provide:
1. List of all generated files with their paths
2. REST API endpoints created (with HTTP methods and URLs)
3. Next steps for the developer (e.g., add migration, configure database)
4. Any warnings or recommendations

---

**Note**: This command leverages the `spring-boot-crud-patterns` skill. Make sure the skill is available and the project has the required Spring Boot dependencies (spring-boot-starter-web, spring-boot-starter-data-jpa, validation).

## Execution Instructions

**Agent Selection**: To execute this task, use the following agent with fallback:
- Primary: `spring-boot-backend-development-expert`
- If not available: Use `developer-kit:spring-boot-backend-development-expert` or fallback to `general-purpose` agent with `spring-boot-crud-patterns` skill

## Overview

Generates complete CRUD implementation for a Spring Boot domain class using spring-boot-crud-patterns skill. Use when creating new domain entities with REST endpoints.


## Usage

```
/devkit.java.generate-crud $ARGUMENTS
```

## Arguments

| Argument | Description |
|----------|-------------|
| `$ARGUMENTS` | Combined arguments passed to the command |
