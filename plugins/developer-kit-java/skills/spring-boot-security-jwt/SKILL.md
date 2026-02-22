---
name: spring-boot-security-jwt
description: Provides JWT authentication and authorization patterns for Spring Boot 3.5.x covering token generation with JJWT, Bearer/cookie authentication, database/OAuth2 integration, and RBAC/permission-based access control using Spring Security 6.x. Use when implementing authentication or authorization in Spring Boot applications.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
category: backend
tags: [spring-boot, spring-security, jwt, authentication, authorization, rbac, oauth2, jjwt]
version: 2.2.0
---

# Spring Boot JWT Security

Comprehensive JWT authentication and authorization patterns for Spring Boot 3.5.x applications using Spring Security 6.x and the JJWT library.

## Overview

JWT authentication enables stateless, scalable security for Spring Boot applications. This skill covers complete JWT lifecycle management including token generation, validation, refresh strategies, and integration patterns with database-backed and OAuth2 authentication providers.

## When to Use

- Implementing stateless authentication for REST APIs
- Building SPA backends with JWT
- Securing microservices with token-based authentication
- Integrating with OAuth2 providers (Google, GitHub, etc.)
- Implementing role-based or permission-based access control
- Setting up JWT refresh token strategies
- Building mobile API backends

## Instructions

### 1. Add Dependencies

Include spring-boot-starter-security, spring-boot-starter-oauth2-resource-server, and JJWT library (jjwt-api, jjwt-impl, jjwt-jackson).

### 2. Configure JWT Properties

Set JWT secret, access token expiration, refresh token expiration, and issuer in application.yml. Never hardcode secrets.

### 3. Create JWT Service

Implement JwtService with methods to generate tokens, extract claims, validate tokens, and check expiration using `Jwts.builder()`.

### 4. Implement JWT Filter

Create JwtAuthenticationFilter extending OncePerRequestFilter. Extract JWT from Authorization header or cookie, validate, and set SecurityContext.

### 5. Configure Security Filter Chain

Set up SecurityConfig with @EnableWebSecurity and @EnableMethodSecurity. Configure stateless session management, CSRF disabled, and authorization rules.

### 6. Create Authentication Endpoints

Implement /register, /authenticate, /refresh, and /logout endpoints returning access and refresh tokens.

### 7. Implement Refresh Token Strategy

Store refresh tokens in database with expiration and revocation status. Implement token rotation.

### 8. Add Authorization Rules

Apply @PreAuthorize annotations with role-based (hasRole) or permission-based (hasAuthority) checks.

### 9. Test Security Configuration

Write tests for authentication success/failure, authorization access control, and token validation.

## Examples

### Application Configuration

```yaml
jwt:
  secret: ${JWT_SECRET:my-very-secret-key-that-is-at-least-256-bits-long}
  access-token-expiration: 86400000    # 24 hours
  refresh-token-expiration: 604800000  # 7 days
  issuer: spring-boot-jwt-example
  cookie-name: jwt-token
  cookie-http-only: true
```

### Security Filter Chain

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final AuthenticationProvider authenticationProvider;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

### JWT Token Generation (Core)

```java
import java.time.Instant;

private String generateToken(UserDetails userDetails, long expiration) {
    return Jwts.builder()
            .subject(userDetails.getUsername())
            .issuer(issuer)
            .issuedAt(Date.from(Instant.now()))
            .expiration(Date.from(Instant.now().plusMillis(expiration)))
            .claim("authorities", getAuthorities(userDetails))
            .signWith(getSigningKey(), Jwts.SIG.HS256)
            .compact();
}

private SecretKey getSigningKey() {
    byte[] keyBytes = secret.getBytes(StandardCharsets.UTF_8);
    return Keys.hmacShaKeyFor(keyBytes);
}
```

## Best Practices

- **Always use HTTPS** in production for JWT token transmission
- **Set appropriate cookie flags**: `HttpOnly`, `Secure`, `SameSite`
- **Use strong secret keys**: minimum 256 bits for HMAC algorithms
- **Implement token expiration**: Never use tokens with infinite lifetime
- **Implement key rotation**: Regularly rotate signing keys
- **Use token blacklisting**: For logout and security incidents (e.g., Redis-based)
- **Cache user details** to avoid database hits on every request
- **Monitor authentication events** with Spring Security event listeners

## Constraints and Warnings

- JWT tokens should stay under HTTP header size limits (typically 8KB)
- Never store sensitive information in JWT tokens (claims are not encrypted, only signed)
- Implement proper token revocation strategies for logout
- Use different keys for different environments (dev, staging, prod)
- Do not validate JWT signatures on the client side
- Always validate token issuer (`iss`) and audience (`aud`) claims

## References

- [Complete JWT Configuration Guide](references/jwt-complete-configuration.md)
- [JWT Testing Guide](references/jwt-testing-guide.md)
- [JWT Quick Reference](references/jwt-quick-reference.md)
- [Authorization Patterns](references/authorization-patterns.md)
- [OAuth2 Integration](references/oauth2-integration.md)
- [Token Management](references/token-management.md)
- [Security Hardening](references/security-hardening.md)
- [Migration Guide for Spring Security 6.x](references/migration-spring-security-6x.md)
- [Complete Examples](references/examples.md)
- [Configuration Reference](references/configuration.md)

## Related Skills

- `spring-boot-dependency-injection` - Constructor injection patterns
- `spring-boot-rest-api-standards` - REST API security patterns
- `unit-test-security-authorization` - Testing Spring Security configurations
- `spring-data-jpa` - User entity and repository patterns
