# CloudFormation Best Practices for EC2

## Use AWS-Specific Parameter Types

Always use AWS-specific parameter types for validation and easier selection.

```yaml
Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: Select a VPC

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Select subnets

  SecurityGroupIds:
    Type: List<AWS::EC2::SecurityGroup::Id>
    Description: Select security groups

  InstanceType:
    Type: AWS::EC2::InstanceType
    Description: EC2 instance type

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Select a key pair
```

## Organize by Lifecycle

Separate resources that change at different rates into different stacks.

```yaml
# Network stack - rarely changes
AWSTemplateFormatVersion: 2010-09-09
Description: Network infrastructure (VPC, subnets, routes)
Resources:
  VPC: AWS::EC2::VPC
  Subnets: AWS::EC2::Subnet

# Security stack - changes occasionally
AWSTemplateFormatVersion: 2010-09-09
Description: Security resources (IAM roles, security groups)
Resources:
  SecurityGroups: AWS::EC2::SecurityGroup
  Roles: AWS::IAM::Role

# Application stack - changes frequently
AWSTemplateFormatVersion: 2010-09-09
Description: Application resources (EC2 instances, ALB)
Parameters:
  NetworkStackName:
    Type: String
  SecurityStackName:
    Type: String
Resources:
  Instances: AWS::EC2::Instance
  LoadBalancer: AWS::ElasticLoadBalancingV2::LoadBalancer
```

## Use Meaningful Names

Use `AWS::StackName` and parameters for consistent naming.

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-instance
        - Key: Environment
          Value: !Ref EnvironmentName
```

## Use Pseudo Parameters

Use pseudo parameters for region-agnostic templates.

```yaml
Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-${AWS::AccountId}-${AWS::Region}

  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      Tags:
        - Key: StackName
          Value: !Ref AWS::StackName
        - Key: Region
          Value: !Ref AWS::Region
```

## Validate Before Deployment

```bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Check for syntax errors
aws cloudformation validate-template \
  --template-body file://template.yaml \
  --query 'Description'

# Use cfn-lint for advanced validation
pip install cfn-lint
cfn-lint template.yaml
```

## Stack Policies

Stack policies protect stack resources from unintended updates that could cause service disruption. Apply policies to prevent accidental modifications or deletions of critical resources.

```yaml
Resources:
  # EC2 instance - allow updates but prevent deletion
  Ec2Instance:
    Type: AWS::EC2::Instance
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain

  # Database - prevent all updates
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Retain
```

**Stack Policy JSON Example:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "Update:*",
      "Principal": "*",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": ["Update:Delete", "Update:Replace"],
      "Principal": "*",
      "Resource": "LogicalId=Ec2Instance"
    },
    {
      "Effect": "Deny",
      "Action": "Update:*",
      "Principal": "*",
      "Resource": "LogicalId=DatabaseInstance"
    }
  ]
}
```

**Apply Stack Policy:**

```bash
aws cloudformation set-stack-policy \
  --stack-name my-ec2-stack \
  --stack-policy-body file://stack-policy.json

# Or from a file
aws cloudformation set-stack-policy \
  --stack-name my-ec2-stack \
  --stack-policy-url https://s3.amazonaws.com/bucket/policy.json
```

## Termination Protection

Enable termination protection to prevent accidental deletion of production stacks. This is critical for production environments.

```bash
# Enable termination protection when creating a stack
aws cloudformation create-stack \
  --stack-name my-ec2-stack \
  --template-body file://template.yaml \
  --enable-termination-protection

# Enable termination protection on existing stack
aws cloudformation update-termination-protection \
  --stack-name my-ec2-stack \
  --enable-termination-protection

# Disable termination protection (use with caution)
aws cloudformation update-termination-protection \
  --stack-name my-ec2-stack \
  --no-enable-termination-protection

# Check if termination protection is enabled
aws cloudformation describe-stacks \
  --stack-name my-ec2-stack \
  --query 'Stacks[0].EnableTerminationProtection'
```

**Best Practices for Termination Protection:**

- Enable on all production stacks
- Use AWS Organizations SCP to enforce termination protection
- Review before deleting development stacks
- Document the process for emergency termination

## Drift Detection

Drift detection identifies differences between the actual infrastructure and the CloudFormation template. Regular drift checks ensure compliance and security.

```bash
# Detect drift on a stack
aws cloudformation detect-drift \
  --stack-name my-ec2-stack

# Get drift detection status
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id abc123

# Get resources that have drifted
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-ec2-stack

# Get detailed drift information for a specific resource
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-ec2-stack \
  --stack-resource-drifts-limit 10
```

**Detect Drift Programmatically:**

```bash
#!/bin/bash
# detect-drift.sh - Automated drift detection script

STACK_NAME=$1
if [ -z "$STACK_NAME" ]; then
    echo "Usage: $0 <stack-name>"
    exit 1
fi

echo "Detecting drift for stack: $STACK_NAME"

# Start drift detection
DETECTION_ID=$(aws cloudformation detect-drift \
  --stack-name $STACK_NAME \
  --query 'StackId' \
  --output text)

echo "Drift detection started: $DETECTION_ID"

# Wait for drift detection to complete
STATUS="DETECTION_IN_PROGRESS"
while [ "$STATUS" = "DETECTION_IN_PROGRESS" ]; do
    sleep 5
    STATUS=$(aws cloudformation describe-stack-drift-detection-status \
      --stack-drift-detection-id $DETECTION_ID \
      --query 'DetectionStatus' \
      --output text)
    echo "Status: $STATUS"
done

# Get drift status
DRIFT_STATUS=$(aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id $DETECTION_ID \
  --query 'DriftStatus' \
  --output text)

echo "Drift Status: $DRIFT_STATUS"

if [ "$DRIFT_STATUS" = "DRIFTED" ]; then
    echo "Resources with drift:"
    aws cloudformation describe-stack-resource-drifts \
      --stack-name $STACK_NAME \
      --query 'StackResourceDrifts[].{LogicalId:LogicalResourceId,Status:ResourceDriftStatus,Type:ResourceType}'
else
    echo "No drift detected - stack is in sync with template"
fi
```

**Common Drift Scenarios:**

| Drift Type | Description | Action Required |
|------------|-------------|-----------------|
| MODIFIED | Resource properties changed | Review and update template or revert changes |
| DELETED | Resource deleted outside CFN | Recreate via template or import |
| ADDED | Resource created outside CFN | Import to stack or delete manually |

## Change Sets

Change sets preview the impact of stack changes before execution. Always review change sets in production environments.

```bash
# Create a change set
aws cloudformation create-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset \
  --template-body file://updated-template.yaml \
  --capabilities CAPABILITY_IAM \
  --change-set-type UPDATE

# List change sets for a stack
aws cloudformation list-change_sets \
  --stack-name my-ec2-stack

# Describe a change set to see the planned changes
aws cloudformation describe-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset

# Execute a change set
aws cloudformation execute-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset

# Delete a change set if changes are not needed
aws cloudformation delete-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset
```

**Change Set Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| UPDATE | Preview changes to existing stack | Modifying existing resources |
| CREATE | Preview new stack creation | Creating new stacks from template |
| IMPORT | Preview resources to import | Importing existing resources |

**Review Change Sets with Filters:**

```bash
# Get changes affecting specific resource types
aws cloudformation describe-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset \
  --query 'Changes[?ResourceChange.ResourceType==`AWS::EC2::Instance`]'

# Get changes with replacement impact
aws cloudformation describe-change-set \
  --stack-name my-ec2-stack \
  --change-set-name my-ec2-changeset \
  --query 'Changes[?ResourceChange.Replacement!=`None`]'
```

**Automated Change Set Review Script:**

```bash
#!/bin/bash
# review-changeset.sh - Automated change set review

STACK_NAME=$1
CHANGE_SET_NAME=$2
AUTO_APPROVE=false

while getopts "a" opt; do
  case $opt in
    a) AUTO_APPROVE=true ;;
    *) echo "Usage: $0 [-a] <stack-name> <change-set-name>"
       echo "  -a: Auto-approve if no critical changes"
       exit 1 ;;
  esac
done

echo "Reviewing change set: $CHANGE_SET_NAME"
echo "Stack: $STACK_NAME"
echo ""

# Get change set summary
CHANGES=$(aws cloudformation describe-change-set \
  --stack-name $STACK_NAME \
  --change-set-name $CHANGE_SET_NAME \
  --query 'Changes[*].{Type:Type,Resource:ResourceChange.LogicalResourceId,Action:ResourceChange.Action,Replacement:ResourceChange.Replacement}' \
  --output table)

echo "Planned Changes:"
echo "$CHANGES"
echo ""

# Check for critical changes (replacements or deletions)
CRITICAL_CHANGES=$(aws cloudformation describe-change-set \
  --stack-name $STACK_NAME \
  --change-set-name $CHANGE_SET_NAME \
  --query 'Changes[?ResourceChange.Replacement==`True` || ResourceChange.Action==`Remove`]' \
  --output json)

if [ -n "$CRITICAL_CHANGES" ] && [ "$CRITICAL_CHANGES" != "[]" ]; then
    echo "WARNING: Critical changes detected that require manual review:"
    echo "$CRITICAL_CHANGES"
    echo ""
    echo "Please review manually before executing."
    exit 1
fi

if [ "$AUTO_APPROVE" = true ]; then
    echo "No critical changes - auto-executing change set..."
    aws cloudformation execute-change-set \
      --stack-name $STACK_NAME \
      --change-set-name $CHANGE_SET_NAME
    echo "Change set executed successfully."
else
    echo "Review complete. No critical changes detected."
    echo "To execute: aws cloudformation execute-change-set --stack-name $STACK_NAME --change-set-name $CHANGE_SET_NAME"
fi
```
