# Troubleshooting SpringDoc OpenAPI

## Common Issues and Solutions

### Parameter Names Not Appearing

**Problem**: Parameter names are not showing up in the generated API documentation.

**Solution**: Add `-parameters` compiler flag (Spring Boot 3.2+):

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <parameters>true</parameters>
    </configuration>
</plugin>
```

**Gradle equivalent**:
```gradle
tasks.withType(JavaCompile).configureEach {
    options.compilerArgs += ["-parameters"]
}
```

### Swagger UI Shows "Unable to render definition"

**Problem**: Swagger UI displays error "Unable to render definition".

**Solution**: Ensure `ByteArrayHttpMessageConverter` is registered when overriding converters:

```java
converters.add(new ByteArrayHttpMessageConverter());
converters.add(new MappingJackson2HttpMessageConverter());
```

**Alternative approach**: Check for missing message converter configuration in your WebMvcConfigurer or similar configuration.

### Endpoints Not Appearing in Documentation

**Problem**: API endpoints are not showing up in the generated OpenAPI specification.

**Solution**: Check these common issues:

1. **Package scanning configuration**:
   ```properties
   # Ensure this is set correctly
   springdoc.packages-to-scan=com.example.controller

   # Or multiple packages
   springdoc.packages-to-scan=com.example.controller,com.example.service
   ```

2. **Path matching configuration**:
   ```properties
   # Ensure paths match your endpoints
   springdoc.paths-to-match=/api/**,public/**
   ```

3. **Hidden endpoints**: Verify endpoints aren't marked with `@Hidden` annotation.

4. **Component scanning**: Ensure controllers are in packages that are component-scanned by Spring Boot.

### Security Configuration Issues

**Problem**: Spring Security blocks access to Swagger UI and OpenAPI endpoints.

**Solution**: Permit SpringDoc endpoints in Spring Security:

```java
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                .anyRequest().authenticated()
            )
            .build();
    }
}
```

### Maven/Gradle Build Issues

**Problem**: Build fails due to conflicting SpringDoc dependencies.

**Solution**: Ensure correct version compatibility:

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.8.13</version>
</dependency>
```

For WebFlux applications:
```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webflux-ui</artifactId>
    <version>2.8.13</version>
</dependency>
```

### JavaDoc Integration Issues

**Problem**: JavaDoc comments are not appearing in the API documentation.

**Solution**: Add the therapi-runtime-javadoc dependency:

```xml
<dependency>
    <groupId>com.github.therapi</groupId>
    <artifactId>therapi-runtime-javadoc</artifactId>
    <version>0.15.0</version>
    <scope>provided</scope>
</dependency>
```

### Kotlin Integration Issues

**Problem**: Kotlin classes or functions are not properly documented.

**Solution**: Use `@field:` annotation prefix for Kotlin properties:

```kotlin
@field:Schema(description = "Book title", example = "Clean Code")
@field:NotBlank
val title: String = ""
```

### Custom Serialization Issues

**Problem**: Custom serialized fields are not appearing in the API documentation.

**Solution**: Ensure proper Jackson configuration:

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
```

### Performance Issues

**Problem**: SpringDoc causes performance issues during startup.

**Solution**:
1. Use specific package scanning instead of scanning the entire classpath
2. Use path exclusions to filter out unwanted endpoints
3. Consider using grouped OpenAPI definitions

```java
@Bean
public GroupedOpenApi publicApi() {
    return GroupedOpenApi.builder()
        .group("public")
        .packagesToScan("com.example.controller.public")
        .pathsToMatch("/api/public/**")
        .pathsToExclude("/api/internal/**")
        .build();
}
```

### Version Compatibility Issues

**Problem**: SpringDoc works in development but not in production.

**Solution**:
1. Ensure consistent Spring Boot and SpringDoc versions
2. Check for environment-specific configurations
3. Verify production environment matches development setup

```properties
# Production-specific configuration
springdoc.swagger-ui.enabled=true
springdoc.api-docs.enabled=true
springdoc.show-actuator=true
```

### Error Response Documentation

**Problem**: Custom error responses are not properly documented.

**Solution**: Use `@Operation(hidden = true)` on exception handlers and define proper error response schemas:

```java
@ExceptionHandler(BookNotFoundException.class)
@ResponseStatus(HttpStatus.NOT_FOUND)
@Operation(hidden = true)
public ErrorResponse handleBookNotFound(BookNotFoundException ex) {
    return new ErrorResponse("BOOK_NOT_FOUND", ex.getMessage());
}

@Schema(description = "Error response")
public record ErrorResponse(
    @Schema(description = "Error code", example = "BOOK_NOT_FOUND")
    String code,

    @Schema(description = "Error message", example = "Book with ID 123 not found")
    String message
) {}
```

### Debugging Tips

1. **Check OpenAPI JSON directly**: Access `http://localhost:8080/v3/api-docs` to see the raw OpenAPI specification
2. **Enable debug logging**: Add `logging.level.org.springdoc=DEBUG` to application.properties
3. **Validate OpenAPI specification**: Use online validators like [Swagger Editor](https://editor.swagger.io/)
4. **Check SpringDoc version**: Ensure you're using a recent version with bug fixes

### Performance Optimization

1. **Reduce scope**: Use specific package scanning and path matching
2. **Cache configurations**: Reuse OpenAPI configurations where possible
3. **Group endpoints**: Use multiple grouped OpenAPI definitions instead of one large specification
4. **Disable unnecessary features**: Turn off features you don't use (e.g., actuator integration)

```properties
# Performance optimizations
springdoc.swagger-ui.enabled=true
springdoc.api-docs.enabled=true
springdoc.show-actuator=false
springdoc.writer-default-response-tags=false
springdoc.default-consumes-media-type=application/json
springdoc.default-produces-media-type=application/json
```