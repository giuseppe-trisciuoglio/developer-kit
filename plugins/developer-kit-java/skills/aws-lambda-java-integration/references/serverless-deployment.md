# Serverless Deployment Reference

Complete guide for deploying Java Lambda functions with Serverless Framework, AWS SAM, and CI/CD pipelines.

## Table of Contents

1. [Serverless Framework](#serverless-framework)
2. [AWS SAM](#aws-sam)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Provisioned Concurrency](#provisioned-concurrency)
5. [Monitoring](#monitoring)
6. [Build Optimization](#build-optimization)
7. [Package Optimization](#package-optimization)
8. [Performance Tuning](#performance-tuning)
9. [Rollback Strategy](#rollback-strategy)
10. [Security Best Practices](#security-best-practices)
11. [Cost Optimization](#cost-optimization)
12. [SAM vs Serverless Framework](#sam-vs-serverless-framework)

---

## Serverless Framework

### Basic Configuration

```yaml
service: java-lambda-api

provider:
  name: aws
  runtime: java21
  memorySize: 512
  timeout: 10
  region: ${opt:region, 'us-east-1'}
  stage: ${opt:stage, 'dev'}

  environment:
    STAGE: ${self:provider.stage}
    USERS_TABLE: !Ref UsersTable

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: '*'
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:DeleteItem
            - dynamodb:Scan
            - dynamodb:Query
          Resource: !GetAtt UsersTable.Arn

package:
  artifact: build/libs/${self:service}-${self:provider.stage}.jar

functions:
  api:
    handler: com.example.Handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-users-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH

  Outputs:
    ApiUrl:
      Value: !Join ['', ['https://', !Ref ApiGatewayRestApi, '.execute-api.', !Ref 'AWS::Region', '.amazonaws.com/', ${self:provider.stage}]]
      Export:
        Name: ${self:service}-api-url-${self:provider.stage}
```

### Multi-Stage Configuration

```yaml
service: java-lambda-api

provider:
  name: aws
  runtime: java21
  memorySize: ${self:custom.memorySize.${self:provider.stage}}
  timeout: ${self:custom.timeout.${self:provider.stage}}
  region: ${opt:region, 'us-east-1'}
  stage: ${opt:stage, 'dev'}

  environment:
    STAGE: ${self:provider.stage}
    LOG_LEVEL: ${self:custom.logLevel.${self:provider.stage}}

custom:
  memorySize:
    dev: 512
    staging: 1024
    prod: 2048

  timeout:
    dev: 10
    staging: 15
    prod: 30

  logLevel:
    dev: DEBUG
    staging: INFO
    prod: WARN
```

### VPC Configuration

```yaml
provider:
  name: aws
  runtime: java21
  vpc:
    securityGroupIds:
      - !Ref LambdaSecurityGroup
    subnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2

resources:
  Resources:
    LambdaSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupDescription: Lambda Security Group
        VpcId: !Ref VPC
        SecurityGroupEgress:
          - IpProtocol: tcp
            FromPort: 443
            ToPort: 443
            CidrIp: 0.0.0.0/0

    PrivateSubnet1:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        CidrBlock: 10.0.1.0/24
        AvailabilityZone: !Select [0, !GetAZs '']

    PrivateSubnet2:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        CidrBlock: 10.0.2.0/24
        AvailabilityZone: !Select [1, !GetAZs '']
```

### Custom Domain

```yaml
plugins:
  - serverless-domain-manager

custom:
  customDomain:
    domainName: api.example.com
    stage: ${self:provider.stage}
    createRoute53Record: true
    certificateName: '*.example.com'
    endpointType: 'regional'
    securityPolicy: tls_1_2
```

---

## AWS SAM

### Basic Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Java Lambda API with SAM

Globals:
  Function:
    Timeout: 10
    MemorySize: 512
    Runtime: java21
    Architectures:
      - x86_64
    Environment:
      Variables:
        JAVA_TOOL_OPTIONS: -XX:+TieredCompilation -XX:TieredStopAtLevel=1
    Tags:
      Project: MyJavaApi

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Description: Java Lambda API Handler
      AutoPublishAlias: live
      DeploymentPreference:
        Type: Canary10Percent5Minutes
        Alarms:
          - !Ref ErrorsAlarm
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref ApiGateway
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
        - Statement:
            - Effect: Allow
              Action:
                - cloudwatch:PutMetricData
              Resource: '*'

  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub '${AWS::StackName}-api'
      StageName: !Ref Stage
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
        AllowOrigin: "'*'"
      TracingEnabled: true
      MethodSettings:
        - ResourcePath: /*
          HttpMethod: '*'
          LoggingLevel: INFO
          DataTraceEnabled: true
          MetricsEnabled: true

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-users'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: !If [IsProd, true, false]

  ErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-errors'
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref ApiFunction

Conditions:
  IsProd: !Equals [!Ref Stage, prod]

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Stage}/'

  FunctionArn:
    Description: Lambda Function ARN
    Value: !GetAtt ApiFunction.Arn
    Export:
      Name: !Sub '${AWS::StackName}-function-arn'
```

### SAM with Layers

```yaml
Resources:
  # Lambda Layer for common dependencies
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: java-dependencies
      Description: Common Java dependencies
      ContentUri: build/layers/dependencies/
      CompatibleRuntimes:
        - java21
      RetentionPolicy: Retain

  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Layers:
        - !Ref DependenciesLayer
      Environment:
        Variables:
          JAVA_TOOL_OPTIONS: -cp /opt/java/lib/*:lib/*
```

### SAM Local Testing

```yaml
# samconfig.toml
version = 0.1

[default]
[default.global.parameters]
stack_name = java-lambda-api

[default.build.parameters]
cached = true
parallel = true

[default.validate.parameters]
lint = true

[default.deploy.parameters]
capabilities = CAPABILITY_IAM
confirm_changeset = true
resolve_s3 = true
s3_prefix = java-lambda-api

[default.local_start_api.parameters]
warm_containers = EAGER

[default.local_invoke.parameters]
parameter_overrides = "Stage=local"
```

---

## CI/CD Pipeline

### GitHub Actions - Full Pipeline

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '21'
  AWS_REGION: us-east-1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'
          cache: gradle

      - name: Run tests
        run: ./gradlew test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: build/reports/jacoco/test/jacocoTestReport.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      artifact-path: ${{ steps.build.outputs.artifact-path }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'
          cache: gradle

      - name: Build JAR
        id: build
        run: |
          ./gradlew shadowJar
          echo "artifact-path=build/libs/$(ls build/libs/*.jar | head -n 1)" >> $GITHUB_OUTPUT

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: lambda-jar
          path: build/libs/*.jar
          retention-days: 1

  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: development
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: lambda-jar
          path: build/libs/

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy with Serverless
        run: |
          npm install -g serverless
          serverless deploy --stage dev --region $AWS_REGION

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: lambda-jar
          path: build/libs/

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy with SAM
        run: |
          sam build
          sam deploy \
            --stack-name java-api-staging \
            --s3-bucket $DEPLOYMENT_BUCKET \
            --region $AWS_REGION \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Stage=staging \
            --no-confirm-changeset

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: lambda-jar
          path: build/libs/

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to Production
        run: |
          sam deploy \
            --stack-name java-api-prod \
            --s3-bucket $DEPLOYMENT_BUCKET \
            --region $AWS_REGION \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Stage=prod \
            --no-confirm-changeset
```

### GitHub Actions - SAM Only

```yaml
# .github/workflows/sam-pipeline.yml
name: SAM Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/setup-sam@v2
        with:
          use-installer: true

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'
          cache: gradle

      - name: Build application
        run: ./gradlew shadowJar

      - name: SAM Build
        run: sam build

      - name: SAM Deploy
        run: |
          sam deploy \
            --stack-name java-api-${{ github.event.inputs.environment || 'staging' }} \
            --resolve-s3 \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Stage=${{ github.event.inputs.environment || 'staging' }} \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset
```

---

## Provisioned Concurrency

### Serverless Framework

```yaml
functions:
  api:
    handler: com.example.Handler
    provisionedConcurrency: 10
    events:
      - http:
          path: /{proxy+}
          method: ANY

    # Scheduled scaling (optional)
    provisionedConcurrencyScalers:
      - schedule: cron(0 9 * * ? *)
        value: 20
      - schedule: cron(0 18 * * ? *)
        value: 5
```

### SAM Template

```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 10

  # Scheduled scaling with Application Auto Scaling
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 50
      MinCapacity: 5
      ResourceId: !Sub 'function:${ApiFunction}:live'
      RoleARN: !Sub 'arn:aws:iam::${AWS::AccountId}:role/aws-service-role/lambda.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_LambdaConcurrency'
      ScalableDimension: lambda:function:ProvisionedConcurrency
      ServiceNamespace: lambda

  ScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: lambda-provisioned-concurrency-policy
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref ScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 0.7
        PredefinedMetricSpecification:
          PredefinedMetricType: LambdaProvisionedConcurrencyUtilization
```

### Auto Scaling Based on Schedule

```yaml
Resources:
  BusinessHoursScaleUp:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName: !Ref ScalableTarget
      MinSize: 20
      MaxSize: 50
      Recurrence: 0 9 * * MON-FRI
      TimeZone: America/New_York

  BusinessHoursScaleDown:
    Type: AWS::AutoScaling::ScheduledAction
    Properties:
      AutoScalingGroupName: !Ref ScalableTarget
      MinSize: 5
      MaxSize: 50
      Recurrence: 0 18 * * MON-FRI
      TimeZone: America/New_York
```

---

## Monitoring

### CloudWatch Alarms

```yaml
Resources:
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-high-error-rate'
      AlarmDescription: Error rate exceeds 1%
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      Dimensions:
        - Name: FunctionName
          Value: !Ref ApiFunction

  HighDurationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-high-duration'
      AlarmDescription: Average duration exceeds 5 seconds
      MetricName: Duration
      Namespace: AWS/Lambda
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref ApiFunction

  ThrottlingAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-throttling'
      MetricName: Throttles
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref ApiFunction
```

### Custom Metrics

```java
// Emit custom metrics from Lambda
private void emitMetric(String name, double value, String unit) {
    PutMetricDataRequest request = PutMetricDataRequest.builder()
        .namespace("MyApplication")
        .metricData(MetricDatum.builder()
            .metricName(name)
            .value(value)
            .unit(unit)
            .dimensions(
                Dimension.builder().name("Function").value("ApiHandler").build(),
                Dimension.builder().name("Stage").value(System.getenv("STAGE")).build()
            )
            .build())
        .build();

    cloudWatchClient.putMetricData(request);
}

// Usage
emitMetric("ProcessingTime", duration, StandardUnit.MILLISECONDS);
emitMetric("ItemsProcessed", count, StandardUnit.Count);
```

### X-Ray Tracing

```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Tracing: Active
      Environment:
        Variables:
          AWS_XRAY_CONTEXT_MISSING: LOG_ERROR
```

```java
// Add subsegments for detailed tracing
import com.amazonaws.xray.AWSXRay;
import com.amazonaws.xray.entities.Subsegment;

public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
    Subsegment subsegment = AWSXRay.beginSubsegment("ProcessRequest");
    try {
        // Business logic
        subsegment.putAnnotation("userId", userId);
        subsegment.putMetadata("request", Map.of("path", request.getPath()));

        return processRequest(request);
    } catch (Exception e) {
        subsegment.addException(e);
        throw e;
    } finally {
        AWSXRay.endSubsegment();
    }
}
```

### CloudWatch Logs Insights Queries

```sql
-- Find cold starts
fields @timestamp, @message, @duration
| filter @message like /INIT_START/
| stats count() as cold_starts by bin(5m)

-- Average duration by stage
fields @duration, @memorySize
| filter @type = "REPORT"
| stats avg(@duration), max(@duration), min(@duration) by @memorySize

-- Error analysis
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as errors by bin(1h)
| sort by @timestamp desc

-- Performance by endpoint (requires custom logging)
fields @timestamp, @message
| parse @message "path: *, duration: *ms" as path, duration
| stats avg(duration), max(duration), count() by path
| sort by avg(duration) desc
```

---

## Build Optimization

### Gradle Configuration

```groovy
// build.gradle
plugins {
    id 'java'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

// Optimized build task for Lambda deployment packages
task buildZip(type: Zip) {
    from compileJava
    from processResources
    into('lib') {
        from configurations.runtimeClasspath
    }
    archiveFileName = "${project.name}-${project.version}.zip"
}

// Shadow JAR with minimized dependencies
shadowJar {
    archiveClassifier = ''
    mergeServiceFiles()

    // Exclude unnecessary files to reduce JAR size
    exclude 'META-INF/*.SF'
    exclude 'META-INF/*.DSA'
    exclude 'META-INF/*.RSA'
    exclude 'META-INF/LICENSE*'
    exclude 'META-INF/NOTICE*'

    // Minimize to only include used classes
    minimize()
}

dependencies {
    // AWS SDK v2 - include only needed modules
    implementation 'software.amazon.awssdk:dynamodb:2.25.0'
    implementation 'software.amazon.awssdk:s3:2.25.0'
    implementation 'software.amazon.awssdk:lambda:2.25.0'

    // Avoid entire AWS SDK - do NOT use:
    // implementation 'software.amazon.awssdk:aws-sdk-java:2.25.0'

    // Prefer lightweight DI frameworks over Spring
    implementation 'com.google.dagger:dagger:2.51'
    annotationProcessor 'com.google.dagger:dagger-compiler:2.51'

    // Or use Guice if needed
    // implementation 'com.google.inject:guice:7.0.0'

    // Lambda runtime
    implementation 'com.amazonaws:aws-lambda-java-core:1.2.3'
    implementation 'com.amazonaws:aws-lambda-java-events:3.11.4'

    // Logging (lightweight)
    implementation 'org.slf4j:slf4j-simple:2.0.12'
}
```

### Maven Configuration

```xml
<!-- pom.xml -->
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.12.1</version>
            <configuration>
                <source>21</source>
                <target>21</target>
            </configuration>
        </plugin>

        <!-- Maven Shade Plugin for creating uber JAR -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-shade-plugin</artifactId>
            <version>3.5.1</version>
            <configuration>
                <createDependencyReducedPom>false</createDependencyReducedPom>
                <filters>
                    <filter>
                        <artifact>*:*</artifact>
                        <excludes>
                            <exclude>META-INF/*.SF</exclude>
                            <exclude>META-INF/*.DSA</exclude>
                            <exclude>META-INF/*.RSA</exclude>
                            <exclude>META-INF/LICENSE*</exclude>
                            <exclude>META-INF/NOTICE*</exclude>
                        </excludes>
                    </filter>
                </filters>
            </configuration>
            <executions>
                <execution>
                    <phase>package</phase>
                    <goals>
                        <goal>shade</goal>
                    </goals>
                    <configuration>
                        <minimizeJar>true</minimizeJar>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>

<dependencies>
    <!-- AWS SDK v2 - selective modules only -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>dynamodb</artifactId>
        <version>2.25.0</version>
    </dependency>
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>s3</artifactId>
        <version>2.25.0</version>
    </dependency>

    <!-- Lambda runtime -->
    <dependency>
        <groupId>com.amazonaws</groupId>
        <artifactId>aws-lambda-java-core</artifactId>
        <version>1.2.3</version>
    </dependency>
</dependencies>
```

### Handler Separation Pattern

```java
// Separate Lambda handler from core business logic
public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private final OrderService orderService;

    // Constructor for Lambda runtime (with dependency injection)
    public LambdaHandler() {
        this.orderService = DaggerOrderComponent.create().orderService();
    }

    // Constructor for testing
    public LambdaHandler(OrderService orderService) {
        this.orderService = orderService;
    }

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        // Delegate to core logic
        return orderService.processOrder(request);
    }
}

// Core business logic separate from Lambda infrastructure
public class OrderService {
    private final OrderRepository repository;
    private final NotificationService notificationService;

    @Inject
    public OrderService(OrderRepository repository, NotificationService notificationService) {
        this.repository = repository;
        this.notificationService = notificationService;
    }

    public APIGatewayProxyResponseEvent processOrder(APIGatewayProxyRequestEvent request) {
        // Business logic here - can be tested independently
    }
}
```

---

## Package Optimization

### Lambda Layers for Java Dependencies

```yaml
# SAM template with Lambda Layers
Resources:
  # Shared dependencies layer
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: java-common-dependencies
      Description: Common Java dependencies for Lambda functions
      ContentUri: build/layers/dependencies/
      CompatibleRuntimes:
        - java21
      RetentionPolicy: Retain

  # Function using the layer
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Layers:
        - !Ref DependenciesLayer
      Environment:
        Variables:
          JAVA_TOOL_OPTIONS: -cp /opt/java/lib/*:lib/*
```

```groovy
// build.gradle - Create layer structure
task buildLayer(type: Copy) {
    from configurations.runtimeClasspath
    into "build/layers/dependencies/java/lib"

    // Exclude AWS SDK provided by Lambda runtime
    exclude 'aws-lambda-java-core*.jar'
    exclude 'aws-lambda-java-events*.jar'
}

// Build minimal function JAR (business logic only)
task buildFunctionJar(type: Jar) {
    from sourceSets.main.output
    exclude '**/lib/**'
    archiveFileName = "function.jar"
}
```

### JAR Size Reduction Techniques

```groovy
// Exclude unnecessary dependencies
dependencies {
    implementation('com.fasterxml.jackson.core:jackson-databind:2.16.0') {
        // Exclude unused Jackson modules
        exclude group: 'com.fasterxml.jackson.module'
    }

    // Use ProGuard for aggressive optimization (advanced)
    // buildscript { dependencies { classpath 'com.guardsquare:proguard-gradle:7.4.0' } }
}

// Gradle configuration for minimal JAR
jar {
    enabled = false  // Disable standard JAR, use shadow only
}

shadowJar {
    // Remove unused classes
    minimize {
        exclude(dependency('org.slf4j:.*:.*'))
    }

    // Relocate packages to avoid conflicts
    relocate 'com.fasterxml.jackson', 'shaded.com.fasterxml.jackson'
}
```

### Maven Dependency Copy for Layer

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-dependency-plugin</artifactId>
    <version>3.6.1</version>
    <executions>
        <execution>
            <id>copy-dependencies</id>
            <phase>package</phase>
            <goals>
                <goal>copy-dependencies</goal>
            </goals>
            <configuration>
                <outputDirectory>${project.build.directory}/layers/java/lib</outputDirectory>
                <includeScope>runtime</includeScope>
                <excludeArtifactIds>aws-lambda-java-core,aws-lambda-java-events</excludeArtifactIds>
            </configuration>
        </execution>
    </executions>
</plugin>
```

---

## Performance Tuning

### JVM Options for Lambda

```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java21
      Environment:
        Variables:
          # Optimized JVM flags for Lambda cold starts
          JAVA_TOOL_OPTIONS: >
            -XX:+TieredCompilation
            -XX:TieredStopAtLevel=1
            -XX:+UseSerialGC
            -XX:MaxRAMPercentage=75.0
            -XX:InitialRAMPercentage=50.0
```

**JVM Option Explanations:**

| Option | Purpose | Impact |
|--------|---------|--------|
| `-XX:+TieredCompilation` | Enable tiered compilation | Faster startup |
| `-XX:TieredStopAtLevel=1` | Stop at C1 compiler only | Reduced compilation time |
| `-XX:+UseSerialGC` | Use single-threaded GC | Lower memory overhead |
| `-XX:MaxRAMPercentage=75.0` | Limit heap to 75% of container memory | Prevent OOM |

### Memory Configuration Guidance

```yaml
# Memory allocation vs vCPU allocation
# 1769MB = 1 vCPU (linear scaling below this threshold)

Resources:
  LowMemoryFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 512
      # Suitable for: Simple CRUD, low throughput

  BalancedFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1024
      # Good balance of performance and cost

  HighPerformanceFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1769
      # 1 full vCPU - optimal for CPU-intensive tasks

  MaximumPerformanceFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 3008
      # 2 vCPUs - for compute-intensive operations
```

### Cold Start Optimization

```java
public class OptimizedHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Initialize heavy resources statically (during init phase)
    private static final DynamoDbClient dynamoDbClient = DynamoDbClient.builder()
        .httpClientBuilder(UrlConnectionHttpClient.builder())  // Lightweight HTTP client
        .build();

    private static final ObjectMapper objectMapper = new ObjectMapper()
        .registerModule(new JavaTimeModule());

    // Initialize during first invocation if needed
    private final OrderRepository orderRepository;

    public OptimizedHandler() {
        // This runs during init phase (not counted in billing)
        this.orderRepository = new OrderRepository(dynamoDbClient);
    }

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        // Handler execution - reuse initialized resources
        return processRequest(request);
    }
}
```

### Connection Pool Settings

```java
// HTTP client configuration for Lambda
public class HttpClientConfig {

    public static HttpClient createOptimizedClient() {
        return HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .version(HttpClient.Version.HTTP_2)
            .build();
    }
}

// Database connection pooling (if using RDS Proxy or direct connections)
public class DatabaseConfig {

    public static HikariDataSource createDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(System.getenv("DB_URL"));
        config.setUsername(System.getenv("DB_USER"));
        config.setPassword(System.getenv("DB_PASSWORD"));

        // Lambda-optimized pool settings
        config.setMaximumPoolSize(2);  // Keep minimal for Lambda
        config.setMinimumIdle(0);      // Don't maintain idle connections
        config.setIdleTimeout(10000);  // 10 second idle timeout
        config.setConnectionTimeout(5000);
        config.setMaxLifetime(300000); // 5 minutes max lifetime

        return new HikariDataSource(config);
    }
}
```

---

## Rollback Strategy

### AWS SAM with CodeDeploy Integration

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Runtime: java21
      AutoPublishAlias: live  # Required for traffic shifting

      # Deployment preferences with automatic rollback
      DeploymentPreference:
        Type: Canary10Percent5Minutes
        Alarms:
          - !Ref ErrorRateAlarm
          - !Ref LatencyAlarm
        Hooks:
          PreTraffic: !Ref PreTrafficHookFunction
          PostTraffic: !Ref PostTrafficHookFunction

  # Pre-traffic hook for validation
  PreTrafficHookFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/hooks.jar
      Handler: com.example.hooks.PreTrafficHook
      Runtime: java21
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - codedeploy:PutLifecycleEventHookExecutionStatus
              Resource: '*'

  # Post-traffic hook for verification
  PostTrafficHookFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/hooks.jar
      Handler: com.example.hooks.PostTrafficHook
      Runtime: java21
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - codedeploy:PutLifecycleEventHookExecutionStatus
              Resource: '*'

  # Alarms for automatic rollback triggers
  ErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-error-rate'
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref ApiFunction

  LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${AWS::StackName}-latency'
      MetricName: Duration
      Namespace: AWS/Lambda
      Statistic: Average
      Period: 60
      EvaluationPeriods: 2
      Threshold: 3000
      ComparisonOperator: GreaterThanThreshold
```

### Deployment Types

```yaml
# Canary deployments - shift traffic gradually
DeploymentPreference:
  Type: Canary10Percent5Minutes  # 10% for 5 minutes, then 100%
  # Other options:
  # - Canary10Percent30Minutes
  # - Canary10Percent5Minutes
  # - Canary10Percent10Minutes
  # - Canary10Percent15Minutes

# Linear deployments - shift traffic in increments
DeploymentPreference:
  Type: Linear10PercentEvery1Minute  # 10% per minute until 100%
  # Other options:
  # - Linear10PercentEvery2Minutes
  # - Linear10PercentEvery3Minutes
  # - Linear10PercentEvery10Minutes

# All-at-once (no rollback capability)
DeploymentPreference:
  Type: AllAtOnce
```

### Pre/Post Traffic Hook Implementation

```java
// Pre-traffic hook for smoke tests
public class PreTrafficHook implements RequestHandler<Map<String, Object>, String> {

    private final CodeDeployClient codeDeployClient;
    private final HttpClient httpClient;

    public PreTrafficHook() {
        this.codeDeployClient = CodeDeployClient.create();
        this.httpClient = HttpClient.newHttpClient();
    }

    @Override
    public String handleRequest(Map<String, Object> event, Context context) {
        String deploymentId = (String) event.get("DeploymentId");
        String lifecycleEventHookExecutionId = (String) event.get("LifecycleEventHookExecutionId");

        try {
            // Run smoke tests against the new version
            boolean testsPassed = runSmokeTests();

            // Report status to CodeDeploy
            PutLifecycleEventHookExecutionStatusRequest statusRequest =
                PutLifecycleEventHookExecutionStatusRequest.builder()
                    .deploymentId(deploymentId)
                    .lifecycleEventHookExecutionId(lifecycleEventHookExecutionId)
                    .status(testsPassed ? LifecycleEventStatus.SUCCEEDED : LifecycleEventStatus.FAILED)
                    .build();

            codeDeployClient.putLifecycleEventHookExecutionStatus(statusRequest);

            return testsPassed ? "Success" : "Failure";

        } catch (Exception e) {
            context.getLogger().log("Pre-traffic hook failed: " + e.getMessage());

            // Report failure to trigger rollback
            codeDeployClient.putLifecycleEventHookExecutionStatus(
                PutLifecycleEventHookExecutionStatusRequest.builder()
                    .deploymentId(deploymentId)
                    .lifecycleEventHookExecutionId(lifecycleEventHookExecutionId)
                    .status(LifecycleEventStatus.FAILED)
                    .build()
            );

            throw new RuntimeException(e);
        }
    }

    private boolean runSmokeTests() {
        // Implement smoke tests (health check, basic functionality)
        return true;
    }
}
```

---

## Security Best Practices

### IAM Least Privilege

```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Policies:
        # Use managed policies for common patterns
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

        # Custom least-privilege policy
        - Statement:
            - Effect: Allow
              Action:
                - s3:GetObject
                - s3:PutObject
              Resource:
                - !Sub 'arn:aws:s3:::${BucketName}/uploads/*'
              Condition:
                StringEquals:
                  s3:x-amz-acl: bucket-owner-full-control

        # Explicit deny for sensitive operations
            - Effect: Deny
              Action:
                - s3:DeleteBucket
                - dynamodb:DeleteTable
              Resource: '*'
```

### VPC Configuration

```yaml
Resources:
  VpcFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      VpcConfig:
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
      # VPC functions require NAT Gateway for internet access
      # or VPC endpoints for AWS services

  # Security group with minimal access
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Lambda security group
      VpcId: !Ref VPC
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS to AWS services
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          DestinationSecurityGroupId: !Ref RdsSecurityGroup
          Description: PostgreSQL to RDS

  # VPC Endpoints for AWS services (avoid NAT Gateway costs)
  S3VpcEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub 'com.amazonaws.${AWS::Region}.s3'
      VpcEndpointType: Gateway
      RouteTableIds:
        - !Ref PrivateRouteTable

  DynamoDbVpcEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPC
      ServiceName: !Sub 'com.amazonaws.${AWS::Region}.dynamodb'
      VpcEndpointType: Gateway
      RouteTableIds:
        - !Ref PrivateRouteTable
```

### Secrets Manager and SSM Parameter Store

```yaml
Resources:
  SecureFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Environment:
        Variables:
          # Reference secrets by ARN (not value)
          DB_SECRET_ARN: !Ref DatabaseSecret
          API_KEY_PARAM: !Ref ApiKeyParameter
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - secretsmanager:GetSecretValue
              Resource: !Ref DatabaseSecret
            - Effect: Allow
              Action:
                - ssm:GetParameter
              Resource: !Ref ApiKeyParameter

  # Secrets Manager for database credentials
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '/${AWS::StackName}/database-credentials'
      Description: RDS database credentials
      GenerateSecretString:
        SecretStringTemplate: '{"username": "dbadmin"}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\\'
      KmsKeyId: !Ref SecretsKmsKey

  # SSM Parameter Store for configuration
  ApiKeyParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Name: !Sub '/${AWS::StackName}/api-key'
      Type: SecureString
      Value: placeholder-replace-manually
      Description: External API key
      Tier: Standard

  # KMS key for encryption
  SecretsKmsKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for Lambda secrets
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
```

```java
// Retrieve secrets in Lambda with caching
public class SecretCache {

    private final SecretsManagerClient secretsClient;
    private final Map<String, String> cache = new ConcurrentHashMap<>();
    private final long cacheTtlMs = 300000; // 5 minutes

    public String getSecret(String secretArn) {
        return cache.computeIfAbsent(secretArn, arn -> {
            GetSecretValueRequest request = GetSecretValueRequest.builder()
                .secretId(arn)
                .build();

            GetSecretValueResponse response = secretsClient.getSecretValue(request);
            return response.secretString();
        });
    }

    // Parse JSON secrets
    public DatabaseCredentials getDatabaseCredentials(String secretArn) {
        String secretString = getSecret(secretArn);
        return new ObjectMapper().readValue(secretString, DatabaseCredentials.class);
    }
}
```

### Resource-Based Policies

```yaml
Resources:
  InternalFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler

  # Explicit resource policy for cross-account or service access
  FunctionResourcePolicy:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref InternalFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub 'arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGateway}/*'

  # Service-specific invocation permission
  S3InvokePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref S3ProcessorFunction
      Action: lambda:InvokeFunction
      Principal: s3.amazonaws.com
      SourceArn: !Sub 'arn:aws:s3:::${BucketName}'
      SourceAccount: !Ref AWS::AccountId
```

---

## Cost Optimization

### Graviton2 (ARM64) Support

```yaml
Resources:
  ArmFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: build/libs/function.jar
      Handler: com.example.Handler
      Runtime: java21
      Architectures:
        - arm64  # Graviton2 - up to 34% better price-performance

  # Build configuration for ARM64
  # Gradle: No changes needed - Java bytecode is architecture-independent
  # But native dependencies must be ARM64 compatible
```

```groovy
// build.gradle - Multi-architecture build support
plugins {
    id 'java'
}

dependencies {
    // AWS SDK CRT client for ARM64 optimization
    implementation 'software.amazon.awssdk:aws-crt-client:2.25.0'

    // Ensure all native dependencies have ARM64 support
    implementation 'io.netty:netty-transport-native-epoll:4.1.107.Final:linux-aarch_64'
}
```

### Memory Size Tuning

```yaml
# Find optimal memory/price ratio using AWS Lambda Power Tuning
Resources:
  TunedFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1769  # Sweet spot: 1 vCPU, good performance/cost ratio
      # Test different values: 512, 1024, 1769, 3008

  # Use Lambda Power Tuning tool to find optimal setting
  # https://github.com/alexcasalboni/aws-lambda-power-tuning
```

### Provisioned Concurrency Cost Analysis

```yaml
# Cost comparison: On-demand vs Provisioned Concurrency

# On-demand (pay per invocation):
# - $0.20 per 1M requests
# - $0.0000166667 per GB-second
# - Cold starts on scale-up

# Provisioned Concurrency (predictable performance):
# - $0.20 per 1M requests (same)
# - $0.000004646 per GB-second (lower compute cost)
# - $0.000004646 per GB-second provisioned (base cost)

Resources:
  # Use for predictable, latency-sensitive workloads
  HighTrafficFunction:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1024
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 10

  # Scheduled scaling to optimize cost
  ScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MinCapacity: 2    # Minimum during off-hours
      MaxCapacity: 50   # Maximum during peak
```

### Lambda Layers for Shared Dependencies

```yaml
# Share common dependencies across functions to reduce deployment size
Resources:
  SharedLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: shared-java-deps
      ContentUri: layers/shared/
      CompatibleRuntimes:
        - java21

  FunctionA:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: function-a/build/distributions/function-a.zip
      Handler: com.example.FunctionAHandler
      Layers:
        - !Ref SharedLayer
      # Smaller deployment package = faster cold starts

  FunctionB:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: function-b/build/distributions/function-b.zip
      Handler: com.example.FunctionBHandler
      Layers:
        - !Ref SharedLayer
      # Reuses same layer, no duplication
```

---

## SAM vs Serverless Framework

| Feature | SAM | Serverless Framework |
|---------|-----|---------------------|
| Native AWS | Yes - AWS-maintained | No - Third-party |
| Build system | Gradle/Maven native | Plugin-based (Gradle plugin available) |
| Local testing | SAM CLI (local invoke, local API) | serverless-offline |
| Java support | Native first-class | Via plugins |
| Deployment | CloudFormation-based | CloudFormation-based |
| Syntax | YAML/JSON | YAML |
| CI/CD integration | Native GitHub Actions, CodePipeline | Extensive plugin ecosystem |
| Rollback | Built-in CodeDeploy integration | Manual or custom scripts |
| IDE support | AWS Toolkit (IntelliJ, VS Code) | Limited |
| Debugging | Local debugging with breakpoints | Limited |
| Velocity macros | Supported | Not applicable |

### When to Choose SAM

- Native AWS tooling and support
- Deep Java integration with build tools
- Built-in safe deployments with rollback
- Local testing with SAM CLI
- AWS IDE toolkit integration

### When to Choose Serverless Framework

- Multi-cloud requirements (Azure, GCP)
- Large plugin ecosystem needed
- Team familiar with Node.js tooling
- Complex event source configurations
- Non-AWS resource management

---

## Deployment Commands

### Serverless

```bash
# Deploy to specific stage
serverless deploy --stage prod --region us-east-1

# Deploy single function
serverless deploy function -f api

# Package without deploying
serverless package --stage prod

# View logs
serverless logs -f api --tail

# Remove stack
serverless remove --stage prod
```

### SAM

```bash
# Build
sam build

# Local test
sam local invoke ApiFunction -e events/test.json
sam local start-api

# Deploy
sam deploy --guided
sam deploy --no-confirm-changeset

# View logs
sam logs -n ApiFunction --tail

# Delete stack
sam delete --stack-name my-stack
```

---

## Environment Variables Management

### SSM Parameter Store

```yaml
provider:
  environment:
    DATABASE_URL: ${ssm:/my-app/${self:provider.stage}/database-url}
    API_KEY: ${ssm:/my-app/${self:provider.stage}/api-key~true}  # SecureString
```

### Secrets Manager

```yaml
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          DB_SECRET_ARN: !Ref DatabaseSecret
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - secretsmanager:GetSecretValue
              Resource: !Ref DatabaseSecret

  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '/${AWS::StackName}/database-credentials'
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: password
        PasswordLength: 16
```

```java
// Retrieve secret in Lambda
private String getSecret(String secretName) {
    GetSecretValueRequest request = GetSecretValueRequest.builder()
        .secretId(secretName)
        .build();

    GetSecretValueResponse response = secretsManager.getSecretValue(request);
    return response.secretString();
}
```
