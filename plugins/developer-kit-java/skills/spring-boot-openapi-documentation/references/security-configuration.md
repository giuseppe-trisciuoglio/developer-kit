# Security Configuration for API Documentation

## JWT Bearer Authentication

### Configuration Class

```java
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

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
                    .description("JWT authentication - Enter token without 'Bearer' prefix")
                )
            );
    }
}
```

### Apply to Controllers

```java
@RestController
@RequestMapping("/api/books")
@SecurityRequirement(name = "bearer-jwt")
@Tag(name = "Book", description = "Protected book management APIs")
public class BookController {
    // All endpoints require JWT authentication
}
```

### Apply to Specific Endpoints

```java
@RestController
@RequestMapping("/api/books")
public class BookController {

    @GetMapping("/public")
    @Operation(summary = "Public endpoint - no auth required")
    public List<Book> getPublicBooks() {
        return service.getPublicBooks();
    }

    @GetMapping("/protected")
    @Operation(summary = "Protected endpoint", security = @SecurityRequirement(name = "bearer-jwt"))
    public List<Book> getProtectedBooks() {
        return service.getProtectedBooks();
    }
}
```

## OAuth2 Configuration

### Authorization Code Flow

```java
import io.swagger.v3.oas.models.security.OAuthFlow;
import io.swagger.v3.oas.models.security.OAuthFlows;
import io.swagger.v3.oas.models.security.Scopes;

@Bean
public OpenAPI oauth2OpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("oauth2", new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .flows(new OAuthFlows()
                    .authorizationCode(new OAuthFlow()
                        .authorizationUrl("https://auth.example.com/oauth/authorize")
                        .tokenUrl("https://auth.example.com/oauth/token")
                        .scopes(new Scopes()
                            .addString("read", "Read access to resources")
                            .addString("write", "Write access to resources")
                            .addString("admin", "Administrative access")
                        )
                    )
                )
            )
        );
}
```

### Client Credentials Flow

```java
@Bean
public OpenAPI clientCredentialsOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("oauth2-client-creds", new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .flows(new OAuthFlows()
                    .clientCredentials(new OAuthFlow()
                        .tokenUrl("https://auth.example.com/oauth/token")
                        .scopes(new Scopes()
                            .addString("api.read", "Read API access")
                            .addString("api.write", "Write API access")
                        )
                    )
                )
            )
        );
}
```

## Basic Authentication

```java
@Bean
public OpenAPI basicAuthOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("basicAuth", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("basic")
                .description("Basic HTTP authentication")
            )
        );
}

@RestController
@SecurityRequirement(name = "basicAuth")
public class AdminController {
    // Endpoints protected by Basic Auth
}
```

## API Key Authentication

```java
@Bean
public OpenAPI apiKeyOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("api-key", new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name("X-API-Key")
                .description("API key in header")
            )
        );
}
```

## Multiple Security Schemes

```java
@Bean
public OpenAPI multipleSecuritySchemes() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")
            )
            .addSecuritySchemes("api-key", new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name("X-API-Key")
            )
        );
}
```

### Apply Multiple Schemes (OR logic)

```java
@Operation(
    summary = "Endpoint with multiple auth options",
    security = {
        @SecurityRequirement(name = "bearer-jwt"),
        @SecurityRequirement(name = "api-key")
    }
)
@GetMapping("/secure")
public ResponseEntity<?> secureEndpoint() {
    return ResponseEntity.ok().build();
}
```

## Conditional Security Requirements

```java
@Operation(
    summary = "Public endpoint (no security)",
    security = {}
)
@GetMapping("/public")
public String publicEndpoint() {
    return "Public access";
}

@Operation(
    summary = "Admin only",
    security = @SecurityRequirement(name = "bearer-jwt")
)
@GetMapping("/admin")
public String adminEndpoint() {
    return "Admin access";
}
```

## Security Scheme Best Practices

1. **Use descriptive descriptions**: Help users understand how to format their tokens
2. **Specify token format**: Include "JWT" or "Bearer" in bearer format
3. **Document scopes clearly**: Explain what each OAuth scope allows
4. **Hide sensitive endpoints**: Use `@Hidden` on auth-related endpoints
5. **Test in Swagger UI**: Verify auth flows work before documenting
6. **Use environment-specific URLs**: Different auth URLs for dev/staging/prod

```java
@Value("${springdoc.oauth2.auth-url:https://auth.example.com/oauth/authorize}")
private String authUrl;

@Bean
public OpenAPI environmentAwareOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("oauth2", new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .flows(new OAuthFlows()
                    .authorizationCode(new OAuthFlow()
                        .authorizationUrl(authUrl)
                        .tokenUrl("${springdoc.oauth2.token-url}")
                        .scopes(new Scopes()
                            .addString("read", "Read access")
                        )
                    )
                )
            )
        );
}
```
