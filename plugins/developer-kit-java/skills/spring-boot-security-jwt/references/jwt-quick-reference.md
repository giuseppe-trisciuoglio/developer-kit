# JWT Quick Reference Card

Quick reference for common JWT patterns in Spring Boot 3.5.x applications.

## Dependencies

```xml
<!-- Maven -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.6</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.6</version>
    <scope>runtime</scope>
</dependency>
```

```kotlin
// Gradle
implementation("io.jsonwebtoken:jjwt-api:0.12.6")
implementation("io.jsonwebtoken:jjwt-impl:0.12.6")
implementation("io.jsonwebtoken:jjwt-jackson:0.12.6")
```

## Basic JWT Service

```java
@Service
public class JwtService {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long expiration;

    public String generateToken(UserDetails userDetails) {
        return Jwts.builder()
                .setSubject(userDetails.getUsername())
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(Keys.hmacShaKeyFor(secret.getBytes()), SignatureAlgorithm.HS256)
                .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        String username = extractUsername(token);
        return username.equals(userDetails.getUsername()) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claimsResolver.apply(claims);
    }
}
```

## Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider())
            .addFilterBefore(jwtAuthFilter(), UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService());
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

## JWT Filter

```java
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);
        String username = jwtService.extractUsername(token);

        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);

            if (jwtService.isTokenValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                    userDetails, null, userDetails.getAuthorities()
                );
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }
}
```

## Authentication Controller

```java
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthenticationController {

    private final AuthenticationService service;

    @PostMapping("/register")
    public ResponseEntity<AuthenticationResponse> register(@RequestBody RegisterRequest request) {
        return ResponseEntity.ok(service.register(request));
    }

    @PostMapping("/authenticate")
    public ResponseEntity<AuthenticationResponse> authenticate(@RequestBody AuthenticationRequest request) {
        return ResponseEntity.ok(service.authenticate(request));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthenticationResponse> refresh(@RequestBody RefreshRequest request) {
        return ResponseEntity.ok(service.refresh(request));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestBody LogoutRequest request) {
        service.logout(request);
        return ResponseEntity.ok().build();
    }
}
```

## Application Properties

```yaml
# application.yml
jwt:
  secret: ${JWT_SECRET:your-256-bit-secret-key-here-at-least-32-characters}
  access-token-expiration: 900000    # 15 minutes
  refresh-token-expiration: 604800000 # 7 days
  issuer: ${JWT_ISSUER:your-app-name}
  cookie:
    name: jwt-token
    secure: ${JWT_COOKIE_SECURE:true}  # true in production
    http-only: true
    same-site: strict

spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI:https://your-auth-server.com}
```

## Common JWT Operations

### Generate Token with Claims
```java
public String generateTokenWithClaims(UserDetails userDetails, Map<String, Object> claims) {
    return Jwts.builder()
            .setClaims(claims)
            .setSubject(userDetails.getUsername())
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + expiration))
            .claim("roles", userDetails.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toList()))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes()), SignatureAlgorithm.HS256)
            .compact();
}
```

### Validate Token with Clock Skew
```java
public boolean isTokenValidWithSkew(String token, UserDetails userDetails) {
    try {
        Jwts.parserBuilder()
            .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
            .setAllowedClockSkewSeconds(60) // 1 minute tolerance
            .build()
            .parseClaimsJws(token);
        return true;
    } catch (JwtException e) {
        return false;
    }
}
```

### Extract All Claims
```java
public Claims extractAllClaims(String token) {
    return Jwts.parserBuilder()
            .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
            .build()
            .parseClaimsJws(token)
            .getBody();
}
```

## Security Best Practices

### 1. Use Strong Keys
```java
// Generate secure key
SecretKey key = Keys.secretKeyFor(SignatureAlgorithm.HS256);
String base64Key = Encoders.BASE64.encode(key.getEncoded());
```

### 2. Set Appropriate Expiration
```java
// Short-lived access tokens (15 minutes)
long accessTokenExpiration = 15 * 60 * 1000; // 15 minutes

// Longer refresh tokens (7 days)
long refreshTokenExpiration = 7 * 24 * 60 * 60 * 1000; // 7 days
```

### 3. Validate All Claims
```java
public boolean validateAllClaims(String token) {
    try {
        Jwts.parserBuilder()
            .setSigningKey(Keys.hmacShaKeyFor(secret.getBytes()))
            .requireIssuer("your-app-name")
            .requireAudience("your-app-users")
            .build()
            .parseClaimsJws(token);
        return true;
    } catch (JwtException e) {
        return false;
    }
}
```

### 4. Implement Token Blacklisting
```java
@Service
public class TokenBlacklistService {
    private final Set<String> blacklistedTokens = ConcurrentHashMap.newKeySet();

    public void blacklistToken(String token) {
        blacklistedTokens.add(token);
    }

    public boolean isBlacklisted(String token) {
        return blacklistedTokens.contains(token);
    }
}
```

## Testing JWT

### Unit Test JWT Service
```java
@Test
void shouldGenerateValidToken() {
    UserDetails userDetails = User.builder()
        .username("test@example.com")
        .password("password")
        .authorities("ROLE_USER")
        .build();

    String token = jwtService.generateToken(userDetails);

    assertThat(token).isNotNull();
    assertThat(jwtService.extractUsername(token)).isEqualTo("test@example.com");
    assertThat(jwtService.isTokenValid(token, userDetails)).isTrue();
}
```

### Integration Test Authentication
```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthenticationIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldAuthenticateUser() throws Exception {
        LoginRequest request = new LoginRequest("user@example.com", "password123");

        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").exists())
                .andExpect(jsonPath("$.refreshToken").exists());
    }
}
```

## Error Handling

### JWT Exception Handler
```java
@RestControllerAdvice
public class JwtExceptionHandler {

    @ExceptionHandler(JwtException.class)
    public ResponseEntity<ErrorResponse> handleJwtException(JwtException e) {
        ErrorResponse error = new ErrorResponse(
            "Invalid token",
            e.getMessage(),
            HttpStatus.UNAUTHORIZED.value()
        );
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }

    @ExceptionHandler(ExpiredJwtException.class)
    public ResponseEntity<ErrorResponse> handleExpiredJwtException(ExpiredJwtException e) {
        ErrorResponse error = new ErrorResponse(
            "Token expired",
            "The authentication token has expired",
            HttpStatus.UNAUTHORIZED.value()
        );
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
    }
}
```

## Common Issues

### Issue: Invalid Key Length
**Error**: The signing key's size is 184 bits which is not secure enough for the HS256 algorithm.
**Solution**: Use a key of at least 256 bits (32 characters).

### Issue: Clock Skew
**Error**: JWT is expired or not yet valid
**Solution**: Add clock skew tolerance.
```java
Jwts.parserBuilder()
    .setAllowedClockSkewSeconds(60)
    .build()
    .parseClaimsJws(token);
```

### Issue: CORS Issues
**Solution**: Configure CORS properly.
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOriginPatterns(List.of("http://localhost:*"));
    configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    configuration.setAllowedHeaders(List.of("*"));
    configuration.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    return source;
}
```

## References

- [JJWT Documentation](https://github.com/jwtk/jjwt)
- [Spring Security OAuth2 Resource Server](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 8725 - JWT Best Practices](https://tools.ietf.org/html/rfc8725)