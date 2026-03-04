# AWS SAM Bootstrap Examples

## Minimal `template.yaml` (Zip package)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Minimal SAM template for Lambda bootstrap

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Tracing: Active

Resources:
  HelloFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hello-sam
      Runtime: python3.12
      Handler: app.lambda_handler
      CodeUri: src/
      Architectures:
        - x86_64
      Policies:
        - AWSLambdaBasicExecutionRole
      Events:
        HelloApi:
          Type: Api
          Properties:
            Path: /hello
            Method: get

Outputs:
  HelloFunctionArn:
    Description: ARN of the deployed function
    Value: !GetAtt HelloFunction.Arn
  HelloApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/hello"
```

## `template.yaml` for Image package

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: SAM template using container image

Resources:
  ImageFunction:
    Type: AWS::Serverless::Function
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .
      DockerTag: v1
    Properties:
      PackageType: Image
      Architectures:
        - x86_64
      Timeout: 30
      MemorySize: 512
      Policies:
        - AWSLambdaBasicExecutionRole
      Events:
        InvokeApi:
          Type: Api
          Properties:
            Path: /invoke
            Method: post
```

## Baseline `samconfig.toml`

```toml
version = 0.1

[default.global.parameters]
stack_name = "my-sam-app"

[default.build.parameters]
cached = true
parallel = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = true
resolve_s3 = true
region = "us-east-1"

[default.package.parameters]
resolve_s3 = true

[prod.global.parameters]
stack_name = "my-sam-app-prod"

[prod.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = false
resolve_s3 = true
region = "us-east-1"
```

## Sample Event Payload

`events/event.json`

```json
{
  "resource": "/hello",
  "path": "/hello",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json"
  },
  "queryStringParameters": {
    "name": "world"
  },
  "body": null,
  "isBase64Encoded": false
}
```

## Command Sequences

### New project flow

```bash
sam init
sam build
sam local invoke HelloFunction -e events/event.json
sam deploy --guided
```

### Existing project migration flow

```bash
sam validate
sam build
sam package
sam deploy --guided
```
