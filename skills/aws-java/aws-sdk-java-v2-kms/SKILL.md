---
name: aws-sdk-java-v2-kms
description: AWS Key Management Service (KMS) patterns using AWS SDK for Java 2.x. Use when creating/managing encryption keys, encrypting/decrypting data, generating data keys, digital signing, key rotation, or integrating encryption into Spring Boot applications.
---

# AWS SDK for Java 2.x - AWS KMS (Key Management Service)

## When to Use

Use this skill when:
- Creating and managing encryption keys
- Encrypting and decrypting data
- Generating data keys for client-side encryption
- Digital signing and verification
- Managing key rotation and lifecycle
- Implementing envelope encryption
- Tagging and organizing keys
- Integrating encryption into Spring Boot applications

## Dependencies

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>kms</artifactId>
</dependency>
```

## Client Setup

### Synchronous Client

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.KmsClient;

KmsClient kmsClient = KmsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Asynchronous Client

```java
import software.amazon.awssdk.services.kms.KmsAsyncClient;

KmsAsyncClient kmsAsyncClient = KmsAsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

## Key Management

### Create KMS Key

```java
import software.amazon.awssdk.services.kms.model.*;

public String createKey(KmsClient kmsClient, String description) {
    try {
        CreateKeyRequest request = CreateKeyRequest.builder()
            .description(description)
            .keyUsage(KeyUsageType.ENCRYPT_DECRYPT)
            .origin(OriginType.AWS_KMS)
            .build();
        
        CreateKeyResponse response = kmsClient.createKey(request);
        
        String keyId = response.keyMetadata().keyId();
        System.out.println("Created key: " + keyId);
        
        return keyId;
        
    } catch (KmsException e) {
        System.err.println("Error creating key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Create Key with Custom Key Store

```java
public String createKeyWithCustomStore(KmsClient kmsClient, 
                                       String description,
                                       String customKeyStoreId) {
    CreateKeyRequest request = CreateKeyRequest.builder()
        .description(description)
        .keyUsage(KeyUsageType.ENCRYPT_DECRYPT)
        .origin(OriginType.AWS_CLOUDHSM)
        .customKeyStoreId(customKeyStoreId)
        .build();
    
    CreateKeyResponse response = kmsClient.createKey(request);
    
    return response.keyMetadata().keyId();
}
```

### List Keys

```java
import java.util.List;

public List<KeyListEntry> listKeys(KmsClient kmsClient) {
    try {
        ListKeysRequest request = ListKeysRequest.builder()
            .limit(100)
            .build();
        
        ListKeysResponse response = kmsClient.listKeys(request);
        
        response.keys().forEach(key -> {
            System.out.println("Key ARN: " + key.keyArn());
            System.out.println("Key ID: " + key.keyId());
            System.out.println();
        });
        
        return response.keys();
        
    } catch (KmsException e) {
        System.err.println("Error listing keys: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### List Keys with Pagination (Async)

```java
import software.amazon.awssdk.services.kms.paginators.ListKeysPublisher;
import java.util.concurrent.CompletableFuture;

public CompletableFuture<Void> listAllKeysAsync(KmsAsyncClient kmsAsyncClient) {
    ListKeysRequest request = ListKeysRequest.builder()
        .limit(15)
        .build();
    
    ListKeysPublisher keysPublisher = kmsAsyncClient.listKeysPaginator(request);
    
    return keysPublisher
        .subscribe(r -> r.keys().forEach(key ->
            System.out.println("Key ARN: " + key.keyArn())))
        .whenComplete((result, exception) -> {
            if (exception != null) {
                System.err.println("Error: " + exception.getMessage());
            } else {
                System.out.println("Successfully listed all keys");
            }
        });
}
```

### Describe Key

```java
public KeyMetadata describeKey(KmsClient kmsClient, String keyId) {
    try {
        DescribeKeyRequest request = DescribeKeyRequest.builder()
            .keyId(keyId)
            .build();
        
        DescribeKeyResponse response = kmsClient.describeKey(request);
        KeyMetadata metadata = response.keyMetadata();
        
        System.out.println("Key ID: " + metadata.keyId());
        System.out.println("Key ARN: " + metadata.arn());
        System.out.println("Key State: " + metadata.keyState());
        System.out.println("Creation Date: " + metadata.creationDate());
        System.out.println("Enabled: " + metadata.enabled());
        
        return metadata;
        
    } catch (KmsException e) {
        System.err.println("Error describing key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Enable/Disable Key

```java
public void enableKey(KmsClient kmsClient, String keyId) {
    try {
        EnableKeyRequest request = EnableKeyRequest.builder()
            .keyId(keyId)
            .build();
        
        kmsClient.enableKey(request);
        System.out.println("Key enabled: " + keyId);
        
    } catch (KmsException e) {
        System.err.println("Error enabling key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}

public void disableKey(KmsClient kmsClient, String keyId) {
    try {
        DisableKeyRequest request = DisableKeyRequest.builder()
            .keyId(keyId)
            .build();
        
        kmsClient.disableKey(request);
        System.out.println("Key disabled: " + keyId);
        
    } catch (KmsException e) {
        System.err.println("Error disabling key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Encryption and Decryption

### Encrypt Data

```java
import software.amazon.awssdk.core.SdkBytes;
import java.nio.charset.StandardCharsets;

public byte[] encryptData(KmsClient kmsClient, String keyId, String plaintext) {
    try {
        SdkBytes plaintextBytes = SdkBytes.fromString(plaintext, StandardCharsets.UTF_8);
        
        EncryptRequest request = EncryptRequest.builder()
            .keyId(keyId)
            .plaintext(plaintextBytes)
            .build();
        
        EncryptResponse response = kmsClient.encrypt(request);
        
        byte[] encryptedData = response.ciphertextBlob().asByteArray();
        System.out.println("Data encrypted successfully");
        
        return encryptedData;
        
    } catch (KmsException e) {
        System.err.println("Error encrypting data: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Decrypt Data

```java
public String decryptData(KmsClient kmsClient, byte[] ciphertext) {
    try {
        SdkBytes ciphertextBytes = SdkBytes.fromByteArray(ciphertext);
        
        DecryptRequest request = DecryptRequest.builder()
            .ciphertextBlob(ciphertextBytes)
            .build();
        
        DecryptResponse response = kmsClient.decrypt(request);
        
        String decryptedText = response.plaintext().asString(StandardCharsets.UTF_8);
        System.out.println("Data decrypted successfully");
        
        return decryptedText;
        
    } catch (KmsException e) {
        System.err.println("Error decrypting data: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Encrypt with Encryption Context

```java
import java.util.Map;

public byte[] encryptWithContext(KmsClient kmsClient, 
                                 String keyId, 
                                 String plaintext,
                                 Map<String, String> encryptionContext) {
    try {
        EncryptRequest request = EncryptRequest.builder()
            .keyId(keyId)
            .plaintext(SdkBytes.fromString(plaintext, StandardCharsets.UTF_8))
            .encryptionContext(encryptionContext)
            .build();
        
        EncryptResponse response = kmsClient.encrypt(request);
        
        return response.ciphertextBlob().asByteArray();
        
    } catch (KmsException e) {
        System.err.println("Error encrypting with context: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Data Key Generation (Envelope Encryption)

### Generate Data Key

```java
public record DataKeyPair(byte[] plaintext, byte[] encrypted) {}

public DataKeyPair generateDataKey(KmsClient kmsClient, String keyId) {
    try {
        GenerateDataKeyRequest request = GenerateDataKeyRequest.builder()
            .keyId(keyId)
            .keySpec(DataKeySpec.AES_256)
            .build();
        
        GenerateDataKeyResponse response = kmsClient.generateDataKey(request);
        
        byte[] plaintextKey = response.plaintext().asByteArray();
        byte[] encryptedKey = response.ciphertextBlob().asByteArray();
        
        System.out.println("Data key generated");
        
        return new DataKeyPair(plaintextKey, encryptedKey);
        
    } catch (KmsException e) {
        System.err.println("Error generating data key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Generate Data Key Without Plaintext

```java
public byte[] generateDataKeyWithoutPlaintext(KmsClient kmsClient, String keyId) {
    try {
        GenerateDataKeyWithoutPlaintextRequest request = 
            GenerateDataKeyWithoutPlaintextRequest.builder()
                .keyId(keyId)
                .keySpec(DataKeySpec.AES_256)
                .build();
        
        GenerateDataKeyWithoutPlaintextResponse response = 
            kmsClient.generateDataKeyWithoutPlaintext(request);
        
        return response.ciphertextBlob().asByteArray();
        
    } catch (KmsException e) {
        System.err.println("Error generating data key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Digital Signing

### Create Signing Key

```java
public String createSigningKey(KmsClient kmsClient, String description) {
    try {
        CreateKeyRequest request = CreateKeyRequest.builder()
            .description(description)
            .keySpec(KeySpec.RSA_2048)
            .keyUsage(KeyUsageType.SIGN_VERIFY)
            .origin(OriginType.AWS_KMS)
            .build();
        
        CreateKeyResponse response = kmsClient.createKey(request);
        
        return response.keyMetadata().keyId();
        
    } catch (KmsException e) {
        System.err.println("Error creating signing key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Sign Data

```java
public byte[] signData(KmsClient kmsClient, String keyId, String message) {
    try {
        SdkBytes messageBytes = SdkBytes.fromString(message, StandardCharsets.UTF_8);
        
        SignRequest request = SignRequest.builder()
            .keyId(keyId)
            .message(messageBytes)
            .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
            .build();
        
        SignResponse response = kmsClient.sign(request);
        
        byte[] signature = response.signature().asByteArray();
        System.out.println("Data signed successfully");
        
        return signature;
        
    } catch (KmsException e) {
        System.err.println("Error signing data: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Verify Signature

```java
public boolean verifySignature(KmsClient kmsClient, 
                                String keyId, 
                                String message, 
                                byte[] signature) {
    try {
        VerifyRequest request = VerifyRequest.builder()
            .keyId(keyId)
            .message(SdkBytes.fromString(message, StandardCharsets.UTF_8))
            .signature(SdkBytes.fromByteArray(signature))
            .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
            .build();
        
        VerifyResponse response = kmsClient.verify(request);
        
        boolean isValid = response.signatureValid();
        System.out.println("Signature valid: " + isValid);
        
        return isValid;
        
    } catch (KmsException e) {
        System.err.println("Error verifying signature: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### Sign and Verify (Async)

```java
public CompletableFuture<Boolean> signAndVerifyAsync(KmsAsyncClient kmsAsyncClient,
                                                      String message) {
    String signMessage = message;
    
    // Create signing key
    CreateKeyRequest createKeyRequest = CreateKeyRequest.builder()
        .keySpec(KeySpec.RSA_2048)
        .keyUsage(KeyUsageType.SIGN_VERIFY)
        .origin(OriginType.AWS_KMS)
        .build();
    
    return kmsAsyncClient.createKey(createKeyRequest)
        .thenCompose(createKeyResponse -> {
            String keyId = createKeyResponse.keyMetadata().keyId();
            
            SdkBytes messageBytes = SdkBytes.fromString(signMessage, StandardCharsets.UTF_8);
            SignRequest signRequest = SignRequest.builder()
                .keyId(keyId)
                .message(messageBytes)
                .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
                .build();
            
            return kmsAsyncClient.sign(signRequest)
                .thenCompose(signResponse -> {
                    byte[] signedBytes = signResponse.signature().asByteArray();
                    
                    VerifyRequest verifyRequest = VerifyRequest.builder()
                        .keyId(keyId)
                        .message(messageBytes)
                        .signature(SdkBytes.fromByteArray(signedBytes))
                        .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
                        .build();
                    
                    return kmsAsyncClient.verify(verifyRequest)
                        .thenApply(VerifyResponse::signatureValid);
                });
        })
        .exceptionally(throwable -> {
            throw new RuntimeException("Failed to sign or verify", throwable);
        });
}
```

## Key Tagging

### Tag Key

```java
public void tagKey(KmsClient kmsClient, String keyId, Map<String, String> tags) {
    try {
        List<Tag> tagList = tags.entrySet().stream()
            .map(entry -> Tag.builder()
                .tagKey(entry.getKey())
                .tagValue(entry.getValue())
                .build())
            .collect(Collectors.toList());
        
        TagResourceRequest request = TagResourceRequest.builder()
            .keyId(keyId)
            .tags(tagList)
            .build();
        
        kmsClient.tagResource(request);
        System.out.println("Key tagged successfully");
        
    } catch (KmsException e) {
        System.err.println("Error tagging key: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

### List Tags

```java
public Map<String, String> listTags(KmsClient kmsClient, String keyId) {
    try {
        ListResourceTagsRequest request = ListResourceTagsRequest.builder()
            .keyId(keyId)
            .build();
        
        ListResourceTagsResponse response = kmsClient.listResourceTags(request);
        
        return response.tags().stream()
            .collect(Collectors.toMap(Tag::tagKey, Tag::tagValue));
        
    } catch (KmsException e) {
        System.err.println("Error listing tags: " + e.awsErrorDetails().errorMessage());
        throw e;
    }
}
```

## Spring Boot Integration

### Configuration

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

### Encryption Service

```java
@Service
public class KmsEncryptionService {
    
    private final KmsClient kmsClient;
    
    @Value("${kms.key-id}")
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

### Sensitive Data Repository

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

### Envelope Encryption Service

```java
@Service
public class EnvelopeEncryptionService {
    
    private final KmsClient kmsClient;
    
    @Value("${kms.master-key-id}")
    private String masterKeyId;
    
    public EnvelopeEncryptionService(KmsClient kmsClient) {
        this.kmsClient = kmsClient;
    }
    
    public EncryptedEnvelope encryptLargeData(byte[] data) {
        // Generate data key
        GenerateDataKeyResponse dataKeyResponse = kmsClient.generateDataKey(
            GenerateDataKeyRequest.builder()
                .keyId(masterKeyId)
                .keySpec(DataKeySpec.AES_256)
                .build());
        
        byte[] plaintextKey = dataKeyResponse.plaintext().asByteArray();
        byte[] encryptedKey = dataKeyResponse.ciphertextBlob().asByteArray();
        
        try {
            // Encrypt data with plaintext data key
            byte[] encryptedData = encryptWithAES(data, plaintextKey);
            
            // Clear plaintext key from memory
            Arrays.fill(plaintextKey, (byte) 0);
            
            return new EncryptedEnvelope(encryptedData, encryptedKey);
            
        } catch (Exception e) {
            throw new RuntimeException("Envelope encryption failed", e);
        }
    }
    
    public byte[] decryptLargeData(EncryptedEnvelope envelope) {
        // Decrypt data key
        DecryptResponse decryptResponse = kmsClient.decrypt(
            DecryptRequest.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(envelope.encryptedKey()))
                .build());
        
        byte[] plaintextKey = decryptResponse.plaintext().asByteArray();
        
        try {
            // Decrypt data with plaintext data key
            byte[] decryptedData = decryptWithAES(envelope.encryptedData(), plaintextKey);
            
            // Clear plaintext key from memory
            Arrays.fill(plaintextKey, (byte) 0);
            
            return decryptedData;
            
        } catch (Exception e) {
            throw new RuntimeException("Envelope decryption failed", e);
        }
    }
    
    private byte[] encryptWithAES(byte[] data, byte[] key) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);
        return cipher.doFinal(data);
    }
    
    private byte[] decryptWithAES(byte[] data, byte[] key) throws Exception {
        SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, keySpec);
        return cipher.doFinal(data);
    }
    
    public record EncryptedEnvelope(byte[] encryptedData, byte[] encryptedKey) {}
}
```

## Best Practices

1. **Key Management**:
   - Use separate keys for different purposes
   - Enable automatic key rotation
   - Implement key lifecycle policies
   - Use aliases for key references

2. **Security**:
   - Never log plaintext or encryption keys
   - Use encryption context for additional security
   - Implement least privilege IAM policies
   - Clear sensitive data from memory after use

3. **Performance**:
   - Cache data keys for envelope encryption
   - Use async operations for non-blocking I/O
   - Implement connection pooling
   - Reuse KMS client instances

4. **Cost Optimization**:
   - Use envelope encryption for large data
   - Cache encrypted data keys
   - Monitor API usage
   - Use data key caching libraries

5. **Error Handling**:
   - Implement retry logic for throttling
   - Handle key state errors gracefully
   - Log KMS-specific error codes
   - Implement circuit breakers

## Testing

### Unit Test with Mocked Client

```java
@ExtendWith(MockitoExtension.class)
class KmsEncryptionServiceTest {
    
    @Mock
    private KmsClient kmsClient;
    
    @InjectMocks
    private KmsEncryptionService encryptionService;
    
    @Test
    void shouldEncryptData() {
        String plaintext = "sensitive data";
        byte[] ciphertext = "encrypted".getBytes();
        
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenReturn(EncryptResponse.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
                .build());
        
        String result = encryptionService.encrypt(plaintext);
        
        assertThat(result).isNotEmpty();
        verify(kmsClient).encrypt(any(EncryptRequest.class));
    }
}
```

## Related Skills

- @aws-sdk-java-v2-core - Core AWS SDK patterns
- @aws-sdk-java-v2-secrets-manager - Secrets management
- @spring-boot-dependency-injection - Spring DI patterns

## References

- [KMS Examples](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/kms)
- [KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/)
- [KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [KMS API Reference](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/kms/package-summary.html)
