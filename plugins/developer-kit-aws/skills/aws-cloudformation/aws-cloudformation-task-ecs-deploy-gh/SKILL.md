---
name: aws-cloudformation-task-ecs-deploy-gh
description: Provides patterns to deploy ECS tasks and services with GitHub Actions CI/CD. Use when building Docker images, pushing to ECR, updating ECS task definitions, deploying ECS services, integrating with CloudFormation stacks, configuring AWS OIDC authentication for GitHub Actions, and implementing production-ready container deployment pipelines. Supports ECS deployments with proper security (OIDC or IAM keys), multi-environment support, blue/green deployments, ECR private repositories with image scanning, and CloudFormation infrastructure updates.
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Task ECS Deploy with GitHub Actions

## Overview

Deploy containerized applications to Amazon ECS using GitHub Actions workflows. This skill covers the complete deployment pipeline: authentication with AWS (OIDC recommended), building Docker images, pushing to Amazon ECR, updating task definitions, and deploying ECS services. Integrate with CloudFormation for infrastructure-as-code management and implement production-grade deployment strategies.

## When to Use

Use this skill when:
- Deploying Docker containers to Amazon ECS via GitHub Actions
- Setting up CI/CD pipelines for AWS container deployments
- Configuring AWS authentication for GitHub Actions (OIDC or IAM keys)
- Building and pushing Docker images to Amazon ECR
- Updating ECS task definitions dynamically
- Implementing blue/green or rolling deployments
- Managing CloudFormation stacks from CI/CD
- Setting up multi-environment deployments (dev/staging/prod)

## Instructions

1. **Configure OIDC Authentication**: Create IAM OIDC provider for GitHub Actions (preferred over IAM keys)
2. **Create IAM Role**: Define role with trust policy for `token.actions.githubusercontent.com` with repo condition
3. **Set Up ECR Repository**: Create private ECR repo with image scanning and lifecycle policy
4. **Create GitHub Workflow**: Define workflow triggered on push/PR with proper permissions (`id-token: write`)
5. **Build and Push Image**: Use `aws-actions/amazon-ecr-login@v2`, build with `docker build`, push with commit SHA tag
6. **Render Task Definition**: Use `aws-actions/amazon-ecs-render-task-definition@v1` to inject new image
7. **Deploy to ECS**: Use `aws-actions/amazon-ecs-deploy-task-definition@v1` with service and cluster
8. **Add Multi-Environment**: Use GitHub environments with protection rules for staging/production

## Best Practices

### Security
- Use OIDC authentication (not IAM access keys) for GitHub Actions
- Scope IAM role trust policy to specific repo/branch with `sub` condition
- Enable ECR image scanning for vulnerability detection
- Store sensitive values in GitHub Secrets, not in workflow files
- Use least-privilege IAM policies for deployment role

### Deployment
- Tag images with commit SHA for traceability
- Use blue/green deployment with CodeDeploy for zero-downtime
- Implement health checks before marking deployment complete
- Add manual approval gates for production deployments
- Keep task definition in repo as JSON for version control

### CI/CD
- Cache Docker layers to speed up builds
- Run tests before building images
- Use matrix strategy for multi-architecture builds (amd64/arm64)
- Set up ECR lifecycle policies to clean old images

## Examples

```yaml
# .github/workflows/deploy.yml
name: Deploy to ECS
on:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          REPOSITORY: my-app
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$REPOSITORY:$IMAGE_TAG .
          docker push $REGISTRY/$REPOSITORY:$IMAGE_TAG

      - name: Render task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: app
          image: ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: my-service
          cluster: my-cluster
          wait-for-service-stability: true
```

```yaml
# CloudFormation: OIDC Provider for GitHub Actions
Resources:
  GitHubOIDCProvider:
    Type: AWS::IAM::OIDCProvider
    Properties:
      Url: https://token.actions.githubusercontent.com
      ClientIdList: [sts.amazonaws.com]
      ThumbprintList: [6938fd4d98bab03faadb97b34396831e3780aea1]

  GitHubActionsRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-github-actions"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Ref GitHubOIDCProvider
            Action: sts:AssumeRoleWithWebIdentity
            Condition:
              StringEquals:
                token.actions.githubusercontent.com:aud: sts.amazonaws.com
              StringLike:
                token.actions.githubusercontent.com:sub: "repo:org/repo:*"
      Policies:
        - PolicyName: ECSDeployment
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ecr:GetAuthorizationToken
                Resource: "*"
              - Effect: Allow
                Action:
                  - ecr:BatchGetImage
                  - ecr:BatchCheckLayerAvailability
                  - ecr:PutImage
                  - ecr:InitiateLayerUpload
                  - ecr:UploadLayerPart
                  - ecr:CompleteLayerUpload
                Resource: !Sub "arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/*"
              - Effect: Allow
                Action:
                  - ecs:UpdateService
                  - ecs:DescribeServices
                  - ecs:RegisterTaskDefinition
                  - ecs:DescribeTaskDefinition
                Resource: "*"
              - Effect: Allow
                Action:
                  - iam:PassRole
                Resource:
                  - !Sub "arn:aws:iam::${AWS::AccountId}:role/*-execution-role"
                  - !Sub "arn:aws:iam::${AWS::AccountId}:role/*-task-role"
```

## Constraints and Warnings

- **OIDC Thumbprint**: GitHub OIDC thumbprint may change; verify current value
- **IAM Role Trust**: Scope `sub` condition to specific repo and branch for security
- **ECR Limits**: Max 10,000 images per repository; use lifecycle policies
- **ECS Deployment**: `wait-for-service-stability` can timeout (default 10 min)
- **Task Definition**: Must match existing service's launch type and network mode
- **Blue/Green**: Requires CodeDeploy application and deployment group pre-configured
- **Image Tags**: Avoid `latest` tag; use commit SHA or semantic versioning

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all CloudFormation resources, see [Reference](references/reference.md).
