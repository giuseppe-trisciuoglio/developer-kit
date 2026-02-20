# Serverless Configuration Reference

Complete reference for deploying NestJS Lambda applications using Serverless Framework and AWS SAM.

## Serverless Framework

### Basic Configuration

```yaml
service: nestjs-lambda-api

provider:
  name: aws
  runtime: nodejs20.x
  region: ${opt:region, 'us-east-1'}
  stage: ${opt:stage, 'dev'}
  memorySize: 512
  timeout: 29
  environment:
    NODE_ENV: production
    DATABASE_URL: ${ssm:/${self:service}/${self:provider.stage}/database-url}
    JWT_SECRET: ${ssm:/${self:service}/${self:provider.stage}/jwt-secret}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource:
            - !Sub 'arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/${self:service}-*'

package:
  individually: false
  patterns:
    - '!node_modules/**'
    - '!test/**'
    - '!.git/**'
    - 'dist/**'
    - '!dist/tsconfig.build.tsbuildinfo'

custom:
  esbuild:
    bundle: true
    minify: true
    target: node20
    platform: node
    external:
      - '@nestjs/microservices'
      - '@nestjs/websockets'
      - 'class-transformer/storage'

functions:
  api:
    handler: dist/lambda.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true
    provisionedConcurrency: ${self:custom.provisionedConcurrency.${self:provider.stage}, 0}

custom:
  provisionedConcurrency:
    prod: 5
    dev: 0

plugins:
  - serverless-esbuild
  - serverless-offline
```

### Commands

```bash
# Deploy
serverless deploy
serverless deploy --stage prod --region eu-west-1

# Local development
serverless offline

# Logs
serverless logs -f api -t

# Remove
serverless remove
```

## AWS SAM

### Basic Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: NestJS Lambda API

Globals:
  Function:
    Timeout: 29
    MemorySize: 512
    Runtime: nodejs20.x
    Architectures:
      - x86_64

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  NestJSApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-api'
      Handler: dist/lambda.handler
      CodeUri: ./
      Environment:
        Variables:
          NODE_ENV: !Ref Environment
          DATABASE_URL: !Sub '{{resolve:ssm-secure:/${AWS::StackName}/database-url}}'
      Events:
        ApiGatewayRoot:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref ApiGatewayApi
        ApiGatewayProxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref ApiGatewayApi
      Policies:
        - AWSLambdaBasicExecutionRole

  ApiGatewayApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: !Sub "'${AllowedOrigins}'"

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ApiGatewayApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/'
```

### Commands

```bash
# Build
sam build

# Local development
sam local start-api --warm-containers EAGER

# Deploy
sam deploy --guided
sam deploy --config-env prod

# Logs
sam logs -n NestJSApiFunction --tail

# Delete
sam delete
```

## Comparison

| Feature | SAM | Serverless Framework |
|---------|-----|---------------------|
| Native AWS | Yes | No (uses CloudFormation) |
| Local testing | `sam local` | `serverless-offline` |
| CI/CD integration | AWS-native | Multi-cloud support |
| Syntax | YAML/JSON | YAML/TypeScript/JavaScript |
| Plugins | SAR, nested stacks | Rich plugin ecosystem |

## When to Choose

**Choose SAM when:**
- Native AWS environment
- Team familiar with CloudFormation
- Deep AWS service integration needed
- AWS CodePipeline/CodeBuild usage

**Choose Serverless Framework when:**
- Multi-cloud requirements
- Large plugin ecosystem needed
- Prefer TypeScript/JavaScript config
- Easier local development preferred
