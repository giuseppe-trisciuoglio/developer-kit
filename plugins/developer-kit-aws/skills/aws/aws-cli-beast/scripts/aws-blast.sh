#!/bin/bash
# AWS Beast Mode Shell Aliases
# Add to ~/.bashrc or ~/.zshrc: source /path/to/aws-blast.sh

# ==========================================
# EC2 ALIASES
# ==========================================

# List all EC2 instances
alias ec2-list='aws ec2 describe-instances --query "Reservations[].Instances[].{Name:Tags[?Key==\`Name\`].Value|[0],Id:InstanceId,State:State.Name,Type:InstanceType,AZ:Placement.AvailabilityZone}" --output table'

# EC2 instances with IPs
alias ec2-ips='aws ec2 describe-instances --query "Reservations[].Instances[].{Name:Tags[?Key==\`Name\`].Value|[0],Id:InstanceId,PrivateIP:PrivateIpAddress,PublicIP:PublicIpAddress,State:State.Name}" --output table'

# EC2 instances by tag
alias ec2-by-tag='aws ec2 describe-instances --filters "Name=tag:$1,Values=$2" --query "Reservations[].Instances[].{Name:Tags[?Key==\`Name\`].Value|[0],Id:InstanceId,State:State.Name}" --output table'

# EC2 instance status
alias ec2-status='aws ec2 describe-instance-status --instance-ids $1 --query "InstanceStatuses[].{InstanceId:InstanceId,SystemStatus:SystemStatus.Status,InstanceStatus:InstanceStatus.Status}" --output table'

# SSH via Session Manager
alias ec2-ssh='aws ssm start-session --target $1'

# Reboot instance
alias ec2-reboot='aws ec2 reboot-instances --instance-ids $1 && aws ec2 wait instance-status-ok --instance-ids $1'

# Stop instance
alias ec2-stop='aws ec2 stop-instances --instance-ids $1'

# Start instance
alias ec2-start='aws ec2 start-instances --instance-ids $1 && aws ec2 wait instance-running --instance-ids $1'

# ==========================================
# S3 ALIASES
# ==========================================

# List buckets
alias s3ls='aws s3 ls'

# List bucket contents recursively
alias s3lsr='aws s3 ls --recursive'

# S3 sync up
alias s3up='aws s3 sync ./ s3://$1/'

# S3 sync down
alias s3down='aws s3 sync s3://$1/ ./'

# S3 copy with multipart
alias s3cp='aws s3 cp $1 s3://$2/'

# S3 presign URL
alias s3sign='aws s3 presign s3://$1/$2 --expires-in 3600'

# ==========================================
# LAMBDA ALIASES
# ==========================================

# List Lambda functions
alias lambda-list='aws lambda list-functions --query "Functions[].{Name:FunctionName,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout}" --output table'

# Lambda invoke (sync)
alias lambda-invoke='aws lambda invoke --function-name $1 --payload '"'"'{}'"'"' --log-type Tail response.json'

# Lambda invoke async
alias lambda-invoke-async='aws lambda invoke --function-name $1 --invocation-type Event --payload '"'"'{}'"'"' /dev/null'

# Lambda logs (tail)
alias lambda-logs='aws logs tail /aws/lambda/$1 --follow'

# Lambda get config
alias lambda-config='aws lambda get-function-configuration --function-name $1 --query "{FunctionName:FunctionName,Runtime:Runtime,Memory:MemorySize,Timeout:Timeout,VPC:VPCConfig}" --output table'

# ==========================================
# IAM ALIASES
# ==========================================

# List IAM users
alias iam-users='aws iam list-users --query "Users[].{Name:UserName,Arn:Arn}" --output table'

# List IAM roles
alias iam-roles='aws iam list-roles --query "Roles[].{Name:RoleName,Arn:Arn}" --output table'

# List IAM policies
alias iam-policies='aws iam list-policies --scope Local --query "Policies[].{Name:PolicyName,Arn:Arn}" --output table'

# Get caller identity
alias whoami='aws sts get-caller-identity'

# ==========================================
# VPC ALIASES
# ==========================================

# List VPCs
alias vpc-list='aws ec2 describe-vpcs --query "Vpcs[].{Id:VpcId,Cidr:CidrBlock,State:VpcState,Name:Tags[?Key==\`Name\`].Value|[0]}" --output table'

# List subnets
alias subnet-list='aws ec2 describe-subnets --query "Subnets[].{Id:SubnetId,VpcId:VpcId,Cidr:CidrBlock,AZ:AvailabilityZone,Public:MapPublicIpOnLaunch}" --output table'

# List security groups
alias sg-list='aws ec2 describe-security-groups --query "SecurityGroups[].{Id:GroupId,Name:GroupName,VpcId:VpcId}" --output table'

# List NAT Gateways
alias nat-list='aws ec2 describe-nat-gateways --query "NatGateways[].{Id:NatGatewayId,VpcId:VpcId,State:State}" --output table'

# ==========================================
# RDS ALIASES
# ==========================================

# List RDS instances
alias rds-list='aws rds describe-db-instances --query "DBInstances[].{Id:DBInstanceIdentifier,Engine:Engine,Class:DBInstanceClass,Status:DBInstanceStatus}" --output table'

# RDS instance status
alias rds-status='aws rds describe-db-instances --db-instance-identifier $1 --query "DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address,Port:Endpoint.Port}" --output table'

# ==========================================
# GENERAL ALIASES
# ==========================================

# Current identity
alias aws-id='aws sts get-caller-identity --query "{Account:Account,Arn:Arn,UserId:UserId}" --output table'

# List profiles
alias aws-profiles='grep -E "^\[profile" ~/.aws/config | sed "s/\[profile //" | sed "s/\]//"'

# Current region
alias aws-region='aws configure get region'

# Switch profile
awsprof() { export AWS_PROFILE=$1; echo "Profile: $1"; }

# Switch region
awsreg() { aws configure set region $1; echo "Region: $1"; }

# Costs today
alias cost-today='aws ce get-cost-and-usage --time-period Start=$(date +%Y-%m-%d),End=$(date +%Y-%m-%d) --metrics UnblendedCost --granularity DAILY --query "ResultsByTime[0].Total.UnblendedCost.Amount" --output text'

# Costs this month
alias cost-month='aws ce get-cost-and-usage --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) --metrics UnblendedCost --granularity MONTHLY --query "ResultsByTime[0].Total.UnblendedCost.Amount" --output text'

# ==========================================
# FUNCTIONS
# ==========================================

# Stop all instances in environment
stop-env() {
  aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=$1" "Name=instance-state-name,Values=running" \
    --query "Reservations[].Instances[].InstanceId" --output text | \
    xargs aws ec2 stop-instances --instance-ids
}

# Start all instances in environment
start-env() {
  aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=$1" "Name=instance-state-name,Values=stopped" \
    --query "Reservations[].Instances[].InstanceId" --output text | \
    xargs aws ec2 start-instances --instance-ids
}

# Delete all objects in S3 bucket
empty-s3() {
  aws s3 rm s3://$1/ --recursive
}

# Get AWS resource by tag
by-tag() {
  aws ec2 describe-tags --filters "Name=tag:$1,Values=$2" --query "Tags[].ResourceId" --output text
}

# Get CloudWatch metric
cw-metric() {
  aws cloudwatch get-metric-statistics \
    --namespace $1 \
    --metric-name $2 \
    --start-time $(date -d "1 hour ago" -Iseconds) \
    --end-time $(date -Iseconds) \
    --period 300 \
    --statistics Average,Maximum \
    --dimensions Name=$3,Value=$4 \
    --query "Datapoints[].{Time:Timestamp,Avg:Average,Max:Maximum}" \
    --output table
}

# IAM policy simulator
iam-sim() {
  aws iam simulate-principal-policy \
    --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
    --action-names $1 \
    --resource-arns $2
}

# Wait for EC2 instance
wait-ec2() {
  aws ec2 wait instance-running --instance-ids $1
  aws ec2 wait instance-status-ok --instance-ids $1
}

# Wait for Lambda function
wait-lambda() {
  aws lambda wait function-active --function-name $1
}
