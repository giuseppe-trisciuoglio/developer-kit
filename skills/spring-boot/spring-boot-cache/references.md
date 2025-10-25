# Spring Boot Cache Abstraction - References

Complete API reference and external resources for Spring Boot caching.

## Spring Cache Abstraction API Reference

### Core Interfaces

#### CacheManager
Interface for managing cache instances.

```java
public interface CacheManager {
    // Get a cache by name
    Cache getCache(String name);
    
    // Get all available cache names
    Collection<String> getCacheNames();
}
```

**Common Implementations:**
- `ConcurrentMapCacheManager` - In-memory, thread-safe caching
- `SimpleCacheManager` - Simple static cache configuration
- `CaffeineCacheManager` - High-performance caching with Caffeine library
- `EhCacheManager` - Enterprise caching with EhCache
- `RedisCacheManager` - Distributed caching with Redis

#### Cache
Interface representing a single cache.

```java
public interface Cache {
    // Get cache name
    String getName();
    
    // Get native cache implementation
    Object getNativeCache();
    
    // Get value by key
    ValueWrapper get(Object key);
    
    // Put value in cache
    void put(Object key, Object value);
    
    // Remove entry from cache
    void evict(Object key);
    
    // Clear entire cache
    void clear();
}
```

### Cache Annotations

| Annotation | Purpose | Target | Parameters |
|-----------|---------|--------|-----------|
| `@Cacheable` | Cache method result before execution | Methods | `value`, `key`, `condition`, `unless` |
| `@CachePut` | Always execute, then cache result | Methods | `value`, `key`, `condition`, `unless` |
| `@CacheEvict` | Remove entry/entries from cache | Methods | `value`, `key`, `allEntries`, `condition`, `beforeInvocation` |
| `@Caching` | Combine multiple cache operations | Methods | `cacheable`, `put`, `evict` |
| `@CacheConfig` | Class-level cache configuration | Classes | `cacheNames` |
| `@EnableCaching` | Enable caching support | Configuration classes | None |

### Annotation Parameters

#### value / cacheNames
Name(s) of the cache(s) to use.

```java
@Cacheable(value = "products")  // Single cache
@Cacheable(value = {"products", "inventory"})  // Multiple caches
```

#### key
SpEL expression to generate cache key (if not using method parameters as key).

```java
@Cacheable(value = "products", key = "#id")
@Cacheable(value = "products", key = "#p0")  // First parameter
@Cacheable(value = "products", key = "#root.methodName + #id")
@Cacheable(value = "products", key = "T(java.util.Objects).hash(#id, #name)")
```

**SpEL Context Variables:**
- `#root.methodName` - Method name being invoked
- `#root.method` - Method object
- `#root.target` - Target object
- `#root.targetClass` - Target class
- `#root.args[0]` - Method arguments array
- `#a0`, `#p0` - First argument
- `#result` - Method result (only in @CachePut, @CacheEvict)

#### condition
SpEL expression evaluated before cache operation. Operation only executes if true.

```java
@Cacheable(value = "products", condition = "#id > 0")
@Cacheable(value = "products", condition = "#price > 100 && #active == true")
@Cacheable(value = "products", condition = "#size() > 0")  // For collections
```

#### unless
SpEL expression evaluated AFTER method execution. Entry is cached only if false.

```java
@Cacheable(value = "products", unless = "#result == null")
@CachePut(value = "products", unless = "#result.isPrivate()")
```

#### beforeInvocation
For @CacheEvict only. If true, cache is evicted BEFORE method execution (default: false).

```java
@CacheEvict(value = "products", beforeInvocation = true)  // Evict before call
@CacheEvict(value = "products", beforeInvocation = false)  // Evict after call
```

#### allEntries
For @CacheEvict only. If true, entire cache is cleared instead of single entry.

```java
@CacheEvict(value = "products", allEntries = true)  // Clear all entries
```

## Configuration Reference

### Maven Dependencies

```xml
<!-- Spring Cache Starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
    <version>3.5.6</version>
</dependency>

<!-- Caffeine (Optional, for advanced caching) -->
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
    <version>3.1.6</version>
</dependency>

<!-- EhCache (Optional, for distributed caching) -->
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

<!-- Redis (Optional, for distributed caching) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
    <version>3.5.6</version>
</dependency>
```

### Gradle Dependencies

```gradle
dependencies {
    // Spring Cache Starter
    implementation 'org.springframework.boot:spring-boot-starter-cache:3.5.6'

    // Caffeine
    implementation 'com.github.ben-manes.caffeine:caffeine:3.1.6'

    // EhCache
    implementation 'javax.cache:cache-api:1.1.1'
    implementation 'org.ehcache:ehcache:3.10.8'

    // Redis
    implementation 'org.springframework.boot:spring-boot-starter-data-redis:3.5.6'
}
```

### Application Properties (application.properties)

```properties
# General Caching Configuration
spring.cache.type=simple  # Type: simple, redis, caffeine, ehcache, jcache

# Caffeine Configuration
spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=10m
spring.cache.cache-names=products,users,orders

# Redis Configuration
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.password=
spring.cache.redis.time-to-live=600000  # 10 minutes in ms

# EhCache Configuration
spring.cache.jcache.config=classpath:ehcache.xml
```

### Application Properties (application.yml)

```yaml
spring:
  cache:
    type: simple
    cache-names:
      - products
      - users
      - orders
    
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=10m
    
    redis:
      time-to-live: 600000  # 10 minutes in ms
    
    jcache:
      config: classpath:ehcache.xml
```

## Performance Tuning Reference

### Cache Types Comparison

| Type | Use Case | Memory | Thread-Safe | Distributed |
|------|----------|--------|------------|-------------|
| Simple | Local, small data | Low | Yes | No |
| Caffeine | High-performance local | Medium | Yes | No |
| EhCache | Enterprise local | High | Yes | Optional |
| Redis | Distributed, large | External | Yes | Yes |

### Performance Tips

**1. Key Generation Strategy:**
```java
// Fast (uses method parameters directly)
@Cacheable(value = "products")  // Uses all parameters as key
@Cacheable(value = "products", key = "#id")  // Specific parameter

// Slower (computed SpEL)
@Cacheable(value = "products", key = "T(java.util.Objects).hash(#id, #name)")
```

**2. Cache Size Tuning:**
```properties
# Caffeine: Set appropriate maximumSize
spring.cache.caffeine.spec=maximumSize=10000,expireAfterWrite=15m

# Redis: Monitor memory usage
# MEMORY STATS command in Redis CLI
```

**3. TTL Configuration:**
```properties
# Redis: TTL in milliseconds
spring.cache.redis.time-to-live=600000  # 10 minutes

# Caffeine: In spec
spring.cache.caffeine.spec=expireAfterWrite=10m
```

## Spring Boot Auto-Configuration

### Auto-Detected Cache Managers

Spring Boot auto-configures a CacheManager based on classpath presence (in priority order):

1. **Redis** - if `spring-boot-starter-data-redis` is present
2. **Caffeine** - if `caffeine` library is present
3. **EhCache** - if `ehcache` library is present
4. **Simple** - default in-memory caching

To explicitly set the cache type:
```properties
spring.cache.type=redis
```

### Conditional Bean Creation

```java
@Bean
@ConditionalOnMissingBean(CacheManager.class)
public CacheManager cacheManager() {
    return new ConcurrentMapCacheManager("products", "users");
}
```

## Transaction Integration

### Cache + @Transactional Interaction

```java
@Service
@Transactional
public class ProductService {
    
    @Cacheable(value = "products", key = "#id")
    @Transactional(readOnly = true)  // Combines with cache
    public Product getProduct(Long id) {
        return productRepository.findById(id).orElse(null);
    }
    
    @CachePut(value = "products", key = "#product.id")
    @Transactional  // Ensure atomicity of save + cache update
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }
    
    @CacheEvict(value = "products", key = "#id")
    @Transactional
    public void deleteProduct(Long id) {
        productRepository.deleteById(id);
    }
}
```

## Monitoring and Metrics

### Spring Boot Actuator Integration

```properties
# Enable caching metrics
management.endpoints.web.exposure.include=metrics,health

# View cache metrics
GET http://localhost:8080/actuator/metrics
GET http://localhost:8080/actuator/metrics/cache.hits
GET http://localhost:8080/actuator/metrics/cache.misses
```

### Custom Cache Metrics

```java
@Component
public class CacheMetricsCollector {
    private final MeterRegistry meterRegistry;

    public void recordCacheHit(String cacheName) {
        meterRegistry.counter("cache.hits", "cache", cacheName).increment();
    }

    public void recordCacheMiss(String cacheName) {
        meterRegistry.counter("cache.misses", "cache", cacheName).increment();
    }
}
```

## EhCache XML Configuration Reference

### ehcache.xml Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ehcache.org/v3"
    xmlns:jsr107="http://www.ehcache.org/v3/jsr107"
    xsi:schemaLocation="
        http://www.ehcache.org/v3 http://www.ehcache.org/schema/ehcache-core-3.0.xsd
        http://www.ehcache.org/v3/jsr107 http://www.ehcache.org/schema/ehcache-107-ext-3.0.xsd">

    <!-- Cache Configuration -->
    <cache alias="cacheName">
        <key-type>java.lang.Long</key-type>
        <value-type>com.example.Product</value-type>
        
        <!-- Time to Live -->
        <expiry>
            <ttl unit="minutes">30</ttl>
        </expiry>
        
        <!-- Storage Configuration -->
        <resources>
            <heap unit="entries">1000</heap>
            <offheap unit="MB">50</offheap>
            <disk unit="GB">1</disk>
        </resources>
        
        <!-- Listeners (optional) -->
        <listeners>
            <listener>
                <class>com.example.CustomCacheEventListener</class>
                <event-firing-mode>ASYNCHRONOUS</event-firing-mode>
                <events-to-fire-on>CREATED</events-to-fire-on>
                <events-to-fire-on>EXPIRED</events-to-fire-on>
            </listener>
        </listeners>
    </cache>
</config>
```

### Common EhCache Attributes

- `heap` - On-heap memory storage (fast, limited)
- `offheap` - Off-heap memory storage (slower, larger)
- `disk` - Disk storage (slowest, unlimited)
- `ttl` - Time to live before expiration
- `idle` - Time to idle before expiration (if not accessed)

## Common Pitfalls and Solutions

### Problem 1: Cache Not Working

**Symptoms:** Cache is never hit, always querying database.

**Causes & Solutions:**
```java
// Problem: @Cacheable on public method called from same bean
@Service
public class ProductService {
    @Cacheable("products")
    public Product get(Long id) { }
    
    public Product getDetails(Long id) {
        return this.get(id);  // ❌ Won't use cache (no proxy)
    }
}

// Solution: Inject service or call through interface
@Service
public class DetailsService {
    @Autowired
    private ProductService productService;
    
    public Product getDetails(Long id) {
        return productService.get(id);  // ✅ Uses cache
    }
}

// Problem: Caching non-serializable objects with Redis
@Cacheable("products")
public Product get(Long id) {
    Product p = new Product();
    p.setConnection(dbConnection);  // ❌ Not serializable
    return p;
}

// Solution: Ensure all cached objects are serializable
@Cacheable("products")
public ProductDTO get(Long id) {
    return mapper.toDTO(productRepository.findById(id));  // ✅ DTO is serializable
}
```

### Problem 2: Stale Cache Data

**Symptoms:** Updates aren't reflected in cached data.

**Solution:**
```java
// Always evict cache on update
@CacheEvict(value = "products", key = "#id")
public void updateProduct(Long id, UpdateRequest req) {
    Product product = productRepository.findById(id).orElseThrow();
    product.update(req);
    productRepository.save(product);
}

// Or use @CachePut to keep cache fresh
@CachePut(value = "products", key = "#result.id")
public Product updateProduct(Long id, UpdateRequest req) {
    Product product = productRepository.findById(id).orElseThrow();
    product.update(req);
    return productRepository.save(product);
}
```

### Problem 3: Memory Leak

**Symptoms:** Memory usage grows unbounded.

**Solution:**
```properties
# Configure cache eviction policies
spring.cache.caffeine.spec=maximumSize=10000,expireAfterWrite=10m

# Redis: Set TTL
spring.cache.redis.time-to-live=600000

# Monitor cache size
```

## External Resources

### Official Documentation

- [Spring Cache Abstraction](https://docs.spring.io/spring-framework/reference/integration/cache.html)
- [Spring Boot Caching Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/io.html#io.caching)
- [Spring Framework Caching Guide](https://spring.io/guides/gs/caching/)

### Third-Party Libraries

- [Caffeine Cache](https://github.com/ben-manes/caffeine/wiki)
- [EhCache Documentation](https://www.ehcache.org/documentation/3.10/)
- [Redis Documentation](https://redis.io/documentation)

### Related Skills

- **spring-boot-performance-tuning** - Comprehensive performance optimization
- **spring-boot-data-persistence** - Database optimization patterns
- **spring-boot-rest-api-standards** - API design with caching headers

### Useful Articles

- [Spring Cache Abstraction Tutorial](https://www.baeldung.com/spring-cache-tutorial)
- [Redis Caching in Spring Boot](https://www.baeldung.com/spring-boot-redis)
- [Cache Stampede Problem](https://en.wikipedia.org/wiki/Cache_stampede)
- [Cache Invalidation Strategies](https://martinfowler.com/bliki/TwoHardThings.html)

## SpEL Reference for Cache Keys

### Basic Expressions

```java
// Method parameters
@Cacheable(key = "#id")           // Single parameter
@Cacheable(key = "#user.id")      // Object property
@Cacheable(key = "#root.args[0]") // First argument

// Composite keys
@Cacheable(key = "#id + '-' + #type")
@Cacheable(key = "T(java.util.Objects).hash(#id, #type)")

// Collections
@Cacheable(key = "#ids.toString()")
@Cacheable(condition = "#ids.size() > 0")
```

### SpEL Context Variables

| Variable | Description |
|----------|-------------|
| `#root.method` | Method object |
| `#root.methodName` | Method name |
| `#root.target` | Target object |
| `#root.targetClass` | Target class |
| `#root.args` | Arguments array |
| `#p<index>` | Argument at index |
| `#<name>` | Named argument |
| `#result` | Method result (@CachePut, @CacheEvict) |

## Testing Reference

### Testing Cache Behavior

```java
@Test
void shouldCacheResult() {
    // Arrange
    when(repository.find(1L)).thenReturn(mockObject);
    
    // Act - First call
    service.get(1L);
    
    // Assert - Database was queried
    verify(repository, times(1)).find(1L);
    
    // Act - Second call
    service.get(1L);
    
    // Assert - Database NOT queried again (cache hit)
    verify(repository, times(1)).find(1L);
}
```

### Disabling Cache in Tests

```java
@SpringBootTest
@PropertySource("classpath:application-test.properties")
class MyServiceTest {
    // In application-test.properties:
    // spring.cache.type=none
}
```
