# CloudFormation Template Structure

## Template Sections Overview

AWS CloudFormation templates are JSON or YAML files with specific sections. Each section serves a purpose in defining your infrastructure.

```yaml
AWSTemplateFormatVersion: 2010-09-09  # Required - template version
Description: Optional description string  # Optional description

# Section order matters for readability but CloudFormation accepts any order
Mappings: {}       # Static configuration tables
Metadata: {}       # Additional information about resources
Parameters: {}     # Input values for customization
Rules: {}          # Parameter validation rules
Conditions: {}     # Conditional resource creation
Transform: {}      # Macro processing (e.g., AWS::Serverless)
Resources: {}      # AWS resources to create (REQUIRED)
Outputs: {}        # Return values after stack creation
```

## Format Version

The `AWSTemplateFormatVersion` identifies the template version. Current version is `2010-09-09`.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: My CloudFormation Template
```

## Description

Add a description to document the template's purpose. Must appear after the format version.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: >
  This template creates an EC2 instance with a security group
  and IAM role for running web applications. It includes:
  - EC2 instance configuration
  - Security group with HTTP/HTTPS access
  - IAM role with S3 access permissions
```

## Metadata

Use `Metadata` for additional information about resources or parameters.

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: EC2 Configuration
        Parameters:
          - InstanceType
          - KeyName
      - Label:
          default: Network Configuration
        Parameters:
          - VpcId
          - SubnetId
    ParameterLabels:
      InstanceType:
        default: EC2 Instance Type
      KeyName:
        default: SSH Key Pair
```

## Parameters

### Parameter Types

Use AWS-specific parameter types for validation and easier selection in the console.

```yaml
Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: Select an existing VPC

  SubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Select a subnet

  SecurityGroupIds:
    Type: List<AWS::EC2::SecurityGroup::Id>
    Description: Select existing security groups

  InstanceType:
    Type: AWS::EC2::InstanceType
    Description: EC2 instance type
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large

  AmiId:
    Type: AWS::EC2::Image::Id
    Description: Select an AMI

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Select an existing key pair

  AlbArn:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer::Arn
    Description: Select an ALB
```

### SSM Parameter Types

Reference Systems Manager parameters for dynamic values.

```yaml
Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Description: Latest AMI ID from SSM
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

  LatestAmiIdARM:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Description: Latest ARM AMI ID from SSM
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-arm64-gp2
```

### Parameter Constraints

Add constraints to validate parameter values.

```yaml
Parameters:
  VpcCidr:
    Type: String
    Description: CIDR block for the VPC
    Default: 10.0.0.0/16
    AllowedPattern: ^([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$
    ConstraintDescription: Must be a valid CIDR block (x.x.x.x/x)

  InstanceCount:
    Type: Number
    Description: Number of instances to launch
    Default: 1
    MinValue: 1
    MaxValue: 10

  Environment:
    Type: String
    Description: Deployment environment
    Default: development
    AllowedValues:
      - development
      - staging
      - production
    ConstraintDescription: Must be development, staging, or production

  VolumeSize:
    Type: Number
    Description: EBS volume size in GB
    Default: 20
    MinValue: 8
    MaxValue: 1000
```

## Mappings

Use `Mappings` for static configuration data based on regions or other factors.

```yaml
Mappings:
  RegionMap:
    us-east-1:
      HVM64: ami-0ff8a95407f89df2f
      HVMG2: ami-0a0c776d80e2a1f3c
    us-west-2:
      HVM64: ami-0a0c776d80e2a1f3c
      HVMG2: ami-0a0c776d80e2a1f3c
    eu-west-1:
      HVM64: ami-0ff8a95407f89df2f
      HVMG2: ami-0a0c776d80e2a1f3c

  EnvironmentConfig:
    development:
      InstanceType: t3.micro
      MinInstances: 1
      MaxInstances: 2
      EnableAutoScaling: false
    staging:
      InstanceType: t3.small
      MinInstances: 1
      MaxInstances: 3
      EnableAutoScaling: false
    production:
      InstanceType: t3.medium
      MinInstances: 2
      MaxInstances: 10
      EnableAutoScaling: true

Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref AWS::Region, HVM64]
      InstanceType: !FindInMap [EnvironmentConfig, !Ref Environment, InstanceType]
```

## Conditions

Use `Conditions` to conditionally create resources based on parameters.

```yaml
Parameters:
  DeployAlb:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

  Environment:
    Type: String
    Default: development
    AllowedValues:
      - development
      - staging
      - production

  UseSpotInstance:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false

Conditions:
  ShouldDeployAlb: !Equals [!Ref DeployAlb, true]
  IsProduction: !Equals [!Ref Environment, production]
  ShouldUseSpot: !Equals [!Ref UseSpotInstance, true]
  IsNotDevelopment: !Not [!Equals [!Ref Environment, development]]

Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Condition: ShouldDeployAlb
    Properties:
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets: !Ref PublicSubnetIds

  ProductionScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Condition: IsProduction
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70.0
```

## Transform

Use `Transform` for macros like AWS::Serverless for SAM templates.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Description: SAM template for serverless application with EC2

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs18.x
      CodeUri: function/
```

## Resources Section

The `Resources` section is the only required section. It defines AWS resources to provision.

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0ff8a95407f89df2f
      InstanceType: t3.micro
      KeyName: my-key-pair
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-instance
```

## Outputs and Cross-Stack References

### Basic Outputs

```yaml
Outputs:
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref Ec2Instance

  PublicIp:
    Description: Public IP address
    Value: !GetAtt Ec2Instance.PublicIp

  PrivateIp:
    Description: Private IP address
    Value: !GetAtt Ec2Instance.PrivateIp

  AvailabilityZone:
    Description: Availability Zone
    Value: !GetAtt Ec2Instance.AvailabilityZone
```

### Exporting Values for Cross-Stack References

Export values so other stacks can import them.

```yaml
Outputs:
  InstanceId:
    Description: EC2 Instance ID for other stacks
    Value: !Ref Ec2Instance
    Export:
      Name: !Sub ${AWS::StackName}-InstanceId

  SecurityGroupId:
    Description: Security Group ID for other stacks
    Value: !Ref InstanceSecurityGroup
    Export:
      Name: !Sub ${AWS::StackName}-SecurityGroupId

  InstanceRoleArn:
    Description: IAM Role ARN for other stacks
    Value: !GetAtt Ec2Role.Arn
    Export:
      Name: !Sub ${AWS::StackName}-InstanceRoleArn

  TargetGroupArn:
    Description: Target Group ARN for other stacks
    Value: !Ref ApplicationTargetGroup
    Export:
      Name: !Sub ${AWS::StackName}-TargetGroupArn
```

### Importing Values in Another Stack

```yaml
Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID from network stack

  SecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Security Group ID from security stack

  InstanceRoleArn:
    Type: String
    Description: IAM Role ARN from security stack

  # Or use Fn::ImportValue for programmatic access
Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue
        Fn::Sub: ${NetworkStackName}-VpcId
      GroupDescription: Security group for application

  Instance:
    Type: AWS::EC2::Instance
    Properties:
      IamInstanceProfile: !ImportValue
        Fn::Sub: ${SecurityStackName}-InstanceRoleArn
```

### Cross-Stack Reference Pattern

Create a dedicated security stack that exports values:

```yaml
# security-stack.yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Security resources stack

Resources:
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instances
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  Ec2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole

Outputs:
  SecurityGroupId:
    Value: !Ref InstanceSecurityGroup
    Export:
      Name: !Sub ${AWS::StackName}-SecurityGroupId

  InstanceRoleArn:
    Value: !GetAtt Ec2Role.Arn
    Export:
      Name: !Sub ${AWS::StackName}-InstanceRoleArn
```

Application stack imports these values:

```yaml
# application-stack.yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Application stack that imports from security stack

Parameters:
  SecurityStackName:
    Type: String
    Description: Name of the security stack
    Default: security-stack

Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      SecurityGroupIds:
        - !ImportValue
          Fn::Sub: ${SecurityStackName}-SecurityGroupId
      IamInstanceProfile: !ImportValue
        Fn::Sub: ${SecurityStackName}-InstanceRoleArn
```
