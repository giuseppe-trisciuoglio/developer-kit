---
name: spring-boot-cache
description: Caching strategies with Spring Cache abstraction using @Cacheable, @CachePut, @CacheEvict and custom cache managers. Use when implementing application-level caching for improved performance.
allowed-tools: Read, Write, Bash
category: backend
tags: [spring-boot, caching, performance, cacheable, cache-managers]
version: 1.0.1
---

# Spring Boot Cache Abstraction

## Overview

Spring provides a powerful **Caching Abstraction** that enables method-level caching with minimal code changes. By using annotations like `@Cacheable`, `@CacheEvict`, and `@CachePut`, you can dramatically improve application performance by reducing expensive method calls and database queries.

The abstraction works with multiple cache implementations (ConcurrentMapCache, Ehcache, Caffeine, Redis) without requiring code changes—only configuration adjustments.

## Dependencies

### Spring Boot Starter (Recommended)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
    <version>3.5.6</version>
</dependency>
```

### Core Spring (Non-Boot)

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-context</artifactId>
    <version>6.2.11</version>
</dependency>
```

### Gradle

```gradle
implementation 'org.springframework.boot:spring-boot-starter-cache:3.5.6'
```

## Enable Caching

Create a configuration class with `@EnableCaching`:

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("users", "addresses", "transactions");
    }
}
```

**Spring Boot Auto-Configuration**: In Spring Boot, merely adding the starter and `@EnableCaching` registers `ConcurrentMapCacheManager` automatically. No bean declaration needed.

### Custom Cache Manager Setup

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();
        cacheManager.setCaches(Arrays.asList(
            new ConcurrentMapCache("users"),
            new ConcurrentMapCache("addresses"),
            new ConcurrentMapCache("transactions")
        ));
        return cacheManager;
    }
}
```

## Caching Annotations

### @Cacheable

Cache method results before execution. If the value exists in cache, the method is **skipped**:

```java
@Service
public class UserService {
    
    @Cacheable(value = "users")
    public User getUser(Long id) {
        // Database call skipped if cached
        return userRepository.findById(id).orElse(null);
    }
}
```

**Multiple caches**:

```java
@Cacheable(value = {"users", "directory"})
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

**Custom cache key**:

```java
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

### @CacheEvict

Remove values from cache to free memory and ensure fresh data is loaded:

```java
@Service
public class UserService {
    
    // Evict single entry
    @CacheEvict(value = "users", key = "#id")
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    // Evict all entries in cache
    @CacheEvict(value = "users", allEntries = true)
    public void clearAllUsers() {
        // Prepare for fresh data
    }
}
```

### @CachePut

Always execute the method and update the cache with the result (differs from `@Cacheable`):

```java
@CachePut(value = "users", key = "#user.id")
public User updateUser(User user) {
    return userRepository.save(user);
}
```

**Key Difference**:
- `@Cacheable`: Skips method execution if cached
- `@CachePut`: Always executes method, then caches result

### @Caching

Combine multiple cache operations on a single method:

```java
@Caching(
    evict = {
        @CacheEvict("users"),
        @CacheEvict(value = "directory", key = "#user.name")
    },
    put = @CachePut(value = "users", key = "#user.id")
)
public User syncUser(User user) {
    return userRepository.save(user);
}
```

### @CacheConfig

Declare cache name at class level to avoid repetition:

```java
@Service
@CacheConfig(cacheNames = {"users", "addresses"})
public class UserService {
    
    @Cacheable
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    @CacheEvict(allEntries = true)
    public void refreshAllUsers() {}
}
```

## Conditional Caching

### Condition Parameter

Cache only based on input conditions using SpEL:

```java
@Cacheable(
    value = "users",
    condition = "#id > 100"  // Cache only ids > 100
)
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

Multiple conditions:

```java
@Cacheable(
    value = "users",
    condition = "#id > 0 && #includeDetails == true"
)
public User getUser(Long id, boolean includeDetails) {
    return userRepository.findById(id).orElse(null);
}
```

### Unless Parameter

Cache based on output using `#result`:

```java
@CachePut(
    value = "addresses",
    unless = "#result.length() < 64"  // Don't cache short addresses
)
public String getAddress(Customer customer) {
    return customer.getAddress();
}
```

Null checking:

```java
@Cacheable(
    value = "users",
    unless = "#result == null"  // Don't cache null results
)
public User getUser(Long id) {
    return userRepository.findById(id).orElse(null);
}
```

## Cache Management with CacheManager

Programmatically evict or clear caches:

```java
@Service
public class CacheManagementService {
    
    @Autowired
    private CacheManager cacheManager;
    
    // Evict single entry
    public void evictUser(Long userId) {
        cacheManager.getCache("users").evict(userId);
    }
    
    // Clear entire cache
    public void clearUsers() {
        cacheManager.getCache("users").clear();
    }
    
    // Clear all caches
    public void clearAllCaches() {
        cacheManager.getCacheNames().stream()
            .forEach(cacheName -> 
                cacheManager.getCache(cacheName).clear()
            );
    }
}
```

### Expose Cache Management Endpoint

```java
@RestController
@RequestMapping("/api/cache")
public class CacheController {
    
    @Autowired
    private CacheManagementService cacheService;
    
    @DeleteMapping("/clear-all")
    public ResponseEntity<String> clearAllCaches() {
        cacheService.clearAllCaches();
        return ResponseEntity.ok("All caches cleared");
    }
    
    @DeleteMapping("/{cacheName}")
    public ResponseEntity<String> clearCache(@PathVariable String cacheName) {
        cacheManager.getCache(cacheName).clear();
        return ResponseEntity.ok("Cache " + cacheName + " cleared");
    }
}
```

## Scheduled Cache Eviction

Automatically clear caches at fixed intervals:

```java
@Component
public class CacheEvictionScheduler {
    
    @Autowired
    private CacheManager cacheManager;
    
    @Scheduled(fixedRate = 600000)  // Every 10 minutes
    public void evictAllCaches() {
        cacheManager.getCacheNames().stream()
            .forEach(cacheName -> 
                cacheManager.getCache(cacheName).clear()
            );
    }
}
```

## Ehcache Configuration

### Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
    <version>3.5.6</version>
</dependency>
<dependency>
    <groupId>javax.cache</groupId>
    <artifactId>cache-api</artifactId>
    <version>1.1.1</version>
</dependency>
<dependency>
    <groupId>org.ehcache</groupId>
    <artifactId>ehcache</artifactId>
    <version>3.10.8</version>
    <classifier>jakarta</classifier>
</dependency>
```

### Application Configuration

```properties
spring.cache.jcache.config=classpath:ehcache.xml
```

### ehcache.xml

```xml
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ehcache.org/v3"
    xmlns:jsr107="http://www.ehcache.org/v3/jsr107"
    xsi:schemaLocation="
            http://www.ehcache.org/v3 http://www.ehcache.org/schema/ehcache-core-3.0.xsd
            http://www.ehcache.org/v3/jsr107 http://www.ehcache.org/schema/ehcache-107-ext-3.0.xsd">

    <cache alias="users">
        <key-type>java.lang.Long</key-type>
        <value-type>com.example.User</value-type>
        <expiry>
            <ttl unit="minutes">30</ttl>
        </expiry>
        <resources>
            <heap unit="entries">1000</heap>
            <offheap unit="MB">50</offheap>
        </resources>
    </cache>

    <cache alias="addresses">
        <key-type>java.lang.Long</key-type>
        <value-type>java.lang.String</value-type>
        <expiry>
            <ttl unit="hours">1</ttl>
        </expiry>
        <resources>
            <heap unit="entries">500</heap>
        </resources>
    </cache>

</config>
```

### Cache Event Listener

```java
public class CacheEventLogger implements CacheEventListener<Object, Object> {
    
    private static final Logger logger = LoggerFactory.getLogger(CacheEventLogger.class);
    
    @Override
    public void onEvent(CacheEvent<? extends Object, ? extends Object> cacheEvent) {
        logger.info("Cache event {} for key {}. Old: {}, New: {}",
            cacheEvent.getType(),
            cacheEvent.getKey(),
            cacheEvent.getOldValue(),
            cacheEvent.getNewValue()
        );
    }
}
```

### Ehcache Configuration with Event Listeners

```xml
<cache alias="users">
    <key-type>java.lang.Long</key-type>
    <value-type>com.example.User</value-type>
    <expiry>
        <ttl unit="minutes">30</ttl>
    </expiry>
    
    <listeners>
        <listener>
            <class>com.example.config.CacheEventLogger</class>
            <event-firing-mode>ASYNCHRONOUS</event-firing-mode>
            <events-to-fire-on>CREATED</events-to-fire-on>
            <events-to-fire-on>EXPIRED</events-to-fire-on>
            <events-to-fire-on>EVICTED</events-to-fire-on>
        </listener>
    </listeners>
    
    <resources>
        <heap unit="entries">1000</heap>
        <offheap unit="MB">50</offheap>
    </resources>
</cache>
```

## Real-World Example

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private CacheManager cacheManager;
    
    // Cacheable: Skip execution if in cache
    @Cacheable(
        value = "orders",
        key = "#orderId",
        unless = "#result == null"
    )
    public Order getOrder(Long orderId) {
        logger.info("Fetching order {} from database", orderId);
        return orderRepository.findById(orderId).orElse(null);
    }
    
    // CachePut: Always execute, then cache
    @CachePut(value = "orders", key = "#order.id")
    public Order updateOrder(Order order) {
        logger.info("Updating order {}", order.getId());
        return orderRepository.save(order);
    }
    
    // CacheEvict: Remove from cache
    @CacheEvict(value = "orders", key = "#orderId")
    public void deleteOrder(Long orderId) {
        logger.info("Deleting order {}", orderId);
        orderRepository.deleteById(orderId);
    }
    
    // Caching: Multiple operations
    @Caching(
        put = @CachePut(value = "orders", key = "#result.id"),
        evict = @CacheEvict(value = "ordersList", allEntries = true)
    )
    public Order createOrder(Order order) {
        logger.info("Creating order");
        return orderRepository.save(order);
    }
}
```

## Testing Cached Methods

```java
@SpringBootTest
public class OrderServiceTest {
    
    @MockBean
    private OrderRepository orderRepository;
    
    @Autowired
    private OrderService orderService;
    
    @Test
    void testCachingBehavior() {
        Order order = new Order(1L, "Test Order");
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));
        
        // First call - hits database
        Order result1 = orderService.getOrder(1L);
        verify(orderRepository, times(1)).findById(1L);
        
        // Second call - hits cache
        Order result2 = orderService.getOrder(1L);
        verify(orderRepository, times(1)).findById(1L);  // Still 1x call
        
        assertEquals(result1, result2);
    }
}
```

## Best Practices

### ✅ DO

- **Use `@Cacheable` for read-heavy operations**: Database queries, external API calls
- **Set cache keys explicitly**: Avoid key generation issues with `key = "#id"`
- **Use conditions for selective caching**: Only cache when beneficial (`#id > 0`)
- **Monitor cache performance**: Log cache hits/misses and eviction events
- **Set appropriate TTLs**: Balance freshness vs. memory usage
- **Test cache behavior**: Verify caching works as expected in unit tests
- **Use `@CachePut` for updates**: Ensures cache stays in sync with database

### ❌ DON'T

- **Cache everything**: Only cache expensive operations with stable data
- **Cache mutable objects**: Use immutable records/DTOs for cache values
- **Ignore null values**: Explicitly handle with `unless = "#result == null"`
- **Use weak cache keys**: Avoid using `toString()` for cache keys
- **Forget to clear caches**: Manage cache lifecycle explicitly
- **Cache sensitive data**: Never cache passwords, tokens, or PII
- **Create circular cache dependencies**: Avoid cache-to-cache lookups

## Performance Considerations

- **Unit test execution time**: Keep cacheable methods < 50ms
- **Memory usage**: Monitor cache size with Ehcache heap/off-heap limits
- **Concurrent access**: Spring caching is thread-safe with proper CacheManager
- **Cache stampede**: Use `condition` parameter to prevent thundering herd

## Related Skills

- **Spring Boot REST API Standards** - Integrate caching with REST endpoints
- **Spring Boot Test Patterns** - Test caching with Testcontainers
- **JUnit Test Patterns** - Unit test cached service methods

## References

- [Spring Cache Tutorial](https://www.baeldung.com/spring-cache-tutorial)
- [Cache Eviction in Spring Boot](https://www.baeldung.com/spring-boot-evict-cache)
- [Spring Boot Ehcache Example](https://www.baeldung.com/spring-boot-ehcache)
- [Official Spring Cache Documentation](https://docs.spring.io/spring-framework/reference/integration/cache.html)
