# SpringDoc OpenAPI Reference Documentation

## Configuration Properties Reference

### Core Properties

```yaml
springdoc:
  # API Documentation Settings
  api-docs:
    enabled: true                          # Enable/disable API docs endpoints (default: true)
    path: /v3/api-docs                     # Path for OpenAPI JSON (default: /v3/api-docs)
    resolve-schema-properties: true        # Resolve schema properties (default: true)
    
  # Swagger UI Settings
  swagger-ui:
    enabled: true                          # Enable/disable Swagger UI (default: true)
    path: /swagger-ui.html                 # Custom Swagger UI path (default: /swagger-ui.html)
    config-url: /v3/api-docs/swagger-config # Swagger UI config URL
    url: /v3/api-docs                      # URL to OpenAPI description
    operations-sorter: alpha               # Sort operations: alpha, method (default: none)
    tags-sorter: alpha                     # Sort tags: alpha (default: none)
    try-it-out-enabled: true               # Enable Try-it-out by default (default: false)
    filter: false                          # Enable filtering (default: false)
    display-request-duration: false        # Display request duration (default: false)
    display-operation-id: false            # Display operation IDs (default: false)
    deep-linking: true                     # Enable deep linking (default: false)
    default-models-expand-depth: 1         # Default expansion depth for models (default: 1)
    default-model-expand-depth: 1          # Default expansion depth for model (default: 1)
    default-model-rendering: example       # Model rendering: example, model (default: example)
    show-extensions: false                 # Show vendor extensions (default: false)
    show-common-extensions: false          # Show common extensions (default: false)
    disable-swagger-default-url: false     # Disable default petstore URL (default: false)
    persist-authorization: false           # Persist authorization data (default: false)
    oauth2-redirect-url: /swagger-ui/oauth2-redirect.html # OAuth2 redirect URL
    supported-submit-methods:              # Supported HTTP methods for Try-it-out
      - get
      - post
      - put
      - delete
      - patch
    validator-url: null                    # Validator URL (default: null)
    
  # Filtering and Scanning
  packages-to-scan:                        # Packages to scan for API endpoints
    - com.example.api
    - com.example.controllers
  packages-to-exclude:                     # Packages to exclude from scanning
    - com.example.internal
  paths-to-match:                          # Path patterns to include
    - /api/**
    - /public/**
  paths-to-exclude:                        # Path patterns to exclude
    - /api/internal/**
    - /admin/**
    
  # Content Type Filtering
  produces-to-match:                       # Produce media types to include
    - application/json
    - application/xml
  consumes-to-match:                       # Consume media types to include
    - application/json
  headers-to-match:                        # Headers to match
    - X-API-Version
    
  # Documentation Enhancements
  auto-tag-classes: true                   # Auto-tag classes (default: true)
  show-actuator: true                      # Show Spring Boot Actuator endpoints (default: false)
  show-login-endpoint: false               # Show login endpoint (default: false)
  model-and-view-allowed: false            # Allow ModelAndView return type (default: false)
  
  # Caching
  cache:
    disabled: false                        # Disable caching (default: false)
    
  # Output Formatting
  writer-with-default-pretty-printer: true # Pretty print JSON output (default: false)
  writer-with-order-by-keys: false         # Order keys in output (default: false)
  
  # Advanced Settings
  default-consumes-media-type: application/json  # Default consumes media type
  default-produces-media-type: application/json  # Default produces media type
  override-with-generic-response: false          # Override with generic response (default: true)
  remove-broken-reference-definitions: true      # Remove broken references (default: true)
  use-management-port: false                     # Use management port for docs (default: false)
  disable-i18n: false                            # Disable i18n (default: false)
  use-fqn: false                                 # Use fully qualified names (default: false)
  
  # Group Configuration
  group-configs:
    - group: public
      display-name: Public API
      paths-to-match:
        - /api/public/**
    - group: admin
      display-name: Admin API
      paths-to-match:
        - /api/admin/**
```

### Properties File Format

```properties
# API Documentation
springdoc.api-docs.enabled=true
springdoc.api-docs.path=/v3/api-docs

# Swagger UI
springdoc.swagger-ui.enabled=true
springdoc.swagger-ui.path=/swagger-ui.html
springdoc.swagger-ui.operations-sorter=alpha
springdoc.swagger-ui.tags-sorter=alpha
springdoc.swagger-ui.try-it-out-enabled=true

# Package Scanning
springdoc.packages-to-scan=com.example.api,com.example.controllers
springdoc.paths-to-match=/api/**,/public/**

# Content Types
springdoc.produces-to-match=application/json,application/xml
springdoc.default-consumes-media-type=application/json
springdoc.default-produces-media-type=application/json

# Features
springdoc.auto-tag-classes=true
springdoc.show-actuator=true
springdoc.writer-with-default-pretty-printer=true
```

## Annotation Reference

### @OpenAPIDefinition

Defines global API information, servers, and security requirements.

```java
@OpenAPIDefinition(
    info = @Info(
        title = "API Title",
        version = "1.0.0",
        description = "API Description",
        termsOfService = "https://example.com/terms",
        contact = @Contact(
            name = "API Support",
            url = "https://example.com/contact",
            email = "support@example.com"
        ),
        license = @License(
            name = "Apache 2.0",
            url = "https://www.apache.org/licenses/LICENSE-2.0.html"
        )
    ),
    servers = {
        @Server(
            url = "https://api.example.com",
            description = "Production server"
        ),
        @Server(
            url = "https://staging.example.com",
            description = "Staging server"
        )
    },
    security = {
        @SecurityRequirement(name = "bearerAuth")
    },
    externalDocs = @ExternalDocumentation(
        description = "Find more info here",
        url = "https://example.com/docs"
    )
)
```

### @Tag

Groups operations under a specific tag.

```java
@Tag(
    name = "Users",
    description = "User management operations",
    externalDocs = @ExternalDocumentation(
        description = "User docs",
        url = "https://example.com/user-docs"
    )
)
```

### @Operation

Documents an individual API operation.

```java
@Operation(
    summary = "Get user by ID",
    description = "Returns a single user by their unique identifier",
    operationId = "getUserById",
    tags = {"Users"},
    security = @SecurityRequirement(name = "bearerAuth"),
    extensions = {
        @Extension(
            name = "x-code-samples",
            properties = {
                @ExtensionProperty(name = "lang", value = "curl"),
                @ExtensionProperty(name = "source", value = "curl -X GET...")
            }
        )
    },
    deprecated = false,
    hidden = false
)
```

### @ApiResponse / @ApiResponses

Documents possible responses from an operation.

```java
@ApiResponses({
    @ApiResponse(
        responseCode = "200",
        description = "Successful operation",
        content = @Content(
            mediaType = "application/json",
            schema = @Schema(implementation = User.class),
            examples = @ExampleObject(
                name = "UserExample",
                summary = "Sample user response",
                value = "{\"id\":1,\"name\":\"John\"}"
            )
        ),
        headers = {
            @Header(
                name = "X-Rate-Limit",
                description = "Calls per hour allowed",
                schema = @Schema(type = "integer")
            )
        }
    ),
    @ApiResponse(
        responseCode = "404",
        description = "User not found",
        content = @Content(
            schema = @Schema(implementation = ErrorResponse.class)
        )
    ),
    @ApiResponse(
        responseCode = "500",
        description = "Internal server error"
    )
})
```

### @Parameter

Documents request parameters.

```java
@Parameter(
    name = "id",
    description = "User ID",
    required = true,
    in = ParameterIn.PATH,
    schema = @Schema(
        type = "integer",
        format = "int64",
        minimum = "1"
    ),
    example = "123",
    deprecated = false,
    allowEmptyValue = false,
    explode = Explode.FALSE
)
```

### @Parameters

Groups multiple parameter annotations.

```java
@Parameters({
    @Parameter(
        name = "page",
        description = "Page number",
        in = ParameterIn.QUERY,
        schema = @Schema(type = "integer", defaultValue = "0")
    ),
    @Parameter(
        name = "size",
        description = "Page size",
        in = ParameterIn.QUERY,
        schema = @Schema(type = "integer", defaultValue = "20")
    )
})
```

### @RequestBody

Documents request body.

```java
@RequestBody(
    description = "User to create",
    required = true,
    content = @Content(
        mediaType = "application/json",
        schema = @Schema(implementation = UserCreateRequest.class),
        examples = {
            @ExampleObject(
                name = "Basic User",
                summary = "Basic user creation",
                value = "{\"name\":\"John\",\"email\":\"john@example.com\"}"
            ),
            @ExampleObject(
                name = "User with Profile",
                summary = "User with complete profile",
                value = "{\"name\":\"Jane\",\"email\":\"jane@example.com\",\"profile\":{\"bio\":\"Developer\"}}"
            )
        }
    )
)
```

### @Schema

Documents model properties and data types.

```java
@Schema(
    name = "User",
    description = "User model",
    example = "{\"id\":1,\"name\":\"John\"}",
    requiredProperties = {"name", "email"},
    accessMode = Schema.AccessMode.READ_ONLY,
    implementation = UserImpl.class,
    subTypes = {AdminUser.class, RegularUser.class},
    discriminatorProperty = "userType",
    discriminatorMapping = {
        @DiscriminatorMapping(value = "admin", schema = AdminUser.class),
        @DiscriminatorMapping(value = "regular", schema = RegularUser.class)
    },
    additionalProperties = Schema.AdditionalPropertiesValue.TRUE,
    deprecated = false,
    hidden = false,
    readOnly = false,
    writeOnly = false,
    nullable = false
)
```

**Property-level @Schema:**

```java
@Schema(
    description = "User's email address",
    example = "user@example.com",
    required = true,
    format = "email",
    pattern = "^[A-Za-z0-9+_.-]+@(.+)$",
    minLength = 5,
    maxLength = 100,
    minimum = "0",
    maximum = "150",
    exclusiveMinimum = false,
    exclusiveMaximum = false,
    multipleOf = 1.0,
    defaultValue = "default@example.com",
    allowableValues = {"user@example.com", "admin@example.com"}
)
private String email;
```

### @SecurityScheme

Defines security schemes for the API.

```java
// HTTP Bearer Authentication
@SecurityScheme(
    name = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT",
    description = "JWT authentication token"
)

// API Key Authentication
@SecurityScheme(
    name = "apiKey",
    type = SecuritySchemeType.APIKEY,
    in = SecuritySchemeIn.HEADER,
    paramName = "X-API-Key",
    description = "API Key authentication"
)

// OAuth2 Authentication
@SecurityScheme(
    name = "oauth2",
    type = SecuritySchemeType.OAUTH2,
    flows = @OAuthFlows(
        authorizationCode = @OAuthFlow(
            authorizationUrl = "https://example.com/oauth/authorize",
            tokenUrl = "https://example.com/oauth/token",
            refreshUrl = "https://example.com/oauth/refresh",
            scopes = {
                @OAuthScope(name = "read:users", description = "Read user data"),
                @OAuthScope(name = "write:users", description = "Modify user data")
            }
        ),
        implicit = @OAuthFlow(
            authorizationUrl = "https://example.com/oauth/authorize",
            scopes = {
                @OAuthScope(name = "read:users", description = "Read user data")
            }
        ),
        password = @OAuthFlow(
            tokenUrl = "https://example.com/oauth/token",
            scopes = {
                @OAuthScope(name = "read:users", description = "Read user data")
            }
        ),
        clientCredentials = @OAuthFlow(
            tokenUrl = "https://example.com/oauth/token",
            scopes = {
                @OAuthScope(name = "read:users", description = "Read user data")
            }
        )
    )
)

// OpenID Connect
@SecurityScheme(
    name = "openId",
    type = SecuritySchemeType.OPENIDCONNECT,
    openIdConnectUrl = "https://example.com/.well-known/openid-configuration"
)

// Basic Authentication
@SecurityScheme(
    name = "basicAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "basic"
)
```

### @Hidden

Hides operations or models from documentation.

```java
@Hidden // On controller method
public void internalMethod() { }

@Schema(hidden = true) // On model property
private String internalField;
```

### @ArraySchema

Documents array types in schemas.

```java
@ArraySchema(
    schema = @Schema(implementation = User.class),
    minItems = 0,
    maxItems = 100,
    uniqueItems = true,
    arraySchema = @Schema(description = "List of users")
)
```

### SpringDoc-Specific Annotations

**@RouterOperation** (Functional endpoints):

```java
@RouterOperation(
    path = "/api/users/{id}",
    method = RequestMethod.GET,
    beanClass = UserService.class,
    beanMethod = "findById",
    operation = @Operation(
        summary = "Get user by ID",
        responses = {
            @ApiResponse(
                responseCode = "200",
                content = @Content(schema = @Schema(implementation = User.class))
            )
        }
    )
)
```

**@RouterOperations** (Multiple functional endpoints):

```java
@RouterOperations({
    @RouterOperation(
        path = "/api/users",
        method = RequestMethod.GET,
        beanClass = UserService.class,
        beanMethod = "findAll"
    ),
    @RouterOperation(
        path = "/api/users/{id}",
        method = RequestMethod.GET,
        beanClass = UserService.class,
        beanMethod = "findById"
    )
})
```

## Validation Annotations Support

SpringDoc automatically maps JSR-303 Bean Validation annotations to OpenAPI schema constraints:

| Validation Annotation | OpenAPI Schema Property |
|-----------------------|-------------------------|
| `@NotNull` | `required: true` |
| `@NotEmpty` | `required: true, minLength: 1` |
| `@NotBlank` | `required: true, minLength: 1, pattern: ".*\\S.*"` |
| `@Size(min, max)` | `minLength: min, maxLength: max` |
| `@Min(value)` | `minimum: value` |
| `@Max(value)` | `maximum: value` |
| `@DecimalMin(value)` | `minimum: value` |
| `@DecimalMax(value)` | `maximum: value` |
| `@Positive` | `minimum: 0, exclusiveMinimum: true` |
| `@PositiveOrZero` | `minimum: 0` |
| `@Negative` | `maximum: 0, exclusiveMaximum: true` |
| `@NegativeOrZero` | `maximum: 0` |
| `@Email` | `format: email` |
| `@Pattern(regexp)` | `pattern: regexp` |
| `@Past` | `format: date-time` |
| `@Future` | `format: date-time` |
| `@PastOrPresent` | `format: date-time` |
| `@FutureOrPresent` | `format: date-time` |

## Programmatic API

### OpenAPIService

Access and modify the generated OpenAPI specification programmatically.

```java
import io.swagger.v3.oas.models.OpenAPI;
import org.springdoc.core.service.OpenAPIService;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class OpenApiAccessService {
    
    @Autowired
    private OpenAPIService openAPIService;
    
    public OpenAPI getOpenApiSpecification() {
        Locale locale = Locale.getDefault();
        return openAPIService.build(locale);
    }
}
```

### OpenApiCustomizer

Customize the entire OpenAPI specification.

```java
import io.swagger.v3.oas.models.OpenAPI;
import org.springdoc.core.customizers.OpenApiCustomizer;

@Bean
public OpenApiCustomizer openApiCustomizer() {
    return openApi -> {
        // Modify info
        openApi.getInfo().setTitle("Custom Title");
        
        // Add servers
        openApi.addServersItem(new Server()
            .url("https://custom.example.com")
            .description("Custom Server"));
        
        // Add custom extensions
        openApi.addExtension("x-custom-property", "value");
        
        // Modify paths
        openApi.getPaths().forEach((path, pathItem) -> {
            pathItem.readOperations().forEach(operation -> {
                // Customize operations
                operation.addExtension("x-custom-op", "value");
            });
        });
    };
}
```

### OperationCustomizer

Customize individual operations based on handler methods.

```java
import io.swagger.v3.oas.models.Operation;
import org.springdoc.core.customizers.OperationCustomizer;
import org.springframework.web.method.HandlerMethod;

@Bean
public OperationCustomizer operationCustomizer() {
    return (operation, handlerMethod) -> {
        // Add custom tag based on package
        String packageName = handlerMethod.getBeanType().getPackageName();
        if (packageName.contains("admin")) {
            operation.addTagsItem("Admin");
        }
        
        // Add custom headers
        operation.addParametersItem(new Parameter()
            .name("X-Request-ID")
            .in("header")
            .required(false)
            .schema(new StringSchema()));
        
        // Add custom extensions
        operation.addExtension("x-visibility", "public");
        
        return operation;
    };
}
```

### GroupedOpenApi

Create multiple API documentation groups.

```java
import org.springdoc.core.models.GroupedOpenApi;

@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder()
        .group("public")
        .displayName("Public API")
        .pathsToMatch("/api/public/**")
        .pathsToExclude("/api/public/internal/**")
        .packagesToScan("com.example.api.public")
        .packagesToExclude("com.example.api.internal")
        .addOpenApiCustomizer(openApi -> {
            openApi.getInfo().setTitle("Public API");
        })
        .addOperationCustomizer((operation, handlerMethod) -> {
            operation.addTagsItem("Public");
            return operation;
        })
        .build();
}

@Bean
public GroupedOpenApi adminApi() {
    return GroupedOpenApi.builder()
        .group("admin")
        .displayName("Admin API")
        .pathsToMatch("/api/admin/**")
        .addOpenApiCustomizer(openApi -> {
            openApi.getInfo().setTitle("Admin API");
            // Add admin-specific security
            openApi.addSecurityItem(new SecurityRequirement()
                .addList("adminAuth"));
        })
        .build();
}
```

## OpenAPI Specification Formats

### Access Endpoints

- JSON: `GET /v3/api-docs`
- YAML: `GET /v3/api-docs.yaml`
- Group-specific: `GET /v3/api-docs/{group-name}`
- Swagger UI: `GET /swagger-ui.html` or `/swagger-ui/index.html`

### Custom Paths

```yaml
springdoc:
  api-docs:
    path: /custom/api-docs
  swagger-ui:
    path: /custom/swagger-ui
```

Access:
- JSON: `GET /custom/api-docs`
- Swagger UI: `GET /custom/swagger-ui`

## Integration with Spring Features

### Spring Data REST

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-data-rest</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Spring Security

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-security</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Spring Hateoas

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-hateoas</artifactId>
    <version>2.8.13</version>
</dependency>
```

### Kotlin Support

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-kotlin</artifactId>
    <version>2.8.13</version>
</dependency>
```

## Swagger UI Customization

### Custom CSS

```yaml
springdoc:
  swagger-ui:
    url: /v3/api-docs
    css-url: /custom-swagger.css
```

### Custom JavaScript

```yaml
springdoc:
  swagger-ui:
    custom-js-url: /custom-swagger.js
```

### OAuth2 Configuration

```yaml
springdoc:
  swagger-ui:
    oauth:
      client-id: my-client-id
      client-secret: my-client-secret
      realm: my-realm
      app-name: my-app
      use-basic-authentication-with-access-code-grant: true
      use-pkce-with-authorization-code-grant: true
```

## Performance Considerations

### Caching

```yaml
springdoc:
  cache:
    disabled: false  # Enable caching for better performance
```

### Lazy Initialization

```yaml
spring:
  main:
    lazy-initialization: true  # Delay OpenAPI spec generation

springdoc:
  api-docs:
    enabled: false  # Disable in non-production profiles
```

### Production Optimization

```yaml
# Disable in production
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
```

Or use profiles:

```yaml
# application-prod.yaml
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
```

## Version Compatibility

| SpringDoc OpenAPI | Spring Boot | OpenAPI Spec | Java |
|-------------------|-------------|--------------|------|
| 2.8.x | 3.4.x | 3.0.1 | 17+ |
| 2.7.x | 3.3.x | 3.0.1 | 17+ |
| 2.6.x | 3.2.x | 3.0.1 | 17+ |
| 2.5.x | 3.1.x | 3.0.1 | 17+ |
| 2.0.x - 2.4.x | 3.0.x | 3.0.1 | 17+ |
| 1.8.x | 2.7.x | 3.0.1 | 8+ |
| 1.7.x | 2.6.x | 3.0.1 | 8+ |

## Migration Guide

### From Springfox to SpringDoc

| Springfox | SpringDoc |
|-----------|-----------|
| `@Api` | `@Tag` |
| `@ApiOperation` | `@Operation` |
| `@ApiParam` | `@Parameter` |
| `@ApiModel` | `@Schema` |
| `@ApiModelProperty` | `@Schema` |
| `@ApiResponse` | `@ApiResponse` |
| `@ApiResponses` | `@ApiResponses` |
| `@ApiIgnore` | `@Hidden` or `@Parameter(hidden = true)` |
| `@ApiImplicitParam` | `@Parameter` |
| `@ApiImplicitParams` | `@Parameters` |
| `Docket` | `GroupedOpenApi` |

### Configuration Migration

**Springfox:**
```java
@Bean
public Docket api() {
    return new Docket(DocumentationType.SWAGGER_2)
        .select()
        .apis(RequestHandlerSelectors.basePackage("com.example"))
        .paths(PathSelectors.ant("/api/**"))
        .build();
}
```

**SpringDoc:**
```java
@Bean
public GroupedOpenApi api() {
    return GroupedOpenApi.builder()
        .group("api")
        .packagesToScan("com.example")
        .pathsToMatch("/api/**")
        .build();
}
```

## Troubleshooting

### Common Issues

**Issue: Swagger UI not loading**
- Check `springdoc.swagger-ui.enabled=true`
- Verify path configuration
- Check Spring Security configuration
- Clear browser cache

**Issue: Operations not appearing**
- Verify package scanning configuration
- Check `@Hidden` annotations
- Verify path matching patterns
- Check if controller methods are public

**Issue: Models not showing up**
- Ensure models are used in request/response
- Check `@Schema` annotations
- Verify model is not `@Hidden`

**Issue: Security not working**
- Verify `@SecurityScheme` configuration
- Check `@SecurityRequirement` on operations
- Ensure Spring Security configuration allows access

### Debug Mode

```yaml
logging:
  level:
    org.springdoc: DEBUG
    io.swagger.v3: DEBUG
```

## Resources

- [SpringDoc OpenAPI GitHub](https://github.com/springdoc/springdoc-openapi)
- [SpringDoc Documentation](https://springdoc.org/)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
