# JWT Complete Configuration Guide

This guide consolidates all JWT configuration patterns for Spring Boot 3.5.x with Spring Security 6.x, covering JJWT library integration, Spring Security OAuth2 resource server configuration, and production-ready security settings.

## Table of Contents

1. [Application Properties](#application-properties)
2. [Security Configuration](#security-configuration)
3. [JWT Service Configuration](#jwt-service-configuration)
4. [OAuth2 Resource Server](#oauth2-resource-server)
5. [Advanced Configuration](#advanced-configuration)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

## Application Properties

### Basic JWT Configuration

```yaml
# application.yml
jwt:
  # Signing key (minimum 256 bits for HS256)
  secret: ${JWT_SECRET:your-256-bit-secret-key-here-at-least-32-characters}

  # Token expiration times
  access-token-expiration: 900000    # 15 minutes in milliseconds
  refresh-token-expiration: 604800000 # 7 days in milliseconds

  # JWT issuer
  issuer: ${JWT_ISSUER:your-application-name}

  # Cookie settings for token storage
  cookie:
    name: ${JWT_COOKIE_NAME:jwt-token}
    secure: ${JWT_COOKIE_SECURE:true}  # true in production with HTTPS
    http-only: true
    same-site: ${JWT_COOKIE_SAME_SITE:strict}
    max-age: ${JWT_COOKIE_MAX_AGE:86400}
    domain: ${JWT_COOKIE_DOMAIN:your-domain.com}
    path: /

# Spring Security OAuth2 Resource Server
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI:https://your-auth-server.com}
          jwk-set-uri: ${JWT_JWK_SET_URI:https://your-auth-server.com/.well-known/jwks.json}
          public-key-location: ${JWT_PUBLIC_KEY_LOCATION:classpath:public.pem}
```

### Environment-Specific Configuration

```yaml
---
# Development profile
spring:
  config:
    activate:
      on-profile: dev

jwt:
  cookie:
    secure: false
    same-site: lax
logging:
  level:
    io.jsonwebtoken: DEBUG
    org.springframework.security: DEBUG

---
# Production profile
spring:
  config:
    activate:
      on-profile: prod

jwt:
  cookie:
    secure: true
    same-site: strict
    domain: api.yourdomain.com
  secret: ${JWT_SECRET}  # Must be provided via environment variable
```

## Security Configuration

### Modern Spring Security 6.x Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final AuthenticationProvider authenticationProvider;
    private final LogoutHandler logoutHandler;
    private final JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .exceptionHandling(ex ->
                ex.authenticationEntryPoint(jwtAuthenticationEntryPoint)
            )
            .authorizeHttpRequests(authz -> authz
                // Public endpoints
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()

                // Swagger/OpenAPI
                .requestMatchers(HttpMethod.GET, "/api-docs/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/swagger-ui/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/swagger-ui.html").permitAll()

                // Admin endpoints
                .requestMatchers("/api/admin/**").hasRole("ADMIN")

                // All other endpoints require authentication
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider)
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")
                .addLogoutHandler(logoutHandler)
                .logoutSuccessHandler((request, response, authentication) ->
                    SecurityContextHolder.clearContext()
                )
            );

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(getAllowedOrigins());
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    private List<String> getAllowedOrigins() {
        return List.of(
            "http://localhost:3000",
            "http://localhost:4200",
            "https://yourdomain.com"
        );
    }
}
```

### JWT Authentication Filter

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;
    private final TokenBlacklistService blacklistService;

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        final String authHeader = request.getHeader("Authorization");
        final String jwt;
        final String userEmail;

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        jwt = authHeader.substring(7);

        // Check if token is blacklisted
        if (blacklistService.isBlacklisted(jwt)) {
            log.warn("Blacklisted JWT token detected");
            filterChain.doFilter(request, response);
            return;
        }

        try {
            userEmail = jwtService.extractUsername(jwt);
        } catch (JwtException e) {
            log.error("Invalid JWT token: {}", e.getMessage());
            filterChain.doFilter(request, response);
            return;
        }

        if (userEmail != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(userEmail);

            if (jwtService.isTokenValid(jwt, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                        userDetails,
                        null,
                        userDetails.getAuthorities()
                );
                authToken.setDetails(
                    new WebAuthenticationDetailsSource().buildDetails(request)
                );
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

## JWT Service Configuration

### JWT Service Implementation

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class JwtService {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.access-token-expiration}")
    private long accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration;

    @Value("${jwt.issuer}")
    private String issuer;

    private final SecretKeyRepository secretKeyRepository;
    private final CacheManager cacheManager;

    public String generateToken(UserDetails userDetails) {
        return generateToken(new HashMap<>(), userDetails);
    }

    public String generateToken(Map<String, Object> extraClaims, UserDetails userDetails) {
        return buildToken(extraClaims, userDetails, accessTokenExpiration);
    }

    public String generateRefreshToken(UserDetails userDetails) {
        return buildToken(new HashMap<>(), userDetails, refreshTokenExpiration);
    }

    private String buildToken(
            Map<String, Object> extraClaims,
            UserDetails userDetails,
            long expiration
    ) {
        SecretKey signingKey = getCurrentSigningKey();

        return Jwts.builder()
                .setClaims(extraClaims)
                .setSubject(userDetails.getUsername())
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .setIssuer(issuer)
                .setId(UUID.randomUUID().toString())
                .claim("authorities", userDetails.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toList()))
                .signWith(signingKey, SignatureAlgorithm.HS256)
                .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String username = extractUsername(token);
        return (username.equals(userDetails.getUsername())) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private Claims extractAllClaims(String token) {
        SecretKey signingKey = getCurrentSigningKey();

        return Jwts.parserBuilder()
                .setSigningKey(signingKey)
                .requireIssuer(issuer)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    private SecretKey getCurrentSigningKey() {
        return secretKeyRepository.findCurrentKey()
                .map(SecretKeyEntity::getKey)
                .orElseGet(() -> {
                    SecretKey newKey = Keys.secretKeyFor(SignatureAlgorithm.HS256);
                    secretKeyRepository.save(new SecretKeyEntity(newKey, LocalDateTime.now()));
                    return newKey;
                });
    }
}
```

### Key Rotation Configuration

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class JwtKeyRotationService {

    private final SecretKeyRepository keyRepository;
    private final CacheManager cacheManager;
    private final ApplicationEventPublisher eventPublisher;

    @Value("${jwt.key-rotation.enabled:true}")
    private boolean keyRotationEnabled;

    @Value("${jwt.key-rotation.cron:0 0 0 * * ?}")
    private String rotationCron;

    @Scheduled(cron = "${jwt.key-rotation.cron}")
    public void rotateKeys() {
        if (!keyRotationEnabled) {
            log.info("JWT key rotation is disabled");
            return;
        }

        try {
            SecretKey newKey = Keys.secretKeyFor(SignatureAlgorithm.HS256);
            SecretKeyEntity keyEntity = new SecretKeyEntity(newKey, LocalDateTime.now());

            keyRepository.save(keyEntity);

            // Clear cache
            cacheManager.getCache("jwt-keys").clear();

            // Publish key rotation event
            eventPublisher.publishEvent(new KeyRotatedEvent(this, keyEntity.getId()));

            log.info("JWT signing key rotated successfully");
        } catch (Exception e) {
            log.error("Failed to rotate JWT signing key", e);
        }
    }

    public SecretKey getCurrentSigningKey() {
        return keyRepository.findCurrentKey()
                .map(SecretKeyEntity::getKey)
                .orElseThrow(() -> new IllegalStateException("No signing key available"));
    }
}
```

## OAuth2 Resource Server

### Pure Resource Server Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class ResourceServerConfig {

    @Value("${spring.security.oauth2.resourceserver.jwt.issuer-uri}")
    private String issuerUri;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .jwtDecoder(jwtDecoder())
                )
            );

        return http.build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        return JwtDecoders.fromIssuerLocation(issuerUri);
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter authoritiesConverter = new JwtGrantedAuthoritiesConverter();
        authoritiesConverter.setAuthorityPrefix("ROLE_");
        authoritiesConverter.setAuthoritiesClaimName("roles");

        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(authoritiesConverter);
        return converter;
    }
}
```

### Custom JWT Decoder

```java
@Component
@RequiredArgsConstructor
public class CustomJwtDecoder implements JwtDecoder {

    private final NimbusJwtDecoder nimbusJwtDecoder;
    private final TokenBlacklistService blacklistService;

    @Override
    public Jwt decode(String token) throws JwtException {
        // Check blacklist
        if (blacklistService.isBlacklisted(token)) {
            throw new BadJwtException("Token has been blacklisted");
        }

        // Decode token
        Jwt jwt = nimbusJwtDecoder.decode(token);

        // Custom validation
        validateCustomClaims(jwt);

        return jwt;
    }

    private void validateCustomClaims(Jwt jwt) {
        // Add custom claim validation logic
        Map<String, Object> claims = jwt.getClaims();

        // Example: Validate tenant claim
        if (!claims.containsKey("tenant_id")) {
            throw new BadJwtException("Missing tenant_id claim");
        }

        // Example: Validate IP address
        String tokenIp = (String) claims.get("ip_address");
        if (tokenIp != null && !tokenIp.equals(getCurrentIpAddress())) {
            throw new BadJwtException("Token IP mismatch");
        }
    }
}
```

## Advanced Configuration

### Token Blacklisting

```java
@Service
@RequiredArgsConstructor
public class TokenBlacklistService {

    private final RedisTemplate<String, String> redisTemplate;
    private static final String BLACKLIST_PREFIX = "blacklist:jwt:";

    @Value("${jwt.blacklist.enabled:true}")
    private boolean blacklistEnabled;

    public void blacklistToken(String token) {
        if (!blacklistEnabled) {
            return;
        }

        try {
            String tokenId = extractTokenId(token);
            long expirationTime = calculateRemainingTime(token);

            redisTemplate.opsForValue().set(
                BLACKLIST_PREFIX + tokenId,
                "1",
                expirationTime,
                TimeUnit.MILLISECONDS
            );

            log.info("Token blacklisted: {}", tokenId);
        } catch (Exception e) {
            log.error("Failed to blacklist token", e);
        }
    }

    public boolean isBlacklisted(String token) {
        if (!blacklistEnabled) {
            return false;
        }

        try {
            String tokenId = extractTokenId(token);
            return Boolean.TRUE.equals(redisTemplate.hasKey(BLACKLIST_PREFIX + tokenId));
        } catch (Exception e) {
            log.error("Failed to check token blacklist", e);
            return false;
        }
    }

    private String extractTokenId(String token) {
        // Extract JTI claim or generate from token hash
        return DigestUtils.md5DigestAsHex(token.getBytes());
    }

    private long calculateRemainingTime(String token) {
        // Parse token and calculate remaining time
        try {
            Jwt jwt = JwtHelper.decode(token);
            Map<String, Object> claims = jwt.getClaims();
            Long exp = (Long) claims.get("exp");
            if (exp != null) {
                return exp * 1000 - System.currentTimeMillis();
            }
        } catch (Exception e) {
            log.error("Failed to calculate token expiration", e);
        }
        return 0;
    }
}
```

### Rate Limiting

```java
@Configuration
@EnableCaching
public class RateLimitConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("login-attempts", "jwt-requests");
    }
}

@Component
@RequiredArgsConstructor
public class JwtRateLimitService {

    private final CacheManager cacheManager;

    @Value("${jwt.rate-limit.enabled:true}")
    private boolean rateLimitEnabled;

    @Value("${jwt.rate-limit.max-attempts:5}")
    private int maxAttempts;

    @Value("${jwt.rate-limit.time-window:300000}") // 5 minutes
    private long timeWindow;

    public boolean isRateLimited(String identifier) {
        if (!rateLimitEnabled) {
            return false;
        }

        Cache cache = cacheManager.getCache("jwt-requests");
        String key = "rate-limit:" + identifier;

        AtomicInteger attempts = cache.get(key, AtomicInteger.class);
        if (attempts == null) {
            attempts = new AtomicInteger(0);
            cache.put(key, attempts);
        }

        int currentAttempts = attempts.incrementAndGet();

        if (currentAttempts >= maxAttempts) {
            log.warn("Rate limit exceeded for identifier: {}", identifier);
            return true;
        }

        return false;
    }
}
```

## Performance Optimization

### JWT Parsing Optimization

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class OptimizedJwtService {

    private final CacheManager cacheManager;
    private final SecretKeyRepository keyRepository;

    @Cacheable(value = "jwt-parsing", key = "#token")
    public Claims parseToken(String token) {
        SecretKey key = getCurrentSigningKey();

        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    @Cacheable(value = "signing-keys", key = "'current'")
    public SecretKey getCurrentSigningKey() {
        return keyRepository.findCurrentKey()
                .map(SecretKeyEntity::getKey)
                .orElseThrow(() -> new IllegalStateException("No signing key available"));
    }

    public String generateTokenOptimized(UserDetails userDetails) {
        // Pre-calculate common claims
        Map<String, Object> claims = new HashMap<>();
        claims.put("authorities", userDetails.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toList()));
        claims.put("user_id", ((User) userDetails).getId());
        claims.put("email", ((User) userDetails).getEmail());

        return buildToken(claims, userDetails, accessTokenExpiration);
    }
}
```

### Connection Pool Configuration

```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000
      max-lifetime: 1200000
      connection-timeout: 20000
      validation-timeout: 5000
      leak-detection-threshold: 60000

  redis:
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5
        max-wait: 5000ms
```

## Troubleshooting

### Common Configuration Issues

1. **Invalid Key Length**
   ```
   Error: The signing key's size is 184 bits which is not secure enough for the HS256 algorithm.
   Solution: Use a key of at least 256 bits (32 characters) for HS256.
   ```

2. **Clock Skew Issues**
   ```java
   // Add clock skew tolerance
   Jwts.parserBuilder()
       .setAllowedClockSkewSeconds(60) // 60 seconds tolerance
       .build()
       .parseClaimsJws(token);
   ```

3. **Issuer Mismatch**
   ```java
   // Always set and validate issuer
   Jwts.parserBuilder()
       .requireIssuer("your-app-name")
       .build()
       .parseClaimsJws(token);
   ```

### Debug Configuration

```yaml
# application.yml
logging:
  level:
    io.jsonwebtoken: DEBUG
    org.springframework.security: DEBUG
    org.springframework.security.oauth2: DEBUG

# Enable request/response logging
spring:
  mvc:
    log-request-details: true
```

### Health Check Endpoint

```java
@Component
public class JwtHealthIndicator implements HealthIndicator {

    private final JwtService jwtService;

    @Override
    public Health health() {
        try {
            // Test JWT signing and parsing
            String testToken = jwtService.generateTestToken();
            boolean isValid = jwtService.validateToken(testToken);

            if (isValid) {
                return Health.up()
                    .withDetail("jwt", "Service is working")
                    .build();
            } else {
                return Health.down()
                    .withDetail("jwt", "Token validation failed")
                    .build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("jwt", "Service error: " + e.getMessage())
                .build();
        }
    }
}
```

## References

- [JJWT Documentation](https://github.com/jwtk/jjwt)
- [Spring Security OAuth2 Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 8725 - JWT Best Practices](https://tools.ietf.org/html/rfc8725)