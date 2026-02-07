# Cloud Foundry Support

Spring Boot Actuator includes additional support when you deploy to a compatible Cloud Foundry instance. The `/cloudfoundryapplication` path provides an alternative secured route to all `@Endpoint` beans.

## Cloud Foundry Configuration

When running on Cloud Foundry, Spring Boot automatically configures:

- Cloud Foundry-specific health indicators
- Cloud Foundry application information
- Secure endpoint access through Cloud Foundry's security model

### Basic Configuration

```yaml
management:
  cloudfoundry:
    enabled: true
  endpoints:
    web:
      exposure:
        include: "*"
```

### Cloud Foundry Health

```java
@Component
public class CloudFoundryHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        // Cloud Foundry specific health checks
        return Health.up()
            .withDetail("cloud-foundry", "available")
            .withDetail("instance-index", System.getenv("CF_INSTANCE_INDEX"))
            .withDetail("application-id", System.getenv("VCAP_APPLICATION"))
            .build();
    }
}
```

## Best Practices

1. **Security**: Use Cloud Foundry's built-in security for actuator endpoints
2. **Service Binding**: Leverage VCAP_SERVICES for automatic configuration
3. **Health Checks**: Configure appropriate health endpoints for load balancer checks
4. **Metrics**: Export metrics to Cloud Foundry monitoring systems