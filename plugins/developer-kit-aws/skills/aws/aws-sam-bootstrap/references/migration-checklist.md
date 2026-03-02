# AWS SAM Migration Checklist

Use this checklist when converting an existing Lambda or CloudFormation project to AWS SAM.

## Discovery

- Identify runtime, handler, and entrypoint per Lambda function
- Identify current deployment method (manual zip, CloudFormation, CI pipeline)
- Identify IAM roles/policies currently required
- Identify triggers (API Gateway, EventBridge, SQS, SNS, S3)

## Template Conversion

- Add `Transform: AWS::Serverless-2016-10-31`
- Convert function resources to `AWS::Serverless::Function` where possible
- Preserve environment variables and timeout/memory settings
- Preserve permissions and event source mappings
- Keep logical IDs stable when possible to reduce replacement risk

## Configuration

- Create `samconfig.toml` with `default` deploy parameters
- Add optional `prod` section for production deployments
- Set `capabilities = "CAPABILITY_IAM"` when needed
- Set `resolve_s3 = true` to simplify packaging

## Local Testing

- Create representative payloads under `events/`
- Run `sam validate`
- Run `sam build`
- Run `sam local invoke <FunctionLogicalId> -e events/event.json`

## Deployment

- First deploy with `sam deploy --guided`
- Review generated changeset before execution
- Validate stack outputs and function runtime behavior
- Capture follow-up changes in a separate PR if broader infra refactoring is needed
