# Actuator Endpoints

Actuator endpoints let you monitor and interact with your application. Spring Boot includes a number of built-in endpoints and lets you add your own. For example, the `health` endpoint provides basic application health information.

You can control access to each individual endpoint and expose them (make them remotely accessible) over HTTP or JMX. An endpoint is considered to be available when access to it is permitted and it is exposed. The built-in endpoints are auto-configured only when they are available. Most applications choose exposure over HTTP, where the ID of the endpoint and a prefix of `/actuator` is mapped to a URL. For example, by default, the `health` endpoint is mapped to `/actuator/health`.

> **TIP**
> 
> To learn more about the Actuator's endpoints and their request and response formats, see the [Spring Boot Actuator API documentation](https://docs.spring.io/spring-boot/docs/current/actuator-api/htmlsingle/).

## Available Endpoints

The following technology-agnostic endpoints are available:

| ID | Description |
|----|----|
| `auditevents` | Exposes audit events information for the current application. Requires an `AuditEventRepository` bean. |
| `beans` | Displays a complete list of all the Spring beans in your application. |
| `caches` | Exposes available caches. |
| `conditions` | Shows the conditions that were evaluated on configuration and auto-configuration classes and the reasons why they did or did not match. |
| `configprops` | Displays a collated list of all `@ConfigurationProperties`. Subject to sanitization. |
| `env` | Exposes properties from Spring's `ConfigurableEnvironment`. Subject to sanitization. |
| `flyway` | Shows any Flyway database migrations that have been applied. Requires one or more `Flyway` beans. |
| `health` | Shows application health information. |
| `httpexchanges` | Displays HTTP exchange information (by default, the last 100 HTTP request-response exchanges). Requires an `HttpExchangeRepository` bean. |
| `info` | Displays arbitrary application info. |
| `integrationgraph` | Shows the Spring Integration graph. Requires a dependency on `spring-integration-core`. |
| `loggers` | Shows and modifies the configuration of loggers in the application. |
| `liquibase` | Shows any Liquibase database migrations that have been applied. Requires one or more `Liquibase` beans. |
| `metrics` | Shows metrics information for the current application. |
| `mappings` | Displays a collated list of all `@RequestMapping` paths. |
| `quartz` | Shows information about Quartz Scheduler jobs. Subject to sanitization. |
| `scheduledtasks` | Displays the scheduled tasks in your application. |
| `sessions` | Allows retrieval and deletion of user sessions from a Spring Session-backed session store. Requires a servlet-based web application that uses Spring Session. |
| `shutdown` | Lets the application be gracefully shutdown. Only works when using jar packaging. Disabled by default. |
| `startup` | Shows the startup steps data collected by the `ApplicationStartup`. Requires the `SpringApplication` to be configured with a `BufferingApplicationStartup`. |
| `threaddump` | Performs a thread dump. |

If your application is a web application (Spring MVC, Spring WebFlux, or Jersey), you can use the following additional endpoints:

| ID | Description |
|----|----|
| `heapdump` | Returns a heap dump file. On a HotSpot JVM, an `HPROF`-format file is returned. On an OpenJ9 JVM, a `PHD`-format file is returned. |
| `logfile` | Returns the contents of the logfile (if the `logging.file.name` or the `logging.file.path` property has been set). Supports the use of the HTTP `Range` header to retrieve part of the log file's content. |
| `prometheus` | Exposes metrics in a format that can be scraped by a Prometheus server. Requires a dependency on `micrometer-registry-prometheus`. |

## Controlling Access to Endpoints

By default, access to all endpoints except for `shutdown` and `heapdump` is unrestricted. To configure the permitted access to an endpoint, use its `management.endpoint.<id>.access` property. The following example allows unrestricted access to the `shutdown` endpoint:

```yaml
management:
  endpoint:
    shutdown:
      access: unrestricted
```

If you prefer access to be opt-in rather than opt-out, set the `management.endpoints.access.default` property to `none` and use individual endpoint `access` properties to opt back in. The following example allows read-only access to the `loggers` endpoint and denies access to all other endpoints:

```yaml
management:
  endpoints:
    access:
      default: none
  endpoint:
    loggers:
      access: read-only
```

> **NOTE**
> 
> Inaccessible endpoints are removed entirely from the application context. If you want to change only the technologies over which an endpoint is exposed, use the `include` and `exclude` properties instead.

### Limiting Access

Application-wide endpoint access can be limited using the `management.endpoints.access.max-permitted` property. This property takes precedence over the default access or an individual endpoint's access level. Set it to `none` to make all endpoints inaccessible. Set it to `read-only` to only allow read access to endpoints.

For `@Endpoint`, `@JmxEndpoint`, and `@WebEndpoint`, read access equates to the endpoint methods annotated with `@ReadOperation`. For `@ControllerEndpoint` and `@RestControllerEndpoint`, read access equates to HTTP GET requests.

## Exposing Endpoints

By default, only the `health` endpoint is exposed over HTTP and JMX. To configure which endpoints are exposed, use the `include` and `exclude` properties:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info,metrics"
        exclude: "beans"
```

The `include` property lists the IDs of the endpoints that are exposed. The `exclude` property lists the IDs of the endpoints that should not be exposed. The `exclude` property takes precedence over the `include` property.

To expose all endpoints over HTTP:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

## Security

For security purposes, only the `/health` endpoint is exposed over HTTP by default. You can use the `management.endpoints.web.exposure.include` property to configure the endpoints that are exposed.

If Spring Security is on the classpath and no other `WebSecurityConfigurer` bean is present, all actuators other than `/health` are secured by Spring Boot auto-configuration. If you define a custom `WebSecurityConfigurer` bean, Spring Boot auto-configuration backs off and lets you fully control the actuator access rules.

## Custom Endpoints

You can add additional endpoints by using `@Endpoint` and `@Component` annotations:

```java
@Component
@Endpoint(id = "custom")
public class CustomEndpoint {

    @ReadOperation
    public String customEndpoint() {
        return "Custom endpoint response";
    }
}
```

### Web Endpoints

For web-specific endpoints, use `@WebEndpoint`:

```java
@Component
@WebEndpoint(id = "web-custom")
public class WebCustomEndpoint {

    @ReadOperation
    public String webCustomEndpoint() {
        return "Web custom endpoint response";
    }
}
```

### JMX Endpoints

For JMX-specific endpoints, use `@JmxEndpoint`:

```java
@Component
@JmxEndpoint(id = "jmx-custom")
public class JmxCustomEndpoint {

    @ReadOperation
    public String jmxCustomEndpoint() {
        return "JMX custom endpoint response";
    }
}
```

## Health Endpoint

The `health` endpoint provides detailed information about the health of the application. By default, only health status is shown to unauthenticated users:

```json
{
  "status": "UP"
}
```

To show detailed health information:

```yaml
management:
  endpoint:
    health:
      show-details: always
```

### Custom Health Indicators

You can provide custom health information by registering Spring beans that implement the `HealthIndicator` interface:

```java
@Component
public class CustomHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // Perform custom health check
        boolean isHealthy = checkHealth();
        
        if (isHealthy) {
            return Health.up()
                .withDetail("custom", "Service is running")
                .build();
        } else {
            return Health.down()
                .withDetail("custom", "Service is down")
                .build();
        }
    }
    
    private boolean checkHealth() {
        // Custom health check logic
        return true;
    }
}
```

## Info Endpoint

The `info` endpoint publishes information about your application. You can customize this information by implementing `InfoContributor`:

```java
@Component
public class CustomInfoContributor implements InfoContributor {

    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("custom", "Custom application info");
    }
}
```

### Git Information

To expose git information in the `info` endpoint, add the following to your build:

**Maven:**
```xml
<plugin>
    <groupId>pl.project13.maven</groupId>
    <artifactId>git-commit-id-plugin</artifactId>
</plugin>
```

**Gradle:**
```groovy
plugins {
    id "com.gorylenko.gradle-git-properties" version "2.4.1"
}
```

### Build Information

Build information can be added to the `info` endpoint by configuring the build plugins:

**Maven:**
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals>
                <goal>build-info</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**Gradle:**
```groovy
springBoot {
    buildInfo()
}
```

## Metrics Endpoint

The `metrics` endpoint provides access to application metrics collected by Micrometer. You can view all available metrics:

```
GET /actuator/metrics
```

Or view a specific metric:

```
GET /actuator/metrics/jvm.memory.used
```

### Custom Metrics

You can add custom metrics using Micrometer:

```java
@Component
public class CustomMetrics {

    private final Counter customCounter;
    private final Timer customTimer;

    public CustomMetrics(MeterRegistry meterRegistry) {
        this.customCounter = Counter.builder("custom.requests")
            .description("Custom request counter")
            .register(meterRegistry);
            
        this.customTimer = Timer.builder("custom.processing.time")
            .description("Custom processing time")
            .register(meterRegistry);
    }

    public void incrementCounter() {
        customCounter.increment();
    }

    public void recordTime(Duration duration) {
        customTimer.record(duration);
    }
}
```

## Environment Endpoint

The `env` endpoint exposes properties from the Spring `Environment`. This includes configuration properties, system properties, environment variables, and more.

To view a specific property:

```
GET /actuator/env/server.port
```

## Loggers Endpoint

The `loggers` endpoint shows and allows modification of logger levels in your application.

To view all loggers:

```
GET /actuator/loggers
```

To view a specific logger:

```
GET /actuator/loggers/com.example.MyClass
```

To change a logger level:

```
POST /actuator/loggers/com.example.MyClass
Content-Type: application/json

{
  "configuredLevel": "DEBUG"
}
```

## Configuration Properties Endpoint

The `configprops` endpoint displays all `@ConfigurationProperties` in your application:

```
GET /actuator/configprops
```

Properties that may contain sensitive information are masked by default.

## Thread Dump Endpoint

The `threaddump` endpoint provides a thread dump of the application:

```
GET /actuator/threaddump
```

This is useful for diagnosing performance issues and detecting deadlocks.

## Shutdown Endpoint

The `shutdown` endpoint allows you to gracefully shut down the application. It's disabled by default for security reasons:

```yaml
management:
  endpoint:
    shutdown:
      enabled: true
```

To trigger shutdown:

```
POST /actuator/shutdown
```

> **WARNING**
> 
> The shutdown endpoint should be secured in production environments as it can terminate the application.