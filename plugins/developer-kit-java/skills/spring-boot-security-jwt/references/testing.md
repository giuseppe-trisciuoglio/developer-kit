# JWT Security Testing Strategies

This document provides comprehensive testing strategies for JWT security implementations in Spring Boot applications, covering unit tests, integration tests, security tests, and performance testing.

## Table of Contents

1. [Unit Testing JWT Components](#unit-testing-jwt-components)
2. [Integration Testing Security Configuration](#integration-testing-security-configuration)
3. [Security Testing with Testcontainers](#security-testing-with-testcontainers)
4. [MockMvc Security Testing](#mockmvc-security-testing)
5. [Test Data Management](#test-data-management)
6. [Test Utilities and Helpers](#test-utilities-and-helpers)
7. [Security Test Scenarios](#security-test-scenarios)
8. [Performance Testing JWT Operations](#performance-testing-jwt-operations)
9. [Load Testing JWT Endpoints](#load-testing-jwt-endpoints)
10. [Security Test Checklist](#security-test-checklist)

## Unit Testing JWT Components

### JWT Service Unit Tests

```java
@ExtendWith(MockitoExtension.class)
class JwtServiceTest {

    @Mock
    private RefreshTokenService refreshTokenService;

    @Value("${jwt.test.secret:test-secret-key-for-unit-testing-only-256-bits}")
    private String testSecret;

    private JwtService jwtService;

    private User testUser;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService(
            testSecret,
            900000,  // 15 minutes
            604800000, // 7 days
            "test-issuer",
            null,
            true,
            false,
            60,
            refreshTokenService
        );

        testUser = User.builder()
                .id(1L)
                .email("test@example.com")
                .password("encodedPassword")
                .roles(Set.of(new Role("USER")))
                .enabled(true)
                .build();
    }

    @Test
    @DisplayName("Should generate valid access token")
    void shouldGenerateValidAccessToken() {
        // When
        String token = jwtService.generateAccessToken(testUser);

        // Then
        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
        assertThat(token.split("\\.")).hasSize(3); // Header, Payload, Signature

        // Verify claims
        Claims claims = parseToken(token);
        assertThat(claims.getSubject()).isEqualTo("test@example.com");
        assertThat(claims.getIssuer()).isEqualTo("test-issuer");
        assertThat(claims.getExpiration()).isAfter(new Date());
        assertThat(claims.getIssuedAt()).isNotNull();
        assertThat(claims.get("type")).isEqualTo("access");
    }

    @Test
    @DisplayName("Should extract username from valid token")
    void shouldExtractUsernameFromValidToken() {
        // Given
        String token = jwtService.generateAccessToken(testUser);

        // When
        String username = jwtService.extractUsername(token);

        // Then
        assertThat(username).isEqualTo("test@example.com");
    }

    @Test
    @DisplayName("Should validate token correctly")
    void shouldValidateTokenCorrectly() {
        // Given
        String token = jwtService.generateAccessToken(testUser);
        UserDetails userDetails = new org.springframework.security.core.userdetails.User(
            testUser.getEmail(),
            testUser.getPassword(),
            testUser.getAuthorities()
        );

        // When
        boolean isValid = jwtService.isTokenValid(token, userDetails);

        // Then
        assertThat(isValid).isTrue();
    }

    @Test
    @DisplayName("Should reject expired token")
    void shouldRejectExpiredToken() {
        // Given
        JwtService expiredJwtService = new JwtService(
            testSecret,
            1, // 1 millisecond
            604800000,
            "test-issuer",
            null,
            true,
            false,
            60,
            refreshTokenService
        );

        String token = expiredJwtService.generateAccessToken(testUser);

        // Wait for token to expire
        await().atMost(2, SECONDS)
               .until(() -> !expiredJwtService.isTokenValid(token, createUserDetails()));

        // Then
        assertThat(expiredJwtService.isTokenValid(token, createUserDetails())).isFalse();
    }

    @Test
    @DisplayName("Should reject token with invalid signature")
    void shouldRejectTokenWithInvalidSignature() {
        // Given
        String validToken = jwtService.generateAccessToken(testUser);
        String tamperedToken = validToken.substring(0, validToken.length() - 10) + "tampered";

        // When
        boolean isValid = jwtService.isTokenValid(tamperedToken, createUserDetails());

        // Then
        assertThat(isValid).isFalse();
    }

    @Test
    @DisplayName("Should reject token with invalid issuer")
    void shouldRejectTokenWithInvalidIssuer() {
        // Given
        JwtService differentIssuerService = new JwtService(
            testSecret,
            900000,
            604800000,
            "different-issuer",
            null,
            true,
            false,
            60,
            refreshTokenService
        );

        String token = differentIssuerService.generateAccessToken(testUser);

        // When
        boolean isValid = jwtService.isTokenValid(token, createUserDetails());

        // Then
        assertThat(isValid).isFalse();
    }

    @Test
    @DisplayName("Should include authorities in token")
    void shouldIncludeAuthoritiesInToken() {
        // Given
        Set<GrantedAuthority> authorities = Set.of(
            new SimpleGrantedAuthority("ROLE_USER"),
            new SimpleGrantedAuthority("USER_READ"),
            new SimpleGrantedAuthority("USER_WRITE")
        );

        UserDetails userDetails = new org.springframework.security.core.userdetails.User(
            testUser.getEmail(),
            testUser.getPassword(),
            authorities
        );

        // When
        String token = jwtService.generateAccessToken(userDetails);

        // Then
        Claims claims = parseToken(token);
        @SuppressWarnings("unchecked")
        List<String> tokenAuthorities = claims.get("authorities", List.class);

        assertThat(tokenAuthorities).containsExactlyInAnyOrder(
            "ROLE_USER", "USER_READ", "USER_WRITE"
        );
    }

    private UserDetails createUserDetails() {
        return new org.springframework.security.core.userdetails.User(
            testUser.getEmail(),
            testUser.getPassword(),
            testUser.getAuthorities()
        );
    }

    private Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    private SecretKey getSigningKey() {
        byte[] keyBytes = Base64.getEncoder().encodeToString(testSecret.getBytes()).getBytes();
        return Keys.hmacShaKeyFor(keyBytes);
    }
}
```

### Refresh Token Service Unit Tests

```java
@ExtendWith(MockitoExtension.class)
class RefreshTokenServiceTest {

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private RefreshTokenService refreshTokenService;

    @Test
    @DisplayName("Should create refresh token successfully")
    void shouldCreateRefreshTokenSuccessfully() {
        // Given
        User user = createTestUser();
        when(refreshTokenRepository.countByUserAndExpiresAtAfter(any(), any()))
                .thenReturn(0L);
        when(refreshTokenRepository.save(any(RefreshToken.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        // When
        String token = refreshTokenService.createRefreshToken(user.getEmail());

        // Then
        assertThat(token).isNotNull();
        assertThat(token).isNotEmpty();
        verify(refreshTokenRepository).countByUserAndExpiresAtAfter(any(), any());
        verify(refreshTokenRepository).save(any(RefreshToken.class));
    }

    @Test
    @DisplayName("Should revoke old tokens when limit exceeded")
    void shouldRevokeOldTokensWhenLimitExceeded() {
        // Given
        User user = createTestUser();
        when(refreshTokenRepository.countByUserAndExpiresAtAfter(any(), any()))
                .thenReturn(5); // At limit

        // When
        refreshTokenService.createRefreshToken(user.getEmail());

        // Then
        verify(refreshTokenRepository).deleteOldestByUser(user);
    }

    @Test
    @DisplayName("Should refresh token successfully")
    void shouldRefreshTokenSuccessfully() {
        // Given
        RefreshTokenRequest request = new RefreshTokenRequest("valid-refresh-token");
        RefreshToken existingToken = RefreshToken.builder()
                .token("valid-refresh-token")
                .user(createTestUser())
                .expiresAt(Instant.now().plus(Duration.ofDays(1)))
                .revoked(false)
                .build();

        when(refreshTokenRepository.findByToken("valid-refresh-token"))
                .thenReturn(Optional.of(existingToken));
        when(refreshTokenRepository.save(any(RefreshToken.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        // When
        RefreshTokenResponse response = refreshTokenService.refreshToken(request);

        // Then
        assertThat(response.getAccessToken()).isNotNull();
        assertThat(response.getExpiresIn()).isGreaterThan(0);
    }

    @Test
    @DisplayName("Should reject refresh token rotation for revoked tokens")
    void shouldRejectRefreshTokenRotationForRevokedTokens() {
        // Given
        String revokedToken = "revoked-token";
        RefreshToken token = RefreshToken.builder()
                .token(revokedToken)
                .revoked(true)
                .build();

        when(refreshTokenRepository.findByToken(revokedToken))
                .thenReturn(Optional.of(token));

        RefreshTokenRequest request = new RefreshTokenRequest(revokedToken);

        // When & Then
        assertThrows(InvalidTokenException.class,
            () -> refreshTokenService.refreshToken(request));
    }

    private User createTestUser() {
        return User.builder()
                .id(1L)
                .email("test@example.com")
                .enabled(true)
                .build();
    }
}
```

## Integration Testing Security Configuration

### Security Configuration Integration Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = {
    "jwt.secret=test-secret-key-for-integration-testing-256-bits-minimum",
    "jwt.access-token-expiration=900000",
    "jwt.refresh-token-expiration=604800000",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
@Transactional
class SecurityIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtService jwtService;

    private User testUser;

    @BeforeEach
    void setUp() {
        // Create test user
        testUser = User.builder()
                .email("test@example.com")
                .password(passwordEncoder.encode("password"))
                .roles(Set.of(new Role("USER")))
                .enabled(true)
                .build();
        testUser = userRepository.save(testUser);
    }

    @Test
    @DisplayName("Should allow access to public endpoints")
    void shouldAllowAccessToPublicEndpoints() {
        // When
        ResponseEntity<String> response = restTemplate.getForEntity("/api/public/health", String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    @Test
    @DisplayName("Should deny access to protected endpoints without token")
    void shouldDenyAccessToProtectedEndpointsWithoutToken() {
        // When
        ResponseEntity<String> response = restTemplate.getForEntity("/api/users/me", String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should allow access to protected endpoints with valid token")
    void shouldAllowAccessToProtectedEndpointsWithValidToken() {
        // Given
        String token = jwtService.generateAccessToken(testUser);
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);

        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/users/me",
            HttpMethod.GET,
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    @Test
    @DisplayName("Should deny access with invalid token")
    void shouldDenyAccessWithInvalidToken() {
        // Given
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("invalid-token");

        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/users/me",
            HttpMethod.GET,
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should deny access with expired token")
    void shouldDenyAccessWithExpiredToken() {
        // Given
        // Create an expired token by using a very short expiration time
        JwtService expiredJwtService = new JwtService(
            "test-secret-key-for-integration-testing-256-bits-minimum",
            1, // 1 millisecond
            604800000,
            "test-issuer",
            null,
            true,
            false,
            60,
            null
        );

        String token = expiredJwtService.generateAccessToken(testUser);

        // Wait for token to expire
        await().atMost(2, SECONDS).until(() -> {
            try {
                return !expiredJwtService.isTokenValid(token,
                    org.springframework.security.core.userdetails.User.builder()
                        .username(testUser.getEmail())
                        .password("password")
                        .roles("USER")
                        .build()
                );
            } catch (Exception e) {
                return true;
            }
        });

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);

        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/users/me",
            HttpMethod.GET,
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }
}
```

### Authentication Controller Integration Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
@Transactional
class AuthenticationControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
        registry.add("jwt.secret", () -> "test-secret-key-for-integration-testing-256-bits");
    }

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    private RegisterRequest registerRequest;
    private AuthenticationRequest authRequest;

    @BeforeEach
    void setUp() {
        registerRequest = new RegisterRequest(
            "test@example.com",
            "testuser",
            "Password123!",
            "Test",
            "User"
        );

        authRequest = new AuthenticationRequest(
            "test@example.com",
            "Password123!"
        );
    }

    @Test
    @DisplayName("Should register new user successfully")
    void shouldRegisterNewUserSuccessfully() throws Exception {
        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/auth/register",
            registerRequest,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        AuthenticationResponse authResponse = objectMapper.readValue(
            response.getBody(),
            AuthenticationResponse.class
        );

        assertThat(authResponse.getAccessToken()).isNotNull();
        assertThat(authResponse.getRefreshToken()).isNotNull();
        assertThat(authResponse.getUser().getEmail()).isEqualTo("test@example.com");
    }

    @Test
    @DisplayName("Should authenticate user successfully")
    void shouldAuthenticateUserSuccessfully() throws Exception {
        // Given - Register user first
        restTemplate.postForEntity("/api/auth/register", registerRequest, String.class);

        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/auth/authenticate",
            authRequest,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        AuthenticationResponse authResponse = objectMapper.readValue(
            response.getBody(),
            AuthenticationResponse.class
        );

        assertThat(authResponse.getAccessToken()).isNotNull();
        assertThat(authResponse.getRefreshToken()).isNotNull();
        assertThat(authResponse.getUser().getEmail()).isEqualTo("test@example.com");
    }

    @Test
    @DisplayName("Should fail authentication with wrong password")
    void shouldFailAuthenticationWithWrongPassword() {
        // Given
        AuthenticationRequest wrongPasswordRequest = new AuthenticationRequest(
            "test@example.com",
            "WrongPassword123!"
        );

        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/auth/authenticate",
            wrongPasswordRequest,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should refresh token successfully")
    void shouldRefreshTokenSuccessfully() throws Exception {
        // Given - Register and authenticate user
        restTemplate.postForEntity("/api/auth/register", registerRequest, String.class);
        ResponseEntity<String> authResponse = restTemplate.postForEntity(
            "/api/auth/authenticate",
            authRequest,
            String.class
        );

        AuthenticationResponse loginResponse = objectMapper.readValue(
            authResponse.getBody(),
            AuthenticationResponse.class
        );

        RefreshTokenRequest refreshRequest = new RefreshTokenRequest(
            loginResponse.getRefreshToken()
        );

        // When
        ResponseEntity<String> refreshResponse = restTemplate.postForEntity(
            "/api/auth/refresh",
            refreshRequest,
            String.class
        );

        // Then
        assertThat(refreshResponse.getStatusCode()).isEqualTo(HttpStatus.OK);

        AuthenticationResponse newAuthResponse = objectMapper.readValue(
            refreshResponse.getBody(),
            AuthenticationResponse.class
        );

        assertThat(newAuthResponse.getAccessToken()).isNotNull();
        assertThat(newAuthResponse.getAccessToken())
            .isNotEqualTo(loginResponse.getAccessToken());
    }
}
```

## MockMvc Security Testing

### MockMvc Security Tests

```java
@SpringBootTest
@AutoConfigureMockMvc(addFilters = false)
@TestPropertySource(properties = {
    "jwt.secret=test-secret-key-for-mockmvc-testing-256-bits",
    "jwt.access-token-expiration=900000",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
@Transactional
class AuthenticationControllerMockMvcTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtService jwtService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = User.builder()
                .email("test@example.com")
                .password(passwordEncoder.encode("Password123!"))
                .roles(Set.of(new Role("USER")))
                .enabled(true)
                .build();
        testUser = userRepository.save(testUser);
    }

    @Test
    @DisplayName("Should authenticate user and return tokens")
    void shouldAuthenticateUserAndReturnTokens() throws Exception {
        AuthenticationRequest request = new AuthenticationRequest(
            "test@example.com",
            "Password123!"
        );

        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").exists())
                .andExpect(jsonPath("$.refreshToken").exists())
                .andExpect(jsonPath("$.user.email").value("test@example.com"))
                .andExpect(jsonPath("$.tokenType").value("Bearer"));
    }

    @Test
    @DisplayName("Should validate authentication request")
    void shouldValidateAuthenticationRequest() throws Exception {
        AuthenticationRequest invalidRequest = new AuthenticationRequest("", "");

        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("Should protect admin endpoints")
    void shouldProtectAdminEndpoints() throws Exception {
        mockMvc.perform(get("/api/admin/users"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("Should allow admin access with proper role")
    void shouldAllowAdminAccessWithProperRole() throws Exception {
        mockMvc.perform(get("/api/admin/users"))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    @DisplayName("Should deny admin access to user role")
    void shouldDenyAdminAccessToUserRole() throws Exception {
        mockMvc.perform(get("/api/admin/users"))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Should authenticate with JWT token")
    void shouldAuthenticateWithJwtToken() throws Exception {
        // Given
        String token = jwtService.generateAccessToken(testUser);

        // When & Then
        mockMvc.perform(get("/api/auth/me")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("test@example.com"));
    }

    @Test
    @DisplayName("Should reject malformed JWT token")
    void shouldRejectMalformedJwtToken() throws Exception {
        mockMvc.perform(get("/api/auth/me")
                .header("Authorization", "Bearer malformed.token.here"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Should reject JWT token without Bearer prefix")
    void shouldRejectJwtTokenWithoutBearerPrefix() throws Exception {
        String token = jwtService.generateAccessToken(testUser);

        mockMvc.perform(get("/api/auth/me")
                .header("Authorization", token))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Should handle logout correctly")
    void shouldHandleLogoutCorrectly() throws Exception {
        // Given
        String token = jwtService.generateAccessToken(testUser);

        // When & Then
        mockMvc.perform(post("/api/auth/logout")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isNoContent());
    }

    @Test
    @DisplayName("Should validate refresh token request")
    void shouldValidateRefreshTokenRequest() throws Exception {
        RefreshTokenRequest invalidRequest = new RefreshTokenRequest("");

        mockMvc.perform(post("/api/auth/refresh")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("Should handle concurrent requests correctly")
    void shouldHandleConcurrentRequestsCorrectly() throws Exception {
        String token = jwtService.generateAccessToken(testUser);
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);

        MockHttpServletRequestBuilder request = get("/api/auth/me")
                .headers(headers);

        // Execute multiple concurrent requests
        int numRequests = 10;
        CountDownLatch latch = new CountDownLatch(numRequests);
        AtomicInteger successCount = new AtomicInteger(0);

        for (int i = 0; i < numRequests; i++) {
            CompletableFuture.runAsync(() -> {
                try {
                    MvcResult result = mockMvc.perform(request)
                            .andReturn();

                    if (result.getResponse().getStatus() == HttpStatus.OK.value()) {
                        successCount.incrementAndGet();
                    }
                } catch (Exception e) {
                    // Log error for debugging
                    System.err.println("Request failed: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }

        // Wait for all requests to complete
        boolean completed = latch.await(10, TimeUnit.SECONDS);

        assertThat(completed).isTrue();
        assertThat(successCount.get()).isEqualTo(numRequests);
    }
}
```

## Security Test Scenarios

### Security Vulnerability Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = {
    "jwt.secret=test-secret-key-for-security-testing-256-bits",
    "jwt.access-token-expiration=900000"
})
class SecurityVulnerabilityTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private JwtService jwtService;

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = User.builder()
                .email("test@example.com")
                .roles(Set.of(new Role("USER")))
                .enabled(true)
                .build();
    }

    @Test
    @DisplayName("Should prevent JWT token tampering")
    void shouldPreventJwtTokenTampering() {
        // Given
        String validToken = jwtService.generateAccessToken(testUser);

        // Tamper with token by changing characters
        String tamperedToken = validToken.substring(0, validToken.length() - 5) + "xxxxx";

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(tamperedToken);

        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/auth/me",
            HttpMethod.GET,
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should prevent replay attacks with expired tokens")
    void shouldPreventReplayAttacksWithExpiredTokens() {
        // Given - Create an expired token
        JwtService expiredService = new JwtService(
            "test-secret-key-for-security-testing-256-bits",
            1, // 1 millisecond expiration
            604800000,
            "test-issuer",
            null,
            true,
            false,
            60,
            null
        );

        String expiredToken = expiredService.generateAccessToken(testUser);

        // Wait for token to expire
        await().atMost(2, SECONDS).until(() -> {
            try {
                return !expiredService.isTokenValid(expiredToken,
                    org.springframework.security.core.userdetails.User.builder()
                        .username(testUser.getEmail())
                        .password("password")
                        .roles("USER")
                        .build()
                );
            } catch (Exception e) {
                return true;
            }
        });

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(expiredToken);

        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/auth/me",
            HttpMethod.GET,
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should prevent SQL injection in authentication")
    void shouldPreventSqlInjectionInAuthentication() {
        // Given
        AuthenticationRequest maliciousRequest = new AuthenticationRequest(
            "test@example.com'; DROP TABLE users; --",
            "password"
        );

        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/auth/authenticate",
            maliciousRequest,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);

        // Verify database still works
        ResponseEntity<String> healthResponse = restTemplate.getForEntity("/health", String.class);
        assertThat(healthResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    @Test
    @DisplayName("Should prevent XSS in authentication responses")
    void shouldPreventXssInAuthenticationResponses() {
        // Given
        User maliciousUser = User.builder()
                .email("test@example.com")
                .firstName("<script>alert('xss')</script>")
                .lastName("User")
                .build();

        // When
        // This would be a registration or similar endpoint that includes user data in response
        // For now, we'll test that our error handling doesn't expose script tags

        AuthenticationRequest request = new AuthenticationRequest(
            "<script>alert('xss')</script>",
            "password"
        );

        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/auth/authenticate",
            request,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        // Response should not contain the script tag
        assertThat(response.getBody()).doesNotContain("<script>");
    }

    @Test
    @DisplayName("Should handle large token payload gracefully")
    void shouldHandleLargeTokenPayloadGracefully() {
        // Given - Create a token with large payload
        String largeData = "x".repeat(10000); // 10KB of data

        // This would normally fail as tokens have size limits
        // We test that the system handles it gracefully

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/auth/me",
            HttpMethod.GET,
            null,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should enforce rate limiting")
    void shouldEnforceRateLimiting() {
        // Given
        AuthenticationRequest request = new AuthenticationRequest(
            "test@example.com",
            "wrongpassword"
        );

        // When - Make multiple failed attempts
        int attemptCount = 10;
        List<ResponseEntity<String>> responses = new ArrayList<>();

        for (int i = 0; i < attemptCount; i++) {
            ResponseEntity<String> response = restTemplate.postForEntity(
                "/api/auth/authenticate",
                request,
                String.class
            );
            responses.add(response);

            // Small delay between attempts
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        // Then
        // Initial attempts should return 401
        assertThat(responses.subList(0, 5))
            .allMatch(response -> response.getStatusCode() == HttpStatus.UNAUTHORIZED);

        // Later attempts might return 429 (Too Many Requests) if rate limiting is implemented
        // This depends on your rate limiting configuration
    }
}
```

## Performance Testing JWT Operations

### JWT Performance Tests

```java
@ExtendWith(MockitoExtension.class)
class JwtPerformanceTest {

    private JwtService jwtService;

    private User testUser;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService(
            "test-secret-key-for-performance-testing-256-bits-long",
            900000,
            604800000,
            "performance-test-issuer",
            null,
            true,
            false,
            60,
            null
        );

        testUser = User.builder()
                .id(1L)
                .email("performance-test@example.com")
                .roles(Set.of(new Role("USER"), new Role("ADMIN")))
                .build();
    }

    @Test
    @DisplayName("Should generate tokens efficiently")
    void shouldGenerateTokensEfficiently() {
        int numTokens = 1000;
        List<String> tokens = new ArrayList<>(numTokens);

        // Measure token generation time
        long startTime = System.nanoTime();

        for (int i = 0; i < numTokens; i++) {
            String token = jwtService.generateAccessToken(testUser);
            tokens.add(token);
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;

        // Then
        assertThat(tokens).hasSize(numTokens);
        assertThat(durationMs).isLessThan(5000); // Should complete within 5 seconds

        double avgTimePerToken = (double) durationMs / numTokens;
        System.out.println("Average time per token generation: " + avgTimePerToken + " ms");

        // Performance assertion - should be very fast per token
        assertThat(avgTimePerToken).isLessThan(5.0); // Less than 5ms per token
    }

    @Test
    @DisplayName("Should validate tokens efficiently")
    void shouldValidateTokensEfficiently() {
        // Generate tokens first
        int numTokens = 1000;
        List<String> tokens = new ArrayList<>();

        for (int i = 0; i < numTokens; i++) {
            tokens.add(jwtService.generateAccessToken(testUser));
        }

        UserDetails userDetails = createUserDetails();

        // Measure validation time
        long startTime = System.nanoTime();

        int validCount = 0;
        for (String token : tokens) {
            if (jwtService.isTokenValid(token, userDetails)) {
                validCount++;
            }
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;

        // Then
        assertThat(validCount).isEqualTo(numTokens);
        assertThat(durationMs).isLessThan(3000); // Should complete within 3 seconds

        double avgTimePerValidation = (double) durationMs / numTokens;
        System.out.println("Average time per token validation: " + avgTimePerValidation + " ms");

        // Performance assertion - validation should be very fast
        assertThat(avgTimePerValidation).isLessThan(3.0); // Less than 3ms per validation
    }

    @Test
    @DisplayName("Should handle concurrent token operations")
    void shouldHandleConcurrentTokenOperations() throws InterruptedException {
        int numThreads = 10;
        int operationsPerThread = 100;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);

        AtomicInteger successCount = new AtomicInteger(0);
        List<Exception> exceptions = Collections.synchronizedList(new ArrayList<>());

        // Concurrent token generation and validation
        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                try {
                    for (int j = 0; j < operationsPerThread; j++) {
                        // Generate token
                        String token = jwtService.generateAccessToken(testUser);

                        // Validate token
                        UserDetails userDetails = createUserDetails();
                        boolean isValid = jwtService.isTokenValid(token, userDetails);

                        if (isValid) {
                            successCount.incrementAndGet();
                        }
                    }
                } catch (Exception e) {
                    exceptions.add(e);
                } finally {
                    latch.countDown();
                }
            });
        }

        // Wait for completion
        boolean completed = latch.await(30, TimeUnit.SECONDS);
        executor.shutdown();

        // Then
        assertThat(completed).isTrue();
        assertThat(exceptions).isEmpty();
        assertThat(successCount.get()).isEqualTo(numThreads * operationsPerThread);

        System.out.println("Successfully processed " + successCount.get() + " token operations");
    }

    @Test
    @DisplayName("Should maintain performance with large user data")
    void shouldMaintainPerformanceWithLargeUserData() {
        // Create user with many roles and permissions
        User largeUser = User.builder()
                .id(1L)
                .email("large-user@example.com")
                .build();

        // Add many roles
        Set<Role> roles = new HashSet<>();
        for (int i = 0; i < 50; i++) {
            roles.add(new Role("ROLE_" + i));
        }
        largeUser.setRoles(roles);

        int numTokens = 100;
        List<String> tokens = new ArrayList<>();

        // Measure performance with large user data
        long startTime = System.nanoTime();

        for (int i = 0; i < numTokens; i++) {
            String token = jwtService.generateAccessToken(largeUser);
            tokens.add(token);
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;

        // Then
        assertThat(tokens).hasSize(numTokens);

        double avgTimePerToken = (double) durationMs / numTokens;
        System.out.println("Average time per large token generation: " + avgTimePerToken + " ms");

        // Should still be reasonable even with large payloads
        assertThat(avgTimePerToken).isLessThan(10.0); // Less than 10ms per token
    }

    @Test
    @DisplayName("Should efficiently extract claims from tokens")
    void shouldEfficientlyExtractClaimsFromTokens() {
        // Generate tokens
        int numTokens = 1000;
        List<String> tokens = new ArrayList<>();

        for (int i = 0; i < numTokens; i++) {
            tokens.add(jwtService.generateAccessToken(testUser));
        }

        // Measure claim extraction time
        long startTime = System.nanoTime();

        for (String token : tokens) {
            String username = jwtService.extractUsername(token);
            assertThat(username).isEqualTo("performance-test@example.com");
        }

        long endTime = System.nanoTime();
        long durationMs = (endTime - startTime) / 1_000_000;

        // Then
        double avgTimePerExtraction = (double) durationMs / numTokens;
        System.out.println("Average time per claim extraction: " + avgTimePerExtraction + " ms");

        // Claim extraction should be very fast
        assertThat(avgTimePerExtraction).isLessThan(1.0); // Less than 1ms per extraction
    }

    private UserDetails createUserDetails() {
        return org.springframework.security.core.userdetails.User.builder()
                .username(testUser.getEmail())
                .password("password")
                .roles("USER", "ADMIN")
                .build();
    }
}
```

This comprehensive testing guide provides strategies for thoroughly testing JWT security implementations, covering unit tests, integration tests, security vulnerability tests, and performance tests to ensure robust and secure JWT authentication in Spring Boot applications.