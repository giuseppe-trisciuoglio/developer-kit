# Automation Patterns

## Shell Aliases and Functions

### Common AWS Aliases

Add these to your `.bashrc` or `.zshrc`:

```bash
# EC2 aliases
alias ec2-list='aws ec2 describe-instances --query "Reservations[].Instances[].{Name:Tags[?Key==\`Name\`].Value|[0],Id:InstanceId,State:State.Name,Type:InstanceType}" --output table'
alias ec2-state='aws ec2 describe-instance-status --instance-ids'
alias ec2-ssh='aws ssm start-session --target'
alias ec2-logs='aws logs tail /aws/ec2/'

# S3 aliases
alias s3ls='aws s3 ls'
alias s3tree='aws s3 ls --recursive | awk "{print \$4}" | tree --noreport -d'
alias s3sync='aws s3 sync'

# Lambda aliases
alias lambda-list='aws lambda list-functions --query "Functions[].{Name:FunctionName,Runtime:Runtime,Memory:MemorySize}" --output table'
alias lambda-invoke='aws lambda invoke --log-type Tail'
alias lambda-logs='aws logs tail /aws/lambda/'

# IAM aliases
alias iam-users='aws iam list-users --query "Users[].{Name:UserName,Created:CreateDate}" --output table'
alias iam-roles='aws iam list-roles --query "Roles[].{Name:RoleName,Path:Path}" --output table'

# General aliases
alias whoami='aws sts get-caller-identity'
alias aws-profiles='cat ~/.aws/config | grep "\[profile" | sed "s/\[profile //" | sed "s/\]//"'
alias aws-region='aws configure get region'
```

### Useful Functions

```bash
# Switch AWS profile
awsprof() {
  export AWS_PROFILE=$1
  echo "Switched to profile: $1"
}

# Get AWS resources by tag
aws-tag() {
  aws ec2 describe-tags --filters "Name=tag:$1,Values=$2" --query "Tags[].ResourceId" --output text
}

# Stop all instances in environment
stop-env() {
  aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=$1" "Name=instance-state-name,Values=running" \
    --query "Reservations[].Instances[].InstanceId" \
    --output text | xargs aws ec2 stop-instances --instance-ids
}

# Get costs for service
aws-costs() {
  aws ce get-cost-and-usage \
    --time-period Start=$(date -d "1 month ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --metrics UnblendedCost \
    --granularity DAILY \
    --group-by Type=DIMENSION,Key=SERVICE \
    --query "ResultsByTime[].Groups[?Keys[0]=='$1'].{Date:TimePeriod.Start,Cost:Metrics.UnblendedCost.Amount}" \
    --output table
}
```

## JMESPath Templates

### Common JMESPath Queries

```json
{
  "ec2_instances": "Reservations[].Instances[].{Id:InstanceId,Name:Tags[?Key==`Name`].Value|[0],Type:InstanceType,State:State.Name}",
  "s3_buckets": "Buckets[].{Name:Name,CreationDate:CreationDate}",
  "lambda_functions": "Functions[].{Name:FunctionName,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout}",
  "iam_users": "Users[].{Name:UserName,Arn:Arn,Created:CreateDate}",
  "vpc_subnets": "Vpcs[].{Id:VpcId,Cidr:CidrBlock,DnsHostnames:DnsHostnamesEnabled,DnsSupport:DnsSupportEnabled}",
  "rds_instances": "DBInstances[].{Id:DBInstanceIdentifier,Engine:Engine,Class:DBInstanceClass,Status:DBInstanceStatus}",
  "cloudwatch_alarms": "MetricAlarms[].{Name:AlarmName,Metric:MetricName,Namespace:Namespace,State:StateValue}"
}
```

### Complex JMESPath Examples

```bash
# Get EC2 with specific tag and filter by state
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?Tags[?Key==`Environment` && Value==`production`] | [0] | {Name:Tags[?Key==`Name`].Value | [0], Id:InstanceId, State:State.Name}'

# Aggregate Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=* \
  --query 'Datapoints[].{Time:Timestamp,Count:Sum}'

# Get unused security groups
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?length(Instances)==`0` && length(NetworkInterfaces)==`0`].{Id:GroupId,Name:GroupName}'
```

## Automation Scripts

### EC2 Fleet Management

```bash
#!/bin/bash
# manage-fleet.sh

ENV=$1
ACTION=$2

case $ACTION in
  start)
    IDS=$(aws ec2 describe-instances \
      --filters "Name=tag:Environment,Values=$ENV" "Name=instance-state-name,Values=stopped" \
      --query "Reservations[].Instances[].InstanceId" --output text)
    [ -n "$IDS" ] && aws ec2 start-instances --instance-ids $IDS
    ;;
  stop)
    IDS=$(aws ec2 describe-instances \
      --filters "Name=tag:Environment,Values=$ENV" "Name=instance-state-name,Values=running" \
      --query "Reservations[].Instances[].InstanceId" --output text)
    [ -n "$IDS" ] && aws ec2 stop-instances --instance-ids $IDS
    ;;
  status)
    aws ec2 describe-instances \
      --filters "Name=tag:Environment,Values=$ENV" \
      --query "Reservations[].Instances[].{Name:Tags[?Key==\`Name\`].Value|[0],Id:InstanceId,State:State.Name}" \
      --output table
    ;;
esac
```

### S3 Backup Script

```bash
#!/bin/bash
# s3-backup.sh

SOURCE_BUCKET=$1
DEST_BUCKET=$2
DATE=$(date +%Y%m%d-%H%M%S)

echo "Starting backup from $SOURCE_BUCKET to $DEST_BUCKET"

# Sync with delete to ensure mirror
aws s3 sync s3://$SOURCE_BUCKET/ s3://$DEST_BUCKET/$DATE/ \
  --storage-class GLACIER \
  --exclude "*.tmp" \
  --exclude "*.log"

# Create lifecycle rule for old backups
aws s3api put-bucket-lifecycle-configuration \
  --bucket $DEST_BUCKET \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "ArchiveOldBackups",
      "Status": "Enabled",
      "Prefix": "",
      "Transitions": [
        {"Days": 30, "StorageClass": "GLACIER"},
        {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
      ]
    }]
  }'

echo "Backup completed: $DATE"
```

### Cost Monitoring Script

```bash
#!/bin/bash
# cost-monitor.sh

START_DATE=$(date -d "1 day ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)

# Get daily costs by service
echo "=== Daily Costs by Service ==="
aws ce get-cost-and-usage \
  --time-period Start=$START_DATE,End=$END_DATE \
  --metrics UnblendedCost \
  --granularity DAILY \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[].{Service:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
  --output table

# Get EC2 costs by instance
echo -e "\n=== EC2 Costs by Instance ==="
aws ce get-cost-and-usage \
  --time-period Start=$START_DATE,End=$END_DATE \
  --metrics UnblendedCost \
  --granularity DAILY \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon EC2"]}}' \
  --query 'ResultsByTime[].Groups[].{UsageType:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
  --output table
```

### Lambda Deployment Script

```bash
#!/bin/bash
# deploy-lambda.sh

FUNCTION_NAME=$1
S3_BUCKET=$2
S3_KEY=$3

# Validate function exists
aws lambda get-function --function-name $FUNCTION_NAME > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Creating new function: $FUNCTION_NAME"
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --role arn:aws:iam::123456789012:role/lambda-role \
    --handler lambda.handler \
    --zip-file fileb://function.zip
else
  echo "Updating existing function: $FUNCTION_NAME"
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --s3-bucket $S3_BUCKET \
    --s3-key $S3_KEY \
    --publish
fi

# Wait for function to be active
echo "Waiting for function to be active..."
aws lambda wait function-active --function-name $FUNCTION_NAME

# Verify
aws lambda get-function-configuration --function-name $FUNCTION_NAME \
  --query '{State:State,Version:Version}' --output table
```

## Parallel Operations

### GNU Parallel Examples

```bash
# Start sessions on multiple instances
cat instances.txt | parallel -j 10 "aws ssm start-session --target {}"

# Copy files to multiple S3 buckets
cat buckets.txt | parallel -j 5 "aws s3 cp file.txt s3://{}/"

# Invoke Lambda functions in parallel
cat functions.txt | parallel -j 20 "aws lambda invoke --function-name {} response.json"

# Run commands on multiple instances
cat instances.txt | parallel -j 10 "aws ssm send-command --instance-ids {} --document-name AWS-RunShellScript --parameters commands=['uptime']"
```

### xargs Examples

```bash
# Delete old snapshots in parallel
aws ec2 describe-snapshots \
  --owner-ids self \
  --query 'Snapshots[?StartTime<=`2024-01-01`].SnapshotId' \
  --output text | xargs -P 5 -I {} aws ec2 delete-snapshot --snapshot-id {}

# Tag resources in batch
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=development" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text | xargs -I {} aws ec2 create-tags --resources {} --tags "Key=Team,Value=DevOps"
```

## Cron Jobs and Scheduling

### Common Scheduled Tasks

```bash
# Stop development instances at 7 PM
0 19 * * 1-5 /home/user/scripts/stop-dev-instances.sh >> /var/log/aws-scheduler.log 2>&1

# Start development instances at 8 AM
0 8 * * 1-5 /home/user/scripts/start-dev-instances.sh >> /var/log/aws-scheduler.log 2>&1

# Daily cost report
0 8 * * * /home/user/scripts/cost-report.sh | mail -s "Daily AWS Costs" team@company.com

# Weekly backup verification
0 2 * * 0 /home/user/scripts/verify-backups.sh >> /var/log/backup-verify.log 2>&1
```

### EventBridge Integration

```bash
# Create scheduled rule
aws events put-rule \
  --name daily-cost-report \
  --schedule-expression "cron(0 8 * * ? *)" \
  --state ENABLED

# Put targets
aws events put-targets \
  --rule daily-cost-report \
  --targets '[{"Id":"1","Arn":"arn:aws:states:us-east-1:123456789012:stateMachine:CostReportStateMachine","RoleArn":"arn:aws:iam::123456789012:role/events-role"}]'
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: AWS Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy Lambda
        run: |
          zip -r function.zip app.py requirements.txt
          aws lambda update-function-code \
            --function-name my-function \
            --zip-file fileb://function.zip \
            --publish

      - name: Run tests
        run: |
          aws lambda invoke \
            --function-name my-function \
            --payload '{"action":"test"}' \
            response.json
          cat response.json | jq '.statusCode'
```

## Rate Limiting Handling

### Retry Patterns

```bash
#!/bin/bash
# retry.sh

max_retries=5
retry_delay=1

retry_aws() {
  local cmd="$@"
  local attempt=1

  while [ $attempt -le $max_retries ]; do
    if eval "$cmd"; then
      return 0
    fi
    echo "Attempt $attempt failed, retrying in $retry_delay seconds..."
    sleep $retry_delay
    retry_delay=$((retry_delay * 2))
    attempt=$((attempt + 1))
  done

  echo "All $max_retries attempts failed"
  return 1
}

# Usage
retry_aws aws ec2 describe-instances
```

### AWS CLI Configuration for Retry

```bash
# Configure in ~/.aws/config
[default]
region = us-east-1
retry_handler_options = retry_mode=adaptive,max_attempts=10

# Or use environment variables
export AWS_MAX_ATTEMPTS=10
export AWS_RETRY_MODE=adaptive
```

## Best Practices

1. **Always use `--dry-run`** for destructive operations
2. **Implement proper error handling** in scripts
3. **Use tags** for resource identification and automation
4. **Enable CloudTrail** for audit compliance
5. **Use least-privilege IAM policies** for automation scripts
6. **Implement retry logic** with exponential backoff
7. **Log all operations** for troubleshooting
8. **Use parallel processing** for bulk operations
9. **Schedule expensive operations** during off-peak hours
10. **Test in lower environments** before production deployment
