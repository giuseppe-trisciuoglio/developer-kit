# AWS CloudFormation ECS - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for ECS container infrastructure.

## AWS::ECS::Cluster

Creates an Amazon ECS cluster.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ClusterName | String | No | The name of the cluster |
| ClusterSettings | List of ClusterSetting | No | The settings for the cluster |
| ServiceConnectDefaults | ServiceConnectDefaults | No | Service Connect configuration |
| Tags | List of Tag | No | Tags for the cluster |

### ClusterSetting Structure

| Property | Type | Description |
|----------|------|-------------|
| Name | String | The setting name (containerInsights) |
| Value | String | The setting value (enabled, disabled) |

### Example

```yaml
Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${AWS::StackName}-cluster"
      ClusterSettings:
        - Name: containerInsights
          Value: enabled
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the cluster |
| ClusterName | The name of the cluster |

## AWS::ECS::TaskDefinition

Creates a task definition for ECS.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Family | String | No | The family name for the task definition |
| Cpu | String | No | The CPU units for the task (128-122880) |
| Memory | String | No | The memory for the task (4-150000 MiB) |
| NetworkMode | String | No | Network mode (none, bridge, awsvpc, host) |
| RequiresCompatibilities | List of String | No | Launch types (EC2, FARGATE) |
| ExecutionRoleArn | String | No | IAM role for task execution |
| TaskRoleArn | String | No | IAM role for task containers |
| TaskRoleArn | String | No | IAM role for task containers |
| Volumes | List of Volume | No | List of volumes |
| ContainerDefinitions | List of ContainerDefinition | Yes | Container definitions |
| InferenceAccelerators | List of InferenceAccelerator | No | Inference accelerators |
| EphemeralStorage | EphemeralStorage | No | Ephemeral storage size (21-200 GB) |
| RuntimePlatform | RuntimePlatform | No | OS/Architecture settings |
| Tags | List of Tag | No | Tags for the task definition |

### ContainerDefinition Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | The name of the container |
| Image | String | Yes | Docker image URI or ECR URI |
| Cpu | Integer | No | CPU units for the container |
| Memory | Integer | No | Memory hard limit for container |
| MemoryReservation | Integer | No | Memory soft limit for container |
| PortMappings | List of PortMapping | No | Port mappings |
| Essential | Boolean | No | Whether container is essential |
| EntryPoint | List of String | No | Entrypoint |
| Command | List of String | No | Command to run |
| Environment | List of KeyValuePair | No | Environment variables |
| Secrets | List of Secret | No | Secrets from Secrets Manager |
| LogConfiguration | LogConfiguration | No | Logging configuration |
| HealthCheck | HealthCheck | No | Health check configuration |
| DependsOn | List of ContainerDependency | No | Dependencies |
| DisableNetworking | Boolean | No | Disable networking |
| Privileged | Boolean | No | Enable privileged mode |
| ReadonlyRootFilesystem | Boolean | No | Read-only root filesystem |
| Ulimits | List of Ulimit | No | Ulimits |
| WorkingDirectory | String | No | Working directory |

### PortMapping Structure

| Property | Type | Description |
|----------|------|-------------|
| ContainerPort | Integer | Port on the container |
| HostPort | Integer | Port on the host instance |
| Protocol | String | Protocol (tcp, udp) |

### Secret Structure

| Property | Type | Description |
|----------|------|-------------|
| Name | String | Name of the secret |
| ValueFrom | String | ARN of the secret |

### LogConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| LogDriver | String | Log driver (json-file, syslog, awslogs, etc.) |
| Options | Map of String | Driver-specific options |

### HealthCheck Structure

| Property | Type | Description |
|----------|------|-------------|
| Command | List of String | Health check command |
| Interval | Integer | Interval in seconds (5-300) |
| Timeout | Integer | Timeout in seconds (2-60) |
| Retries | Integer | Retry attempts (1-10) |
| StartPeriod | Integer | Start period in seconds (0-300) |

### Example

```yaml
Resources:
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: web-app
      Cpu: "512"
      Memory: "1024"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - EC2
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: web
          Image: nginx:latest
          Cpu: 256
          Memory: 512
          PortMappings:
            - ContainerPort: 80
              Protocol: tcp
          Environment:
            - Name: ENV
              Value: !Ref Environment
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:80/health || exit 1
            Interval: 30
            Timeout: 5
            Retries: 3
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| TaskDefinitionArn | The ARN of the task definition |
| Family | The family name of the task definition |
| Revision | The revision number |

## AWS::ECS::Service

Creates an Amazon ECS service.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Cluster | String | Yes | ARN or name of the cluster |
| ServiceName | String | No | The name of the service |
| TaskDefinition | String | Yes | ARN or family:revision of task definition |
| DesiredCount | Integer | No | Desired number of tasks (1-1000) |
| LaunchType | String | No | Launch type (EC2, FARGATE, EXTERNAL) |
| CapacityProviderStrategy | List of CapacityProviderStrategyItem | No | Capacity provider strategy |
| DeploymentConfiguration | DeploymentConfiguration | No | Deployment configuration |
| SchedulingStrategy | String | No | REPLICA or DAEMON |
| PlacementConstraints | List of PlacementConstraint | No | Placement constraints |
| PlacementStrategies | List of PlacementStrategy | No | Placement strategies |
| NetworkConfiguration | NetworkConfiguration | No | Network configuration |
| LoadBalancers | List of LoadBalancer | No | Load balancers |
| ServiceRegistries | List of ServiceRegistry | No | Service discovery |
| PropagateTags | String | No | Propagate tags (TASK_DEFINITION, SERVICE) |
| EnableExecuteCommand | Boolean | No | Enable ECS Execute |
| HealthCheckGracePeriodSeconds | Integer | No | Grace period for health checks |
| Tags | List of Tag | No | Tags for the service |

### DeploymentConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| MaximumPercent | Integer | Max tasks during deployment (100-200) |
| MinimumHealthyPercent | Integer | Min healthy tasks (0-100) |
| DeploymentCircuitBreaker | DeploymentCircuitBreaker | Circuit breaker config |

### DeploymentCircuitBreaker Structure

| Property | Type | Description |
|----------|------|-------------|
| Enable | Boolean | Enable circuit breaker |
| Rollback | Boolean | Enable automatic rollback |

### CapacityProviderStrategyItem Structure

| Property | Type | Description |
|----------|------|-------------|
| CapacityProvider | String | Capacity provider name |
| Weight | Integer | Weight for the provider |
| Base | Integer | Base tasks for the provider |

### NetworkConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| AwsvpcConfiguration | AwsVpcConfiguration | VPC configuration |

### AwsVpcConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| AssignPublicIp | String | ENABLED or DISABLED |
| SecurityGroups | List of String | Security group IDs |
| Subnets | List of String | Subnet IDs |

### LoadBalancer Structure

| Property | Type | Description |
|----------|------|-------------|
| ContainerName | String | Name of the container |
| ContainerPort | Integer | Port on the container |
| TargetGroupArn | String | ARN of target group |

### ServiceRegistry Structure

| Property | Type | Description |
|----------|------|-------------|
| RegistryArn | String | ARN of service discovery |
| Port | Integer | Port number |
| ContainerName | String | Container name |
| ContainerPort | Integer | Container port |

### PlacementConstraint Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | Constraint type (memberOf, distinctInstance) |
| Expression | String | Constraint expression |

### PlacementStrategy Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | Strategy type (random, spread, binpack) |
| Field | String | Field for spread/binpack |

### Example

```yaml
Resources:
  EcsService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${AWS::StackName}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 50
        DeploymentCircuitBreaker:
          Enable: true
          Rollback: true
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: DISABLED
          SecurityGroups:
            - !Ref EcsSecurityGroup
          Subnets: !Ref PrivateSubnets
      LoadBalancers:
        - ContainerName: web
          ContainerPort: 80
          TargetGroupArn: !Ref TargetGroup
      PropagateTags: SERVICE
      ServiceRegistries:
        - RegistryArn: !GetAtt ServiceDiscoveryService.Arn
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| ServiceArn | The ARN of the service |
| ServiceName | The name of the service |
| DesiredCount | The desired task count |

## AWS::ECS::TaskSet

Creates a task set for an ECS service.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Cluster | String | Yes | ARN of the cluster |
| Service | String | Yes | ARN of the service |
| TaskDefinition | String | Yes | ARN of the task definition |
| Scale | Scale | No | Scale configuration |
| TaskSetTags | List of Tag | No | Tags |

### Scale Structure

| Property | Type | Description |
|----------|------|-------------|
| Unit | String | PERCENT |
| Value | Integer | Scale value (0-100) |

### Attributes

| Attribute | Description |
|-----------|-------------|
| TaskSetArn | The ARN of the task set |

## AWS::ECS::CapacityProvider

Creates a capacity provider for ECS.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the capacity provider |
| AutoScalingGroupProvider | AutoScalingGroupProvider | Yes | ASG configuration |
| Tags | List of Tag | No | Tags |

### AutoScalingGroupProvider Structure

| Property | Type | Description |
|----------|------|-------------|
| AutoScalingGroupArn | String | ARN of the ASG |
| ManagedScaling | ManagedScaling | Scaling settings |
| ManagedTerminationProtection | String | Termination protection |

### ManagedScaling Structure

| Property | Type | Description |
|----------|------|-------------|
| Status | String | ENABLED or DISABLED |
| TargetCapacity | Integer | Target capacity |
| MinimumScalingStepSize | Integer | Min step |
| MaximumScalingStepSize | Integer | Max step |
| ScaleInInterval | Integer | Scale-in interval |

### Example

```yaml
Resources:
  CapacityProvider:
    Type: AWS::ECS::CapacityProvider
    Properties:
      Name: !Sub "${AWS::StackName}-capacity-provider"
      AutoScalingGroupProvider:
        AutoScalingGroupArn: !Ref AutoScalingGroup
        ManagedScaling:
          Status: ENABLED
          TargetCapacity: 80
          MinimumScalingStepSize: 1
          MaximumScalingStepSize: 10
        ManagedTerminationProtection: DISABLED
```

## AWS::ApplicationAutoScaling::ScalableTarget

Creates a scalable target for ECS service auto scaling.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| MaxCapacity | Integer | Yes | Maximum capacity |
| MinCapacity | Integer | Yes | Minimum capacity |
| ResourceId | String | Yes | Resource ID (service/cluster/service) |
| RoleARN | String | Yes | IAM role ARN |
| ScalableDimension | String | Yes | ecs:service:DesiredCount |
| ServiceNamespace | String | Yes | ecs |

### Example

```yaml
Resources:
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 10
      MinCapacity: 2
      ResourceId: !Sub "service/${ClusterName}/${ServiceName}"
      RoleARN: !Ref AutoScalingRoleArn
      ScalableDimension: ecs:service:DesiredCount
      ServiceNamespace: ecs
```

## AWS::ApplicationAutoScaling::ScalingPolicy

Creates a scaling policy for ECS.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PolicyName | String | Yes | Name of the policy |
| PolicyType | String | Yes | TargetTrackingScaling or StepScaling |
| ScalingTargetId | String | Yes | ID of scalable target |
| TargetTrackingScalingPolicyConfiguration | TargetTrackingScalingPolicyConfiguration | Cond | Target tracking config |
| StepScalingPolicyConfiguration | StepScalingPolicyConfiguration | Cond | Step scaling config |

### TargetTrackingScalingPolicyConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| PredefinedMetricSpecification | PredefinedMetricSpecification | Predefined metric |
| CustomizedMetricSpecification | CustomizedMetricSpecification | Custom metric |
| TargetValue | Double | Target value |
| ScaleInCooldown | Integer | Scale-in cooldown |
| ScaleOutCooldown | Integer | Scale-out cooldown |

### PredefinedMetricSpecification Structure

| Property | Type | Description |
|----------|------|-------------|
| PredefinedMetricType | String | ECSServiceAverageCPUUtilization, ECSServiceAverageMemoryUtilization |

### StepScalingPolicyConfiguration Structure

| Property | Type | Description |
|----------|------|-------------|
| AdjustmentType | String | ChangeInCapacity, PercentChangeInCapacity, ExactCapacity |
| Cooldown | Integer | Cooldown period |
| MetricAggregationType | String | Average, Maximum, Minimum |
| StepAdjustments | List of StepAdjustment | Step adjustments |

### StepAdjustment Structure

| Property | Type | Description |
|----------|------|-------------|
| MetricIntervalLowerBound | Double | Lower bound |
| MetricIntervalUpperBound | Double | Upper bound |
| ScalingAdjustment | Integer | Adjustment amount |

### Example

```yaml
Resources:
  CpuScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-cpu-scaling"
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ECSServiceAverageCPUUtilization
        TargetValue: 70
        ScaleInCooldown: 300
        ScaleOutCooldown: 60
```

## AWS::ServiceDiscovery::Service

Creates a service discovery service.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the service |
| NamespaceId | String | Yes | ARN of the namespace |
| DnsConfig | DnsConfig | Yes | DNS configuration |
| HealthCheckConfig | HealthCheckConfig | No | Health check config |
| HealthCheckCustomConfig | HealthCheckCustomConfig | No | Custom health check |
| Description | String | No | Description |
| Tags | List of Tag | No | Tags |

### DnsConfig Structure

| Property | Type | Description |
|----------|------|-------------|
| NamespaceId | String | Namespace ARN |
| RoutingPolicy | String | MULTIVALUE, LATENCY, GEODNS |
| DnsRecords | List of DnsRecord | DNS records |

### DnsRecord Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | A, AAAA, SRV, CNAME |
| TTL | Integer | TTL in seconds |

### Example

```yaml
Resources:
  ServiceDiscoveryService:
    Type: AWS::ServiceDiscovery::Service
    Properties:
      Name: web-app
      NamespaceId: !Ref ServiceDiscoveryNamespace
      DnsConfig:
        DnsRecords:
          - Type: A
            TTL: 60
      HealthCheckConfig:
        Type: HTTP
        ResourcePath: /health
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the service |
| Name | The name of the service |

## AWS::ServiceDiscovery::PrivateDnsNamespace

Creates a private DNS namespace.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the namespace |
| Vpc | String | Yes | VPC ID |
| Description | String | No | Description |
| Tags | List of Tag | No | Tags |

### Example

```yaml
Resources:
  ServiceDiscoveryNamespace:
    Type: AWS::ServiceDiscovery::PrivateDnsNamespace
    Properties:
      Name: !Sub "${Environment}.internal"
      Vpc: !Ref VpcId
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the namespace |
| Id | The ID of the namespace |

## AWS::CodeDeploy::BlueGreen

Creates a blue/green hook for ECS deployments.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| TrafficRoutingConfig | TrafficRoutingConfig | No | Traffic routing config |
| AdditionalOptions | AdditionalOptions | No | Additional options |
| LifecycleEventHooks | LifecycleEventHooks | No | Lifecycle hooks |
| ServiceRole | String | Yes | CodeDeploy service role |
| Applications | List of BlueGreenApplication | Yes | Target applications |

### TrafficRoutingConfig Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | AllAtOnce, TimeBasedCanary, TimeBasedLinear |
| TimeBasedCanary | TimeBasedCanary | Canary config |
| TimeBasedLinear | TimeBasedLinear | Linear config |

### TimeBasedCanary Structure

| Property | Type | Description |
|----------|------|-------------|
| StepPercentage | Integer | Traffic percentage for first step (>=14) |
| BakeTimeMins | Integer | Minutes between steps |

### TimeBasedLinear Structure

| Property | Type | Description |
|----------|------|-------------|
| StepPercentage | Integer | Traffic increment percentage |
| BakeTimeMins | Integer | Minutes between increments |

### AdditionalOptions Structure

| Property | Type | Description |
|----------|------|-------------|
| TerminationWaitTimeInMinutes | Integer | Wait time before termination |

### LifecycleEventHooks Structure

| Property | Type | Description |
|----------|------|-------------|
| BeforeInstall | String | Lambda function for BeforeInstall |
| AfterInstall | String | Lambda function for AfterInstall |
| AfterAllowTestTraffic | String | Lambda function for AfterAllowTestTraffic |
| BeforeAllowTraffic | String | Lambda function for BeforeAllowTraffic |
| AfterAllowTraffic | String | Lambda function for AfterAllowTraffic |

### BlueGreenApplication Structure

| Property | Type | Description |
|----------|------|-------------|
| Target | BlueGreenTarget | Target service |
| ECSAttributes | ECSAttributes | ECS-specific config |

### BlueGreenTarget Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | AWS::ECS::Service |
| LogicalID | String | Logical ID of the service |

### ECSAttributes Structure

| Property | Type | Description |
|----------|------|-------------|
| TaskDefinitions | List of String | Task definition logical IDs |
| TaskSets | List of String | Task set logical IDs |
| TrafficRouting | TrafficRouting | Traffic routing config |

### TrafficRouting Structure

| Property | Type | Description |
|----------|------|-------------|
| ProdTrafficRoute | TrafficRoute | Production listener |
| TestTrafficRoute | TrafficRoute | Test listener |
| TargetGroups | List of String | Target group logical IDs |

### TrafficRoute Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | AWS::ElasticLoadBalancingV2::Listener |
| LogicalID | String | Logical ID of the listener |

### Example

```yaml
Hooks:
  BlueGreenHook:
    Type: AWS::CodeDeploy::BlueGreen
    Properties:
      TrafficRoutingConfig:
        Type: TimeBasedCanary
        TimeBasedCanary:
          StepPercentage: 15
          BakeTimeMins: 5
      AdditionalOptions:
        TerminationWaitTimeInMinutes: 5
      ServiceRole: !Ref CodeDeployRoleArn
      Applications:
        - Target:
            Type: AWS::ECS::Service
            LogicalID: EcsService
          ECSAttributes:
            TaskDefinitions:
              - TaskDefinitionBlue
              - TaskDefinitionGreen
            TaskSets:
              - TaskSetBlue
              - TaskSetGreen
            TrafficRouting:
              ProdTrafficRoute:
                Type: AWS::ElasticLoadBalancingV2::Listener
                LogicalID: ProductionListener
              TestTrafficRoute:
                Type: AWS::ElasticLoadBalancingV2::Listener
                LogicalID: TestListener
              TargetGroups:
                - BlueTargetGroup
                - GreenTargetGroup
```

## AWS::ElasticLoadBalancingV2::TargetGroup

Creates a target group for ALB.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | Name of the target group |
| Port | Integer | Yes | Port on the targets |
| Protocol | String | Yes | Protocol (HTTP, HTTPS, TCP, TLS) |
| VpcId | String | Yes | VPC ID |
| HealthCheckPath | String | No | Health check path |
| HealthCheckProtocol | String | No | Health check protocol |
| HealthCheckPort | String | No | Health check port |
| HealthCheckIntervalSeconds | Integer | No | Interval (5-300) |
| HealthCheckTimeoutSeconds | Integer | No | Timeout (2-60) |
| HealthyThresholdCount | Integer | No | Healthy threshold (2-10) |
| UnhealthyThresholdCount | Integer | No | Unhealthy threshold (2-10) |
| Matcher | Matcher | No | Success codes |
| TargetType | String | No | instance, ip, lambda |
| IpAddressType | String | No | ipv4, ipv6 |
| Tags | List of Tag | No | Tags |

### Matcher Structure

| Property | Type | Description |
|----------|------|-------------|
| HttpCode | String | HTTP status code(s) |
| GrpcCode | String | gRPC status code(s) |

### Example

```yaml
Resources:
  BlueTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${AWS::StackName}-blue-tg"
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      Matcher:
        HttpCode: 200-499
      TargetType: ip
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| TargetGroupArn | The ARN of the target group |
| TargetGroupName | The name of the target group |

## AWS::ElasticLoadBalancingV2::Listener

Creates a listener for ALB.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DefaultActions | List of Action | Yes | Default actions |
| LoadBalancerArn | String | Yes | ARN of the load balancer |
| Port | Integer | Yes | Port (1-65535) |
| Protocol | String | Yes | Protocol (HTTP, HTTPS, TCP, TLS) |
| Certificates | List of Certificate | No | Certificates |
| SslPolicy | String | No | SSL policy (HTTPS/TLS only) |

### Action Structure

| Property | Type | Description |
|----------|------|-------------|
| Type | String | forward, redirect, authenticate-oidc, authenticate-cognito, fixed-response |
| TargetGroupArn | String | Target group ARN |
| ForwardConfig | ForwardConfig | Forward config |
| RedirectConfig | RedirectConfig | Redirect config |

### Example

```yaml
Resources:
  ProductionListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          ForwardConfig:
            TargetGroupStickinessConfig:
              Enabled: true
              DurationSeconds: 3600
            TargetGroups:
              - TargetGroupArn: !Ref BlueTargetGroup
                Weight: 100
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
```

## Intrinsic Functions Reference

### !Ref

Returns the value of the specified parameter or resource.

```yaml
# Reference a parameter
ClusterName: !Ref ClusterNameParam

# Reference a resource (returns the physical ID)
ClusterArn: !Ref ECSCluster
```

### !GetAtt

Returns the value of an attribute from an ECS resource.

```yaml
# Get the cluster ARN
ClusterArn: !GetAtt ECSCluster.Arn

# Get service ARN
ServiceArn: !GetAtt EcsService.Arn

# Get task definition ARN
TaskDefinitionArn: !Ref TaskDefinition
```

### !Sub

Substitutes variables in an input string.

```yaml
# With variable substitution
ClusterName: !Sub "${AWS::StackName}-cluster"

# With multiple variables
RoleArn: !Sub "arn:aws:iam::${AWS::AccountId}:role/${RoleName}"
```

### !ImportValue

Imports values exported by other stacks.

```yaml
# Import from another stack
ClusterArn: !ImportValue
  !Sub "${NetworkStackName}-ClusterArn"
```

### !FindInMap

Returns the value from a mapping.

```yaml
# Find in mapping
MemorySize: !FindInMap [EnvironmentConfig, !Ref Environment, Memory]
```

### !If

Returns one value if condition is true, another if false.

```yaml
# Conditional resource
DesiredCount: !If [IsProduction, 10, 2]
```

## IAM Policy Templates for ECS

### AmazonECSTaskExecutionRolePolicy

```yaml
Policies:
  - AmazonECSTaskExecutionRolePolicy
```

### Custom Policy for ECR

```yaml
Policies:
  - PolicyName: EcrPullPolicy
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - ecr:GetDownloadUrlForLayer
            - ecr:BatchGetImage
            - ecr:BatchCheckLayerAvailability
          Resource: !Ref EcrRepositoryArn
```

### Custom Policy for Secrets

```yaml
Policies:
  - PolicyName: SecretsPolicy
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource: !Ref SecretArn
```

### Custom Policy for CloudWatch Logs

```yaml
Policies:
  - PolicyName: CloudWatchLogsPolicy
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: !GetAtt LogGroup.Arn
```

## ECS Task Definition Parameters

### CPU and Memory Values

| CPU Units | Memory Options (MiB) |
|-----------|---------------------|
| 128 | 4-1024 |
| 256 | 4-2048 |
| 512 | 4-4096 |
| 1024 | 8-8192 |
| 2048 | 16-16384 |
| 4096 | 32-30720 |

### Fargate CPU/Memory Combinations

| CPU (vCPU) | Memory (GiB) |
|------------|--------------|
| 0.25 | 0.5, 1, 2 |
| 0.5 | 1, 2, 3, 4 |
| 1 | 2, 3, 4, 5, 6, 7, 8 |
| 2 | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 4 | 8-30 |
| 8 | 16-60 |

### Container Sizes

| Container Size | Memory Hard Limit | Memory Soft Limit |
|----------------|-------------------|-------------------|
| Small | 512 MiB | 256 MiB |
| Medium | 1024 MiB | 512 MiB |
| Large | 2048 MiB | 1024 MiB |
| X-Large | 4096 MiB | 2048 MiB |

## Common Tags for ECS

```yaml
Resources:
  EcsService:
    Type: AWS::ECS::Service
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: team@example.com
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: "12345"
        - Key: Version
          Value: "1.0.0"
```

## Limits and Quotas

### ECS Limits

| Resource | Default Limit |
|----------|---------------|
| Clusters per account | 1000 |
| Services per cluster | 500 |
| Tasks per service (EC2) | 1000 |
| Tasks per service (Fargate) | 200 |
| Container instances per cluster | 1000 |
| Container definitions per task | 10 |
| Volumes per task | 5 |
| Port mappings per container | 100 |

### Fargate Limits

| Resource | Default Limit |
|----------|---------------|
| Tasks per launch | 10 |
| CPU (vCPU) | 0.25-16 |
| Memory (GiB) | 0.5-120 |
| Ephemeral storage (GB) | 20-200 |

### CloudWatch Limits

| Metric | Limit |
|--------|-------|
| Dimensions per metric | 30 |
| Alarm actions | 5 |
| Metric data points | 150000 |

## Health Check Best Practices

### Health Check Command Examples

```yaml
HealthCheck:
  Command:
    - CMD-SHELL
    - curl -f http://localhost:8080/health || exit 1
  Interval: 30
  Timeout: 5
  Retries: 3
  StartPeriod: 60
```

### HTTP Health Check

```yaml
HealthCheck:
  Command:
    - CMD-SHELL
    - wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
```

### TCP Health Check

```yaml
HealthCheck:
  Command:
    - CMD-SHELL
    - nc -z localhost 8080 || exit 1
```

### Health Check Considerations

- Set `StartPeriod` to allow container initialization
- Keep `Interval` reasonable (15-30 seconds)
- Set `Timeout` shorter than interval
- Set `Retries` appropriately (2-3)
- Use specific endpoint for health checks
