# Serverless Deployment for Python Lambda

Deployment patterns for Python Lambda functions using Serverless Framework, AWS SAM, and CI/CD pipelines.

## Serverless Framework

### Basic Configuration

```yaml
# serverless.yml
service: my-python-api

provider:
  name: aws
  runtime: python3.12  # or python3.11
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}
  memorySize: 256
  timeout: 10

  # Environment variables for all functions
  environment:
    STAGE: ${self:provider.stage}
    REGION: ${self:provider.region}
    TABLE_NAME: ${self:service}-table-${self:provider.stage}

  # IAM permissions
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: '*'

functions:
  api:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

### Advanced Configuration

```yaml
# serverless.yml
service: my-python-api

provider:
  name: aws
  runtime: python3.12  # or python3.11
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}
  memorySize: 256
  timeout: 10
  logRetentionInDays: 14
  versionFunctions: false

  # VPC configuration
  vpc:
    securityGroupIds:
      - sg-xxxxxxxx
    subnetIds:
      - subnet-xxxxxxxx
      - subnet-yyyyyyyy

  # Environment variables
  environment:
    STAGE: ${self:provider.stage}
    REGION: ${self:provider.region}
    TABLE_NAME: !Ref UsersTable
    BUCKET_NAME: !Ref AssetsBucket

  # IAM role statements
  iam:
    role:
      name: ${self:service}-${self:provider.stage}-role
      statements:
        # DynamoDB permissions
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
            - dynamodb:Query
            - dynamodb:Scan
          Resource:
            - !GetAtt UsersTable.Arn
            - !Sub "${UsersTable.Arn}/index/*"

        # S3 permissions
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:PutObject
            - s3:DeleteObject
          Resource:
            - !Sub "${AssetsBucket.Arn}/*"

        # CloudWatch permissions
        - Effect: Allow
          Action:
            - cloudwatch:PutMetricData
          Resource: '*'

  # API Gateway settings
  apiGateway:
    binaryMediaTypes:
      - 'multipart/form-data'
    minimumCompressionSize: 1024

plugins:
  - serverless-python-requirements
  - serverless-offline

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
    layer: false

  serverless-offline:
    httpPort: 3000
    lambdaPort: 3002

package:
  individually: false
  patterns:
    - '!.git/**'
    - '!.gitignore'
    - '!.DS_Store'
    - '!node_modules/**'
    - '!.pytest_cache/**'
    - '!tests/**'
    - '!.env'
    - '!.venv/**'
    - '!venv/**'
    - '!__pycache__/**'
    - '!.mypy_cache/**'

functions:
  api:
    handler: lambda_function.lambda_handler
    description: Main API handler
    memorySize: 512
    timeout: 30
    reservedConcurrency: 100
    provisionedConcurrency: 10
    environment:
      FUNCTION_NAME: api
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors:
            origin: '*'
            headers:
              - Content-Type
              - Authorization
              - X-Amz-Date
              - X-Api-Key
              - X-Amz-Security-Token
            allowCredentials: true

  scheduled-task:
    handler: handlers.scheduled_task
    description: Daily scheduled task
    events:
      - schedule: rate(1 day)

  sqs-processor:
    handler: handlers.process_sqs_message
    description: SQS message processor
    reservedConcurrency: 50
    events:
      - sqs:
          arn: !GetAtt MessageQueue.Arn
          batchSize: 10
          maximumBatchingWindowInSeconds: 5

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
          - AttributeName: email
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        GlobalSecondaryIndexes:
          - IndexName: email-index
            KeySchema:
              - AttributeName: email
                KeyType: HASH
            Projection:
              ProjectionType: ALL

    AssetsBucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:service}-assets-${self:provider.stage}
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true

    MessageQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-messages-${self:provider.stage}
        VisibilityTimeout: 300

  Outputs:
    ApiGatewayRestApiId:
      Value: !Ref ApiGatewayRestApi
      Export:
        Name: ${self:service}-${self:provider.stage}-restApiId

    ApiGatewayRestApiRootResourceId:
      Value: !GetAtt ApiGatewayRestApi.RootResourceId
      Export:
        Name: ${self:service}-${self:provider.stage}-rootResourceId
```

### Commands

```bash
# Install plugins
npm install

# Deploy to dev
serverless deploy

# Deploy to specific stage
serverless deploy --stage prod

# Deploy specific function
serverless deploy function -f api

# Invoke locally
serverless invoke local -f api -p event.json

# View logs
serverless logs -f api --tail

# Remove stack
serverless remove
```

## AWS SAM

### Basic Template

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Python Lambda API

Globals:
  Function:
    Timeout: 10
    MemorySize: 256
    Runtime: python3.12  # or python3.11
    Architectures:
      - x86_64
    Environment:
      Variables:
        LOG_LEVEL: INFO

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Conditions:
  IsProd: !Equals [!Ref Stage, prod]

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: lambda_function.lambda_handler
      Description: Main API handler
      MemorySize: 512
      Timeout: 30
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        !If [IsProd, {ProvisionedConcurrentExecutions: 10}, !Ref "AWS::NoValue"]
      Environment:
        Variables:
          TABLE_NAME: !Ref UsersTable
          STAGE: !Ref Stage
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref ApiGatewayApi
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  ApiGatewayApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Stage
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
        MaxAge: "'600'"

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-users"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ApiGatewayApi}.execute-api.${AWS::Region}.amazonaws.com/${Stage}/"

  ApiFunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt ApiFunction.Arn
```

### SAM with Lambda Layers

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 10
    Runtime: python3.12  # or python3.11
    Layers:
      - !Ref DependenciesLayer

Resources:
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: python-dependencies
      Description: Common Python dependencies
      ContentUri: dependencies/
      CompatibleRuntimes:
        - python3.12
        - python3.10
      RetentionPolicy: Retain
    Metadata:
      BuildMethod: python3.12

  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.lambda_handler
      Environment:
        Variables:
          TABLE_NAME: !Ref UsersTable
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

### SAM Commands

```bash
# Build the application
sam build

# Build with specific runtime
sam build --use-container

# Local invoke
sam local invoke ApiFunction -e events/api.json

# Local API server
sam local start-api

# Validate template
sam validate

# Deploy (guided)
sam deploy --guided

# Deploy (CI/CD)
sam deploy \
  --stack-name my-stack \
  --s3-bucket my-deployment-bucket \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides Stage=prod

# Delete stack
sam delete
```

## AWS Chalice Deployment

### Chalice Config

```json
{
  "version": "2.0",
  "app_name": "my-api",
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "DEBUG": "true"
      },
      "lambda_functions": {
        "api_handler": {
          "lambda_timeout": 10,
          "lambda_memory_size": 256,
          "tags": {
            "Environment": "dev"
          }
        }
      }
    },
    "prod": {
      "api_gateway_stage": "api",
      "environment_variables": {
        "DEBUG": "false"
      },
      "lambda_functions": {
        "api_handler": {
          "lambda_timeout": 30,
          "lambda_memory_size": 512,
          "reserved_concurrent_executions": 100,
          "provisioned_concurrency": 10
        }
      },
      "tags": {
        "Environment": "prod"
      }
    }
  }
}
```

### Chalice Deployment Commands

```bash
# Deploy to dev
chalice deploy

# Deploy to prod
chalice deploy --stage prod

# Generate CloudFormation template
chalice package --stage prod ./out

# Deploy with CloudFormation
cd out
aws cloudformation deploy \
  --template-file sam.json \
  --stack-name my-api-prod \
  --capabilities CAPABILITY_IAM
```

## CI/CD Pipelines

### GitHub Actions - SAM

```yaml
# .github/workflows/deploy.yml
name: Deploy Lambda

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          flake8 .
          black --check .
          isort --check-only .

      - name: Run type checking
        run: mypy .

      - name: Run tests
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}

  deploy-dev:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: dev
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install SAM CLI
        run: |
          pip install aws-sam-cli

      - name: Build
        run: sam build --use-container

      - name: Deploy to Dev
        run: |
          sam deploy \
            --stack-name my-api-dev \
            --s3-bucket ${{ secrets.DEPLOYMENT_BUCKET }} \
            --region ${{ env.AWS_REGION }} \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Stage=dev \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset

  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: prod
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install SAM CLI
        run: |
          pip install aws-sam-cli

      - name: Build
        run: sam build --use-container

      - name: Deploy to Prod
        run: |
          sam deploy \
            --stack-name my-api-prod \
            --s3-bucket ${{ secrets.DEPLOYMENT_BUCKET }} \
            --region ${{ env.AWS_REGION }} \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Stage=prod \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset
```

### GitHub Actions - Serverless Framework

```yaml
# .github/workflows/deploy-serverless.yml
name: Deploy with Serverless

on:
  push:
    branches: [main]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest

      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Serverless
        run: npm install -g serverless

      - name: Install plugins
        run: npm install

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to Dev
        if: github.ref != 'refs/heads/main'
        run: serverless deploy --stage dev

      - name: Deploy to Prod
        if: github.ref == 'refs/heads/main'
        run: serverless deploy --stage prod
```

## Deployment Best Practices

### Stages and Environments

```yaml
# serverless.yml
provider:
  stage: ${opt:stage, 'dev'}

  environment:
    STAGE: ${self:provider.stage}
    LOG_LEVEL: ${self:custom.logLevel.${self:provider.stage}}

custom:
  logLevel:
    dev: DEBUG
    staging: INFO
    prod: WARN
```

### Secrets Management

```yaml
# serverless.yml
provider:
  environment:
    DATABASE_URL: ${ssm:/${self:service}/${self:provider.stage}/database-url}
    API_KEY: ${ssm:/${self:service}/${self:provider.stage}/api-key~true}  # SecureString
```

### Rollback Strategy

```yaml
# serverless.yml
provider:
  versionFunctions: true
  deploymentSettings:
    alias: live
    type: AllAtOnce
    # For canary deployment:
    # type: Canary10Percent5Minutes
```

### Monitoring and Alarms

```yaml
# serverless.yml
resources:
  Resources:
    ErrorAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: ${self:service}-${self:provider.stage}-errors
        MetricName: Errors
        Namespace: AWS/Lambda
        Statistic: Sum
        Period: 60
        EvaluationPeriods: 1
        Threshold: 1
        ComparisonOperator: GreaterThanOrEqualToThreshold
        Dimensions:
          - Name: FunctionName
            Value: ${self:service}-${self:provider.stage}-api
```

## Comparison

| Feature | Serverless Framework | AWS SAM | AWS Chalice |
|---------|---------------------|---------|-------------|
| Ease of use | Medium | Medium | High |
| Multi-cloud | Yes | No | No |
| Local testing | Yes (offline) | Yes (local) | Yes (local) |
| Plugin ecosystem | Extensive | Limited | Minimal |
| AWS-native | No | Yes | Yes |
| Infrastructure as Code | CloudFormation | CloudFormation | CloudFormation |
| Best for | Complex setups | AWS-native | Python APIs |
