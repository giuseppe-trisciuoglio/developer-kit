# Best Practices, Monitoring, and Troubleshooting

## Security Best Practices

### Use OIDC Authentication

OpenID Connect (OIDC) provides secure, passwordless authentication between GitHub Actions and AWS, eliminating the need for long-lived IAM credentials.

**Benefits:**
- No IAM access keys to manage or rotate
- Temporary credentials with limited lifetime
- Scoped permissions by repository/branch
- Centralized audit trail

### Implement Least Privilege IAM Roles

```yaml
Policies:
  - PolicyName: ECSDeployPolicy
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - ecs:UpdateService
            - ecs:RegisterTaskDefinition
          Resource: !Sub 'arn:aws:ecs:${AWS::Region}:${AWS::AccountId}:service/cluster-name/*'
```

### Enable ECR Image Scanning

```yaml
ECRRepository:
  Type: AWS::ECR::Repository
  Properties:
    ImageScanningConfiguration:
      ScanOnPush: true
```

### Use AWS Secrets Manager

Never store secrets in GitHub repository or workflow files.

```yaml
secrets:
  - Name: DB_PASSWORD
    ValueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:my-app/db-password
```

### VPC Endpoints for Private Networks

```yaml
ECRInterfaceEndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ecr.dkr'
    VpcEndpointType: Interface
    PrivateDnsEnabled: true
    SubnetIds:
      - !Ref PrivateSubnetA
    SecurityGroupIds:
      - !Ref EndpointSecurityGroup
```

## Performance Optimization

### Docker Layer Caching

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Multi-Stage Builds

Minimize image size by using multi-stage Dockerfiles.

```dockerfile
# Build stage
FROM maven:3.8-openjdk-11 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package

# Runtime stage
FROM openjdk:11-jre-slim
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Parallel Deployments

Deploy to multiple environments in parallel using matrix strategy.

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
```

### Fargate Spot for Cost Savings

```yaml
CapacityProviderStrategy:
  - Base: FARGATE_SPOT
    Weight: 1
  - Base: FARGATE
    Weight: 3
```

## Cost Optimization

### ECR Lifecycle Policies

```yaml
LifecyclePolicy:
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
        },
        {
          "rulePriority": 2,
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

### Right-Sized Task CPU and Memory

Monitor and adjust CPU/memory based on actual usage.

```yaml
AutoScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MaxCapacity: 10
    MinCapacity: 2
    ResourceId: !Sub 'service/${ECSCluster}/${ECSService}'
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs
```

### Scheduled Scaling

```yaml
ScheduledAction:
  Type: AWS::ApplicationAutoScaling::ScheduledAction
  Properties:
    ScheduledActionName: scale-up-during-business-hours
    Schedule: 'cron(0 8 * * ? *)'
    ScalableTargetAction:
      MinCapacity: 5
      MaxCapacity: 10
```

## Monitoring and Observability

### CloudWatch Container Insights

```yaml
Cluster:
  Type: AWS::ECS::Cluster
  Properties:
    ClusterSettings:
      - Name: containerInsights
        Value: enabled
```

### Centralized Logging

```yaml
LogConfiguration:
  LogDriver: awslogs
  Options:
    awslogs-group: !Ref LogGroup
    awslogs-region: !Ref AWS::Region
    awslogs-stream-prefix: ecs
```

### Health Check Configuration

```yaml
HealthCheckGracePeriodSeconds: 60
```

### CloudWatch Alarms

```yaml
CPUPercentageAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    MetricName: CPUUtilization
    Namespace: AWS/ECS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
```

### X-Ray Tracing

```yaml
TracingConfiguration:
  Mode: Active
```

## Troubleshooting

### Authentication Failures

**Symptoms**: `User is not authorized to perform action: ecs:UpdateService`

**Solutions**:
- Verify OIDC trust relationship matches GitHub organization/repository
- Check IAM role has proper permissions for ECR and ECS
- Ensure GitHub Actions repository has `id-token: write` permission
- Verify role assumption conditions match repository path

**Debug Commands**:
```yaml
- name: Debug AWS credentials
  run: |
    aws sts get-caller-identity
    aws iam list-attached-role-policies --role-name github-actions-ecs-role
```

### Deployment Failures

**Symptoms**: Tasks fail to start or service never stabilizes

**Solutions**:
- Check CloudWatch Logs for application errors
- Verify task definition matches service requirements
- Ensure sufficient CPU/memory in Fargate cluster
- Review health check configuration
- Verify security group rules allow necessary traffic

**Debug Commands**:
```bash
aws ecs describe-services --cluster my-cluster --services my-service
aws ecs describe-tasks --cluster my-cluster --tasks <task-ids>
```

### ECR Push Failures

**Symptoms**: `denied: Your authorization token has expired` or `no basic creds`

**Solutions**:
- Verify repository exists and permissions are correct
- Check image tag format and registry URL
- Ensure Docker daemon is running in GitHub Actions runner
- Verify image size doesn't exceed ECR limits (10 GB per image layer)

### CloudFormation Rollback

**Symptoms**: Stack creation/update fails and rolls back

**Solutions**:
- Review stack events in AWS Console
- Check parameter values match resource constraints
- Verify IAM role has `cloudformation:UpdateStack` permission
- Enable termination protection for production stacks
- Check for resource quotas and limits

**Debug Commands**:
```bash
aws cloudformation describe-stack-events --stack-name my-stack --max-items 10
aws cloudformation describe-stack-resources --stack-name my-stack
```

### Task Stuck in PENDING State

**Symptoms**: Tasks remain in PENDING state and never start

**Solutions**:
- Check if there are sufficient resources in the VPC (subnets, ENIs)
- Verify security groups allow outbound traffic
- Check IAM task execution role has proper permissions
- Review task definition for misconfigurations
- Verify container image exists in ECR and is accessible

### Service Deployment Timeout

**Symptoms**: Deployment exceeds timeout and fails

**Solutions**:
- Increase deployment timeout with `deploy_timeout` parameter
- Adjust health check grace period
- Review application startup time
- Check if service is receiving enough traffic for health checks
- Verify load balancer target group is healthy

## Additional Monitoring Commands

### View Service Events

```bash
aws ecs describe-services --cluster my-cluster --services my-service --query 'services[0].events'
```

### View Task Logs

```bash
aws logs tail /ecs/my-app --follow
```

### View CloudWatch Metrics

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=my-service \
  --statistic Average \
  --period 300
```

### Check Deployment Status

```bash
aws ecs describe-services \
  --cluster my-cluster \
  --services my-service \
  --query 'services[0].deployments[0]'
```
