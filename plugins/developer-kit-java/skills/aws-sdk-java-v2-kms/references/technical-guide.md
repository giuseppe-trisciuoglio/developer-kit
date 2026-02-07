# AWS KMS Technical Guide

## Key Management Operations

### Create KMS Key

```java
import software.amazon.awssdk.services.kms.model.*;
import java.util.stream.Collectors;

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

## Advanced Techniques

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

### Error Handling Strategies

```java
public class KmsErrorHandler {

    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 1000;

    public <T> T executeWithRetry(Supplier<T> operation, String operationName) {
        int attempt = 0;
        KmsException lastException = null;

        while (attempt < MAX_RETRIES) {
            try {
                return operation.get();
            } catch (KmsException e) {
                lastException = e;
                attempt++;

                // Check if it's a throttling error and retryable
                if (e.awsErrorDetails().errorCode().equals("ThrottlingException") && attempt < MAX_RETRIES) {
                    try {
                        Thread.sleep(RETRY_DELAY_MS);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException("Retry interrupted", ie);
                    }
                } else {
                    // Non-retryable error or max retries exceeded
                    throw e;
                }
            }
        }

        throw new RuntimeException(String.format("Failed to execute %s after %d attempts", operationName, MAX_RETRIES), lastException);
    }

    public boolean isRetryableError(KmsException e) {
        String errorCode = e.awsErrorDetails().errorCode();
        return "ThrottlingException".equals(errorCode)
            || "TooManyRequestsException".equals(errorCode)
            || "LimitExceededException".equals(errorCode);
    }
}
```

### Connection Pooling Configuration

```java
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;

public class KmsConnectionPool {

    public static KmsClient createPooledClient() {
        // Configure connection pool
        PoolingHttpClientConnectionManager connectionManager =
            new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(100);
        connectionManager.setDefaultMaxPerRoute(20);

        CloseableHttpClient httpClient = HttpClients.custom()
            .setConnectionManager(connectionManager)
            .build();

        ApacheHttpClient.Builder httpClientBuilder = ApacheHttpClient.builder()
            .httpClient(httpClient);

        return KmsClient.builder()
            .region(Region.US_EAST_1)
            .httpClientBuilder(httpClientBuilder)
            .build();
    }
}
```