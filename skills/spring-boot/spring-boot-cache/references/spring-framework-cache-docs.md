# Spring Framework Cache Reference (Official)

Curated excerpts from the official Spring Framework reference documentation
covering caching fundamentals and annotation usage. Source pages are from the
[Spring Framework Reference Guide 6.2](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/).

## Cache Abstraction Overview

- **Purpose**: Transparently wrap expensive service methods and reuse results
  resolved from configured cache managers.
- **Enablement**:

  ```java
  @Configuration
  @EnableCaching
  public class CacheConfig {
      @Bean
      public CacheManager cacheManager() {
          return new ConcurrentMapCacheManager("books");
      }
  }
  ```

  Source: [/integration/cache/annotations](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/annotations)

- **Supported return types**: `CompletableFuture`, Reactor `Mono`/`Flux`,
  blocking objects, and collections are all cacheable. For async/reactive types,
  Spring stores the resolved value and rehydrates it on retrieval.

## Core Annotations

### `@Cacheable`

- Cache the method invocation result using the provided cache name and key.
- Supports conditional caching with `condition` (pre-invocation) and `unless`
  (post-invocation, access `#result`).

```java
@Cacheable(cacheNames = "book", condition = "#isbn.length() == 13", unless = "#result.hardback")
public Book findBook(String isbn) { ... }
```

Source: [/integration/cache/annotations](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/annotations)

### `@CachePut` and `@CacheEvict`

- `@CachePut`: Always run the method and update cache entry with fresh result.
- `@CacheEvict`: Remove entries; use `allEntries = true` or `beforeInvocation`
  for pre-call eviction.

```java
@CacheEvict(cacheNames = "books", key = "#isbn", beforeInvocation = true)
public void reset(String isbn) { ... }
```

Source: [/integration/cache/annotations](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/annotations)

### `@Caching`

- Bundle multiple cache operations on a single method:

```java
@Caching(evict = {
    @CacheEvict("primary"),
    @CacheEvict(cacheNames = "secondary", key = "#isbn")
})
public Book importBooks(String isbn) { ... }
```

Source: [/integration/cache/annotations](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/annotations)

## Store Configuration Highlights

- **Caffeine**: Configure `CaffeineCacheManager` to create caches on demand.

  ```java
  @Bean
  CacheManager cacheManager() {
      return new CaffeineCacheManager();
  }
  ```

  Source: [/integration/cache/store-configuration](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/store-configuration)

- **XML alternative**: Use `<cache:annotation-driven cache-manager="..."/>`
  when annotation configuration is not feasible.

  ```xml
  <cache:annotation-driven cache-manager="cacheManager"/>
  <bean id="cacheManager" class="org.springframework.cache.caffeine.CaffeineCacheManager"/>
  ```

  Source: [/integration/cache/declarative-xml](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/declarative-xml)

## Reactive and Async Support

- `@Cacheable` works with asynchronous signatures:

  ```java
  @Cacheable("books")
  public Mono<Book> findBook(ISBN isbn) { ... }
  ```

  ```java
  @Cacheable(cacheNames = "foos", sync = true)
  public CompletableFuture<Foo> executeExpensiveOperation(String id) { ... }
  ```

  Source: [/integration/cache/annotations](https://docs.spring.io/spring-framework/reference/6.2/-SNAPSHOT/integration/cache/annotations)

## Additional Resources

- [`spring-cache-doc-snippet.md`](spring-cache-doc-snippet.md): Excerpt of the
  narrative caching overview from the Spring documentation.
- Refer to [`cache-core-reference.md`](cache-core-reference.md) for expanded
  API reference material and `cache-examples.md` for progressive examples.
