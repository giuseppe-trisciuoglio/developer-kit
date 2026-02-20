# Serverless Deployment Reference

Complete deployment patterns for PHP Lambda functions using Serverless Framework and AWS SAM.

## Table of Contents

1. [Serverless Framework](#serverless-framework)
2. [AWS SAM](#aws-sam)
3. [CI/CD Pipelines](#cicd-pipelines)
4. [Multi-Stage Deployments](#multi-stage-deployments)
5. [Custom Domains](#custom-domains)

---

## Serverless Framework

### Basic Configuration

```yaml
# serverless.yml
service: php-lambda-api

provider:
  name: aws
  runtime: php-82
  stage: ${opt:stage, 'dev'}
  region: ${opt:region, 'us-east-1'}
  memorySize: 512
  timeout: 20
  environment:
    APP_ENV: ${self:provider.stage}
    AWS_REGION: ${self:provider.region}

  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource: '*'

functions:
  api:
    handler: public/index.php
    description: PHP Lambda API
    events:
      - httpApi: '*'

plugins:
  - ./vendor/bref/bref
```

### Environment-Specific Settings

```yaml
# serverless.yml
custom:
  stage: ${opt:stage, 'dev'}

  # Development settings
  dev:
    memorySize: 256
    timeout: 10
    provisioned: 0

  # Production settings
  prod:
    memorySize: 1024
    timeout: 30
    provisioned: 5

provider:
  environment:
    STAGE: ${self:custom.stage}

functions:
  api:
    handler: public/index.php
    memorySize: ${self:custom.${self:custom.stage}.memorySize}
    timeout: ${self:custom.${self:custom.stage}.timeout}
    provisionedConcurrency: ${self:custom.${self:custom.stage}.provisioned}
```

### Multiple Functions

```yaml
functions:
  # API function
  api:
    handler: public/index.php
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY

  # Background processing
  process:
    handler: functions/process.php
    timeout: 300
    events:
      - sqs:
          arn: !GetAtt MyQueue.Arn

  # Scheduled task
  cleanup:
    handler: functions/cleanup.php
    timeout: 900
    events:
      - schedule: cron(0 3 * * ? *)
```

### Layers

```yaml
# serverless.yml
package:
  layers:
    - arn:aws:lambda:us-east-1:123456789012:layer:php-extensions:1

functions:
  api:
    handler: public/index.php
    layers:
      - arn:aws:lambda:us-east-1:123456789012:layer:php-extensions:1
```

---

## AWS SAM

### Basic Template

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: PHP Lambda API

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Globals:
  Function:
    Runtime: php-82
    Timeout: 20
    MemorySize: 512
    Environment:
      Variables:
        APP_ENV: !Ref Stage

Resources:
  PhpFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: public/indexphp
      Events:
        Api:
          Type: HttpApi
          Properties:
            ApiId: !Ref ApiGateway
            Path: /{proxy+}
            Method: ANY
        RootApi:
          Type: HttpApi
          Properties:
            ApiId: !Ref ApiGateway
            Path: /
            Method: ANY

  ApiGateway:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      ProtocolType: HTTP
      StageName: !Ref Stage

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub users-${Stage}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

Outputs:
  ApiUrl:
    Description: API URL
    Value: !Sub https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Stage}
```

### SAM CLI Commands

```bash
# Build the function
sam build

# Deploy
sam deploy --guided

# Local testing
sam local start-api
```

---

## CI/CD Pipelines

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy PHP Lambda

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'

      - name: Install dependencies
        run: composer install --no-interaction

      - name: Run tests
        run: vendor/bin/phpunit

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'

      - name: Install Serverless
        run: npm install -g serverless

      - name: Install dependencies
        run: composer install --no-dev --optimize-autoloader

      - name: Deploy to AWS
        run: vendor/bin/bref deploy --stage prod
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test:
  stage: test
  image: php:8.2-cli
  script:
    - composer install
    - vendor/bin/phpunit

deploy:
  stage: deploy
  image: php:8.2-cli
  script:
    - npm install -g serverless
    - composer install --no-dev
    - vendor/bin/bref deploy --stage $CI_ENVIRONMENT_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
  only:
    - develop
  except:
    - main

deploy-prod:
  stage: deploy
  image: php:8.2-cli
  script:
    - npm install -g serverless
    - composer install --no-dev
    - vendor/bin/bref deploy --stage prod
  environment:
    name: production
  only:
    - main
```

### AWS CodePipeline

```yaml
# buildspec.yml
version: 0.2

phases:
  install:
    runtime-versions:
      php: 8.2
    commands:
      - composer install --no-dev --optimize-autoloader

  build:
    commands:
      - echo "Building..."

  post_build:
    commands:
      - vendor/bin/bref deploy --stage ${STAGE}
        env:
          AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
          AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
```

---

## Multi-Stage Deployments

### Environment Configuration

```yaml
# serverless.yml
custom:
  environments:
    dev:
      domain: dev-api.example.com
      stage: dev
    staging:
      domain: staging-api.example.com
      stage: staging
    prod:
      domain: api.example.com
      stage: prod

provider:
  stage: ${self:custom.environments.${self:provider.stage}.stage}

functions:
  api:
    handler: public/index.php
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
          authorizer:
            type: jwt
            identitySource: $request.header.Authorization
            jwt:
              audience:
                - ${self:custom.environments.${self:provider.stage}.clientId}
              issuer:
                - https://${self:custom.environments.${self:provider.stage}.authDomain}
```

### Deployment Commands

```bash
# Deploy to dev
vendor/bin/bref deploy --stage dev

# Deploy to staging
vendor/bin/bref deploy --stage staging

# Deploy to production
vendor/bin/bref deploy --stage prod
```

---

## Custom Domains

### Serverless Domain Plugin

```yaml
# serverless.yml
plugins:
  - ./vendor/bref/bref
  - serverless-domain-manager

custom:
  customDomain:
    domainName: api.example.com
    stage: ${self:provider.stage}
    basePath: ''
    certificateArn: arn:aws:acm:us-east-1:123456789012:certificate/cert-id
    createRoute53Record: true
```

### API Gateway Custom Domain

```yaml
# serverless.yml
resources:
  Resources:
    ApiDomain:
      Type: AWS::ApiGatewayV2::DomainName
      Properties:
        DomainName: api.example.com
        DomainNameConfigurations:
          - CertificateArn: arn:aws:acm:us-east-1:123456789012:certificate/cert-id
            EndpointType: REGIONAL
            SecurityPolicy: TLS_1_2
```

---

## Monitoring

### CloudWatch Logs

```yaml
# serverless.yml
functions:
  api:
    handler: public/index.php
    loggingConfig:
      level: error
      retentionInDays: 7
```

### X-Ray Tracing

```yaml
# serverless.yml
provider:
  tracing:
    api: true

functions:
  api:
    handler: public/index.php
    tracing: Active
```
