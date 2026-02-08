# AWS CloudFormation DynamoDB Reference Guide

## AWS::DynamoDB::Table Resource

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AttributeDefinitions | List | Yes | Attributes that describe the key schema |
| KeySchema | List | Yes | Primary key structure (partition key + optional sort key) |
| TableName | String | No | Name of the table (auto-generated if not specified) |
| BillingMode | String | No | Billing mode: PAY_PER_REQUEST or PROVISIONED |
| ProvisionedThroughput | ProvisionedThroughput | Conditionally | RCU/WCU for PROVISIONED mode |
| GlobalSecondaryIndexes | List | No | List of global secondary indexes |
| LocalSecondaryIndexes | List | No | List of local secondary indexes |
| StreamSpecification | StreamSpecification | No | DynamoDB Streams configuration |
| SSESpecification | SSESpecification | No | Server-side encryption settings |
| PointInTimeRecoverySpecification | PointInTimeRecoverySpecification | No | Point-in-time recovery settings |
| TimeToLiveSpecification | TimeToLiveSpecification | No | TTL settings for automatic data expiration |
| Tags | List | No | Tags for resource management |

### AttributeDefinitions

```yaml
AttributeDefinitions:
  - AttributeName: pk
    AttributeType: S  # String
  - AttributeName: sk
    AttributeType: N  # Number
  - AttributeName: data
    AttributeType: B  # Binary
```

**AttributeType values:**
- `S` - String
- `N` - Number
- `B` - Binary

### KeySchema

```yaml
KeySchema:
  - AttributeName: pk
    KeyType: HASH  # Partition key
  - AttributeName: sk
    KeyType: RANGE  # Sort key (optional)
```

**KeyType values:**
- `HASH` - Partition key
- `RANGE` - Sort key

### ProvisionedThroughput

```yaml
ProvisionedThroughput:
  ReadCapacityUnits: 5
  WriteCapacityUnits: 5
```

**Limits:**
- Minimum: 1 RCU/WCU
- Maximum: 40,000 RCU/WCU per table
- For higher limits: request through AWS Support

### GlobalSecondaryIndex

```yaml
GlobalSecondaryIndexes:
  - IndexName: my-index
    KeySchema:
      - AttributeName: gsi_pk
        KeyType: HASH
      - AttributeName: gsi_sk
        KeyType: RANGE
    Projection:
      ProjectionType: ALL  # ALL, KEYS_ONLY, INCLUDE
      NonKeyAttributes:
        - attribute1
        - attribute2
    ProvisionedThroughput:
      ReadCapacityUnits: 5
      WriteCapacityUnits: 5
```

### LocalSecondaryIndex

```yaml
LocalSecondaryIndexes:
  - IndexName: my-lsi
    KeySchema:
      - AttributeName: pk
        KeyType: HASH
      - AttributeName: lsi_sk
        KeyType: RANGE
    Projection:
      ProjectionType: ALL
```

### StreamSpecification

```yaml
StreamSpecification:
  StreamViewType: NEW_AND_OLD_IMAGES
```

**StreamViewType values:**
- `KEYS_ONLY` - Only key attributes
- `NEW_IMAGE` - Entire item after change
- `OLD_IMAGE` - Entire item before change
- `NEW_AND_OLD_IMAGES` - Both before and after

### SSESpecification

```yaml
SSESpecification:
  SSEEnabled: true
  SSEType: AES256  # or KMS
  KMSMasterKeyId: arn:aws:kms:region:account:key/key-id
```

### PointInTimeRecoverySpecification

```yaml
PointInTimeRecoverySpecification:
  PointInTimeRecoveryEnabled: true
```

### TimeToLiveSpecification

```yaml
TimeToLiveSpecification:
  AttributeName: ttl
  Enabled: true
```

## AWS::ApplicationAutoScaling::ScalableTarget

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ServiceNamespace | String | Yes | Must be `dynamodb` |
| ResourceId | String | Yes | Table or index identifier |
| ScalableDimension | String | Yes | dynamodb:table:ReadCapacityUnits, dynamodb:table:WriteCapacityUnits, dynamodb:index:ReadCapacityUnits, dynamodb:index:WriteCapacityUnits |
| MinCapacity | Number | Yes | Minimum scalable capacity |
| MaxCapacity | Number | Yes | Maximum scalable capacity |
| RoleARN | String | Yes | Auto scaling role ARN |

### ResourceId Formats

- Table: `table/{table-name}`
- GSI: `table/{table-name}/index/{index-name}`

## AWS::ApplicationAutoScaling::ScalingPolicy

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PolicyName | String | Yes | Name of the scaling policy |
| PolicyType | String | Yes | TargetTrackingScaling or StepScaling |
| ScalingTargetId | String | Yes | Reference to ScalableTarget |
| TargetTrackingScalingPolicyConfiguration | Configuration | Yes | Target tracking configuration |

### TargetTrackingScalingPolicyConfiguration

```yaml
TargetTrackingScalingPolicyConfiguration:
  PredefinedMetricSpecification:
    PredefinedMetricType: DynamoDBReadCapacityUtilization | DynamoDBWriteCapacityUtilization
  TargetValue: 70
  ScaleInCooldown: 60
  ScaleOutCooldown: 60
  DisableScaleIn: false
```

## Intrinsic Functions Reference

### !GetAtt

```yaml
TableArn: !GetAtt MyTable.Arn
TableName: !Ref MyTable
StreamArn: !GetAtt MyTable.StreamArn
```

### !Ref

```yaml
TableName: !Ref MyDynamoDBTable
```

### !ImportValue

```yaml
TableName: !ImportValue !Sub "${NetworkStackName}-TableName"
```

### !FindInMap

```yaml
ReadCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, ReadCapacity]
```

## Capacity Units Explained

### Read Capacity Units (RCU)

- One RCU = 1 strongly consistent read per second for items up to 4 KB
- One RCU = 2 eventually consistent reads per second for items up to 4 KB

### Write Capacity Units (WCU)

- One WCU = 1 write per second for items up to 1 KB

### Example Calculations

For 10 items per second, 2 KB each, strongly consistent:
- RCU needed: 10 * (2 / 4) = 5 RCU
- WCU needed: 10 * (2 / 1) = 20 WCU

## Limits and Quotas

### Table Limits

| Resource | Limit |
|----------|-------|
| Tables per account | 2,500 |
| Attributes per table | 100,000,000 items (total size) |
| Item size | 400 KB maximum |

### Index Limits

| Resource | Limit |
|----------|-------|
| GSIs per table | 20 |
| LSIs per table | 5 (one per sort key) |
| Attributes per index | 20 |
| Projected attributes | Unlimited |

### Throughput Limits

| Resource | Limit |
|----------|-------|
| RCU per table | 40,000 (default) |
| WCU per table | 40,000 (default) |
| RCU per GSI | 40,000 (default) |
| WCU per GSI | 40,000 (default) |

## Key Patterns and Anti-Patterns

### Good Partition Key Patterns

```yaml
# Good: High cardinality, uniform distribution
KeySchema:
  - AttributeName: user_id
    KeyType: HASH
```

```yaml
# Good: Composite key for range queries
KeySchema:
  - AttributeName: pk
    KeyType: HASH
  - AttributeName: sk
    KeyType: RANGE
```

### Bad Partition Key Patterns

```yaml
# Bad: Low cardinality (only a few values)
KeySchema:
  - AttributeName: status
    KeyType: HASH
```

```yaml
# Bad: Time-based keys (hot partitions)
KeySchema:
  - AttributeName: timestamp
    KeyType: HASH
```

### GSI Design Considerations

- GSI partition key should have high cardinality
- GSI throughput is separate from table throughput
- GSI can only project attributes from the table
- LSI must use same partition key as table

## IAM Permissions

### Table Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/table-name"
    }
  ]
}
```

### Index Access

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:Query"
  ],
  "Resource": "arn:aws:dynamodb:region:account:table/table-name/index/index-name"
}
```

### Stream Access

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetRecords",
    "dynamodb:GetShardIterator",
    "dynamodb:DescribeStream",
    "dynamodb:ListStreams"
  ],
  "Resource": "arn:aws:dynamodb:region:account:table/table-name/stream/*"
}
```
