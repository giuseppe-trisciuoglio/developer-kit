# Networking and Security Hardened

## VPC Advanced Patterns

### VPC Creation and Configuration

#### VPC and Subnet Operations

```bash
# Create VPC with CIDR block
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=main-vpc}]'

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-12345678 \
  --enable-dns-hostnames "Value=true"

# Enable DNS support
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-12345678 \
  --enable-dns-support "Value=true"

# Create subnets
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1a}]'

aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1b}]'
```

### Internet Gateway and NAT Gateway

#### Network Connectivity

```bash
# Create and attach Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=main-igw}]'

aws ec2 attach-internet-gateway \
  --vpc-id vpc-12345678 \
  --internet-gateway-id igw-12345678

# Create NAT Gateway
aws ec2 create-nat-gateway \
  --subnet-id subnet-12345678 \
  --allocation-id eip-12345678

# Wait for NAT Gateway to be available
aws ec2 wait nat-gateway-available --nat-gateway-ids nat-12345678

# Update route table for private subnets
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-12345678
```

### Security Groups

#### Security Group Management

```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-sg \
  --description "Security group for web servers" \
  --vpc-id vpc-12345678

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --description "HTTPS from anywhere"

aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Add outbound rules
aws ec2 authorize-security-group-egress \
  --group-id sg-12345678 \
  --protocol -1 \
  --cidr 0.0.0.0/0

# Copy security group rules
aws ec2 describe-security-groups --group-ids sg-source > sg-rules.json
aws ec2 create-security-group --group-name new-sg --vpc-id vpc-new --description "Copied from source"
# Apply rules from sg-rules.json to new-sg
```

### VPC Flow Logs

#### Monitor Network Traffic

```bash
# Create IAM role for flow logs
aws iam create-role \
  --role-name vpc-flow-logs-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "vpc-flow-logs.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach flow logs policy
aws iam put-role-policy \
  --role-name vpc-flow-logs-role \
  --policy-name flow-logs-policy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:*:*:*"
    }]
  }'

# Create flow log
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flow-logs \
  --deliver-logs-permission-role-arn arn:aws:iam::123456789012:role/vpc-flow-logs-role

# Query flow logs
aws logs filter-log-events \
  --log-group-name /aws/vpc/flow-logs \
  --filter-pattern "[version, account, eni, source, destination, srcport, dstport, protocol, packets, bytes]"
```

### VPC Peering

#### Cross-VPC Connectivity

```bash
# Create VPC peering connection
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-12345678 \
  --peer-vpc-id vpc-87654321

# Accept VPC peering connection
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-12345678

# Update route tables for peering
aws ec2 create-route \
  --route-table-id rtb-12345678 \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-12345678

# Enable DNS hostnames for peering
aws ec2 modify-vpc-peering-connection-options \
  --vpc-peering-connection-id pcx-12345678 \
  --requester-peering-connection-options '{"AllowDnsHostnamesFromRequesterVPC":true}'
```

### Transit Gateway

#### Centralized Routing

```bash
# Create Transit Gateway
aws ec2 create-transit-gateway \
  --description "Main TGW" \
  --amazon-asn 64512

# Attach VPC to Transit Gateway
aws ec2 attach-transit-gateway-vpc-attachment \
  --transit-gateway-id tgw-12345678 \
  --vpc-id vpc-12345678 \
  --subnet-ids subnet-1 subnet-2

# Attach VPN to Transit Gateway
aws ec2 attach-vpn-gateway \
  --transit-gateway-id tgw-12345678 \
  --vpn-connection-id vpn-12345678

# Create Transit Gateway route table
aws ec2 create-transit-gateway-route-table \
  --transit-gateway-id tgw-12345678

# Add route
aws ec2 create-transit-gateway-route \
  --transit-gateway-route-table-id tgw-rtb-12345678 \
  --destination-cidr-block 10.0.0.0/16 \
  --transit-gateway-attachment-id tgw-attach-12345678
```

## Route53 Operations

### DNS Management

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference "reference-$(date +%s)"

# Create record set
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.example.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "1.2.3.4"}]
      }
    }]
  }'

# Create alias record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "my-alb-1234567890.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

### Health Checks

```bash
# Create health check
aws route53 create-health-check \
  --caller-reference "healthcheck-$(date +%s)" \
  --health-check-config '{
    "Type": "HTTPS",
    "FullyQualifiedDomainName": "example.com",
    "Port": 443,
    "ResourcePath": "/health",
    "RequestInterval": 10,
    "FailureThreshold": 3
  }'

# Get health check status
aws route53 get-health-check-status \
  --health-check-id abcdef12-3456-7890-abcd-ef1234567890
```

## CloudFront Distribution

### CDN Management

```bash
# Create distribution
aws cloudfront create-distribution \
  --origin-domain-name my-bucket.s3.amazonaws.com \
  --default-root-object index.html \
  --comment "Main distribution"

# Get distribution config
aws cloudfront get-distribution-config \
  --id EDFDVBD6EXAMPLE

# Update distribution
aws cloudfront update-distribution \
  --id EDFDVBD6EXAMPLE \
  --distribution-config file://dist-config.json \
  --if-match E2QWR3HEG8SAMPLE

# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/*"
```

## IAM Advanced Patterns

### Policy Management

#### Create and Manage Policies

```bash
# Create IAM policy
aws iam create-policy \
  --policy-name my-policy \
  --policy-document file://policy.json

# Create policy version
aws iam create-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/my-policy \
  --policy-document file://new-policy.json \
  --set-as-default

# List policy versions
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::123456789012:policy/my-policy
```

### IAM Policy Simulation

#### Validate Policies Before Deployment

```bash
# Simulate principal policy
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/myuser \
  --action-names s3:GetObject s3:PutObject s3:DeleteObject \
  --resource-arns "arn:aws:s3:::my-bucket/*"

# Simulate principal policy with context
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/myuser \
  --action-names dynamodb:GetItem \
  --resource-arns "arn:aws:dynamodb:us-east-1:123456789012:table/my-table" \
  --context-entries '[{"ContextKeyName":"dynamodb:Select","ContextKeyValues":["ALL_ATTRIBUTES"],"ContextKeyType":"string"}]'
```

### Role Management

#### Create and Manage Roles

```bash
# Create role with trust policy
aws iam create-role \
  --role-name my-role \
  --assume-role-policy-document file://trust-policy.json

# Attach managed policy
aws iam attach-role-policy \
  --role-name my-role \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Attach inline policy
aws iam put-role-policy \
  --role-name my-role \
  --policy-name my-inline-policy \
  --policy-document file://inline-policy.json
```

### Access Keys Management

#### Key Rotation

```bash
# List access keys
aws iam list-access-keys --user-name myuser

# Create access key
aws iam create-access-key --user-name myuser

# Rotate access keys
aws iam update-access-key \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive \
  --user-name myuser

# Delete old access key
aws iam delete-access-key \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --user-name myuser
```

### Password Policy

#### Configure Password Policy

```bash
# Get account password policy
aws iam get-account-password-policy

# Update password policy
aws iam update-account-password-policy \
  --minimum-length 12 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-letters \
  --require-lowercase-letters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5
```

### MFA Management

#### Enable MFA

```bash
# List MFA devices
aws iam list-mfa-devices --user-name myuser

# Enable MFA device
aws iam enable-mfa-device \
  --user-name myuser \
  --serial-number arn:aws:iam::123456789012:mfa/myuser \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

## Secrets Manager

### Secret Management

```bash
# Create secret
aws secretsmanager create-secret \
  --name my-secret \
  --secret-string '{"username":"admin","password":"secret123"}'

# Get secret value
aws secretsmanager get-secret-value \
  --secret-id my-secret \
  --query SecretString \
  --output text

# Update secret
aws secretsmanager put-secret-value \
  --secret-id my-secret \
  --secret-string '{"username":"admin","password":"newpassword"}'

# Rotate secret
aws secretsmanager rotate-secret \
  --secret-id my-secret

# Delete secret (with recovery)
aws secretsmanager delete-secret \
  --secret-id my-secret \
  --recovery-window-in-days 7
```

### Cross-Account Secret Access

```bash
# Grant cross-account access to secret
aws secretsmanager put-resource-policy \
  --secret-id my-secret \
  --resource-policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::987654321098:root"},
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "*"
    }]
  }'
```

## Security Best Practices

1. **VPC**: Use private subnets for sensitive workloads, enable flow logs
2. **Security Groups**: Use least-privilege, prefer security groups over CIDR ranges
3. **IAM**: Use IAM roles instead of access keys, implement MFA
4. **Secrets Manager**: Enable automatic rotation, use cross-account access
5. **Route53**: Use health checks for automated failover
6. **CloudFront**: Enable WAF, use origin access identity for S3
7. **Monitoring**: Enable CloudTrail for all API calls, use GuardDuty
