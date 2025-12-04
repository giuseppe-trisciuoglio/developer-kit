# Spring Security JWT Skill

## Overview

This comprehensive Spring Security JWT skill provides production-ready implementations for JWT-based authentication and authorization in Spring Boot applications. It covers advanced patterns including token rotation, multi-tenancy, microservices integration, and both RBAC and permission-based access control.

## Quick Start

### 1. Add Dependencies

```xml
<!-- Maven -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-jose</artifactId>
</dependency>
```

### 2. Basic Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/api/public/**").permitAll()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .addFilterBefore(jwtAuthenticationFilter(),
                UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

### 3. Generate JWT Token

```java
@Service
public class JwtTokenService {
    public AccessTokenResponse generateAccessToken(User user) {
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
            .issuer("my-app")
            .subject(user.getId().toString())
            .issuedAt(now)
            .expiresAt(now.plus(1, ChronoUnit.HOURS))
            .claim("roles", user.getAuthorities())
            .build();

        String token = jwtEncoder.encode(
            JwtEncoderParameters.from(claims)).getTokenValue();

        return new AccessTokenResponse(token,
            now.plus(1, ChronoUnit.HOURS).toEpochMilli());
    }
}
```

## Features

### Core JWT Features
- ✅ JWT generation and validation with RSA/HMAC/ECDSA
- ✅ Access and refresh token pattern
- ✅ Token rotation and revocation
- ✅ Secure key management and rotation
- ✅ Token blacklisting support

### Authentication Patterns
- ✅ Bearer token authentication
- ✅ Cookie-based authentication
- ✅ Database-backed user stores
- ✅ OAuth2 provider integration
- ✅ Multi-factor authentication support

### Authorization Models
- ✅ Role-Based Access Control (RBAC)
- ✅ Permission-based authorization
- ✅ Attribute-Based Access Control (ABAC)
- ✅ Time-based access control
- ✅ Location-based restrictions
- ✅ Organizational access control

### Advanced Features
- ✅ Multi-tenancy support
- ✅ Microservices security patterns
- ✅ API gateway integration
- ✅ Service-to-service authentication
- ✅ Distributed token validation
- ✅ Event-driven security

### Security Hardening
- ✅ Brute force protection
- ✅ Rate limiting
- ✅ CSRF protection
- ✅ Security headers
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ Security monitoring and alerting

## Usage Examples

### 1. Simple JWT Authentication

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        Authentication auth = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(
                request.username(), request.password()));

        String token = tokenService.generateToken(
            (User) auth.getPrincipal());

        return ResponseEntity.ok(new AuthResponse(token));
    }
}
```

### 2. Permission-Based Authorization

```java
@PreAuthorize("hasPermission(#customerId, 'CUSTOMER_READ')")
public Customer getCustomer(Long customerId) {
    return customerService.findById(customerId);
}

@PreAuthorize("hasRole('ADMIN') or hasPermission(#orderId, 'ORDER', 'APPROVE')")
public Order approveOrder(Long orderId) {
    return orderService.approve(orderId);
}
```

### 3. Refresh Token Implementation

```java
@Service
public class RefreshTokenService {

    public RefreshTokenResponse refreshToken(RefreshTokenRequest request) {
        String refreshToken = request.refreshToken();

        // Validate refresh token
        RefreshToken token = refreshTokenRepository.findByToken(refreshToken)
            .orElseThrow(() -> new InvalidTokenException("Invalid refresh token"));

        if (token.isExpired()) {
            refreshTokenRepository.delete(token);
            throw new ExpiredTokenException("Refresh token expired");
        }

        // Generate new access token
        User user = token.getUser();
        String accessToken = jwtTokenService.generateAccessToken(user);

        return new RefreshTokenResponse(accessToken, refreshToken);
    }
}
```

## Testing

### Run the Test Suite

```bash
# Make the test script executable
chmod +x scripts/test-jwt-setup.sh

# Run all tests
./scripts/test-jwt-setup.sh

# Run with custom configuration
BASE_URL=http://localhost:8080 TEST_EMAIL=admin@example.com ./scripts/test-jwt-setup.sh
```

### Test Coverage

The test suite covers:
- ✅ User registration and authentication
- ✅ JWT token generation and validation
- ✅ Refresh token flow
- ✅ Token revocation on logout
- ✅ Role-based access control
- ✅ Security headers validation
- ✅ Rate limiting verification

## Security Best Practices

### 1. Token Security
- Use short-lived access tokens (15-30 minutes)
- Implement secure refresh token storage
- Use asymmetric keys (RSA 2048+ or ECDSA)
- Implement key rotation strategy
- Validate all JWT claims

### 2. Configuration Security
```yaml
jwt:
  access-token-expiration: "PT15M"
  refresh-token-expiration: "P7D"
  issuer: "https://auth.myapp.com"
  audience: "myapp-client"

spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          jwk-set-uri: "https://auth.myapp.com/.well-known/jwks.json"
```

### 3. Password Security
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new Argon2PasswordEncoder(
        16,    // salt length
        32,    // hash length
        1,     // parallelism
        65536, // memory
        3      // iterations
    );
}
```

## Performance Optimization

### 1. Caching Strategy
```java
@Service
public class CachedTokenValidationService {

    @Cacheable(value = "tokenValidation", key = "#token")
    public TokenValidationResult validateToken(String token) {
        return performValidation(token);
    }
}
```

### 2. Async Processing
```java
@Async("tokenProcessingExecutor")
public CompletableFuture<Void> processTokenInBackground(
        String token, String action) {
    // Process token without blocking
    return CompletableFuture.completedFuture(null);
}
```

### 3. Monitoring Metrics
```java
@Component
public class JwtMetricsCollector {
    public void recordTokenGenerated() {
        tokenGenerationCounter.increment();
    }

    public void recordTokenValidationTime(Timer.Sample sample) {
        sample.stop(tokenValidationTimer);
    }
}
```

## Troubleshooting

### Common Issues

1. **Token Not Accepted (401)**
   - Check token format: `header.payload.signature`
   - Verify token expiration
   - Validate key configuration
   - Check audience/issuer claims

2. **Signature Verification Failed**
   - Verify correct key is being used
   - Check if key rotation occurred
   - Validate algorithm matches

3. **Performance Issues**
   - Enable token validation caching
   - Check database connection pool
   - Monitor JWT processing time

### Debug Tools

```bash
# Decode JWT token
echo "eyJhbGci..." | cut -d. -f2 | base64 -d | jq .

# Check service health
curl http://localhost:8080/actuator/health

# Validate token with debug
curl -H "X-Auth-Debug: true" -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/users/me
```

## References

- [JWT Configuration](references/jwt-configuration.md)
- [Implementation Examples](references/examples.md)
- [Authorization Patterns](references/authorization-patterns.md)
- [Token Management](references/token-management.md)
- [Microservices Security](references/microservices-security.md)
- [OAuth2 Integration](references/oauth2-integration.md)
- [Testing JWT Security](references/testing-jwt-security.md)
- [Performance Optimization](references/performance-optimization.md)
- [Security Hardening](references/security-hardening.md)
- [Troubleshooting Guide](references/troubleshooting.md)

## Integration with Other Skills

This JWT security skill integrates seamlessly with:

- **spring-boot-actuator**: For security monitoring and health checks
- **spring-boot-cache**: For token validation caching
- **spring-data-jpa**: For user and token persistence
- **junit-test**: For comprehensive security testing
- **langchain4j**: For AI-powered security analysis

## Contributing

When contributing to this skill:

1. Follow the existing code patterns and structure
2. Add comprehensive tests for new features
3. Update documentation
4. Consider security implications
5. Ensure backward compatibility

## License

This skill follows the same license as the parent project.

## Support

For questions or issues:

1. Check the troubleshooting guide
2. Review the examples
3. Search existing issues
4. Create a new issue with detailed information

---

**Remember**: Security is an ongoing process. Regularly review and update your JWT implementation to address new vulnerabilities and follow best practices.