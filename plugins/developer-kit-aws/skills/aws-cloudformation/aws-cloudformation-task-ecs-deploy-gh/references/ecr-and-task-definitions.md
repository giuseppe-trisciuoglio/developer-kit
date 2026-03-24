# ECR and Task Definitions

## ECR Repository Configuration

### ECR Repository with Image Scanning

```yaml
ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    ImageScanningConfiguration:
      ScanOnPush: true
    ImageTagMutability: IMMUTABLE
    LifecyclePolicy:
      LifecyclePolicyText: |
        {
          "rules": [
            {
              "rulePriority": 1,
              "description": "Keep last 30 images",
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

### ECR Repository with KMS Encryption

```yaml
KMSKey:
  Type: AWS::KMS::Key
  Properties:
    Description: KMS key for ECR encryption
    KeyPolicy:
      Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
          Action: 'kms:*'
          Resource: '*'

ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    RepositoryName: my-app
    EncryptionConfiguration:
      EncryptionType: KMS
      KmsKey: !GetAtt KMSKey.Arn
```

### Build and Push to ECR

```yaml
- name: Login to ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: |
      ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
      ${{ steps.login-ecr.outputs.registry }}/my-app:latest
      ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.ref_name }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
    build-args: |
      BUILD_DATE=${{ github.event.head_commit.timestamp }}
      VERSION=${{ github.sha }}
```

## Task Definition Management

### Basic Task Definition (JSON)

**task-definition.json:**

```json
{
  "family": "my-app-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "my-app",
      "image": "PLACEHOLDER_IMAGE",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "info"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-app/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      },
      "ulimits": [
        {
          "name": "nofile",
          "softLimit": 65536,
          "hardLimit": 65536
        }
      ]
    }
  ]
}
```

### Dynamic Task Definition Update

```yaml
- name: Render task definition
  uses: aws-actions/amazon-ecs-render-task-definition@v1
  id: render-task
  with:
    task-definition: task-definition.json
    container-name: my-app
    image: ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}

- name: Deploy task definition
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: ${{ steps.render-task.outputs.task-definition }}
    service: my-service
    cluster: my-cluster
    wait-for-service-stability: true
    deploy_timeout: 30 minutes
```

### CloudFormation Task Definition

```yaml
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
            Protocol: tcp
        Environment:
          - Name: ENVIRONMENT
            Value: !Ref Environment
          - Name: LOG_LEVEL
            Value: !Ref LogLevel
        Secrets:
          - Name: DB_PASSWORD
            ValueFrom: !Ref DBPasswordSecret
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: !Ref AWS::Region
            awslogs-stream-prefix: ecs
        LinuxParameters:
          Ulimits:
            - Name: nofile
              SoftLimit: 65536
              HardLimit: 65536
```

## Task Definition with Sidecar Container

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: my-app-with-sidecar
    Cpu: '512'
    Memory: '1024'
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    ContainerDefinitions:
      - Name: my-app
        Image: !Ref AppImageUrl
        PortMappings:
          - ContainerPort: 8080
        DependsOn:
          - ContainerName: log-router
          Condition: START
        Environment:
          - Name: LOG_HOSTNAME
            Value: localhost
          - Name: LOG_PORT
            Value: '5000'
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup

      - Name: log-router
        Image: !Ref LogRouterImage
        Essential: false
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
        PortMappings:
          - ContainerPort: 5000
```

## Task Definition with Multiple Containers

```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: multi-container-app
    Cpu: '1024'
    Memory: '2048'
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    ContainerDefinitions:
      - Name: web-app
        Image: !Ref WebAppImage
        PortMappings:
          - ContainerPort: 8080
        Environment:
          - Name: API_URL
            Value: http://localhost:8081
        Links:
          - api

      - Name: api
        Image: !Ref ApiImage
        PortMappings:
          - ContainerPort: 8081
        Environment:
          - Name: DB_HOST
            Value: !Ref DatabaseEndpoint

      - Name: nginx-proxy
        Image: nginx:latest
        PortMappings:
          - ContainerPort: 80
        Essential: true
        Links:
          - web-app
        MountPoints:
          - SourceVolume: nginx-config
            Destination: /etc/nginx
        LogConfiguration:
          LogDriver: awslogs

    Volumes:
      - Name: nginx-config
```
