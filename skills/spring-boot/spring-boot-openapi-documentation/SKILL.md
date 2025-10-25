---
name: spring-boot-openapi-documentation
description: Expert in documenting Spring Boot REST APIs using SpringDoc OpenAPI 3.0 and Swagger UI. Use when generating API documentation, configuring Swagger UI, adding OpenAPI annotations, implementing API security documentation, or enhancing REST endpoint documentation with examples and schemas.
allowed-tools: Read, Write, Bash
---

# Spring Boot OpenAPI Documentation with SpringDoc

Expert skill for implementing comprehensive REST API documentation using SpringDoc OpenAPI 3.0 and Swagger UI in Spring Boot 3.x applications.

## When to Use

Use this skill when you need to:
- Set up SpringDoc OpenAPI in Spring Boot 3.x projects
- Generate OpenAPI 3.0 specifications for REST APIs
- Configure and customize Swagger UI
- Add detailed API documentation with annotations
- Document request/response models with validation
- Implement API security documentation (JWT, OAuth2, Basic Auth)
- Document pageable and sortable endpoints
- Add examples and schemas to API endpoints
- Customize OpenAPI definitions programmatically
- Generate API documentation for WebMvc or WebFlux applications
- Support multiple API groups and versions
- Document error responses and exception handlers
- Add JSR-303 Bean Validation to API documentation
- Support Kotlin-based Spring Boot APIs

## Core Setup

### Maven Dependency (Spring Boot 3.x)

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Gradle Dependency

```gradle
implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.13'
```

### WebFlux Support

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webflux-ui</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Compatibility Matrix

| Spring Boot Version | SpringDoc OpenAPI Version |
|---------------------|---------------------------|
| 3.4.x               | 2.7.x - 2.8.x            |
| 3.3.x               | 2.6.x                    |
| 3.2.x               | 2.3.x - 2.5.x            |
| 3.1.x               | 2.2.x                    |
| 3.0.x               | 2.0.x - 2.1.x            |

## Default Endpoints

After adding the dependency:
- **OpenAPI JSON**: `http://localhost:8080/v3/api-docs`
- **OpenAPI YAML**: `http://localhost:8080/v3/api-docs.yaml`
- **Swagger UI**: `http://localhost:8080/swagger-ui/index.html`

## Application Configuration

### Basic Configuration (application.properties)

```properties
# Custom API docs path
springdoc.api-docs.path=/api-docs

# Custom Swagger UI path
springdoc.swagger-ui.path=/swagger-ui-custom.html

# Sort operations by HTTP method
springdoc.swagger-ui.operationsSorter=method

# Sort tags alphabetically
springdoc.swagger-ui.tagsSorter=alpha

# Enable/disable Swagger UI
springdoc.swagger-ui.enabled=true

# Disable springdoc-openapi endpoints
springdoc.api-docs.enabled=false

# Show actuator endpoints in documentation
springdoc.show-actuator=true

# Packages to scan
springdoc.packages-to-scan=com.example.controller

# Paths to match
springdoc.paths-to-match=/api/**,/public/**

# Disable default response messages
springdoc.default-produces-media-type=application/json
springdoc.default-consumes-media-type=application/json
```

### YAML Configuration (application.yml)

```yaml
springdoc:
  api-docs:
    path: /api-docs
    enabled: true
  swagger-ui:
    path: /swagger-ui.html
    enabled: true
    operationsSorter: method
    tagsSorter: alpha
    tryItOutEnabled: true
    filter: true
    displayRequestDuration: true
  packages-to-scan: com.example.controller
  paths-to-match: /api/**
  show-actuator: false
```

## OpenAPI Information Configuration

### Programmatic Configuration

```java
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenAPIConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Book API")
                .version("1.0")
                .description("REST API for managing books")
                .termsOfService("https://example.com/terms")
                .contact(new Contact()
                    .name("API Support")
                    .url("https://example.com/support")
                    .email("support@example.com"))
                .license(new License()
                    .name("Apache 2.0")
                    .url("https://www.apache.org/licenses/LICENSE-2.0.html")))
            .servers(List.of(
                new Server().url("http://localhost:8080").description("Development server"),
                new Server().url("https://api.example.com").description("Production server")
            ));
    }
}
```

## Controller Documentation

### Basic Controller Documentation

```java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/books")
@Tag(name = "Book", description = "Book management APIs")
public class BookController {
    
    private final BookRepository repository;
    
    public BookController(BookRepository repository) {
        this.repository = repository;
    }
    
    @Operation(
        summary = "Retrieve a book by ID",
        description = "Get a Book object by specifying its ID. The response is Book object with id, title, author and description."
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Successfully retrieved book",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = Book.class)
            )
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Book not found",
            content = @Content
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Internal server error",
            content = @Content
        )
    })
    @GetMapping("/{id}")
    public Book findById(
        @Parameter(description = "ID of book to retrieve", required = true)
        @PathVariable Long id
    ) {
        return repository.findById(id)
            .orElseThrow(() -> new BookNotFoundException());
    }
    
    @Operation(summary = "Get all books", description = "Returns list of all books")
    @ApiResponse(
        responseCode = "200",
        description = "Found all books",
        content = @Content(
            mediaType = "application/json",
            array = @ArraySchema(schema = @Schema(implementation = Book.class))
        )
    )
    @GetMapping
    public List<Book> findAll() {
        return repository.findAll();
    }
}
```

### Request Body Documentation

```java
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import io.swagger.v3.oas.annotations.media.ExampleObject;

@Operation(summary = "Create a new book")
@ApiResponses(value = {
    @ApiResponse(
        responseCode = "201",
        description = "Book created successfully",
        content = @Content(
            mediaType = "application/json",
            schema = @Schema(implementation = Book.class)
        )
    ),
    @ApiResponse(responseCode = "400", description = "Invalid input provided")
})
@PostMapping
@ResponseStatus(HttpStatus.CREATED)
public Book createBook(
    @RequestBody(
        description = "Book to create",
        required = true,
        content = @Content(
            mediaType = "application/json",
            schema = @Schema(implementation = Book.class),
            examples = @ExampleObject(
                value = """
                {
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "isbn": "978-0132350884",
                    "description": "A handbook of agile software craftsmanship"
                }
                """
            )
        )
    )
    @org.springframework.web.bind.annotation.RequestBody Book book
) {
    return repository.save(book);
}
```

### Query Parameters Documentation

```java
@Operation(summary = "Search books by criteria")
@GetMapping("/search")
public List<Book> searchBooks(
    @Parameter(description = "Search by title", example = "Clean Code")
    @RequestParam(required = false) String title,
    
    @Parameter(description = "Search by author", example = "Robert Martin")
    @RequestParam(required = false) String author,
    
    @Parameter(description = "Minimum year", example = "2000")
    @RequestParam(required = false) Integer minYear
) {
    return repository.search(title, author, minYear);
}
```

## Model Documentation

### Entity with Validation Annotations

```java
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;

@Entity
@Schema(description = "Book entity representing a published book")
public class Book {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Schema(description = "Unique identifier", example = "1", accessMode = Schema.AccessMode.READ_ONLY)
    private Long id;
    
    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 200)
    @Schema(description = "Book title", example = "Clean Code", required = true, maxLength = 200)
    private String title;
    
    @NotBlank(message = "Author is required")
    @Size(min = 1, max = 100)
    @Schema(description = "Book author", example = "Robert C. Martin", required = true)
    private String author;
    
    @Pattern(regexp = "^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")
    @Schema(description = "ISBN number", example = "978-0132350884")
    private String isbn;
    
    @Size(max = 1000)
    @Schema(description = "Book description", example = "A handbook of agile software craftsmanship", maxLength = 1000)
    private String description;
    
    @Min(value = 1900)
    @Max(value = 2100)
    @Schema(description = "Publication year", example = "2008", minimum = "1900", maximum = "2100")
    private Integer publicationYear;
    
    @DecimalMin(value = "0.0")
    @Schema(description = "Book price", example = "49.99", minimum = "0")
    private BigDecimal price;
    
    // Constructor, getters, setters
}
```

### Hidden Fields

```java
import com.fasterxml.jackson.annotation.JsonIgnore;
import io.swagger.v3.oas.annotations.media.Schema;

@Schema(hidden = true)
private String internalField;

@JsonIgnore
@Schema(accessMode = Schema.AccessMode.READ_ONLY)
private LocalDateTime createdAt;
```

## Pageable and Sorting Documentation

### Spring Data Pageable Support

```java
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

@Operation(summary = "Get paginated list of books")
@GetMapping("/paginated")
public Page<Book> findAllPaginated(
    @ParameterObject Pageable pageable
) {
    return repository.findAll(pageable);
}
```

This automatically generates documentation for:
- `page`: Page number (0-indexed)
- `size`: Page size
- `sort`: Sorting criteria (e.g., "title,asc")

## Security Documentation

### JWT Bearer Authentication

```java
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.security.SecurityScheme;

@Configuration
public class OpenAPISecurityConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .components(new Components()
                .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                    .type(SecurityScheme.Type.HTTP)
                    .scheme("bearer")
                    .bearerFormat("JWT")
                    .description("JWT authentication")
                )
            );
    }
}

// On controller or method level
@SecurityRequirement(name = "bearer-jwt")
@GetMapping("/secure")
public String secureEndpoint() {
    return "Secure data";
}
```

### Basic Authentication

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("basicAuth", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("basic")
            )
        );
}
```

### OAuth2 Configuration

```java
import io.swagger.v3.oas.models.security.OAuthFlow;
import io.swagger.v3.oas.models.security.OAuthFlows;
import io.swagger.v3.oas.models.security.Scopes;

@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("oauth2", new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .flows(new OAuthFlows()
                    .authorizationCode(new OAuthFlow()
                        .authorizationUrl("https://auth.example.com/oauth/authorize")
                        .tokenUrl("https://auth.example.com/oauth/token")
                        .scopes(new Scopes()
                            .addString("read", "Read access")
                            .addString("write", "Write access")
                        )
                    )
                )
            )
        );
}
```

### API Key Authentication

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("api-key", new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name("X-API-Key")
            )
        );
}
```

## Exception Handling Documentation

### @ControllerAdvice Documentation

```java
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BookNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @Operation(hidden = true)
    public ErrorResponse handleBookNotFound(BookNotFoundException ex) {
        return new ErrorResponse("BOOK_NOT_FOUND", ex.getMessage());
    }
    
    @ExceptionHandler(ValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @Operation(hidden = true)
    public ErrorResponse handleValidation(ValidationException ex) {
        return new ErrorResponse("VALIDATION_ERROR", ex.getMessage());
    }
}

@Schema(description = "Error response")
public record ErrorResponse(
    @Schema(description = "Error code", example = "BOOK_NOT_FOUND")
    String code,
    
    @Schema(description = "Error message", example = "Book with ID 123 not found")
    String message,
    
    @Schema(description = "Timestamp", example = "2024-01-15T10:30:00Z")
    LocalDateTime timestamp
) {
    public ErrorResponse(String code, String message) {
        this(code, message, LocalDateTime.now());
    }
}
```

## Advanced Features

### Multiple API Groups

```java
@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder()
        .group("public")
        .pathsToMatch("/api/public/**")
        .build();
}

@Bean
public GroupedOpenApi adminApi() {
    return GroupedOpenApi.builder()
        .group("admin")
        .pathsToMatch("/api/admin/**")
        .build();
}
```

Access groups at:
- `/v3/api-docs/public`
- `/v3/api-docs/admin`

### Hiding Endpoints

```java
@Operation(hidden = true)
@GetMapping("/internal")
public String internalEndpoint() {
    return "Hidden from docs";
}

// Or hide entire controller
@Hidden
@RestController
public class InternalController {
    // All endpoints hidden
}
```

### Custom Operation Customizer

```java
import org.springdoc.core.customizers.OperationCustomizer;

@Bean
public OperationCustomizer customizeOperation() {
    return (operation, handlerMethod) -> {
        operation.addExtension("x-custom-field", "custom-value");
        return operation;
    };
}
```

### Filtering Packages and Paths

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI();
}

@Bean
public GroupedOpenApi apiGroup() {
    return GroupedOpenApi.builder()
        .group("api")
        .packagesToScan("com.example.controller")
        .pathsToMatch("/api/**")
        .pathsToExclude("/api/internal/**")
        .build();
}
```

## Kotlin Support

### Kotlin Data Class Documentation

```kotlin
import io.swagger.v3.oas.annotations.media.Schema
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

@Entity
data class Book(
    @field:Schema(description = "Unique identifier", accessMode = Schema.AccessMode.READ_ONLY)
    @Id
    val id: Long = 0,
    
    @field:NotBlank
    @field:Size(min = 1, max = 200)
    @field:Schema(description = "Book title", example = "Clean Code", required = true)
    val title: String = "",
    
    @field:NotBlank
    @field:Schema(description = "Author name", example = "Robert Martin")
    val author: String = ""
)

@RestController
@RequestMapping("/api/books")
@Tag(name = "Book", description = "Book management APIs")
class BookController(private val repository: BookRepository) {
    
    @Operation(summary = "Get all books")
    @ApiResponses(value = [
        ApiResponse(
            responseCode = "200",
            description = "Found books",
            content = [Content(
                mediaType = "application/json",
                array = ArraySchema(schema = Schema(implementation = Book::class))
            )]
        ),
        ApiResponse(responseCode = "404", description = "No books found", content = [Content()])
    ])
    @GetMapping
    fun getAllBooks(): List<Book> = repository.findAll()
}
```

### Enhanced Kotlin Support Dependency

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-common</artifactId>
    <version>2.8.13</version>
</dependency>
```

## Maven and Gradle Plugins

### Maven Plugin for Generating OpenAPI

```xml
<plugin>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-maven-plugin</artifactId>
    <version>1.4</version>
    <executions>
        <execution>
            <phase>integration-test</phase>
            <goals>
                <goal>generate</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <apiDocsUrl>http://localhost:8080/v3/api-docs</apiDocsUrl>
        <outputFileName>openapi.json</outputFileName>
        <outputDir>${project.build.directory}</outputDir>
    </configuration>
</plugin>
```

### Gradle Plugin

```gradle
plugins {
    id 'org.springdoc.openapi-gradle-plugin' version '1.9.0'
}

openApi {
    apiDocsUrl = "http://localhost:8080/v3/api-docs"
    outputDir = file("$buildDir/docs")
    outputFileName = "openapi.json"
}
```

## Common Annotations Reference

### Core Annotations

- `@Tag`: Group operations under a tag
- `@Operation`: Describe a single API operation
- `@ApiResponse` / `@ApiResponses`: Document response codes
- `@Parameter`: Document a single parameter
- `@RequestBody`: Document request body (OpenAPI version)
- `@Schema`: Document model schema
- `@SecurityRequirement`: Apply security to operations
- `@Hidden`: Hide from documentation
- `@ParameterObject`: Document complex objects as parameters

### Validation Annotations (Auto-documented)

- `@NotNull`, `@NotBlank`, `@NotEmpty`: Required fields
- `@Size(min, max)`: String/collection length constraints
- `@Min`, `@Max`: Numeric range constraints
- `@Pattern`: Regex validation
- `@Email`: Email validation
- `@DecimalMin`, `@DecimalMax`: Decimal constraints
- `@Positive`, `@PositiveOrZero`, `@Negative`, `@NegativeOrZero`

## Best Practices

1. **Use descriptive operation summaries and descriptions**
   - Summary: Short, clear statement (< 120 chars)
   - Description: Detailed explanation with use cases

2. **Document all response codes**
   - Include success (2xx), client errors (4xx), server errors (5xx)
   - Provide meaningful descriptions for each

3. **Add examples to request/response bodies**
   - Use `@ExampleObject` for realistic examples
   - Include edge cases when relevant

4. **Leverage JSR-303 validation annotations**
   - SpringDoc auto-generates constraints from validation annotations
   - Reduces duplication between code and documentation

5. **Use `@ParameterObject` for complex parameters**
   - Especially useful for Pageable, custom filter objects
   - Keeps controller methods clean

6. **Group related endpoints with @Tag**
   - Organize API by domain entities or features
   - Use consistent tag names across controllers

7. **Document security requirements**
   - Apply `@SecurityRequirement` where authentication needed
   - Configure security schemes globally in OpenAPI bean

8. **Hide internal/admin endpoints appropriately**
   - Use `@Hidden` or create separate API groups
   - Prevent exposing internal implementation details

9. **Customize Swagger UI for better UX**
   - Enable filtering, sorting, try-it-out features
   - Set appropriate default behaviors

10. **Version your API documentation**
    - Include version in OpenAPI Info
    - Consider multiple API groups for versioned APIs

## Troubleshooting

### Parameter Names Not Appearing

Add `-parameters` compiler flag (Spring Boot 3.2+):

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <parameters>true</parameters>
    </configuration>
</plugin>
```

### Swagger UI Shows "Unable to render definition"

Ensure `ByteArrayHttpMessageConverter` is registered when overriding converters:

```java
converters.add(new ByteArrayHttpMessageConverter());
converters.add(new MappingJackson2HttpMessageConverter());
```

### Endpoints Not Appearing

Check:
- `springdoc.packages-to-scan` configuration
- `springdoc.paths-to-match` configuration
- Endpoints aren't marked with `@Hidden`

### Security Configuration Issues

Permit SpringDoc endpoints in Spring Security:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    return http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
            .anyRequest().authenticated()
        )
        .build();
}
```

## Related Skills

- @spring-boot-rest-api-standards - REST API design standards
- @spring-boot-dependency-injection - Dependency injection patterns
- @unit-test-controller-layer - Testing REST controllers
- @spring-boot-actuator - Production monitoring and management

## References

- [SpringDoc Official Documentation](https://springdoc.org/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger UI Configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/)
