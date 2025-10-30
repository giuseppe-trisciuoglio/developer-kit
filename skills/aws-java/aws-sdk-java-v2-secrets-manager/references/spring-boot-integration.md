# AWS Secrets Manager Spring Boot Integration

## Overview
Integrate AWS Secrets Manager with Spring Boot applications using the caching library for optimal performance and security.

## Dependencies

### Required Dependencies
```xml
<!-- AWS Secrets Manager -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>secretsmanager</artifactId>
</dependency>

<!-- AWS Secrets Manager Caching -->
<dependency>
    <groupId>com.amazonaws.secretsmanager</groupId>
    <artifactId>aws-secretsmanager-caching-java</artifactId>
    <version>2.0.0</version> // Use the latest version compatible with sdk v2
</dependency>

<!-- Spring Boot Starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>

<!-- Jackson for JSON processing -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

<!-- Connection Pooling -->
<dependency>
    <groupId>com.zaxxer</groupId>
    <artifactId>HikariCP</artifactId>
</dependency>
```

## Configuration Properties

### application.yml
```yaml
spring:
  application:
    name: aws-secrets-manager-app
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: ${db.username}
    password: ${db.password}
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5

aws:
  secrets:
    region: us-east-1
    # Secret names for different environments
    database-credentials: prod/database/credentials
    api-keys: prod/external-api/keys
    redis-config: prod/redis/config

app:
  external-api:
    secret-name: prod/external/credentials
    base-url: https://api.example.com
```

## Core Components

### SecretsManager Configuration
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import com.amazonaws.secretsmanager.caching.SecretCacheConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;

@Configuration
public class SecretsManagerConfiguration {

    @Value("${aws.secrets.region}")
    private String region;

    @Bean
    public SecretsManagerClient secretsManagerClient() {
        return SecretsManagerClient.builder()
            .region(Region.of(region))
            .build();
    }

    @Bean
    public SecretCache secretCache(SecretsManagerClient secretsClient) {
        SecretCacheConfiguration config = SecretCacheConfiguration.builder()
            .maxCacheSize(100)
            .cacheItemTTL(3600000) // 1 hour
            .build();

        return new SecretCache(secretsClient, config);
    }
}
```

### Secrets Service
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import java.util.Map;

@Service
public class SecretsService {

    private final SecretCache secretCache;
    private final ObjectMapper objectMapper;

    public SecretsService(SecretCache secretCache, ObjectMapper objectMapper) {
        this.secretCache = secretCache;
        this.objectMapper = objectMapper;
    }

    /**
     * Get secret as string
     */
    public String getSecret(String secretName) {
        try {
            return secretCache.getSecretString(secretName);
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve secret: " + secretName, e);
        }
    }

    /**
     * Get secret as object of specified type
     */
    public <T> T getSecretAsObject(String secretName, Class<T> type) {
        try {
            String secretJson = secretCache.getSecretString(secretName);
            return objectMapper.readValue(secretJson, type);
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse secret: " + secretName, e);
        }
    }

    /**
     * Get secret as Map
     */
    public Map<String, String> getSecretAsMap(String secretName) {
        try {
            String secretJson = secretCache.getSecretString(secretName);
            return objectMapper.readValue(secretJson,
                new TypeReference<Map<String, String>>() {});
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse secret map: " + secretName, e);
        }
    }

    /**
     * Get secret with fallback
     */
    public String getSecretWithFallback(String secretName, String defaultValue) {
        try {
            String secret = secretCache.getSecretString(secretName);
            return secret != null ? secret : defaultValue;
        } catch (Exception e) {
            return defaultValue;
        }
    }
}
```

## Database Configuration Integration

### Dynamic DataSource Configuration
```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import javax.sql.DataSource;

@Configuration
public class DatabaseConfiguration {

    private final SecretsService secretsService;

    @Value("${aws.secrets.database-credentials}")
    private String dbSecretName;

    public DatabaseConfiguration(SecretsService secretsService) {
        this.secretsService = secretsService;
    }

    @Bean
    public DataSource dataSource() {
        Map<String, String> credentials = secretsService.getSecretAsMap(dbSecretName);

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(credentials.get("url"));
        config.setUsername(credentials.get("username"));
        config.setPassword(credentials.get("password"));
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(5);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);
        config.setLeakDetectionThreshold(15000);

        return new HikariDataSource(config);
    }
}
```

### Configuration Properties with Secrets
```java
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private final SecretsService secretsService;

    @Value("${app.external-api.secret-name}")
    private String apiSecretName;

    public AppProperties(SecretsService secretsService) {
        this.secretsService = secretsService;
    }

    private String apiKey;

    public String getApiKey() {
        if (apiKey == null) {
            apiKey = secretsService.getSecret(apiSecretName);
        }
        return apiKey;
    }

    // Additional application properties
    private String externalApiBaseUrl;

    public String getExternalApiBaseUrl() {
        return externalApiBaseUrl;
    }

    public void setExternalApiBaseUrl(String externalApiBaseUrl) {
        this.externalApiBaseUrl = externalApiBaseUrl;
    }
}
```

## Property Source Integration

### Custom Property Source
```java
import org.springframework.core.env.Environment;
import org.springframework.core.env.PropertySource;
import org.springframework.stereotype.Component;
import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

@Component
public class SecretsManagerPropertySource extends PropertySource<SecretsService> {

    public static final String SECRETS_MANAGER_PROPERTY_SOURCE_NAME = "secretsManagerPropertySource";

    private final SecretsService secretsService;
    private final Environment environment;

    public SecretsManagerPropertySource(SecretsService secretsService, Environment environment) {
        super(SECRETS_MANAGER_PROPERTY_SOURCE_NAME, secretsService);
        this.secretsService = secretsService;
        this.environment = environment;
    }

    @PostConstruct
    public void loadSecrets() {
        // Load secrets specified in application.yml
        String secretPrefix = "aws.secrets.";
        environment.getPropertyNames().forEach(propertyName -> {
            if (propertyName.startsWith(secretPrefix)) {
                String secretName = environment.getProperty(propertyName);
                String secretValue = secretsService.getSecret(secretName);
                if (secretValue != null) {
                    // Add to property source (note: this is simplified)
                    // In practice, you'd need to work with PropertySources
                }
            }
        });
    }

    @Override
    public Object getProperty(String name) {
        if (name.startsWith("aws.secret.")) {
            String secretName = name.substring("aws.secret.".length());
            return secretsService.getSecret(secretName);
        }
        return null;
    }
}
```

## API Integration

### REST Client with Secrets
```java
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ExternalApiClient {

    private final SecretsService secretsService;
    private final RestTemplate restTemplate;
    private final AppProperties appProperties;

    public ExternalApiClient(SecretsService secretsService,
                           RestTemplate restTemplate,
                           AppProperties appProperties) {
        this.secretsService = secretsService;
        this.restTemplate = restTemplate;
        this.appProperties = appProperties;
    }

    public String callExternalApi(String endpoint) {
        Map<String, String> apiCredentials = secretsService.getSecretAsMap(
            appProperties.getExternalApiSecretName());

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + apiCredentials.get("api_token"));
        headers.set("X-API-Key", apiCredentials.get("api_key"));
        headers.set("Content-Type", "application/json");

        HttpEntity<String> entity = new HttpEntity<>(headers);

        ResponseEntity<String> response = restTemplate.exchange(
            endpoint,
            HttpMethod.GET,
            entity,
            String.class);

        return response.getBody();
    }
}
```

### Configuration for REST Template
```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class RestTemplateConfiguration {

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

## Security Configuration

### Security Setup
```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/secrets/**").hasRole("ADMIN")
                .anyRequest().permitAll()
            )
            .httpBasic()
            .and()
            .csrf().disable();

        return http.build();
    }
}
```

## Testing Configuration

### Test Configuration
```java
import com.amazonaws.secretsmanager.caching.SecretCache;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.mock.env.MockEnvironment;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueResponse;

import static org.mockito.Mockito.*;

@TestConfiguration
public class TestSecretsConfiguration {

    @Bean
    @Primary
    public SecretsManagerClient secretsManagerClient() {
        SecretsManagerClient mockClient = mock(SecretsManagerClient.class);

        // Mock successful secret retrieval
        when(mockClient.getSecretValue(any()))
            .thenReturn(GetSecretValueResponse.builder()
                .secretString("{\"username\":\"test\",\"password\":\"testpass\"}")
                .build());

        return mockClient;
    }

    @Bean
    @Primary
    public SecretCache secretCache(SecretsManagerClient mockClient) {
        SecretCache mockCache = mock(SecretCache.class);
        when(mockCache.getSecretString(anyString()))
            .thenReturn("{\"username\":\"test\",\"password\":\"testpass\"}");
        return mockCache;
    }

    @Bean
    public MockEnvironment mockEnvironment() {
        MockEnvironment env = new MockEnvironment();
        env.setProperty("aws.secrets.region", "us-east-1");
        env.setProperty("aws.secrets.database-credentials", "test-db-credentials");
        return env;
    }
}
```

### Unit Tests
```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class SecretsServiceTest {

    @Mock
    private SecretCache secretCache;

    @InjectMocks
    private SecretsService secretsService;

    @Test
    void shouldGetSecret() {
        String secretName = "test-secret";
        String expectedValue = "secret-value";

        when(secretCache.getSecretString(secretName))
            .thenReturn(expectedValue);

        String result = secretsService.getSecret(secretName);

        assertEquals(expectedValue, result);
        verify(secretCache).getSecretString(secretName);
    }

    @Test
    void shouldGetSecretAsMap() throws Exception {
        String secretName = "test-secret";
        String secretJson = "{\"key\":\"value\"}";
        Map<String, String> expectedMap = Map.of("key", "value");

        when(secretCache.getSecretString(secretName))
            .thenReturn(secretJson);

        Map<String, String> result = secretsService.getSecretAsMap(secretName);

        assertEquals(expectedMap, result);
    }
}
```

## Best Practices

1. **Environment-Specific Configuration**:
   - Use different secret names for development, staging, and production
   - Implement proper environment variable management
   - Use Spring profiles for environment-specific configurations

2. **Security Considerations**:
   - Never log secret values
   - Use appropriate IAM roles and policies
   - Enable encryption in transit and at rest
   - Implement proper access controls

3. **Performance Optimization**:
   - Use caching for frequently accessed secrets
   - Configure appropriate TTL values
   - Monitor cache hit rates and adjust accordingly
   - Use connection pooling for database connections

4. **Error Handling**:
   - Implement fallback mechanisms for critical secrets
   - Handle partial secret retrieval gracefully
   - Provide meaningful error messages without exposing sensitive information
   - Implement circuit breakers for external API calls

5. **Monitoring and Logging**:
   - Monitor secret retrieval performance
   - Track cache hit/miss ratios
   - Log secret access patterns (without values)
   - Set up alerts for abnormal secret access patterns