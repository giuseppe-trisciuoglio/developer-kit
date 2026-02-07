# AWS KMS Best Practices

## Security Best Practices

### Key Management

1. **Use Separate Keys for Different Purposes**
   - Create unique keys for different applications or data types
   - Avoid reusing keys across multiple purposes
   - Use aliases instead of raw key IDs for references

   ```java
   // Good: Create specific keys
   String encryptionKey = kms.createKey("Database encryption key");
   String signingKey = kms.createSigningKey("Document signing key");

   // Bad: Use the same key for everything
   ```

2. **Enable Automatic Key Rotation**
   - Enable automatic key rotation for enhanced security
   - Review rotation schedules based on compliance requirements

   ```java
   public void enableKeyRotation(KmsClient kmsClient, String keyId) {
       EnableKeyRotationRequest request = EnableKeyRotationRequest.builder()
           .keyId(keyId)
           .build();
       kmsClient.enableKeyRotation(request);
   }
   ```

3. **Implement Key Lifecycle Policies**
   - Set key expiration dates based on data retention policies
   - Schedule key deletion when no longer needed
   - Use key policies to enforce lifecycle rules

4. **Use Key Aliases**
   - Always use aliases instead of raw key IDs
   - Create meaningful aliases following naming conventions
   - Regularly review and update aliases

   ```java
   public void createKeyWithAlias(KmsClient kmsClient, String alias, String description) {
       // Create key
       CreateKeyResponse response = kmsClient.createKey(
           CreateKeyRequest.builder()
               .description(description)
               .build());

       // Create alias
       CreateAliasRequest aliasRequest = CreateAliasRequest.builder()
           .aliasName(alias)
           .targetKeyId(response.keyMetadata().keyId())
           .build();
       kmsClient.createAlias(aliasRequest);
   }
   ```

### Encryption Security

1. **Never Log Plaintext or Encryption Keys**
   - Avoid logging sensitive data in any form
   - Ensure proper logging configuration to prevent accidental exposure

   ```java
   // Bad: Logging sensitive data
   logger.info("Encrypted data: {}", encryptedData);

   // Good: Log only metadata
   logger.info("Encryption completed for user: {}", userId);
   ```

2. **Use Encryption Context**
   - Always include encryption context for additional security
   - Use contextual information to verify data integrity

   ```java
   public Map<String, String> createEncryptionContext(String userId, String dataType) {
       return Map.of(
           "userId", userId,
           "dataType", dataType,
           "timestamp", Instant.now().toString()
       );
   }
   ```

3. **Implement Least Privilege IAM Policies**
   - Grant minimal required permissions to KMS keys
   - Use IAM policies to restrict access to specific resources

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Principal": {"AWS": "arn:aws:iam::123456789012:role/app-role"},
               "Action": [
                   "kms:Encrypt",
                   "kms:Decrypt",
                   "kms:DescribeKey"
               ],
               "Resource": "arn:aws:kms:us-east-1:123456789012:key/your-key-id",
               "Condition": {
                   "StringEquals": {
                       "kms:EncryptionContext:userId": "${aws:userid}"
                   }
               }
           }
       ]
   }
   ```

4. **Clear Sensitive Data from Memory**
   - Explicitly clear sensitive data from memory after use
   - Use secure memory management practices

   ```java
   public void secureMemoryExample() {
       byte[] sensitiveKey = new byte[32];
       // ... use the key ...

       // Clear sensitive data
       Arrays.fill(sensitiveKey, (byte) 0);
   }
   ```

## Performance Best Practices

1. **Cache Data Keys for Envelope Encryption**
   - Cache encrypted data keys to avoid repeated KMS calls
   - Use appropriate cache eviction policies
   - Monitor cache hit rates

   ```java
   public class DataKeyCache {
       private final Cache<String, byte[]> keyCache;

       public DataKeyCache() {
           this.keyCache = Caffeine.newBuilder()
               .expireAfterWrite(1, TimeUnit.HOURS)
               .maximumSize(1000)
               .build();
       }

       public byte[] getCachedDataKey(String keyId, KmsClient kmsClient) {
           return keyCache.get(keyId, k -> {
               GenerateDataKeyResponse response = kmsClient.generateDataKey(
                   GenerateDataKeyRequest.builder()
                       .keyId(keyId)
                       .keySpec(DataKeySpec.AES_256)
                       .build());
               return response.ciphertextBlob().asByteArray();
           });
       }
   }
   ```

2. **Use Async Operations for Non-Blocking I/O**
   - Leverage async clients for parallel processing
   - Use CompletableFuture for chaining operations

   ```java
   public CompletableFuture<Void> processMultipleAsync(List<String> dataItems) {
       List<CompletableFuture<Void>> futures = dataItems.stream()
           .map(item -> CompletableFuture.runAsync(() ->
               encryptAndStoreItem(item)))
           .collect(Collectors.toList());

       return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
   }
   ```

3. **Implement Connection Pooling**
   - Configure connection pooling for better resource utilization
   - Set appropriate pool sizes based on load

   ```java
   public KmsClient createPooledClient() {
       return KmsClient.builder()
           .region(Region.US_EAST_1)
           .httpClientBuilder(ApacheHttpClient.builder()
               .maxConnections(100)
               .connectionTimeToLive(Duration.ofSeconds(30))
               .build())
           .build();
   }
   ```

4. **Reuse KMS Client Instances**
   - Create and reuse client instances rather than creating new ones
   - Use dependency injection for client management

   ```java
   @Service
   @RequiredArgsConstructor
   public class KmsService {
       private final KmsClient kmsClient; // Inject and reuse

       public void performOperation() {
           // Use the same client instance
           kmsClient.someOperation();
       }
   }
   ```

## Cost Optimization

1. **Use Envelope Encryption for Large Data**
   - Generate data keys for encrypting large datasets
   - Only use KMS for encrypting the data key, not the entire dataset

   ```java
   public class EnvelopeEncryption {
       private final KmsClient kmsClient;

       public byte[] encryptLargeData(byte[] largeData) {
           // Generate data key
           GenerateDataKeyResponse response = kmsClient.generateDataKey(
               GenerateDataKeyRequest.builder()
                   .keyId("master-key-id")
                   .keySpec(DataKeySpec.AES_256)
                   .build());

           byte[] encryptedKey = response.ciphertextBlob().asByteArray();
           byte[] plaintextKey = response.plaintext().asByteArray();

           // Encrypt data with local key
           byte[] encryptedData = localEncrypt(largeData, plaintextKey);

           // Return both encrypted data and encrypted key
           return combine(encryptedKey, encryptedData);
       }
   }
   ```

2. **Cache Encrypted Data Keys**
   - Cache encrypted data keys to avoid repeated KMS calls
   - Use time-based cache expiration

3. **Monitor API Usage**
   - Track KMS API calls for billing and optimization
   - Set up CloudWatch alarms for unexpected usage

   ```java
   public class KmsUsageMonitor {
       private final MeterRegistry meterRegistry;

       public void recordEncryption() {
           meterRegistry.counter("kms.encryption.count").increment();
           meterRegistry.timer("kms.encryption.time").record(() -> {
               // Perform encryption
           });
       }
   }
   ```

4. **Use Data Key Caching Libraries**
   - Implement proper caching strategies
   - Consider using dedicated caching solutions for data keys

## Error Handling Best Practices

1. **Implement Retry Logic for Throttling**
   - Add retry logic for throttling exceptions
   - Use exponential backoff for retries

   ```java
   public class KmsRetryHandler {
       private static final int MAX_RETRIES = 3;
       private static final long INITIAL_DELAY = 1000; // 1 second

       public <T> T executeWithRetry(Supplier<T> operation) {
           int attempt = 0;
           while (attempt < MAX_RETRIES) {
               try {
                   return operation.get();
               } catch (KmsException e) {
                   if (!isRetryable(e) || attempt == MAX_RETRIES - 1) {
                       throw e;
                   }
                   attempt++;
                   try {
                       Thread.sleep(INITIAL_DELAY * (long) Math.pow(2, attempt));
                   } catch (InterruptedException ie) {
                       Thread.currentThread().interrupt();
                       throw new RuntimeException("Retry interrupted", ie);
                   }
               }
           }
           throw new IllegalStateException("Should not reach here");
       }

       private boolean isRetryable(KmsException e) {
           return "ThrottlingException".equals(e.awsErrorDetails().errorCode());
       }
   }
   ```

2. **Handle Key State Errors Gracefully**
   - Check key state before performing operations
   - Handle key states like PendingDeletion, Disabled, etc.

   ```java
   public void performOperationWithKeyStateCheck(KmsClient kmsClient, String keyId) {
       KeyMetadata metadata = describeKey(kmsClient, keyId);

       switch (metadata.keyState()) {
           case ENABLED:
               // Perform operation
               break;
           case DISABLED:
               throw new IllegalStateException("Key is disabled");
           case PENDING_DELETION:
               throw new IllegalStateException("Key is scheduled for deletion");
           default:
               throw new IllegalStateException("Unknown key state: " + metadata.keyState());
       }
   }
   ```

3. **Log KMS-Specific Error Codes**
   - Implement comprehensive error logging
   - Map KMS error codes to meaningful application errors

   ```java
   public class KmsErrorHandler {
       public String mapKmsErrorToAppError(KmsException e) {
           String errorCode = e.awsErrorDetails().errorCode();
           switch (errorCode) {
               case "NotFoundException":
                   return "Key not found";
               case "DisabledException":
                   return "Key is disabled";
               case "AccessDeniedException":
                   return "Access denied";
               case "InvalidKeyUsageException":
                   return "Invalid key usage";
               default:
                   return "KMS error: " + errorCode;
           }
       }
   }
   ```

4. **Implement Circuit Breakers**
   - Use circuit breakers to handle KMS unavailability
   - Prevent cascading failures during outages

   ```java
   public class KmsCircuitBreaker {
       private final CircuitBreaker circuitBreaker;

       public KmsCircuitBreaker() {
           this.circuitBreaker = CircuitBreaker.builder()
               .name("kmsService")
               .failureRateThreshold(50)
               .waitDurationInOpenState(Duration.ofSeconds(30))
               .ringBufferSizeInHalfOpenState(2)
               .ringBufferSizeInClosedState(2)
               .build();
       }

       public <T> T executeWithCircuitBreaker(Callable<T> operation) {
           return circuitBreaker.executeCallable(() -> {
               try {
                   return operation.call();
               } catch (KmsException e) {
                   if (isFailure(e)) {
                       throw new CircuitBreakerOpenException("KMS service unavailable");
                   }
                   throw e;
               }
           });
       }

       private boolean isFailure(KmsException e) {
           return "KMSDisabledException".equals(e.awsErrorDetails().errorCode());
       }
   }
   ```

## Testing Best Practices

1. **Test with Mock KMS Client**
   - Use mock clients for unit tests
   - Verify all expected interactions

   ```java
   @Test
   void shouldEncryptWithProperEncryptionContext() {
       // Arrange
       when(kmsClient.encrypt(any(EncryptRequest.class))).thenReturn(...);

       // Act
       String result = encryptionService.encrypt("test", "user123");

       // Assert
       verify(kmsClient).encrypt(argThat(request ->
           request.encryptionContext().containsKey("userId") &&
           request.encryptionContext().get("userId").equals("user123")));
   }
   ```

2. **Test Error Scenarios**
   - Test various error conditions
   - Verify proper error handling and recovery

3. **Performance Testing**
   - Test performance under load
   - Measure latency and throughput

4. **Integration Testing with Local KMS**
   - Test with local KMS when possible
   - Verify integration with real AWS services

## Monitoring and Observability

1. **Implement Comprehensive Logging**
   - Log all KMS operations with appropriate levels
   - Include correlation IDs for tracing

   ```java
   public class KmsLoggingAspect {
       private static final Logger logger = LoggerFactory.getLogger(KmsService.class);

       @Around("execution(* com.yourcompany.kms..*.*(..))")
       public Object logKmsOperation(ProceedingJoinPoint joinPoint) throws Throwable {
           String operation = joinPoint.getSignature().getName();
           logger.info("Starting KMS operation: {}", operation);

           long startTime = System.currentTimeMillis();
           try {
               Object result = joinPoint.proceed();
               long duration = System.currentTimeMillis() - startTime;
               logger.info("Completed KMS operation: {} in {}ms", operation, duration);
               return result;
           } catch (Exception e) {
               long duration = System.currentTimeMillis() - startTime;
               logger.error("KMS operation {} failed in {}ms: {}", operation, duration, e.getMessage());
               throw e;
           }
       }
   }
   ```

2. **Set Up CloudWatch Alarms**
   - Monitor API call rates
   - Set up alarms for error rates
   - Track key usage patterns

3. **Use Distributed Tracing**
   - Implement tracing for KMS operations
   - Correlate KMS calls with application operations

4. **Monitor Key Usage Metrics**
   - Track key usage patterns
   - Monitor for unusual usage patterns

## Compliance and Auditing

1. **Enable KMS Key Usage Logging**
   - Configure CloudTrail to log KMS operations
   - Enable detailed logging for compliance

2. **Regular Security Audits**
   - Conduct regular audits of KMS key usage
   - Review access policies periodically

3. **Comprehensive Backup Strategy**
   - Implement key backup and recovery procedures
   - Test backup restoration processes

4. **Comprehensive Access Reviews**
   - Regularly review IAM policies for KMS access
   - Remove unnecessary permissions

## Advanced Security Considerations

1. **Multi-Region KMS Keys**
   - Consider multi-region keys for disaster recovery
   - Test failover scenarios

2. **Cross-Account Access**
   - Implement proper cross-account access controls
   - Use resource-based policies for account sharing

3. **Custom Key Stores**
   - Consider custom key stores for enhanced security
   - Implement proper key management in custom stores

4. **Key Material External**
   - Use imported key material for enhanced control
   - Implement proper key rotation for imported keys

## Development Best Practices

1. **Use Dependency Injection**
   - Inject KMS clients rather than creating them directly
   - Use proper configuration management

   ```java
   @Configuration
   @ConfigurationProperties(prefix = "aws.kms")
   public class KmsProperties {
       private String region = "us-east-1";
       private String encryptionKeyId;
       private int maxRetries = 3;

       // Getters and setters
   }
   ```

2. **Proper Configuration Management**
   - Use environment-specific configurations
   - Secure sensitive configuration values

3. **Version Control and Documentation**
   - Keep KMS-related code well documented
   - Track key usage patterns in version control

4. **Code Reviews**
   - Conduct thorough code reviews for KMS-related code
   - Focus on security and error handling

## Implementation Checklists

### Key Setup Checklist
- [ ] Create appropriate KMS keys for different purposes
- [ ] Enable automatic key rotation
- [ ] Set up key aliases
- [ ] Configure IAM policies with least privilege
- [ ] Set up CloudTrail logging

### Implementation Checklist
- [ ] Use envelope encryption for large data
- [ ] Implement proper error handling
- [ ] Add comprehensive logging
- [ ] Set up monitoring and alarms
- [ ] Write comprehensive tests

### Security Checklist
- [ ] Never log sensitive data
- [ ] Use encryption context
- [ ] Implement proper access controls
- [ ] Clear sensitive data from memory
- [ ] Regularly audit access patterns

By following these best practices, you can ensure that your AWS KMS implementation is secure, performant, cost-effective, and maintainable.