---
name: aws-rds
description: AWS RDS (Relational Database Service) management using AWS SDK for Java 2.x. Use when working with RDS instances, creating databases, managing snapshots, parameter groups, or querying RDS metadata and configurations.
category: aws
tags: [aws, rds, database, java, sdk, postgresql, mysql, aurora]
version: 1.0.1
allowed-tools: Read, Write, Bash
---

# AWS RDS Skill

This skill provides comprehensive guidance for working with Amazon RDS (Relational Database Service) using the AWS SDK for Java 2.x, covering database instance management, snapshots, parameter groups, and RDS operations.

## When to Use This Skill

Use this skill when:
- Creating and managing RDS database instances (PostgreSQL, MySQL, Aurora, etc.)
- Taking and restoring database snapshots
- Managing DB parameter groups and configurations
- Querying RDS instance metadata and status
- Setting up Multi-AZ deployments
- Configuring automated backups
- Managing security groups for RDS
- Connecting Lambda functions to RDS databases
- Implementing RDS IAM authentication
- Monitoring RDS instances and metrics

## Core Concepts

### RDS Client Setup

The `RdsClient` is the main entry point for interacting with Amazon RDS.

**Basic Client Creation:**
```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsClient;
import software.amazon.awssdk.services.rds.model.*;

public class RdsExample {
    public static void main(String[] args) {
        Region region = Region.US_EAST_1;
        RdsClient rdsClient = RdsClient.builder()
            .region(region)
            .build();
        
        // Use client
        describeInstances(rdsClient);
        
        // Always close the client
        rdsClient.close();
    }
}
```

**Client with Custom Configuration:**
```java
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;

RdsClient rdsClient = RdsClient.builder()
    .region(Region.US_WEST_2)
    .credentialsProvider(ProfileCredentialsProvider.create("myprofile"))
    .httpClient(ApacheHttpClient.builder()
        .connectionTimeout(Duration.ofSeconds(30))
        .socketTimeout(Duration.ofSeconds(60))
        .build())
    .build();
```

### Describing DB Instances

Retrieve information about existing RDS instances.

**List All DB Instances:**
```java
public static void describeInstances(RdsClient rdsClient) {
    try {
        DescribeDbInstancesResponse response = rdsClient.describeDBInstances();
        List<DBInstance> instanceList = response.dbInstances();
        
        for (DBInstance instance : instanceList) {
            System.out.println("Instance ARN: " + instance.dbInstanceArn());
            System.out.println("Engine: " + instance.engine());
            System.out.println("Status: " + instance.dbInstanceStatus());
            System.out.println("Endpoint: " + instance.endpoint().address());
            System.out.println("Port: " + instance.endpoint().port());
            System.out.println("---");
        }
    } catch (RdsException e) {
        System.err.println(e.getMessage());
        System.exit(1);
    }
}
```

**Describe Specific Instance:**
```java
public static void describeSpecificInstance(RdsClient rdsClient, String instanceId) {
    try {
        DescribeDbInstancesRequest request = DescribeDbInstancesRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .build();
            
        DescribeDbInstancesResponse response = rdsClient.describeDBInstances(request);
        DBInstance instance = response.dbInstances().get(0);
        
        System.out.println("Instance ID: " + instance.dbInstanceIdentifier());
        System.out.println("Engine: " + instance.engine());
        System.out.println("Engine Version: " + instance.engineVersion());
        System.out.println("Instance Class: " + instance.dbInstanceClass());
        System.out.println("Storage: " + instance.allocatedStorage() + " GB");
        System.out.println("Multi-AZ: " + instance.multiAZ());
        System.out.println("Status: " + instance.dbInstanceStatus());
        
        if (instance.endpoint() != null) {
            System.out.println("Endpoint: " + instance.endpoint().address() + ":" + instance.endpoint().port());
        }
    } catch (RdsException e) {
        System.err.println("Error describing instance: " + e.getMessage());
    }
}
```

### Creating DB Instances

Create new RDS database instances with various configurations.

**Create Basic DB Instance:**
```java
public static String createDBInstance(RdsClient rdsClient, 
                                     String dbInstanceIdentifier,
                                     String dbName,
                                     String masterUsername,
                                     String masterPassword) {
    try {
        CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .dbName(dbName)
            .engine("postgres")
            .engineVersion("14.7")
            .dbInstanceClass("db.t3.micro")
            .allocatedStorage(20)
            .masterUsername(masterUsername)
            .masterUserPassword(masterPassword)
            .publiclyAccessible(false)
            .build();
            
        CreateDbInstanceResponse response = rdsClient.createDBInstance(request);
        System.out.println("Creating DB instance: " + response.dbInstance().dbInstanceArn());
        
        return response.dbInstance().dbInstanceArn();
    } catch (RdsException e) {
        System.err.println("Error creating instance: " + e.getMessage());
        throw e;
    }
}
```

**Create DB Instance with Advanced Options:**
```java
public static String createAdvancedDBInstance(RdsClient rdsClient,
                                             String dbInstanceIdentifier,
                                             String dbParameterGroupName,
                                             List<String> securityGroups) {
    try {
        CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .dbName("mydatabase")
            .engine("postgres")
            .engineVersion("15.2")
            .dbInstanceClass("db.r5.large")
            .allocatedStorage(100)
            .storageType("gp3")
            .iops(3000)
            .masterUsername("admin")
            .masterUserPassword("SecurePassword123!")
            .dbParameterGroupName(dbParameterGroupName)
            .vpcSecurityGroupIds(securityGroups)
            .availabilityZone("us-east-1a")
            .multiAZ(true)
            .backupRetentionPeriod(7)
            .preferredBackupWindow("03:00-04:00")
            .preferredMaintenanceWindow("mon:04:00-mon:05:00")
            .enableCloudwatchLogsExports("postgresql")
            .storageEncrypted(true)
            .publiclyAccessible(false)
            .deletionProtection(true)
            .build();
            
        CreateDbInstanceResponse response = rdsClient.createDBInstance(request);
        System.out.println("Created instance: " + response.dbInstance().dbInstanceIdentifier());
        
        return response.dbInstance().dbInstanceArn();
    } catch (RdsException e) {
        System.err.println("Error creating advanced instance: " + e.getMessage());
        throw e;
    }
}
```

### Managing DB Parameter Groups

Create and manage custom parameter groups for database configuration.

**Create DB Parameter Group:**
```java
public static void createDBParameterGroup(RdsClient rdsClient,
                                         String groupName,
                                         String description) {
    try {
        CreateDbParameterGroupRequest request = CreateDbParameterGroupRequest.builder()
            .dbParameterGroupName(groupName)
            .dbParameterGroupFamily("postgres15")
            .description(description)
            .build();
            
        CreateDbParameterGroupResponse response = rdsClient.createDBParameterGroup(request);
        System.out.println("Created parameter group: " + response.dbParameterGroup().dbParameterGroupName());
    } catch (RdsException e) {
        System.err.println("Error creating parameter group: " + e.getMessage());
        throw e;
    }
}
```

**Modify DB Parameter Group:**
```java
public static void modifyDBParameterGroup(RdsClient rdsClient,
                                         String groupName,
                                         Map<String, String> parameters) {
    try {
        List<Parameter> parameterList = parameters.entrySet().stream()
            .map(entry -> Parameter.builder()
                .parameterName(entry.getKey())
                .parameterValue(entry.getValue())
                .applyMethod(ApplyMethod.IMMEDIATE)
                .build())
            .collect(Collectors.toList());
            
        ModifyDbParameterGroupRequest request = ModifyDbParameterGroupRequest.builder()
            .dbParameterGroupName(groupName)
            .parameters(parameterList)
            .build();
            
        ModifyDbParameterGroupResponse response = rdsClient.modifyDBParameterGroup(request);
        System.out.println("Modified parameter group: " + response.dbParameterGroupName());
    } catch (RdsException e) {
        System.err.println("Error modifying parameter group: " + e.getMessage());
        throw e;
    }
}
```

**Describe DB Parameter Groups:**
```java
public static void describeDBParameterGroups(RdsClient rdsClient) {
    try {
        DescribeDbParameterGroupsResponse response = rdsClient.describeDBParameterGroups();
        
        response.dbParameterGroups().forEach(group -> {
            System.out.println("Group Name: " + group.dbParameterGroupName());
            System.out.println("Family: " + group.dbParameterGroupFamily());
            System.out.println("Description: " + group.description());
            System.out.println("---");
        });
    } catch (RdsException e) {
        System.err.println("Error describing parameter groups: " + e.getMessage());
    }
}
```

### Managing DB Snapshots

Create, restore, and manage database snapshots.

**Create DB Snapshot:**
```java
public static String createDBSnapshot(RdsClient rdsClient,
                                     String dbInstanceIdentifier,
                                     String snapshotIdentifier) {
    try {
        CreateDbSnapshotRequest request = CreateDbSnapshotRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .dbSnapshotIdentifier(snapshotIdentifier)
            .build();
            
        CreateDbSnapshotResponse response = rdsClient.createDBSnapshot(request);
        System.out.println("Creating snapshot: " + response.dbSnapshot().dbSnapshotIdentifier());
        
        return response.dbSnapshot().dbSnapshotArn();
    } catch (RdsException e) {
        System.err.println("Error creating snapshot: " + e.getMessage());
        throw e;
    }
}
```

**List DB Snapshots:**
```java
public static void describeDBSnapshots(RdsClient rdsClient) {
    try {
        DescribeDbSnapshotsResponse response = rdsClient.describeDBSnapshots();
        
        response.dbSnapshots().forEach(snapshot -> {
            System.out.println("Snapshot ID: " + snapshot.dbSnapshotIdentifier());
            System.out.println("Instance ID: " + snapshot.dbInstanceIdentifier());
            System.out.println("Status: " + snapshot.status());
            System.out.println("Created: " + snapshot.snapshotCreateTime());
            System.out.println("Size: " + snapshot.allocatedStorage() + " GB");
            System.out.println("---");
        });
    } catch (RdsException e) {
        System.err.println("Error describing snapshots: " + e.getMessage());
    }
}
```

**Restore from Snapshot:**
```java
public static String restoreDBFromSnapshot(RdsClient rdsClient,
                                          String snapshotIdentifier,
                                          String newInstanceIdentifier) {
    try {
        RestoreDbInstanceFromDbSnapshotRequest request = RestoreDbInstanceFromDbSnapshotRequest.builder()
            .dbSnapshotIdentifier(snapshotIdentifier)
            .dbInstanceIdentifier(newInstanceIdentifier)
            .dbInstanceClass("db.t3.micro")
            .publiclyAccessible(false)
            .build();
            
        RestoreDbInstanceFromDbSnapshotResponse response = rdsClient.restoreDBInstanceFromDBSnapshot(request);
        System.out.println("Restoring instance: " + response.dbInstance().dbInstanceIdentifier());
        
        return response.dbInstance().dbInstanceArn();
    } catch (RdsException e) {
        System.err.println("Error restoring from snapshot: " + e.getMessage());
        throw e;
    }
}
```

**Delete DB Snapshot:**
```java
public static void deleteDBSnapshot(RdsClient rdsClient, String snapshotIdentifier) {
    try {
        DeleteDbSnapshotRequest request = DeleteDbSnapshotRequest.builder()
            .dbSnapshotIdentifier(snapshotIdentifier)
            .build();
            
        DeleteDbSnapshotResponse response = rdsClient.deleteDBSnapshot(request);
        System.out.println("Deleted snapshot: " + response.dbSnapshot().dbSnapshotIdentifier());
    } catch (RdsException e) {
        System.err.println("Error deleting snapshot: " + e.getMessage());
        throw e;
    }
}
```

### Modifying DB Instances

Update existing RDS instances.

**Modify DB Instance:**
```java
public static void modifyDBInstance(RdsClient rdsClient,
                                   String dbInstanceIdentifier,
                                   String newInstanceClass) {
    try {
        ModifyDbInstanceRequest request = ModifyDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .dbInstanceClass(newInstanceClass)
            .applyImmediately(false) // Apply during maintenance window
            .build();
            
        ModifyDbInstanceResponse response = rdsClient.modifyDBInstance(request);
        System.out.println("Modified instance: " + response.dbInstance().dbInstanceIdentifier());
        System.out.println("New class: " + response.dbInstance().dbInstanceClass());
    } catch (RdsException e) {
        System.err.println("Error modifying instance: " + e.getMessage());
        throw e;
    }
}
```

**Enable Multi-AZ:**
```java
public static void enableMultiAZ(RdsClient rdsClient, String dbInstanceIdentifier) {
    try {
        ModifyDbInstanceRequest request = ModifyDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .multiAZ(true)
            .applyImmediately(false)
            .build();
            
        rdsClient.modifyDBInstance(request);
        System.out.println("Enabled Multi-AZ for: " + dbInstanceIdentifier);
    } catch (RdsException e) {
        System.err.println("Error enabling Multi-AZ: " + e.getMessage());
        throw e;
    }
}
```

### Deleting DB Instances

Delete RDS instances with optional final snapshot.

**Delete with Final Snapshot:**
```java
public static void deleteDBInstanceWithSnapshot(RdsClient rdsClient,
                                               String dbInstanceIdentifier,
                                               String finalSnapshotIdentifier) {
    try {
        DeleteDbInstanceRequest request = DeleteDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .skipFinalSnapshot(false)
            .finalDBSnapshotIdentifier(finalSnapshotIdentifier)
            .build();
            
        DeleteDbInstanceResponse response = rdsClient.deleteDBInstance(request);
        System.out.println("Deleting instance: " + response.dbInstance().dbInstanceIdentifier());
    } catch (RdsException e) {
        System.err.println("Error deleting instance: " + e.getMessage());
        throw e;
    }
}
```

**Delete without Snapshot:**
```java
public static void deleteDBInstanceNoSnapshot(RdsClient rdsClient,
                                             String dbInstanceIdentifier) {
    try {
        DeleteDbInstanceRequest request = DeleteDbInstanceRequest.builder()
            .dbInstanceIdentifier(dbInstanceIdentifier)
            .skipFinalSnapshot(true)
            .build();
            
        rdsClient.deleteDBInstance(request);
        System.out.println("Deleting instance without snapshot: " + dbInstanceIdentifier);
    } catch (RdsException e) {
        System.err.println("Error deleting instance: " + e.getMessage());
        throw e;
    }
}
```

## Spring Boot Integration

### Spring Boot Configuration

**Application Properties:**
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
```

**RDS Client Bean:**
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

**RDS Service:**
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
}
```

**REST Controller:**
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
}
```

## Lambda Integration

### Connecting Lambda to RDS

**Lambda Handler with RDS Connection:**
```java
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class RdsLambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent event, Context context) {
        APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();

        try {
            String connectionString = String.format(
                "jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true",
                System.getenv("ProxyHostName"),
                System.getenv("Port"),
                System.getenv("DBName")
            );

            try (Connection connection = DriverManager.getConnection(
                    connectionString,
                    System.getenv("DBUserName"),
                    System.getenv("DBPassword"));
                 PreparedStatement statement = connection.prepareStatement("SELECT COUNT(*) FROM users")) {

                try (ResultSet resultSet = statement.executeQuery()) {
                    if (resultSet.next()) {
                        int count = resultSet.getInt(1);
                        response.setStatusCode(200);
                        response.setBody("User count: " + count);
                    }
                }
            }
        } catch (Exception e) {
            response.setStatusCode(500);
            response.setBody("Error: " + e.getMessage());
        }

        return response;
    }
}
```

## Best Practices

### 1. Security

**Always use encryption:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .storageEncrypted(true)
    .kmsKeyId("arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012")
    .build();
```

**Use VPC security groups:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .vpcSecurityGroupIds("sg-12345678")
    .publiclyAccessible(false)
    .build();
```

### 2. High Availability

**Enable Multi-AZ for production:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .multiAZ(true)
    .build();
```

### 3. Backups

**Configure automated backups:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .backupRetentionPeriod(7)
    .preferredBackupWindow("03:00-04:00")
    .build();
```

### 4. Monitoring

**Enable CloudWatch logs:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .enableCloudwatchLogsExports("postgresql", "upgrade")
    .build();
```

### 5. Cost Optimization

**Use appropriate instance class:**
```java
// Development
.dbInstanceClass("db.t3.micro")

// Production
.dbInstanceClass("db.r5.large")
```

### 6. Deletion Protection

**Enable for production databases:**
```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .deletionProtection(true)
    .build();
```

### 7. Resource Management

**Always close clients:**
```java
try (RdsClient rdsClient = RdsClient.builder().region(Region.US_EAST_1).build()) {
    // Use client
} // Automatically closed
```

## Maven Dependencies

```xml
<dependencies>
    <!-- AWS SDK for RDS -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>rds</artifactId>
        <version>2.20.0</version>
    </dependency>
    
    <!-- PostgreSQL Driver -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <version>42.6.0</version>
    </dependency>
    
    <!-- MySQL Driver -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>8.0.33</version>
    </dependency>
</dependencies>
```

## Gradle Dependencies

```gradle
dependencies {
    // AWS SDK for RDS
    implementation 'software.amazon.awssdk:rds:2.20.0'
    
    // PostgreSQL Driver
    implementation 'org.postgresql:postgresql:42.6.0'
    
    // MySQL Driver
    implementation 'mysql:mysql-connector-java:8.0.33'
}
```

## Summary

This AWS RDS skill covers:

1. **Client Setup**: RdsClient configuration and initialization
2. **Instance Management**: Create, describe, modify, delete DB instances
3. **Parameter Groups**: Custom configuration management
4. **Snapshots**: Create, restore, manage database backups
5. **Spring Boot Integration**: Configuration and service implementation
6. **Lambda Integration**: Connecting serverless functions to RDS
7. **Security**: Encryption, VPC, IAM authentication
8. **High Availability**: Multi-AZ deployments
9. **Monitoring**: CloudWatch integration
10. **Best Practices**: Security, backups, resource management

All patterns are based on official AWS SDK for Java 2.x documentation and represent modern cloud-native database management practices.
