# Deployment Strategies and CloudFormation Templates

## Rolling Deployment

### GitHub Actions Rolling Deployment

```yaml
- name: Deploy to ECS (Rolling)
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.render-task.outputs.task-definition }}
    service: my-service
    cluster: my-cluster
    wait-for-service-stability: true
```

### CloudFormation Service Configuration

```yaml
ECSService:
  Type: AWS::ECS::Service
  Properties:
    ServiceName: my-service
    Cluster: !Ref ECSCluster
    TaskDefinition: !Ref TaskDefinition
    DeploymentConfiguration:
      MaximumPercent: 200
      MinimumHealthyPercent: 100
      DeploymentCircuitBreaker:
        Enable: true
        Rollback: true
    HealthCheckGracePeriodSeconds: 60
    EnableECSManagedTags: true
    PropagateTags: SERVICE
```

## Blue/Green Deployment

### GitHub Actions Blue/Green Deployment

```yaml
- name: Deploy to ECS (Blue/Green)
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.render-task.outputs.task-definition }}
    service: my-service
    cluster: my-cluster
    codedeploy-appspec: appspec.yaml
    codedeploy-application: my-app
    codedeploy-deployment-group: my-deployment-group
    wait-for-service-stability: true
```

### AppSpec Configuration

**appspec.yaml:**

```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: my-app
          ContainerPort: 8080
        PlatformVersion: "1.4.0"
```

### CodeDeploy Application and Deployment Group

```yaml
CodeDeployApplication:
  Type: AWS::CodeDeploy::Application
  Properties:
    ApplicationName: my-app
    ComputePlatform: ECS

CodeDeployDeploymentGroup:
  Type: AWS::CodeDeploy::DeploymentGroup
  Properties:
    ApplicationName: !Ref CodeDeployApplication
    DeploymentGroupName: my-deployment-group
    ServiceRoleArn: !Ref CodeDeployServiceRole
    DeploymentConfigName: CodeDeployDefault.ECSAllAtOnce
    DeploymentStyle:
      DeploymentType: BLUE_GREEN
      DeploymentOption: WITH_TRAFFIC_CONTROL
    AutoRollbackConfiguration:
      Enabled: true
      Events:
        - DEPLOYMENT_FAILURE
        - DEPLOYMENT_STOP_ON_ALARM
        - DEPLOYMENT_STOP_ON_REQUEST
    AlarmConfiguration:
      Alarms:
        - !Ref CPUPercentageAlarm
        - !Ref MemoryPercentageAlarm
    BlueGreenDeploymentConfiguration:
      TerminateBlueInstancesOnDeploymentSuccess:
        Action: TERMINATE
        WaitTimeInMinutes: 5
      DeploymentReadyOption:
        ActionOnTimeout: CONTINUE_DEPLOYMENT
        WaitTimeInMinutes: 0
    LoadBalancerInfo:
      TargetGroupPairInfoList:
        - TargetGroups:
            - Ref: BlueTargetGroup
            - Ref: GreenTargetGroup
          ProdTrafficRoute:
            ListenerArns:
              - !Ref ProductionListener

# CloudWatch Alarms
CPUPercentageAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alarm for CPU percentage
    MetricName: CPUUtilization
    Namespace: AWS/ECS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold

MemoryPercentageAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alarm for Memory percentage
    MetricName: MemoryUtilization
    Namespace: AWS/ECS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
```

## Complete CloudFormation ECS Stack

### Full Infrastructure Template

**ecs-stack.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: ECS Fargate Service with CloudFormation

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
  DesiredCount:
    Type: Number
    Default: 2
  CPU:
    Type: String
    Default: '256'
  Memory:
    Type: String
    Default: '512'
  ImageUrl:
    Type: String

Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-cluster'
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub '${Environment}-task'
      Cpu: !Ref CPU
      Memory: !Ref Memory
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: my-app
          Image: !Ref ImageUrl
          PortMappings:
            - ContainerPort: 8080
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  ECSService:
    Type: AWS::ECS::Service
    DependsOn: LoadBalancerListener
    Properties:
      ServiceName: !Sub '${Environment}-service'
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: !Ref DesiredCount
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnetA
            - !Ref PrivateSubnetB
          SecurityGroups:
            - !Ref ContainerSecurityGroup
          AssignPublicIp: DISABLED
      LoadBalancers:
        - ContainerName: my-app
          ContainerPort: 8080
          TargetGroupArn: !Ref TargetGroup
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 100
        DeploymentCircuitBreaker:
          Enable: true
          Rollback: true
      HealthCheckGracePeriodSeconds: 60

  # IAM Roles
  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: TaskRolePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ssm:GetParameter
                  - ssm:GetParameters
                Resource: !Sub 'arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/my-app/*'

  # Security
  ContainerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ECS containers
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
          IpProtocol: -1

  # Load Balancer
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Type: application
      Name: !Sub '${Environment}-alb'
      Scheme: internet-facing
      Subnets:
        - !Ref PublicSubnetA
        - !Ref PublicSubnetB
      SecurityGroups:
        - !Ref LoadBalancerSecurityGroup

  LoadBalancerListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref LoadBalancer
      Port: 80
      Protocol: HTTP

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${Environment}-tg'
      Port: 8080
      Protocol: HTTP
      TargetType: ip
      VpcId: !Ref VPC

  # CloudWatch Logs
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/ecs/${Environment}'
      RetentionInDays: 7

Outputs:
  ServiceURL:
    Description: Service URL
    Value: !Sub 'http://${LoadBalancer.DNSName}'
  ClusterName:
    Description: ECS Cluster Name
    Value: !Ref ECSCluster
    Export:
      Name: !Sub '${AWS::StackName}-ClusterName'
  ServiceName:
    Description: ECS Service Name
    Value: !Ref ECSService
    Export:
      Name: !Sub '${AWS::StackName}-ServiceName'
```

## CloudFormation Stack Update from GitHub Actions

```yaml
- name: Deploy CloudFormation stack
  run: |
    aws cloudformation deploy \
      --template-file infrastructure/ecs-stack.yaml \
      --stack-name my-app-ecs \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides \
        Environment=production \
        DesiredCount=2 \
        CPU=256 \
        Memory=512 \
        ImageUrl=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

## Cross-Stack References

### Export Values from Base Stack

```yaml
Outputs:
  VPC:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPC'

  PublicSubnets:
    Description: Public subnets
    Value: !Join [',', !Ref PublicSubnetA, !Ref PublicSubnetB]
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnets'

  PrivateSubnets:
    Description: Private subnets
    Value: !Join [',', !Ref PrivateSubnetA, !Ref PrivateSubnetB]
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnets'
```

### Import Values in App Stack

```yaml
Parameters:
  VPC:
    Type: AWS::EC2::VPC::Id
  PrivateSubnets:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref PrivateSubnets
          VpcId: !Ref VPC
```
