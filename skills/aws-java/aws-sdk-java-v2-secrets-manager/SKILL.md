---
name: aws-sdk-java-v2-secrets-manager
description: AWS Secrets Manager patterns using AWS SDK for Java 2.x. Use when storing/retrieving secrets (passwords, API keys, tokens), rotating secrets automatically, managing database credentials, or integrating secret management into Spring Boot applications.
---

# AWS SDK for Java 2.x - AWS Secrets Manager

## When to Use

Use this skill when:
- Storing and retrieving application secrets
- Managing database credentials securely
- Rotating secrets automatically
- Storing API keys and tokens
- Implementing secure configuration management
- Managing multi-region secrets
- Integrating with Spring Boot configuration
- Implementing secret caching for performance

## Dependencies

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>secretsmanager</artifactId>
</dependency>

<!-- For secret caching (recommended) -->
<dependency>
    <groupId>com.amazonaws.secretsmanager</groupId>
    <artifactId>aws-secretsmanager-caching-java</artifactId>
    <version>2.0.2</version>
</dependency>
```

## Client Setup

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;

SecretsManagerClient secretsClient = SecretsManagerClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

## Secret Operations

### Create Secret

```java
import software.amazon.awssdk.services.secretsmanager.model.*;

public String createSecret(SecretsManagerClient secretsClient, 
                           String secretName, 
                           String secretValue) {
    try {
        CreateSecretRequest request = CreateSecretRequest.builder()
            .name(secretName)
            .secretString(secretValue)
            .description("Application secret")
            .build();
        
        CreateSecretResponse response = secretsClient.createSecret(request);
        
        System.out.println("Secret created: " + response.arn());
        return response.arn();
        
    } catch (SecretsManagerException e) {
        System.err.println("Error creating secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Create Secret with JSON

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;

public String createJsonSecret(SecretsManagerClient secretsClient, 
                               String secretName,
                               Map<String, String> secretData) {
    try {
        ObjectMapper objectMapper = new ObjectMapper();
        String secretJson = objectMapper.writeValueAsString(secretData);
        
        CreateSecretRequest request = CreateSecretRequest.builder()
            .name(secretName)
            .secretString(secretJson)
            .build();
        
        CreateSecretResponse response = secretsClient.createSecret(request);
        
        return response.arn();
        
    } catch (Exception e) {
        System.err.println("Error creating JSON secret: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Create Secret with KMS Encryption

```java
public String createEncryptedSecret(SecretsManagerClient secretsClient, 
                                    String secretName, 
                                    String secretValue,
                                    String kmsKeyId) {
    CreateSecretRequest request = CreateSecretRequest.builder()
        .name(secretName)
        .secretString(secretValue)
        .kmsKeyId(kmsKeyId)
        .build();
    
    CreateSecretResponse response = secretsClient.createSecret(request);
    
    return response.arn();
}
```

### Get Secret Value

```java
public String getSecretValue(SecretsManagerClient secretsClient, String secretName) {
    try {
        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretName)
            .build();
        
        GetSecretValueResponse response = secretsClient.getSecretValue(request);
        
        return response.secretString();
        
    } catch (SecretsManagerException e) {
        System.err.println("Error getting secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Get Secret with Specific Version

```java
public String getSecretVersion(SecretsManagerClient secretsClient, 
                               String secretName, 
                               String versionId) {
    GetSecretValueRequest request = GetSecretValueRequest.builder()
        .secretId(secretName)
        .versionId(versionId)
        .build();
    
    GetSecretValueResponse response = secretsClient.getSecretValue(request);
    
    return response.secretString();
}
```

### Get Secret with Version Stage

```java
public String getSecretByStage(SecretsManagerClient secretsClient, 
                               String secretName, 
                               String versionStage) {
    GetSecretValueRequest request = GetSecretValueRequest.builder()
        .secretId(secretName)
        .versionStage(versionStage)
        .build();
    
    GetSecretValueResponse response = secretsClient.getSecretValue(request);
    
    return response.secretString();
}
```

### Parse JSON Secret

```java
public Map<String, String> getJsonSecret(SecretsManagerClient secretsClient, 
                                         String secretName) {
    try {
        String secretJson = getSecretValue(secretsClient, secretName);
        
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(secretJson, 
            new TypeReference<Map<String, String>>() {});
        
    } catch (Exception e) {
        System.err.println("Error parsing JSON secret: " + e.getMessage());
        throw new RuntimeException(e);
    }
}
```

### Update Secret

```java
public void updateSecret(SecretsManagerClient secretsClient, 
                         String secretName, 
                         String newSecretValue) {
    try {
        UpdateSecretRequest request = UpdateSecretRequest.builder()
            .secretId(secretName)
            .secretString(newSecretValue)
            .build();
        
        UpdateSecretResponse response = secretsClient.updateSecret(request);
        
        System.out.println("Secret updated: " + response.arn());
        System.out.println("Version ID: " + response.versionId());
        
    } catch (SecretsManagerException e) {
        System.err.println("Error updating secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Delete Secret

```java
public void deleteSecret(SecretsManagerClient secretsClient, 
                         String secretName, 
                         int recoveryWindowDays) {
    try {
        DeleteSecretRequest request = DeleteSecretRequest.builder()
            .secretId(secretName)
            .recoveryWindowInDays((long) recoveryWindowDays)
            .build();
        
        DeleteSecretResponse response = secretsClient.deleteSecret(request);
        
        System.out.println("Secret scheduled for deletion");
        System.out.println("Deletion date: " + response.deletionDate());
        
    } catch (SecretsManagerException e) {
        System.err.println("Error deleting secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Delete Secret Immediately

```java
public void deleteSecretImmediately(SecretsManagerClient secretsClient, String secretName) {
    DeleteSecretRequest request = DeleteSecretRequest.builder()
        .secretId(secretName)
        .forceDeleteWithoutRecovery(true)
        .build();
    
    secretsClient.deleteSecret(request);
    
    System.out.println("Secret deleted immediately");
}
```

### Restore Secret

```java
public void restoreSecret(SecretsManagerClient secretsClient, String secretName) {
    try {
        RestoreSecretRequest request = RestoreSecretRequest.builder()
            .secretId(secretName)
            .build();
        
        RestoreSecretResponse response = secretsClient.restoreSecret(request);
        
        System.out.println("Secret restored: " + response.arn());
        
    } catch (SecretsManagerException e) {
        System.err.println("Error restoring secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Secret Rotation

### Configure Rotation

```java
public void enableRotation(SecretsManagerClient secretsClient, 
                           String secretName,
                           String lambdaArn,
                           int rotationDays) {
    try {
        RotateSecretRequest request = RotateSecretRequest.builder()
            .secretId(secretName)
            .rotationLambdaArn(lambdaArn)
            .rotationRules(RotationRulesType.builder()
                .automaticallyAfterDays((long) rotationDays)
                .build())
            .build();
        
        RotateSecretResponse response = secretsClient.rotateSecret(request);
        
        System.out.println("Rotation configured");
        System.out.println("Version ID: " + response.versionId());
        
    } catch (SecretsManagerException e) {
        System.err.println("Error configuring rotation: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Rotate Secret Immediately

```java
public void rotateSecretNow(SecretsManagerClient secretsClient, String secretName) {
    RotateSecretRequest request = RotateSecretRequest.builder()
        .secretId(secretName)
        .build();
    
    RotateSecretResponse response = secretsClient.rotateSecret(request);
    
    System.out.println("Secret rotation initiated");
    System.out.println("New version ID: " + response.versionId());
}
```

## List and Describe Secrets

### List Secrets

```java
import java.util.List;

public List<SecretListEntry> listSecrets(SecretsManagerClient secretsClient) {
    try {
        ListSecretsRequest request = ListSecretsRequest.builder()
            .maxResults(100)
            .build();
        
        ListSecretsResponse response = secretsClient.listSecrets(request);
        
        response.secretList().forEach(secret -> {
            System.out.println("Name: " + secret.name());
            System.out.println("ARN: " + secret.arn());
            System.out.println("Last Changed: " + secret.lastChangedDate());
            System.out.println();
        });
        
        return response.secretList();
        
    } catch (SecretsManagerException e) {
        System.err.println("Error listing secrets: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Describe Secret

```java
public DescribeSecretResponse describeSecret(SecretsManagerClient secretsClient, 
                                              String secretName) {
    try {
        DescribeSecretRequest request = DescribeSecretRequest.builder()
            .secretId(secretName)
            .build();
        
        DescribeSecretResponse response = secretsClient.describeSecret(request);
        
        System.out.println("Name: " + response.name());
        System.out.println("ARN: " + response.arn());
        System.out.println("Description: " + response.description());
        System.out.println("Rotation enabled: " + response.rotationEnabled());
        System.out.println("Last rotated: " + response.lastRotatedDate());
        
        return response;
        
    } catch (SecretsManagerException e) {
        System.err.println("Error describing secret: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Secret Caching

### Setup Cache

```java
import com.amazonaws.secretsmanager.caching.SecretCache;

public class SecretCacheManager {
    
    private final SecretCache secretCache;
    
    public SecretCacheManager(SecretsManagerClient secretsClient) {
        this.secretCache = new SecretCache(secretsClient);
    }
    
    public String getCachedSecret(String secretName) {
        try {
            return secretCache.getSecretString(secretName);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get cached secret", e);
        }
    }
}
```

### Custom Cache Configuration

```java
import com.amazonaws.secretsmanager.caching.SecretCacheConfiguration;

public SecretCache createConfiguredCache(SecretsManagerClient secretsClient) {
    SecretCacheConfiguration config = new SecretCacheConfiguration()
        .withMaxCacheSize(1000)
        .withCacheItemTTL(3600000); // 1 hour in milliseconds
    
    return new SecretCache(secretsClient, config);
}
```

## Spring Boot Integration

### Configuration

```java
@Configuration
public class SecretsManagerConfiguration {
    
    @Bean
    public SecretsManagerClient secretsManagerClient() {
        return SecretsManagerClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
    
    @Bean
    public SecretCache secretCache(SecretsManagerClient secretsClient) {
        SecretCacheConfiguration config = new SecretCacheConfiguration()
            .withMaxCacheSize(100)
            .withCacheItemTTL(3600000);
        
        return new SecretCache(secretsClient, config);
    }
}
```

### Secrets Service

```java
@Service
public class SecretsService {
    
    private final SecretCache secretCache;
    private final ObjectMapper objectMapper;
    
    public SecretsService(SecretCache secretCache, ObjectMapper objectMapper) {
        this.secretCache = secretCache;
        this.objectMapper = objectMapper;
    }
    
    public String getSecret(String secretName) {
        try {
            return secretCache.getSecretString(secretName);
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve secret: " + secretName, e);
        }
    }
    
    public <T> T getSecretAsObject(String secretName, Class<T> type) {
        try {
            String secretJson = secretCache.getSecretString(secretName);
            return objectMapper.readValue(secretJson, type);
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse secret: " + secretName, e);
        }
    }
    
    public Map<String, String> getSecretAsMap(String secretName) {
        try {
            String secretJson = secretCache.getSecretString(secretName);
            return objectMapper.readValue(secretJson, 
                new TypeReference<Map<String, String>>() {});
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse secret map: " + secretName, e);
        }
    }
}
```

### Database Configuration from Secrets

```java
@Configuration
public class DatabaseConfiguration {
    
    private final SecretsService secretsService;
    
    @Value("${aws.secrets.database-credentials}")
    private String secretName;
    
    public DatabaseConfiguration(SecretsService secretsService) {
        this.secretsService = secretsService;
    }
    
    @Bean
    public DataSource dataSource() {
        Map<String, String> credentials = secretsService.getSecretAsMap(secretName);
        
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(credentials.get("url"));
        config.setUsername(credentials.get("username"));
        config.setPassword(credentials.get("password"));
        config.setMaximumPoolSize(10);
        
        return new HikariDataSource(config);
    }
}
```

### Property Source Integration

```java
@Component
public class SecretsManagerPropertySource extends PropertySource<SecretsService> {
    
    public static final String SECRETS_MANAGER_PROPERTY_SOURCE_NAME = 
        "secretsManagerPropertySource";
    
    public SecretsManagerPropertySource(SecretsService secretsService) {
        super(SECRETS_MANAGER_PROPERTY_SOURCE_NAME, secretsService);
    }
    
    @Override
    public Object getProperty(String name) {
        if (name.startsWith("aws.secret.")) {
            String secretName = name.substring("aws.secret.".length());
            try {
                return source.getSecret(secretName);
            } catch (Exception e) {
                return null;
            }
        }
        return null;
    }
}
```

### Configuration Properties with Secrets

```java
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    
    private final SecretsService secretsService;
    
    @Value("${app.api-key-secret-name}")
    private String apiKeySecretName;
    
    public AppProperties(SecretsService secretsService) {
        this.secretsService = secretsService;
    }
    
    public String getApiKey() {
        return secretsService.getSecret(apiKeySecretName);
    }
}
```

### API Client with Secrets

```java
@Service
public class ExternalApiClient {
    
    private final SecretsService secretsService;
    private final RestTemplate restTemplate;
    
    @Value("${external-api.secret-name}")
    private String apiSecretName;
    
    public ExternalApiClient(SecretsService secretsService, RestTemplate restTemplate) {
        this.secretsService = secretsService;
        this.restTemplate = restTemplate;
    }
    
    public String callExternalApi(String endpoint) {
        Map<String, String> apiCredentials = secretsService.getSecretAsMap(apiSecretName);
        
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + apiCredentials.get("api_token"));
        headers.set("X-API-Key", apiCredentials.get("api_key"));
        
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

## Common Secret Structures

### Database Credentials

```json
{
  "engine": "postgres",
  "host": "mydb.us-east-1.rds.amazonaws.com",
  "port": 5432,
  "username": "admin",
  "password": "MySecurePassword123!",
  "dbname": "mydatabase",
  "url": "jdbc:postgresql://mydb.us-east-1.rds.amazonaws.com:5432/mydatabase"
}
```

### API Keys

```json
{
  "api_key": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
  "api_secret": "MySecretKey123!",
  "api_token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### OAuth Credentials

```json
{
  "client_id": "my-client-id",
  "client_secret": "my-client-secret",
  "redirect_uri": "https://myapp.com/callback",
  "scopes": "read write"
}
```

## Best Practices

1. **Secret Management**:
   - Use descriptive secret names
   - Add tags for organization
   - Use secret versioning
   - Implement automatic rotation

2. **Caching**:
   - Always use caching in production
   - Configure appropriate TTL
   - Handle cache misses gracefully
   - Monitor cache hit rates

3. **Security**:
   - Never log secret values
   - Use KMS encryption
   - Implement least privilege IAM policies
   - Enable CloudTrail logging

4. **Performance**:
   - Cache secrets client-side
   - Reuse client instances
   - Batch secret retrievals when possible
   - Monitor API throttling

5. **Error Handling**:
   - Implement retry logic
   - Handle deleted secrets
   - Provide fallback mechanisms
   - Log errors without exposing secrets

## Testing

### Unit Test with Mocked Client

```java
@ExtendWith(MockitoExtension.class)
class SecretsServiceTest {
    
    @Mock
    private SecretCache secretCache;
    
    @Mock
    private ObjectMapper objectMapper;
    
    @InjectMocks
    private SecretsService secretsService;
    
    @Test
    void shouldGetSecret() {
        String secretName = "test-secret";
        String expectedValue = "secret-value";
        
        when(secretCache.getSecretString(secretName))
            .thenReturn(expectedValue);
        
        String result = secretsService.getSecret(secretName);
        
        assertThat(result).isEqualTo(expectedValue);
        verify(secretCache).getSecretString(secretName);
    }
    
    @Test
    void shouldGetSecretAsMap() throws Exception {
        String secretName = "test-secret";
        String secretJson = "{\"key\":\"value\"}";
        Map<String, String> expectedMap = Map.of("key", "value");
        
        when(secretCache.getSecretString(secretName))
            .thenReturn(secretJson);
        when(objectMapper.readValue(eq(secretJson), any(TypeReference.class)))
            .thenReturn(expectedMap);
        
        Map<String, String> result = secretsService.getSecretAsMap(secretName);
        
        assertThat(result).isEqualTo(expectedMap);
    }
}
```

## Application Properties

```yaml
aws:
  secrets:
    database-credentials: prod/database/credentials
    api-keys: prod/external-api/keys
    
app:
  api-key-secret-name: prod/app/api-key
  
external-api:
  secret-name: prod/external/credentials
```

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns
- @aws-sdk-java-v2-kms - Key management and encryption
- @spring-boot-dependency-injection - Spring DI patterns

## References

- [Secrets Manager Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/secrets-manager)
- [Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/)
- [Secret Caching Library](https://github.com/aws/aws-secretsmanager-caching-java)
- [Secrets Manager API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/secretsmanager/package-summary.html)
