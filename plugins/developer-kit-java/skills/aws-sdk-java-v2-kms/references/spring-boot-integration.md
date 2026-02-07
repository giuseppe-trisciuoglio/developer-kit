# Spring Boot Integration with AWS KMS

## Configuration

### Basic Configuration

```java
@Configuration
public class KmsConfiguration {

    @Bean
    public KmsClient kmsClient() {
        return KmsClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public KmsAsyncClient kmsAsyncClient() {
        return KmsAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### Configuration with Custom Settings

```java
@Configuration
@ConfigurationProperties(prefix = "aws.kms")
public class KmsAdvancedConfiguration {

    private Region region = Region.US_EAST_1;
    private String endpoint;
    private Duration timeout = Duration.ofSeconds(10);
    private String accessKeyId;
    private String secretAccessKey;

    @Bean
    public KmsClient kmsClient() {
        KmsClientBuilder builder = KmsClient.builder()
            .region(region)
            .overrideConfiguration(c -> c.retryPolicy(RetryPolicy.builder()
                .numRetries(3)
                .build()));

        if (endpoint != null) {
            builder.endpointOverride(URI.create(endpoint));
        }

        // Add credentials if provided
        if (accessKeyId != null && secretAccessKey != null) {
            builder.credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(accessKeyId, secretAccessKey)));
        }

        return builder.build();
    }

    // Getters and Setters
    public Region getRegion() { return region; }
    public void setRegion(Region region) { this.region = region; }
    public String getEndpoint() { return endpoint; }
    public void setEndpoint(String endpoint) { this.endpoint = endpoint; }
    public Duration getTimeout() { return timeout; }
    public void setTimeout(Duration timeout) { this.timeout = timeout; }
    public String getAccessKeyId() { return accessKeyId; }
    public void setAccessKeyId(String accessKeyId) { this.accessKeyId = accessKeyId; }
    public String getSecretAccessKey() { return secretAccessKey; }
    public void setSecretAccessKey(String secretAccessKey) { this.secretAccessKey = secretAccessKey; }
}
```

### Application Properties

```properties
# AWS KMS Configuration
aws.kms.region=us-east-1
aws.kms.endpoint=
aws.kms.timeout=10s
aws.kms.access-key-id=
aws.kms.secret-access-key=

# KMS Key Configuration
kms.encryption-key-id=alias/your-encryption-key
kms.signing-key-id=alias/your-signing-key
```

## Encryption Service

### Basic Encryption Service

```java
@Service
public class KmsEncryptionService {

    private final KmsClient kmsClient;

    @Value("${kms.encryption-key-id}")
    private String keyId;

    public KmsEncryptionService(KmsClient kmsClient) {
        this.kmsClient = kmsClient;
    }

    public String encrypt(String plaintext) {
        try {
            EncryptRequest request = EncryptRequest.builder()
                .keyId(keyId)
                .plaintext(SdkBytes.fromString(plaintext, StandardCharsets.UTF_8))
                .build();

            EncryptResponse response = kmsClient.encrypt(request);

            // Return Base64-encoded ciphertext
            return Base64.getEncoder()
                .encodeToString(response.ciphertextBlob().asByteArray());

        } catch (KmsException e) {
            throw new RuntimeException("Encryption failed", e);
        }
    }

    public String decrypt(String ciphertextBase64) {
        try {
            byte[] ciphertext = Base64.getDecoder().decode(ciphertextBase64);

            DecryptRequest request = DecryptRequest.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
                .build();

            DecryptResponse response = kmsClient.decrypt(request);

            return response.plaintext().asString(StandardCharsets.UTF_8);

        } catch (KmsException e) {
            throw new RuntimeException("Decryption failed", e);
        }
    }
}
```

### Secure Data Repository

```java
@Repository
public class SecureDataRepository {

    private final KmsEncryptionService encryptionService;
    private final JdbcTemplate jdbcTemplate;

    public SecureDataRepository(KmsEncryptionService encryptionService,
                                JdbcTemplate jdbcTemplate) {
        this.encryptionService = encryptionService;
        this.jdbcTemplate = jdbcTemplate;
    }

    public void saveSecureData(String id, String sensitiveData) {
        String encryptedData = encryptionService.encrypt(sensitiveData);

        jdbcTemplate.update(
            "INSERT INTO secure_data (id, encrypted_value) VALUES (?, ?)",
            id, encryptedData);
    }

    public String getSecureData(String id) {
        String encryptedData = jdbcTemplate.queryForObject(
            "SELECT encrypted_value FROM secure_data WHERE id = ?",
            String.class, id);

        return encryptionService.decrypt(encryptedData);
    }
}
```

### Advanced Envelope Encryption Service

```java
@Service
public class EnvelopeEncryptionService {

    private final KmsClient kmsClient;

    @Value("${kms.master-key-id}")
    private String masterKeyId;

    private final Cache<String, DataKeyPair> keyCache =
        Caffeine.newBuilder()
            .expireAfterWrite(1, TimeUnit.HOURS)
            .maximumSize(100)
            .build();

    public EnvelopeEncryptionService(KmsClient kmsClient) {
        this.kmsClient = kmsClient;
    }

    public EncryptedEnvelope encryptLargeData(byte[] data) {
        // Check cache for existing key
        DataKeyPair dataKeyPair = keyCache.getIfPresent(masterKeyId);

        if (dataKeyPair == null) {
            // Generate new data key
            GenerateDataKeyResponse dataKeyResponse = kmsClient.generateDataKey(
                GenerateDataKeyRequest.builder()
                    .keyId(masterKeyId)
                    .keySpec(DataKeySpec.AES_256)
                    .build());

            dataKeyPair = new DataKeyPair(
                dataKeyResponse.plaintext().asByteArray(),
                dataKeyResponse.ciphertextBlob().asByteArray());

            // Cache the encrypted key (not plaintext)
            keyCache.put(masterKeyId, dataKeyPair);
        }

        try {
            // Encrypt data with plaintext data key
            byte[] encryptedData = encryptWithAES(data, dataKeyPair.plaintext());

            // Clear plaintext key from memory immediately after use
            Arrays.fill(dataKeyPair.plaintext(), (byte) 0);

            return new EncryptedEnvelope(encryptedData, dataKeyPair.encrypted());

        } catch (Exception e) {
            throw new RuntimeException("Envelope encryption failed", e);
        }
    }

    public byte[] decryptLargeData(EncryptedEnvelope envelope) {
        // Get data key from cache or decrypt from KMS
        DataKeyPair dataKeyPair = keyCache.getIfPresent(masterKeyId);

        if (dataKeyPair == null || !Arrays.equals(dataKeyPair.encrypted(), envelope.encryptedKey())) {
            // Decrypt data key from KMS
            DecryptResponse decryptResponse = kmsClient.decrypt(
                DecryptRequest.builder()
                    .ciphertextBlob(SdkBytes.fromByteArray(envelope.encryptedKey()))
                    .build());

            dataKeyPair = new DataKeyPair(
                decryptResponse.plaintext().asByteArray(),
                envelope.encryptedKey());

            // Cache for future use
            keyCache.put(masterKeyId, dataKeyPair);
        }

        try {
            // Decrypt data with plaintext data key
            byte[] decryptedData = decryptWithAES(envelope.encryptedData(), dataKeyPair.plaintext());

            // Clear plaintext key from memory
            Arrays.fill(dataKeyPair.plaintext(), (byte) 0);

            return decryptedData;

        } catch (Exception e) {
            throw new RuntimeException("Envelope decryption failed", e);
        }
    }

    private byte[] encryptWithAES(byte[] data, byte[] key) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, key, key.length - 16);
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, spec);
        return cipher.doFinal(data);
    }

    private byte[] decryptWithAES(byte[] data, byte[] key) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, key, key.length - 16);
        cipher.init(Cipher.DECRYPT_MODE, keySpec, spec);
        return cipher.doFinal(data);
    }

    public record DataKeyPair(byte[] plaintext, byte[] encrypted) {}
    public record EncryptedEnvelope(byte[] encryptedData, byte[] encryptedKey) {}
}
```

## Data Encryption Interceptor

### SQL Encryption Interceptor

```java
public class KmsDataEncryptInterceptor implements StatementInterceptor {

    private final KmsEncryptionService encryptionService;

    public KmsDataEncryptInterceptor(KmsEncryptionService encryptionService) {
        this.encryptionService = encryptionService;
    }

    @Override
    public ResultSet intercept(ResultSet rs, Statement statement, Connection connection) throws SQLException {
        return new EncryptingResultSetWrapper(rs, encryptionService);
    }

    @Override
    public void interceptAfterExecution(Statement statement) {
        // No-op
    }
}

class EncryptingResultSetWrapper implements ResultSet {

    private final ResultSet delegate;
    private final KmsEncryptionService encryptionService;

    public EncryptingResultSetWrapper(ResultSet delegate, KmsEncryptionService encryptionService) {
        this.delegate = delegate;
        this.encryptionService = encryptionService;
    }

    @Override
    public String getString(String columnLabel) throws SQLException {
        String value = delegate.getString(columnLabel);
        if (value == null) return null;

        // Check if this is an encrypted column
        if (isEncryptedColumn(columnLabel)) {
            return encryptionService.decrypt(value);
        }

        return value;
    }

    private boolean isEncryptedColumn(String columnLabel) {
        // Implement logic to identify encrypted columns
        return columnLabel.contains("encrypted") || columnLabel.contains("secure");
    }

    // Delegate other methods to original ResultSet
    @Override
    public boolean next() throws SQLException {
        return delegate.next();
    }

    // ... other ResultSet method implementations
}
```

## Configuration Profiles

### Development Profile

```properties
# src/main/resources/application-dev.properties
aws.kms.region=us-east-1
kms.encryption-key-id=alias/dev-encryption-key
logging.level.com.yourcompany=DEBUG
```

### Production Profile

```properties
# src/main/resources/application-prod.properties
aws.kms.region=${AWS_REGION:us-east-1}
kms.encryption-key-id=${KMS_ENCRYPTION_KEY_ID:alias/production-encryption-key}
logging.level.com.yourcompany=WARN
spring.cloud.aws.credentials.access-key=${AWS_ACCESS_KEY_ID}
spring.cloud.aws.credentials.secret-key=${AWS_SECRET_ACCESS_KEY}
```

### Test Configuration

```java
@Configuration
@Profile("test")
public class KmsTestConfiguration {

    @Bean
    @Primary
    public KmsClient testKmsClient() {
        // Return a mock or test-specific KMS client
        return mock(KmsClient.class);
    }

    @Bean
    public KmsEncryptionService testKmsEncryptionService() {
        return new KmsEncryptionService(testKmsClient());
    }
}
```

## Health Checks and Monitoring

### KMS Health Indicator

```java
@Component
public class KmsHealthIndicator implements HealthIndicator {

    private final KmsClient kmsClient;
    private final String keyId;

    public KmsHealthIndicator(KmsClient kmsClient,
                             @Value("${kms.encryption-key-id}") String keyId) {
        this.kmsClient = kmsClient;
        this.keyId = keyId;
    }

    @Override
    public Health health() {
        try {
            // Test KMS connectivity by describing the key
            DescribeKeyRequest request = DescribeKeyRequest.builder()
                .keyId(keyId)
                .build();

            DescribeKeyResponse response = kmsClient.describeKey(request);

            // Check if key is in a healthy state
            KeyState keyState = response.keyMetadata().keyState();
            boolean isHealthy = keyState == KeyState.ENABLED;

            if (isHealthy) {
                return Health.up()
                    .withDetail("keyId", keyId)
                    .withDetail("keyState", keyState)
                    .withDetail("keyArn", response.keyMetadata().arn())
                    .build();
            } else {
                return Health.down()
                    .withDetail("keyId", keyId)
                    .withDetail("keyState", keyState)
                    .withDetail("message", "KMS key is not in ENABLED state")
                    .build();
            }

        } catch (KmsException e) {
            return Health.down()
                .withDetail("keyId", keyId)
                .withDetail("error", e.awsErrorDetails().errorMessage())
                .withDetail("errorCode", e.awsErrorDetails().errorCode())
                .build();
        }
    }
}
```

### Metrics Collection

```java
@Service
public class KmsMetricsCollector {

    private final MeterRegistry meterRegistry;
    private final KmsClient kmsClient;

    private final Counter encryptionCounter;
    private final Counter decryptionCounter;
    private final Timer encryptionTimer;
    private final Timer decryptionTimer;

    public KmsMetricsCollector(MeterRegistry meterRegistry, KmsClient kmsClient) {
        this.meterRegistry = meterRegistry;
        this.kmsClient = kmsClient;

        this.encryptionCounter = Counter.builder("kms.encryption.count")
            .description("Number of encryption operations")
            .register(meterRegistry);

        this.decryptionCounter = Counter.builder("kms.decryption.count")
            .description("Number of decryption operations")
            .register(meterRegistry);

        this.encryptionTimer = Timer.builder("kms.encryption.time")
            .description("Time taken for encryption operations")
            .register(meterRegistry);

        this.decryptionTimer = Timer.builder("kms.decryption.time")
            .description("Time taken for decryption operations")
            .register(meterRegistry);
    }

    public String encryptWithMetrics(String plaintext) {
        encryptionCounter.increment();

        return encryptionTimer.record(() -> {
            try {
                EncryptRequest request = EncryptRequest.builder()
                    .keyId("your-key-id")
                    .plaintext(SdkBytes.fromString(plaintext, StandardCharsets.UTF_8))
                    .build();

                EncryptResponse response = kmsClient.encrypt(request);
                return Base64.getEncoder().encodeToString(
                    response.ciphertextBlob().asByteArray());

            } catch (KmsException e) {
                meterRegistry.counter("kms.encryption.errors")
                    .increment();
                throw e;
            }
        });
    }
}
```