# Compute Mastery: EC2 and Lambda

## EC2 Advanced Patterns

### Instance Management

#### List All Instances with Details

```bash
# Comprehensive instance listing with tags
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[{
    Id: InstanceId,
    Type: InstanceType,
    State: State.Name,
    PrivateIP: PrivateIpAddress,
    PublicIP: PublicIpAddress,
    Name: Tags[?Key==`Name`].Value | [0],
    Env: Tags[?Key==`Environment`].Value | [0],
    AZ: Placement.AvailabilityZone,
    Subnet: SubnetId,
    VpcId: VpcId
  }]' \
  --output table
```

#### Instance Lifecycle Operations

```bash
# Start instances with validation
aws ec2 describe-instances \
  --instance-ids i-1234567890abcdef0 \
  --query 'Reservations[0].Instances[0].State.Name'

aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 wait instance-running --instance-ids i-1234567890abcdef0

# Graceful stop with shutdown script
aws ec2 stop-instances --instance-ids i-1234567890abcdef0 --force

# Reboot with wait
aws ec2 reboot-instances --instance-ids i-1234567890abcdef0
aws ec2 wait instance-status-ok --instance-ids i-1234567890abcdef0
```

#### Instance Metadata

```bash
# Get instance metadata
curl -s http://169.254.169.254/latest/meta-data/

# Get specific metadata
curl -s http://169.254.169.254/latest/meta-data/instance-id
curl -s http://169.254.169.254/latest/meta-data/ami-id
curl -s http://169.254.169.254/latest/meta-data/security-groups

# Get user data (if available)
curl -s http://169.254.169.254/latest/user-data/
```

### Spot Instance Management

#### Request Spot Fleet

```bash
# Create spot fleet request
aws ec2 request-spot-fleet \
  --spot-fleet-request-config file://spot-config.json

# spot-config.json
# {
#   "SpotFleetRequestConfig": {
#     "AllocationStrategy": "lowestPrice",
#     "TargetCapacity": 10,
#     "LaunchSpecifications": [
#       {
#         "ImageId": "ami-0c55b159cbfafe1f0",
#         "InstanceType": "t3.medium",
#         "SubnetId": "subnet-12345678",
#         "IamFleetRole": "arn:aws:iam::123456789012:role/fleet-role"
#       }
#     ]
#   }
# }
```

#### Cancel Spot Requests

```bash
# Cancel spot requests
aws ec2 cancel-spot-fleet-requests \
  --spot-fleet-request-ids sfr-12345678-1234-1234-1234-123456789012 \
  --terminate-instances
```

### Auto Scaling Groups

#### ASG Operations

```bash
# List ASGs with desired capacity
aws autoscaling describe-auto-scaling-groups \
  --query 'AutoScalingGroups[].[AutoScalingGroupName, MinSize, MaxSize, DesiredCapacity, AvailabilityZones[]]' \
  --output table

# Update ASG capacity
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 5

# Scale up immediately
aws autoscaling execute-policy \
  --auto-scaling-group-name my-asg \
  --policy-name scale-up-policy
```

### Security Groups Management

#### List and Analyze Security Groups

```bash
# Get all security groups with rules
aws ec2 describe-security-groups \
  --query 'SecurityGroups[].{
    Name: GroupName,
    Id: GroupId,
    VPC: VpcId,
    Rules: IpPermissions
  }' \
  --output json > security-groups.json

# Find security groups with open SSH (port 22)
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?length(IpPermissions[?to_string(to_int(FromPort))==`22`])>`0`]' \
  --output json

# Find security groups allowing all traffic
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?length(IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]])>`0`]' \
  --output json
```

### Elastic Block Store (EBS)

#### Volume Operations

```bash
# Create volume
aws ec2 create-volume \
  --size 100 \
  --availability-zone us-east-1a \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=DataVolume}]'

# Attach volume
aws ec2 attach-volume \
  --volume-id vol-1234567890abcdef0 \
  --instance-id i-1234567890abcdef0 \
  --device /dev/sdf

# Create snapshot
aws ec2 create-snapshot \
  --volume-id vol-1234567890abcdef0 \
  --description "Backup $(date)"

# List snapshots by volume
aws ec2 describe-snapshots \
  --filters "Name=volume-id,Values=vol-1234567890abcdef0" \
  --query 'Snapshots[].{ID:SnapshotId,Time:StartTime,Size:VolumeSize,State:State}' \
  --output table
```

## Lambda Advanced Patterns

### Function Deployment

#### Deploy Function with Layers

```bash
# Create deployment package
zip -r function.zip app.py requirements.txt

# Update function code
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip \
  --publish

# Add layers
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:us-east-1:123456789012:layer:numpy:1 arn:aws:lambda:us-east-1:123456789012:layer:pandas:1
```

#### Function Configuration

```bash
# Update memory and timeout
aws lambda update-function-configuration \
  --function-name my-function \
  --memory-size 512 \
  --timeout 300 \
  --environment "Variables={ENV=production}"

# Set VPC configuration
aws lambda update-function-configuration \
  --function-name my-function \
  --vpc-config SubnetIds=subnet-12345678,subnet-87654321,SecurityGroupIds=sg-12345678

# Configure dead letter queue
aws lambda update-function-configuration \
  --function-name my-function \
  --dead-letter-config TargetArn=arn:aws:sqs:us-east-1:123456789012:my-dlq
```

### Invocation Patterns

#### Synchronous Invocation

```bash
# Invoke and wait for response
aws lambda invoke \
  --function-name my-function \
  --payload '{"key": "value"}' \
  --log-type Tail \
  response.json

# Parse logs from response
cat response.json | jq -r '.LogResult' | base64 -d
```

#### Asynchronous Invocation

```bash
# Invoke asynchronously
aws lambda invoke \
  --function-name my-function \
  --invocation-type Event \
  --payload '{"event": "data"}' \
  /dev/null

# Check function state after async invoke
sleep 5
aws lambda get-function-concurrency --function-name my-function
```

#### Invocation with AWS SDK Payload

```bash
# Use payload as JSON file
aws lambda invoke \
  --function-name my-function \
  --payload file://event.json \
  response.json
```

### Layer Management

#### Create and Publish Layer

```bash
# Create layer package
mkdir python/lib/python3.9/site-packages
pip install -r requirements.txt -t python/lib/python3.9/site-packages/
zip -r layer.zip python/

# Publish layer
aws lambda publish-layer-version \
  --layer-name my-layer \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.9 python3.10 \
  --license-info "MIT" \
  --description "Common dependencies"

# List layer versions
aws lambda list-layer-versions --layer-name my-layer
```

### CloudWatch Logs Integration

#### View Function Logs

```bash
# Get recent logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -d "1 hour ago" +%s)000 \
  --query 'events[].message' \
  --output text | head -50

# Stream logs in real-time
aws logs tail /aws/lambda/my-function --follow
```

### Aliases and Versions

#### Manage Versions

```bash
# Publish version
aws lambda publish-version \
  --function-name my-function \
  --description "Production release v1.0"

# Create alias
aws lambda create-alias \
  --function-name my-function \
  --name production \
  --function-version 1 \
  --description "Production alias"

# Update alias to new version
aws lambda update-alias \
  --function-name my-function \
  --name production \
  --function-version 2
```

### Concurrency and Scaling

#### Configure Reserved Concurrency

```bash
# Set reserved concurrency
aws lambda put-function-concurrency \
  --function-name my-function \
  --reserved-concurrency 10

# Remove reserved concurrency
aws lambda delete-function-concurrency \
  --function-name my-function

# Get current concurrency
aws lambda get-function-concurrency \
  --function-name my-function
```

### Cost Optimization

#### Analyze Lambda Costs

```bash
# Get Lambda invocation and duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --start-time $(date -d "30 days ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 86400 \
  --statistics Sum \
  --dimensions Name=FunctionName,Value=my-function

# Get duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --start-time $(date -d "30 days ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 86400 \
  --statistics Average,Maximum \
  --dimensions Name=FunctionName,Value=my-function
```

## EC2 and Lambda Best Practices

1. **Use IAM roles** instead of access keys for EC2 and Lambda
2. **Enable VPC** for Lambda functions requiring network isolation
3. **Use provisioned concurrency** for latency-sensitive applications
4. **Implement proper error handling** and dead letter queues
5. **Monitor costs** with CloudWatch metrics and cost allocation tags
6. **Use lifecycle hooks** for graceful ASG scaling operations
7. **Enable termination protection** for production instances
8. **Use SSM Session Manager** instead of SSH where possible
