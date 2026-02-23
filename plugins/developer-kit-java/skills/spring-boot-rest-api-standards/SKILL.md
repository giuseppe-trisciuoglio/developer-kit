---
name: spring-boot-rest-api-standards
description: Provides REST API design standards and best practices for Spring Boot projects. Use when creating or reviewing REST endpoints, DTOs, error handling, pagination, security headers, HATEOAS and architecture patterns.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot REST API Standards

## Overview

Use this skill as the entry point for designing consistent, production-ready REST APIs in Spring Boot 3.x. It focuses on resource modeling, HTTP semantics, validation, error contracts, pagination, and security defaults.

## When to Use

Use when you are:
- Defining new controller endpoints or versioned API routes.
- Reviewing DTO contracts, validation, and response models.
- Standardizing exception handling and status codes.
- Adding pagination/filtering/sorting behavior.
- Hardening APIs with security headers and CORS policy.

## Instructions

1. Model URLs as resources (plural nouns, versioned base path).
2. Assign correct HTTP methods and status codes per operation.
3. Keep controllers thin; move business logic to services/use cases.
4. Use request/response DTOs and validate all external input.
5. Centralize exceptions in `@RestControllerAdvice` with one error schema.
6. Add pagination and filter contracts for list endpoints.
7. Apply security headers and explicit CORS configuration.
8. Add tests for success, validation, and error paths.

## Examples

### Example 1: Create resource with `201 Created`

```java
@PostMapping("/v1/users")
public ResponseEntity<UserResponse> create(@Valid @RequestBody CreateUserRequest request) {
    UserResponse created = userService.create(request);
    URI location = ServletUriComponentsBuilder.fromPath("/v1/users/{id}")
            .buildAndExpand(created.id())
            .toUri();
    return ResponseEntity.created(location).body(created);
}
```

See complete references:
- [Examples](references/examples.md)
- [Architecture patterns](references/architecture-patterns.md)
- [HTTP reference](references/http-reference.md)
- [Pagination and filtering](references/pagination-and-filtering.md)
- [Security headers](references/security-headers.md)
- [Spring Web annotations](references/spring-web-annotations.md)

## Best Practices

- Prefer immutable DTOs (Java records where practical).
- Return `201 Created` with `Location` for POST resource creation.
- Keep API error payloads stable across endpoints.
- Use constructor injection only.
- Document defaults for page size, sort, and filter semantics.

## Constraints and Warnings

- Do not expose JPA entities directly from controllers.
- Do not place persistence logic in controllers.
- Avoid ambiguous status codes and inconsistent error formats.
- Be explicit about backward compatibility for versioned APIs.
- Avoid permissive CORS and wildcard origins in production.

## References

- [Architecture Patterns](references/architecture-patterns.md)
- [Examples](references/examples.md)
- [HTTP Reference](references/http-reference.md)
- [Pagination and Filtering](references/pagination-and-filtering.md)
- [Security Headers](references/security-headers.md)
- [Spring Web Annotations](references/spring-web-annotations.md)
- [Additional references](references/references.md)
