# Spring Boot Integration with AWS RDS

## Configuration

### application.properties
```properties
# AWS Configuration
aws.region=us-east-1
aws.rds.instance-identifier=mydb-instance

# RDS Connection (from RDS endpoint)
spring.datasource.url=jdbc:postgresql://mydb.abc123.us-east-1.rds.amazonaws.com:5432/mydatabase
spring.datasource.username=admin
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA Configuration
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

# Connection Pool Configuration
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.idle-timeout=30000
spring.datasource.hikari.connection-timeout=20000
```

### AWS Configuration
```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsClient;

@Configuration
public class AwsRdsConfig {

    @Value("${aws.region}")
    private String awsRegion;

    @Bean
    public RdsClient rdsClient() {
        return RdsClient.builder()
            .region(Region.of(awsRegion))
            .build();
    }
}
```

### Service Layer
```java
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.rds.RdsClient;
import software.amazon.awssdk.services.rds.model.*;
import java.util.List;

@Service
public class RdsService {

    private final RdsClient rdsClient;

    public RdsService(RdsClient rdsClient) {
        this.rdsClient = rdsClient;
    }

    public List<DBInstance> listInstances() {
        DescribeDbInstancesResponse response = rdsClient.describeDBInstances();
        return response.dbInstances();
    }

    public DBInstance getInstanceDetails(String instanceId) {
        DescribeDbInstancesRequest request = DescribeDbInstancesRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .build();

        DescribeDbInstancesResponse response = rdsClient.describeDBInstances(request);
        return response.dbInstances().get(0);
    }

    public String createSnapshot(String instanceId, String snapshotId) {
        CreateDbSnapshotRequest request = CreateDbSnapshotRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .dbSnapshotIdentifier(snapshotId)
            .build();

        CreateDbSnapshotResponse response = rdsClient.createDBSnapshot(request);
        return response.dbSnapshot().dbSnapshotArn();
    }

    public void modifyInstance(String instanceId, String newInstanceClass) {
        ModifyDbInstanceRequest request = ModifyDbInstanceRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .dbInstanceClass(newInstanceClass)
            .applyImmediately(true)
            .build();

        rdsClient.modifyDBInstance(request);
    }
}
```

### REST Controller
```java
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import software.amazon.awssdk.services.rds.model.DBInstance;
import java.util.List;

@RestController
@RequestMapping("/api/rds")
public class RdsController {

    private final RdsService rdsService;

    public RdsController(RdsService rdsService) {
        this.rdsService = rdsService;
    }

    @GetMapping("/instances")
    public ResponseEntity<List<DBInstance>> listInstances() {
        return ResponseEntity.ok(rdsService.listInstances());
    }

    @GetMapping("/instances/{id}")
    public ResponseEntity<DBInstance> getInstanceDetails(@PathVariable String id) {
        return ResponseEntity.ok(rdsService.getInstanceDetails(id));
    }

    @PostMapping("/snapshots")
    public ResponseEntity<String> createSnapshot(
            @RequestParam String instanceId,
            @RequestParam String snapshotId) {
        String arn = rdsService.createSnapshot(instanceId, snapshotId);
        return ResponseEntity.ok(arn);
    }

    @PutMapping("/instances/{id}")
    public ResponseEntity<String> modifyInstance(
            @PathVariable String id,
            @RequestParam String instanceClass) {
        rdsService.modifyInstance(id, instanceClass);
        return ResponseEntity.ok("Instance modified successfully");
    }
}
```

### Exception Handling
```java
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class RdsExceptionHandler {

    @ExceptionHandler(RdsException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleRdsException(RdsException e) {
        return new ErrorResponse(
            "RDS_ERROR",
            e.getMessage(),
            e.awsErrorDetails().errorCode()
        );
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleGenericException(Exception e) {
        return new ErrorResponse(
            "INTERNAL_ERROR",
            e.getMessage()
        );
    }
}

class ErrorResponse {
    private String code;
    private String message;
    private String details;

    // Constructor, getters, setters
}
```

## Testing

### Unit Tests
```java
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class RdsServiceTest {

    @Mock
    private RdsClient rdsClient;

    @Test
    void listInstances_shouldReturnInstances() {
        // Arrange
        DescribeDbInstancesResponse response = DescribeDbInstancesResponse.builder()
            .dbInstances(List.of(createTestInstance()))
            .build();

        when(rdsClient.describeDBInstances()).thenReturn(response);

        RdsService service = new RdsService(rdsClient);

        // Act
        List<DBInstance> result = service.listInstances();

        // Assert
        assertEquals(1, result.size());
        verify(rdsClient).describeDBInstances();
    }

    private DBInstance createTestInstance() {
        return DBInstance.builder()
            .dbInstanceIdentifier("test-instance")
            .engine("postgres")
            .dbInstanceStatus("available")
            .build();
    }
}
```

### Integration Tests
```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles = "test"
class RdsServiceIntegrationTest {

    @Autowired
    private RdsService rdsService;

    @Test
    void listInstances_integrationTest() {
        // This test requires actual AWS credentials and RDS instances
        // Should only run with proper test configuration
        assumeTrue(false, "Integration test disabled");

        List<DBInstance> instances = rdsService.listInstances();
        assertNotNull(instances);
    }
}
```

## Best Practices

### 1. Configuration Management
- Use Spring profiles for different environments
- Externalize sensitive configuration (passwords, keys)
- Use Spring Cloud Config for multi-environment management

### 2. Connection Pooling
```properties
# HikariCP Configuration
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=10
spring.datasource.hikari.idle-timeout=600000
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.connection-test-query=SELECT 1
```

### 3. Retry Logic
```java
import org.springframework.retry.annotation.Retryable;
import org.springframework.retry.annotation.Backoff;

@Service
public class RdsServiceWithRetry {

    private final RdsClient rdsClient;

    @Retryable(value = { RdsException.class },
               maxAttempts = 3,
               backoff = @Backoff(delay = 1000))
    public List<DBInstance> listInstancesWithRetry() {
        return rdsClient.describeDBInstances().dbInstances();
    }
}
```

### 4. Monitoring
```java
import org.springframework.boot.actuator.health.Health;
import org.springframework.boot.actuator.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class RdsHealthIndicator implements HealthIndicator {

    private final RdsClient rdsClient;

    public RdsHealthIndicator(RdsClient rdsClient) {
        this.rdsClient = rdsClient;
    }

    @Override
    public Health health() {
        try {
            rdsClient.describeDBInstances();
            return Health.up()
                .withDetail("service", "RDS")
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```