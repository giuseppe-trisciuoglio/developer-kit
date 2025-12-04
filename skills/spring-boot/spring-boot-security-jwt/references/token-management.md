# Token Management Best Practices

## Refresh Token Strategy

### Secure Refresh Token Storage
```java
@Entity
@Table(name = "refresh_tokens")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RefreshToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false, columnDefinition = "TEXT")
    private String token;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "token_id", unique = true, nullable = false)
    private String tokenId; // JWT ID (jti claim)

    @Column(name = "session_id")
    private String sessionId; // Session identifier

    @Column(name = "device_id")
    private String deviceId; // Device fingerprint

    @Column(name = "device_info")
    private String deviceInfo; // User agent and device details

    @Column(name = "ip_address")
    private String ipAddress;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    @Column(name = "last_used_at")
    private Instant lastUsedAt;

    @Column(name = "revoked_at")
    private Instant revokedAt;

    @Column(name = "replaced_by")
    private String replacedBy; // New token ID if rotated

    @Column(nullable = false)
    private boolean revoked = false;

    @Column(nullable = false)
    private boolean active = true;

    // Token metadata
    @Column(name = "usage_count")
    private int usageCount = 0;

    @Column(name = "max_usage")
    private Integer maxUsage; // Optional usage limit

    public boolean isExpired() {
        return Instant.now().isAfter(expiresAt);
    }

    public boolean isValid() {
        return !revoked && active && !isExpired();
    }

    public void revoke() {
        this.revoked = true;
        this.revokedAt = Instant.now();
        this.active = false;
    }

    public void markUsed() {
        this.lastUsedAt = Instant.now();
        this.usageCount++;
    }
}
```

### Refresh Token Repository
```java
@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {

    Optional<RefreshToken> findByToken(String token);

    Optional<RefreshToken> findByTokenId(String tokenId);

    List<RefreshToken> findByUserAndRevokedFalse(User user);

    List<RefreshToken> findByUserAndRevokedFalseAndExpiresAtAfter(User user, Instant now);

    List<RefreshToken> findByExpiresAtBefore(Instant cutoff);

    List<RefreshToken> findByRevokedTrueAndRevokedAtBefore(Instant cutoff);

    @Query("SELECT rt FROM RefreshToken rt WHERE rt.user = :user AND rt.revoked = false ORDER BY rt.createdAt ASC")
    List<RefreshToken> findOldestActiveTokensByUser(@Param("user") User user);

    @Query("SELECT COUNT(rt) FROM RefreshToken rt WHERE rt.user = :user AND rt.revoked = false AND rt.expiresAt > :now")
    long countActiveTokensByUser(@Param("user") User user, @Param("now") Instant now);

    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.user = :user AND rt.createdAt < :cutoff")
    void deleteOldTokensByUser(@Param("user") User user, @Param("cutoff") Instant cutoff);
}
```

### Refresh Token Service with Rotation
```java
@Service
@Transactional
@Slf4j
public class RefreshTokenService {

    private final RefreshTokenRepository refreshTokenRepository;
    private final UserRepository userRepository;
    private final JwtTokenService jwtTokenService;
    private final JwtClaimsService claimsService;

    @Value("${jwt.refresh-token-expiration:P7D}")
    private Duration refreshTokenExpiration;

    @Value("${jwt.max-active-tokens:5}")
    private int maxActiveTokensPerUser;

    @Value("${jwt.token-rotation-enabled:true}")
    private boolean tokenRotationEnabled;

    @Value("${jwt.token-rotation-threshold:P3D}")
    private Duration tokenRotationThreshold;

    public RefreshTokenResponse createRefreshToken(User user, HttpServletRequest request) {
        // Enforce maximum active tokens
        enforceMaxActiveTokens(user);

        // Extract request information
        String ipAddress = extractIpAddress(request);
        String deviceInfo = extractDeviceInfo(request);
        String deviceId = generateDeviceId(request);

        // Create JWT claims
        JwtClaimsSet claims = claimsService.createRefreshTokenClaims(user);
        String tokenValue = jwtTokenService.encodeToken(claims);

        // Create refresh token entity
        RefreshToken refreshToken = RefreshToken.builder()
            .token(tokenValue)
            .user(user)
            .tokenId(claims.getClaimAsString("jti"))
            .sessionId(claims.getClaimAsString("sessionId"))
            .deviceId(deviceId)
            .deviceInfo(deviceInfo)
            .ipAddress(ipAddress)
            .createdAt(Instant.now())
            .expiresAt(claims.getExpiresAt())
            .active(true)
            .revoked(false)
            .build();

        refreshToken = refreshTokenRepository.save(refreshToken);

        // Publish token created event
        applicationEventPublisher.publishEvent(
            new RefreshTokenCreatedEvent(refreshToken));

        return new RefreshTokenResponse(
            refreshToken.getToken(),
            refreshToken.getExpiresAt().toEpochMilli(),
            refreshToken.getSessionId()
        );
    }

    @Transactional
    public AccessTokenResponse refreshToken(RefreshTokenRequest request,
            HttpServletRequest httpRequest) {

        String refreshTokenValue = request.refreshToken();
        String ipAddress = extractIpAddress(httpRequest);

        // Validate and retrieve refresh token
        RefreshToken refreshToken = validateRefreshToken(refreshTokenValue, ipAddress);

        User user = refreshToken.getUser();

        // Check account status
        validateUserAccount(user);

        // Mark token as used
        refreshToken.markUsed();
        refreshTokenRepository.save(refreshToken);

        // Generate new access token
        AccessTokenResponse accessToken = jwtTokenService.generateAccessToken(user);

        // Implement token rotation if enabled
        if (shouldRotateRefreshToken(refreshToken)) {
            RefreshTokenResponse newRefreshToken = createRefreshToken(user, httpRequest);

            // Mark old token as replaced
            refreshToken.setReplacedBy(extractTokenId(newRefreshToken.token()));
            refreshToken.revoke();
            refreshTokenRepository.save(refreshToken);

            return AccessTokenResponse.builder()
                .token(accessToken.token())
                .expiresAt(accessToken.expiresAt())
                .refreshToken(newRefreshToken.token())
                .refreshTokenExpiresAt(newRefreshToken.expiresAt())
                .build();
        }

        return accessToken;
    }

    @Transactional
    public void revokeRefreshToken(String token, String reason) {
        refreshTokenRepository.findByToken(token)
            .ifPresent(refreshToken -> {
                refreshToken.revoke();
                refreshTokenRepository.save(refreshToken);

                // Publish token revoked event
                applicationEventPublisher.publishEvent(
                    new RefreshTokenRevokedEvent(refreshToken, reason));
            });
    }

    @Transactional
    public void revokeAllUserTokens(User user, String reason) {
        List<RefreshToken> activeTokens = refreshTokenRepository
            .findByUserAndRevokedFalse(user);

        activeTokens.forEach(token -> {
            token.revoke();
            // Store revocation reason in audit log
        });

        refreshTokenRepository.saveAll(activeTokens);

        // Publish batch revocation event
        applicationEventPublisher.publishEvent(
            new AllRefreshTokensRevokedEvent(user, activeTokens.size(), reason));
    }

    private RefreshToken validateRefreshToken(String tokenValue, String ipAddress) {
        RefreshToken refreshToken = refreshTokenRepository.findByToken(tokenValue)
            .orElseThrow(() -> new InvalidTokenException("Refresh token not found"));

        // Validate token status
        if (!refreshToken.isValid()) {
            if (refreshToken.isRevoked()) {
                throw new TokenRevokedException("Token has been revoked");
            }
            if (refreshToken.isExpired()) {
                refreshTokenRepository.delete(refreshToken);
                throw new ExpiredTokenException("Refresh token expired");
            }
            throw new InvalidTokenException("Token is invalid");
        }

        // Validate token usage
        if (refreshToken.getMaxUsage() != null &&
            refreshToken.getUsageCount() >= refreshToken.getMaxUsage()) {
            refreshToken.revoke();
            refreshTokenRepository.save(refreshToken);
            throw new TokenUsageExceededException("Token usage limit exceeded");
        }

        // Validate IP address (optional security measure)
        if (!isValidIpAddress(refreshToken.getIpAddress(), ipAddress)) {
            log.warn("Suspicious refresh token usage - IP mismatch. Expected: {}, Actual: {}",
                refreshToken.getIpAddress(), ipAddress);

            // Optional: revoke token on IP mismatch
            // refreshToken.revoke();
            // refreshTokenRepository.save(refreshToken);
            // throw new SecurityException("IP address mismatch");
        }

        return refreshToken;
    }

    private void enforceMaxActiveTokens(User user) {
        long activeTokens = refreshTokenRepository.countActiveTokensByUser(
            user, Instant.now());

        if (activeTokens >= maxActiveTokensPerUser) {
            // Revoke oldest token
            List<RefreshToken> oldestTokens = refreshTokenRepository
                .findOldestActiveTokensByUser(user);

            if (!oldestTokens.isEmpty()) {
                RefreshToken oldestToken = oldestTokens.get(0);
                oldestToken.revoke();
                refreshTokenRepository.save(oldestToken);

                log.info("Revoked oldest refresh token for user {} due to limit",
                    user.getId());
            }
        }
    }

    private boolean shouldRotateRefreshToken(RefreshToken refreshToken) {
        if (!tokenRotationEnabled) {
            return false;
        }

        // Rotate if token is older than threshold
        boolean ageThreshold = refreshToken.getCreatedAt()
            .isBefore(Instant.now().minus(tokenRotationThreshold));

        // Rotate if token has been used too many times
        boolean usageThreshold = refreshToken.getUsageCount() > 50;

        return ageThreshold || usageThreshold;
    }

    // Cleanup expired and revoked tokens
    @Scheduled(fixedRate = 86400000) // Daily
    public void cleanupTokens() {
        Instant cutoff = Instant.now().minus(30, ChronoUnit.DAYS);

        // Delete expired tokens older than 30 days
        List<RefreshToken> expiredTokens = refreshTokenRepository
            .findByExpiresAtBefore(cutoff);
        refreshTokenRepository.deleteAll(expiredTokens);

        // Delete revoked tokens older than 30 days
        List<RefreshToken> revokedTokens = refreshTokenRepository
            .findByRevokedTrueAndRevokedAtBefore(cutoff);
        refreshTokenRepository.deleteAll(revokedTokens);

        log.info("Cleaned up {} expired and {} revoked tokens",
            expiredTokens.size(), revokedTokens.size());
    }
}
```

## Token Blacklisting

### BlacklistedToken Entity
```java
@Entity
@Table(name = "blacklisted_tokens")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BlacklistedToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "token_id", unique = true, nullable = false)
    private String tokenId; // JWT ID (jti claim)

    @Column(columnDefinition = "TEXT")
    private String token; // Full token (for debugging)

    @Column(name = "blacklisted_at", nullable = false)
    private Instant blacklistedAt;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    @Column(name = "blacklisted_by")
    private String blacklistedBy; // User ID or system

    private String reason; // Reason for blacklisting

    @Enumerated(EnumType.STRING)
    private BlacklistReason blacklistReason;

    public enum BlacklistReason {
        LOGOUT,
        PASSWORD_CHANGE,
        ROLE_CHANGE,
        ACCOUNT_SUSPENSION,
        SUSPICIOUS_ACTIVITY,
        TOKEN_THEFT,
        ADMIN_REVOCATION,
        MASS_REVOCATION
    }

    public boolean isExpired() {
        return Instant.now().isAfter(expiresAt);
    }
}
```

### Token Blacklisting Service
```java
@Service
@Transactional
public class TokenBlacklistingService {

    private final BlacklistedTokenRepository blacklistedTokenRepository;
    private final JwtDecoder jwtDecoder;

    public void blacklistToken(String token, String reason, BlacklistReason blacklistReason) {
        try {
            Jwt jwt = jwtDecoder.decode(token);
            String tokenId = jwt.getClaimAsString("jti");
            Instant expiresAt = jwt.getExpiresAt();

            if (tokenId == null || expiresAt == null) {
                throw new InvalidTokenException("Token missing required claims");
            }

            BlacklistedToken blacklistedToken = BlacklistedToken.builder()
                .tokenId(tokenId)
                .token(token.substring(0, Math.min(token.length(), 100))) // Store first 100 chars
                .blacklistedAt(Instant.now())
                .expiresAt(expiresAt)
                .blacklistedBy(getCurrentUser())
                .reason(reason)
                .blacklistReason(blacklistReason)
                .build();

            blacklistedTokenRepository.save(blacklistedToken);

            log.info("Token {} blacklisted for reason: {}", tokenId, reason);

        } catch (JwtException e) {
            log.error("Failed to blacklist token", e);
            throw new InvalidTokenException("Invalid token", e);
        }
    }

    @Transactional(readOnly = true)
    public boolean isTokenBlacklisted(String token) {
        try {
            Jwt jwt = jwtDecoder.decode(token);
            String tokenId = jwt.getClaimAsString("jti");

            if (tokenId == null) {
                return false;
            }

            return blacklistedTokenRepository.existsByTokenId(tokenId);

        } catch (JwtException e) {
            // If token is invalid, it's effectively blacklisted
            return true;
        }
    }

    @Transactional
    public void blacklistAllUserTokens(User user, String reason, BlacklistReason blacklistReason) {
        // This would require tracking all active tokens in the system
        // For now, we'll implement a user-based blacklist
        UserBlacklist blacklist = UserBlacklist.builder()
            .user(user)
            .blacklistedAt(Instant.now())
            .reason(reason)
            .blacklistReason(blacklistReason)
            .build();

        userBlacklistRepository.save(blacklist);
    }

    @Scheduled(fixedRate = 3600000) // Every hour
    public void cleanupExpiredBlacklistedTokens() {
        List<BlacklistedToken> expiredTokens = blacklistedTokenRepository
            .findByExpiresAtBefore(Instant.now());

        blacklistedTokenRepository.deleteAll(expiredTokens);

        if (!expiredTokens.isEmpty()) {
            log.info("Cleaned up {} expired blacklisted tokens", expiredTokens.size());
        }
    }
}
```

## Session Management

### Session Tracking
```java
@Entity
@Table(name = "user_sessions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "session_id", unique = true, nullable = false)
    private String sessionId;

    @Column(name = "device_id")
    private String deviceId;

    @Column(name = "device_info")
    private String deviceInfo;

    @Column(name = "ip_address")
    private String ipAddress;

    @Column(name = "user_agent")
    private String userAgent;

    @Column(name = "location")
    private String location; // Geolocation based on IP

    @Column(name = "login_at", nullable = false)
    private Instant loginAt;

    @Column(name = "last_activity_at")
    private Instant lastActivityAt;

    @Column(name = "logout_at")
    private Instant logoutAt;

    @Column(name = "session_timeout_at")
    private Instant sessionTimeoutAt;

    @Column(nullable = false)
    private boolean active = true;

    @Column(nullable = false)
    private boolean persistent = false;

    // Session metadata
    @Column(name = "login_method")
    @Enumerated(EnumType.STRING)
    private LoginMethod loginMethod;

    @Column(name = "mfa_verified")
    private boolean mfaVerified = false;

    @Column(name = "risk_score")
    private Integer riskScore;

    public boolean isValid() {
        return active && !isExpired();
    }

    public boolean isExpired() {
        return sessionTimeoutAt != null && Instant.now().isAfter(sessionTimeoutAt);
    }

    public void updateActivity() {
        this.lastActivityAt = Instant.now();
        // Update session timeout based on inactivity policy
        this.sessionTimeoutAt = Instant.now().plus(30, ChronoUnit.MINUTES);
    }

    public void terminate() {
        this.active = false;
        this.logoutAt = Instant.now();
    }
}

@Service
public class SessionManagementService {

    @Value("${security.session.max-concurrent:5}")
    private int maxConcurrentSessions;

    @Value("${security.session.inactivity-timeout:PT30M}")
    private Duration inactivityTimeout;

    public UserSession createSession(User user, HttpServletRequest request, LoginMethod loginMethod) {
        String sessionId = UUID.randomUUID().toString();
        String ipAddress = extractIpAddress(request);
        String deviceInfo = extractDeviceInfo(request);
        String deviceId = generateDeviceId(request);

        // Enforce concurrent session limit
        enforceConcurrentSessionLimit(user);

        UserSession session = UserSession.builder()
            .user(user)
            .sessionId(sessionId)
            .deviceId(deviceId)
            .deviceInfo(deviceInfo)
            .ipAddress(ipAddress)
            .userAgent(request.getHeader("User-Agent"))
            .location(lookupLocation(ipAddress))
            .loginAt(Instant.now())
            .lastActivityAt(Instant.now())
            .sessionTimeoutAt(Instant.now().plus(inactivityTimeout))
            .active(true)
            .loginMethod(loginMethod)
            .riskScore(calculateRiskScore(request))
            .build();

        session = sessionRepository.save(session);

        // Publish session created event
        applicationEventPublisher.publishEvent(new UserSessionCreatedEvent(session));

        return session;
    }

    @Transactional
    public void terminateSession(String sessionId, String reason) {
        sessionRepository.findBySessionId(sessionId)
            .ifPresent(session -> {
                session.terminate();
                sessionRepository.save(session);

                // Revoke associated refresh tokens
                refreshTokenService.revokeTokensBySessionId(sessionId);

                // Publish session terminated event
                applicationEventPublisher.publishEvent(
                    new UserSessionTerminatedEvent(session, reason));
            });
    }

    @Transactional
    public void terminateAllUserSessions(User user, String reason) {
        List<UserSession> activeSessions = sessionRepository
            .findByUserAndActiveTrue(user);

        activeSessions.forEach(session -> {
            session.terminate();
            // Revoke associated tokens
            refreshTokenService.revokeTokensBySessionId(session.getSessionId());
        });

        sessionRepository.saveAll(activeSessions);

        // Publish batch session termination event
        applicationEventPublisher.publishEvent(
            new AllUserSessionsTerminatedEvent(user, activeSessions.size(), reason));
    }

    private void enforceConcurrentSessionLimit(User user) {
        long activeSessions = sessionRepository.countByUserAndActiveTrue(user);

        if (activeSessions >= maxConcurrentSessions) {
            // Terminate oldest session
            List<UserSession> oldestSessions = sessionRepository
                .findByUserAndActiveTrueOrderByLoginAtAsc(user);

            if (!oldestSessions.isEmpty()) {
                UserSession oldestSession = oldestSessions.get(0);
                terminateSession(oldestSession.getSessionId(),
                    "Concurrent session limit exceeded");
            }
        }
    }

    // Cleanup inactive sessions
    @Scheduled(fixedRate = 300000) // Every 5 minutes
    public void cleanupInactiveSessions() {
        List<UserSession> inactiveSessions = sessionRepository
            .findByActiveTrueAndSessionTimeoutAtBefore(Instant.now());

        inactiveSessions.forEach(session -> {
            session.terminate();
            // Revoke associated refresh tokens
            refreshTokenService.revokeTokensBySessionId(session.getSessionId());
        });

        sessionRepository.saveAll(inactiveSessions);

        if (!inactiveSessions.isEmpty()) {
            log.info("Cleaned up {} inactive sessions", inactiveSessions.size());
        }
    }
}
```

## Token Security Headers

### Security Headers Configuration
```java
@Configuration
public class SecurityHeadersConfig {

    @Bean
    public SecurityFilterChain securityHeaders(HttpSecurity http) throws Exception {
        return http
            .headers(headers -> headers
                .contentTypeOptions(cto -> cto.and()
                    .xssProtection(xss -> xss.headerValue(XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
                    .httpStrictTransportSecurity(hsts -> hsts
                        .maxAgeInSeconds(31536000)
                        .includeSubdomains(true)
                        .preload(true))
                    .frameOptions(frame -> frame.deny())
                    .contentSecurityPolicy(csp -> csp
                        .policyDirectives("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"))
                    .referrerPolicy(referrer -> referrer
                        .policy(ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))))
                .and())
            .build();
    }
}
```

### Rate Limiting for Token Endpoints
```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final RateLimiter authRateLimiter;

    @PostMapping("/login")
    @RateLimited(requests = 5, window = "PT1M")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        // Login implementation
    }

    @PostMapping("/refresh")
    @RateLimited(requests = 10, window = "PT1M")
    public ResponseEntity<RefreshTokenResponse> refresh(
            @RequestBody RefreshTokenRequest request) {
        // Refresh token implementation
    }
}

@Aspect
@Component
public class RateLimitingAspect {

    private final Map<String, Bucket> bucketCache = new ConcurrentHashMap<>();

    @Around("@annotation(rateLimited)")
    public Object around(ProceedingJoinPoint joinPoint, RateLimited rateLimited) throws Throwable {
        String key = generateKey(joinPoint, rateLimited);
        Bucket bucket = bucketCache.computeIfAbsent(key, k -> createBucket(rateLimited));

        if (bucket.tryConsume(1)) {
            return joinPoint.proceed();
        } else {
            throw new RateLimitExceededException("Rate limit exceeded");
        }
    }

    private String generateKey(ProceedingJoinPoint joinPoint, RateLimited rateLimited) {
        HttpServletRequest request = getCurrentRequest();
        String clientIp = getClientIpAddress(request);

        return String.format("%s:%s:%s",
            joinPoint.getSignature().toShortString(),
            clientIp,
            rateLimited.identifier());
    }
}
```