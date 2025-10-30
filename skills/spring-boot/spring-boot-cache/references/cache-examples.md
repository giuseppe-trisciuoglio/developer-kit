# Spring Boot Cache Abstraction - Examples

This document provides concrete, progressive examples demonstrating Spring Boot caching patterns from basic to advanced scenarios.

## Example 1: Basic Product Caching

A simple e-commerce scenario with product lookup caching.

### Domain Model

```java
@Getter
@ToString
@EqualsAndHashCode(of = "id")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class Product {
    private Long id;
    private String name;
    private BigDecimal price;
    private Integer stock;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### Service with @Cacheable

```java
@Service
@CacheConfig(cacheNames = "products")
@RequiredArgsConstructor
@Slf4j
public class ProductService {
    private final ProductRepository productRepository;

    @Cacheable
    public Product getProductById(Long id) {
        log.info("Fetching product {} from database", id);
        return productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }

    @Cacheable(key = "#name")
    public Product getProductByName(String name) {
        log.info("Fetching product by name: {}", name);
        return productRepository.findByName(name)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }

    @CachePut(key = "#product.id")
    public Product updateProduct(Product product) {
        log.info("Updating product {}", product.getId());
        return productRepository.save(product);
    }

    @CacheEvict
    public void deleteProduct(Long id) {
        log.info("Deleting product {}", id);
        productRepository.deleteById(id);
    }

    @CacheEvict(allEntries = true)
    public void refreshAllProducts() {
        log.info("Refreshing all product cache");
    }
}
```

### Test Example

```java
@SpringBootTest
@Testcontainers
class ProductServiceCacheTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");
    
    @Autowired
    private ProductService productService;
    
    @SpyBean
    private ProductRepository productRepository;

    @Test
    void shouldCacheProductAfterFirstCall() {
        // Given
        Product product = Product.builder()
            .id(1L)
            .name("Laptop")
            .price(BigDecimal.valueOf(999.99))
            .stock(10)
            .build();

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        // When - First call
        Product result1 = productService.getProductById(1L);
        
        // Then - Verify database was called
        verify(productRepository, times(1)).findById(1L);
        assertThat(result1).isEqualTo(product);

        // When - Second call (should hit cache)
        Product result2 = productService.getProductById(1L);

        // Then - Database not called again
        verify(productRepository, times(1)).findById(1L);  // Still 1x
        assertThat(result2).isEqualTo(result1);
    }

    @Test
    void shouldEvictCacheOnDelete() {
        // Given
        Product product = Product.builder()
            .id(1L)
            .name("Laptop")
            .price(BigDecimal.valueOf(999.99))
            .build();

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        // Populate cache
        productService.getProductById(1L);
        verify(productRepository, times(1)).findById(1L);

        // When - Delete (evicts cache)
        productService.deleteProduct(1L);

        // Then - Next call should query database again
        when(productRepository.findById(1L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> productService.getProductById(1L))
            .isInstanceOf(ResourceNotFoundException.class);
        verify(productRepository, times(2)).findById(1L);
    }
}
```

---

## Example 2: Conditional Caching with Business Logic

Cache products only under specific conditions (e.g., only expensive items).

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class PremiumProductService {
    private final ProductRepository productRepository;

    @Cacheable(
        value = "premiumProducts",
        condition = "#price > 500",  // Cache only items over 500
        unless = "#result == null"
    )
    public Product getPremiumProduct(Long id, BigDecimal price) {
        log.info("Fetching premium product {} (price: {})", id, price);
        return productRepository.findById(id)
            .orElse(null);
    }

    @CachePut(
        value = "discountedProducts",
        key = "#product.id",
        condition = "#product.price < 50"  // Cache only discounted items
    )
    public Product updateDiscountedProduct(Product product) {
        log.info("Updating discounted product {}", product.getId());
        return productRepository.save(product);
    }
}
```

**Test:**

```java
@Test
void shouldCachePremiumProductsOnly() {
    // Given - Cheap product
    Product cheapProduct = Product.builder()
        .id(1L)
        .name("Budget Item")
        .price(BigDecimal.valueOf(29.99))
        .build();

    // When - Call with cheap price (won't cache due to condition)
    Product result = premiumProductService.getPremiumProduct(1L, BigDecimal.valueOf(29.99));

    // Then - Result should be cached (condition false, so not cached)
    verify(productRepository, times(1)).findById(1L);
    
    // Second call should hit DB again
    premiumProductService.getPremiumProduct(1L, BigDecimal.valueOf(29.99));
    verify(productRepository, times(2)).findById(1L);
}
```

---

## Example 3: Multiple Caches and @Caching

Handle complex scenarios with multiple cache operations.

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class InventoryService {
    private final ProductRepository productRepository;

    @Caching(
        cacheable = @Cacheable("inventoryCache"),
        put = {
            @CachePut(value = "stockCache", key = "#id"),
            @CachePut(value = "priceCache", key = "#id")
        }
    )
    public Product getInventoryDetails(Long id) {
        log.info("Fetching inventory details for {}", id);
        return productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }

    @Caching(
        evict = {
            @CacheEvict("inventoryCache"),
            @CacheEvict("stockCache"),
            @CacheEvict("priceCache")
        }
    )
    public void reloadInventory(Long id) {
        log.info("Reloading inventory for {}", id);
        // Trigger inventory sync from external system
    }
}
```

---

## Example 4: Programmatic Cache Management

Manually managing caches for advanced scenarios.

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class CacheManagementService {
    private final CacheManager cacheManager;

    public void evictProductCache(Long productId) {
        Cache cache = cacheManager.getCache("products");
        if (cache != null) {
            cache.evict(productId);
            log.info("Evicted product {} from cache", productId);
        }
    }

    public void clearAllCaches() {
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                cache.clear();
                log.info("Cleared cache: {}", cacheName);
            }
        });
    }

    public <T> T getOrCompute(String cacheName, Object key, Callable<T> valueLoader) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache == null) {
            log.warn("Cache {} not found", cacheName);
            return null;
        }

        Cache.ValueWrapper wrapper = cache.get(key);
        if (wrapper != null) {
            return (T) wrapper.get();
        }

        try {
            T value = valueLoader.call();
            cache.put(key, value);
            return value;
        } catch (Exception e) {
            log.error("Error computing cache value", e);
            throw new RuntimeException(e);
        }
    }
}
```

---

## Example 5: Cache Warming/Preloading

Populate cache with frequently accessed data at startup.

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class CacheWarmupService implements InitializingBean {
    private final ProductService productService;
    private final ProductRepository productRepository;

    @Override
    public void afterPropertiesSet() {
        warmupCache();
    }

    private void warmupCache() {
        log.info("Warming up product cache...");
        
        // Load top 100 products
        List<Product> topProducts = productRepository.findTop100ByOrderByPopularityDesc();
        topProducts.forEach(product -> {
            try {
                productService.getProductById(product.getId());
            } catch (Exception e) {
                log.warn("Failed to warm cache for product {}", product.getId(), e);
            }
        });
        
        log.info("Cache warmup completed. {} products cached", topProducts.size());
    }
}
```

---

## Example 6: Cache Statistics and Monitoring

Track cache performance metrics.

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class CacheStatsService {
    private final CacheManager cacheManager;

    @Scheduled(fixedRate = 60000)  // Every minute
    public void logCacheStats() {
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null && cache.getNativeCache() instanceof ConcurrentMapCache) {
                ConcurrentMapCache concreteCache = (ConcurrentMapCache) cache.getNativeCache();
                log.info("Cache [{}] - Size: {}", cacheName, concreteCache.getStore().size());
            }
        });
    }

    @GetMapping("/cache/stats")
    public ResponseEntity<Map<String, CacheStats>> getCacheStatistics() {
        Map<String, CacheStats> stats = new HashMap<>();
        
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                CacheStats cacheStats = new CacheStats(
                    cacheName,
                    getCacheSize(cache),
                    LocalDateTime.now()
                );
                stats.put(cacheName, cacheStats);
            }
        });
        
        return ResponseEntity.ok(stats);
    }

    private int getCacheSize(Cache cache) {
        if (cache.getNativeCache() instanceof ConcurrentMap) {
            return ((ConcurrentMap<?, ?>) cache.getNativeCache()).size();
        }
        return 0;
    }
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class CacheStats {
    private String cacheName;
    private int size;
    private LocalDateTime timestamp;
}
```

---

## Example 7: TTL-Based Cache with Scheduled Eviction

Expire cache entries after a specific time.

```java
@Configuration
@EnableCaching
@EnableScheduling
public class CacheConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("products", "users", "orders");
    }
}

@Component
@RequiredArgsConstructor
@Slf4j
public class CacheExpirationService {
    private final CacheManager cacheManager;
    private final Map<String, LocalDateTime> cacheExpirations = new ConcurrentHashMap<>();

    public void setExpiration(String cacheName, Object key, Duration duration) {
        String expirationKey = cacheName + ":" + key;
        cacheExpirations.put(expirationKey, LocalDateTime.now().plus(duration));
        log.info("Set cache expiration for {} after {}", expirationKey, duration);
    }

    @Scheduled(fixedRate = 5000)  // Check every 5 seconds
    public void evictExpiredEntries() {
        LocalDateTime now = LocalDateTime.now();
        
        cacheExpirations.entrySet()
            .removeIf(entry -> {
                if (now.isAfter(entry.getValue())) {
                    String[] parts = entry.getKey().split(":");
                    String cacheName = parts[0];
                    String key = parts[1];
                    
                    Cache cache = cacheManager.getCache(cacheName);
                    if (cache != null) {
                        cache.evict(key);
                        log.info("Evicted expired cache entry: {}", entry.getKey());
                    }
                    return true;
                }
                return false;
            });
    }
}
```

---

## Example 8: Cache Invalidation Pattern with Events

Use domain events to invalidate cache across services.

```java
public class ProductUpdatedEvent extends ApplicationEvent {
    private final Long productId;
    private final String changeType;  // UPDATED, DELETED, CREATED

    public ProductUpdatedEvent(Object source, Long productId, String changeType) {
        super(source);
        this.productId = productId;
        this.changeType = changeType;
    }
}

@Component
@RequiredArgsConstructor
@Slf4j
public class ProductService {
    private final ProductRepository productRepository;
    private final ApplicationEventPublisher eventPublisher;

    public Product updateProduct(Long id, UpdateProductRequest request) {
        Product product = productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
        
        product.setName(request.getName());
        product.setPrice(request.getPrice());
        Product updated = productRepository.save(product);
        
        // Publish event to invalidate cache
        eventPublisher.publishEvent(new ProductUpdatedEvent(this, id, "UPDATED"));
        
        return updated;
    }
}

@Component
@RequiredArgsConstructor
@Slf4j
public class CacheInvalidationListener {
    private final CacheManager cacheManager;

    @EventListener
    public void onProductUpdated(ProductUpdatedEvent event) {
        log.info("Invalidating cache for product {}", event.getProductId());
        
        Cache productsCache = cacheManager.getCache("products");
        if (productsCache != null) {
            productsCache.evict(event.getProductId());
        }
        
        Cache productsListCache = cacheManager.getCache("productsList");
        if (productsListCache != null) {
            productsListCache.clear();
        }
    }
}
```

---

## Example 9: Distributed Caching with Caffeine

Using Caffeine for local caching with advanced features.

```java
@Configuration
@EnableCaching
public class CaffeineCacheConfig {

    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager("products", "users");
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .recordStats());
        return cacheManager;
    }
}

@Component
@RequiredArgsConstructor
public class CacheMetricsService {
    private final CacheManager cacheManager;

    @GetMapping("/cache/metrics")
    public ResponseEntity<Map<String, Object>> getCacheMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null && cache.getNativeCache() instanceof com.github.benmanes.caffeine.cache.Cache) {
                com.github.benmanes.caffeine.cache.Cache<?, ?> caffeineCache = 
                    (com.github.benmanes.caffeine.cache.Cache<?, ?>) cache.getNativeCache();
                
                com.github.benmanes.caffeine.cache.stats.CacheStats stats = caffeineCache.stats();
                metrics.put(cacheName, Map.of(
                    "hitCount", stats.hitCount(),
                    "missCount", stats.missCount(),
                    "hitRate", stats.hitRate(),
                    "size", caffeineCache.estimatedSize()
                ));
            }
        });
        
        return ResponseEntity.ok(metrics);
    }
}
```

---

## Example 10: Testing Cache-Related Scenarios

```java
@SpringBootTest
class CacheIntegrationTest {
    
    @Autowired
    private ProductService productService;
    
    @Autowired
    private CacheManager cacheManager;
    
    @MockBean
    private ProductRepository productRepository;

    @Test
    void shouldDemonstrateCachingLifecycle() {
        // Given
        Product product = Product.builder()
            .id(1L)
            .name("Test Product")
            .price(BigDecimal.TEN)
            .build();

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        // Verify cache is empty
        Cache cache = cacheManager.getCache("products");
        assertThat(cache.get(1L)).isNull();

        // First call - populates cache
        Product result1 = productService.getProductById(1L);
        verify(productRepository, times(1)).findById(1L);
        
        // Cache is now populated
        assertThat(cache.get(1L)).isNotNull();

        // Second call - uses cache
        Product result2 = productService.getProductById(1L);
        verify(productRepository, times(1)).findById(1L);  // Still 1x
        assertThat(result1).isEqualTo(result2);

        // Manual eviction
        cache.evict(1L);
        assertThat(cache.get(1L)).isNull();

        // Next call queries database again
        Product result3 = productService.getProductById(1L);
        verify(productRepository, times(2)).findById(1L);
    }
}
```
