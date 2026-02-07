# AWS CloudFormation EC2 - Examples

This file contains comprehensive examples for EC2 infrastructure patterns with CloudFormation.

## Example 1: Production-Ready EC2 with Auto Scaling

Complete production-ready EC2 configuration with Auto Scaling, ALB, and health checks.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production EC2 with Auto Scaling and Application Load Balancer

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    AllowedValues:
      - development
      - staging
      - production

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
      - t3.xlarge

  MinSize:
    Type: Number
    Default: 2
    Description: Minimum number of instances

  MaxSize:
    Type: Number
    Default: 10
    Description: Maximum number of instances

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

Conditions:
  IsProduction: !Equals [!Ref EnvironmentName, production]

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

  PublicSubnet3:
    Type: AWS::EC2::Subnet
    Condition: IsProduction
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.3.0/24
      AvailabilityZone: !Select [2, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-3
        - Key: SubnetType
          Value: Public

  # Security Groups
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

  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for instances
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref AlbSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref AlbSecurityGroup
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance-sg

  # IAM Role
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
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: S3ReadAccess
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "arn:aws:s3:::${EnvironmentName}-assets/*"
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
        - !If [IsProduction, !Ref PublicSubnet3, !Ref "AWS::NoValue"]
      Type: application
      LoadBalancerAttributes:
        - Key: idle_timeout.timeout_seconds
          Value: "60"
        - Key: deletion_protection.enabled
          Value: !If [IsProduction, "true", "false"]

  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${EnvironmentName}-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
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

  # Launch Configuration
  LaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: !Ref InstanceType
      IamInstanceProfile: !Ref Ec2InstanceProfile
      SecurityGroups:
        - !Ref InstanceSecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from $(hostname)</h1>" > /var/www/html/index.html

  # Auto Scaling Group
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub ${EnvironmentName}-asg
      LaunchConfigurationName: !Ref LaunchConfiguration
      MinSize: !Ref MinSize
      MaxSize: !Ref MaxSize
      DesiredCapacity: !Ref MinSize
      VPCZoneIdentifier:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
        - !If [IsProduction, !Ref PublicSubnet3, !Ref "AWS::NoValue"]
      TargetGroupARNs:
        - !Ref ApplicationTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance
          PropagateAtLaunch: true
        - Key: Environment
          Value: !Ref EnvironmentName
          PropagateAtLaunch: true

  # Scaling Policy
  ScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70.0
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

Outputs:
  LoadBalancerDnsName:
    Description: ALB DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  AutoScalingGroupName:
    Description: Auto Scaling Group Name
    Value: !Ref AutoScalingGroup

  TargetGroupArn:
    Description: Target Group ARN
    Value: !Ref ApplicationTargetGroup
```

## Example 2: SPOT Fleet with Cost Optimization

Cost-optimized SPOT fleet configuration with fallback to On-Demand.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: SPOT Fleet for cost-optimized instances with fallback

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

  TargetCapacity:
    Type: Number
    Default: 10
    Description: Target number of instances

  MaxPrice:
    Type: Number
    Default: 0.05
    Description: Maximum price per instance hour

Resources:
  # Security Group
  SpotSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for SPOT instances
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16

  # IAM Role for SPOT Fleet
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
                  - ec2:DescribeSpotFleetRequests
                  - ec2:RequestSpotFleet
                  - ec2:CancelSpotFleetRequests
                  - ec2:DescribeSpotFleetInstances
                Resource: "*"
              - Effect: Allow
                Action:
                  - elasticloadbalancing:RegisterInstancesWithLoadBalancer
                Resource: !Ref TargetGroupArn

  # SPOT Fleet
  SpotFleet:
    Type: AWS::EC2::SpotFleet
    Properties:
      SpotFleetRequestConfigData:
        TargetCapacity: !Ref TargetCapacity
        IamFleetRole: !GetAtt SpotFleetRole.Arn
        AllocationStrategy: capacityOptimized
        SpotPrice: !Sub ${MaxPrice}
        TerminateInstancesWithExpiration: true
        Type: request
        ValidFrom: !Sub ${AWS::StackName}-valid-from
        ValidUntil: !Sub ${AWS::StackName}-valid-until
        LaunchSpecifications:
          - ImageId: !Ref LatestAmiId
            InstanceType: t3.micro
            SubnetId: !Ref SubnetId
            SecurityGroups:
              - !Ref SpotSecurityGroup
            WeightedCapacity: 1
            SpotPlacement:
              AvailabilityZone: !Select [0, !GetAZs '']
          - ImageId: !Ref LatestAmiId
            InstanceType: t3.small
            SubnetId: !Ref SubnetId
            SecurityGroups:
              - !Ref SpotSecurityGroup
            WeightedCapacity: 2
            SpotPlacement:
              AvailabilityZone: !Select [0, !GetAZs '']
          - ImageId: !Ref LatestAmiId
            InstanceType: t3.medium
            SubnetId: !Ref SubnetId
            SecurityGroups:
              - !Ref SpotSecurityGroup
            WeightedCapacity: 2
            SpotPlacement:
              AvailabilityZone: !Select [1, !GetAZs '']

  # Target Group for SPOT instances
  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${AWS::StackName}-spot-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: instance
      HealthCheckPath: /health

Outputs:
  SpotFleetRequestId:
    Description: SPOT Fleet Request ID
    Value: !Ref SpotFleet
```

## Example 3: EC2 with Detailed Monitoring and CloudWatch

EC2 instance with CloudWatch metrics, alarms, and custom metrics.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: EC2 with CloudWatch monitoring and alarms

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  # EC2 Instance with detailed monitoring
  MonitoredInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: t3.micro
      Monitoring: true
      SecurityGroupIds:
        - !Ref SecurityGroup
      SubnetId: !Ref SubnetId
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-monitored

  # Security Group
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for monitored instance
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16

  # IAM Role for CloudWatch
  CloudWatchRole:
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
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

  # Instance Profile
  CloudWatchInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref CloudWatchRole

  # CPU High Alarm
  CpuHighAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-cpu-high
      AlarmDescription: Triggered when CPU utilization exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref MonitoredInstance
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref CpuHighAlarmTopic
      OKActions:
        - !Ref CpuHighAlarmTopic

  # CPU Low Alarm
  CpuLowAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-cpu-low
      AlarmDescription: Triggered when CPU utilization falls below 20%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref MonitoredInstance
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 20
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref CpuLowAlarmTopic

  # Status Check Alarm
  StatusCheckAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-status-check
      AlarmDescription: Triggered when instance status check fails
      MetricName: StatusCheckFailed
      Namespace: AWS/EC2
      Dimensions:
        - Name: InstanceId
          Value: !Ref MonitoredInstance
      Statistic: Maximum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 0
      ComparisonOperator: GreaterThanThreshold

  # SNS Topic for alarms
  CpuHighAlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-cpu-alerts

  CpuLowAlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-cpu-low-alerts

Outputs:
  InstanceId:
    Description: Monitored Instance ID
    Value: !Ref MonitoredInstance

  AlarmTopicArn:
    Description: SNS Topic ARN for CPU alerts
    Value: !Ref CpuHighAlarmTopic
```

## Example 4: Multi-Tier Architecture with ALB

Three-tier architecture with public ALB, private application tier, and security groups.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-tier architecture with ALB, app tier, and security groups

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  # Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.11.0/24
      AvailabilityZone: !Select [1, !GetAZs '']

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Security Groups
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
          Value: !Sub ${AWS::StackName}-alb-sg

  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application tier
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref AlbSecurityGroup
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-app-sg

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${AWS::StackName}-alb
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
      Name: !Sub ${AWS::StackName}-tg
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3

  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # EC2 Instance in private subnet
  AppInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: t3.micro
      SubnetId: !Ref PrivateSubnet1
      SecurityGroupIds:
        - !Ref AppSecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y java11
          # Application deployment commands here
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-app-instance
        - Key: Tier
          Value: Application

Outputs:
  LoadBalancerDnsName:
    Description: ALB DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  InstancePrivateIp:
    Description: Instance Private IP
    Value: !GetAtt AppInstance.PrivateIp
```

## Example 5: EC2 with RDS Connection

EC2 instance configured to connect to RDS database with proper security groups.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: EC2 instance with RDS database connection

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  # Public Subnet for EC2
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  # Private Subnet for RDS
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Security Group for EC2
  Ec2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          DestinationSecurityGroupId: !Ref DatabaseSecurityGroup

  # Security Group for RDS
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref Ec2SecurityGroup

  # RDS Subnet Group
  DbSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref PrivateSubnet

  # RDS Instance
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub ${AWS::StackName}-db
      Engine: postgres
      MasterUsername: admin
      MasterUserPassword: !Ref DbPassword
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DbSubnetGroup
      BackupRetentionPeriod: 7
      MultiAZ: false

  # EC2 Instance
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: t3.micro
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref Ec2SecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y postgresql-jdbc
          # Database connection configuration
          echo "jdbc:postgresql://${DatabaseInstance.Endpoint.Address}:5432/mydb" > /etc/app/db.properties

  # Database Password (for demo only - use Secrets Manager in production)
  DbPassword:
    Type: String
    NoEcho: true
    Description: Database password

Outputs:
  DatabaseEndpoint:
    Description: RDS Endpoint
    Value: !GetAtt DatabaseInstance.Endpoint.Address

  InstancePublicIp:
    Description: EC2 Public IP
    Value: !GetAtt Ec2Instance.PublicIp
```

## Example 6: EC2 with User Data Scripts

EC2 instance with comprehensive user data scripts for application setup.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: EC2 instance with comprehensive user data scripts

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  # Security Group
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  # EC2 Instance with User Data
  Ec2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: t3.medium
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      SubnetId: !Ref SubnetId
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          set -e

          # Variables
          REGION=${AWS::Region}
          STACK_NAME=${AWS::StackName}

          echo "Starting instance initialization..."
          echo "Region: $REGION"
          echo "Stack: $STACK_NAME"

          # Update system
          yum update -y

          # Install dependencies
          yum install -y \
            wget \
            unzip \
            java-11-openjdk-devel \
            git \
            nginx

          # Configure timezone
          timedatectl set-timezone UTC

          # Enable services
          systemctl enable nginx
          systemctl start nginx

          # Create application directory
          mkdir -p /opt/app
          chown ec2-user:ec2-user /opt/app

          # Download application (example)
          cd /opt/app
          wget -O app.jar https://example.com/app.jar

          # Create systemd service
          cat > /etc/systemd/system/app.service << 'EOF'
          [Unit]
          Description=My Application
          After=network.target

          [Service]
          Type=simple
          User=ec2-user
          WorkingDirectory=/opt/app
          ExecStart=/usr/bin/java -jar /opt/app/app.jar
          Restart=always
          Environment=REGION=${AWS::Region}

          [Install]
          WantedBy=multi-user.target
          EOF

          systemctl daemon-reload
          systemctl enable app
          systemctl start app

          # Configure log rotation
          cat > /etc/logrotate.d/app << 'EOF'
          /var/log/app/*.log {
            daily
            rotate 14
            compress
            delaycompress
            missingok
            notifempty
          }
          EOF

          # Send signal to CloudFormation
          /opt/aws/bin/cfn-init -v \
            --resource Ec2Instance \
            --stack ${AWS::StackName} \
            --region ${AWS::Region}

          echo "Instance initialization completed"

Outputs:
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref Ec2Instance

  InstancePublicIp:
    Description: EC2 Public IP
    Value: !GetAtt Ec2Instance.PublicIp
```

## Example 7: EC2 with Multiple ENIs

EC2 instance with multiple network interfaces for different purposes.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: EC2 instance with multiple network interfaces

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  # Subnets
  ManagementSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  ApplicationSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  # Security Groups
  ManagementSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for management
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16

  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  # Network Interfaces
  ManagementNetworkInterface:
    Type: AWS::EC2::NetworkInterface
    Properties:
      SubnetId: !Ref ManagementSubnet
      Description: Management ENI
      GroupSet:
        - !Ref ManagementSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-mgmt-ni

  ApplicationNetworkInterface:
    Type: AWS::EC2::NetworkInterface
    Properties:
      SubnetId: !Ref ApplicationSubnet
      Description: Application ENI
      GroupSet:
        - !Ref ApplicationSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-app-ni

  # EC2 Instance
  MultiEniInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: t3.large
      NetworkInterfaces:
        - NetworkInterfaceId: !Ref ManagementNetworkInterface
          DeviceIndex: 0
        - NetworkInterfaceId: !Ref ApplicationNetworkInterface
          DeviceIndex: 1
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-multi-nic-instance

Outputs:
  ManagementInterfaceIp:
    Description: Management Network Interface IP
    Value: !GetAtt ManagementNetworkInterface.PrimaryPrivateIpAddress

  ApplicationInterfaceIp:
    Description: Application Network Interface IP
    Value: !GetAtt ApplicationNetworkInterface.PrimaryPrivateIpAddress
```

## Example 8: Complete Stack with Nested Stacks

Modular architecture using nested stacks for reusability.

```yaml
# master.yaml - Master stack
AWSTemplateFormatVersion: 2010-09-09
Description: Master stack with nested stacks

Parameters:
  EnvironmentName:
    Type: String
    Default: production

Resources:
  # Network stack
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./network.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName

  # Security stack
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: ./security.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VpcId: !GetAtt NetworkStack.Outputs.VpcId

  # Application stack
  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: SecurityStack
    Properties:
      TemplateURL: ./application.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        SubnetIds: !GetAtt NetworkStack.Outputs.PublicSubnetIds
        SecurityGroupId: !GetAtt SecurityStack.Outputs.InstanceSecurityGroupId

Outputs:
  LoadBalancerDnsName:
    Value: !GetAtt ApplicationStack.Outputs.LoadBalancerDnsName
```

```yaml
# security.yaml - Security resources
AWSTemplateFormatVersion: 2010-09-09
Description: Security resources stack

Parameters:
  EnvironmentName:
    Type: String

  VpcId:
    Type: AWS::EC2::VPC::Id

Resources:
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for instances
      VpcId: !Ref VpcId
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
          Value: !Sub ${EnvironmentName}-instance-sg

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
        - arn:aws:iam::aws:policy/ReadOnlyAccess

  Ec2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref Ec2Role

Outputs:
  InstanceSecurityGroupId:
    Value: !Ref InstanceSecurityGroup

  InstanceRoleArn:
    Value: !GetAtt Ec2Role.Arn
```

```yaml
# application.yaml - Application resources
AWSTemplateFormatVersion: 2010-09-09
Description: Application resources stack

Parameters:
  EnvironmentName:
    Type: String

  VpcId:
    Type: AWS::EC2::VPC::Id

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

  SecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id

Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${EnvironmentName}-alb
      Scheme: internet-facing
      SecurityGroups:
        - !Ref SecurityGroupId
      Subnets: !Ref SubnetIds

  ApplicationTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${EnvironmentName}-tg
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: instance
      HealthCheckPath: /health

  ApplicationListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ApplicationTargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

Outputs:
  LoadBalancerDnsName:
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  TargetGroupArn:
    Value: !Ref ApplicationTargetGroup
```
