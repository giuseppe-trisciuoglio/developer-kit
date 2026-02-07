# Security Hardening Checklist

## Secure Configuration

### Production Security Headers
```java
@Configuration
public class SecurityHeadersConfig {

    @Bean
    public SecurityFilterChain securityHeadersFilterChain(HttpSecurity http) throws Exception {
        return http
            .headers(headers -> headers
                .contentTypeOptions(cto -> cto.and()
                    .xssProtection(xss -> xss
                        .headerValue(XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
                    .httpStrictTransportSecurity(hsts -> hsts
                        .maxAgeInSeconds(31536000)
                        .includeSubdomains(true)
                        .preload(true))
                    .frameOptions(frame -> frame
                        .deny()
                        .and())
                    .contentSecurityPolicy(csp -> csp
                        .policyDirectives(
                            "default-src 'self'; " +
                            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
                            "style-src 'self' 'unsafe-inline'; " +
                            "img-src 'self' data: https:; " +
                            "font-src 'self'; " +
                            "connect-src 'self'; " +
                            "frame-ancestors 'none'; " +
                            "base-uri 'self'; " +
                            "form-action 'self'; " +
                            "upgrade-insecure-requests;"
                        )
                        .and())
                    .referrerPolicy(referrer -> referrer
                        .policy(ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))
                    .permissionsPolicy(permissions -> permissions
                        .policy(
                            "geolocation=(), " +
                            "microphone=(), " +
                            "camera=(), " +
                            "payment=(), " +
                            "usb=(), " +
                            "magnetometer=(), " +
                            "gyroscope=(), " +
                            "accelerometer=()"
                        ))
                )
            )
            .build();
    }
}
```

### Enhanced Password Security
```java
@Service
public class SecurePasswordService {

    private final PasswordEncoder passwordEncoder;
    private final PasswordHistoryRepository passwordHistoryRepository;
    private final PasswordPolicy passwordPolicy;

    public String encodePassword(String rawPassword) {
        // Use Argon2 for better security
        return passwordEncoder.encode(rawPassword);
    }

    public void validatePassword(String password, User user) {
        // Check password against policy
        if (!meetsPasswordPolicy(password)) {
            throw new PasswordPolicyViolationException(getPasswordPolicyViolations(password));
        }

        // Check against password history
        if (isPasswordReused(password, user)) {
            throw new PasswordReusedException("Password has been used before");
        }

        // Check against breached passwords
        if (isBreachedPassword(password)) {
            throw new BreachedPasswordException("Password has been exposed in data breaches");
        }
    }

    private boolean meetsPasswordPolicy(String password) {
        return password.length() >= passwordPolicy.getMinLength() &&
               password.matches(".*[A-Z].*") && // At least one uppercase
               password.matches(".*[a-z].*") && // At least one lowercase
               password.matches(".*\\d.*") &&    // At least one digit
               password.matches(".*[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?].*"); // Special char
    }

    @Async
    public CompletableFuture<Boolean> isBreachedPasswordAsync(String password) {
        String sha1Hash = DigestUtils.sha1Hex(password);
        String prefix = sha1Hash.substring(0, 5);
        String suffix = sha1Hash.substring(5);

        return CompletableFuture.supplyAsync(() -> {
            try {
                String response = restTemplate.getForObject(
                    "https://api.pwnedpasswords.com/range/" + prefix, String.class);

                if (response != null) {
                    return Arrays.stream(response.split("\\r?\\n"))
                        .anyMatch(line -> line.startsWith(suffix.toUpperCase()));
                }
            } catch (Exception e) {
                log.warn("Failed to check breached password API", e);
            }
            return false;
        });
    }
}

@Configuration
public class PasswordConfig {

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
}
```

## Advanced Attack Prevention

### Rate Limiting and Brute Force Protection
```java
@Component
public class BruteForceProtectionService {

    private final LoadingCache<String, Integer> loginAttemptsCache;
    private final LoadingCache<String, Long> lockoutCache;
    private final int maxAttempts;
    private final Duration lockoutDuration;

    public BruteForceProtectionService() {
        this.maxAttempts = 5;
        this.lockoutDuration = Duration.ofMinutes(15);

        this.loginAttemptsCache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofMinutes(15))
            .build(key -> 0);

        this.lockoutCache = Caffeine.newBuilder()
            .expireAfterWrite(lockoutDuration)
            .build(key -> 0L);
    }

    public void recordFailedAttempt(String identifier) {
        int attempts = loginAttemptsCache.asMap().merge(identifier, 1, Integer::sum);

        if (attempts >= maxAttempts) {
            lockout(identifier);
            publishSecurityEvent("ACCOUNT_LOCKED", identifier);
        }
    }

    public void recordSuccessfulAttempt(String identifier) {
        loginAttemptsCache.invalidate(identifier);
        lockoutCache.invalidate(identifier);
    }

    public boolean isLockedOut(String identifier) {
        Long lockTime = lockoutCache.getIfPresent(identifier);
        return lockTime != null && lockTime > 0;
    }

    private void lockout(String identifier) {
        lockoutCache.put(identifier, System.currentTimeMillis());
    }

    @EventListener
    @Async
    public void handleAuthenticationFailure(AuthenticationFailureBadCredentialsEvent event) {
        String username = event.getAuthentication().getName();
        recordFailedAttempt(username);

        // Also track by IP
        String clientIp = getClientIpAddress();
        recordFailedAttempt(clientIp);
    }
}

@RestController
@RequestMapping("/api/auth")
public class SecureAuthController {

    private final BruteForceProtectionService bruteForceProtection;
    private final RecaptchaService recaptchaService;

    @PostMapping("/login")
    @RateLimited(requests = 5, window = "PT1M")
    public ResponseEntity<LoginResponse> login(
            @RequestBody LoginRequest request,
            HttpServletRequest httpRequest) {

        String clientIp = getClientIpAddress(httpRequest);

        // Check IP-based rate limiting
        if (bruteForceProtection.isLockedOut(clientIp)) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .body(new ErrorResponse("Too many failed attempts. Please try again later."));
        }

        // Check username-based rate limiting
        if (bruteForceProtection.isLockedOut(request.username())) {
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .body(new ErrorResponse("Account temporarily locked due to failed attempts."));
        }

        // Verify reCAPTCHA for suspicious activity
        if (shouldRequireRecaptcha(request.username(), clientIp)) {
            if (!recaptchaService.verifyRecaptcha(request.recaptchaToken(), clientIp)) {
                return ResponseEntity.badRequest()
                    .body(new ErrorResponse("Invalid reCAPTCHA"));
            }
        }

        // Proceed with authentication
        return performAuthentication(request);
    }
}
```

### CSRF Protection with State Management
```java
@Configuration
public class CsrfConfig {

    @Bean
    public CsrfTokenRepository customCsrfTokenRepository() {
        HttpSessionCsrfTokenRepository repository = new HttpSessionCsrfTokenRepository();
        repository.setHeaderName("X-CSRF-TOKEN");
        repository.setParameterName("_csrf");
        return repository;
    }

    @Bean
    public SecurityFilterChain csrfFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf
                .csrfTokenRepository(customCsrfTokenRepository())
                .ignoringRequestMatchers("/api/auth/**")
                .csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler())
                .and()
            )
            .addFilterAfter(new CsrfCookieFilter(), BasicAuthenticationFilter.class)
            .build();
    }
}

@Component
public class CsrfCookieFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {

        CsrfToken csrfToken = (CsrfToken) request.getAttribute(CsrfToken.class.getName());

        if (csrfToken != null) {
            Cookie cookie = new Cookie("XSRF-TOKEN", csrfToken.getToken());
            cookie.setPath("/");
            cookie.setHttpOnly(false);
            cookie.setSecure(true);
            cookie.setMaxAge(-1);
            response.addCookie(cookie);
        }

        filterChain.doFilter(request, response);
    }
}
```

## Input Validation and Sanitization

### Request Validation Filter
```java
@Component
public class SecurityValidationFilter implements Filter {

    private final InputSanitizer inputSanitizer;
    private final XssProtectionService xssProtection;

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                        FilterChain chain) throws IOException, ServletException {

        // Wrap request for validation
        SecurityValidatedRequestWrapper wrappedRequest =
            new SecurityValidatedRequestWrapper((HttpServletRequest) request);

        // Validate all inputs
        if (!validateRequest(wrappedRequest)) {
            ((HttpServletResponse) response).sendError(
                HttpServletResponse.SC_BAD_REQUEST, "Invalid input detected");
            return;
        }

        chain.doFilter(wrappedRequest, response);
    }

    private boolean validateRequest(SecurityValidatedRequestWrapper request) {
        try {
            // Validate query parameters
            request.getParameterMap().forEach((key, values) -> {
                if (xssProtection.containsXss(key) ||
                    Arrays.stream(values).anyMatch(xssProtection::containsXss)) {
                    throw new SecurityException("XSS detected in parameters");
                }
            });

            // Validate headers for injection attacks
            Collections.list(request.getHeaderNames()).forEach(headerName -> {
                if (isSuspiciousHeader(headerName, request.getHeader(headerName))) {
                    throw new SecurityException("Suspicious header detected");
                }
            });

            return true;

        } catch (Exception e) {
            log.warn("Request validation failed", e);
            return false;
        }
    }

    private boolean isSuspiciousHeader(String headerName, String headerValue) {
        String suspiciousPatterns = "(?i)(script|javascript|vbscript|onload|onerror|onclick)";
        return headerName.matches(suspiciousPatterns) || headerValue.matches(suspiciousPatterns);
    }
}

@Component
public class XssProtectionService {

    private final Pattern[] xssPatterns = {
        Pattern.compile("<script[^>]*>.*?</script>", Pattern.CASE_INSENSITIVE),
        Pattern.compile("javascript:", Pattern.CASE_INSENSITIVE),
        Pattern.compile("vbscript:", Pattern.CASE_INSENSITIVE),
        Pattern.compile("onload(.*?)=", Pattern.CASE_INSENSITIVE),
        Pattern.compile("onerror(.*?)=", Pattern.CASE_INSENSITIVE),
        Pattern.compile("onclick(.*?)=", Pattern.CASE_INSENSITIVE),
        Pattern.compile("<img[^>]*src[^=]*=[\"']?javascript:", Pattern.CASE_INSENSITIVE)
    };

    public boolean containsXss(String input) {
        if (input == null || input.isEmpty()) {
            return false;
        }

        for (Pattern pattern : xssPatterns) {
            if (pattern.matcher(input).find()) {
                return true;
            }
        }

        return false;
    }

    public String sanitize(String input) {
        if (input == null) {
            return null;
        }

        // HTML encode
        String sanitized = HtmlUtils.htmlEscape(input);

        // Remove potentially dangerous tags
        sanitized = sanitized.replaceAll("<script[^>]*>.*?</script>", "");
        sanitized = sanitized.replaceAll("javascript:", "");
        sanitized = sanitized.replaceAll("vbscript:", "");

        return sanitized;
    }
}
```

### SQL Injection Prevention
```java
@Repository
public class SecureUserRepository {

    @PersistenceContext
    private EntityManager entityManager;

    public User findByEmailSafe(String email) {
        // Using parameterized query
        String jpql = "SELECT u FROM User u WHERE u.email = :email";
        TypedQuery<User> query = entityManager.createQuery(jpql, User.class);
        query.setParameter("email", email);
        return query.getSingleResult();
    }

    public List<User> searchUsersSecure(String searchTerm) {
        // Validate search term first
        if (!isValidSearchTerm(searchTerm)) {
            throw new InvalidSearchTermException("Invalid search term");
        }

        // Using Criteria API for dynamic queries
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> root = query.from(User.class);

        // Build safe search predicate
        Predicate predicate = cb.or(
            cb.like(root.get("email"), "%" + escapeSql(searchTerm) + "%"),
            cb.like(root.get("firstName"), "%" + escapeSql(searchTerm) + "%"),
            cb.like(root.get("lastName"), "%" + escapeSql(searchTerm) + "%")
        );

        query.where(predicate);
        return entityManager.createQuery(query).getResultList();
    }

    private boolean isValidSearchTerm(String term) {
        // Check for SQL injection patterns
        String[] dangerousPatterns = {
            "'", "\"", ";", "--", "/*", "*/",
            "xp_", "sp_", "DROP", "DELETE", "UPDATE",
            "INSERT", "UNION", "SELECT", "EXEC"
        };

        String upperTerm = term.toUpperCase();
        return Arrays.stream(dangerousPatterns)
            .noneMatch(upperTerm::contains);
    }

    private String escapeSql(String input) {
        return input.replace("'", "''");
    }
}
```

## Secure Key Management

### Key Rotation Service
```java
@Service
public class KeyRotationService {

    private final JwtKeyStore keyStore;
    private final JwtEncoder jwtEncoder;
    private final ApplicationEventPublisher eventPublisher;

    @Value("${jwt.rotation.enabled:true}")
    private boolean rotationEnabled;

    @Value("${jwt.rotation.schedule:0 0 2 * * ?}") // 2 AM daily
    private String rotationSchedule;

    @Scheduled(cron = "${jwt.rotation.schedule}")
    public void rotateKeys() {
        if (!rotationEnabled) {
            log.info("Key rotation is disabled");
            return;
        }

        try {
            log.info("Starting JWT key rotation");

            // Generate new key pair
            KeyPair newKeyPair = generateNewKeyPair();
            String newKeyId = generateKeyId();

            // Add new key to store
            keyStore.addKey(newKeyId, newKeyPair);

            // Promote new key to primary after grace period
            scheduleKeyPromotion(newKeyId);

            // Mark old key for retirement
            String oldKeyId = keyStore.getCurrentKeyId();
            if (oldKeyId != null) {
                scheduleKeyRetirement(oldKeyId);
            }

            // Publish rotation event
            eventPublisher.publishEvent(new KeyRotationEvent(oldKeyId, newKeyId));

            log.info("JWT key rotation completed successfully");

        } catch (Exception e) {
            log.error("Failed to rotate JWT keys", e);
            eventPublisher.publishEvent(new KeyRotationFailedEvent(e));
        }
    }

    private KeyPair generateNewKeyPair() {
        try {
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
            keyGen.initialize(2048);
            return keyGen.generateKeyPair();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate key pair", e);
        }
    }

    @EventListener
    public void handleKeyRotation(KeyRotationEvent event) {
        log.info("Key rotated from {} to {}", event.getOldKeyId(), event.getNewKeyId());

        // Invalidate all existing refresh tokens if required
        if (shouldInvalidateTokensOnRotation()) {
            refreshTokenService.invalidateAllTokens();
        }
    }
}

@Component
public class SecureKeyStore {

    private final Map<String, KeyPair> keys = new ConcurrentHashMap<>();
    private volatile String currentKeyId;

    @PostConstruct
    public void initialize() {
        // Load keys from secure storage
        loadKeysFromSecureStorage();
    }

    public RSAPrivateKey getCurrentPrivateKey() {
        KeyPair currentKey = keys.get(currentKeyId);
        if (currentKey == null) {
            throw new IllegalStateException("No current key available");
        }
        return (RSAPrivateKey) currentKey.getPrivate();
    }

    public RSAPublicKey getPublicKey(String keyId) {
        KeyPair keyPair = keys.get(keyId);
        if (keyPair == null) {
            throw new IllegalArgumentException("Key not found: " + keyId);
        }
        return (RSAPublicKey) keyPair.getPublic();
    }

    public void addKey(String keyId, KeyPair keyPair) {
        // Store key in secure storage
        storeKeySecurely(keyId, keyPair);
        keys.put(keyId, keyPair);
    }

    private void storeKeySecurely(String keyId, KeyPair keyPair) {
        // Implement secure storage (e.g., AWS KMS, HashiCorp Vault)
        // Never store private keys in application properties or files
    }

    private void loadKeysFromSecureStorage() {
        // Load keys from secure storage
        // This should integrate with your organization's key management solution
    }
}
```

## Security Monitoring and Alerting

### Security Event Monitoring
```java
@Component
@Slf4j
public class SecurityEventMonitor {

    private final MeterRegistry meterRegistry;
    private final AlertService alertService;

    @EventListener
    @Async
    public void monitorAuthenticationFailure(AuthenticationFailureBadCredentialsEvent event) {
        String username = event.getAuthentication().getName();
        String clientIp = getClientIp();

        // Record metrics
        Counter.builder("security.auth.failures")
            .tag("username", maskUsername(username))
            .tag("ip", clientIp)
            .register(meterRegistry)
            .increment();

        // Check for attack patterns
        checkForAttackPatterns(username, clientIp);
    }

    @EventListener
    @Async
    public void monitorSuspiciousActivity(SuspiciousActivityEvent event) {
        // Record security event
        Gauge.builder("security.suspicious.activities")
            .tag("type", event.getActivityType())
            .register(meterRegistry, () -> 1);

        // Determine severity
        SecuritySeverity severity = calculateSeverity(event);

        // Send alert if high severity
        if (severity == SecuritySeverity.HIGH || severity == SecuritySeverity.CRITICAL) {
            alertService.sendSecurityAlert(event, severity);
        }

        // Log with appropriate level
        switch (severity) {
            case CRITICAL:
                log.error("CRITICAL security event: {}", event);
                break;
            case HIGH:
                log.warn("HIGH security event: {}", event);
                break;
            default:
                log.info("Security event: {}", event);
        }
    }

    private void checkForAttackPatterns(String username, String clientIp) {
        // Check for credential stuffing
        if (isCredentialStuffingAttack(username, clientIp)) {
            publishSecurityEvent("CREDENTIAL_STUFFING", Map.of(
                "username", username,
                "ip", clientIp
            ));
        }

        // Check for brute force attack
        if (isBruteForceAttack(clientIp)) {
            publishSecurityEvent("BRUTE_FORCE", Map.of("ip", clientIp));
        }

        // Check for password spraying
        if (isPasswordSprayingAttack(clientIp)) {
            publishSecurityEvent("PASSWORD_SPRAYING", Map.of("ip", clientIp));
        }
    }
}
```

### Security Health Indicator
```java
@Component
public class SecurityHealthIndicator implements HealthIndicator {

    private final SecurityConfigService securityConfig;
    private final VulnerabilityScanner vulnerabilityScanner;

    @Override
    public Health health() {
        try {
            Health.Builder builder = Health.up();

            // Check security configuration
            SecurityConfigurationStatus configStatus = securityConfig.validateConfiguration();
            builder.withDetail("securityConfig", configStatus);

            if (!configStatus.isSecure()) {
                builder.status(Status.WARNING)
                    .withDetail("configIssues", configStatus.getIssues());
            }

            // Check for known vulnerabilities
            List<Vulnerability> vulnerabilities = vulnerabilityScanner.scan();
            if (!vulnerabilities.isEmpty()) {
                builder.status(Status.WARNING)
                    .withDetail("vulnerabilities", vulnerabilities);
            }

            // Check key expiration
            KeyStatus keyStatus = securityConfig.checkKeyStatus();
            builder.withDetail("keyStatus", keyStatus);

            if (keyStatus.isExpiringSoon()) {
                builder.status(Status.WARNING)
                    .withDetail("keyWarning", "Keys will expire soon");
            }

            // Check SSL/TLS certificates
            CertificateStatus certStatus = securityConfig.checkCertificates();
            builder.withDetail("certificateStatus", certStatus);

            if (certStatus.hasExpiringCertificates()) {
                builder.status(Status.WARNING)
                    .withDetail("certWarning", "Some certificates will expire soon");
            }

            return builder.build();

        } catch (Exception e) {
            return Health.down(e)
                .withDetail("error", "Security health check failed")
                .build();
        }
    }
}
```

## Security Audit Logging

### Comprehensive Audit Logger
```java
@Component
@Slf4j
public class SecurityAuditLogger {

    private final AuditLogRepository auditLogRepository;
    private final ObjectMapper objectMapper;

    @EventListener
    @Async("auditEventExecutor")
    public void auditAuthenticationEvent(AuthenticationEvent event) {
        AuditLog auditLog = AuditLog.builder()
            .eventType(event.getType())
            .userId(extractUserId(event))
            .username(extractUsername(event))
            .clientIp(event.getClientIp())
            .userAgent(event.getUserAgent())
            .resource(event.getResource())
            .action(event.getAction())
            .result(event.getResult())
            .timestamp(Instant.now())
            .build();

        // Add additional context
        Map<String, Object> context = new HashMap<>();
        context.put("sessionId", event.getSessionId());
        context.put("requestId", event.getRequestId());

        if (event.getFailureReason() != null) {
            context.put("failureReason", event.getFailureReason());
        }

        auditLog.setContext(serializeContext(context));

        // Save to database
        auditLogRepository.save(auditLog);

        // Log to file
        logAuditEvent(auditLog);
    }

    @EventListener
    @Async
    public void auditDataAccess(DataAccessEvent event) {
        AuditLog auditLog = AuditLog.builder()
            .eventType("DATA_ACCESS")
            .userId(event.getUserId())
            .resource(event.getResource())
            .action(event.getAction())
            .clientIp(event.getClientIp())
            .timestamp(Instant.now())
            .result("SUCCESS")
            .build();

        // Record what data was accessed
        Map<String, Object> context = new HashMap<>();
        context.put("recordIds", event.getRecordIds());
        context.put("fields", event.getAccessedFields());
        context.put("query", event.getQuery());

        auditLog.setContext(serializeContext(context));
        auditLogRepository.save(auditLog);
    }

    @Scheduled(fixedRate = 3600000) // Hourly
    public void generateSecurityReport() {
        SecurityReport report = securityReportGenerator.generateHourlyReport();
        reportService.sendReport(report);
    }

    private void logAuditEvent(AuditLog auditLog) {
        try {
            String logMessage = objectMapper.writeValueAsString(auditLog);
            log.info("AUDIT: {}", logMessage);
        } catch (Exception e) {
            log.error("Failed to serialize audit log", e);
        }
    }

    private String serializeContext(Map<String, Object> context) {
        try {
            return objectMapper.writeValueAsString(context);
        } catch (Exception e) {
            return "{}";
        }
    }
}
```

### GDPR Compliance Features
```java
@Service
public class GdprComplianceService {

    @Transactional
    public UserDataExport exportUserData(String userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));

        return UserDataExport.builder()
            .user(extractUserData(user))
            .authHistory(getAuthenticationHistory(userId))
            .consents(getConsents(userId))
            .activityLogs(getActivityLogs(userId))
            .exportDate(Instant.now())
            .build();
    }

    @Transactional
    public void deleteUserData(String userId) {
        // Anonymize user data instead of hard delete for audit purposes
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));

        // Mark as deleted
        user.setEmail(generateAnonymizedEmail());
        user.setFirstName("DELETED");
        user.setLastName("USER");
        user.setPhoneNumber(null);
        user.setDeletedAt(Instant.now());

        userRepository.save(user);

        // Delete sensitive data
        refreshTokenService.deleteAllUserTokens(user);
        auditLogService.anonymizeAuditLogs(userId);

        // Record deletion
        auditLogger.logDataDeletion(userId, "GDPR_REQUEST");
    }

    private String generateAnonymizedEmail() {
        return "deleted-" + UUID.randomUUID() + "@deleted.local";
    }

    @EventListener
    public void handleDataSubjectRequest(DataSubjectRequestEvent event) {
        switch (event.getRequestType()) {
            case ACCESS:
                processAccessRequest(event);
                break;
            case DELETION:
                processDeletionRequest(event);
                break;
            case RECTIFICATION:
                processRectificationRequest(event);
                break;
        }
    }
}