# EC2 Instances Configuration

## Basic Instance Configuration

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      SubnetId: !Ref SubnetId
      SecurityGroupIds:
        - !Ref SecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-instance
        - Key: Environment
          Value: !Ref EnvironmentName
```

## Instance with Multiple Volumes

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 20
            DeleteOnTermination: true
            VolumeType: gp3
        - DeviceName: /dev/xvdh
          Ebs:
            VolumeSize: 50
            DeleteOnTermination: false
            VolumeType: gp3
        - DeviceName: /dev/xvdi
          Ebs:
            VolumeSize: 100
            DeleteOnTermination: false
            VolumeType: st1
```

## Instance with Detailed Monitoring

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      Monitoring: true
      Metrics:
        CollectionInterval: 60
```

## Instance with Placement

```yaml
Resources:
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      Placement:
        AvailabilityZone: !Select [0, !GetAZs '']
        GroupName: !Ref PlacementGroup
        Tenancy: default
```

## SPOT Instances

### SPOT Fleet

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: SPOT Fleet for cost-optimized instances

Parameters:
  MaxPrice:
    Type: Number
    Default: 0.05
    Description: Maximum price per instance hour

Resources:
  SpotFleet:
    Type: AWS::EC2::SpotFleet
    Properties:
      SpotFleetRequestConfigData:
        TargetCapacity: 10
        IamFleetRole: !GetAtt SpotFleetRole.Arn
        LaunchSpecifications:
          - InstanceType: t3.micro
            ImageId: !Ref AmiId
            SubnetId: !Ref SubnetId
            WeightedCapacity: 1
          - InstanceType: t3.small
            ImageId: !Ref AmiId
            SubnetId: !Ref SubnetId
            WeightedCapacity: 2
        AllocationStrategy: lowestPrice
        SpotPrice: !Sub ${MaxPrice}

  SpotFleetRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: spotfleet.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: SpotFleetPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ec2:DescribeInstances
                  - ec2:DescribeImages
                Resource: "*"
```

### SPOT Instance Request

```yaml
Resources:
  SpotRequest:
    Type: AWS::EC2::SpotFleet
    Properties:
      SpotFleetRequestConfigData:
        TargetCapacity: 1
        IamFleetRole: !GetAtt SpotFleetRole.Arn
        LaunchSpecifications:
          - InstanceType: t3.medium
            ImageId: !Ref AmiId
            SubnetId: !Ref SubnetId
            KeyName: !Ref KeyName
        Type: persistent
```

### SPOT Instance with Fallback

```yaml
Resources:
  OnDemandInstance:
    Type: AWS::EC2::Instance
    Condition: IsNotSpot
    Properties:
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType

  SpotInstance:
    Type: AWS::EC2::SpotFleet
    Condition: UseSpot
    Properties:
      SpotFleetRequestConfigData:
        TargetCapacity: 1
        IamFleetRole: !GetAtt SpotFleetRole.Arn
        LaunchSpecifications:
          - InstanceType: t3.medium
            ImageId: !Ref AmiId
            SubnetId: !Ref SubnetId
```

## Complete Example: Full EC2 Stack with ALB

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete EC2 stack with ALB, security groups, and IAM role

Parameters:
  EnvironmentName:
    Type: String
    Default: production

  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc
        - Key: Environment
          Value: !Ref EnvironmentName

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw
        - Key: Environment
          Value: !Ref EnvironmentName

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-1
        - Key: SubnetType
          Value: Public

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-2
        - Key: SubnetType
          Value: Public

  # Security Group for ALB
  AlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ALB
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-alb-sg
        - Key: Environment
          Value: !Ref EnvironmentName

  # Security Group for EC2
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instances
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref AlbSecurityGroup
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance-sg
        - Key: Environment
          Value: !Ref EnvironmentName

  # IAM Role with specific permissions
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
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource: !Sub "arn:aws:s3:::${S3BucketName}/*"
        - PolicyName: CloudWatchLogs
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/ec2/${EnvironmentName}/*"
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-ec2-role

  Ec2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref Ec2Role

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${EnvironmentName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      Type: application

  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${EnvironmentName}-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-tg

  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # EC2 Instance
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: !Ref InstanceType
      IamInstanceProfile: !Ref Ec2InstanceProfile
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      SubnetId: !Ref PublicSubnet1
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from $(hostname)</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance
        - Key: Environment
          Value: !Ref EnvironmentName

Outputs:
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref Ec2Instance

  InstancePublicIp:
    Description: EC2 Instance Public IP
    Value: !GetAtt Ec2Instance.PublicIp

  LoadBalancerDnsName:
    Description: ALB DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  TargetGroupArn:
    Description: Target Group ARN
    Value: !Ref ApplicationTargetGroup

  SecurityGroupId:
    Description: Instance Security Group ID
    Value: !Ref InstanceSecurityGroup

  RoleArn:
    Description: IAM Role ARN
    Value: !GetAtt Ec2Role.Arn
```
