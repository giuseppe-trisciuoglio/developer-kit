# SpringDoc OpenAPI Official Documentation

## Overview

SpringDoc OpenAPI is a Java library that automates API documentation generation for Spring Boot projects. It examines applications at runtime to infer API semantics based on Spring configurations and annotations.

## Key Features

- **OpenAPI 3 support** with Spring Boot v3 (Java 17 & Jakarta EE 9)
- **Swagger UI integration** for interactive API documentation
- **Scalar support** as an alternative UI
- **Multiple endpoint support** with grouping capabilities
- **Security integration** with Spring Security and OAuth2
- **Functional endpoints** support for WebFlux and WebMvc.fn

## Dependencies

### Maven (Spring Boot 3.x)
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Gradle (Spring Boot 3.x)
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

## Default Endpoints

After adding the dependency:
- **OpenAPI JSON**: `http://localhost:8080/v3/api-docs`
- **OpenAPI YAML**: `http://localhost:8080/v3/api-docs.yaml`
- **Swagger UI**: `http://localhost:8080/swagger-ui/index.html`

## Compatibility Matrix

| Spring Boot Version | SpringDoc OpenAPI Version |
|---------------------|---------------------------|
| 3.4.x               | 2.7.x - 2.8.x            |
| 3.3.x               | 2.6.x                    |
| 3.2.x               | 2.3.x - 2.5.x            |
| 3.1.x               | 2.2.x                    |
| 3.0.x               | 2.0.x - 2.1.x            |

## Basic Configuration

### application.properties
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

# Default response messages
springdoc.default-produces-media-type=application/json
springdoc.default-consumes-media-type=application/json
```

### application.yml
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

## Migration from SpringFox

Replace SpringFox dependencies and update annotations:
- `@Api` → `@Tag`
- `@ApiOperation` → `@Operation`
- `@ApiParam` → `@Parameter`
- Remove `Docket` beans, use `GroupedOpenApi` instead

## Common Issues and Solutions

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

## External References

- [SpringDoc Official Documentation](https://springdoc.org/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger UI Configuration](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/)