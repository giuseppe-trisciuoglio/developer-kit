# AWS CloudFormation Deploy - Production Examples

Complete, production-ready examples for deploying ECS containers with GitHub Actions and CloudFormation.

## Table of Contents

- [Example 1: Basic ECS Deployment with OIDC](#example-1-basic-ecs-deployment-with-oidc)
- [Example 2: Multi-Environment Deployment](#example-2-multi-environment-deployment)
- [Example 3: Blue/Green Deployment with CodeDeploy](#example-3-bluegreen-deployment-with-codedeploy)
- [Example 4: Private ECR with Image Scanning](#example-4-private-ecr-with-image-scanning)
- [Example 5: CloudFormation Stack Update Workflow](#example-5-cloudformation-stack-update-workflow)
- [Example 6: Complete CI/CD Pipeline with Tests](#example-6-complete-cicd-pipeline-with-tests)

## Example 1: Basic ECS Deployment with OIDC

### CloudFormation Infrastructure Template

**infrastructure/ecs-basic.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Basic ECS Fargate deployment with GitHub Actions OIDC

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

  GitHubOrg:
    Type: String
    Description: GitHub organization name

  GitHubRepo:
    Type: String
    Description: GitHub repository name

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID for ECS resources

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: List of public subnet IDs for NAT

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: List of private subnet IDs for ECS tasks

  ImageUrl:
    Type: String
    Description: Docker image URL from ECR

  DesiredCount:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 10

Resources:
  # OIDC Provider for GitHub Actions
  GitHubOIDCProvider:
    Type: AWS::IAM::OIDCProvider
    Condition: HasOIDCProvider
    Properties:
      Url: https://token.actions.githubusercontent.com
      ClientIdList:
        - sts.amazonaws.com
      ThumbprintList:
        - a031c46782e6e6c662c2c87c76da9aa62ccabd8e

  # IAM Role for GitHub Actions
  GitHubActionsRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${Environment}-github-actions-ecs-role'
      Description: Role for GitHub Actions OIDC authentication
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Sub 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
            Action: sts:AssumeRoleWithWebIdentity
            Condition:
              StringEquals:
                token.actions.githubusercontent.com:aud: sts.amazonaws.com
              StringLike:
                token.actions.githubusercontent.com:sub: !Sub 'repo:${GitHubOrg}/${GitHubRepo}:*'
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonECS_FullAccess
        - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-cluster'
      ClusterSettings:
        - Name: containerInsights
          Value: enabled
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/ecs/${Environment}-app'
      RetentionInDays: 7

  # ECS Task Execution Role
  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${Environment}-ecs-task-execution-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  # ECS Task Role
  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${Environment}-ecs-task-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: TaskRolePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogStreams
                Resource: !GetAtt LogGroup.Arn

  # ECS Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub '${Environment}-app-task'
      Cpu: '256'
      Memory: '512'
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Ref ImageUrl
          Essential: true
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: LOG_LEVEL
              Value: INFO
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:8080/actuator/health || exit 1
            Interval: 30
            Timeout: 5
            Retries: 3
            StartPeriod: 60

  # Security Group for ECS Tasks
  ContainerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Sub 'Security group for ${Environment} ECS tasks'
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - Description: Allow HTTP from ALB
          IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref ALBSecurityGroup
      SecurityGroupEgress:
        - Description: Allow all outbound
          IpProtocol: -1
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # ALB Security Group
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Sub 'Security group for ${Environment} ALB'
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - Description: Allow HTTP from internet
          IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
      SecurityGroupEgress:
        - Description: Allow all outbound
          IpProtocol: -1
          CidrIp: 0.0.0.0/0

  # Application Load Balancer
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${Environment}-alb'
      Scheme: internet-facing
      Type: application
      Subnets: !Ref PublicSubnetIds
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # ALB Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${Environment}-tg'
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: ip
      HealthCheckConfig:
        Path: /actuator/health
        IntervalSeconds: 30
        TimeoutSeconds: 5
        HealthyThreshold: 2
        UnhealthyThreshold: 3
        Matcher:
          HttpCode: '200'

  # ALB Listener
  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref ALB
      Port: 80
      Protocol: HTTP

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    DependsOn: ALBListener
    Properties:
      ServiceName: !Sub '${Environment}-service'
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: !Ref DesiredCount
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref PrivateSubnetIds
          SecurityGroups:
            - !Ref ContainerSecurityGroup
          AssignPublicIp: DISABLED
      LoadBalancers:
        - ContainerName: app
          ContainerPort: 8080
          TargetGroupArn: !Ref TargetGroup
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 100
        DeploymentCircuitBreaker:
          Enable: true
          Rollback: true
      HealthCheckGracePeriodSeconds: 60
      EnableECSManagedTags: true
      PropagateTags: SERVICE
      Tags:
        - Key: Environment
          Value: !Ref Environment

Outputs:
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

  LoadBalancerURL:
    Description: Load Balancer URL
    Value: !Sub 'http://${ALB.DNSName}'
    Export:
      Name: !Sub '${AWS::StackName}-LoadBalancerURL'

  GitHubActionsRoleArn:
    Description: GitHub Actions Role ARN
    Value: !GetAtt GitHubActionsRole.Arn

Conditions:
  HasOIDCProvider: !Equals ['true', 'false']
```

### GitHub Actions Workflow

**.github/workflows/deploy-basic.yaml:**

```yaml
name: Deploy to ECS (Basic)

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app
  ECS_CLUSTER: dev-cluster
  ECS_SERVICE: dev-service
  ECS_TASK_DEFINITION: task-definition.json

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    name: Deploy to ECS
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/dev-github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Fill in the new image ID in the Amazon ECS task definition
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: render-task
        with:
          task-definition: ${{ env.ECS_TASK_DEFINITION }}
          container-name: app
          image: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}

      - name: Deploy Amazon ECS task definition
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.render-task.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
          deploy-timeout: 30 minutes

      - name: Deployment summary
        run: |
          echo "### Deployment Summary :rocket:" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Cluster:** ${{ env.ECS_CLUSTER }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Service:** ${{ env.ECS_SERVICE }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Image:** ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Commit:** ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
```

### Task Definition Template

**task-definition.json:**

```json
{
  "family": "dev-app-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/dev-ecs-task-execution-role",
  "taskRoleArn": "arn:aws:iam::123456789012:role/dev-ecs-task-role",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "PLACEHOLDER_IMAGE",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "dev"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dev-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8080/actuator/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

## Example 2: Multi-Environment Deployment

### Multi-Environment CloudFormation Template

**infrastructure/ecs-multi-env.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-environment ECS deployment

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

  ImageUrl:
    Type: String
    Description: Docker image URL

  DesiredCount:
    Type: Number
    Default: 2

Mappings:
  EnvironmentConfig:
    dev:
      CPU: '256'
      Memory: '512'
      DesiredCount: 1
      MinCapacity: 1
      MaxCapacity: 3
      EnableTerminationProtection: 'false'
      LogLevel: DEBUG
    staging:
      CPU: '512'
      Memory: '1024'
      DesiredCount: 2
      MinCapacity: 2
      MaxCapacity: 5
      EnableTerminationProtection: 'false'
      LogLevel: INFO
    prod:
      CPU: '1024'
      Memory: '2048'
      DesiredCount: 3
      MinCapacity: 3
      MaxCapacity: 10
      EnableTerminationProtection: 'true'
      LogLevel: WARN

Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-cluster'
      ClusterSettings:
        - Name: containerInsights
          Value: enabled

  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/ecs/${Environment}-app'
      RetentionInDays:
        !If [
          IsProd,
          30,
          !If [IsStaging, 14, 7]
        ]

  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub '${Environment}-app-task'
      Cpu: !FindInMap [EnvironmentConfig, !Ref Environment, CPU]
      Memory: !FindInMap [EnvironmentConfig, !Ref Environment, Memory]
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Ref ImageUrl
          Essential: true
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: LOG_LEVEL
              Value: !FindInMap [EnvironmentConfig, !Ref Environment, LogLevel]
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, MaxCapacity]
      MinCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, MinCapacity]
      ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
      RoleARN: !Sub 'arn:aws:iam::${AWS::AccountId}:role/aws-application-autoscaling-role'
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs

  ScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub '${Environment}-cpu-scaling'
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 70.0
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization

Conditions:
  IsProd: !Equals [!Ref Environment, prod]
  IsStaging: !Equals [!Ref Environment, staging]
```

### Multi-Environment GitHub Actions Workflow

**.github/workflows/deploy-multi-env.yaml:**

```yaml
name: Multi-Environment Deploy

on:
  push:
    branches:
      - main
      - staging
      - develop
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app

permissions:
  id-token: write
  contents: read

jobs:
  determine-environment:
    name: Determine environment
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
      role-arn: ${{ steps.set-env.outputs.role-arn }}
      cluster: ${{ steps.set-env.outputs.cluster }}
      service: ${{ steps.set-env.outputs.service }}
    steps:
      - name: Set environment
        id: set-env
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            ENV="${{ github.event.inputs.environment }}"
          else
            case "${{ github.ref }}" in
              refs/heads/main) ENV="prod" ;;
              refs/heads/staging) ENV="staging" ;;
              *) ENV="dev" ;;
            esac
          fi

          echo "environment=$ENV" >> $GITHUB_OUTPUT
          echo "role-arn=arn:aws:iam::123456789012:role/${ENV}-github-actions-ecs-role" >> $GITHUB_OUTPUT
          echo "cluster=${ENV}-cluster" >> $GITHUB_OUTPUT
          echo "service=${ENV}-service" >> $GITHUB_OUTPUT

  deploy:
    name: Deploy to ${{ needs.determine-environment.outputs.environment }}
    needs: determine-environment
    runs-on: ubuntu-latest
    environment:
      name: ${{ needs.determine-environment.outputs.environment }}
    timeout-minutes: 45

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ needs.determine-environment.outputs.role-arn }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ needs.determine-environment.outputs.environment }}
          build-args: |
            ENVIRONMENT=${{ needs.determine-environment.outputs.environment }}
            VERSION=${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Update CloudFormation stack
        run: |
          aws cloudformation deploy \
            --template-file infrastructure/ecs-multi-env.yaml \
            --stack-name my-app-${{ needs.determine-environment.outputs.environment }} \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides \
              Environment=${{ needs.determine-environment.outputs.environment }} \
              ImageUrl=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}

      - name: Wait for service stability
        run: |
          aws ecs wait services-stable \
            --cluster ${{ needs.determine-environment.outputs.cluster }} \
            --services ${{ needs.determine-environment.outputs.service }}

      - name: Get service URL
        id: service-url
        run: |
          STACK=my-app-${{ needs.determine-environment.outputs.environment }}
          URL=$(aws cloudformation describe-stacks \
            --stack-name $STACK \
            --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
            --output text)
          echo "url=$URL" >> $GITHUB_OUTPUT
          echo "Service URL: $URL"

      - name: Notify deployment
        if: always()
        run: |
          STATUS="${{ job.status }}"
          ENV="${{ needs.determine-environment.outputs.environment }}"
          URL="${{ steps.service-url.outputs.url }}"
          echo "Deployment to $ENV completed with status: $STATUS"
          echo "Service available at: $URL"
```

## Example 3: Blue/Green Deployment with CodeDeploy

### Blue/Green Infrastructure

**infrastructure/ecs-bluegreen.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: ECS Blue/Green deployment with CodeDeploy

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]

  ImageUrl:
    Type: String

  VpcId:
    Type: AWS::EC2::VPC::Id

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-bg-cluster'

  # Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/ecs/${Environment}-bg-app'
      RetentionInDays: 30

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub '${Environment}-bg-task'
      Cpu: '512'
      Memory: '1024'
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Ref ImageUrl
          Essential: true
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # Load Balancer
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${Environment}-bg-alb'
      Scheme: internet-facing
      Type: application
      Subnets: !Ref PublicSubnetIds
      SecurityGroups:
        - !Ref ALBSecurityGroup

  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: ALB security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # Target Groups
  BlueTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${Environment}-blue-tg'
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: ip
      HealthCheckConfig:
        Path: /actuator/health
        IntervalSeconds: 30
        TimeoutSeconds: 5

  GreenTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${Environment}-green-tg'
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      TargetType: ip
      HealthCheckConfig:
        Path: /actuator/health
        IntervalSeconds: 30
        TimeoutSeconds: 5

  # Test Listener
  TestListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref GreenTargetGroup
      LoadBalancerArn: !Ref LoadBalancer
      Port: 8080
      Protocol: HTTP

  # Production Listener
  ProductionListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref BlueTargetGroup
      LoadBalancerArn: !Ref LoadBalancer
      Port: 80
      Protocol: HTTP

  # CodeDeploy Application
  CodeDeployApplication:
    Type: AWS::CodeDeploy::Application
    Properties:
      ApplicationName: !Sub '${Environment}-bg-app'
      ComputePlatform: ECS

  # CodeDeploy Service Role
  CodeDeployServiceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codedeploy.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForECS

  # CloudWatch Alarms
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${Environment}-high-cpu-alarm'
      MetricName: CPUUtilization
      Namespace: AWS/ECS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold

  # CodeDeploy Deployment Group
  CodeDeployDeploymentGroup:
    Type: AWS::CodeDeploy::DeploymentGroup
    Properties:
      ApplicationName: !Ref CodeDeployApplication
      DeploymentGroupName: !Sub '${Environment}-bg-deployment-group'
      ServiceRoleArn: !GetAtt CodeDeployServiceRole.Arn
      DeploymentConfigName: CodeDeployDefault.ECSAllAtOnce
      DeploymentStyle:
        DeploymentType: BLUE_GREEN
        DeploymentOption: WITH_TRAFFIC_CONTROL
      AutoRollbackConfiguration:
        Enabled: true
        Events:
          - DEPLOYMENT_FAILURE
          - DEPLOYMENT_STOP_ON_ALARM
      AlarmConfiguration:
        Alarms:
          - !Ref CPUAlarm
        Enabled: true
      BlueGreenDeploymentConfiguration:
        TerminateBlueInstancesOnDeploymentSuccess:
          Action: TERMINATE
          WaitTimeInMinutes: 10
        DeploymentReadyOption:
          ActionOnTimeout: CONTINUE_DEPLOYMENT
      LoadBalancerInfo:
        TargetGroupPairInfoList:
          - TargetGroups:
              - Ref: BlueTargetGroup
              - Ref: GreenTargetGroup
            ProdTrafficRoute:
              ListenerArns:
                - !Ref ProductionListener
            TestTrafficRoute:
              ListenerArns:
                - !Ref TestListener

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    DependsOn: ProductionListener
    Properties:
      ServiceName: !Sub '${Environment}-bg-service'
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      DeploymentController:
        Type: CODE_DEPLOY
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref PrivateSubnetIds
          SecurityGroups:
            - !Ref ContainerSecurityGroup
          AssignPublicIp: DISABLED
      LoadBalancers:
        - ContainerName: app
          ContainerPort: 8080
          TargetGroupArn: !Ref BlueTargetGroup

  ContainerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Container security group
      VpcId: !Ref VpcId

Outputs:
  LoadBalancerURL:
    Description: Load Balancer URL
    Value: !Sub 'http://${LoadBalancer.DNSName}'
```

### Blue/Green GitHub Actions Workflow

**.github/workflows/deploy-bluegreen.yaml:**

```yaml
name: Blue/Green Deployment

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app
  CODEDEPLOY_APP: prod-bg-app
  CODEDEPLOY_GROUP: prod-bg-deployment-group

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    name: Blue/Green Deploy
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/prod-github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest

      - name: Render task definition
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: render-task
        with:
          task-definition: task-definition.json
          container-name: app
          image: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}

      - name: Create AppSpec file
        run: |
          cat > appspec.yaml <<EOF
          version: 0.0
          Resources:
            - TargetService:
                Type: AWS::ECS::Service
                Properties:
                  TaskDefinition: <TASK_DEFINITION>
                  LoadBalancerInfo:
                    ContainerName: app
                    ContainerPort: 8080
                  PlatformVersion: "1.4.0"
          EOF

      - name: Deploy to ECS (Blue/Green)
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.render-task.outputs.task-definition }}
          service: prod-bg-service
          cluster: prod-bg-cluster
          codedeploy-appspec: appspec.yaml
          codedeplay-application: ${{ env.CODEDEPLOY_APP }}
          codedeploy-deployment-group: ${{ env.CODEDEPLOY_GROUP }}
          wait-for-service-stability: true
          deploy-timeout: 45 minutes

      - name: Get deployment status
        id: deployment-status
        run: |
          STATUS=$(aws deploy list-deployments \
            --application-name ${{ env.CODEDEPLOY_APP }} \
            --deployment-group-name ${{ env.CODEDEPLOY_GROUP }} \
            --query 'deployments[0]' \
            --output text)

          aws deploy get-deployment \
            --deployment-id $STATUS \
            --query 'deploymentInfo.[status, statusMessage]' \
            --output table

          echo "deployment-id=$STATUS" >> $GITHUB_OUTPUT
```

**appspec.yaml:**

```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: app
          ContainerPort: 8080
        PlatformVersion: "1.4.0"
        NetworkConfiguration:
          AwsvpcConfiguration:
            Subnets:
              - subnet-12345678
              - subnet-87654321
            SecurityGroups:
              - sg-12345678
            AssignPublicIp: DISABLED
```

## Example 4: Private ECR with Image Scanning

### Private ECR Infrastructure

**infrastructure/ecr-private.yaml:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Private ECR with enhanced scanning

Parameters:
  RepositoryName:
    Type: String
    Default: my-app

Resources:
  # KMS Key for encryption
  EncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for ECR encryption
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
          - Sid: Allow ECR Service
            Effect: Allow
            Principal:
              Service: ecr.amazonaws.com
            Action:
              - kms:Decrypt
              - kms:DescribeKey
              - kms:Encrypt
              - kms:GenerateDataKey*
              - kms:ReEncrypt*
          - Sid: Allow CloudWatch Logs
            Effect: Allow
            Principal:
              Service: !Sub 'logs.${AWS::Region}.amazonaws.com'
            Action:
              - kms:Decrypt
              - kms:GenerateDataKey*

  # KMS Alias
  EncryptionKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub 'alias/ecr-${RepositoryName}'
      TargetKeyId: !Ref EncryptionKey

  # ECR Repository
  ECRRepository:
    Type: AWS::ECR::Repository
    Properties:
      RepositoryName: !Ref RepositoryName
      ImageScanningConfiguration:
        ScanOnPush: true
      ImageTagMutability: IMMUTABLE
      EncryptionConfiguration:
        EncryptionType: KMS
        KmsKey: !GetAtt EncryptionKey.Arn
      Tags:
        - Key: Environment
          Value: production

  # Lifecycle Policy
  LifecyclePolicy:
    Type: AWS::ECR::LifecyclePolicy
    Properties:
      RepositoryName: !Ref ECRRepository
      LifecyclePolicyText: !Sub |
        {
          "rules": [
            {
              "rulePriority": 1,
              "description": "Keep last 30 production images",
              "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["prod"],
                "countType": "imageCountMoreThan",
                "countNumber": 30
              },
              "action": {
                "type": "expire"
              }
            },
            {
              "rulePriority": 2,
              "description": "Keep last 10 staging images",
              "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["staging"],
                "countType": "imageCountMoreThan",
                "countNumber": 10
              },
              "action": {
                "type": "expire"
              }
            },
            {
              "rulePriority": 3,
              "description": "Keep last 5 dev images",
              "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["dev"],
                "countType": "imageCountMoreThan",
                "countNumber": 5
              },
              "action": {
                "type": "expire"
              }
            },
            {
              "rulePriority": 4,
              "description": "Expire untagged images after 1 day",
              "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": 1
              },
              "action": {
                "type": "expire"
              }
            }
          ]
        }

  # Repository Policy (optional - for cross-account access)
  RepositoryPolicy:
    Type: AWS::ECR::RepositoryPolicy
    Properties:
      RepositoryName: !Ref ECRRepository
      PolicyText: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AllowPullFromECS",
              "Effect": "Allow",
              "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
              },
              "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability"
              ]
            }
          ]
        }

  # CloudWatch Event for image scan findings
  ScanFindingsEventRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub '${RepositoryName}-scan-findings'
      Description: Trigger on ECR image scan findings
      EventPattern:
        source:
          - aws.ecr
        detail-type:
          - ECR Image Scan
        detail:
          scan-status:
            - COMPLETE
          finding-severity:
            - HIGH
            - CRITICAL
      State: ENABLED
      Targets:
        - Arn: !Sub 'arn:aws:sns:${AWS::Region}:${AWS::AccountId}:security-alerts'
          Id: SecurityAlerts

  # SNS Topic for security alerts
  SecurityAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: security-alerts
      DisplayName: Security Alerts

Outputs:
  RepositoryURI:
    Description: ECR Repository URI
    Value: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${RepositoryName}'
    Export:
      Name: !Sub '${AWS::StackName}-RepositoryURI'

  RepositoryName:
    Description: ECR Repository Name
    Value: !Ref RepositoryName
    Export:
      Name: !Sub '${AWS::StackName}-RepositoryName'

  EncryptionKeyArn:
    Description: KMS Key ARN
    Value: !GetAtt EncryptionKey.Arn
```

### ECR Deployment Workflow with Scanning

**.github/workflows/deploy-ecr-scanning.yaml:**

```yaml
name: Deploy with ECR Scanning

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app

permissions:
  id-token: write
  contents: read

jobs:
  build-and-push:
    name: Build and Push to ECR
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecr-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}
          tags: |
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VERSION=${{ github.sha }}

      - name: Trigger ECR scan
        run: |
          IMAGE_TAG=$(echo ${{ steps.meta.outputs.tags }} | awk '{print $1}')
          aws ecr start-image-scan \
            --repository-name ${{ env.ECR_REPOSITORY }} \
            --image-id imageTag=$(echo $IMAGE_TAG | cut -d: -f2)

      - name: Wait for scan to complete
        run: |
          IMAGE_TAG=$(echo ${{ steps.meta.outputs.tags }} | awk '{print $1}')
          aws ecr wait image-scan-complete \
            --repository-name ${{ env.ECR_REPOSITORY }} \
            --image-id imageTag=$(echo $IMAGE_TAG | cut -d: -f2)

      - name: Get scan results
        id: scan-results
        run: |
          IMAGE_TAG=$(echo ${{ steps.meta.outputs.tags }} | awk '{print $1}')
          SCAN_RESULTS=$(aws ecr describe-image-scan-findings \
            --repository-name ${{ env.ECR_REPOSITORY }} \
            --image-id imageTag=$(echo $IMAGE_TAG | cut -d: -f2) \
            --query 'imageScanFindings.findingSeverityCounts' \
            --output json)

          echo "results=$SCAN_RESULTS" >> $GITHUB_OUTPUT

          # Check for critical vulnerabilities
          CRITICAL=$(echo $SCAN_RESULTS | jq -r '.CRITICAL // 0')
          HIGH=$(echo $SCAN_RESULTS | jq -r '.HIGH // 0')

          if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
            echo "::warning::Security vulnerabilities found: $SCAN_RESULTS"
            echo "CRITICAL=$CRITICAL" >> $GITHUB_OUTPUT
            echo "HIGH=$HIGH" >> $GITHUB_OUTPUT
          else
            echo "No critical vulnerabilities found"
          fi

      - name: Upload scan results
        uses: actions/upload-artifact@v4
        with:
          name: scan-results
          path: |
            scan-results.json

  deploy-to-ecs:
    name: Deploy to ECS
    needs: build-and-push
    runs-on: ubuntu-latest
    # Only deploy if no critical vulnerabilities
    if: needs.build-and-push.outputs.CRITICAL == '0' || needs.build-and-push.outputs.CRITICAL == ''
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Render task definition
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: render-task
        with:
          task-definition: task-definition.json
          container-name: app
          image: ${{ needs.build-and-push.outputs.image-tag }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.render-task.outputs.task-definition }}
          service: my-service
          cluster: my-cluster
          wait-for-service-stability: true

  security-failure:
    name: Security Failure
    needs: build-and-push
    runs-on: ubuntu-latest
    # Run if critical vulnerabilities found
    if: needs.build-and-push.outputs.CRITICAL != '0' && needs.build-and-push.outputs.CRITICAL != ''
    steps:
      - name: Fail on security vulnerabilities
        run: |
          echo "::error::Critical or high severity vulnerabilities found in image scan"
          echo "Deployment blocked due to security findings"
          exit 1
```

## Example 5: CloudFormation Stack Update Workflow

### Stack Update Workflow

**.github/workflows/deploy-cloudformation.yaml:**

```yaml
name: CloudFormation Stack Deploy

on:
  push:
    branches:
      - main
      - staging
    paths:
      - 'infrastructure/**'
      - 'Dockerfile'
  workflow_dispatch:
    inputs:
      stack-name:
        description: 'CloudFormation stack name'
        required: true
        type: string
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app

permissions:
  id-token: write
  contents: read

jobs:
  validate-templates:
    name: Validate CloudFormation Templates
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/cloudformation-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Validate CloudFormation templates
        run: |
          for template in infrastructure/**/*.yaml; do
            echo "Validating $template"
            aws cloudformation validate-template \
              --template-body file://$template
          done

      - name: Check CloudFormation syntax
        run: |
          pip install cfn-lint
          cfn-lint infrastructure/**/*.yaml

  deploy-stack:
    name: Deploy CloudFormation Stack
    needs: validate-templates
    runs-on: ubuntu-latest
    outputs:
      stack-name: ${{ steps.deploy.outputs.stack-name }}
      load-balancer-url: ${{ steps.outputs.outputs.url }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/cloudformation-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest

      - name: Determine stack name and environment
        id: config
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            ENV="${{ github.event.inputs.environment }}"
            STACK="${{ github.event.inputs.stack-name }}"
          else
            case "${{ github.ref }}" in
              refs/heads/main)
                ENV="prod"
                STACK="my-app-prod"
                ;;
              refs/heads/staging)
                ENV="staging"
                STACK="my-app-staging"
                ;;
              *)
                ENV="dev"
                STACK="my-app-dev"
                ;;
            esac
          fi

          echo "environment=$ENV" >> $GITHUB_OUTPUT
          echo "stack-name=$STACK" >> $GITHUB_OUTPUT

      - name: Deploy CloudFormation stack
        id: deploy
        run: |
          IMAGE_URL="${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}"

          # Check if stack exists
          if aws cloudformation describe-stacks \
            --stack-name ${{ steps.config.outputs.stack-name }} \
            --region ${{ env.AWS_REGION }} 2>/dev/null; then
            ACTION="UPDATE"
          else
            ACTION="CREATE"
          fi

          echo "Action: $ACTION"

          # Deploy or create stack
          aws cloudformation deploy \
            --template-file infrastructure/ecs-stack.yaml \
            --stack-name ${{ steps.config.outputs.stack-name }} \
            --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
            --no-fail-on-empty-changeset \
            --parameter-overrides \
              Environment=${{ steps.config.outputs.environment }} \
              ImageUrl=$IMAGE_URL \
              DesiredCount=2 \
              CPU=512 \
              Memory=1024 \
            --tags \
              Environment=${{ steps.config.outputs.environment }} \
              Project=my-app \
              ManagedBy=GitHubActions \
              Commit=${{ github.sha }} \
              Branch=${{ github.ref_name }}

          echo "stack-name=${{ steps.config.outputs.stack-name }}" >> $GITHUB_OUTPUT

      - name: Wait for stack operations
        run: |
          aws cloudformation wait stack-${{ steps.deploy.outputs.action == 'CREATE' && 'create' || 'update' }}-complete \
            --stack-name ${{ steps.config.outputs.stack-name }} \
            --region ${{ env.AWS_REGION }}

      - name: Get stack outputs
        id: outputs
        run: |
          URL=$(aws cloudformation describe-stacks \
            --stack-name ${{ steps.config.outputs.stack-name }} \
            --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
            --output text)

          echo "url=$URL" >> $GITHUB_OUTPUT
          echo "Load Balancer URL: $URL"

      - name: Describe stack events
        if: failure()
        run: |
          aws cloudformation describe-stack-events \
            --stack-name ${{ steps.config.outputs.stack-name }} \
            --query 'sort_by(StackEvents, &Timestamp)[*].[ResourceType,ResourceStatus,ResourceStatusReason]' \
            --output table

  rollback-on-failure:
    name: Rollback on Failure
    needs: deploy-stack
    runs-on: ubuntu-latest
    if: failure()
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/cloudformation-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Check stack status
        run: |
          STATUS=$(aws cloudformation describe-stacks \
            --stack-name ${{ needs.deploy-stack.outputs.stack-name }} \
            --query 'Stacks[0].StackStatus' \
            --output text)

          echo "Stack status: $STATUS"

          if [[ $STATUS == *"ROLLBACK_COMPLETE"* ]] || [[ $STATUS == *"UPDATE_ROLLBACK_COMPLETE"* ]]; then
            echo "Stack rolled back successfully"
          fi

      - name: Notify team
        run: |
          echo "::error::CloudFormation stack deployment failed for ${{ needs.deploy-stack.outputs.stack-name }}"
          echo "Stack has been rolled back to previous stable state"

  detect-drift:
    name: Detect Configuration Drift
    needs: deploy-stack
    runs-on: ubuntu-latest
    if: success()
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/cloudformation-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Initiate drift detection
        run: |
          DETECTION_ID=$(aws cloudformation detect-stack-drift \
            --stack-name ${{ needs.deploy-stack.outputs.stack-name }} \
            --query 'DriftDetectionId' \
            --output text)

          echo "Drift detection initiated: $DETECTION_ID"

      - name: Wait for drift detection
        run: |
          aws cloudformation wait stack-drift-detection-complete \
            --stack-name ${{ needs.deploy-stack.outputs.stack-name }}

      - name: Check drift results
        run: |
          RESULTS=$(aws cloudformation describe-stack-drift-detection-status \
            --stack-name ${{ needs.deploy-stack.outputs.stack-name }} \
            --drift-detection-id $(aws cloudformation describe-stack-resource-drifts \
              --stack-name ${{ needs.deploy-stack.outputs.stack-name }} \
              --query 'Drifts[0].StackResourceDriftId' \
              --output text))

          DRIFT_STATUS=$(echo $RESULTS | jq -r '.DetectionStatus')
          echo "Drift status: $DRIFT_STATUS"

          if [ "$DRIFT_STATUS" != "DRIFTED" ]; then
            echo "No configuration drift detected"
          else
            echo "::warning::Configuration drift detected in stack"
          fi
```

## Example 6: Complete CI/CD Pipeline with Tests

### Full Pipeline Workflow

**.github/workflows/ci-cd-pipeline.yaml:**

```yaml
name: Complete CI/CD Pipeline

on:
  push:
    branches:
      - '**'
  pull_request:
    branches:
      - main
      - staging

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app
  JAVA_VERSION: '21'
  NODE_VERSION: '20'

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  code-quality:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}
          cache: 'maven'

      - name: Run Checkstyle
        run: mvn checkstyle:check

      - name: Run SpotBugs
        run: mvn spotbugs:check

      - name: Run PMD
        run: mvn pmd:check

  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}
          cache: 'maven'

      - name: Run unit tests
        run: mvn clean test -DskipITs=true

      - name: Generate test report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Unit Test Results
          path: target/surefire-reports/*.xml
          reporter: java-junit
          fail-on-error: true

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: unit-test-results
          path: target/surefire-reports/

      - name: Upload coverage reports
        uses: codecov/codecov-action@v4
        with:
          files: target/site/jacoco/jacoco.xml
          flags: unittests
          name: codecov-umbrella

  integration-tests:
    name: Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}
          cache: 'maven'

      - name: Run integration tests
        run: mvn verify -DskipUnitTests=true
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/testdb
          SPRING_DATASOURCE_USERNAME: testuser
          SPRING_DATASOURCE_PASSWORD: testpass
          SPRING_REDIS_HOST: localhost
          SPRING_REDIS_PORT: 6379

      - name: Generate integration test report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Integration Test Results
          path: target/failsafe-reports/*.xml
          reporter: java-junit
          fail-on-error: true

  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run OWASP dependency check
        run: |
          mvn org.owasp:dependency-check-maven:check

      - name: Run Snyk security scan
        uses: snyk/actions/maven@0.4.0
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  build-docker:
    name: Build Docker Image
    needs: [code-quality, unit-tests, integration-tests]
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecr-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}
          tags: |
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
            type=semver,pattern={{version}}
          labels: |
            org.opencontainers.image.title=My Application
            org.opencontainers.image.description=Production-ready application
            org.opencontainers.image.vendor=My Company

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VERSION=${{ github.sha }}
            COMMIT=${{ github.sha }}

      - name: Scan Docker image
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ steps.meta.outputs.version }}
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

  deploy-dev:
    name: Deploy to Development
    needs: build-docker
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: development
      url: http://dev-my-app.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/dev-github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Update CloudFormation stack
        run: |
          aws cloudformation deploy \
            --template-file infrastructure/ecs-stack.yaml \
            --stack-name my-app-dev \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides \
              Environment=dev \
              ImageUrl=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ needs.build-docker.outputs.image-tag }}

      - name: Smoke tests
        run: |
          # Run smoke tests against dev environment
          curl -f http://dev-my-app.example.com/actuator/health || exit 1

  deploy-staging:
    name: Deploy to Staging
    needs: build-docker
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: http://staging-my-app.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/staging-github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Update CloudFormation stack
        run: |
          aws cloudformation deploy \
            --template-file infrastructure/ecs-stack.yaml \
            --stack-name my-app-staging \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides \
              Environment=staging \
              ImageUrl=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ needs.build-docker.outputs.image-tag }}

      - name: Run integration tests
        run: |
          # Run integration tests against staging
          mvn verify -Dtest.environment=staging

  deploy-production:
    name: Deploy to Production
    needs: [build-docker, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://my-app.example.com
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/prod-github-actions-ecs-role
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Create CloudFormation change set
        run: |
          aws cloudformation create-change-set \
            --stack-name my-app-prod \
            --change-set-name prod-changeset-${{ github.sha }} \
            --template-body file://infrastructure/ecs-stack.yaml \
            --parameters \
              ParameterKey=Environment,ParameterValue=prod \
              ParameterKey=ImageUrl,ParameterValue=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ needs.build-docker.outputs.image-tag }} \
            --capabilities CAPABILITY_NAMED_IAM \
            --change-set-type UPDATE

      - name: Wait for change set creation
        run: |
          aws cloudformation wait change-set-create-complete \
            --stack-name my-app-prod \
            --change-set-name prod-changeset-${{ github.sha }}

      - name: Describe change set
        run: |
          aws cloudformation describe-change-set \
            --stack-name my-app-prod \
            --change-set-name prod-changeset-${{ github.sha }}

      - name: Request approval
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GITHUB_TOKEN }}
          approvers: devops-team,platform-team
          minimum-approvals: 2
          timeout-minutes: 30

      - name: Execute change set
        run: |
          aws cloudformation execute-change-set \
            --stack-name my-app-prod \
            --change-set-name prod-changeset-${{ github.sha }}

      - name: Wait for stack update
        run: |
          aws cloudformation wait stack-update-complete \
            --stack-name my-app-prod

      - name: Run smoke tests
        run: |
          # Run smoke tests against production
          curl -f https://my-app.example.com/actuator/health || exit 1

      - name: Run load tests
        run: |
          # Run load tests
          k6 run tests/load/production.js

      - name: Notify on success
        if: success()
        run: |
          echo "Production deployment successful"

      - name: Rollback on failure
        if: failure()
        run: |
          echo "::error::Production deployment failed, initiating rollback"
          aws cloudformation rollback-stack \
            --stack-name my-app-prod \
            --role-arn arn:aws:iam::123456789012:role/cloudformation-rollback-role

  post-deployment:
    name: Post-Deployment Tests
    needs: [deploy-production]
    if: always() && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run end-to-end tests
        run: |
          # Run E2E tests
          mvn verify -P e2e -Dtest.environment=production

      - name: Verify metrics
        run: |
          # Verify CloudWatch metrics
          aws cloudwatch get-metric-statistics \
            --namespace AWS/ECS \
            --metric-name CPUUtilization \
            --dimensions Name=ServiceName,Value=my-service \
            --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
            --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
            --period 300 \
            --statistics Average

      - name: Check CloudWatch alarms
        run: |
          # Check for any alarms in ALARM state
          aws cloudwatch describe-alarms \
            --alarm-names my-app-prod-* \
            --query 'MetricAlarms[?StateValue==`ALARM`].AlarmName' \
            --output table

      - name: Generate deployment report
        run: |
          cat > deployment-report.md <<EOF
          # Deployment Report

          **Commit:** ${{ github.sha }}
          **Branch:** ${{ github.ref_name }}
          **Deployed at:** $(date)
          **Image:** ${{ needs.deploy-production.outputs.image-tag }}
          EOF

          cat deployment-report.md

      - name: Upload deployment report
        uses: actions/upload-artifact@v4
        with:
          name: deployment-report
          path: deployment-report.md

  notify:
    name: Notify Team
    needs: [post-deployment]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Deployment completed for ${{ github.ref_name }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Deployment to *${{ github.ref_name }}* completed with status: *${{ job.status }}*"
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {
                      "type": "mrkdwn",
                      "text": "*Commit:* ${{ github.sha }}"
                    },
                    {
                      "type": "mrkdwn",
                      "text": "*Author:* ${{ github.actor }}"
                    }
                  ]
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

These production-ready examples demonstrate comprehensive patterns for deploying ECS containers with GitHub Actions and CloudFormation, covering various deployment strategies, security considerations, and testing approaches.
