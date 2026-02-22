---
name: aws-sdk-java-v2-rds
description: Provides AWS RDS (Relational Database Service) management patterns using AWS SDK for Java 2.x. Use when creating, modifying, monitoring, or managing Amazon RDS database instances, snapshots, parameter groups, and configurations.
category: aws
tags: [aws, rds, database, java, sdk, postgresql, mysql, aurora, spring-boot]
version: 2.2.0
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# AWS SDK for Java v2 - RDS Management

## Overview

Comprehensive guidance for working with Amazon RDS using the AWS SDK for Java 2.x, covering database instance management, snapshots, parameter groups, and integration patterns.

## When to Use

- Creating and managing RDS database instances (PostgreSQL, MySQL, Aurora)
- Taking and restoring database snapshots
- Managing DB parameter groups and configurations
- Setting up Multi-AZ deployments and automated backups
- Implementing RDS IAM authentication
- Integrating with Spring Boot or Lambda functions

## Instructions

1. **Add Dependencies** - Include AWS RDS SDK dependency and database drivers
2. **Create RDS Client** - Instantiate RdsClient with proper region and credentials
3. **Create DB Instance** - Use createDBInstance() with appropriate configuration
4. **Configure Security** - Set up VPC security groups and encryption
5. **Set Up Backups** - Configure automated backup windows and retention
6. **Monitor Status** - Use describeDBInstances() to check instance state
7. **Create Snapshots** - Take manual snapshots before major changes

## Examples

### Client Setup

```java
RdsClient rdsClient = RdsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### Create Secure PostgreSQL Instance

```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .dbInstanceIdentifier(instanceIdentifier)
    .dbName(dbName)
    .engine("postgres")
    .engineVersion("15.4")
    .dbInstanceClass("db.t3.micro")
    .allocatedStorage(20)
    .masterUsername(masterUsername)
    .masterUserPassword(masterPassword)
    .storageEncrypted(true)
    .vpcSecurityGroupIds(vpcSecurityGroupId)
    .publiclyAccessible(false)
    .multiAZ(true)
    .backupRetentionPeriod(7)
    .deletionProtection(true)
    .build();

CreateDbInstanceResponse response = rdsClient.createDBInstance(request);
```

### Create Snapshot

```java
CreateDbSnapshotResponse response = rdsClient.createDBSnapshot(
    CreateDbSnapshotRequest.builder()
        .dbInstanceIdentifier(instanceId)
        .dbSnapshotIdentifier(snapshotId)
        .build());
```

### Wait for Availability

```java
rdsClient.waiter().waitUntilDBInstanceAvailable(
    DescribeDbInstancesRequest.builder()
        .dbInstanceIdentifier(instanceId).build());
```

## Best Practices

- **Always use encryption** with `storageEncrypted(true)`
- **Use VPC security groups** with `publiclyAccessible(false)`
- **Enable Multi-AZ** for production deployments
- **Configure automated backups** with appropriate retention period
- **Enable deletion protection** for production databases
- **Enable CloudWatch logs** for monitoring
- **Always close clients** using try-with-resources

## Constraints and Warnings

- AWS accounts have limits on DB instances per region
- Maximum storage varies by engine and instance class
- Multi-AZ deployments approximately double compute costs
- Instances may be unavailable during maintenance windows
- Manual snapshots are billed based on storage used
- Not all database engines support IAM authentication

## References

- [API Reference](references/api-reference.md)
- [Spring Boot Integration](references/spring-boot-integration.md)
- [Lambda Integration](references/lambda-integration.md)
