# AWS RDS API Reference

## Core API Operations

### Describe Operations
- `describeDBInstances` - List database instances
- `describeDBParameterGroups` - List parameter groups
- `describeDBSnapshots` - List database snapshots
- `describeDBSubnetGroups` - List subnet groups

### Instance Management
- `createDBInstance` - Create new database instance
- `modifyDBInstance` - Modify existing instance
- `deleteDBInstance` - Delete database instance

### Parameter Groups
- `createDBParameterGroup` - Create parameter group
- `modifyDBParameterGroup` - Modify parameters
- `deleteDBParameterGroup` - Delete parameter group

### Snapshots
- `createDBSnapshot` - Create database snapshot
- `restoreDBInstanceFromDBSnapshot` - Restore from snapshot
- `deleteDBSnapshot` - Delete snapshot

## Key Data Models

### DBInstance
```java
String dbInstanceIdentifier()          // Instance name
String dbInstanceArn()                // ARN identifier
String engine()                        // Database engine
String engineVersion()                // Engine version
String dbInstanceClass()              // Instance type
int allocatedStorage()                 // Storage size in GB
Endpoint endpoint()                   // Connection endpoint
String dbInstanceStatus()             // Instance status
boolean multiAZ()                     // Multi-AZ enabled
boolean storageEncrypted()            // Storage encrypted
```

### DBParameter
```java
String parameterName()                // Parameter name
String parameterValue()               // Parameter value
String description()                 // Description
int applyMethod()                     // Apply method (immediate/reboot)
```

### CreateDbInstanceRequest Builder
```java
CreateDbInstanceRequest.builder()
    .dbInstanceIdentifier(identifier)
    .engine("postgres")                 // Database engine
    .engineVersion("15.2")             // Engine version
    .dbInstanceClass("db.t3.micro")    // Instance type
    .allocatedStorage(20)               // Storage size
    .masterUsername(username)          // Admin username
    .masterUserPassword(password)      // Admin password
    .publiclyAccessible(false)         // Public access
    .storageEncrypted(true)           // Storage encryption
    .multiAZ(true)                    // High availability
    .backupRetentionPeriod(7)          // Backup retention
    .deletionProtection(true)         // Protection from deletion
    .build()
```

## Error Handling

### Common Exceptions
- `DBInstanceNotFoundFault` - Instance doesn't exist
- `DBSnapshotAlreadyExistsFault` - Snapshot name conflicts
- `InsufficientDBInstanceCapacity` - Instance type unavailable
- `InvalidParameterValueException` - Invalid configuration value
- `StorageQuotaExceeded` - Storage limit reached

### Error Response Structure
```java
try {
    rdsClient.createDBInstance(request);
} catch (RdsException e) {
    // AWS specific error handling
    String errorCode = e.awsErrorDetails().errorCode();
    String errorMessage = e.awsErrorDetails().errorMessage();

    switch (errorCode) {
        case "DBInstanceNotFoundFault":
            // Handle missing instance
            break;
        case "InvalidParameterValueException":
            // Handle invalid parameters
            break;
        default:
            // Generic error handling
    }
}
```

## Pagination Support

### List Instances with Pagination
```java
DescribeDbInstancesRequest request = DescribeDbInstancesRequest.builder()
    .maxResults(100)                   // Limit results per page
    .build();

String marker = null;
do {
    if (marker != null) {
        request = request.toBuilder()
            .marker(marker)
            .build();
    }

    DescribeDbInstancesResponse response = rdsClient.describeDBInstances(request);
    List<DBInstance> instances = response.dbInstances();

    // Process instances

    marker = response.marker();
} while (marker != null);
```