# Spring Boot + AWS RDS Examples

## Example 1: Aurora PostgreSQL with Spring Data JPA and HikariCP

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-core</artifactId>
    </dependency>
</dependencies>
```

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://${RDS_ENDPOINT}:5432/${RDS_DB}?sslmode=require
    username: ${RDS_USERNAME}
    password: ${RDS_PASSWORD}
    driver-class-name: org.postgresql.Driver
    hikari:
      pool-name: RdsPool
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
      max-lifetime: 1200000
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
  flyway:
    enabled: true
    validate-on-migrate: true
```

## Example 2: Typed datasource properties + DataSource bean

```java
package com.example.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
@EnableConfigurationProperties(RdsDataSourceProperties.class)
public class DataSourceConfig {

    @Bean
    DataSource dataSource(RdsDataSourceProperties properties) {
        return DataSourceBuilder.create()
                .type(HikariDataSource.class)
                .url(properties.url())
                .username(properties.username())
                .password(properties.password())
                .driverClassName(properties.driverClassName())
                .build();
    }
}
```

```java
package com.example.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.rds")
public record RdsDataSourceProperties(
        String url,
        String username,
        String password,
        String driverClassName
) {
}
```

```yaml
# application.yml
app:
  rds:
    url: jdbc:mysql://${RDS_ENDPOINT}:3306/${RDS_DB}?useSSL=true&requireSSL=true
    username: ${RDS_USERNAME}
    password: ${RDS_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
```

## Example 3: Secrets Manager-backed datasource credentials

```java
package com.example.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest;

import java.util.Map;

@Configuration
public class SecretsManagerConfig {

    @Bean
    SecretsManagerClient secretsManagerClient(@Value("${aws.region}") String region) {
        return SecretsManagerClient.builder().region(Region.of(region)).build();
    }

    @Bean
    Map<String, String> rdsSecret(
            SecretsManagerClient client,
            ObjectMapper objectMapper,
            @Value("${aws.secretsmanager.rds-secret-id}") String secretId
    ) {
        try {
            String secret = client.getSecretValue(GetSecretValueRequest.builder().secretId(secretId).build())
                    .secretString();
            return objectMapper.readValue(secret, objectMapper.getTypeFactory()
                    .constructMapType(Map.class, String.class, String.class));
        } catch (Exception ex) {
            throw new IllegalStateException("Unable to load RDS secret", ex);
        }
    }
}
```

## Example 4: Health check endpoint for DB connectivity

```java
package com.example.health;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
public class DatabaseHealthController {

    private final DataSource dataSource;

    public DatabaseHealthController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @GetMapping("/db")
    public ResponseEntity<Map<String, Object>> checkDatabase() {
        Map<String, Object> body = new HashMap<>();
        try (Connection connection = dataSource.getConnection()) {
            body.put("status", "UP");
            body.put("database", connection.getCatalog());
            return ResponseEntity.ok(body);
        } catch (Exception ex) {
            body.put("status", "DOWN");
            body.put("error", ex.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body);
        }
    }
}
```

## Example 5: Aurora writer/reader split properties

```yaml
# application.yml
spring:
  datasource:
    writer:
      jdbc-url: jdbc:postgresql://${AURORA_WRITER_ENDPOINT}:5432/${RDS_DB}?sslmode=require
      username: ${RDS_USERNAME}
      password: ${RDS_PASSWORD}
      driver-class-name: org.postgresql.Driver
      maximum-pool-size: 12
    reader:
      jdbc-url: jdbc:postgresql://${AURORA_READER_ENDPOINT}:5432/${RDS_DB}?sslmode=require
      username: ${RDS_USERNAME}
      password: ${RDS_PASSWORD}
      driver-class-name: org.postgresql.Driver
      maximum-pool-size: 24
```

Use `references/advanced-configuration.md` for full multi-datasource bean wiring.
