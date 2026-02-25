# Data Operations Beast: S3, DynamoDB, RDS

## S3 Advanced Patterns

### Bulk Operations

#### S3 Sync Patterns

```bash
# Standard sync
aws s3 sync s3://source-bucket/ s3://dest-bucket/

# Sync with delete (removes files not in source)
aws s3 sync s3://source-bucket/ s3://dest-bucket/ --delete

# Sync with storage class
aws s3 sync ./data s3://my-bucket/ --storage-class STANDARD_IA

# Sync with encryption
aws s3 sync ./data s3://my-bucket/ --sse AES256

# Sync with metadata
aws s3 sync ./data s3://my-bucket/ --metadata "Cache-Control=max-age=3600"
```

#### Multipart Upload for Large Files

```bash
# Manual multipart upload
aws s3api create-multipart-upload \
  --bucket my-bucket \
  --key large-file.tar.gz

# Upload parts
aws s3api upload-part \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --part-number 1 \
  --body part1.tar.gz \
  --upload-id "multipart-upload-id"

# Complete multipart upload
aws s3api complete-multipart-upload \
  --bucket my-bucket \
  --key large-file.tar.gz \
  --upload-id "multipart-upload-id" \
  --multipart-upload '{"Parts": [{"ETag": "part1-etag", "PartNumber": 1}]}'
```

#### S3 Batch Operations

```bash
# List all objects with pagination
aws s3api list-objects-v2 \
  --bucket my-bucket \
  --prefix logs/ \
  --page-size 1000

# Get all object versions
aws s3api list-object-versions \
  --bucket my-bucket \
  --prefix data/

# Delete objects in bulk
aws s3api delete-objects \
  --bucket my-bucket \
  --delete '{"Objects": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]}'

# Use objects filter file for bulk delete
aws s3api delete-objects \
  --bucket my-bucket \
  --delete file://delete-objects.json
```

### Lifecycle Policies

#### Configure Lifecycle Rules

```bash
# Put lifecycle configuration
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-bucket \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
# {
#   "Rules": [
#     {
#       "ID": "ArchiveOldLogs",
#       "Status": "Enabled",
#       "Filter": {
#         "Prefix": "logs/"
#       },
#       "Transitions": [
#         {"Days": 30, "StorageClass": "STANDARD_IA"},
#         {"Days": 90, "StorageClass": "GLACIER"},
#         {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
#       ],
#       "Expiration": {"Days": 730}
#     },
#     {
#       "ID": "DeleteIncompleteUploads",
#       "Status": "Enabled",
#       "Filter": {
#         "Prefix": "uploads/"
#       },
#       "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7}
#     }
#   ]
# }
```

### Replication

#### Configure Cross-Region Replication

```bash
# Enable versioning first
aws s3api put-bucket-versioning \
  --bucket source-bucket \
  --versioning-configuration Status=Enabled

# Create IAM role for replication
aws iam create-role \
  --role-name s3-replication-role \
  --assume-role-policy-document file://trust-policy.json

# Attach replication policy
aws iam put-role-policy \
  --role-name s3-replication-role \
  --policy-name replication-policy \
  --policy-document file://replication-policy.json

# Configure replication
aws s3api put-bucket-replication \
  --bucket source-bucket \
  --replication-configuration file://replication.json
```

### Security Auditing

#### Bucket Policy Operations

```bash
# Get bucket policy
aws s3api get-bucket-policy --bucket my-bucket --query Policy --output text | python3 -m json.tool

# Check public access
aws s3api get-public-access-block --bucket my-bucket

# Get bucket encryption
aws s3api get-bucket-encryption --bucket my-bucket

# List bucket ACL
aws s3api get-bucket-acl --bucket my-bucket
```

### Presigned URLs

#### Generate Presigned URLs

```bash
# Presigned URL for download (1 hour)
aws s3 presign s3://my-bucket/file.txt --expires-in 3600

# Presigned URL for upload
aws s3 presign s3://my-bucket/upload.txt --expires-in 3600 --put

# Programmatic presigned URL
aws s3 presign s3://my-bucket/data.json --expires-in 86400
```

### S3 Access Points

#### Manage Access Points

```bash
# Create access point
aws s3control create-access-point \
  --account-id 123456789012 \
  --name my-access-point \
  --bucket my-bucket

# Configure access point policy
aws s3control put-access-point-policy \
  --account-id 123456789012 \
  --name my-access-point \
  --policy file://ap-policy.json
```

## DynamoDB Advanced Patterns

### Query Operations

#### Advanced Queries

```bash
# Query with key condition
aws dynamodb query \
  --table-name users \
  --key-condition-expression "PK = :pk AND begins_with(SK, :sk)" \
  --expression-attribute-values '{"pk":{"S":"USER#123"},"sk":{"S":"ORDER#"}}'

# Query with filter
aws dynamodb query \
  --table-name products \
  --key-condition-expression "Category = :cat" \
  --filter-expression "Price > :minPrice" \
  --expression-attribute-values '{":cat":{"S":"Electronics"},":minPrice":{"N":"100"}}'

# Query with projection
aws dynamodb query \
  --table-name orders \
  --key-condition-expression "CustomerId = :cid" \
  --projection-expression "OrderId, OrderDate, TotalAmount" \
  --expression-attribute-values '{":cid":{"S":"CUST#456"}}'
```

### Scan Operations

#### Efficient Scanning

```bash
# Parallel scan with segments
aws dynamodb scan \
  --table-name large-table \
  --segment 0 \
  --total-segments 4 \
  --output json

# Scan with filter
aws dynamodb scan \
  --table-name logs \
  --filter-expression "#t > :threshold" \
  --expression-attribute-names '{"#t":"timestamp"}' \
  --expression-attribute-values '{":threshold":{"N":"1640000000"}}'

# Scan with pagination
aws dynamodb scan \
  --table-name my-table \
  --page-size 100 \
  --max-items 1000
```

### Batch Operations

#### Batch Get and Write

```bash
# Batch get item (up to 100 items)
aws dynamodb batch-get-item \
  --request-items '{
    "Table1": {
      "Keys": [{"PK":{"S":"A"}},{"PK":{"S":"B"}}],
      "ProjectionExpression": "PK, SK, Data"
    }
  }'

# Batch write (up to 25 items)
aws dynamodb batch-write-item \
  --request-items '{
    "Table1": [
      {"PutRequest": {"Item": {"PK":{"S":"A"},"Data":{"S":"Value"}}}},
      {"DeleteRequest": {"Key": {"PK":{"S":"B"}}}}
    ]
  }'

# Use items file for complex operations
aws dynamodb batch-write-item --request-items file://items.json
```

### Time to Live (TTL)

#### Manage TTL

```bash
# Enable TTL on table
aws dynamodb update-time-to-live \
  --table-name sessions \
  --time-to-live-specification "Enabled=true, AttributeName=expiresAt"

# Check TTL status
aws dynamodb describe-time-to-live --table-name sessions

# Get expired items
aws dynamodb scan \
  --table-name sessions \
  --filter-expression "expiresAt < :now" \
  --expression-attribute-values '{":now":{"N":"1640000000"}}'
```

### Global Tables

#### Manage Global Tables

```bash
# Create global table
aws dynamodb create-global-table \
  --global-table-name my-global-table \
  --replication-group RegionName=us-east-1

# Describe global table
aws dynamodb describe-global-table --global-table-name my-global-table
```

### Backup and Restore

#### Backup Operations

```bash
# Create on-demand backup
aws dynamodb create-backup \
  --table-name my-table \
  --backup-name "backup-$(date +%Y%m%d)"

# List backups
aws dynamodb list-backups --table-name my-table

# Restore table
aws dynamodb restore-table-from-backup \
  --target-table-name my-table-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:123456789012:table/my-table/backup/1234567890
```

## RDS Advanced Patterns

### Instance Management

#### Instance Operations

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier my-db \
  --engine postgres \
  --db-instance-class db.t3.micro \
  --allocated-storage 20 \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --vpc-security-group-ids sg-12345678

# Modify instance
aws rds modify-db-instance \
  --db-instance-identifier my-db \
  --db-instance-class db.t3.small \
  --allocated-storage 50 \
  --apply-immediately

# Delete instance (create snapshot first)
aws rds delete-db-instance \
  --db-instance-identifier my-db \
  --skip-final-snapshot \
  --final-db-snapshot-name my-final-snapshot
```

### Snapshot Management

#### Snapshot Operations

```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier my-db \
  --db-snapshot-identifier "snapshot-$(date +%Y%m%d)"

# Copy snapshot
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:source \
  --target-db-snapshot-identifier target-snapshot \
  --kms-key-id alias/my-key

# Share snapshot
aws rds modify-db-snapshot-attribute \
  --db-snapshot-identifier my-snapshot \
  --attribute-name restore \
  --values-to-add '["123456789012", "all"]'

# List shared snapshots
aws rds describe-db-snapshots-shared-by --max-records 100
```

### Parameter Groups

#### Parameter Group Management

```bash
# Create parameter group
aws rds create-db-parameter-group \
  --db-parameter-group-name my-pg \
  --db-parameter-group-family postgres14 \
  --description "Custom parameter group"

# Modify parameters
aws rds modify-db-parameter-group \
  --db-parameter-group-name my-pg \
  --parameters '[{"ParameterName":"max_connections","ParameterValue":"200","ApplyMethod":"immediate"}]'

# Reset parameters
aws rds reset-db-parameter-group \
  --db-parameter-group-name my-pg \
  --reset-all-parameters
```

### Read Replicas

#### Manage Read Replicas

```bash
# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier my-replica \
  --source-db-instance-identifier my-db \
  --availability-zone us-east-1a

# Promote read replica
aws rds promote-read-replica \
  --db-instance-identifier my-replica

# Monitor replica lag
aws rds describe-db-instances \
  --db-instance-identifier my-replica \
  --query 'DBInstances[0].ReadReplicaSourceDBInstanceIdentifier'
```

### Multi-AZ Deployment

#### Configure Multi-AZ

```bash
# Modify for Multi-AZ
aws rds modify-db-instance \
  --db-instance-identifier my-db \
  --multi-az \
  --apply-immediately

# Failover to standby
aws rds failover-db-instance \
  --db-instance-identifier my-db

# Describe DB instances status
aws rds describe-db-instances \
  --query 'DBInstances[].{ID:DBInstanceIdentifier,Status:DBInstanceStatus,AZ:AvailabilityZone,MultiAZ:MultiAZ}'
```

### Enhanced Monitoring

#### Enable Monitoring

```bash
# Enable enhanced monitoring
aws rds modify-db-instance \
  --db-instance-identifier my-db \
  --monitoring-interval 60 \
  --monitoring-role-arn arn:aws:iam::123456789012:role/rds-monitoring-role

# Get monitoring metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --start-time $(date -d "1 hour ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Average \
  --dimensions Name=DBInstanceIdentifier,Value=my-db
```

### Performance Insights

#### Use Performance Insights

```bash
# Enable Performance Insights
aws rds modify-db-instance \
  --db-instance-identifier my-db \
  --enable-performance-insights \
  --performance-insights-kms-key-id alias/my-key

# Get performance insights metrics
aws pi get-resource-metrics \
  --service-type RDS \
  --identifier db-ABC123 \
  --metric-queries '[{"Metric":"os.cpuUtilization.user"}]'
```

## Data Operations Best Practices

1. **S3**: Use appropriate storage classes, enable lifecycle policies, enable versioning
2. **DynamoDB**: Use on-demand capacity for unpredictable workloads, use GSIs for queries
3. **RDS**: Enable Multi-AZ for production, use read replicas for scaling
4. **All**: Implement proper backup strategies, enable encryption at rest
5. **Monitoring**: Use CloudWatch metrics and alarms for all data services
6. **Security**: Use IAM policies with least-privilege, enable VPC endpoints
