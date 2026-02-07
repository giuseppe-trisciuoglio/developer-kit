# AWS Secrets Manager Caching Guide

## Overview
The AWS Secrets Manager Java caching client enables in-process caching of secrets for Java applications, reducing API calls and improving performance.

## Prerequisites
- Java 8+ development environment
- AWS account with Secrets Manager access
- Appropriate IAM permissions

## Installation

### Maven Dependency
```xml
<dependency>
    <groupId>com.amazonaws.secretsmanager</groupId>
    <artifactId>aws-secretsmanager-caching-java</artifactId>
    <version>2.0.0</version> // Use the latest version compatible with sdk v2
</dependency>
```

### Gradle Dependency
```gradle
implementation 'com.amazonaws.secretsmanager:aws-secretsmanager-caching-java:2.0.0'
```

## Basic Usage

### Simple Cache Setup
```java
import com.amazonaws.secretsmanager.caching.SecretCache;

public class SimpleCacheExample {
    private final SecretCache cache = new SecretCache();

    public String getSecret(String secretId) {
        return cache.getSecretString(secretId);
    }
}
```

### Cache with Custom SecretsManagerClient
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;

public class ClientAwareCacheExample {
    private final SecretCache cache;

    public ClientAwareCacheExample(SecretsManagerClient secretsClient) {
        this.cache = new SecretCache(secretsClient);
    }

    public String getSecret(String secretId) {
        return cache.getSecretString(secretId);
    }
}
```

## Cache Configuration

### SecretCacheConfiguration
```java
import com.amazonaws.secretsmanager.caching.SecretCacheConfiguration;

public class ConfiguredCacheExample {
    private final SecretCache cache;

    public ConfiguredCacheExample(SecretsManagerClient secretsClient) {
        SecretCacheConfiguration config = new SecretCacheConfiguration()
            .withMaxCacheSize(1000)           // Maximum number of cached secrets
            .withCacheItemTTL(3600000);        // 1 hour TTL in milliseconds

        this.cache = new SecretCache(secretsClient, config);
    }
}
```

### Configuration Options
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `maxCacheSize` | Integer | 1000 | Maximum number of cached secrets |
| `cacheItemTTL` | Long | 300000 (5 min) | Cache item TTL in milliseconds |
| `cacheSizeEvictionPercentage` | Integer | 10 | Percentage of items to evict when cache is full |

## Advanced Caching Patterns

### Multi-Layer Cache
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import java.util.concurrent.ConcurrentHashMap;

public class MultiLayerCache {
    private final SecretCache secretsManagerCache;
    private final ConcurrentHashMap<String, String> localCache;
    private final long localCacheTtl = 30000; // 30 seconds

    public MultiLayerCache(SecretsManagerClient secretsClient) {
        this.secretsManagerCache = new SecretCache(secretsClient);
        this.localCache = new ConcurrentHashMap<>();
    }

    public String getSecret(String secretId) {
        // Check local cache first
        String cached = localCache.get(secretId);
        if (cached != null) {
            return cached;
        }

        // Get from Secrets Manager cache
        String secret = secretsManagerCache.getSecretString(secretId);
        if (secret != null) {
            localCache.put(secretId, secret);
        }

        return secret;
    }
}
```

### Cache Statistics
```java
import com.amazonaws.secretsmanager.caching.SecretCache;

public class CacheStatsExample {
    private final SecretCache cache;

    public void demonstrateCacheStats() {
        // Get cache statistics
        long hitCount = cache.getHitCount();
        long missCount = cache.getMissCount();
        double hitRatio = cache.getHitRatio();

        System.out.println("Cache Hit Ratio: " + hitRatio);
        System.out.println("Hits: " + hitCount + ", Misses: " + missCount);

        // Clear cache statistics
        cache.clearCacheStats();
    }
}
```

## Error Handling and Cache Management

### Cache Refresh Strategy
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class CacheRefreshManager {
    private final SecretCache cache;
    private final ScheduledExecutorService scheduler;

    public CacheRefreshManager(SecretsManagerClient secretsClient) {
        this.cache = new SecretCache(secretsClient);
        this.scheduler = Executors.newScheduledThreadPool(1);
    }

    public void startRefreshSchedule() {
        // Refresh cache every hour
        scheduler.scheduleAtFixedRate(this::refreshCache, 1, 1, TimeUnit.HOURS);
    }

    private void refreshCache() {
        System.out.println("Refreshing cache...");
        cache.refresh();
    }

    public void shutdown() {
        scheduler.shutdown();
    }
}
```

### Fallback Mechanism
```java
import com.amazonaws.secretsmanager.caching.SecretCache;

public class FallbackCacheExample {
    private final SecretCache cache;
    private final SecretsManagerClient fallbackClient;

    public FallbackCacheExample(SecretsManagerClient primaryClient, SecretsManagerClient fallbackClient) {
        this.cache = new SecretCache(primaryClient);
        this.fallbackClient = fallbackClient;
    }

    public String getSecretWithFallback(String secretId) {
        try {
            // Try cached value first
            return cache.getSecretString(secretId);
        } catch (Exception e) {
            // Fallback to direct API call
            return getSecretDirect(secretId);
        }
    }

    private String getSecretDirect(String secretId) {
        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretId)
            .build();

        return fallbackClient.getSecretValue(request).secretString();
    }
}
```

## Performance Optimization

### Batch Secret Retrieval
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import java.util.List;
import java.util.ArrayList;

public class BatchSecretRetrieval {
    private final SecretCache cache;

    public List<String> getMultipleSecrets(List<String> secretIds) {
        List<String> results = new ArrayList<>();

        for (String secretId : secretIds) {
            String secret = cache.getSecretString(secretId);
            results.add(secret != null ? secret : "NOT_FOUND");
        }

        return results;
    }

    public Map<String, String> getSecretsAsMap(List<String> secretIds) {
        Map<String, String> secretMap = new HashMap<>();

        for (String secretId : secretIds) {
            String secret = cache.getSecretString(secretId);
            if (secret != null) {
                secretMap.put(secretId, secret);
            }
        }

        return secretMap;
    }
}
```

## Monitoring and Debugging

### Cache Monitoring
```java
import com.amazonaws.secretsmanager.caching.SecretCache;

public class CacheMonitor {
    private final SecretCache cache;

    public void monitorCachePerformance() {
        // Monitor cache hit rate
        double hitRatio = cache.getHitRatio();
        System.out.println("Cache Hit Ratio: " + hitRatio);

        // Monitor cache size
        long currentSize = cache.size();
        System.out.println("Current Cache Size: " + currentSize);

        // Monitor cache hits and misses
        long hits = cache.getHitCount();
        long misses = cache.getMissCount();
        System.out.println("Cache Hits: " + hits + ", Misses: " + misses);
    }

    public void printCacheContents() {
        // Note: SecretCache doesn't provide direct access to all cached items
        // This is a security feature to prevent accidental exposure of secrets
        System.out.println("Cache contents are protected and cannot be directly inspected");
    }
}
```

## Best Practices

1. **Cache Size Configuration**:
   - Adjust `maxCacheSize` based on available memory
   - Monitor memory usage and adjust accordingly
   - Consider using heap analysis tools

2. **TTL Configuration**:
   - Balance between performance and freshness
   - Shorter TTL for frequently changing secrets
   - Longer TTL for stable secrets

3. **Error Handling**:
   - Implement fallback mechanisms
   - Handle cache misses gracefully
   - Log errors without exposing sensitive information

4. **Security Considerations**:
   - Never log secret values
   - Use appropriate IAM permissions
   - Consider encryption at rest for cached data

5. **Memory Management**:
   - Monitor memory usage
   - Consider cache eviction strategies
   - Implement proper cleanup in shutdown hooks