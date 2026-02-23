---
name: spring-boot-crud-patterns
description: Provides repeatable CRUD workflows for Spring Boot 3 services with Spring Data JPA and feature-focused architecture. Use when modeling aggregates, repositories, controllers, and DTOs for REST APIs.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot CRUD Patterns

## Overview

Use this skill to implement maintainable CRUD features in Spring Boot 3.x with clear boundaries across domain, application, infrastructure, and presentation layers.

## When to Use

Use when you need to:
- Build create/read/update/delete workflows backed by Spring Data JPA.
- Standardize feature package layout and repository adapters.
- Add DTO mapping, request validation, and pagination.
- Review transaction boundaries and CRUD endpoint behavior.

## Instructions

1. Create a feature package with `domain`, `application`, `infrastructure`, and `presentation`.
2. Model domain behavior first; keep business rules out of controllers.
3. Define repository ports in domain and adapters in infrastructure.
4. Implement application services with constructor injection and `@Transactional`.
5. Use request/response DTOs with Jakarta validation annotations.
6. Expose REST endpoints with consistent status codes and error handling.
7. Add tests: domain unit tests plus persistence/API integration tests.

## Examples

### Example 1: Basic create endpoint

```java
@PostMapping
public ResponseEntity<ProductResponse> create(@Valid @RequestBody ProductCreateRequest request) {
    ProductResponse created = productService.create(request);
    URI location = ServletUriComponentsBuilder.fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(created.id())
            .toUri();
    return ResponseEntity.created(location).body(created);
}
```

- [CRUD reference](references/crud-reference.md)
- [Product feature examples](references/examples-product-feature.md)
- [Generator usage](references/generator-usage.md)
- [Spring official docs pointers](references/spring-official-docs.md)

## Best Practices

- Prefer immutable DTOs and explicit mapper classes.
- Use `ddl-auto=validate` for non-local environments.
- Keep controllers thin and deterministic.
- Use pagination defaults and document them.
- Log create/update/delete actions with stable identifiers.

## Constraints and Warnings

- Do not expose persistence entities directly in API responses.
- Avoid field injection and deprecated Spring APIs.
- Do not mix unrelated feature concerns in one package.
- Ensure schema migrations are applied before runtime writes.
- Validate input at boundaries to avoid leaking low-level exceptions.

## References

- [CRUD Reference](references/crud-reference.md)
- [Examples: Product Feature](references/examples-product-feature.md)
- [Generator Usage](references/generator-usage.md)
- [Spring Official Docs](references/spring-official-docs.md)
- [Generator script](scripts/generate_crud_boilerplate.py)
