# AWS CloudFormation Deploy - Technical Reference

Comprehensive technical reference for deploying ECS containers with GitHub Actions and CloudFormation.

## Table of Contents

- [GitHub Actions Workflow Syntax](#github-actions-workflow-syntax)
- [AWS OIDC Trust Policy Configuration](#aws-oidc-trust-policy-configuration)
- [ECR Repository Configuration](#ecr-repository-configuration)
- [Task Definition Structure](#task-definition-structure)
- [ECS Service Update Parameters](#ecs-service-update-parameters)
- [CloudFormation Stack Updates](#cloudformation-stack-updates)
- [Security Considerations](#security-considerations)
- [Environment Configurations](#environment-configurations)
- [Monitoring and Logging](#monitoring-and-logging)

## GitHub Actions Workflow Syntax

### Workflow File Structure

GitHub Actions workflows are defined in YAML files in `.github/workflows/`:

```yaml
name: Workflow Name                    # Human-readable name
on:                                    # Triggers for workflow
  push:                                # Run on git push
    branches: [main, develop]          # Specific branches
    paths:                             # Specific file paths
      - 'src/**'
      - 'Dockerfile'
  pull_request:                        # Run on pull requests
  schedule:                            # Cron-based triggers
    - cron: '0 0 * * *'
  workflow_dispatch:                   # Manual trigger
  release:                             # Run on release
    types: [created]

env:                                   # Environment variables available to all jobs
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app

permissions:                           # Workflow-level permissions
  id-token: write                      # Required for OIDC
  contents: read                       # Required for checkout
  pull-requests: write                 # For PR comments

jobs:                                  # Job definitions
  job-name:
    runs-on: ubuntu-latest             # Runner type
    timeout-minutes: 30                # Job timeout
    permissions:                       # Job-specific permissions (overrides workflow-level)
      id-token: write
    steps:                             # Step sequence
      - name: Step name
        uses: action@v1                # Use an action
      - name: Run command
        run: |                         # Run shell commands
          echo "Command"
```

### Workflow Triggers

**Push-based triggers:**

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'                  # Wildcard matching
    tags:
      - 'v*.*.*'                      # Semantic versioning
    paths:
      - 'src/**'
      - 'Dockerfile'
      - '.github/workflows/deploy.yml'
```

**Pull request triggers:**

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - develop
```

**Manual trigger with inputs:**

```yaml
on:
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
      version:
        description: 'Image version tag'
        required: false
        default: 'latest'
```

**Scheduled triggers:**

```yaml
on:
  schedule:
    - cron: '0 2 * * *'               # Daily at 2 AM UTC
    - cron: '0 0 * * 0'               # Weekly on Sunday
```

### Job Dependencies and Matrix Builds

**Sequential jobs:**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  build:
    needs: test                       # Requires test job to complete
    runs-on: ubuntu-latest
    steps:
      - run: docker build
```

**Parallel matrix builds:**

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        environment: [dev, staging, prod]
        region: [us-east-1, eu-west-1]
        include:
          - environment: prod
            region: us-east-1
            timeout: 60
        exclude:
          - environment: prod
            region: eu-west-1
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Deploy to ${{ matrix.environment }} in ${{ matrix.region }}"
```

**Conditional execution:**

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Only runs on main branch push"
```

### Step Syntax and Features

**Using actions:**

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
    with:
      fetch-depth: 0                  # Full git history
      token: ${{ secrets.GITHUB_TOKEN }}
      sparse-checkout: |
        src/
        Dockerfile

  - name: Configure AWS
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/my-role
      aws-region: us-east-1
      mask-aws-account-id: true       # Hide account ID in logs
```

**Running shell commands:**

```yaml
steps:
  - name: Build and push
    run: |
      echo "Building Docker image..."
      docker build -t my-app:${{ github.sha }} .
      docker push my-app:${{ github.sha }}
    shell: bash                       # Optional: bash, pwsh, python, etc.

  - name: Multi-line script
    run: |
      set -x                          # Debug mode
      aws ecr describe-repositories \
        --repository-names my-app \
        --region $AWS_REGION
```

**Working with outputs:**

```yaml
steps:
  - id: login-ecr
    name: Login to ECR
    uses: aws-actions/amazon-ecr-login@v2

  - name: Use output
    run: |
      echo "Registry: ${{ steps.login-ecr.outputs.registry }}"
      echo "Using registry URL in next step..."
```

**Conditional steps:**

```yaml
steps:
  - name: Deploy to production
    if: github.ref == 'refs/heads/main'
    run: |
      echo "Deploying to production"

  - name: Deploy to staging
    if: github.ref == 'refs/heads/staging'
    run: |
      echo "Deploying to staging"
```

### Environment Variables and Secrets

**Setting environment variables:**

```yaml
env:
  GLOBAL_VAR: value
jobs:
  job1:
    env:
      JOB_VAR: value
    steps:
      - env:
          STEP_VAR: value
        run: |
          echo "$GLOBAL_VAR $JOB_VAR $STEP_VAR"
```

**Using secrets:**

```yaml
steps:
  - name: Use secret
    env:
      SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
    run: |
      curl -X POST $SLACK_WEBHOOK -d "Deployment complete"
```

**Passing outputs between jobs:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.build.outputs.tag }}
    steps:
      - id: build
        run: echo "tag=${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Using image tag: ${{ needs.build.outputs.image-tag }}"
```

## AWS OIDC Trust Policy Configuration

### OIDC Provider Setup

**Create OIDC provider in AWS IAM:**

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
```

**Or via CloudFormation:**

```yaml
GitHubOIDCProvider:
  Type: AWS::IAM::OIDCProvider
  Properties:
    Url: https://token.actions.githubusercontent.com
    ClientIdList:
      - sts.amazonaws.com
    ThumbprintList:
      - a031c46782e6e6c662c2c87c76da9aa62ccabd8e
```

### IAM Role with OIDC Trust Policy

**Basic OIDC trust policy:**

```yaml
GitHubActionsRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: github-actions-ecs-role
    Description: Role for GitHub Actions to deploy ECS
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
```

**Repository-scoped trust policy:**

```yaml
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
          token.actions.githubusercontent.com:sub: repo:my-org/my-repo:ref:refs/heads/main
```

**Environment-based trust policy:**

```yaml
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
          token.actions.githubusercontent.com:sub:
            - repo:my-org/my-repo:ref:refs/heads/main
            - repo:my-org/my-repo:ref:refs/heads/production
```

**Multi-repository trust policy:**

```yaml
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
          token.actions.githubusercontent.com:sub:
            - repo:my-org/*:ref:refs/heads/main
            - repo:my-org/*:ref:refs/heads/production
```

### Role Permissions for ECS Deployment

**ECS-specific permissions:**

```yaml
ECSDeployPolicy:
  Type: AWS::IAM::Policy
  Properties:
    PolicyName: ECSDeployPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - ecs:DescribeServices
            - ecs:DescribeTaskDefinition
            - ecs:DescribeTasks
            - ecs:ListTasks
            - ecs:ListServices
            - ecs:ListClusters
            - ecs:RegisterTaskDefinition
            - ecs:UpdateService
            - ecs:CreateService
            - ecs:DeleteService
            - ecs:UpdateServicePrimaryTaskSet
            - ecs:CreateTaskSet
          Resource:
            - !Sub 'arn:aws:ecs:${AWS::Region}:${AWS::AccountId}:*'
```

**ECR-specific permissions:**

```yaml
ECRPushPolicy:
  Type: AWS::IAM::Policy
  Properties:
    PolicyName: ECRPushPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - ecr:GetAuthorizationToken
          Resource: '*'
        - Effect: Allow
          Action:
            - ecr:BatchCheckLayerAvailability
            - ecr:GetDownloadUrlForLayer
            - ecr:GetRepositoryPolicy
            - ecr:DescribeRepositories
            - ecr:ListImages
            - ecr:DescribeImages
            - ecr:BatchGetImage
            - ecr:InitiateLayerUpload
            - ecr:UploadLayerPart
            - ecr:CompleteLayerUpload
            - ecr:PutImage
            - ecr:SetRepositoryPolicy
          Resource:
            - !Sub 'arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/my-app'
```

**CloudFormation permissions:**

```yaml
CloudFormationDeployPolicy:
  Type: AWS::IAM::Policy
  Properties:
    PolicyName: CloudFormationDeployPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - cloudformation:DescribeStacks
            - cloudformation:DescribeStackEvents
            - cloudformation:DescribeStackResource
            - cloudformation:CreateStack
            - cloudformation:UpdateStack
            - cloudformation:DeleteStack
            - cloudformation:ListStacks
            - cloudformation:GetTemplate
            - cloudformation:ValidateTemplate
          Resource:
            - !Sub 'arn:aws:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/my-app-*'
        - Effect: Allow
          Action:
            - iam:PassRole
          Resource:
            - !Sub 'arn:aws:iam::${AWS::AccountId}:role/ecsTaskExecutionRole'
            - !Sub 'arn:aws:iam::${AWS::AccountId}:role/ecsTaskRole'
          Condition:
            StringEquals:
              iam:PassedToService: ecs-tasks.amazonaws.com
```

**Secrets Manager permissions:**

```yaml
SecretsAccessPolicy:
  Type: AWS::IAM::Policy
  Properties:
    PolicyName: SecretsAccessPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
            - secretsmanager:DescribeSecret
          Resource:
            - !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-app/*'
```

### Session Tags and Transitive Keys

**Enable session tags for cross-account access:**

```yaml
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
          token.actions.githubusercontent.com:sub: repo:my-org/my-repo:*
        ForAllValues:StringEquals:
          aws:PrincipalTag/JobBranch: [main, production]
```

**Configure session tags in GitHub Actions:**

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecs-role
    aws-region: us-east-1
    audience: sts.amazonaws.com
```

## ECR Repository Configuration

### Basic ECR Repository

```yaml
ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    ImageScanningConfiguration:
      ScanOnPush: true
    ImageTagMutability: IMMUTABLE
    EncryptionConfiguration:
      EncryptionType: KMS
      KmsKey: !GetAtt KMSKey.Arn
```

### Lifecycle Policy

**Keep last N tagged images:**

```yaml
LifecyclePolicy:
  Type: AWS::ECR::LifecyclePolicy
  Properties:
    RepositoryName: !Ref ECRRepository
    LifecyclePolicyText: |
      {
        "rules": [
          {
            "rulePriority": 1,
            "description": "Keep last 30 tagged images",
            "selection": {
              "tagStatus": "tagged",
              "tagPrefixList": ["v"],
              "countType": "imageCountMoreThan",
              "countNumber": 30
            },
            "action": {
              "type": "expire"
            }
          }
        ]
      }
```

**Clean up untagged images:**

```yaml
LifecyclePolicy:
  Type: AWS::ECR::LifecyclePolicy
  Properties:
    RepositoryName: !Ref ECRRepository
    LifecyclePolicyText: |
      {
        "rules": [
          {
            "rulePriority": 1,
            "description": "Expire untagged images older than 7 days",
            "selection": {
              "tagStatus": "untagged",
              "countType": "sinceImagePushed",
              "countUnit": "days",
              "countNumber": 7
            },
            "action": {
              "type": "expire"
            }
          }
        ]
      }
```

**Multiple lifecycle rules:**

```yaml
LifecyclePolicy:
  Type: AWS::ECR::LifecyclePolicy
  Properties:
    RepositoryName: !Ref ECRRepository
    LifecyclePolicyText: |
      {
        "rules": [
          {
            "rulePriority": 1,
            "description": "Keep production tagged images",
            "selection": {
              "tagStatus": "tagged",
              "tagPrefixList": ["prod"],
              "countType": "imageCountMoreThan",
              "countNumber": 10
            },
            "action": {
              "type": "expire"
            }
          },
          {
            "rulePriority": 2,
            "description": "Keep last 30 development images",
            "selection": {
              "tagStatus": "tagged",
              "tagPrefixList": ["dev", "staging"],
              "countType": "imageCountMoreThan",
              "countNumber": 30
            },
            "action": {
              "type": "expire"
            }
          },
          {
            "rulePriority": 3,
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
```

### Repository Policy

**Cross-account access:**

```yaml
RepositoryPolicy:
  Type: AWS::ECR::RepositoryPolicy
  Properties:
    RepositoryName: !Ref ECRRepository
    PolicyText: |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "AllowCrossAccountPull",
            "Effect": "Allow",
            "Principal": {
              "AWS": [
                "arn:aws:iam::111111111111:root",
                "arn:aws:iam::222222222222:root"
              ]
            },
            "Action": [
              "ecr:GetDownloadUrlForLayer",
              "ecr:BatchGetImage",
              "ecr:BatchCheckLayerAvailability"
            ]
          }
        ]
      }
```

**Pull-only access for specific IAM role:**

```yaml
RepositoryPolicy:
  Type: AWS::ECR::RepositoryPolicy
  Properties:
    RepositoryName: !Ref ECRRepository
    PolicyText: |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "AllowECSPull",
            "Effect": "Allow",
            "Principal": {
              "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": [
              "ecr:GetDownloadUrlForLayer",
              "ecr:BatchGetImage",
              "ecr:BatchCheckLayerAvailability"
            ],
            "Condition": {
              "ArnLike": {
                "aws:SourceArn": "arn:aws:ecs:us-east-1:123456789012:task-definition/*"
              }
            }
          }
        ]
      }
```

### ECR Registry Scanning Configuration

**Basic scan on push:**

```yaml
ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    ImageScanningConfiguration:
      ScanOnPush: true
```

**Enhanced scanning with continuous monitoring:**

```yaml
# First create an inspector scanner
InspectorScanner:
  Type: AWS::InspectorV2::Filter
  Properties:
    Name: ECRScanFilter
    FilterCriteria:
      -
    # Configure scanning rules

ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    ImageScanningConfiguration:
      ScanOnPush: true
    ImageTagMutability: IMMUTABLE
```

### ECR Event Notifications

**CloudWatch Events for image push:**

```yaml
ImagePushEventRule:
  Type: AWS::Events::Rule
  Properties:
    Name: ECRImagePush
    Description: Trigger on image push
    EventPattern:
      source:
        - aws.ecr
      detail-type:
        - ECR Image Action
      detail:
        action-type:
          - PUSH
    State: ENABLED
    Targets:
      - Arn: !GetAtt LambdaFunction.Arn
        Id: ECRPushTarget

# Lambda function to trigger deployment
LambdaPermission:
  Type: AWS::Lambda::Permission
  Properties:
    FunctionName: !Ref LambdaFunction
    Action: lambda:InvokeFunction
    Principal: events.amazonaws.com
    SourceArn: !GetAtt ImagePushEventRule.Arn
```

## Task Definition Structure

### Basic Fargate Task Definition

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: my-app-task
    Cpu: '256'
    Memory: '512'
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
    TaskRoleArn: !GetAtt TaskRole.Arn
    ContainerDefinitions:
      - Name: my-app
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
        Secrets:
          - Name: DB_PASSWORD
            ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-app/db-password'
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: ecs
            awslogs-create-group: 'true'
        HealthCheck:
          Command:
            - CMD-SHELL
            - curl -f http://localhost:8080/actuator/health || exit 1
          Interval: 30
          Timeout: 5
          Retries: 3
          StartPeriod: 60
        DockerLabels:
          com.mycompany.label: value
        ReadonlyRootFilesystem: false
        Ulimits:
          - Name: nofile
            SoftLimit: 65536
            HardLimit: 65536
```

### Multi-Container Task Definition

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: multi-container-app
    Cpu: '512'
    Memory: '1024'
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
    ContainerDefinitions:
      # Application container
      - Name: app
        Image: !Ref AppImageUrl
        Essential: true
        PortMappings:
          - ContainerPort: 8080
            Protocol: tcp
        Environment:
          - Name: DATABASE_HOST
            Value: localhost
          - Name: DATABASE_PORT
            Value: '5432'
        DependsOn:
          - ContainerName: database
            Condition: START
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: app

      # Sidecar container (e.g., log collector)
      - Name: log-collector
        Image: !Ref LogCollectorImageUrl
        Essential: false
        Environment:
          - Name: LOG_PATH
            Value: /var/log/app
        MountPoints:
          - SourceVolume: app-logs
            ContainerPath: /var/log/app
            ReadOnly: false
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: log-collector

      # Database container (for development)
      - Name: database
        Image: postgres:14
        Essential: false
        PortMappings:
          - ContainerPort: 5432
            Protocol: tcp
        Environment:
          - Name: POSTGRES_DB
            Value: myapp
          - Name: POSTGRES_USER
            Value: appuser
          - Name: POSTGRES_PASSWORD
            Value: secret123
        MountPoints:
          - SourceVolume: db-data
            ContainerPath: /var/lib/postgresql/data
            ReadOnly: false
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: database

    Volumes:
      - Name: app-logs
      - Name: db-data
```

### Firelens Configuration for Log Routing

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: my-app-firelens
    Cpu: '512'
    Memory: '1024'
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
    RuntimePlatform:
      CpuArchitecture: X86_64
      OperatingSystemFamily: LINUX
    ContainerDefinitions:
      # Firelens sidecar
      - Name: log_router
        Image: public.ecr.aws/aws-observability/aws-for-fluent-bit:stable
        Essential: true
        ReadOnlyRootFilesystem: true
        FirelensConfiguration:
          Type: fluentbit
          Options:
            Enable-CloudWatchLogs: 'true'
            Enable-ELBLogs: 'true'
            ConfigFileValueType: file
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref FirelensLogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: firelens
            awslogs-create-group: 'true'

      # Application container using Firelens
      - Name: my-app
        Image: !Ref ImageUrl
        Essential: true
        LogConfiguration:
          LogDriver: awsfirelens
          Options:
            Name: cloudwatch_logs
            region: !Ref AWS::Region
            log_key: log
            log_group_name: !Ref AppLogGroup
            auto_create_group: 'true'
        PortMappings:
          - ContainerPort: 8080
```

### Environment Variable Injection Strategies

**Static environment variables:**

```yaml
Environment:
  - Name: ENVIRONMENT
    Value: production
  - Name: LOG_LEVEL
    Value: INFO
  - Name: MAX_THREADS
    Value: '200'
```

**Parameter Store references:**

```yaml
Environment:
  - Name: API_ENDPOINT
    Value: !Sub '{{resolve:ssm:/my-app/${Environment}/api-endpoint:1}}'
  - Name: MAX_CONNECTIONS
    Value: !Sub '{{resolve:ssm:/my-app/${Environment}/max-connections:1}}'
```

**Secrets Manager references:**

```yaml
Secrets:
  - Name: DATABASE_PASSWORD
    ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-app/database-password'
  - Name: API_KEY
    ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-app/api-key'
```

**Dynamic image URL from CloudFormation parameter:**

```yaml
Parameters:
  ImageUrl:
    Type: String
    Description: Docker image URL from ECR

Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-app
          Image: !Ref ImageUrl
```

## ECS Service Update Parameters

### Service Update Configuration

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
    EnableECSManagedTags: true
    PropagateTags: SERVICE
    HealthCheckGracePeriodSeconds: 60
    DeploymentController:
      Type: ECS                # ECS, CODE_DEPLOY, or EXTERNAL
```

### Rolling Update Configuration

```yaml
DeploymentConfiguration:
  MaximumPercent: 200
  MinimumHealthyPercent: 100
  DeploymentCircuitBreaker:
    Enable: true
    Rollback: true
```

**Parameters:**
- `MaximumPercent`: Maximum percentage of tasks running during deployment (100-200)
- `MinimumHealthyPercent`: Minimum percentage of healthy tasks (0-100)
- `DeploymentCircuitBreaker`: Enable automatic rollback on failure

**Common configurations:**

**Fast rolling update:**
```yaml
DeploymentConfiguration:
  MaximumPercent: 200
  MinimumHealthyPercent: 50
```

**Conservative rolling update:**
```yaml
DeploymentConfiguration:
  MaximumPercent: 150
  MinimumHealthyPercent: 100
```

### Auto Scaling Configuration

```yaml
ScalableTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MaxCapacity: 10
    MinCapacity: 2
    ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
    RoleARN: !Sub 'arn:aws:iam::${AWS::AccountId}:role/aws-application-autoscaling-role'
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs

TargetTrackingScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: CPUScalingPolicy
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref ScalableTarget
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 70.0
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization
      ScaleInCooldown: 300
      ScaleOutCooldown: 60
```

**Memory-based scaling:**

```yaml
TargetTrackingScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: MemoryScalingPolicy
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref ScalableTarget
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 80.0
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageMemoryUtilization
```

**Custom metric scaling:**

```yaml
TargetTrackingScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: CustomScalingPolicy
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref ScalableTarget
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 1000.0
      CustomizedMetricSpecification:
        MetricName: RequestCountPerTarget
        Namespace: AWS/ApplicationELB
        Statistic: Sum
        Dimensions:
          - Name: TargetGroup
            Value: !Ref TargetGroup
```

### Scheduled Scaling

```yaml
ScheduledActionScaleOut:
  Type: AWS::ApplicationAutoScaling::ScheduledAction
  Properties:
    ScheduledActionName: ScaleOutBusinessHours
    Schedule: 'cron(0 8 ? * MON-FRI *)'
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs
    ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
    ScalableTargetAction:
      MinCapacity: 4
      MaxCapacity: 10

ScheduledActionScaleIn:
  Type: AWS::ApplicationAutoScaling::ScheduledAction
  Properties:
    ScheduledActionName: ScaleInAfterHours
    Schedule: 'cron(0 18 ? * MON-FRI *)'
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs
    ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
    ScalableTargetAction:
      MinCapacity: 2
      MaxCapacity: 4
```

### Task Placement Strategies

```yaml
ECSService:
  Type: AWS::ECS::Service
  Properties:
    PlacementStrategies:
      - Type: binpack
        Field: memory
      - Type: spread
        Field: attribute:ecs.availability-zone
    PlacementConstraints:
      - Type: distinctInstance
      - Type: memberOf
        Expression: attribute:ecs.instance-type =~ t2.*
```

**Available strategies:**
- `random`: Random placement
- `binpack`: Bin pack based on CPU or memory
- `spread`: Spread tasks across availability zones or instances

## CloudFormation Stack Updates

### Basic Stack Update

```yaml
DeployStack:
  Type: Custom::DeployStack
  Properties:
    ServiceToken: !GetAtt LambdaFunction.Arn
```

**GitHub Actions step:**

```yaml
- name: Update CloudFormation stack
  run: |
    aws cloudformation deploy \
      --template-file infrastructure/ecs-stack.yaml \
      --stack-name my-app-ecs \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides \
        Environment=production \
        ImageUrl=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }} \
        DesiredCount=3 \
        CPU=512 \
        Memory=1024
```

### Change Set Deployment

```yaml
- name: Create change set
  run: |
    aws cloudformation create-change-set \
      --stack-name my-app-ecs \
      --change-set-name my-changeset-${{ github.sha }} \
      --template-body file://infrastructure/ecs-stack.yaml \
      --parameters \
        ParameterKey=Environment,ParameterValue=production \
        ParameterKey=ImageUrl,ParameterValue=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }} \
      --capabilities CAPABILITY_NAMED_IAM \
      --change-set-type UPDATE

- name: Wait for change set creation
  run: |
    aws cloudformation wait change-set-create-complete \
      --stack-name my-app-ecs \
      --change-set-name my-changeset-${{ github.sha }}

- name: Describe change set
  run: |
    aws cloudformation describe-change-set \
      --stack-name my-app-ecs \
      --change-set-name my-changeset-${{ github.sha }}

- name: Execute change set
  run: |
    aws cloudformation execute-change-set \
      --stack-name my-app-ecs \
      --change-set-name my-changeset-${{ github.sha }}

- name: Wait for stack update
  run: |
    aws cloudformation wait stack-update-complete \
      --stack-name my-app-ecs
```

### Stack Policies

**Update policy to protect resources:**

```yaml
- name: Deploy with stack policy
  run: |
    aws cloudformation deploy \
      --template-file infrastructure/ecs-stack.yaml \
      --stack-name my-app-ecs \
      --stack-policy-url file://infrastructure/stack-policy.json \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides \
        ImageUrl=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

**stack-policy.json:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "Update:Modify",
      "Principal": "*",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": ["Update:Replace", "Update:Delete"],
      "Principal": "*",
      "Resource": ["LogicalResourceId/DatabaseInstance"]
    }
  ]
}
```

### Nested Stack Updates

```yaml
MainStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${S3Bucket}.s3.amazonaws.com/templates/main.yaml'
    Parameters:
      Environment: !Ref Environment
      VpcId: !ImportValue NetworkStack-VPCId

ECSStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${S3Bucket}.s3.amazonaws.com/templates/ecs.yaml'
    Parameters:
      ClusterName: !Ref ClusterName
      ImageUrl: !Ref ImageUrl
      DesiredCount: !Ref DesiredCount
```

**Update nested stack:**

```yaml
- name: Update nested stack
  run: |
    aws cloudformation update-stack \
      --stack-name my-app-main \
      --use-previous-template \
      --parameters \
        ParameterKey=ImageUrl,ParameterValue=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

### Drift Detection

```yaml
- name: Detect drift
  run: |
    aws cloudformation detect-stack-drift \
      --stack-name my-app-ecs

- name: Wait for drift detection
  run: |
    aws cloudformation wait stack-drift-detection-complete \
      --stack-name my-app-ecs

- name: Describe drift
  run: |
    aws cloudformation describe-stack-drift-detection-status \
      --stack-name my-app-ecs \
      --drift-detection-id $(aws cloudformation describe-stack-resource-drifts \
        --stack-name my-app-ecs \
        --query 'Drifts[0].StackResourceDriftId' \
        --output text)
```

## Security Considerations

### IAM Best Practices

**Least privilege roles:**

```yaml
ECSDeployRole:
  Type: AWS::IAM::Role
  Properties:
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
              token.actions.githubusercontent.com:sub: repo:my-org/my-repo:ref:refs/heads/main
    Policies:
      - PolicyName: MinimalECSDeployPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - ecs:DescribeServices
                - ecs:DescribeTaskDefinition
                - ecs:RegisterTaskDefinition
                - ecs:UpdateService
              Resource: !Sub 'arn:aws:ecs:${AWS::Region}:${AWS::AccountId}:service/my-cluster/my-service'
            - Effect: Allow
              Action:
                - ecr:BatchCheckLayerAvailability
                - ecr:GetDownloadUrlForLayer
                - ecr:InitiateLayerUpload
                - ecr:UploadLayerPart
                - ecr:CompleteLayerUpload
                - ecr:PutImage
              Resource: !Sub 'arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/my-app'
```

**Role chaining for multi-account access:**

```yaml
CrossAccountRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub 'arn:aws:iam::${SourceAccountId}:role/github-actions-ecs-role'
          Action: sts:AssumeRole
    Policies:
      - PolicyName: CrossAccountDeployPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - ecs:UpdateService
                - ecs:RegisterTaskDefinition
              Resource: !Sub 'arn:aws:ecs:${AWS::Region}:${AWS::AccountId}:*'
```

### Secrets Management

**Store sensitive data in Secrets Manager:**

```yaml
DatabaseSecret:
  Type: AWS::SecretsManager::Secret
  Properties:
    Name: !Sub '${Environment}/my-app/database'
    Description: Database credentials for my-app
    GenerateSecretString:
      SecretStringTemplate: '{"username": "myapp_user"}'
      GenerateStringKey: password
      PasswordLength: 32
      ExcludeCharacters: '"@/\'

SecretRotationSchedule:
  Type: AWS::SecretsManager::RotationSchedule
  Properties:
    SecretId: !Ref DatabaseSecret
    RotationLambdaARN: !Ref RotationLambda
    RotationRules:
      AutomaticallyAfterDays: 30
```

**Reference secrets in task definition:**

```yaml
ContainerDefinitions:
  - Name: my-app
    Secrets:
      - Name: DB_HOST
        ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${Environment}/my-app/database:host'
      - Name: DB_PASSWORD
        ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${Environment}/my-app/database:password'
```

### Network Security

**VPC configuration for ECS:**

```yaml
ECSService:
  Type: AWS::ECS::Service
  Properties:
    NetworkConfiguration:
      AwsvpcConfiguration:
        Subnets:
          - !Ref PrivateSubnetA
          - !Ref PrivateSubnetB
        SecurityGroups:
          - !Ref ContainerSecurityGroup
        AssignPublicIp: DISABLED

ContainerSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for ECS containers
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - Description: Allow traffic from load balancer
        IpProtocol: tcp
        FromPort: 8080
        ToPort: 8080
        SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
    SecurityGroupEgress:
      - Description: Allow HTTPS outbound
        IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
```

**VPC endpoints for private communication:**

```yaml
ECREndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ecr.dkr'
    VpcId: !Ref VPC
    VpcEndpointType: Interface
    SubnetIds:
      - !Ref PrivateSubnetA
      - !Ref PrivateSubnetB
    SecurityGroupIds:
      - !Ref VPCEndpointSecurityGroup
    PrivateDnsEnabled: true

ECSEndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ecs'
    VpcId: !Ref VPC
    VpcEndpointType: Interface
    SubnetIds:
      - !Ref PrivateSubnetA
      - !Ref PrivateSubnetB
    SecurityGroupIds:
      - !Ref VPCEndpointSecurityGroup
    PrivateDnsEnabled: true

CloudWatchLogsEndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.logs'
    VpcId: !Ref VPC
    VpcEndpointType: Interface
    SubnetIds:
      - !Ref PrivateSubnetA
      - !Ref PrivateSubnetB
    SecurityGroupIds:
      - !Ref VPCEndpointSecurityGroup
    PrivateDnsEnabled: true
```

### Encryption

**KMS encryption for ECR:**

```yaml
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
          Resource: '*'
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
          Resource: '*'

ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    EncryptionConfiguration:
      EncryptionType: KMS
      KmsKey: !GetAtt EncryptionKey.Arn
```

**Encrypted task secrets:**

```yaml
ContainerDefinitions:
  - Name: my-app
    Secrets:
      - Name: ENCRYPTED_SECRET
        ValueFrom: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:my-app/secret'
```

## Environment Configurations

### Development Environment

```yaml
DevStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${S3Bucket}.s3.amazonaws.com/templates/ecs-stack.yaml'
    Parameters:
      Environment: dev
      DesiredCount: 1
      CPU: '256'
      Memory: '512'
      AutoScalingMinCapacity: 1
      AutoScalingMaxCapacity: 3
      EnableXRayTracing: false
      LogLevel: DEBUG
```

### Staging Environment

```yaml
StagingStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${S3Bucket}.s3.amazonaws.com/templates/ecs-stack.yaml'
    Parameters:
      Environment: staging
      DesiredCount: 2
      CPU: '512'
      Memory: '1024'
      AutoScalingMinCapacity: 2
      AutoScalingMaxCapacity: 5
      EnableXRayTracing: true
      LogLevel: INFO
```

### Production Environment

```yaml
ProdStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${S3Bucket}.s3.amazonaws.com/templates/ecs-stack.yaml'
    Parameters:
      Environment: prod
      DesiredCount: 3
      CPU: '1024'
      Memory: '2048'
      AutoScalingMinCapacity: 3
      AutoScalingMaxCapacity: 10
      EnableXRayTracing: true
      EnableShield: true
      EnableWAF: true
      LogLevel: WARN
      EnableTerminationProtection: true
```

## Monitoring and Logging

### CloudWatch Logs

```yaml
LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /ecs/my-app
    RetentionInDays: 30

LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /ecs/my-app/firelens
    RetentionInDays: 7
```

### CloudWatch Alarms

```yaml
CPUAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: my-app-high-cpu
    AlarmDescription: Alert when CPU exceeds 80%
    MetricName: CPUUtilization
    Namespace: AWS/ECS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: ServiceName
        Value: my-service
      - Name: ClusterName
        Value: my-cluster

MemoryAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: my-app-high-memory
    AlarmDescription: Alert when memory exceeds 85%
    MetricName: MemoryUtilization
    Namespace: AWS/ECS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 85
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: ServiceName
        Value: my-service
      - Name: ClusterName
        Value: my-cluster
```

### Container Insights

```yaml
ECSCluster:
  Type: AWS::ECS::Cluster
  Properties:
    ClusterName: my-cluster
    ClusterSettings:
      - Name: containerInsights
        Value: enabled
```

### X-Ray Tracing

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: my-app
        Image: !Ref ImageUrl
        Environment:
          - Name: AWS_XRAY_DAEMON_ADDRESS
            Value: xray-daemon:2000
          - Name: AWS_XRAY_CONTEXT_MISSING
            Value: LOG_ERROR

  # Add X-Ray sidecar
  - Name: xray-daemon
    Image: amazon/aws-xray-daemon
    Essential: true
    PortMappings:
      - ContainerPort: 2000
        Protocol: udp
```

## Advanced Patterns

### Blue/Green Deployment with CodeDeploy

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
        - !Ref MemoryAlarm
      Enabled: true
    BlueGreenDeploymentConfiguration:
      TerminateBlueInstancesOnDeploymentSuccess:
        Action: TERMINATE
        WaitTimeInMinutes: 10
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
          TestTrafficRoute:
            ListenerArns:
              - !Ref TestListener
```

### A/B Testing Deployments

```yaml
ABTestingDeploymentGroup:
  Type: AWS::CodeDeploy::DeploymentGroup
  Properties:
    ApplicationName: !Ref CodeDeployApplication
    DeploymentGroupName: ab-testing-group
    DeploymentStyle:
      DeploymentType: BLUE_GREEN
      DeploymentOption: WITH_TRAFFIC_CONTROL
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
    BlueGreenDeploymentConfiguration:
      TerminateBlueInstancesOnDeploymentSuccess:
        Action: KEEP_ALIVE
        WaitTimeInMinutes: 60
```

This comprehensive reference provides the technical details needed to implement production-ready ECS deployments with GitHub Actions and CloudFormation.
