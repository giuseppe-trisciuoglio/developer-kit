---
name: spring-boot-openapi-documentation
description: Provides patterns to generate comprehensive REST API documentation using SpringDoc OpenAPI 3.0 and Swagger UI in Spring Boot 3.x applications. Use when setting up API documentation, configuring Swagger UI, adding OpenAPI annotations, implementing security documentation, or enhancing REST endpoints with examples and schemas.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Spring Boot OpenAPI Documentation with SpringDoc

## Overview

SpringDoc OpenAPI automates generation of OpenAPI 3.0 documentation for Spring Boot projects with a Swagger UI web interface. This skill covers integrating SpringDoc into Spring Boot 3.x applications, documenting REST endpoints, securing API documentation, and customizing the specification.

## When to Use

- Set up SpringDoc OpenAPI in Spring Boot 3.x projects
- Generate OpenAPI 3.0 specifications for REST APIs
- Configure and customize Swagger UI
- Add detailed API documentation with annotations
- Document request/response models with validation
- Implement API security documentation (JWT, OAuth2)
- Support multiple API groups and versions

## Instructions

### 1. Add Dependencies and Configure

Add the correct starter dependency for your stack:
- `springdoc-openapi-starter-webmvc-ui` for Spring MVC
- `springdoc-openapi-starter-webflux-ui` for Spring WebFlux

Configure basic settings in application.yml.

### 2. Document Controllers

Use @Tag, @Operation, @ApiResponse, @Parameter annotations on REST controllers.

### 3. Document Models

Apply @Schema annotations to DTOs for field constraints, examples, and validation rules.

### 4. Configure Security

Set up security schemes (JWT Bearer, OAuth2) and apply @SecurityRequirement to protected endpoints.

### 5. Test Documentation

Access Swagger UI at /swagger-ui/index.html to verify completeness.

### 6. Customize for Production

Configure API grouping, versioning, and UI appearance.

## Examples

### Dependencies

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>last-release-version</version>
</dependency>
```

### Configuration

```yaml
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    operationsSorter: method
    tagsSorter: alpha
    tryItOutEnabled: true
  packages-to-scan: com.example.controller
  paths-to-match: /api/**
```

Access: Swagger UI at `/swagger-ui.html` (redirects to `/swagger-ui/index.html`), OpenAPI JSON at `/v3/api-docs`

### Controller Documentation

```java
@RestController
@RequestMapping("/api/books")
@Tag(name = "Book", description = "Book management APIs")
@SecurityRequirement(name = "bearer-jwt")
public class BookController {

    @Operation(summary = "Get book by ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Book found"),
        @ApiResponse(responseCode = "404", description = "Book not found")
    })
    @GetMapping("/{id}")
    public Book getBookById(@PathVariable Long id) {
        return bookService.getBookById(id);
    }
}
```

### JWT Security Scheme

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")));
}
```

### Multiple API Groups

```java
@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder().group("public").pathsToMatch("/api/public/**").build();
}

@Bean
public GroupedOpenApi adminApi() {
    return GroupedOpenApi.builder().group("admin").pathsToMatch("/api/admin/**").build();
}
```

## Best Practices

1. **Descriptive summaries** (<120 chars) and detailed descriptions
2. **Document all response codes** (2xx, 4xx, 5xx)
3. **Add examples** with @ExampleObject for realistic data
4. **Leverage JSR-303 validation** (auto-generates constraints)
5. **Use @ParameterObject** for Pageable and complex parameters
6. **Group with @Tag** by domain entities
7. **Document security** with @SecurityRequirement
8. **Hide internal endpoints** with @Hidden

## Constraints and Warnings

- Do not expose sensitive data in API examples or schema descriptions
- Large API definitions can impact Swagger UI performance; consider grouping
- Schema generation may not work with complex generic types; use explicit @Schema
- Avoid circular references in DTOs (causes infinite recursion)
- Hidden endpoints are still visible in code

## References

- [Comprehensive SpringDoc documentation](references/springdoc-official.md)
- [Common issues and solutions](references/troubleshooting.md)
- [SpringDoc Official Documentation](https://springdoc.org/)

## Related Skills

- `spring-boot-rest-api-standards` - REST API design standards
- `unit-test-controller-layer` - Testing REST controllers
