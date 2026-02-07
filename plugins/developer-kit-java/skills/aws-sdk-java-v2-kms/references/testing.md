# Testing AWS KMS Integration

## Unit Testing with Mocked Client

### Basic Unit Test

```java
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class KmsEncryptionServiceTest {

    @Mock
    private KmsClient kmsClient;

    @InjectMocks
    private KmsEncryptionService encryptionService;

    @Test
    void shouldEncryptData() {
        // Arrange
        String plaintext = "sensitive data";
        byte[] ciphertext = "encrypted".getBytes();

        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenReturn(EncryptResponse.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
                .build());

        // Act
        String result = encryptionService.encrypt(plaintext);

        // Assert
        assertThat(result).isNotEmpty();
        verify(kmsClient).encrypt(any(EncryptRequest.class));
    }

    @Test
    void shouldDecryptData() {
        // Arrange
        String encryptedText = "ciphertext";
        String expectedPlaintext = "sensitive data";

        when(kmsClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromString(expectedPlaintext, StandardCharsets.UTF_8))
                .build());

        // Act
        String result = encryptionService.decrypt(encryptedText);

        // Assert
        assertThat(result).isEqualTo(expectedPlaintext);
        verify(kmsClient).decrypt(any(DecryptRequest.class));
    }

    @Test
    void shouldThrowExceptionOnEncryptionFailure() {
        // Arrange
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenThrow(KmsException.builder()
                .awsErrorDetails(AwsErrorDetails.builder()
                    .errorCode("KMSDisabledException")
                    .errorMessage("KMS is disabled")
                    .build())
                .build());

        // Act & Assert
        assertThatThrownBy(() -> encryptionService.encrypt("test"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Encryption failed");
    }
}
```

### Parameterized Tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class KmsEncryptionParameterizedTest {

    @Mock
    private KmsClient kmsClient;

    @InjectMocks
    private KmsEncryptionService encryptionService;

    @ParameterizedTest
    @CsvSource({
        "hello, world",
        "12345, 67890",
        "special@chars, normal",
        "very long string with multiple words, another string",
        "", // empty string
        "null test, null test"
    })
    void shouldEncryptAndDecrypt(String plaintext, String testIdentifier) {
        // Arrange
        byte[] ciphertext = "encrypted".getBytes();

        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenReturn(EncryptResponse.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
                .build());

        when(kmsClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromString(plaintext, StandardCharsets.UTF_8))
                .build());

        // Act
        String encrypted = encryptionService.encrypt(plaintext);
        String decrypted = encryptionService.decrypt(encrypted);

        // Assert
        assertThat(decrypted).isEqualTo(plaintext);
    }
}
```

## Integration Testing with Testcontainers

### Local KMS Mock Setup

```java
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

import static org.testcontainers.containers.localstack.LocalStackContainer.Service.KMS;

@Testcontainers
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class KmsIntegrationTest {

    @Container
    private static final LocalStackContainer localStack =
        new LocalStackContainer(DockerImageName.parse("localstack/localstack:latest"))
            .withServices(KMS);

    private KmsClient kmsClient;

    @BeforeAll
    void setup() {
        kmsClient = KmsClient.builder()
            .region(Region.of(localStack.getRegion()))
            .endpointOverride(localStack.getEndpointOverride(KMS))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(localStack.getAccessKey(), localStack.getSecretKey())))
            .build();
    }

    @Test
    void shouldCreateAndManageKeysWithLocalKms() {
        // Create a key
        String keyId = createTestKey(kmsClient, "test-key");
        assertThat(keyId).isNotEmpty();

        // Describe the key
        KeyMetadata metadata = describeKey(kmsClient, keyId);
        assertThat(metadata.keyState()).isEqualTo(KeyState.ENABLED);

        // List keys
        List<KeyListEntry> keys = listKeys(kmsClient);
        assertThat(keys).hasSizeGreaterThan(0);
    }
}
```

## Testing with Spring Boot Test Slices

### KmsServiceSlice Test

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class KmsControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private KmsEncryptionService kmsEncryptionService;

    @Test
    void shouldEncryptData() throws Exception {
        String plaintext = "test data";
        String encrypted = "encrypted-data";

        when(kmsEncryptionService.encrypt(plaintext)).thenReturn(encrypted);

        mockMvc.perform(post("/api/kms/encrypt")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"data\":\"" + plaintext + "\"}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data").value(encrypted));

        verify(kmsEncryptionService).encrypt(plaintext);
    }

    @Test
    void shouldHandleEncryptionErrors() throws Exception {
        when(kmsEncryptionService.encrypt(any()))
            .thenThrow(new RuntimeException("KMS error"));

        mockMvc.perform(post("/api/kms/encrypt")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"data\":\"test\"}"))
            .andExpect(status().isInternalServerError());
    }
}
```

### Testing with SpringBootTest and Configuration

```java
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;

@TestConfiguration
class KmsTestConfiguration {

    @Bean
    @Primary
    public KmsClient testKmsClient() {
        // Create a mock KMS client for testing
        KmsClient mockClient = mock(KmsClient.class);

        // Mock key creation
        when(mockClient.createKey(any(CreateKeyRequest.class)))
            .thenReturn(CreateKeyResponse.builder()
                .keyMetadata(KeyMetadata.builder()
                    .keyId("test-key-id")
                    .keyArn("arn:aws:kms:us-east-1:123456789012:key/test-key-id")
                    .keyState(KeyState.ENABLED)
                    .build())
                .build());

        // Mock encryption
        when(mockClient.encrypt(any(EncryptRequest.class)))
            .thenReturn(EncryptResponse.builder()
                .ciphertextBlob(SdkBytes.fromString("encrypted-data", StandardCharsets.UTF_8))
                .build());

        // Mock decryption
        when(mockClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromString("decrypted-data", StandardCharsets.UTF_8))
                .build());

        return mockClient;
    }
}

@SpringBootTest(classes = {Application.class, KmsTestConfiguration.class})
class KmsServiceWithTestConfigIntegrationTest {

    @Autowired
    private KmsEncryptionService encryptionService;

    @Test
    void shouldUseTestConfiguration() {
        String result = encryptionService.encrypt("test");
        assertThat(result).isNotEmpty();
    }
}
```

## Testing Envelope Encryption

### Envelope Encryption Test

```java
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class EnvelopeEncryptionServiceTest {

    @Mock
    private KmsClient kmsClient;

    @InjectMocks
    private EnvelopeEncryptionService envelopeEncryptionService;

    @Test
    void shouldEncryptAndDecryptLargeData() {
        // Arrange
        byte[] testData = "large test data".getBytes();
        byte[] encryptedDataKey = "encrypted-data-key".getBytes();

        // Mock data key generation
        when(kmsClient.generateDataKey(any(GenerateDataKeyRequest.class)))
            .thenReturn(GenerateDataKeyResponse.builder()
                .plaintext(SdkBytes.fromByteArray("data-key".getBytes()))
                .ciphertextBlob(SdkBytes.fromByteArray(encryptedDataKey))
                .build());

        // Mock data key decryption
        when(kmsClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromByteArray("data-key".getBytes()))
                .build());

        // Act
        EncryptedEnvelope encryptedEnvelope = envelopeEncryptionService.encryptLargeData(testData);
        byte[] decryptedData = envelopeEncryptionService.decryptLargeData(encryptedEnvelope);

        // Assert
        assertThat(encryptedEnvelope.encryptedData()).isNotEmpty();
        assertThat(encryptedEnvelope.encryptedKey()).isEqualTo(encryptedDataKey);
        assertThat(decryptedData).isEqualTo(testData);

        // Verify interactions
        verify(kmsClient).generateDataKey(any(GenerateDataKeyRequest.class));
        verify(kmsClient).decrypt(any(DecryptRequest.class));
    }

    @Test
    void shouldClearSensitiveDataFromMemory() {
        // Arrange
        byte[] testData = "test data".getBytes();
        byte[] encryptedDataKey = "encrypted-key".getBytes();

        when(kmsClient.generateDataKey(any(GenerateDataKeyRequest.class)))
            .thenReturn(GenerateDataKeyResponse.builder()
                .plaintext(SdkBytes.fromByteArray("sensitive-data-key".getBytes()))
                .ciphertextBlob(SdkBytes.fromByteArray(encryptedDataKey))
                .build());

        when(kmsClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromByteArray("sensitive-data-key".getBytes()))
                .build());

        // Act
        envelopeEncryptionService.encryptLargeData(testData);
        envelopeEncryptionService.decryptLargeData(new EncryptedEnvelope(testData, encryptedDataKey));

        // Note: Memory clearing is difficult to test directly
        // In real tests, you would verify no sensitive data remains in memory traces
    }
}
```

## Testing Digital Signatures

### Digital Signature Tests

```java
class DigitalSignatureServiceTest {

    @Mock
    private KmsClient kmsClient;

    @InjectMocks
    private DigitalSignatureService signatureService;

    @Test
    void shouldSignAndVerifyData() {
        // Arrange
        String message = "test message";
        byte[] signature = "signature-data".getBytes();

        when(kmsClient.sign(any(SignRequest.class)))
            .thenReturn(SignResponse.builder()
                .signature(SdkBytes.fromByteArray(signature))
                .build());

        when(kmsClient.verify(any(VerifyRequest.class)))
            .thenReturn(VerifyResponse.builder()
                .signatureValid(true)
                .build());

        // Act
        byte[] signedSignature = signatureService.signData(message);
        boolean isValid = signatureService.verifySignature(message, signedSignature);

        // Assert
        assertThat(signedSignature).isEqualTo(signature);
        assertThat(isValid).isTrue();
    }

    @Test
    void shouldDetectInvalidSignature() {
        // Arrange
        String message = "test message";
        byte[] signature = "invalid-signature".getBytes();

        when(kmsClient.verify(any(VerifyRequest.class)))
            .thenReturn(VerifyResponse.builder()
                .signatureValid(false)
                .build());

        // Act & Assert
        assertThatThrownBy(() ->
            signatureService.verifySignature(message, signature))
            .isInstanceOf(SecurityException.class)
            .hasMessageContaining("Invalid signature");
    }
}
```

## Performance Testing

### Performance Test with JMH

```java
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;
import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 1)
@Fork(1)
class KmsPerformanceTest {

    @MockBean
    private KmsClient kmsClient;

    @Autowired
    private KmsEncryptionService encryptionService;

    @Benchmark
    public void testEncryptionPerformance(Blackhole bh) {
        String testData = "performance test data with some content";
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenReturn(EncryptResponse.builder()
                .ciphertextBlob(SdkBytes.fromString("encrypted", StandardCharsets.UTF_8))
                .build());

        String result = encryptionService.encrypt(testData);
        bh.consume(result);
    }

    @Benchmark
    public void testDecryptionPerformance(Blackhole bh) {
        String encryptedData = "encrypted-performance-data";
        when(kmsClient.decrypt(any(DecryptRequest.class)))
            .thenReturn(DecryptResponse.builder()
                .plaintext(SdkBytes.fromString("decrypted", StandardCharsets.UTF_8))
                .build());

        String result = encryptionService.decrypt(encryptedData);
        bh.consume(result);
    }
}
```

## Testing Error Scenarios

### Error Handling Tests

```java
class KmsErrorHandlingTest {

    @Mock
    private KmsClient kmsClient;

    @InjectMocks
    private KmsEncryptionService encryptionService;

    @Test
    void shouldHandleThrottlingException() {
        // Arrange
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenThrow(KmsException.builder()
                .awsErrorDetails(AwsErrorDetails.builder()
                    .errorCode("ThrottlingException")
                    .errorMessage("Rate exceeded")
                    .build())
                .build());

        // Act & Assert
        assertThatThrownBy(() -> encryptionService.encrypt("test"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Rate limit exceeded");
    }

    @Test
    void shouldHandleDisabledKey() {
        // Arrange
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenThrow(KmsException.builder()
                .awsErrorDetails(AwsErrorDetails.builder()
                    .errorCode("DisabledException")
                    .errorMessage("Key is disabled")
                    .build())
                .build());

        // Act & Assert
        assertThatThrownBy(() -> encryptionService.encrypt("test"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Key is disabled");
    }

    @Test
    void shouldHandleNotFoundException() {
        // Arrange
        when(kmsClient.encrypt(any(EncryptRequest.class)))
            .thenThrow(KmsException.builder()
                .awsErrorDetails(AwsErrorDetails.builder()
                    .errorCode("NotFoundException")
                    .errorMessage("Key not found")
                    .build())
                .build());

        // Act & Assert
        assertThatThrownBy(() -> encryptionService.encrypt("test"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("Key not found");
    }
}
```

## Integration Testing with AWS Local

### Testcontainers KMS Setup

```java
import org.testcontainers.containers.localstack.LocalStackContainer;
import software.amazon.awssdk.services.kms.KmsClient;
import static org.testcontainers.containers.localstack.LocalStackContainer.Service.KMS;

@SpringBootTest
class KmsAwsLocalIntegrationTest {

    @Container
    private static final LocalStackContainer localStack =
        new LocalStackContainer(DockerImageName.parse("localstack/localstack:latest"))
            .withServices(KMS)
            .withEnv("DEFAULT_REGION", "us-east-1");

    private KmsClient kmsClient;

    @BeforeEach
    void setup() {
        kmsClient = KmsClient.builder()
            .region(Region.AWS_GLOBAL)
            .endpointOverride(localStack.getEndpointOverride(KMS))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(localStack.getAccessKey(), localStack.getSecretKey())))
            .build();
    }

    @Test
    void shouldCreateKeyInLocalKms() {
        // This test creates a real key in the local KMS instance
        CreateKeyRequest request = CreateKeyRequest.builder()
            .description("Test key")
            .keyUsage(KeyUsageType.ENCRYPT_DECRYPT)
            .build();

        CreateKeyResponse response = kmsClient.createKey(request);
        assertThat(response.keyMetadata().keyId()).isNotEmpty();
    }
}
```