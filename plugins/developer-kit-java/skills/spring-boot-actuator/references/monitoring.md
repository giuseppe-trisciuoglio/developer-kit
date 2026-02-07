# HTTP Monitoring and Management

If you are developing a web application, Spring Boot Actuator auto-configures all enabled endpoints to be exposed over HTTP. The default convention is to use the `id` of the endpoint with a prefix of `/actuator` as the URL path. For example, `health` is exposed as `/actuator/health`.

> **TIP**
> 
> Actuator is supported natively with Spring MVC, Spring WebFlux, and Jersey. If both Jersey and Spring MVC are available, Spring MVC is used.

> **NOTE**
> 
> Jackson is a required dependency in order to get the correct JSON responses as documented in the [API documentation](https://docs.spring.io/spring-boot/docs/current/actuator-api/htmlsingle/).

## Customizing the Management Endpoint Paths

Sometimes, it is useful to customize the prefix for the management endpoints. For example, your application might already use `/actuator` for another purpose. You can use the `management.endpoints.web.base-path` property to change the prefix for your management endpoint, as the following example shows:

```yaml
management:
  endpoints:
    web:
      base-path: "/manage"
```

The preceding example changes the endpoint from `/actuator/{id}` to `/manage/{id}` (for example, `/manage/info`).

> **NOTE**
> 
> Unless the management port has been configured to expose endpoints by using a different HTTP port, `management.endpoints.web.base-path` is relative to `server.servlet.context-path` (for servlet web applications) or `spring.webflux.base-path` (for reactive web applications). If `management.server.port` is configured, `management.endpoints.web.base-path` is relative to `management.server.base-path`.

If you want to map endpoints to a different path, you can use the `management.endpoints.web.path-mapping` property.

The following example remaps `/actuator/health` to `/healthcheck`:

```yaml
management:
  endpoints:
    web:
      base-path: "/"
      path-mapping:
        health: "healthcheck"
```

## Customizing the Management Server Port

Exposing management endpoints by using the default HTTP port is a sensible choice for cloud-based deployments. If, however, your application runs inside your own data center, you may prefer to expose endpoints by using a different HTTP port.

You can set the `management.server.port` property to change the HTTP port, as the following example shows:

```yaml
management:
  server:
    port: 8081
```

> **NOTE**
> 
> On Cloud Foundry, by default, applications receive requests only on port 8080 for both HTTP and TCP routing. If you want to use a custom management port on Cloud Foundry, you need to explicitly set up the application's routes to forward traffic to the custom port.

## Configuring Management-specific SSL

When configured to use a custom port, you can also configure the management server with its own SSL by using the various `management.server.ssl.*` properties. For example, doing so lets a management server be available over HTTP while the main application uses HTTPS, as the following property settings show:

```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: "classpath:store.jks"
    key-password: "secret"
management:
  server:
    port: 8080
    ssl:
      enabled: false
```

Alternatively, both the main server and the management server can use SSL but with different key stores, as follows:

```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: "classpath:main.jks"
    key-password: "secret"
management:
  server:
    port: 8080
    ssl:
      enabled: true
      key-store: "classpath:management.jks"
      key-password: "secret"
```

## Customizing the Management Server Address

You can customize the address on which the management endpoints are available by setting the `management.server.address` property. Doing so can be useful if you want to listen only on an internal or ops-facing network or to listen only for connections from `localhost`.

> **NOTE**
> 
> You can listen on a different address only when the port differs from the main server port.

The following example does not allow remote management connections:

```yaml
management:
  server:
    port: 8081
    address: "127.0.0.1"
```

## Disabling HTTP Endpoints

If you do not want to expose endpoints over HTTP, you can set the management port to `-1`, as the following example shows:

```yaml
management:
  server:
    port: -1
```

You can also achieve this by using the `management.endpoints.web.exposure.exclude` property, as the following example shows:

```yaml
management:
  endpoints:
    web:
      exposure:
        exclude: "*"
```

## Security Configuration for Management Endpoints

### Basic Authentication

To secure management endpoints with basic authentication:

```yaml
spring:
  security:
    user:
      name: admin
      password: secret
      roles: ACTUATOR

management:
  endpoints:
    web:
      exposure:
        include: "*"
  endpoint:
    health:
      show-details: when-authorized
```

### Custom Security Configuration

For more granular control, create a custom security configuration:

```java
@Configuration
public class ManagementSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> 
                requests
                    .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                    .anyRequest().hasRole("ACTUATOR")
            )
            .httpBasic(withDefaults())
            .build();
    }

    @Bean
    public SecurityFilterChain defaultSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(requests -> 
                requests.anyRequest().authenticated())
            .formLogin(withDefaults())
            .build();
    }
}
```

### Role-based Access Control

Different endpoints can require different roles:

```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorSecurityFilterChain(HttpSecurity http) throws Exception {
        return http
            .requestMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(requests -> 
                requests
                    .requestMatchers(EndpointRequest.to("health", "info")).permitAll()
                    .requestMatchers(EndpointRequest.to("metrics", "prometheus")).hasRole("METRICS_READER")
                    .requestMatchers(EndpointRequest.to("env", "configprops")).hasRole("CONFIG_READER")
                    .requestMatchers(EndpointRequest.to("shutdown")).hasRole("ADMIN")
                    .anyRequest().hasRole("ACTUATOR")
            )
            .httpBasic(withDefaults())
            .build();
    }
}
```

## CORS Configuration

To enable Cross-Origin Resource Sharing (CORS) for management endpoints:

```yaml
management:
  endpoints:
    web:
      cors:
        allowed-origins: "https://example.com"
        allowed-methods: "GET,POST"
        allowed-headers: "*"
        allow-credentials: true
```

## Custom Management Context Path

When using a separate management port, you can configure a custom context path:

```yaml
management:
  server:
    port: 9090
    base-path: "/admin"
  endpoints:
    web:
      base-path: "/actuator"
```

This configuration makes endpoints available at `http://localhost:9090/admin/actuator/*`.

## Load Balancer Configuration

When running behind a load balancer, configure the health endpoint appropriately:

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        liveness:
          include: "livenessState"
        readiness:
          include: "readinessState,db"
  endpoints:
    web:
      exposure:
        include: "health,info,metrics"
```

This allows the load balancer to check:
- Liveness: `GET /actuator/health/liveness`
- Readiness: `GET /actuator/health/readiness`

## Best Practices

1. **Separate Management Port**: Use a different port for management endpoints in production
2. **Secure Endpoints**: Always secure management endpoints in production environments
3. **Limit Exposure**: Only expose necessary endpoints (`include` specific endpoints rather than using `*`)
4. **Monitor Access**: Log and monitor access to management endpoints
5. **Network Security**: Use firewalls to restrict access to management ports
6. **SSL/TLS**: Use HTTPS for management endpoints in production
7. **Health Checks**: Configure appropriate health indicators for your infrastructure
8. **Graceful Shutdown**: Consider enabling graceful shutdown for production deployments

```yaml
# Production-ready configuration example
server:
  port: 8080
  shutdown: graceful

management:
  server:
    port: 8081
    address: "127.0.0.1"  # Only local access
    ssl:
      enabled: true
      key-store: "classpath:management.p12"
      key-store-password: "${KEYSTORE_PASSWORD}"
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
    enabled-by-default: false
  endpoint:
    health:
      enabled: true
      show-details: when-authorized
      probes:
        enabled: true
    info:
      enabled: true
    metrics:
      enabled: true
    prometheus:
      enabled: true

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```