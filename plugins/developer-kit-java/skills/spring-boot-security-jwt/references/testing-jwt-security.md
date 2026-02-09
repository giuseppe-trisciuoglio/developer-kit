# Testing JWT Security

## Unit Testing Authentication

### Testing JWT Token Service
```java
@ExtendWith(MockitoExtension.class)
class JwtTokenServiceTest {

    @Mock
    private JwtEncoder jwtEncoder;

    @Mock
    private JwtDecoder jwtDecoder;

    @Mock
    private JwtClaimsService claimsService;

    @InjectMocks
    private JwtTokenService tokenService;

    @Test
    @DisplayName("Should generate access token successfully")
    void generateAccessToken_Success() {
        // Given
        User user = createTestUser();
        JwtClaimsSet claims = createTestClaims();
        Jwt encodedToken = createEncodedToken();

        when(claimsService.createAccessTokenClaims(user)).thenReturn(claims);
        when(jwtEncoder.encode(any(JwtEncoderParameters.class)))
            .thenReturn(new Jwt(encodedToken.getTokenValue()));

        // When
        AccessTokenResponse response = tokenService.generateAccessToken(user);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.token()).isEqualTo(encodedToken.getTokenValue());
        assertThat(response.expiresAt()).isEqualTo(claims.getExpiresAt().toEpochMilli());
        assertThat(response.type()).isEqualTo("access");

        verify(claimsService).createAccessTokenClaims(user);
        verify(jwtEncoder).encode(any(JwtEncoderParameters.class));
    }

    @Test
    @DisplayName("Should validate token successfully")
    void isTokenValid_Success() {
        // Given
        String validToken = "valid.jwt.token";
        Jwt jwt = createTestJwt();
        when(jwtDecoder.decode(validToken)).thenReturn(jwt);

        // When
        boolean isValid = tokenService.isTokenValid(validToken);

        // Then
        assertThat(isValid).isTrue();
        verify(jwtDecoder).decode(validToken);
    }

    @Test
    @DisplayName("Should reject expired token")
    void isTokenValid_ExpiredToken_ReturnsFalse() {
        // Given
        String expiredToken = "expired.jwt.token";
        Jwt jwt = createExpiredJwt();
        when(jwtDecoder.decode(expiredToken)).thenReturn(jwt);

        // When
        boolean isValid = tokenService.isTokenValid(expiredToken);

        // Then
        assertThat(isValid).isFalse();
    }

    @Test
    @DisplayName("Should reject invalid token")
    void isTokenValid_InvalidToken_ReturnsFalse() {
        // Given
        String invalidToken = "invalid.token";
        when(jwtDecoder.decode(invalidToken))
            .thenThrow(new JwtException("Invalid token"));

        // When
        boolean isValid = tokenService.isTokenValid(invalidToken);

        // Then
        assertThat(isValid).isFalse();
    }

    @Test
    @DisplayName("Should extract claim from token")
    void extractTokenClaim_Success() {
        // Given
        String token = "test.jwt.token";
        String claimName = "sub";
        String expectedClaim = "12345";
        Jwt jwt = createTestJwt();
        when(jwtDecoder.decode(token)).thenReturn(jwt);
        when(jwt.getClaimAsString(claimName)).thenReturn(expectedClaim);

        // When
        String claim = tokenService.extractTokenClaim(token, claimName);

        // Then
        assertThat(claim).isEqualTo(expectedClaim);
    }

    private User createTestUser() {
        return User.builder()
            .id(1L)
            .email("test@example.com")
            .password("encodedPassword")
            .roles(Set.of(new Role("USER")))
            .enabled(true)
            .build();
    }

    private JwtClaimsSet createTestClaims() {
        return JwtClaimsSet.builder()
            .issuer("test-issuer")
            .subject("12345")
            .audience(List.of("test-audience"))
            .issuedAt(Instant.now())
            .expiresAt(Instant.now().plus(1, ChronoUnit.HOURS))
            .claim("type", "access")
            .build();
    }

    private Jwt createEncodedToken() {
        return new Jwt("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
                      Map.of(),
                      Map.of("exp", Instant.now().plus(1, ChronoUnit.HOURS).getEpochSecond()));
    }

    private Jwt createTestJwt() {
        return Jwt.withTokenValue("test.token")
            .header("alg", "RS256")
            .claim("sub", "12345")
            .claim("type", "access")
            .expiresAt(Instant.now().plus(1, ChronoUnit.HOURS))
            .build();
    }

    private Jwt createExpiredJwt() {
        return Jwt.withTokenValue("expired.token")
            .header("alg", "RS256")
            .claim("sub", "12345")
            .claim("type", "access")
            .expiresAt(Instant.now().minus(1, ChronoUnit.HOURS))
            .build();
    }
}
```

### Testing Security Configuration
```java
@SpringBootTest
@AutoConfigureTestDatabase
@TestPropertySource(properties = {
    "jwt.secret=test-secret-key-for-testing-only",
    "jwt.access-token-expiration=PT5M"
})
class SecurityConfigTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @MockBean
    private AuthenticationManager authenticationManager;

    @Test
    @DisplayName("Should allow access to public endpoints")
    void publicEndpoints_AccessAllowed() {
        // When
        ResponseEntity<String> response = restTemplate.getForEntity(
            "/api/public/health", String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }

    @Test
    @DisplayName("Should deny access to protected endpoints without authentication")
    void protectedEndpoints_NoAuthentication_Returns401() {
        // When
        ResponseEntity<String> response = restTemplate.getForEntity(
            "/api/users/me", String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should allow access with valid JWT")
    void protectedEndpoints_ValidJwt_Returns200() {
        // Given
        String validToken = generateValidToken();
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(validToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<UserProfileResponse> response = restTemplate.exchange(
            "/api/users/me", HttpMethod.GET, entity, UserProfileResponse.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
    }

    @Test
    @DisplayName("Should reject invalid JWT")
    void protectedEndpoints_InvalidJwt_Returns401() {
        // Given
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("invalid.jwt.token");
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/users/me", HttpMethod.GET, entity, String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    @DisplayName("Should enforce role-based access control")
    void adminEndpoints_UserRole_Returns403() {
        // Given
        String userToken = generateUserToken();
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(userToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        // When
        ResponseEntity<String> response = restTemplate.exchange(
            "/api/admin/users", HttpMethod.GET, entity, String.class);

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.FORBIDDEN);
    }

    private String generateValidToken() {
        // Generate a valid JWT for testing
        // This should use the same JWT encoder as the application
        User testUser = createTestUser();
        JwtTokenService tokenService = new JwtTokenService(/* dependencies */);
        AccessTokenResponse response = tokenService.generateAccessToken(testUser);
        return response.token();
    }

    private String generateUserToken() {
        // Generate a token with USER role only
        User testUser = createTestUserWithRole("USER");
        JwtTokenService tokenService = new JwtTokenService(/* dependencies */);
        AccessTokenResponse response = tokenService.generateAccessToken(testUser);
        return response.token();
    }
}
```

## Integration Testing with Testcontainers

### Security Integration Tests
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Transactional
class SecurityIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void postgresProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private TestRestTemplate restTemplate;

    @MockBean
    private EmailService emailService;

    @Test
    @DisplayName("Complete authentication flow")
    void completeAuthenticationFlow_Success() {
        // Given
        LoginRequest loginRequest = new LoginRequest("user@example.com", "password");

        // When
        ResponseEntity<LoginResponse> loginResponse = restTemplate.postForEntity(
            "/api/auth/login", loginRequest, LoginResponse.class);

        // Then
        assertThat(loginResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(loginResponse.getBody()).isNotNull();
        assertThat(loginResponse.getBody().accessToken()).isNotEmpty();

        // Use token for authenticated request
        String token = loginResponse.getBody().accessToken();
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        ResponseEntity<UserProfileResponse> profileResponse = restTemplate.exchange(
            "/api/users/me", HttpMethod.GET, entity, UserProfileResponse.class);

        assertThat(profileResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(profileResponse.getBody().email()).isEqualTo("user@example.com");
    }

    @Test
    @DisplayName("Refresh token flow")
    void refreshTokenFlow_Success() {
        // Given
        LoginRequest loginRequest = new LoginRequest("user@example.com", "password");
        ResponseEntity<LoginResponse> loginResponse = restTemplate.postForEntity(
            "/api/auth/login", loginRequest, LoginResponse.class);
        String refreshToken = loginResponse.getBody().refreshToken();

        RefreshTokenRequest refreshRequest = new RefreshTokenRequest(refreshToken);

        // When
        ResponseEntity<RefreshTokenResponse> refreshResponse = restTemplate.postForEntity(
            "/api/auth/refresh", refreshRequest, RefreshTokenResponse.class);

        // Then
        assertThat(refreshResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(refreshResponse.getBody().accessToken()).isNotEmpty();
        assertThat(refreshResponse.getBody().refreshToken()).isNotEmpty();
    }

    @Test
    @DisplayName("Logout invalidates tokens")
    void logout_InvalidatesTokens() {
        // Given
        LoginRequest loginRequest = new LoginRequest("user@example.com", "password");
        ResponseEntity<LoginResponse> loginResponse = restTemplate.postForEntity(
            "/api/auth/login", loginRequest, LoginResponse.class);
        String token = loginResponse.getBody().accessToken();

        // When
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(token);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        restTemplate.postForEntity("/api/auth/logout", null, String.class);

        // Then
        ResponseEntity<String> protectedResponse = restTemplate.exchange(
            "/api/users/me", HttpMethod.GET, entity, String.class);

        assertThat(protectedResponse.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @BeforeEach
    void setUp() {
        // Create test user
        User testUser = User.builder()
            .email("user@example.com")
            .password(passwordEncoder.encode("password"))
            .firstName("Test")
            .lastName("User")
            .enabled(true)
            .build();

        userRepository.save(testUser);
    }
}
```

### Testing Custom Filters
```java
@ExtendWith(MockitoExtension.class)
class JwtAuthenticationFilterTest {

    @Mock
    private JwtTokenService tokenService;

    @Mock
    private UserDetailsService userDetailsService;

    @InjectMocks
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Mock
    private FilterChain filterChain;

    @Mock
    private HttpServletRequest request;

    @Mock
    private HttpServletResponse response;

    @Test
    @DisplayName("Should authenticate with valid token")
    void doFilterInternal_ValidToken_SetsAuthentication() throws Exception {
        // Given
        String token = "valid.jwt.token";
        String authHeader = "Bearer " + token;
        String username = "user@example.com";

        when(request.getHeader(HttpHeaders.AUTHORIZATION)).thenReturn(authHeader);
        when(tokenService.isTokenValid(token)).thenReturn(true);
        when(tokenService.extractTokenClaim(token, "sub")).thenReturn(username);

        UserDetails userDetails = User.builder()
            .username(username)
            .password("password")
            .authorities(List.of(new SimpleGrantedAuthority("ROLE_USER")))
            .build();

        when(userDetailsService.loadUserByUsername(username)).thenReturn(userDetails);

        // When
        jwtAuthenticationFilter.doFilterInternal(request, response, filterChain);

        // Then
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        assertThat(authentication).isNotNull();
        assertThat(authentication.getName()).isEqualTo(username);
        assertThat(authentication.getAuthorities())
            .containsExactly(new SimpleGrantedAuthority("ROLE_USER"));

        verify(filterChain).doFilter(request, response);
    }

    @Test
    @DisplayName("Should skip authentication for no token")
    void doFilterInternal_NoToken_SkipsAuthentication() throws Exception {
        // Given
        when(request.getHeader(HttpHeaders.AUTHORIZATION)).thenReturn(null);

        // When
        jwtAuthenticationFilter.doFilterInternal(request, response, filterChain);

        // Then
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        assertThat(authentication).isNull();

        verify(filterChain).doFilter(request, response);
    }

    @Test
    @DisplayName("Should reject invalid token")
    void doFilterInternal_InvalidToken_Returns401() throws Exception {
        // Given
        String token = "invalid.jwt.token";
        String authHeader = "Bearer " + token;

        when(request.getHeader(HttpHeaders.AUTHORIZATION)).thenReturn(authHeader);
        when(tokenService.isTokenValid(token)).thenReturn(false);

        // When
        jwtAuthenticationFilter.doFilterInternal(request, response, filterChain);

        // Then
        verify(response).sendError(HttpStatus.UNAUTHORIZED.value(), "Invalid JWT token");
        verify(filterChain, never()).doFilter(request, response);
    }
}
```

## Testing Authorization

### Method-Level Security Tests
```java
@ExtendWith(MockitoExtension.class)
class DocumentServiceSecurityTest {

    @InjectMocks
    private DocumentService documentService;

    @Mock
    private DocumentRepository documentRepository;

    @Test
    @WithMockUser(roles = "USER")
    @DisplayName("User should access own documents")
    void getMyDocument_UserRole_Success() {
        // Given
        Long documentId = 1L;
        Document document = createDocument();
        when(documentRepository.findById(documentId)).thenReturn(Optional.of(document));

        // When
        Document result = documentService.getMyDocument(documentId);

        // Then
        assertThat(result).isNotNull();
        verify(documentRepository).findById(documentId);
    }

    @Test
    @WithMockUser(roles = "USER")
    @DisplayName("User should not access admin endpoints")
    void deleteAllDocuments_UserRole_AccessDenied() {
        // When & Then
        assertThrows(AccessDeniedException.class,
            () -> documentService.deleteAllDocuments());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    @DisplayName("Admin should access admin endpoints")
    void deleteAllDocuments_AdminRole_Success() {
        // When
        documentService.deleteAllDocuments();

        // Then
        verify(documentRepository).deleteAll();
    }

    @Test
    @DisplayName("Permission-based authorization should work")
    void approveDocument_WithPermission_Success() {
        // Given
        Long documentId = 1L;
        User user = createUserWithPermission("DOCUMENT_APPROVE");
        Document document = createDocument();
        document.setOwner(createDifferentUser());

        when(documentRepository.findById(documentId)).thenReturn(Optional.of(document));

        Authentication auth = new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());
        SecurityContextHolder.getContext().setAuthentication(auth);

        // When
        Document result = documentService.approveDocument(documentId);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getStatus()).isEqualTo(DocumentStatus.APPROVED);
    }

    private Document createDocument() {
        return Document.builder()
            .id(1L)
            .title("Test Document")
            .status(DocumentStatus.DRAFT)
            .owner(createTestUser())
            .build();
    }

    private User createUserWithPermission(String permission) {
        User user = new User();
        user.setAuthorities(List.of(new SimpleGrantedAuthority(permission)));
        return user;
    }
}
```

### Testing Custom Security Rules
```java
@SpringBootTest
class CustomPermissionEvaluatorTest {

    @Autowired
    private CustomPermissionEvaluator permissionEvaluator;

    @MockBean
    private PermissionService permissionService;

    @Test
    @DisplayName("Should allow owner to access resource")
    void hasPermission_OwnerAccess_ReturnsTrue() {
        // Given
        User user = createTestUser();
        Document document = createDocumentOwnedBy(user);
        Authentication auth = new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());

        // When
        boolean hasPermission = permissionEvaluator.hasPermission(
            auth, document, "READ");

        // Then
        assertThat(hasPermission).isTrue();
    }

    @Test
    @DisplayName("Should check department-based permissions")
    void hasPermission_DepartmentAccess_ReturnsTrue() {
        // Given
        User user = createUserInDepartment("FINANCE");
        Document document = createDocumentInDepartment("FINANCE");
        Authentication auth = new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());

        when(permissionService.hasDepartmentPermission(user, "FINANCE", "READ"))
            .thenReturn(true);

        // When
        boolean hasPermission = permissionEvaluator.hasPermission(
            auth, document, "READ");

        // Then
        assertThat(hasPermission).isTrue();
        verify(permissionService).hasDepartmentPermission(user, "FINANCE", "READ");
    }

    @Test
    @DisplayName("Should validate time-based restrictions")
    void hasTimeBasedPermission_WithinBusinessHours_ReturnsTrue() {
        // Given
        User user = createTestUser();
        Authentication auth = new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());

        // Mock business hours (9 AM - 5 PM)
        Instant accessTime = LocalDate.now()
            .atTime(14, 0)
            .atZone(ZoneId.systemDefault())
            .toInstant();

        // When
        boolean hasPermission = permissionEvaluator.hasTimeBasedPermission(
            auth, "READ", accessTime);

        // Then
        assertThat(hasPermission).isTrue();
    }

    @Test
    @DisplayName("Should restrict access outside business hours")
    void hasTimeBasedPermission_OutsideBusinessHours_ReturnsFalse() {
        // Given
        User user = createTestUser();
        Authentication auth = new UsernamePasswordAuthenticationToken(
            user, null, user.getAuthorities());

        // Mock outside business hours (2 AM)
        Instant accessTime = LocalDate.now()
            .atTime(2, 0)
            .atZone(ZoneId.systemDefault())
            .toInstant();

        // When
        boolean hasPermission = permissionEvaluator.hasTimeBasedPermission(
            auth, "READ", accessTime);

        // Then
        assertThat(hasPermission).isFalse();
    }
}
```

## Performance Testing

### JWT Token Generation Performance Test
```java
@SpringBootTest
class JwtPerformanceTest {

    @Autowired
    private JwtTokenService tokenService;

    @Autowired
    private UserRepository userRepository;

    @Test
    @DisplayName("Token generation should be fast under load")
    void generateToken_UnderLoad_PerformsWell() {
        // Given
        List<User> testUsers = createTestUsers(1000);
        int iterations = 10000;

        // When
        long startTime = System.nanoTime();
        List<CompletableFuture<AccessTokenResponse>> futures = new ArrayList<>();

        for (int i = 0; i < iterations; i++) {
            User user = testUsers.get(i % testUsers.size());
            CompletableFuture<AccessTokenResponse> future = CompletableFuture.supplyAsync(
                () -> tokenService.generateAccessToken(user));
            futures.add(future);
        }

        // Wait for all to complete
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .join();

        long endTime = System.nanoTime();
        long duration = endTime - startTime;

        // Then
        double avgTimePerToken = (double) duration / iterations / 1_000_000; // ms

        assertThat(avgTimePerToken).isLessThan(10.0); // Should be under 10ms per token
        System.out.printf("Average token generation time: %.2f ms%n", avgTimePerToken);
    }

    @Test
    @DisplayName("Token validation should be fast")
    void validateToken_MultipleTokens_PerformsWell() {
        // Given
        List<String> tokens = generateTestTokens(1000);

        // When
        long startTime = System.nanoTime();
        int validTokens = 0;

        for (String token : tokens) {
            if (tokenService.isTokenValid(token)) {
                validTokens++;
            }
        }

        long endTime = System.nanoTime();
        long duration = endTime - startTime;

        // Then
        double avgTimePerValidation = (double) duration / tokens.size() / 1_000_000; // ms

        assertThat(avgTimePerValidation).isLessThan(5.0); // Should be under 5ms per validation
        assertThat(validTokens).isEqualTo(tokens.size());

        System.out.printf("Average token validation time: %.2f ms%n", avgTimePerValidation);
    }

    private List<User> createTestUsers(int count) {
        List<User> users = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            users.add(User.builder()
                .id((long) i)
                .email("user" + i + "@example.com")
                .password("password")
                .roles(Set.of(new Role("USER")))
                .build());
        }
        return users;
    }

    private List<String> generateTestTokens(int count) {
        List<String> tokens = new ArrayList<>();
        for (User user : createTestUsers(count)) {
            AccessTokenResponse response = tokenService.generateAccessToken(user);
            tokens.add(response.token());
        }
        return tokens;
    }
}
```

## Security Testing with OWASP ZAP

### Security Test Configuration
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class SecurityScanTest {

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    @DisplayName("Should be secure against common vulnerabilities")
    void application_CommonVulnerabilities_IsSecure() {
        // Test SQL Injection
        testSqlInjectionProtection();

        // Test XSS
        testXssProtection();

        // Test CSRF
        testCsrfProtection();

        // Test Authentication Bypass
        testAuthenticationBypassProtection();

        // Test Authorization Bypass
        testAuthorizationBypassProtection();
    }

    private void testSqlInjectionProtection() {
        String[] maliciousInputs = {
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --"
        };

        for (String input : maliciousInputs) {
            LoginRequest request = new LoginRequest(input, "password");
            ResponseEntity<String> response = restTemplate.postForEntity(
                "/api/auth/login", request, String.class);

            // Should return 401, not 500 or 200
            assertThat(response.getStatusCode())
                .isIn(HttpStatus.UNAUTHORIZED, HttpStatus.BAD_REQUEST);
        }
    }

    private void testXssProtection() {
        String xssPayload = "<script>alert('xss')</script>";

        // Test in registration
        RegistrationRequest request = RegistrationRequest.builder()
            .email("test@example.com")
            .password("password")
            .firstName(xssPayload)
            .lastName("Test")
            .build();

        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/register", request, String.class);

        if (response.getStatusCode() == HttpStatus.CREATED) {
            // Verify payload is escaped in response
            assertThat(response.getBody())
                .doesNotContain("<script>")
                .contains("&lt;script&gt;");
        }
    }

    private void testCsrfProtection() {
        // CSRF should be enforced for state-changing operations
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        // Don't include CSRF token

        HttpEntity<String> entity = new HttpEntity<>("{}", headers);

        ResponseEntity<String> response = restTemplate.postForEntity(
            "/api/users/profile", entity, String.class);

        // Should reject without CSRF token
        assertThat(response.getStatusCode()).isIn(HttpStatus.FORBIDDEN, HttpStatus.UNAUTHORIZED);
    }

    private void testAuthenticationBypassProtection() {
        // Test accessing protected endpoints without authentication
        String[] protectedEndpoints = {
            "/api/users/me",
            "/api/documents",
            "/api/orders"
        };

        for (String endpoint : protectedEndpoints) {
            ResponseEntity<String> response = restTemplate.getForEntity(
                endpoint, String.class);

            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        }
    }

    private void testAuthorizationBypassProtection() {
        // Test accessing admin endpoints with user token
        String userToken = generateUserToken();
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(userToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        String[] adminEndpoints = {
            "/api/admin/users",
            "/api/admin/roles",
            "/api/admin/permissions"
        };

        for (String endpoint : adminEndpoints) {
            ResponseEntity<String> response = restTemplate.exchange(
                endpoint, HttpMethod.GET, entity, String.class);

            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.FORBIDDEN);
        }
    }
}
```