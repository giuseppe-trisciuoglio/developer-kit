# Caching Test Examples

## Example 1: Verify cache hit and miss with `@Cacheable`

```java
package com.example.cache;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class CacheableServiceTest {

    private AnnotationConfigApplicationContext context;
    private ProductService productService;
    private ProductRepository productRepository;
    private CacheManager cacheManager;

    @BeforeEach
    void setUp() {
        context = new AnnotationConfigApplicationContext(CacheTestConfig.class);
        productService = context.getBean(ProductService.class);
        productRepository = context.getBean(ProductRepository.class);
        cacheManager = context.getBean(CacheManager.class);
        cacheManager.getCache("products").clear();
    }

    @Test
    void shouldUseCacheAfterFirstLookup() {
        when(productRepository.findNameById(1L)).thenReturn("Laptop");

        String first = productService.getProductName(1L);
        String second = productService.getProductName(1L);

        assertThat(first).isEqualTo("Laptop");
        assertThat(second).isEqualTo("Laptop");
        verify(productRepository, times(1)).findNameById(1L);
    }

    interface ProductRepository {
        String findNameById(Long id);
    }

    static class ProductService {
        private final ProductRepository repository;

        ProductService(ProductRepository repository) {
            this.repository = repository;
        }

        @Cacheable(cacheNames = "products", key = "#id")
        String getProductName(Long id) {
            return repository.findNameById(id);
        }
    }

    @Configuration
    @EnableCaching
    static class CacheTestConfig {
        @Bean
        CacheManager cacheManager() {
            return new ConcurrentMapCacheManager("products");
        }

        @Bean
        ProductRepository productRepository() {
            return mock(ProductRepository.class);
        }

        @Bean
        ProductService productService(ProductRepository repository) {
            return new ProductService(repository);
        }
    }
}
```

## Example 2: Verify `@CachePut` and `@CacheEvict`

```java
package com.example.cache;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static org.assertj.core.api.Assertions.assertThat;

class CachePutAndEvictTest {

    private AnnotationConfigApplicationContext context;
    private InventoryService inventoryService;
    private Cache cache;

    @BeforeEach
    void setUp() {
        context = new AnnotationConfigApplicationContext(TestConfig.class);
        inventoryService = context.getBean(InventoryService.class);
        CacheManager cacheManager = context.getBean(CacheManager.class);
        cache = cacheManager.getCache("inventory");
        cache.clear();
    }

    @Test
    void shouldRefreshCacheEntryWithCachePut() {
        inventoryService.updateStock("SKU-1", 10);

        Integer cachedValue = cache.get("SKU-1", Integer.class);
        assertThat(cachedValue).isEqualTo(10);
    }

    @Test
    void shouldRemoveCacheEntryWithCacheEvict() {
        inventoryService.updateStock("SKU-2", 5);
        assertThat(cache.get("SKU-2", Integer.class)).isEqualTo(5);

        inventoryService.deleteStock("SKU-2");

        assertThat(cache.get("SKU-2")).isNull();
    }

    static class InventoryService {
        @Cacheable(cacheNames = "inventory", key = "#sku")
        Integer getStock(String sku) {
            return 0;
        }

        @CachePut(cacheNames = "inventory", key = "#sku")
        Integer updateStock(String sku, Integer value) {
            return value;
        }

        @CacheEvict(cacheNames = "inventory", key = "#sku")
        void deleteStock(String sku) {
        }
    }

    @Configuration
    @EnableCaching
    static class TestConfig {
        @Bean
        CacheManager cacheManager() {
            return new ConcurrentMapCacheManager("inventory");
        }

        @Bean
        InventoryService inventoryService() {
            return new InventoryService();
        }
    }
}
```
