# Authentication - OIDC and IAM Configuration

## OIDC Provider Setup (Recommended)

### CloudFormation Template for OIDC Provider

```yaml
OidcProvider:
  Type: AWS::IAM::OIDCProvider
  Properties:
    Url: https://token.actions.githubusercontent.com
    ClientIdList:
      - sts.amazonaws.com
    ThumbprintList:
      - 6938fd4d98bab03faabd97ca34b7b5dbd06c4ee5

GitHubActionsRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: github-actions-ecs-role
    AssumeRolePolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Federated: !Sub 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
          Action: sts:AssumeRoleWithWebIdentity
          Condition:
            StringEquals:
              token.actions.githubusercontent.com:aud: sts.amazonaws.com
            StringLike:
              token.actions.githubusercontent.com:sub: repo:my-org/my-repo:*
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AmazonECS_FullAccess
      - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

Outputs:
  RoleArn:
    Description: GitHub Actions Role ARN
    Value: !GetAtt GitHubActionsRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-RoleArn'
```

### GitHub Actions OIDC Configuration

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecs-role
    aws-region: us-east-1
```

## IAM Key Authentication (Legacy)

### GitHub Actions Configuration with IAM Keys

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

### Store Credentials in GitHub Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `AWS_ACCESS_KEY_ID`
4. Add `AWS_SECRET_ACCESS_KEY`
5. Optionally add `AWS_SESSION_TOKEN` for temporary credentials

## IAM Role with Least Privilege

### Minimal Permissions for ECS Deployment

```yaml
ECSDeployRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Federated: !Sub 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
          Action: sts:AssumeRoleWithWebIdentity
          Condition:
            StringEquals:
              token.actions.githubusercontent.com:aud: sts.amazonaws.com
            StringLike:
              token.actions.githubusercontent.com:sub: repo:${GitHubOrg}/${GitHubRepo}:*
    Policies:
      - PolicyName: ECSDeployPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - ecs:DescribeServices
                - ecs:DescribeTaskDefinition
                - ecs:DescribeTasks
                - ecs:ListTasks
                - ecs:RegisterTaskDefinition
                - ecs:UpdateService
              Resource: !Sub 'arn:aws:ecs:${AWS::Region}:${AWS::AccountId}:*'
            - Effect: Allow
              Action:
                - ecr:GetAuthorizationToken
                - ecr:BatchCheckLayerAvailability
                - ecr:GetDownloadUrlForLayer
                - ecr:GetRepositoryPolicy
                - ecr:DescribeRepositories
                - ecr:ListImages
                - ecr:DescribeImages
                - ecr:BatchGetImage
                - ecr:InitiateLayerUpload
                - ecr:UploadLayerPart
                - ecr:CompleteLayerUpload
                - ecr:PutImage
              Resource: !Sub 'arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/${ECRRepositoryName}'
            - Effect: Allow
              Action:
                - cloudformation:DescribeStacks
                - cloudformation:CreateStack
                - cloudformation:UpdateStack
                - cloudformation:DescribeStackEvents
              Resource: !Sub 'arn:aws:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/${CloudFormationStackName}/*'
            - Effect: Allow
              Action:
                - iam:PassRole
              Resource: !Sub 'arn:aws:iam::${AWS::AccountId}:role/ecsTaskExecutionRole'
```

## Cross-Account Deployment

### Assume Role in Different Account

```yaml
- name: Configure AWS credentials (Account A)
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_A_ID:role/github-actions-base-role
    aws-region: us-east-1

- name: Assume role in target account (Account B)
  run: |
    ASSUME_ROLE_ARN=arn:aws:iam::ACCOUNT_B_ID:role/cross-account-deployment-role
    TEMP_ROLE=$(aws sts assume-role --role-arn $ASSUME_ROLE_ARN --role-session-name github-actions --query 'Credentials.{AccessKeyId:AccessKeyId,SecretAccessKey:SecretAccessKey,SessionToken:SessionToken}' --output json)
    export AWS_ACCESS_KEY_ID=$(echo $TEMP_ROLE | jq -r '.AccessKeyId')
    export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_ROLE | jq -r '.SecretAccessKey')
    export AWS_SESSION_TOKEN=$(echo $TEMP_ROLE | jq -r '.SessionToken')
```

## Multi-Repository OIDC Configuration

```yaml
GitHubActionsRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Federated: !Sub 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
          Action: sts:AssumeRoleWithWebIdentity
          Condition:
            StringEquals:
              token.actions.githubusercontent.com:aud: sts.amazonaws.com
            StringLike:
              # Allow multiple repositories
              token.actions.githubusercontent.com:sub: |
                repo:my-org/frontend:*
                repo:my-org/backend:*
                repo:my-org/api:*
```

## Environment-Specific Roles

```yaml
DevRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: github-actions-ecs-dev
    AssumeRolePolicyDocument:
      # ... (OIDC trust policy)
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AmazonECS_FullAccess

StagingRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: github-actions-ecs-staging
    AssumeRolePolicyDocument:
      # ... (OIDC trust policy)
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AmazonECS_FullAccess

ProdRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: github-actions-ecs-prod
    AssumeRolePolicyDocument:
      # ... (OIDC trust policy with stricter conditions)
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AmazonECS_FullAccess
```
