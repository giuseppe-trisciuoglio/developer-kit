# JWT Security Configuration Reference

This document provides comprehensive configuration options for JWT security in Spring Boot applications using JJWT library and Spring Security 6.x.

## Table of Contents

1. [Application Properties](#application-properties)
2. [JWT Configuration Beans](#jwt-configuration-beans)
3. [Security Filter Chain Options](#security-filter-chain-options)
4. [Token Validation Configuration](#token-validation-configuration)
5. [Key Management](#key-management)
6. [CORS and CSRF Configuration](#cors-and-csrf-configuration)
7. [Session Management](#session-management)
8. [Error Handling Configuration](#error-handling-configuration)
9. [Performance Configuration](#performance-configuration)
10. [Monitoring and Audit Configuration](#monitoring-and-audit-configuration)

## Application Properties

### Complete JWT Configuration (application.yml)

```yaml
# JWT Configuration
jwt:
  # Token settings
  secret: ${JWT_SECRET:my-very-secret-key-that-is-at-least-256-bits-long-for-hmac-sha256}
  access-token-expiration: 900000          # 15 minutes in milliseconds
  refresh-token-expiration: 604800000     # 7 days in milliseconds
  issuer: ${JWT_ISSUER:spring-boot-jwt-app}
  audience: ${JWT_AUDIENCE:spring-boot-client}

  # Cookie settings
  cookie-name: jwt-token
  cookie-secure: ${JWT_COOKIE_SECURE:false} # Set to true in production with HTTPS
  cookie-http-only: true
  cookie-same-site: lax                   # strict, lax, or none
  cookie-domain: ${JWT_COOKIE_DOMAIN:}    # Optional domain
  cookie-path: /
  cookie-max-age: 86400                   # 24 hours

  # Token validation
  validate-issuer: true
  validate-audience: false
  validate-expiration: true
  clock-skew-seconds: 60                  # Allow 60 seconds clock skew

  # Refresh token settings
  refresh-token-limit: 5                  # Max active refresh tokens per user
  refresh-token-rotation-enabled: true
  refresh-token-cleanup-enabled: true
  refresh-token-cleanup-cron: "0 0 2 * * ?" # Daily at 2 AM

  # Security settings
  blacklist-enabled: true
  blacklist-cleanup-enabled: true
  blacklist-cleanup-cron: "0 0 3 * * ?"    # Daily at 3 AM

# Spring Security Configuration
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, profile, email
            redirect-uri: "{baseUrl}/login/oauth2/code/google"
            client-name: Google
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope: user:email
            redirect-uri: "{baseUrl}/login/oauth2/code/github"
            client-name: GitHub
        provider:
          google:
            authorization-uri: https://accounts.google.com/o/oauth2/v2/auth
            token-uri: https://oauth2.googleapis.com/token
            user-info-uri: https://www.googleapis.com/oauth2/v2/userinfo
          github:
            authorization-uri: https://github.com/login/oauth/authorize
            token-uri: https://github.com/login/oauth/access_token
            user-info-uri: https://api.github.com/user

  # Session configuration (if needed)
  session:
    store-type: none                      # Use stateless sessions
    timeout: 30m                          # Session timeout
    jdbc:
      initialize-schema: always

  # CORS configuration
  web:
    cors:
      allowed-origins: ${CORS_ALLOWED_ORIGINS:http://localhost:3000,http://localhost:8080}
      allowed-methods: GET,POST,PUT,DELETE,OPTIONS
      allowed-headers: "*"
      allow-credentials: true
      max-age: 3600

# Logging configuration
logging:
  level:
    org.springframework.security: DEBUG
    io.jsonwebtoken: DEBUG
    com.example.security: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# Management endpoints for monitoring
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when_authorized
  security:
    enabled: true
```

## JWT Configuration Beans

### JWT Service Configuration

```java
@Configuration
@RequiredArgsConstructor
public class JwtConfig {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.access-token-expiration}")
    private long accessTokenExpiration;

    @Value("${jwt.refresh-token-expiration}")
    private long refreshTokenExpiration;

    @Value("${jwt.issuer}")
    private String issuer;

    @Value("${jwt.audience:}")
    private String audience;

    @Value("${jwt.validate-issuer:true}")
    private boolean validateIssuer;

    @Value("${jwt.validate-audience:false}")
    private boolean validateAudience;

    @Value("${jwt.clock-skew-seconds:60}")
    private int clockSkewSeconds;

    @Bean
    public JwtService jwtService(RefreshTokenService refreshTokenService) {
        return new JwtService(
            secret,
            accessTokenExpiration,
            refreshTokenExpiration,
            issuer,
            audience,
            validateIssuer,
            validateAudience,
            clockSkewSeconds,
            refreshTokenService
        );
    }

    @Bean
    public JwtParser jwtParser() {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .requireIssuer(issuer)
                .setAllowedClockSkewSeconds(clockSkewSeconds)
                .build();
    }

    @Bean
    public SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(
            Base64.getEncoder().encodeToString(secret.getBytes())
        );
        return Keys.hmacShaKeyFor(keyBytes);
    }

    @Bean
    public ClaimsSetExtractor claimsSetExtractor() {
        return new DefaultClaimsSetExtractor(
            issuer,
            audience,
            Duration.ofMillis(accessTokenExpiration)
        );
    }
}
```

### Custom JWT Parser with Validation

```java
@Configuration
public class JwtParserConfig {

    @Bean
    public JwtParser jwtParser(SecretKey signingKey, JwtProperties jwtProperties) {
        JwtParserBuilder parser = Jwts.parser()
                .verifyWith(signingKey)
                .setAllowedClockSkewSeconds(jwtProperties.getClockSkewSeconds());

        // Add required claims
        if (jwtProperties.isValidateIssuer()) {
            parser.requireIssuer(jwtProperties.getIssuer());
        }

        if (jwtProperties.isValidateAudience() &&
            StringUtils.hasText(jwtProperties.getAudience())) {
            parser.requireAudience(jwtProperties.getAudience());
        }

        return parser.build();
    }

    @Bean
    public JwtValidator jwtValidator(JwtParser jwtParser) {
        return new DefaultJwtValidator(jwtParser);
    }
}
```

### Configuration Properties Class

```java
@ConfigurationProperties(prefix = "jwt")
@Data
@Validated
public class JwtProperties {

    /**
     * JWT secret key for HMAC signing
     */
    @NotBlank
    @Size(min = 32, message = "JWT secret must be at least 32 characters")
    private String secret;

    /**
     * Access token expiration in milliseconds
     */
    @Min(60000) // Minimum 1 minute
    private long accessTokenExpiration = 900000; // 15 minutes

    /**
     * Refresh token expiration in milliseconds
     */
    @Min(3600000) // Minimum 1 hour
    private long refreshTokenExpiration = 604800000; // 7 days

    /**
     * JWT issuer
     */
    @NotBlank
    private String issuer;

    /**
     * JWT audience
     */
    private String audience;

    /**
     * Validate issuer claim
     */
    private boolean validateIssuer = true;

    /**
     * Validate audience claim
     */
    private boolean validateAudience = false;

    /**
     * Clock skew in seconds for token validation
     */
    @Min(0)
    private int clockSkewSeconds = 60;

    /**
     * Cookie configuration
     */
    private CookieProperties cookie = new CookieProperties();

    /**
     * Refresh token configuration
     */
    private RefreshTokenProperties refreshToken = new RefreshTokenProperties();

    /**
     * Blacklist configuration
     */
    private BlacklistProperties blacklist = new BlacklistProperties();

    @Data
    public static class CookieProperties {
        private String name = "jwt-token";
        private boolean secure = false;
        private boolean httpOnly = true;
        private String sameSite = "lax";
        private String domain;
        private String path = "/";
        private int maxAge = 86400;
    }

    @Data
    public static class RefreshTokenProperties {
        private int limit = 5;
        private boolean rotationEnabled = true;
        private boolean cleanupEnabled = true;
        private String cleanupCron = "0 0 2 * * ?";
    }

    @Data
    public static class BlacklistProperties {
        private boolean enabled = true;
        private boolean cleanupEnabled = true;
        private String cleanupCron = "0 0 3 * * ?";
    }
}
```

## Security Filter Chain Options

### Advanced Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
public class AdvancedSecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final AuthenticationProvider authenticationProvider;
    private final JwtAuthenticationEntryPoint authenticationEntryPoint;
    private final CustomAccessDeniedHandler accessDeniedHandler;
    private final SecurityCorsConfigurationSource corsConfigurationSource;
    private final LogoutHandler logoutHandler;
    private final SecurityContextRepository securityContextRepository;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            // CORS Configuration
            .cors(cors -> cors.configurationSource(corsConfigurationSource))

            // CSRF Configuration
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .ignoringRequestMatchers("/api/auth/**", "/api/public/**")
                .sessionAuthenticationStrategy(new NullSessionAuthenticationStrategy())
            )

            // Security Headers
            .headers(headers -> headers
                .contentSecurityPolicy(csp -> csp
                    .policyDirectives("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
                )
                .frameOptions().deny()
                .httpStrictTransportSecurity(hsts -> hsts
                    .maxAgeInSeconds(31536000)
                    .includeSubdomains(true)
                    .preload(true)
                )
                .permissionsPolicy(permissions -> permissions
                    .policy("camera=(), microphone=(), geolocation=()")
                )
                .referrerPolicy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)
            )

            // Session Management
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .sessionAuthenticationStrategy(sessionAuthenticationStrategy())
                .maximumSessions(10)
                .maxSessionsPreventsLogin(false)
                .sessionRegistry(sessionRegistry())
            )

            // Exception Handling
            .exceptionHandling(exceptions -> exceptions
                .authenticationEntryPoint(authenticationEntryPoint)
                .accessDeniedHandler(accessDeniedHandler)
            )

            // Request Authorization
            .authorizeHttpRequests(auth -> auth
                // Public endpoints
                .requestMatchers("/api/auth/**", "/api/public/**", "/health", "/actuator/health").permitAll()

                // Admin endpoints
                .requestMatchers("/api/admin/**").hasRole("ADMIN")

                // API endpoints with specific permissions
                .requestMatchers(HttpMethod.GET, "/api/users/**").hasAuthority("USER_READ")
                .requestMatchers(HttpMethod.POST, "/api/users/**").hasAuthority("USER_WRITE")
                .requestMatchers(HttpMethod.PUT, "/api/users/**").hasAuthority("USER_WRITE")
                .requestMatchers(HttpMethod.DELETE, "/api/users/**").hasAuthority("USER_DELETE")

                // OAuth2 endpoints
                .requestMatchers("/oauth2/**", "/login/oauth2/**").permitAll()

                // Actuator endpoints
                .requestMatchers("/actuator/**").hasRole("ADMIN")

                // All other requests require authentication
                .anyRequest().authenticated()
            )

            // OAuth2 Resource Server
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt
                    .decoder(jwtDecoder())
                    .jwtAuthenticationConverter(jwtAuthenticationConverter())
                )
                .accessDeniedHandler(accessDeniedHandler)
                .authenticationEntryPoint(authenticationEntryPoint)
            )

            // OAuth2 Login
            .oauth2Login(oauth2 -> oauth2
                .authorizationEndpoint(authorization -> authorization
                    .baseUri("/oauth2/authorization")
                )
                .redirectionEndpoint(redirection -> redirection
                    .baseUri("/login/oauth2/code/*")
                )
                .userInfoEndpoint(userInfo -> userInfo
                    .userService(oAuth2UserService())
                )
                .successHandler(oAuth2AuthenticationSuccessHandler())
                .failureHandler(oAuth2AuthenticationFailureHandler())
            )

            // Authentication Providers
            .authenticationProvider(authenticationProvider)

            // Filters
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .addFilterBefore(securityContextFilter(), UsernamePasswordAuthenticationFilter.class)
            .addFilterAfter(auditLoggingFilter(), UsernamePasswordAuthenticationFilter.class)

            // Logout Configuration
            .logout(logout -> logout
                .logoutUrl("/api/auth/logout")
                .addLogoutHandler(securityContextLogoutHandler())
                .addLogoutHandler(logoutHandler)
                .addLogoutHandler(cookieClearingLogoutHandler())
                .logoutSuccessHandler((request, response, authentication) ->
                    response.setStatus(HttpStatus.NO_CONTENT.value()))
                .deleteCookies("JSESSIONID", "jwt-token")
                .clearAuthentication(true)
                .invalidateHttpSession(true)
            )

            // Security Context Repository
            .securityContext(securityContextRepository)

            .build();
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withSecretKey(getSigningKey())
                .signatureAlgorithm(SignatureAlgorithm.HS256)
                .build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter authoritiesConverter = new JwtGrantedAuthoritiesConverter();
        authoritiesConverter.setAuthorityPrefix("ROLE_");
        authoritiesConverter.setAuthoritiesClaimName("authorities");

        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(authoritiesConverter);
        converter.setPrincipalClaimName("sub");
        converter.setPrincipalAttributeName("sub");

        return converter;
    }

    @Bean
    public OAuth2UserService<OAuth2UserRequest, OAuth2User> oAuth2UserService() {
        DefaultOAuth2UserService delegate = new DefaultOAuth2UserService();
        return new CustomOAuth2UserService(delegate);
    }

    @Bean
    public AuthenticationSuccessHandler oAuth2AuthenticationSuccessHandler() {
        return new OAuth2AuthenticationSuccessHandler(jwtService);
    }

    @Bean
    public AuthenticationFailureHandler oAuth2AuthenticationFailureHandler() {
        return new OAuth2AuthenticationFailureHandler();
    }

    @Bean
    public SessionAuthenticationStrategy sessionAuthenticationStrategy() {
        return new CompositeSessionAuthenticationStrategy(Arrays.asList(
            new RegisterSessionAuthenticationStrategy(sessionRegistry()),
            new CsrfAuthenticationStrategy()
        ));
    }

    @Bean
    public SessionRegistry sessionRegistry() {
        return new SessionRegistryImpl();
    }

    @Bean
    public SecurityContextRepository securityContextRepository() {
        return new JwtSecurityContextRepository(jwtService, userDetailsService);
    }

    @Bean
    public Filter securityContextFilter() {
        return new SecurityContextPersistenceFilter(securityContextRepository());
    }

    @Bean
    public Filter auditLoggingFilter() {
        return new AuditLoggingFilter();
    }

    @Bean
    public LogoutHandler securityContextLogoutHandler() {
        return new SecurityContextLogoutHandler();
    }

    @Bean
    public LogoutHandler cookieClearingLogoutHandler() {
        return new CookieClearingLogoutHandler("JSESSIONID", "jwt-token");
    }
}
```

## Token Validation Configuration

### Custom JWT Validator

```java
@Component
@RequiredArgsConstructor
public class CustomJwtValidator implements JwtValidator {

    private final JwtParser jwtParser;
    private final BlacklistedTokenService blacklistedTokenService;
    private final JwtProperties jwtProperties;

    @Override
    public ValidationResult validate(String token) {
        try {
            // Check if token is blacklisted
            if (jwtProperties.getBlacklist().isEnabled()) {
                String jti = extractClaim(token, "jti");
                if (blacklistedTokenService.isBlacklisted(jti)) {
                    return ValidationResult.error("Token is blacklisted");
                }
            }

            // Parse and validate token
            Claims claims = jwtParser.parseSignedClaims(token).getPayload();

            // Additional custom validations
            return validateCustomClaims(claims);

        } catch (ExpiredJwtException e) {
            return ValidationResult.error("Token has expired");
        } catch (UnsupportedJwtException e) {
            return ValidationResult.error("Token is unsupported");
        } catch (MalformedJwtException e) {
            return ValidationResult.error("Token is malformed");
        } catch (SecurityException e) {
            return ValidationResult.error("Token signature validation failed");
        } catch (IllegalArgumentException e) {
            return ValidationResult.error("Token is invalid");
        } catch (JwtException e) {
            return ValidationResult.error("JWT processing failed: " + e.getMessage());
        }
    }

    private ValidationResult validateCustomClaims(Claims claims) {
        // Validate issuer
        if (jwtProperties.isValidateIssuer() &&
            !claims.getIssuer().equals(jwtProperties.getIssuer())) {
            return ValidationResult.error("Invalid issuer");
        }

        // Validate audience
        if (jwtProperties.isValidateAudience()) {
            List<String> audiences = claims.getAudience();
            if (audiences == null || audiences.isEmpty() ||
                !audiences.contains(jwtProperties.getAudience())) {
                return ValidationResult.error("Invalid audience");
            }
        }

        // Validate token type
        String tokenType = claims.get("type", String.class);
        if (tokenType == null || !tokenType.equals("access")) {
            return ValidationResult.error("Invalid token type");
        }

        return ValidationResult.success();
    }

    private String extractClaim(String token, String claimName) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(getSigningKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
            return claims.get(claimName, String.class);
        } catch (JwtException e) {
            return null;
        }
    }

    @Value("${jwt.secret}")
    private String secret;

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(
            Base64.getEncoder().encodeToString(secret.getBytes())
        );
        return Keys.hmacShaKeyFor(keyBytes);
    }
}

@Data
@AllArgsConstructor
public class ValidationResult {
    private boolean valid;
    private String errorMessage;

    public static ValidationResult success() {
        return new ValidationResult(true, null);
    }

    public static ValidationResult error(String message) {
        return new ValidationResult(false, message);
    }
}
```

## Key Management

### Asymmetric Key Configuration

```java
@Configuration
@ConditionalOnProperty(name = "jwt.algorithm", havingValue = "RSA")
public class AsymmetricJwtConfig {

    @Value("${jwt.public-key}")
    private String publicKeyString;

    @Value("${jwt.private-key}")
    private String privateKeyString;

    @Bean
    public RSAPublicKey publicKey() throws Exception {
        return (RSAPublicKey) KeyFactory.getInstance("RSA")
                .generatePublic(new X509EncodedKeySpec(
                    Base64.getDecoder().decode(publicKeyString)
                ));
    }

    @Bean
    public RSAPrivateKey privateKey() throws Exception {
        return (RSAPrivateKey) KeyFactory.getInstance("RSA")
                .generatePrivate(new PKCS8EncodedKeySpec(
                    Base64.getDecoder().decode(privateKeyString)
                ));
    }

    @Bean
    public JwtDecoder jwtDecoder(RSAPublicKey publicKey) {
        return NimbusJwtDecoder.withPublicKey(publicKey)
                .signatureAlgorithm(SignatureAlgorithm.RS256)
                .build();
    }

    @Bean
    public JwtEncoder jwtEncoder(RSAPrivateKey privateKey) {
        RSASSASigner rsaSigner = new RSASSASigner(privateKey);
        return new NimbusJwtEncoder(
            new ImmutableJWEHeader(JWSAlgorithm.RS256),
            rsaSigner
        );
    }
}
```

### Key Rotation Support

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class KeyRotationService {

    private final KeyRepository keyRepository;
    private final Map<String, KeyPair> activeKeys = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    @PostConstruct
    public void initialize() {
        loadActiveKeys();
        scheduleKeyRotation();
    }

    @Scheduled(cron = "${jwt.key-rotation.cron:0 0 0 1 * ?}") // Monthly
    public void rotateKeys() {
        try {
            log.info("Starting JWT key rotation");

            // Generate new key pair
            KeyPair newKeyPair = generateKeyPair();

            // Save new key
            JwtKey newKey = JwtKey.builder()
                    .keyId(UUID.randomUUID().toString())
                    .publicKey(Base64.getEncoder().encodeToString(newKeyPair.getPublic().getEncoded()))
                    .privateKey(Base64.getEncoder().encodeToString(newKeyPair.getPrivate().getEncoded()))
                    .algorithm("RS256")
                    .createdAt(Instant.now())
                    .isActive(true)
                    .build();

            // Deactivate old keys
            keyRepository.deactivateAllKeys();

            // Save new key
            keyRepository.save(newKey);

            // Update active keys cache
            loadActiveKeys();

            log.info("JWT key rotation completed successfully");

        } catch (Exception e) {
            log.error("JWT key rotation failed", e);
        }
    }

    public KeyPair getCurrentKeyPair() {
        return activeKeys.values().iterator().next();
    }

    public KeyPair getKeyPair(String keyId) {
        return activeKeys.get(keyId);
    }

    private void loadActiveKeys() {
        List<JwtKey> activeJwtKeys = keyRepository.findByIsActiveTrue();

        activeKeys.clear();

        for (JwtKey key : activeJwtKeys) {
            try {
                KeyPair keyPair = restoreKeyPair(key);
                activeKeys.put(key.getKeyId(), keyPair);
            } catch (Exception e) {
                log.error("Failed to restore key pair for keyId: {}", key.getKeyId(), e);
            }
        }

        if (activeKeys.isEmpty()) {
            log.warn("No active keys found, generating new key pair");
            rotateKeys();
        }
    }

    private KeyPair generateKeyPair() throws NoSuchAlgorithmException {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
        keyPairGenerator.initialize(2048);
        return keyPairGenerator.generateKeyPair();
    }

    private KeyPair restoreKeyPair(JwtKey jwtKey) throws Exception {
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");

        byte[] publicKeyBytes = Base64.getDecoder().decode(jwtKey.getPublicKey());
        X509EncodedKeySpec publicKeySpec = new X509EncodedKeySpec(publicKeyBytes);
        RSAPublicKey publicKey = (RSAPublicKey) keyFactory.generatePublic(publicKeySpec);

        byte[] privateKeyBytes = Base64.getDecoder().decode(jwtKey.getPrivateKey());
        PKCS8EncodedKeySpec privateKeySpec = new PKCS8EncodedKeySpec(privateKeyBytes);
        RSAPrivateKey privateKey = (RSAPrivateKey) keyFactory.generatePrivate(privateKeySpec);

        return new KeyPair(publicKey, privateKey);
    }

    private void scheduleKeyRotation() {
        scheduler.scheduleAtFixedRate(
            this::rotateKeys,
            1,  // Initial delay
            30,  // Period (days)
            TimeUnit.DAYS
        );
    }
}
```

## CORS and CSRF Configuration

### Advanced CORS Configuration

```java
@Configuration
public class CorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // Allowed origins (configure based on environment)
        configuration.setAllowedOriginPatterns(Arrays.asList(
            "http://localhost:*",
            "https://*.yourdomain.com"
        ));

        // Allowed HTTP methods
        configuration.setAllowedMethods(Arrays.asList(
            "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"
        ));

        // Allowed headers
        configuration.setAllowedHeaders(Arrays.asList(
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ));

        // Exposed headers
        configuration.setExposedHeaders(Arrays.asList(
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page"
        ));

        // Allow credentials
        configuration.setAllowCredentials(true);

        // Max age for pre-flight requests
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        source.registerCorsConfiguration("/oauth2/**", configuration);

        return source;
    }
}
```

### Custom CSRF Configuration

```java
@Configuration
public class CsrfConfig {

    @Bean
    public CsrfTokenRepository csrfTokenRepository() {
        CookieCsrfTokenRepository repository = CookieCsrfTokenRepository.withHttpOnlyFalse();
        repository.setCookieName("XSRF-TOKEN");
        repository.setHeaderName("X-XSRF-TOKEN");
        repository.setCookieHttpOnly(false);
        repository.setCookiePath("/");

        // Set secure flag in production
        if (isProductionEnvironment()) {
            repository.setCookieSecure(true);
        }

        return repository;
    }

    @Bean
    public CsrfTokenRequestHandler csrfTokenRequestHandler() {
        return new CsrfTokenRequestAttributeHandler();
    }

    @Bean
    public CsrfTokenRequestHandler spaCsrfTokenRequestHandler() {
        return new SpaCsrfTokenRequestHandler();
    }

    private boolean isProductionEnvironment() {
        String[] activeProfiles = Environment.getActiveProfiles();
        return Arrays.asList(activeProfiles).contains("prod");
    }
}

// SPA CSRF handler for single-page applications
public class SpaCsrfTokenRequestHandler extends CsrfTokenRequestAttributeHandler {

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response,
            Supplier<CsrfToken> csrfToken) {

        String csrfTokenValue = csrfToken.get().getToken();
        response.setHeader("X-CSRF-TOKEN", csrfTokenValue);
        response.setHeader("Access-Control-Expose-Headers", "X-CSRF-TOKEN");
    }
}
```

This configuration reference provides comprehensive options for setting up JWT security in Spring Boot applications with various security features, key management strategies, and advanced configurations for production environments.