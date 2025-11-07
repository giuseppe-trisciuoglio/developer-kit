# Performance Tuning and Optimization

Optimize Apache Camel routes for maximum throughput, low latency, and efficient resource utilization.

## Thread Pool Optimization

### Configure Thread Pools

```java
@Configuration
public class ThreadPoolConfig {

    @Bean
    public ThreadPoolProfile highThroughputPool() {
        ThreadPoolProfile profile = new ThreadPoolProfile("highThroughput");
        profile.setPoolSize(50);
        profile.setMaxPoolSize(100);
        profile.setMaxQueueSize(1000);
        profile.setKeepAliveTime(60L);
        profile.setRejectedPolicy(ThreadPoolRejectedPolicy.CallerRuns);
        return profile;
    }

    @Bean
    public ThreadPoolProfile lowLatencyPool() {
        ThreadPoolProfile profile = new ThreadPoolProfile("lowLatency");
        profile.setPoolSize(20);
        profile.setMaxPoolSize(50);
        profile.setMaxQueueSize(100);
        profile.setKeepAliveTime(30L);
        return profile;
    }
}
```

### Apply Thread Pools to Routes

```java
from("kafka:high-volume-events")
    .threads()
        .threadPoolProfile("highThroughput")
        .poolSize(50)
        .maxPoolSize(100)
    .to("direct:process");

from("direct:critical-path")
    .threads()
        .threadPoolProfile("lowLatency")
    .to("direct:process");
```

## Parallel Processing

### Parallel Splitter

```java
from("jms:queue:bulk-orders")
    .split(body())
        .parallelProcessing()
        .streaming()
        .executorService(executorService)
        .to("direct:process-order")
    .end();
```

### Parallel Multicast

```java
from("direct:notify")
    .multicast()
        .parallelProcessing()
        .executorService(executorService)
        .to("direct:email", "direct:sms", "direct:push")
    .end();
```

### Concurrent Consumers

```java
from("jms:queue:orders?concurrentConsumers=10&maxConcurrentConsumers=20")
    .to("direct:process");

from("kafka:events?consumersCount=10")
    .to("direct:process");

from("seda:async?concurrentConsumers=10")
    .to("direct:process");
```

## Streaming and Batching

### Streaming Large Files

```java
from("file:/data/large-files")
    .split(body().tokenize("\n"))
        .streaming()  // Don't load entire file into memory
        .to("direct:process-line")
    .end();
```

### Batch Processing

```java
from("kafka:events?maxPollRecords=500")
    .aggregate(constant(true), new GroupedBodyAggregationStrategy())
        .completionSize(100)
        .completionTimeout(5000)
        .parallelProcessing()
        .to("direct:process-batch");
```

### Batch Database Operations

```java
from("seda:db-inserts")
    .aggregate(constant(true), new GroupedBodyAggregationStrategy())
        .completionSize(100)
        .completionTimeout(2000)
    .process(exchange -> {
        @SuppressWarnings("unchecked")
        List<Order> orders = exchange.getIn().getBody(List.class);
        orderRepository.saveAll(orders);  // Batch insert
    });
```

## Caching

### Simple Cache

```java
@Bean
public CaffeineCache orderCache() {
    return new CaffeineCache("orders",
        Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .build());
}

from("direct:get-order")
    .setHeader(CaffeineConstants.ACTION, constant(CaffeineConstants.ACTION_GET))
    .setHeader(CaffeineConstants.KEY, simple("${body.id}"))
    .to("caffeine-cache:orders")
    .choice()
        .when(header(CaffeineConstants.ACTION_HAS_RESULT).isEqualTo(true))
            .log("Cache hit for ${body.id}")
        .otherwise()
            .to("jpa:com.example.model.Order?query=SELECT o FROM Order o WHERE o.id = ${body.id}")
            .setHeader(CaffeineConstants.ACTION, constant(CaffeineConstants.ACTION_PUT))
            .to("caffeine-cache:orders")
    .end();
```

### HTTP Response Caching

```java
from("direct:api-call")
    .setProperty("cacheKey", simple("${header.endpoint}-${body}"))
    .choice()
        .when(simple("${exchangeProperty.cacheKey} != null"))
            .to("direct:check-cache")
            .choice()
                .when(header("CacheHit").isEqualTo(true))
                    .log("Cache hit")
                .otherwise()
                    .to("http://external-api")
                    .to("direct:update-cache")
            .end()
        .otherwise()
            .to("http://external-api")
    .end();
```

## Connection Pooling

### Database Connection Pool

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      pool-name: CamelHikariPool
```

### HTTP Connection Pool

```java
@Bean
public HttpComponent http() {
    HttpComponent http = new HttpComponent();

    HttpClientConfigurer configurer = (HttpClientBuilder builder) -> {
        PoolingHttpClientConnectionManager cm =
            new PoolingHttpClientConnectionManager();
        cm.setMaxTotal(200);
        cm.setDefaultMaxPerRoute(50);
        builder.setConnectionManager(cm);
        return builder;
    };

    http.setHttpClientConfigurer(configurer);
    return http;
}
```

## Message Optimization

### Reduce Message Copying

```java
// Bad: Multiple body transformations create copies
from("direct:start")
    .transform(body().append(" - processed"))
    .transform(body().append(" - validated"))
    .transform(body().append(" - enriched"));

// Good: Single transformation
from("direct:start")
    .process(exchange -> {
        String body = exchange.getIn().getBody(String.class);
        String result = body + " - processed - validated - enriched";
        exchange.getIn().setBody(result);
    });
```

### Use Direct References

```java
// Bad: Marshalling/unmarshalling unnecessarily
from("direct:start")
    .marshal().json()
    .to("direct:intermediate")
    .unmarshal().json(Order.class);

// Good: Pass object directly
from("direct:start")
    .to("direct:intermediate");
```

## JVM Tuning

### Heap Configuration

```bash
# For high-throughput applications
-Xms4g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+ParallelRefProcEnabled

# For low-latency applications
-Xms2g -Xmx2g
-XX:+UseZGC
-XX:+UnlockExperimentalVMOptions
-XX:ZCollectionInterval=5
```

### GC Logging

```bash
-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=100M
```

## Throttling and Rate Limiting

### Throttle Requests

```java
from("jms:queue:high-volume")
    .throttle(100).timePeriodMillis(1000)  // 100 msg/sec
    .asyncDelayed()  // Non-blocking
    .to("http://rate-limited-api");
```

### Dynamic Throttling

```java
from("kafka:events")
    .throttle(simple("${bean:throttleConfig.getMaxRate()}"))
        .timePeriodMillis(1000)
    .to("direct:process");

@Component
class ThrottleConfig {
    public int getMaxRate() {
        // Dynamic rate based on system load
        return getCurrentSystemLoad() < 0.8 ? 1000 : 500;
    }
}
```

## Circuit Breaker

```java
from("direct:external-call")
    .circuitBreaker()
        .resilience4jConfiguration()
            .failureRateThreshold(50)
            .slowCallRateThreshold(50)
            .slowCallDurationThreshold(2000)
            .waitDurationInOpenState(10000)
            .slidingWindowSize(10)
            .minimumNumberOfCalls(5)
        .end()
        .to("http://unreliable-service")
    .onFallback()
        .to("direct:cached-fallback")
    .end();
```

## Asynchronous Processing

### Async Routing

```java
from("direct:sync-entry")
    .to("seda:async-queue?size=10000");

from("seda:async-queue?concurrentConsumers=10")
    .to("direct:async-process");
```

### WireTap for Async Side Effects

```java
from("direct:main-flow")
    .wireTap("seda:audit?waitForTaskToComplete=Never")
    .to("direct:process");

from("seda:audit")
    .to("jpa:com.example.model.AuditLog");
```

## Memory Management

### Stream Caching

```yaml
camel:
  springboot:
    stream-caching-enabled: true
    stream-caching-spool-directory: /tmp/camel-streams
    stream-caching-spool-threshold: 128KB
```

```java
from("http://api/upload")
    .streamCaching()
    .to("file:/data/uploads");
```

### Limit Queue Sizes

```java
from("direct:input")
    .to("seda:processing?size=1000&blockWhenFull=true");
```

## Monitoring and Profiling

### Enable JMX

```yaml
camel:
  springboot:
    jmx-enabled: true
    jmx-management-statistics-level: Extended
```

### Performance Metrics

```java
from("kafka:events")
    .to("micrometer:timer:message.processing?action=start")
    .to("direct:process")
    .to("micrometer:timer:message.processing?action=stop")
    .to("micrometer:counter:messages.processed");
```

### Custom Performance Logging

```java
from("direct:monitored")
    .process(exchange -> {
        Stopwatch stopwatch = Stopwatch.createStarted();
        exchange.setProperty("stopwatch", stopwatch);
    })
    .to("direct:process")
    .process(exchange -> {
        Stopwatch stopwatch = exchange.getProperty("stopwatch", Stopwatch.class);
        long elapsed = stopwatch.elapsed(TimeUnit.MILLISECONDS);
        if (elapsed > 1000) {
            log.warn("Slow processing: {} ms", elapsed);
        }
    });
```

## Route Optimization Patterns

### Pattern: Pre-fetch and Cache

```java
@EventListener(ApplicationReadyEvent.class)
public void prefetchData() {
    // Pre-load cache on startup
    productRepository.findAll().forEach(product ->
        cache.put(product.getId(), product)
    );
}

from("direct:get-product")
    .to("direct:check-cache")
    .choice()
        .when(header("CacheHit").isEqualTo(false))
            .to("jpa:Product")
            .to("direct:update-cache")
    .end();
```

### Pattern: Lazy Initialization

```java
from("timer:init?repeatCount=0&delay=5000")
    .to("direct:initialize-resources");

from("direct:process")
    .choice()
        .when(simple("${bean:resourceManager.isInitialized()} == false"))
            .to("direct:initialize-resources")
    .end()
    .to("direct:main-processing");
```

### Pattern: Bulk Operations

```java
// Inefficient: One-by-one
from("direct:save-orders")
    .split(body())
        .to("jpa:Order")
    .end();

// Efficient: Batch insert
from("direct:save-orders")
    .process(exchange -> {
        List<Order> orders = exchange.getIn().getBody(List.class);
        orderRepository.saveAll(orders);  // Single batch operation
    });
```

## Benchmarking

### Route Performance Test

```java
@Test
void benchmarkRoute() throws Exception {
    int messageCount = 10000;
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(messageCount);
    mock.setResultWaitTime(60000);

    StopWatch watch = new StopWatch();

    for (int i = 0; i < messageCount; i++) {
        template.sendBody("direct:start", "message " + i);
    }

    mock.assertIsSatisfied();
    long elapsed = watch.taken();

    double throughput = (messageCount * 1000.0) / elapsed;
    log.info("Throughput: {} msg/sec", throughput);
    log.info("Average latency: {} ms", elapsed / messageCount);
}
```

## Performance Checklist

- [ ] Use parallel processing for independent operations
- [ ] Configure appropriate thread pool sizes
- [ ] Enable streaming for large files
- [ ] Implement batch processing where applicable
- [ ] Use caching for frequently accessed data
- [ ] Configure connection pooling
- [ ] Minimize message copying and transformation
- [ ] Use asynchronous processing for non-critical paths
- [ ] Enable stream caching for large messages
- [ ] Set appropriate queue sizes
- [ ] Monitor and profile in production
- [ ] Use circuit breakers for external calls
- [ ] Implement throttling to protect downstream systems
- [ ] Tune JVM and GC settings
- [ ] Use efficient data formats (Avro, Protobuf)

## Common Performance Anti-Patterns

### ❌ Synchronous External Calls in High-Volume Routes

```java
// Bad
from("kafka:high-volume")
    .to("http://slow-external-service")  // Blocks thread
    .to("jms:queue:output");

// Good
from("kafka:high-volume")
    .wireTap("seda:async-external-call")
    .to("jms:queue:output");

from("seda:async-external-call?concurrentConsumers=10")
    .to("http://slow-external-service");
```

### ❌ Not Using Streaming for Large Files

```java
// Bad: Loads entire file into memory
from("file:/data/large-files")
    .split(body())
        .to("direct:process")
    .end();

// Good: Streams file line by line
from("file:/data/large-files")
    .split(body().tokenize("\n"))
        .streaming()
        .to("direct:process")
    .end();
```

### ❌ Excessive Marshalling/Unmarshalling

```java
// Bad
from("direct:start")
    .marshal().json()
    .to("direct:step1")
    .unmarshal().json(Order.class)
    .marshal().json()
    .to("direct:step2")
    .unmarshal().json(Order.class);

// Good
from("direct:start")
    .to("direct:step1")
    .to("direct:step2");
```

### ❌ Single-Threaded Processing

```java
// Bad: Sequential processing
from("kafka:events")
    .to("direct:process");

from("direct:process")
    .to("http://service1")
    .to("http://service2")
    .to("http://service3");

// Good: Parallel processing
from("kafka:events?consumersCount=10")
    .multicast()
        .parallelProcessing()
        .to("http://service1", "http://service2", "http://service3")
    .end();
```

## References

- [Camel Performance Tuning](https://camel.apache.org/manual/performance-tuning.html)
- [JVM Performance Tuning](https://docs.oracle.com/en/java/javase/17/gctuning/)
- [HikariCP Configuration](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)
