# Performance Optimization for JWT Security

## Caching Strategies

### Token Validation Cache
```java
@Configuration
@EnableCaching
public class JwtCacheConfig {

    @Bean
    public CacheManager jwtCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(Duration.ofMinutes(15))
            .recordStats());

        // Configure separate caches
        cacheManager.setCacheNames(Arrays.asList(
            "tokenValidation",
            "userPermissions",
            "refreshTokens",
            "blacklistedTokens"
        ));

        return cacheManager;
    }

    @Bean
    @Primary
    public JwtDecoder cachedJwtDecoder(JwtDecoder delegate) {
        return new CachingJwtDecoder(delegate);
    }
}

@Component
@Slf4j
public class CachingJwtDecoder implements JwtDecoder {

    private final JwtDecoder delegate;
    private final Cache<String, Jwt> cache;

    public CachingJwtDecoder(JwtDecoder delegate) {
        this.delegate = delegate;
        this.cache = CacheBuilder.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(Duration.ofMinutes(5))
            .build();
    }

    @Override
    public Jwt decode(String token) throws JwtException {
        try {
            // Generate cache key from token header and payload (exclude signature)
            String cacheKey = extractCacheKey(token);

            return cache.get(cacheKey, () -> {
                log.debug("Cache miss for token, decoding...");
                return delegate.decode(token);
            });

        } catch (ExecutionException e) {
            throw new JwtException("Failed to decode token", e.getCause());
        }
    }

    private String extractCacheKey(String token) {
        String[] parts = token.split("\\.");
        if (parts.length >= 2) {
            return parts[0] + "." + parts[1]; // header.payload
        }
        return token;
    }

    @Scheduled(fixedRate = 300000) // Every 5 minutes
    public void logCacheStats() {
        CacheStats stats = cache.stats();
        log.info("JWT Decoder Cache - Hit rate: {:.2f}%, Miss rate: {:.2f}%, Size: {}",
            stats.hitRate() * 100,
            stats.missRate() * 100,
            cache.estimatedSize());
    }
}

@Service
public class CachedTokenValidationService {

    @Cacheable(value = "tokenValidation", key = "#token")
    public TokenValidationResult validateToken(String token) {
        // Actual token validation logic
        return performValidation(token);
    }

    @CacheEvict(value = "tokenValidation", key = "#token")
    public void evictToken(String token) {
        log.debug("Evicting token from cache: {}", token.substring(0, 20));
    }

    @CacheEvict(value = "tokenValidation", allEntries = true)
    public void clearCache() {
        log.info("Clearing token validation cache");
    }
}
```

### Permission Caching
```java
@Service
public class CachedPermissionService {

    @Cacheable(value = "userPermissions", key = "#user.id")
    public Set<String> getUserPermissions(User user) {
        return permissionRepository.findByUser(user).stream()
            .map(Permission::getName)
            .collect(Collectors.toSet());
    }

    @CacheEvict(value = "userPermissions", key = "#user.id")
    public void refreshUserPermissions(User user) {
        // Cache eviction will trigger refresh on next access
    }

    @CacheEvict(value = "userPermissions", allEntries = true)
    @Scheduled(fixedRate = 3600000) // Hourly
    public void refreshAllPermissions() {
        log.info("Refreshing all user permissions cache");
    }
}
```

## Database Optimization

### Token Storage Optimization
```java
@Entity
@Table(name = "refresh_tokens", indexes = {
    @Index(name = "idx_refresh_token_user_id", columnList = "user_id"),
    @Index(name = "idx_refresh_token_token_id", columnList = "token_id"),
    @Index(name = "idx_refresh_token_expires_at", columnList = "expires_at"),
    @Index(name = "idx_refresh_token_revoked", columnList = "revoked, expires_at")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RefreshToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Use varbinary for better performance with large tokens
    @Column(name = "token", columnDefinition = "BINARY(2048)")
    private byte[] token;

    @Column(name = "token_id", unique = true, nullable = false, length = 64)
    private String tokenId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    // Store timestamps as long for better performance
    @Column(name = "created_at", nullable = false)
    private Long createdAt;

    @Column(name = "expires_at", nullable = false)
    private Long expiresAt;

    @Column(name = "last_used_at")
    private Long lastUsedAt;

    @Column(name = "revoked_at")
    private Long revokedAt;

    @Column(nullable = false)
    private boolean revoked = false;

    // Add hash for quick lookup
    @Column(name = "token_hash", unique = true, nullable = false, length = 64)
    private String tokenHash;

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = Instant.now().toEpochMilli();
        }
        if (token != null && tokenHash == null) {
            tokenHash = DigestUtils.sha256Hex(token);
        }
    }
}

@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {

    @Query("SELECT rt FROM RefreshToken rt WHERE rt.tokenHash = :hash")
    Optional<RefreshToken> findByTokenHash(@Param("hash") String hash);

    @Query("SELECT COUNT(rt) FROM RefreshToken rt WHERE rt.user = :user AND rt.revoked = false AND rt.expiresAt > :now")
    long countActiveTokensByUser(@Param("user") User user, @Param("now") Long now);

    @Modifying
    @Query(value = "DELETE FROM refresh_tokens WHERE expires_at < :cutoff LIMIT 1000", nativeQuery = true)
    int deleteBatchExpired(@Param("cutoff") Long cutoff);

    @Query(value = "SELECT * FROM refresh_tokens WHERE user_id = :userId AND revoked = false ORDER BY created_at ASC LIMIT :limit", nativeQuery = true)
    List<RefreshToken> findOldestActiveTokens(@Param("userId") Long userId, @Param("limit") int limit);
}
```

### Batch Operations
```java
@Service
public class OptimizedTokenService {

    @Transactional
    public void cleanupExpiredTokensBatch() {
        int batchSize = 1000;
        int deletedCount = 0;

        do {
            deletedCount = refreshTokenRepository.deleteBatchExpired(
                Instant.now().minus(7, ChronoUnit.DAYS).toEpochMilli());
            log.info("Deleted {} expired tokens in batch", deletedCount);
        } while (deletedCount > 0);
    }

    @Transactional
    public void revokeAllUserTokensBatch(User user) {
        // Update in batches to avoid memory issues
        int batchSize = 100;
        int offset = 0;
        List<RefreshToken> tokens;

        do {
            tokens = refreshTokenRepository.findActiveTokensByUserWithLimit(
                user, batchSize, offset);

            if (!tokens.isEmpty()) {
                tokens.forEach(token -> {
                    token.setRevoked(true);
                    token.setRevokedAt(Instant.now().toEpochMilli());
                });
                refreshTokenRepository.saveAll(tokens);
                refreshTokenRepository.flush(); // Force batch execution
            }

            offset += batchSize;
        } while (tokens.size() == batchSize);
    }
}
```

## Connection Pooling and Async Processing

### Async Token Processing
```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("tokenProcessingExecutor")
    public Executor tokenProcessingExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("TokenProcess-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setKeepAliveSeconds(60);
        executor.initialize();
        return executor;
    }

    @Bean("authEventExecutor")
    public Executor authEventExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(2);
        executor.setMaxPoolSize(5);
        executor.setQueueCapacity(50);
        executor.setThreadNamePrefix("AuthEvent-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.AbortPolicy());
        executor.initialize();
        return executor;
    }
}

@Service
public class AsyncTokenService {

    @Async("tokenProcessingExecutor")
    public CompletableFuture<Void> processTokenInBackground(String token, String action) {
        try {
            // Process token without blocking main thread
            switch (action) {
                case "validate":
                    tokenValidationService.validateToken(token);
                    break;
                case "revoke":
                    tokenService.revokeToken(token);
                    break;
                case "refresh":
                    refreshService.processRefreshToken(token);
                    break;
            }
        } catch (Exception e) {
            log.error("Error processing token in background", e);
        }
        return CompletableFuture.completedFuture(null);
    }

    @EventListener
    @Async("authEventExecutor")
    public void handleAuthenticationEvent(AuthenticationEvent event) {
        // Process authentication events asynchronously
        auditService.recordAuthenticationEvent(event);
        metricsService.incrementAuthenticationCounter(event);
    }
}
```

## Monitoring and Metrics

### JWT Performance Metrics
```java
@Component
public class JwtMetricsCollector {

    private final MeterRegistry meterRegistry;
    private final Counter tokenGenerationCounter;
    private final Counter tokenValidationCounter;
    private final Timer tokenGenerationTimer;
    private final Timer tokenValidationTimer;

    public JwtMetricsCollector(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.tokenGenerationCounter = Counter.builder("jwt.token.generated")
            .description("Number of JWT tokens generated")
            .register(meterRegistry);

        this.tokenValidationCounter = Counter.builder("jwt.token.validated")
            .description("Number of JWT tokens validated")
            .tag("result", "success")
            .register(meterRegistry);

        this.tokenGenerationTimer = Timer.builder("jwt.token.generation.time")
            .description("Time taken to generate JWT token")
            .register(meterRegistry);

        this.tokenValidationTimer = Timer.builder("jwt.token.validation.time")
            .description("Time taken to validate JWT token")
            .register(meterRegistry);
    }

    public void recordTokenGenerated() {
        tokenGenerationCounter.increment();
    }

    public void recordTokenValidationSuccess() {
        tokenValidationCounter.increment();
    }

    public Timer.Sample startTokenGenerationTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordTokenGenerationTime(Timer.Sample sample) {
        sample.stop(tokenGenerationTimer);
    }

    public Timer.Sample startTokenValidationTimer() {
        return Timer.start(meterRegistry);
    }

    public void recordTokenValidationTime(Timer.Sample sample) {
        sample.stop(tokenValidationTimer);
    }
}

@Service
public class MonitoredJwtTokenService {

    private final JwtTokenService delegate;
    private final JwtMetricsCollector metrics;

    public AccessTokenResponse generateAccessToken(User user) {
        Timer.Sample sample = metrics.startTokenGenerationTimer();
        try {
            AccessTokenResponse response = delegate.generateAccessToken(user);
            metrics.recordTokenGenerated();
            return response;
        } finally {
            metrics.recordTokenGenerationTime(sample);
        }
    }

    public boolean isTokenValid(String token) {
        Timer.Sample sample = metrics.startTokenValidationTimer();
        try {
            boolean isValid = delegate.isTokenValid(token);
            if (isValid) {
                metrics.recordTokenValidationSuccess();
            }
            return isValid;
        } finally {
            metrics.recordTokenValidationTime(sample);
        }
    }
}
```

### Performance Health Indicators
```java
@Component
public class JwtPerformanceHealthIndicator implements HealthIndicator {

    private final JwtMetricsCollector metrics;
    private final CacheManager cacheManager;

    @Override
    public Health health() {
        try {
            // Check token generation performance
            double avgGenerationTime = metrics.getAverageTokenGenerationTime();
            double avgValidationTime = metrics.getAverageTokenValidationTime();

            // Check cache performance
            Cache tokenCache = cacheManager.getCache("tokenValidation");
            double cacheHitRate = tokenCache != null ? getCacheHitRate(tokenCache) : 0.0;

            Health.Builder builder = Health.up();

            // Add metrics details
            builder.withDetail("avgTokenGenerationTime", avgGenerationTime + "ms");
            builder.withDetail("avgTokenValidationTime", avgValidationTime + "ms");
            builder.withDetail("cacheHitRate", String.format("%.2f%%", cacheHitRate * 100));

            // Check thresholds
            if (avgGenerationTime > 10) {
                builder.status(Status.WARNING)
                    .withDetail("warning", "Token generation time is high");
            }

            if (avgValidationTime > 5) {
                builder.status(Status.WARNING)
                    .withDetail("warning", "Token validation time is high");
            }

            if (cacheHitRate < 0.8) {
                builder.status(Status.WARNING)
                    .withDetail("warning", "Cache hit rate is low");
            }

            return builder.build();

        } catch (Exception e) {
            return Health.down(e).build();
        }
    }

    private double getCacheHitRate(Cache cache) {
        if (cache.getNativeCache() instanceof com.github.benmanes.caffeine.cache.Cache) {
            com.github.benmanes.caffeine.cache.Cache<?, ?> nativeCache =
                (com.github.benmanes.caffeine.cache.Cache<?, ?>) cache.getNativeCache();
            return nativeCache.stats().hitRate();
        }
        return 0.0;
    }
}
```

## Load Balancing and Scaling

### Stateless JWT Configuration
```java
@Configuration
public class StatelessSecurityConfig {

    @Bean
    public SecurityFilterChain statelessSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
}
```

### Distributed Cache Configuration
```java
@Configuration
@EnableCaching
public class DistributedCacheConfig {

    @Bean
    @ConditionalOnProperty(name = "cache.type", havingValue = "redis")
    public CacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(15))
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .transactionAware()
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "cache.type", havingValue = "hazelcast")
    public CacheManager hazelcastCacheManager(HazelcastInstance hazelcastInstance) {
        return new HazelcastCacheManager(hazelcastInstance);
    }
}
```

## Resource Optimization

### Memory-Efficient Token Handling
```java
@Component
public class MemoryEfficientTokenHandler {

    private final ObjectMapper objectMapper;
    private final CompressionUtils compressionUtils;

    public String compressToken(String token) {
        try {
            byte[] compressed = compressionUtils.compress(token.getBytes(StandardCharsets.UTF_8));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(compressed);
        } catch (Exception e) {
            log.error("Failed to compress token", e);
            return token;
        }
    }

    public String decompressToken(String compressedToken) {
        try {
            byte[] compressed = Base64.getUrlDecoder().decode(compressedToken);
            byte[] decompressed = compressionUtils.decompress(compressed);
            return new String(decompressed, StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.error("Failed to decompress token", e);
            return compressedToken;
        }
    }

    public JwtClaimsSet parseClaimsEfficiently(String token) {
        // Parse only the payload section for claims
        String[] parts = token.split("\\.");
        if (parts.length >= 2) {
            String payload = new String(Base64.getUrlDecoder().decode(parts[1]));
            return parseClaimsFromJson(payload);
        }
        throw new IllegalArgumentException("Invalid token format");
    }

    private JwtClaimsSet parseClaimsFromJson(String json) {
        // Efficient JSON parsing for specific claims only
        try {
            JsonNode node = objectMapper.readTree(json);
            JwtClaimsSet.Builder builder = JwtClaimsSet.builder();

            // Extract only necessary claims
            if (node.has("sub")) {
                builder.subject(node.get("sub").asText());
            }
            if (node.has("exp")) {
                builder.expiresAt(Instant.ofEpochSecond(node.get("exp").asLong()));
            }
            if (node.has("roles")) {
                List<String> roles = new ArrayList<>();
                node.get("roles").forEach(role -> roles.add(role.asText()));
                builder.claim("roles", roles);
            }

            return builder.build();

        } catch (Exception e) {
            throw new RuntimeException("Failed to parse claims", e);
        }
    }
}
```

### Connection Pool Configuration
```yaml
# Application Properties for Performance
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 30000
      max-lifetime: 1800000
      connection-timeout: 30000
      leak-detection-threshold: 60000
      pool-name: "AuthHikariPool"

  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50
          batch_versioned_data: true
        order_inserts: true
        order_updates: true
        generate_statistics: false

  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=10000,expireAfterWrite=5m

  task:
    execution:
      pool:
        core-size: 10
        max-size: 50
        queue-capacity: 100
      thread-name-prefix: auth-exec-

  web:
    resources:
      cache:
        cachecontrol:
          max-age: 3600
          cache-public: true

# JWT Performance Properties
jwt:
  performance:
    cache-size: 10000
    cache-expiration: PT5M
    batch-size: 100
    async-processing: true
    compress-tokens: false

# Monitoring Properties
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5,0.95,0.99
```