# AWS CloudFormation Auto Scaling - Examples

This file contains comprehensive examples for Auto Scaling patterns with CloudFormation.

## Example 1: Complete EC2 Auto Scaling with ALB

Complete Auto Scaling group with Application Load Balancer, multiple availability zones, and health checks.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production EC2 Auto Scaling with Application Load Balancer

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large

  AmiId:
    Type: AWS::EC2::Image::Id
    Description: AMI ID for instances

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: SSH key pair name

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Public subnet IDs for ALB

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnet IDs for instances

Mappings:
  EnvironmentConfig:
    dev:
      MinSize: 1
      MaxSize: 3
      DesiredCapacity: 1
      InstanceType: t3.micro
      SpotPrice: ""
    staging:
      MinSize: 2
      MaxSize: 6
      DesiredCapacity: 2
      InstanceType: t3.medium
      SpotPrice: ""
    production:
      MinSize: 3
      MaxSize: 12
      DesiredCapacity: 3
      InstanceType: t3.large
      SpotPrice: ""

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]
  UseSpot: !Or [!Equals [!Ref Environment, dev], !Equals [!Ref Environment, staging]]

Resources:
  # Security Group for Instances
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-instance-sg"
      GroupDescription: Security group for Auto Scaling instances
      VpcId: !Ref VpcId
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
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  # Security Group for ALB
  AlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: Security group for Application Load Balancer
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
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  # Launch Configuration
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc-${Environment}"
      ImageId: !Ref AmiId
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      SecurityGroups:
        - !Ref InstanceSecurityGroup
      InstanceMonitoring:
        Enabled: true
      SpotPrice: !If [UseSpot, !FindInMap [EnvironmentConfig, !Ref Environment, SpotPrice], !Ref AWS::NoValue]
      UserData:
        Fn::Base64: |
          #!/bin/bash
          # Set hostname
          hostnamectl set-hostname "$(curl -s http://169.254.169.254/latest/meta-data/instance-id)"
          # Update packages
          yum update -y
          # Install Apache
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          # Create health check endpoint
          echo "OK - Instance $(hostname)" > /var/www/html/health.html
          # Configure logging
          echo "<VirtualHost *:80>
            CustomLog /var/log/httpd/access.log combined
            ErrorLog /var/log/httpd/error.log
          </VirtualHost>" > /etc/httpd/conf.d/logging.conf
          # Instance metadata
          echo "Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)" > /var/www/html/metadata.html
          echo "AZ: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)" >> /var/www/html/metadata.html

  # Auto Scaling Group
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg-${Environment}"
      MinSize: !FindInMap [EnvironmentConfig, !Ref Environment, MinSize]
      MaxSize: !FindInMap [EnvironmentConfig, !Ref Environment, MaxSize]
      DesiredCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, DesiredCapacity]
      VPCZoneIdentifier: !Ref PrivateSubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration
      TargetGroupARNs:
        - !Ref MyTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      TerminationPolicies:
        - OldestInstance
        - Default
      InstanceMaintenancePolicy:
        MinHealthyPercentage: 50
        MaxHealthyPercentage: 200
      Tags:
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true
        - Key: Name
          Value: !Sub "${AWS::StackName}-instance-${Environment}"
          PropagateAtLaunch: true
        - Key: ManagedBy
          Value: CloudFormation
          PropagateAtLaunch: true
        - Key: CostCenter
          Value: "engineering"
          PropagateAtLaunch: true

  # Application Load Balancer
  MyApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb-${Environment}"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets: !Ref PublicSubnetIds
      Type: application
      IpAddressType: ipv4

  # ALB Target Group
  MyTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg-${Environment}"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health.html
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 5
      UnhealthyThresholdCount: 2
      TargetType: instance
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  # ALB Listener
  MyAlbListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          ForwardConfig:
            TargetGroupStickinessConfig:
              Enabled: false
            TargetGroups:
              - TargetGroupArn: !Ref MyTargetGroup
                Weight: 1
          TargetGroupArn: !Ref MyTargetGroup
      LoadBalancerArn: !Ref MyApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # Target Tracking Scaling Policy
  CpuTargetTrackingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cpu-target-tracking"
      PolicyType: TargetTrackingScaling
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70
        DisableScaleIn: !IsProduction

Outputs:
  AutoScalingGroupName:
    Description: Name of the Auto Scaling Group
    Value: !Ref MyAutoScalingGroup

  AlbDnsName:
    Description: DNS name of the Application Load Balancer
    Value: !GetAtt MyApplicationLoadBalancer.DNSName

  AlbArn:
    Description: ARN of the Application Load Balancer
    Value: !Ref MyApplicationLoadBalancer

  TargetGroupArn:
    Description: ARN of the Target Group
    Value: !Ref MyTargetGroup
```

## Example 2: Auto Scaling with Launch Template and Mixed Instances

Auto Scaling group using launch template with mixed on-demand and Spot instances.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Auto Scaling with Launch Template and Mixed Instances Policy

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  AmiId:
    Type: AWS::EC2::Image::Id
    Description: AMI ID for instances

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Subnet IDs

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: SSH key pair name

Mappings:
  InstanceTypes:
    x86:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large
    arm:
      - t4g.micro
      - t4g.small
      - t4g.medium

Resources:
  # Launch Template
  MyLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub "${AWS::StackName}-lt-${Environment}"
      LaunchTemplateData:
        ImageId: !Ref AmiId
        KeyName: !Ref KeyName
        DisableApiTermination: false
        InstanceInitiatedShutdownBehavior: terminate
        EbsOptimized: true
        Monitoring:
          Enabled: true
        NetworkInterfaces:
          - DeviceIndex: 0
            AssociatePublicIpAddress: false
            Groups:
              - !Ref SecurityGroup
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub "${AWS::StackName}-instance"
              - Key: Environment
                Value: !Ref Environment
              - Key: ManagedBy
                Value: CloudFormation
          - ResourceType: volume
            Tags:
              - Key: Environment
                Value: !Ref Environment
              - Key: ManagedBy
                Value: CloudFormation
        UserData:
          Fn::Base64: |
            #!/bin/bash
            yum update -y
            yum install -y amazon-ssm-agent
            systemctl start amazon-ssm-agent

  # Security Group
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-sg"
      GroupDescription: Security group for instances
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref AlbSg
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref AlbSg
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16

  AlbSg:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: ALB security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # Auto Scaling Group with Mixed Instances
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg-${Environment}"
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchTemplate:
        LaunchTemplateId: !Ref MyLaunchTemplate
        Version: !GetAtt MyLaunchTemplate.LatestVersionNumber
      MixedInstancesPolicy:
        InstancesDistribution:
          OnDemandAllocationStrategy: prioritized
          OnDemandBaseCapacity: 2
          OnDemandPercentageAboveBaseCapacity: 50
          SpotAllocationStrategy: capacity-optimized
          SpotInstancePools: 3
          SpotMaxPrice: "0.06"
        LaunchTemplate:
          LaunchTemplateId: !Ref MyLaunchTemplate
          Version: !GetAtt MyLaunchTemplate.LatestVersionNumber
          Overrides:
            - InstanceType: t3.micro
            - InstanceType: t3.small
            - InstanceType: t3.medium
            - InstanceType: t4g.micro
            - InstanceType: t4g.small
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300

  # Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg-${Environment}"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30

  # Scaling Policy with Steps
  StepScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-step-scaling"
      PolicyType: StepScaling
      AdjustmentType: PercentChangeInCapacity
      Cooldown: 300
      StepAdjustments:
        - MetricIntervalLowerBound: 0
          MetricIntervalUpperBound: 10000
          ScalingAdjustment: 100
        - MetricIntervalLowerBound: 10000
          MetricIntervalUpperBound: 20000
          ScalingAdjustment: 200
        - MetricIntervalLowerBound: 20000
          ScalingAdjustment: 300
      AutoScalingGroupName: !Ref MyAutoScalingGroup

  # CloudWatch Alarm for Step Scaling
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      AlarmDescription: Scale out when CPU is high
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref MyAutoScalingGroup
      Statistic: Average
      Period: 60
      EvaluationPeriods: 3
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref StepScalingPolicy

Outputs:
  LaunchTemplateId:
    Description: Launch template ID
    Value: !Ref MyLaunchTemplate

  AutoScalingGroupName:
    Description: Auto Scaling group name
    Value: !Ref MyAutoScalingGroup
```

## Example 3: Auto Scaling with Lifecycle Hooks

Auto Scaling group with lifecycle hooks for custom actions during instance launch and termination.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Auto Scaling with Lifecycle Hooks for instance management

Parameters:
  Environment:
    Type: String
    Default: production

  AmiId:
    Type: AWS::EC2::Image::Id

  VpcId:
    Type: AWS::EC2::VPC::Id

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  # Launch Configuration
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc"
      ImageId: !Ref AmiId
      InstanceType: t3.micro
      SecurityGroups:
        - !Ref InstanceSecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          # Bootstrap script
          yum update -y
          # Install SSM agent for lifecycle management
          yum install -y amazon-ssm-agent
          systemctl enable amazon-ssm-agent
          systemctl start amazon-ssm-agent
          # Write instance metadata to S3 for lifecycle tracking
          INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
          AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
          aws s3api put-object --bucket ${BootstrapBucket} --key "instances/${INSTANCE_ID}.json" --Body "{\"instanceId\":\"${INSTANCE_ID}\",\"az\":\"${AZ}\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"status\":\"launched\"}"

  # Security Group
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-sg"
      GroupDescription: Instance security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # Auto Scaling Group
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration
      LifecycleHookSpecificationList:
        - LifecycleHookName: !Sub "${AWS::StackName}-launch-hook"
          LifecycleTransition: autoscaling:EC2_INSTANCE_LAUNCHING
          HeartbeatTimeout: 900
          NotificationTargetARN: !Ref LifecycleTopic
          RoleARN: !GetAtt LifecycleRole.Arn
          DefaultResult: CONTINUE
        - LifecycleHookName: !Sub "${AWS::StackName}-termination-hook"
          LifecycleTransition: autoscaling:EC2_INSTANCE_TERMINATING
          HeartbeatTimeout: 3600
          NotificationTargetARN: !Ref LifecycleTopic
          RoleARN: !GetAtt LifecycleRole.Arn
          DefaultResult: CONTINUE

  # Lifecycle Hook - Instance Launch
  LifecycleHookLaunch:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: !Sub "${AWS::StackName}-launch-hook"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_LAUNCHING
      HeartbeatTimeout: 900
      NotificationTargetARN: !Ref LifecycleTopic
      RoleARN: !GetAtt LifecycleRole.Arn
      DefaultResult: CONTINUE

  # Lifecycle Hook - Instance Termination
  LifecycleHookTermination:
    Type: AWS::AutoScaling::LifecycleHook
    Properties:
      LifecycleHookName: !Sub "${AWS::StackName}-termination-hook"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      LifecycleTransition: autoscaling:EC2_INSTANCE_TERMINATING
      HeartbeatTimeout: 3600
      NotificationTargetARN: !Ref LifecycleTopic
      RoleARN: !GetAtt LifecycleRole.Arn
      DefaultResult: CONTINUE

  # SNS Topic for Lifecycle Events
  LifecycleTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-lifecycle-${Environment}"
      Subscription:
        - Endpoint: !Ref LifecycleNotificationEmail
          Protocol: email

  # IAM Role for Lifecycle Hooks
  LifecycleRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lifecycle-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: autoscaling.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-lifecycle-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sns:Publish
                Resource: !Ref LifecycleTopic
              - Effect: Allow
                Action:
                  - ssm:GetParameters
                Resource: !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/*"
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:DeleteObject
                Resource: !Sub "${BootstrapBucket}/*"

Parameters:
  LifecycleNotificationEmail:
    Type: String
    Description: Email for lifecycle notifications

  BootstrapBucket:
    Type: String
    Description: S3 bucket for bootstrap data

Outputs:
  LifecycleTopicArn:
    Description: SNS Topic ARN for lifecycle events
    Value: !Ref LifecycleTopic

  AutoScalingGroupName:
    Description: Auto Scaling Group name
    Value: !Ref MyAutoScalingGroup
```

## Example 4: ECS Service Auto Scaling

ECS service with Application Auto Scaling for task count management.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS Service with Auto Scaling

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues:
      - dev
      - staging
      - production

  ImageUrl:
    Type: String
    Description: Container image URL

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Public subnet IDs

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnet IDs

Mappings:
  EnvironmentConfig:
    dev:
      DesiredCount: 1
      MinCount: 1
      MaxCount: 3
      Cpu: "256"
      Memory: "512"
    staging:
      DesiredCount: 2
      MinCount: 2
      MaxCount: 6
      Cpu: "512"
      Memory: "1024"
    production:
      DesiredCount: 4
      MinCount: 2
      MaxCount: 10
      Cpu: "1024"
      Memory: "2048"

Resources:
  # ECS Cluster
  EcsCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster-${Environment}"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${AWS::StackName}-task-${Environment}"
      Cpu: !FindInMap [EnvironmentConfig, !Ref Environment, Cpu]
      Memory: !FindInMap [EnvironmentConfig, !Ref Environment, Memory]
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref EcsTaskExecutionRole
      ContainerDefinitions:
        - Name: web
          Image: !Ref ImageUrl
          PortMappings:
            - ContainerPort: 80
              Protocol: tcp
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:80/ || exit 1
            Interval: 30
            Timeout: 5
            Retries: 3
          Ulimits:
            - Name: nofile
              SoftLimit: 65536
              HardLimit: 65536

  # ECS Service
  EcsService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service-${Environment}"
      Cluster: !Ref EcsCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: !FindInMap [EnvironmentConfig, !Ref Environment, DesiredCount]
      LaunchType: FARGATE
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 50
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: DISABLED
          SecurityGroups:
            - !Ref EcsSecurityGroup
          Subnets: !Ref PrivateSubnetIds
      LoadBalancers:
        - ContainerName: web
          ContainerPort: 80
          TargetGroupArn: !Ref TargetGroup

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb-${Environment}"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSecurityGroup
      Subnets: !Ref PublicSubnetIds
      Type: application

  # Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg-${Environment}"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /
      HealthCheckIntervalSeconds: 30
      TargetType: ip

  # ALB Listener
  AlbListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # Application Auto Scaling Scalable Target
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, MaxCount]
      MinCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, MinCount]
      ResourceId: !Sub "service/${EcsCluster}/${EcsService.Name}"
      RoleARN: !GetAtt EcsScalingRole.Arn
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs

  # Target Tracking Scaling Policy
  CpuTargetTrackingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cpu-target-tracking"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  # Memory Target Tracking Policy
  MemoryTargetTrackingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-memory-target-tracking"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 80
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageMemoryUtilization
        ScaleInCooldown: 300
        ScaleOutCooldown: 60

  # Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${AWS::StackName}-${Environment}"
      RetentionInDays: 30

  # Security Groups
  EcsSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-ecs-sg"
      GroupDescription: Security group for ECS tasks
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref AlbSecurityGroup

  AlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: Security group for ALB
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # IAM Roles
  EcsTaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-ecs-task-execution-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  EcsScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-ecs-scaling-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: application-autoscaling.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceAutoscaleRole

Outputs:
  ClusterName:
    Description: ECS Cluster name
    Value: !Ref EcsCluster

  ServiceName:
    Description: ECS Service name
    Value: !Ref EcsService

  AlbDnsName:
    Description: ALB DNS name
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  ScalableTargetArn:
    Description: Scalable Target ARN
    Value: !Ref ScalableTarget
```

## Example 5: Scheduled Scaling Actions

Auto Scaling with scheduled actions for predictable traffic patterns.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Auto Scaling with Scheduled Scaling Actions

Parameters:
  Environment:
    Type: String
    Default: production

  AmiId:
    Type: AWS::EC2::Image::Id

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  # Launch Configuration
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc"
      ImageId: !Ref AmiId
      InstanceType: t3.micro
      SecurityGroups:
        - !Ref SecurityGroup

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-sg"
      GroupDescription: Instance SG
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # Auto Scaling Group
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg"
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration

  # Morning Scale Up - Weekdays at 7 AM
  MorningScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      ScheduledActionName: !Sub "${AWS::StackName}-morning-scale-up"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      MinSize: "5"
      MaxSize: "15"
      DesiredCapacity: "5"
      Recurrence: "0 7 * * 1-5"

  # Evening Scale Down - Weekdays at 7 PM
  EveningScaleDown:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      ScheduledActionName: !Sub "${AWS::StackName}-evening-scale-down"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      Recurrence: "0 19 * * 1-5"

  # Weekend Scale Down - Saturday at 1 AM
  WeekendScaleDown:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      ScheduledActionName: !Sub "${AWS::StackName}-weekend-scale-down"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      MinSize: "1"
      MaxSize: "5"
      DesiredCapacity: "1"
      Recurrence: "0 1 * * 0"

  # Weekend Scale Up - Monday at 6 AM
  WeekendScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      ScheduledActionName: !Sub "${AWS::StackName}-weekend-scale-up"
      AutoScalingGroupName: !Ref MyAutoScalingGroup
      MinSize: "5"
      MaxSize: "15"
      DesiredCapacity: "5"
      Recurrence: "0 6 * * 1"

Outputs:
  ScheduledActionArns:
    Description: ARNs of scheduled actions
    Value: !Join [",", [!Ref MorningScaleUp, !Ref EveningScaleDown, !Ref WeekendScaleDown, !Ref WeekendScaleUp]]
```

## Example 6: Complete Production Auto Scaling with Alarms

Complete production-ready Auto Scaling with comprehensive CloudWatch alarms.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production Auto Scaling with comprehensive monitoring

Parameters:
  Environment:
    Type: String
    Default: production

  AmiId:
    Type: AWS::EC2::Image::Id

  VpcId:
    Type: AWS::EC2::VPC::Id

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

  AlertEmail:
    Type: String
    Description: Email for alert notifications

Resources:
  # Launch Configuration
  MyLaunchConfiguration:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      LaunchConfigurationName: !Sub "${AWS::StackName}-lc"
      ImageId: !Ref AmiId
      InstanceType: t3.micro
      SecurityGroups:
        - !Ref SecurityGroup
      InstanceMonitoring:
        Enabled: true
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-sg"
      GroupDescription: Instance security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # Auto Scaling Group
  MyAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${AWS::StackName}-asg-${Environment}"
      MinSize: "2"
      MaxSize: "10"
      DesiredCapacity: "2"
      VPCZoneIdentifier: !Ref SubnetIds
      LaunchConfigurationName: !Ref MyLaunchConfiguration
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true

  # Scaling Policies
  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-scale-up"
      PolicyType: StepScaling
      AdjustmentType: PercentChangeInCapacity
      Cooldown: 300
      StepAdjustments:
        - MetricIntervalLowerBound: 0
          MetricIntervalUpperBound: 10000
          ScalingAdjustment: 100
        - MetricIntervalLowerBound: 10000
          MetricIntervalUpperBound: 20000
          ScalingAdjustment: 200
      AutoScalingGroupName: !Ref MyAutoScalingGroup

  ScaleDownPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-scale-down"
      PolicyType: StepScaling
      AdjustmentType: PercentChangeInCapacity
      Cooldown: 600
      StepAdjustments:
        - MetricIntervalLowerBound: -20000
          MetricIntervalUpperBound: 0
          ScalingAdjustment: -50
      AutoScalingGroupName: !Ref MyAutoScalingGroup

  # SNS Topic for Alarms
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-alerts-${Environment}"
      Subscription:
        - Endpoint: !Ref AlertEmail
          Protocol: email

  # CloudWatch Alarms

  # High CPU Alarm
  HighCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-cpu"
      AlarmDescription: Scale out when CPU utilization is high
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref MyAutoScalingGroup
      Statistic: Average
      Period: 60
      EvaluationPeriods: 3
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref ScaleUpPolicy
        - !Ref AlertTopic
      OKActions:
        - !Ref AlertTopic

  # Low CPU Alarm
  LowCpuAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-low-cpu"
      AlarmDescription: Scale in when CPU utilization is low
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref MyAutoScalingGroup
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 30
      ComparisonOperator: LessThanThreshold
      AlarmActions:
        - !Ref ScaleDownPolicy
        - !Ref AlertTopic
      OKActions:
        - !Ref AlertTopic

  # High Request Count Alarm
  HighRequestCountAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-requests"
      AlarmDescription: Alarm when request count per instance is too high
      MetricName: RequestCountPerTarget
      Namespace: AWS/ApplicationELB
      Dimensions:
        - Name: TargetGroup
          Value: !GetAtt TargetGroup.TargetGroupName
        - Name: LoadBalancer
          Value: !GetAtt LoadBalancer.LoadBalancerFullName
      Statistic: Average
      Period: 60
      EvaluationPeriods: 3
      Threshold: 1000
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref ScaleUpPolicy
        - !Ref AlertTopic

  # Unhealthy Host Count Alarm
  UnhealthyHostAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-unhealthy-hosts"
      AlarmDescription: Alarm when there are unhealthy hosts
      MetricName: UnHealthyHostCount
      Namespace: AWS/ApplicationELB
      Dimensions:
        - Name: TargetGroup
          Value: !GetAtt TargetGroup.TargetGroupName
        - Name: LoadBalancer
          Value: !GetAtt LoadBalancer.LoadBalancerFullName
      Statistic: Maximum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  # High Latency Alarm
  HighLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-latency"
      AlarmDescription: Alarm when latency is too high
      MetricName: TargetResponseTime
      Namespace: AWS/ApplicationELB
      Dimensions:
        - Name: TargetGroup
          Value: !GetAtt TargetGroup.TargetGroupName
        - Name: LoadBalancer
          Value: !GetAtt LoadBalancer.LoadBalancerFullName
      Statistic: p99
      Period: 60
      EvaluationPeriods: 3
      Threshold: 2
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  # ALB and Target Group
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${AWS::StackName}-alb"
      Scheme: internet-facing
      SecurityGroups:
        - !Ref AlbSg
      Subnets: !Ref SubnetIds

  AlbSg:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: ALB security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-tg"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /

Outputs:
  AutoScalingGroupName:
    Description: Auto Scaling Group name
    Value: !Ref MyAutoScalingGroup

  AlertTopicArn:
    Description: SNS Topic ARN for alerts
    Value: !Ref AlertTopic

  LoadBalancerDns:
    Description: Load Balancer DNS name
    Value: !GetAtt LoadBalancer.DNSName
```

## Example 7: Lambda with Provisioned Concurrency Auto Scaling

Lambda function with Application Auto Scaling for provisioned concurrency management.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda with Provisioned Concurrency Auto Scaling

Parameters:
  Environment:
    Type: String
    Default: production

  CodeBucket:
    Type: String
    Description: S3 bucket for Lambda code

  CodeKey:
    Type: String
    Description: S3 key for Lambda code

Resources:
  # Lambda Function
  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-api-${Environment}"
      Runtime: python3.11
      Handler: app.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Ref CodeKey
      MemorySize: 512
      Timeout: 30
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO

  # Lambda Version
  LambdaVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref MyLambdaFunction
      Description: Version with provisioned concurrency

  # Application Auto Scaling Scalable Target
  LambdaScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 20
      MinCapacity: 5
      ResourceId: !Sub "function:${MyLambdaFunction}:${LambdaVersion.Version}"
      RoleARN: !GetAtt LambdaScalingRole.Arn
      ScalableDimension: lambda:function:ProvisionedConcurrency
      ServiceNamespace: lambda

  # Target Tracking Scaling Policy
  LambdaTargetTrackingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-lambda-target-tracking"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref LambdaScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 90
        PredefinedMetricSpecification:
          PredefinedMetricType: LambdaProvisionedConcurrencyUtilization
        ScaleInCooldown: 120
        ScaleOutCooldown: 60

  # Step Scaling Policy for burst handling
  LambdaStepScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-lambda-step-scaling"
      PolicyType: StepScaling
      AdjustmentType: PercentChangeInCapacity
      Cooldown: 120
      StepScalingPolicyConfiguration:
        StepAdjustments:
          - MetricIntervalLowerBound: 0
            ScalingAdjustment: 20
          - MetricIntervalLowerBound: 10
            ScalingAdjustment: 50
      ScalingTargetId: !Ref LambdaScalableTarget

  # CloudWatch Alarm for Step Scaling
  HighUtilizationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${AWS::StackName}-high-utilization"
      AlarmDescription: Alarm when provisioned concurrency utilization is high
      MetricName: ProvisionedConcurrencyUtilization
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref MyLambdaFunction
        - Name: Resource
          Value: !Sub "${MyLambdaFunction}:${LambdaVersion.Version}"
      Statistic: Maximum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 95
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref LambdaStepScalingPolicy

  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-exec-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  # Lambda Scaling Role
  LambdaScalingRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-scaling-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: application-autoscaling.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-lambda-scaling-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - lambda:PutProvisionedConcurrencyConfig
                  - lambda:GetProvisionedConcurrencyConfig
                  - lambda:ListProvisionedConcurrencyConfigs
                Resource: !Ref MyLambdaFunction

Outputs:
  FunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt MyLambdaFunction.Arn

  FunctionVersion:
    Description: Lambda function version
    Value: !Ref LambdaVersion

  ScalableTargetArn:
    Description: Scalable target ARN
    Value: !Ref LambdaScalableTarget
```
