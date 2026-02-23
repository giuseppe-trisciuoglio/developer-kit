---
name: unit-test-caching
description: Provides patterns for unit testing caching behavior using Spring Cache annotations (@Cacheable, @CachePut, @CacheEvict). Use when validating cache configuration and cache hit/miss scenarios.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Unit Testing Spring Caching

## Overview

This skill defines focused tests for Spring cache behavior in Boot 3.x.
It validates cache hits, misses, updates, and evictions using deterministic in-memory cache managers.

## When to Use

Use this skill when:
- Testing `@Cacheable`, `@CachePut`, and `@CacheEvict` behavior
- Verifying cache key construction and lookup consistency
- Confirming conditional caching (`condition`, `unless`)
- Validating explicit cache invalidation after writes

Trigger phrases:
- "test cacheable behavior"
- "verify cache hit miss"
- "test cache eviction"
- "spring cache unit test"

## Instructions

1. Enable caching in test configuration with `@EnableCaching`.
2. Use in-memory `CacheManager` such as `ConcurrentMapCacheManager`.
3. Provide mocked repositories as beans for proxied cache method calls.
4. Clear cache state before each test for isolation.
5. Call the same method twice and verify dependency call count is one.
6. After update/delete actions, assert cache refresh or eviction behavior.

## Examples

```java
@Test
void shouldUseCacheAfterFirstCall() {
  when(repo.findName(1L)).thenReturn("Laptop");

  String a = service.getName(1L);
  String b = service.getName(1L);

  assertThat(a).isEqualTo("Laptop");
  assertThat(b).isEqualTo("Laptop");
  verify(repo, times(1)).findName(1L);
}
```

For complete runnable examples, see [examples.md](references/examples.md)

## Best Practices

- Verify both returned value and repository interaction counts.
- Keep cache names and key strategy centralized and testable.
- Use explicit cache cleanup to avoid cross-test contamination.

## Constraints and Warnings

- Cache annotations require proxy-managed beans; direct method calls can bypass caching.
- Self-invocation in the same class does not trigger `@Cacheable` interception.
- In-memory cache tests do not validate provider-specific behavior (Redis, Caffeine tuning).
- TTL/expiration should be tested in integration scope, not with sleeps in unit tests.

## Constraints

- Do not use remote cache infrastructure in unit scope.
- Do not assert internal proxy classes or framework internals.
- Keep cache tests deterministic and timing-independent.

## References

- [Examples](references/examples.md) - Complete runnable test examples
