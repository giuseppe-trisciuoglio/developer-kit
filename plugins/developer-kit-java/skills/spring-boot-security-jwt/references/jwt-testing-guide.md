# JWT Testing Guide

Comprehensive testing strategies for JWT authentication and authorization in Spring Boot applications, including unit tests, integration tests, and security testing patterns.

## Table of Contents

1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [Security Testing](#security-testing)
4. [Performance Testing](#performance-testing)
5. [Test Data Management](#test-data-management)
6. [Mock Strategies](#mock-strategies)
7. [Continuous Testing](#continuous-testing)

## Unit Testing

### Testing JWT Service

```java
@ExtendWith(MockitoExtension.class)
class JwtServiceTest {

    @Mock
    private SecretKeyRepository secretKeyRepository;

    @Mock
    private CacheManager cacheManager;

    @InjectMocks
    private JwtService jwtService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(jwtService, "secret", "test-secret-key-that-is-at-least-256-bits-long");
        ReflectionTestUtils.setField(jwtService, "accessTokenExpiration", 900000L);
        ReflectionTestUtils.setField(jwtService, "refreshTokenExpiration", 604800000L);
        ReflectionTestUtils.setField(jwtService, "issuer", "test-issuer");
    }

    @Test
    void shouldGenerateValidToken() {
        // Given
        UserDetails userDetails = User.builder()
                .username("test@example.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        // When
        String token = jwtService.generateToken(userDetails);

        // Then
        assertThat(token).isNotNull();
        assertThat(jwtService.extractUsername(token)).isEqualTo("test@example.com");
        assertThat(jwtService.isTokenValid(token, userDetails)).isTrue();
    }

    @Test
    void shouldExtractAllClaims() {
        // Given
        UserDetails userDetails = User.builder()
                .username("test@example.com")
                .password("password")
                .authorities("ROLE_USER", "ROLE_ADMIN")
                .build();

        String token = jwtService.generateToken(userDetails);

        // When
        Claims claims = jwtService.extractAllClaims(token);

        // Then
        assertThat(claims.getSubject()).isEqualTo("test@example.com");
        assertThat(claims.getIssuer()).isEqualTo("test-issuer");
        assertThat(claims.get("authorities")).asList()
                .containsExactly("ROLE_USER", "ROLE_ADMIN");
    }

    @Test
    void shouldDetectExpiredToken() {
        // Given
        UserDetails userDetails = User.builder()
                .username("test@example.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        // Generate token with expired time
        ReflectionTestUtils.setField(jwtService, "accessTokenExpiration", -1000L);
        String expiredToken = jwtService.generateToken(userDetails);

        // When/Then
        assertThat(jwtService.isTokenValid(expiredToken, userDetails)).isFalse();
    }

    @Test
    void shouldHandleInvalidToken() {
        // Given
        String invalidToken = "invalid.token.here";
        UserDetails userDetails = User.builder()
                .username("test@example.com")
                .password("password")
                .build();

        // When/Then
        assertThatThrownBy(() -> jwtService.extractUsername(invalidToken))
                .isInstanceOf(JwtException.class);
    }
}
```

### Testing Token Blacklist

```java
@ExtendWith(MockitoExtension.class)
class TokenBlacklistServiceTest {

    @Mock
    private RedisTemplate<String, String> redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    @InjectMocks
    private TokenBlacklistService blacklistService;

    @BeforeEach
    void setUp() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    }

    @Test
    void shouldBlacklistToken() {
        // Given
        String token = "test.jwt.token";

        // When
        blacklistService.blacklistToken(token, 900000L);

        // Then
        verify(valueOperations).set(
                eq("blacklist:jwt:" + DigestUtils.md5DigestAsHex(token.getBytes())),
                eq("1"),
                eq(900000L),
                eq(TimeUnit.MILLISECONDS)
        );
    }

    @Test
    void shouldDetectBlacklistedToken() {
        // Given
        String token = "test.jwt.token";
        String tokenId = "blacklist:jwt:" + DigestUtils.md5DigestAsHex(token.getBytes());

        when(redisTemplate.hasKey(tokenId)).thenReturn(true);

        // When
        boolean isBlacklisted = blacklistService.isBlacklisted(token);

        // Then
        assertThat(isBlacklisted).isTrue();
    }

    @Test
    void shouldReturnFalseForNonBlacklistedToken() {
        // Given
        String token = "test.jwt.token";
        String tokenId = "blacklist:jwt:" + DigestUtils.md5DigestAsHex(token.getBytes());

        when(redisTemplate.hasKey(tokenId)).thenReturn(false);

        // When
        boolean isBlacklisted = blacklistService.isBlacklisted(token);

        // Then
        assertThat(isBlacklisted).isFalse();
    }
}
```

### Testing JWT Authentication Filter

```java
@ExtendWith(MockitoExtension.class)
class JwtAuthenticationFilterTest {

    @Mock
    private JwtService jwtService;

    @Mock
    private UserDetailsService userDetailsService;

    @Mock
    private TokenBlacklistService blacklistService;

    @Mock
    private HttpServletRequest request;

    @Mock
    private HttpServletResponse response;

    @Mock
    private FilterChain filterChain;

    @InjectMocks
    private JwtAuthenticationFilter filter;

    @Test
    void shouldAuthenticateWithValidToken() throws Exception {
        // Given
        String token = "valid.jwt.token";
        String username = "test@example.com";
        UserDetails userDetails = User.builder()
                .username(username)
                .password("password")
                .authorities("ROLE_USER")
                .build();

        when(request.getHeader("Authorization")).thenReturn("Bearer " + token);
        when(blacklistService.isBlacklisted(token)).thenReturn(false);
        when(jwtService.extractUsername(token)).thenReturn(username);
        when(userDetailsService.loadUserByUsername(username)).thenReturn(userDetails);
        when(jwtService.isTokenValid(token, userDetails)).thenReturn(true);

        // When
        filter.doFilterInternal(request, response, filterChain);

        // Then
        ArgumentCaptor<UsernamePasswordAuthenticationToken> authCaptor =
                ArgumentCaptor.forClass(UsernamePasswordAuthenticationToken.class);
        verify(filterChain).doFilter(request, response);

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        assertThat(authentication).isNotNull();
        assertThat(authentication.getPrincipal()).isEqualTo(userDetails);
    }

    @Test
    void shouldSkipAuthenticationWithoutBearerToken() throws Exception {
        // Given
        when(request.getHeader("Authorization")).thenReturn(null);

        // When
        filter.doFilterInternal(request, response, filterChain);

        // Then
        verify(filterChain).doFilter(request, response);
        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
    }

    @Test
    void shouldSkipAuthenticationWithBlacklistedToken() throws Exception {
        // Given
        String token = "blacklisted.jwt.token";

        when(request.getHeader("Authorization")).thenReturn("Bearer " + token);
        when(blacklistService.isBlacklisted(token)).thenReturn(true);

        // When
        filter.doFilterInternal(request, response, filterChain);

        // Then
        verify(filterChain).doFilter(request, response);
        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
    }
}
```

## Integration Testing

### Testing Authentication Endpoints

```java
@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
@Transactional
class AuthenticationControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @BeforeEach
    void setUp() {
        User user = User.builder()
                .email("test@example.com")
                .password(passwordEncoder.encode("password123"))
                .firstName("Test")
                .lastName("User")
                .role(Role.USER)
                .enabled(true)
                .build();
        userRepository.save(user);
    }

    @Test
    void shouldAuthenticateUser() throws Exception {
        // Given
        LoginRequest request = new LoginRequest("test@example.com", "password123");

        // When & Then
        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").exists())
                .andExpect(jsonPath("$.refreshToken").exists())
                .andExpect(jsonPath("$.tokenType").value("Bearer"))
                .andExpect(jsonPath("$.expiresIn").exists());
    }

    @Test
    void shouldRejectInvalidCredentials() throws Exception {
        // Given
        LoginRequest request = new LoginRequest("test@example.com", "wrongpassword");

        // When & Then
        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.error").value("Invalid credentials"));
    }

    @Test
    void shouldRefreshToken() throws Exception {
        // Given
        LoginRequest loginRequest = new LoginRequest("test@example.com", "password123");
        MvcResult result = mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginRequest)))
                .andReturn();

        AuthenticationResponse authResponse = objectMapper.readValue(
                result.getResponse().getContentAsString(),
                AuthenticationResponse.class
        );

        RefreshTokenRequest refreshRequest = new RefreshTokenRequest(authResponse.getRefreshToken());

        // When & Then
        mockMvc.perform(post("/api/auth/refresh")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(refreshRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").exists());
    }
}
```

### Testing Secured Endpoints

```java
@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
@Transactional
class SecuredEndpointIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private UserRepository userRepository;

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    private String generateTokenForUser(String email, Role role) {
        User user = User.builder()
                .email(email)
                .password("password")
                .role(role)
                .enabled(true)
                .build();
        user = userRepository.save(user);

        return jwtService.generateToken(user);
    }

    @Test
    void shouldAccessEndpointWithValidToken() throws Exception {
        // Given
        String token = generateTokenForUser("user@example.com", Role.USER);

        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("user@example.com"));
    }

    @Test
    void shouldRejectRequestWithoutToken() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/users/me"))
                .andExpect(status().isForbidden());
    }

    @Test
    void shouldRejectRequestWithInvalidToken() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer invalid.token.here"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldAccessAdminEndpointWithAdminRole() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/admin/users"))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldRejectAdminEndpointWithUserRole() throws Exception {
        // When & Then
        mockMvc.perform(get("/api/admin/users"))
                .andExpect(status().isForbidden());
    }
}
```

### Testing with Testcontainers

```java
@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class JwtSecurityTestcontainersTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @Container
    static GenericContainer<?> redis = new GenericContainer<>("redis:7-alpine")
            .withExposedPorts(6379);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.redis.host", redis::getHost);
        registry.add("spring.redis.port", redis::getFirstMappedPort);
    }

    @Test
    void shouldWorkWithFullInfrastructure() {
        // Integration test with real database and Redis
    }
}
```

## Security Testing

### Testing Token Security

```java
@SpringBootTest
@AutoConfigureMockMvc
class JwtSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Test
    void shouldRejectTokenWithWrongSignature() throws Exception {
        // Given - Create token with different secret
        String maliciousToken = Jwts.builder()
                .setSubject("user@example.com")
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 900000))
                .signWith(Keys.secretKeyFor(SignatureAlgorithm.HS256))
                .compact();

        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer " + maliciousToken))
                .andExpect(status().isForbidden());
    }

    @Test
    void shouldRejectExpiredToken() throws Exception {
        // Given - Create expired token
        String expiredToken = Jwts.builder()
                .setSubject("user@example.com")
                .setIssuedAt(new Date(System.currentTimeMillis() - 3600000))
                .setExpiration(new Date(System.currentTimeMillis() - 1800000))
                .signWith(Keys.secretKeyFor(SignatureAlgorithm.HS256))
                .compact();

        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer " + expiredToken))
                .andExpect(status().isForbidden());
    }

    @Test
    void shouldRejectTokenWithInvalidClaims() throws Exception {
        // Given - Create token with invalid issuer
        SecretKey key = Keys.secretKeyFor(SignatureAlgorithm.HS256);
        String tokenWithInvalidIssuer = Jwts.builder()
                .setSubject("user@example.com")
                .setIssuer("invalid-issuer")
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 900000))
                .signWith(key)
                .compact();

        // Set the same key in service
        ReflectionTestUtils.setField(jwtService, "secret", Encoders.BASE64.encode(key.getEncoded()));

        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer " + tokenWithInvalidIssuer))
                .andExpect(status().isForbidden());
    }
}
```

### Testing Rate Limiting

```java
@SpringBootTest
@AutoConfigureMockMvc
class JwtRateLimitTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldRateLimitLoginAttempts() throws Exception {
        // Given
        LoginRequest request = new LoginRequest("user@example.com", "wrongpassword");

        // When - Make multiple failed attempts
        for (int i = 0; i < 5; i++) {
            mockMvc.perform(post("/api/auth/authenticate")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized());
        }

        // Then - 6th attempt should be rate limited
        mockMvc.perform(post("/api/auth/authenticate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isTooManyRequests());
    }
}
```

### Testing Token Blacklisting

```java
@SpringBootTest
@AutoConfigureMockMvc
class TokenBlacklistTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private TokenBlacklistService blacklistService;

    @Test
    void shouldRejectBlacklistedToken() throws Exception {
        // Given
        UserDetails user = User.builder()
                .username("user@example.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        String token = jwtService.generateToken(user);
        blacklistService.blacklistToken(token);

        // When & Then
        mockMvc.perform(get("/api/users/me")
                .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());
    }

    @Test
    void shouldBlacklistTokenOnLogout() throws Exception {
        // Given
        UserDetails user = User.builder()
                .username("user@example.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        String token = jwtService.generateToken(user);
        LogoutRequest logoutRequest = new LogoutRequest(token);

        // When
        mockMvc.perform(post("/api/auth/logout")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(logoutRequest)))
                .andExpect(status().isOk());

        // Then
        assertThat(blacklistService.isBlacklisted(token)).isTrue();
    }
}
```

## Performance Testing

### JWT Generation Performance

```java
@SpringBootTest
@AutoConfigureMockMvc
class JwtPerformanceTest {

    @Autowired
    private JwtService jwtService;

    @Test
    void measureTokenGenerationPerformance() {
        // Given
        UserDetails user = User.builder()
                .username("performance@test.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        // Warm up
        for (int i = 0; i < 1000; i++) {
            jwtService.generateToken(user);
        }

        // Measure
        long startTime = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            jwtService.generateToken(user);
        }
        long endTime = System.nanoTime();

        long durationMs = (endTime - startTime) / 1_000_000;
        double avgTimeMs = durationMs / 10000.0;

        log.info("Average token generation time: {} ms", avgTimeMs);
        assertThat(avgTimeMs).isLessThan(1.0); // Should be less than 1ms per token
    }
}
```

### Concurrent Token Validation

```java
@SpringBootTest
class JwtConcurrencyTest {

    @Autowired
    private JwtService jwtService;

    @Test
    void testConcurrentTokenValidation() throws InterruptedException {
        // Given
        UserDetails user = User.builder()
                .username("concurrent@test.com")
                .password("password")
                .authorities("ROLE_USER")
                .build();

        String token = jwtService.generateToken(user);

        // When
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(1000);
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failureCount = new AtomicInteger(0);

        for (int i = 0; i < 1000; i++) {
            executor.submit(() -> {
                try {
                    if (jwtService.isTokenValid(token, user)) {
                        successCount.incrementAndGet();
                    } else {
                        failureCount.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await();
        executor.shutdown();

        // Then
        assertThat(successCount.get()).isEqualTo(1000);
        assertThat(failureCount.get()).isEqualTo(0);
    }
}
```

## Test Data Management

### Test Data Builders

```java
@TestConfiguration
public class TestDataFactory {

    public static User.UserBuilder userBuilder() {
        return User.builder()
                .email("test@example.com")
                .password("password123")
                .firstName("Test")
                .lastName("User")
                .role(Role.USER)
                .enabled(true)
                .emailVerified(true);
    }

    public static LoginRequest loginRequest(String email, String password) {
        return new LoginRequest(email, password);
    }

    public static String generateValidToken(JwtService jwtService, UserDetails user) {
        return jwtService.generateToken(user);
    }

    public static String generateExpiredToken(JwtService jwtService, UserDetails user) {
        // Generate token with past expiration
        return Jwts.builder()
                .setSubject(user.getUsername())
                .setIssuedAt(new Date(System.currentTimeMillis() - 3600000))
                .setExpiration(new Date(System.currentTimeMillis() - 1800000))
                .signWith(Keys.secretKeyFor(SignatureAlgorithm.HS256))
                .compact();
    }
}
```

### Database Test Data

```java
@TestConfiguration
public class DatabaseTestData {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public User createTestUser(String email, Role role) {
        User user = User.builder()
                .email(email)
                .password(passwordEncoder.encode("password123"))
                .firstName("Test")
                .lastName("User")
                .role(role)
                .enabled(true)
                .emailVerified(true)
                .build();
        return userRepository.save(user);
    }

    public void cleanUp() {
        userRepository.deleteAll();
    }
}
```

## Mock Strategies

### Mocking JWT Service

```java
@TestConfiguration
public class JwtTestConfig {

    @Bean
    @Primary
    public JwtService jwtService() {
        JwtService mockService = Mockito.mock(JwtService.class);

        // Configure default behavior
        when(mockService.generateToken(any(UserDetails.class)))
                .thenReturn("mock.jwt.token");

        when(mockService.isTokenValid(anyString(), any(UserDetails.class)))
                .thenReturn(true);

        when(mockService.extractUsername(anyString()))
                .thenReturn("test@example.com");

        return mockService;
    }
}
```

### Mocking Authentication

```java
@WebMvcTest(controllers = UserController.class)
@Import(JwtTestConfig.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @WithMockUser(username = "test@example.com", roles = {"USER"})
    void shouldAccessWithMockUser() throws Exception {
        mockMvc.perform(get("/api/users/me"))
                .andExpect(status().isOk());
    }

    @Test
    void shouldAccessWithMockJwt() throws Exception {
        Jwt jwt = Jwt.withTokenValue("mock.jwt.token")
                .header("alg", "HS256")
                .claim("sub", "test@example.com")
                .claim("scope", "ROLE_USER")
                .build();

        SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthenticationToken(jwt)
        );

        mockMvc.perform(get("/api/users/me"))
                .andExpect(status().isOk());
    }
}
```

## Continuous Testing

### GitHub Actions Workflow

```yaml
name: JWT Security Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Cache Maven dependencies
        uses: actions/cache@v3
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-m2

      - name: Run JWT security tests
        run: mvn test -Dspring.profiles.active=test

      - name: Generate test report
        uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: JWT Security Test Results
          path: target/surefire-reports/*.xml
          reporter: java-junit
```

### Test Coverage

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <configuration>
        <excludes>
            <exclude>**/config/**</exclude>
            <exclude>**/dto/**</exclude>
            <exclude>**/entity/**</exclude>
            <exclude>**/Application.class</exclude>
        </excludes>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>jacoco-check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>PACKAGE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## Best Practices

1. **Test Pyramid**: Maintain proper test pyramid with more unit tests than integration tests
2. **Test Isolation**: Each test should be independent and not rely on test execution order
3. **Test Data**: Use realistic test data that covers edge cases
4. **Performance**: Include performance tests for JWT operations
5. **Security**: Test both positive and negative security scenarios
6. **Mocking**: Mock external dependencies for unit tests
7. **Coverage**: Aim for at least 80% code coverage
8. **Automation**: Integrate tests into CI/CD pipeline

## References

- [Spring Security Testing](https://docs.spring.io/spring-security/reference/servlet/test/index.html)
- [Testcontainers](https://www.testcontainers.org/)
- [JUnit 5 Documentation](https://junit.org/junit5/docs/current/user-guide/)
- [Mockito Documentation](https://site.mockito.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html)