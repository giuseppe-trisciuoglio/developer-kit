---
name: aws-rds-spring-boot-integration
description: Provides patterns to configure AWS RDS (Aurora, MySQL, PostgreSQL) with Spring Boot applications. Use when setting up datasources, connection pooling, security, and production-ready database configuration.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS RDS Spring Boot Integration

## Overview

Use this skill to connect Spring Boot 3.x services to AWS RDS or Aurora with secure configuration, resilient connection pooling, and operational readiness.

## When to Use

Use when you need to:
- Configure `spring.datasource` for Aurora MySQL or Aurora PostgreSQL.
- Tune HikariCP pool settings for production workloads.
- Enable Flyway/Liquibase migrations for schema evolution.
- Add SSL/TLS, failover-aware JDBC settings, and profile-based config.
- Integrate credential retrieval through AWS Secrets Manager.

## Instructions

1. Confirm runtime stack: Spring Boot 3.x, Java 17+, JDBC driver, and migration tool.
2. Start with a single datasource configuration and explicit JPA/Hibernate defaults.
3. Add HikariCP limits (`maximum-pool-size`, timeouts, max lifetime) sized for RDS class limits.
4. Externalize credentials via env vars or AWS Secrets Manager (never hardcode).
5. Enable SSL and use cluster endpoints for Aurora failover behavior.
6. Add health checks and migration validation in startup/CI.
7. For read-heavy systems, move to writer/reader split with separate datasources.

## Examples

### Example 1: Minimal Aurora datasource config

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${RDS_ENDPOINT}:5432/${RDS_DB}?sslmode=require
    username: ${RDS_USERNAME}
    password: ${RDS_PASSWORD}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
```

Use complete, runnable examples in:
- [Spring Boot + RDS examples](references/examples.md)
- [Advanced configuration](references/advanced-configuration.md)
- [Troubleshooting](references/troubleshooting.md)

## Best Practices

- Use constructor injection and explicit `@ConfigurationProperties` objects.
- Prefer `spring.jpa.hibernate.ddl-auto=validate` outside local development.
- Disable `open-in-view` for API services.
- Keep pool sizes conservative; monitor before scaling up.
- Test failover and connection recovery behavior before production cutover.

## Constraints and Warnings

- Do not commit credentials, endpoints, or account-specific secrets to source control.
- Avoid oversized pools; they can exhaust RDS connections and degrade throughput.
- Ensure security groups, subnets, and routing allow application-to-database traffic.
- SSL misconfiguration may cause intermittent handshake failures.
- Read replicas can lag; do not route write-after-read critical paths without consistency strategy.

## References

- [Examples](references/examples.md)
- [Advanced Configuration](references/advanced-configuration.md)
- [Troubleshooting](references/troubleshooting.md)
