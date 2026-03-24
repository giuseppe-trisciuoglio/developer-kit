# Advanced SpringDoc Configuration

## Multiple API Groups

### Group by Path

```java
import org.springdoc.core.models.GroupedOpenApi;

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

@Bean
public GroupedOpenApi userApi() {
    return GroupedOpenApi.builder()
        .group("user")
        .pathsToMatch("/api/user/**")
        .build();
}
```

### Group by Package

```java
@Bean
public GroupedOpenApi controllerGroup() {
    return GroupedOpenApi.builder()
        .group("controllers")
        .packagesToScan("com.example.controller")
        .build();
}

@Bean
public GroupedOpenApi controllerGroup2() {
    return GroupedOpenApi.builder()
        .group("vendor-controllers")
        .packagesToScan("com.vendor.controller")
        .build();
}
```

### Group with Custom Configuration

```java
@Bean
public GroupedOpenApi customGroup() {
    return GroupedOpenApi.builder()
        .group("custom")
        .pathsToMatch("/api/custom/**")
        .addOpenApiMethodFilter(method -> method.isAnnotationPresent(CustomApi.class))
        .build();
}
```

## Custom Operation Customizer

### Global Operation Customization

```java
import org.springdoc.core.customizers.OperationCustomizer;

@Bean
public OperationCustomizer customizeOperation() {
    return (operation, handlerMethod) -> {
        // Add custom extension
        operation.addExtension("x-custom-field", "custom-value");

        // Add tag based on annotation
        if (handlerMethod.getMethod().isAnnotationPresent(Deprecated.class)) {
            operation.addTagsItem("deprecated");
        }

        // Customize summary
        String className = handlerMethod.getBeanType().getSimpleName();
        operation.setSummary(className + ": " + operation.getSummary());

        return operation;
    };
}
```

### Conditional Customization

```java
@Bean
public OperationCustomizer authOperationCustomizer() {
    return (operation, handlerMethod) -> {
        // Add security requirement for methods with @RequireAuth
        if (handlerMethod.hasMethodAnnotation(RequireAuth.class)) {
            operation.addSecurityItem(new SecurityRequirement().addList("bearer-jwt"));
        }
        return operation;
    };
}
```

## Hide Endpoints

### Hide Single Endpoint

```java
@Operation(hidden = true)
@GetMapping("/internal")
public String internalEndpoint() {
    return "Hidden from docs";
}
```

### Hide Entire Controller

```java
import io.swagger.v3.oas.annotations.Hidden;

@Hidden
@RestController
@RequestMapping("/internal")
public class InternalController {
    // All endpoints hidden from documentation
}
```

### Conditional Hiding

```java
@Bean
public OperationCustomizer conditionalHiding() {
    return (operation, handlerMethod) -> {
        // Hide endpoints based on profile
        if (isProductionProfile()) {
            if (handlerMethod.getMethod().getName().contains("Debug")) {
                operation.setHidden(true);
            }
        }
        return operation;
    };
}
```

## Custom OpenAPI Bean

### Complete OpenAPI Configuration

```java
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;

@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title("Book Management API")
            .description("Comprehensive API for managing books, authors, and publishers")
            .version("v1.0.0")
            .contact(new Contact()
                .name("API Support")
                .email("support@example.com")
                .url("https://example.com/support")
            )
            .license(new License()
                .name("MIT License")
                .url("https://opensource.org/licenses/MIT")
            )
        )
        .addServersItem(new Server()
            .url("https://api.example.com")
            .description("Production server")
        )
        .addServersItem(new Server()
            .url("https://staging-api.example.com")
            .description("Staging server")
        )
        .addServersItem(new Server()
            .url("http://localhost:8080")
            .description("Development server")
        );
}
```

### Environment-Specific Configuration

```java
@Value("${api.version:v1.0.0}")
private String apiVersion;

@Value("${api.title:My API}")
private String apiTitle;

@Profile("production")
@Bean
public OpenAPI prodOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title(apiTitle)
            .version(apiVersion)
            .description("Production API")
        )
        .addServersItem(new Server().url("https://api.example.com"));
}

@Profile("development")
@Bean
public OpenAPI devOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title(apiTitle + " (DEV)")
            .version(apiVersion)
            .description("Development API")
        )
        .addServersItem(new Server().url("http://localhost:8080"));
}
```

## Custom Server Configuration

### Multiple Servers with Variables

```java
@Bean
public OpenAPI serversOpenAPI() {
    Server prodServer = new Server()
        .url("https://{environment}.example.com:{port}/api")
        .description("Production server")
        .addVariable("environment", new ServerVariable()
            .defaultValue("api")
            .enumeration(Arrays.asList("api", "api-staging"))
            .description("Server environment")
        )
        .addVariable("port", new ServerVariable()
            .defaultValue("443")
            .description("Server port")
        );

    return new OpenAPI().addServersItem(prodServer);
}
```

## Custom Tags

### Dynamic Tag Configuration

```java
@Bean
public OpenAPI customTagsOpenAPI() {
    return new OpenAPI()
        .tags(Arrays.asList(
            new Tag()
                .name("public")
                .description("Publicly accessible endpoints")
                .externalDocs(new ExternalDocumentation()
                    .description("Public API documentation")
                    .url("https://docs.example.com/public")
                ),
            new Tag()
                .name("admin")
                .description("Administrative endpoints")
                .externalDocs(new ExternalDocumentation()
                    .description("Admin guide")
                    .url("https://docs.example.com/admin")
                )
        ));
}
```

## Custom Properties

### Adding Custom Extensions

```java
@Bean
public OperationCustomizer addCustomExtensions() {
    return (operation, handlerMethod) -> {
        // Add rate limit info
        operation.addExtension("x-rate-limit", 100);

        // Add cost info
        operation.addExtension("x-cost", 1);

        // Add deprecation notice
        if (handlerMethod.getMethod().isAnnotationPresent(Deprecated.class)) {
            operation.addExtension("x-deprecated-since", "v1.0");
            operation.addExtension("x-removal-date", "2025-01-01");
        }

        return operation;
    };
}
```

## Custom Response Headers

### Documenting Response Headers

```java
@Operation(
    summary = "Get book with headers",
    responses = {
        @ApiResponse(
            responseCode = "200",
            description = "Book found",
            headers = {
                @Header(name = "X-RateLimit-Remaining", description = "Remaining API calls", schema = @Schema(type = "integer")),
                @Header(name = "X-RateLimit-Reset", description = "Rate limit reset time", schema = @Schema(type = "string"))
            }
        )
    }
)
@GetMapping("/{id}")
public Book getBook(@PathVariable Long id) {
    return repository.findById(id).orElseThrow();
}
```

## WebFlux Configuration

### Reactive Router Function Documentation

```java
import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.web.reactive.function.server.RouterFunction;
import org.springframework.web.reactive.function.server.ServerResponse;

@Bean
public RouterFunction<ServerResponse> bookRouter(BookHandler handler) {
    return RouterFunctions.route()
        .GET("/api/books", handler::getAllBooks)
        .GET("/api/books/{id}", handler::getBookById)
        .POST("/api/books", handler::createBook)
        .build();
}
```

## Kotlin Support

### Kotlin DSL Configuration

```kotlin
@Bean
fun customOpenAPI(): OpenAPI {
    return OpenAPI()
        .info(Info()
            .title("Kotlin API")
            .version("1.0.0")
            .description("API built with Kotlin and Spring Boot")
        )
}
```
