# AWS CloudFormation IAM - Examples

This file contains comprehensive examples for IAM patterns with CloudFormation.

## Example 1: Multi-Environment IAM Infrastructure

Complete IAM setup with environment-specific configurations for development, staging, and production.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Multi-environment IAM infrastructure with users, roles, and policies

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production
    Description: Deployment environment

  ProjectName:
    Type: String
    Default: myapp
    Description: Name of the project

  AdministratorUserArns:
    Type: CommaDelimitedList
    Default: ""
    Description: ARNs of users who can assume admin role in production

Mappings:
  EnvironmentConfig:
    dev:
      MaxSessionDuration: 3600
      RequireMFA: false
      AllowDeleteResources: true
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
    staging:
      MaxSessionDuration: 7200
      RequireMFA: true
      AllowDeleteResources: true
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
        - arn:aws:iam::aws:policy/ViewBilling
    production:
      MaxSessionDuration: 43200
      RequireMFA: true
      AllowDeleteResources: false
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
        - arn:aws:iam::aws:policy/ViewBilling
        - arn:aws:iam::aws:policy/SecurityAudit

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]
  IsDev: !Equals [!Ref Environment, dev]
  HasAdminUsers: !Not [!Equals [!Join ["", !Ref AdministratorUserArns], ""]]

Resources:
  # IAM Group for Developers
  DevelopersGroup:
    Type: AWS::IAM::Group
    Properties:
      GroupName: !Sub "${ProjectName}-developers-${Environment}"
      ManagedPolicyArns: !FindInMap [EnvironmentConfig, !Ref Environment, ManagedPolicies]

  # IAM User for Application Service Account
  AppServiceUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${ProjectName}-svc-${Environment}"
      Groups:
        - !Ref DevelopersGroup
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: Platform Team

  # Access Key for Service Account
  AppServiceAccessKey:
    Type: AWS::IAM::AccessKey
    Properties:
      UserName: !Ref AppServiceUser
      Status: Active
      Serial: 1

  # Secret for Access Key Storage
  AppServiceCredentialsSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${ProjectName}/${Environment}/app-service-credentials"
      Description: Credentials for the application service account
      SecretString: !Sub |
        {
          "username": "${AppServiceUser.UserName}",
          "access_key_id": "${AppServiceAccessKey.Ref}",
          "secret_access_key": "{{resolve:secretsmanager:${AppServiceAccessKey.SecretAccessKey}}}",
          "created_date": "${!Timestamp}"
        }
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-lambda-exec-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      MaxSessionDuration: !FindInMap [EnvironmentConfig, !Ref Environment, MaxSessionDuration]
      Policies:
        - PolicyName: !Sub "${ProjectName}-dynamodb-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${ProjectName}*"
                Condition:
                  StringEquals:
                    dynamodb:TableName: !Sub "${ProjectName}-${Environment}-data"
              - Effect: Allow
                Action:
                  - dynamodb:DescribeTable
                  - dynamodb:ListTagsOfResource
                Resource: "*"
        - PolicyName: !Sub "${ProjectName}-secrets-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                  - secretsmanager:DescribeSecret
                Resource: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${ProjectName}/${Environment}/*"
        - PolicyName: !Sub "${ProjectName}-s3-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Sub "arn:aws:s3:::${ProjectName}-${Environment}-*"
                  - !Sub "arn:aws:s3:::${ProjectName}-${Environment}-*/*"
        - PolicyName: !Sub "${ProjectName}-kms-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:DescribeKey
                Resource: "*"
                Condition:
                  StringEquals:
                    kms:ViaService: !Sub "lambda.${AWS::Region}.amazonaws.com"
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # Administrator Role (Production Only)
  AdministratorRole:
    Type: AWS::IAM::Role
    Condition: IsProduction
    Properties:
      RoleName: !Sub "${ProjectName}-admin-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Ref AdministratorUserArns
            Action: sts:AssumeRole
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: "true"
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
      MaxSessionDuration: 14400
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # Cross-Account Read Role for Staging and Production
  CrossAccountReadRole:
    Type: AWS::IAM::Role
    Condition: !Or [IsStaging, IsProduction]
    Properties:
      RoleName: !Sub "${ProjectName}-crossaccount-read-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: "*"
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                sts:Externalid: !Sub "${ProjectName}-${Environment}-external-id"
              IpAddress:
                aws:SourceIp:
                  - 10.0.0.0/8
                  - 172.16.0.0/12
      Policies:
        - PolicyName: !Sub "${ProjectName}-readonly-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:GetObjectVersion
                  - s3:ListBucket
                Resource:
                  - !Sub "arn:aws:s3:::${ProjectName}-${Environment}-data"
                  - !Sub "arn:aws:s3:::${ProjectName}-${Environment}-data/*"
              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:GetItem
                Resource:
                  - !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${ProjectName}*"
              - Effect: Deny
                Action:
                  - s3:DeleteObject
                  - s3:PutObject
                Resource:
                  - !Sub "arn:aws:s3:::${ProjectName}-${Environment}-data/*"
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Read-Only Group Policy
  ReadOnlyAccessPolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      ManagedPolicyName: !Sub "${ProjectName}-readonly-${Environment}"
      Description: Read-only access policy for the project
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action:
              - s3:Get*
              - s3:List*
            Resource: "*"
          - Effect: Allow
            Action:
              - dynamodb:Describe*
              - dynamodb:Get*
              - dynamodb:List*
              - dynamodb:Query
              - dynamodb:Scan
            Resource: "*"
          - Effect: Allow
            Action:
              - lambda:Get*
              - lambda:List*
            Resource: "*"
          - Effect: Allow
            Action:
              - logs:Describe*
              - logs:Get*
              - logs:List*
              - logs:Filter*
              - logs:StartQuery
            Resource: "*"

Outputs:
  AppServiceUserArn:
    Description: ARN of the application service user
    Value: !GetAtt AppServiceUser.Arn

  LambdaExecutionRoleArn:
    Description: ARN of the Lambda execution role
    Value: !GetAtt LambdaExecutionRole.Arn
    Export:
      Name: !Sub "${ProjectName}-LambdaExecutionRoleArn-${Environment}"

  CrossAccountReadRoleArn:
    Description: ARN of the cross-account read role
    Value: !GetAtt CrossAccountReadRole.Arn
    Condition: !Or [IsStaging, IsProduction]
    Export:
      Name: !Sub "${ProjectName}-CrossAccountReadRoleArn-${Environment}"

  AdministratorRoleArn:
    Description: ARN of the administrator role
    Value: !GetAtt AdministratorRole.Arn
    Condition: IsProduction
```

## Example 2: Cross-Account Access with Security Controls

Complete cross-account access setup with external ID, IP restrictions, and MFA requirements.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Cross-account access role with security controls

Parameters:
  SourceAccountId:
    Type: String
    Description: AWS account ID that can assume this role
    MaxLength: 12
    MinLength: 12

  ExternalId:
    Type: String
    Description: External ID for trust relationship
    MinLength: 16
    MaxLength: 64

  ProjectName:
    Type: String
    Default: myproject
    Description: Name of the project

  AllowedIpRanges:
    Type: CommaDelimitedList
    Description: IP ranges allowed to assume this role
    Default: "10.0.0.0/8,172.16.0.0/12"

Resources:
  # Cross-Account Read Role
  CrossAccountReadRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-crossaccount-read"
      Description: Role for cross-account read access with enhanced security
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${SourceAccountId}:root"
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                sts:Externalid: !Ref ExternalId
              IpAddress:
                aws:SourceIp: !Ref AllowedIpRanges
              Bool:
                aws:MultiFactorAuthPresent: "true"
      MaxSessionDuration: 7200
      Policies:
        - PolicyName: !Sub "${ProjectName}-s3-readonly"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:GetObjectVersion
                  - s3:ListBucket
                Resource:
                  - !Ref SourceBucketArn
                  - !Sub "${SourceBucketArn}/*"
              - Effect: Deny
                Action:
                  - s3:DeleteObject
                  - s3:PutObject
                  - s3:PutObjectAcl
                Resource:
                  - !Sub "${SourceBucketArn}/*"
                Condition:
                  StringNotEquals:
                    aws:PrincipalTag/Role: breakglass
        - PolicyName: !Sub "${ProjectName}-dynamodb-readonly"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:GetItem
                  - dynamodb:DescribeTable
                Resource:
                  - !GetAtt SourceTable.Arn
                  - !Sub "${GetAtt SourceTable.Arn}/index/*"
              - Effect: Deny
                Action:
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                Resource:
                  - !GetAtt SourceTable.Arn
                Condition:
                  StringNotEquals:
                    aws:PrincipalTag/Role: breakglass
        - PolicyName: !Sub "${ProjectName}-cloudwatch-readonly"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:Describe*
                  - logs:Get*
                  - logs:List*
                  - logs:Filter*
                  - logs:StartQuery
                Resource: "*"
      Tags:
        - Key: Project
          Value: !Ref ProjectName
        - Key: SecurityTier
          Value: high

  # Cross-Account Write Role (More Privileged)
  CrossAccountWriteRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-crossaccount-write"
      Description: Role for cross-account write access with enhanced security
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${SourceAccountId}:root"
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                sts:Externalid: !Ref ExternalId
              IpAddress:
                aws:SourceIp: !Ref AllowedIpRanges
              Bool:
                aws:MultiFactorAuthPresent: "true"
              NumericLessThanEquals:
                aws:MultiFactorAuthAge: 3600
      MaxSessionDuration: 3600
      Policies:
        - PolicyName: !Sub "${ProjectName}-s3-write"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                  - s3:ListBucket
                Resource:
                  - !Ref ProcessBucketArn
                  - !Sub "${ProcessBucketArn}/*"
        - PolicyName: !Sub "${ProjectName}-dynamodb-write"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                Resource: !GetAtt ProcessTable.Arn
      Tags:
        - Key: Project
          Value: !Ref ProjectName
        - Key: SecurityTier
          Value: critical

  # Secrets for External Account
  CrossAccountCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${ProjectName}/cross-account-credentials"
      Description: Credentials for cross-account access
      SecretString: !Sub |
        {
          "external_id": "${ExternalId}",
          "read_role_arn": "${CrossAccountReadRole.Arn}",
          "write_role_arn": "${CrossAccountWriteRole.Arn}"
        }

Outputs:
  ReadRoleArn:
    Description: ARN of the read-only cross-account role
    Value: !GetAtt CrossAccountReadRole.Arn
    Export:
      Name: !Sub "${ProjectName}-CrossAccountReadRoleArn"

  WriteRoleArn:
    Description: ARN of the write cross-account role
    Value: !GetAtt CrossAccountWriteRole.Arn
    Export:
      Name: !Sub "${ProjectName}-CrossAccountWriteRoleArn"

  ExternalId:
    Description: External ID for cross-account role assumption
    Value: !Ref ExternalId
    Sensitive: true
```

## Example 3: Permission Boundaries with Least Privilege

Implementation of permission boundaries to enforce least privilege access for developers.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Permission boundary implementation for developer access control

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  ProjectName:
    Type: String
    Default: myproject
    Description: Name of the project

Mappings:
  EnvironmentConfig:
    dev:
      AllowProductionRead: true
      AllowResourceDeletion: true
      MaxBudgetUSD: 1000
    staging:
      AllowProductionRead: false
      AllowResourceDeletion: true
      MaxBudgetUSD: 500
    production:
      AllowProductionRead: false
      AllowResourceDeletion: false
      MaxBudgetUSD: 100

Resources:
  # Permission Boundary Policy - Prevents Privilege Escalation
  DeveloperBoundaryPolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      ManagedPolicyName: !Sub "${ProjectName}-developer-boundary-${Environment}"
      Description: Permission boundary for developers - enforces least privilege
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          # Deny actions on production resources
          - Sid: DenyProductionWrite
            Effect: Deny
            Action:
              - s3:Delete*
              - s3:Put*
              - dynamodb:Delete*
              - dynamodb:PutItem
              - dynamodb:UpdateItem
              - lambda:Delete*
              - lambda:Update*
              - rds:Delete*
              - rds:Modify*
              - ec2:Terminate*
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production

          # Deny IAM privilege escalation
          - Sid: DenyPrivilegeEscalation
            Effect: Deny
            Action:
              - iam:CreateUser
              - iam:DeleteUser
              - iam:AttachUserPolicy
              - iam:DetachUserPolicy
              - iam:PutUserPolicy
              - iam:DeleteUserPolicy
              - iam:CreateRole
              - iam:DeleteRole
              - iam:AttachRolePolicy
              - iam:DetachRolePolicy
              - iam:PutRolePolicy
              - iam:DeleteRolePolicy
              - iam:CreateGroup
              - iam:DeleteGroup
              - iam:AttachGroupPolicy
              - iam:DetachGroupPolicy
            Resource: "*"

          # Deny access to sensitive resources
          - Sid: DenySensitiveResources
            Effect: Deny
            Action:
              - iam:CreateAccessKey
              - iam:CreateLoginProfile
              - iam:EnableMFADevice
              - iam:GenerateCredentialReport
              - organizations:*
            Resource: "*"

          # Deny cost-related actions without approval
          - Sid: DenyCostManagement
            Effect: Deny
            Action:
              - billing:*
              - ce:*
              - budgets:*
            Resource: "*"

          # Restrict resource creation to project resources
          - Sid: RestrictResourceCreation
            Effect: Deny
            Action:
              - s3:CreateBucket
              - dynamodb:CreateTable
              - lambda:CreateFunction
              - rds:CreateDBInstance
            Resource: "*"
            Condition:
              StringNotLike:
                aws:ResourceTag/project: !Ref ProjectName

          # Production read requires explicit tag
          - Sid: DenyProductionRead
            Effect: Deny
            Action:
              - s3:GetObject*
              - dynamodb:GetItem*
              - dynamodb:Query
              - dynamodb:Scan
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production
              StringNotEquals:
                aws:PrincipalTag/environment: !Ref Environment
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production
              Bool:
                aws:PrincipalIsAWSService: false

          # Allow S3 read operations
          - Sid: AllowS3Read
            Effect: Allow
            Action:
              - s3:Get*
              - s3:List*
            Resource: "*"

          # Allow DynamoDB read operations
          - Sid: AllowDynamoDBRead
            Effect: Allow
            Action:
              - dynamodb:DescribeTable
              - dynamodb:Get*
              - dynamodb:List*
              - dynamodb:Query
              - dynamodb:Scan
            Resource: "*"

          # Allow Lambda read operations
          - Sid: AllowLambdaRead
            Effect: Allow
            Action:
              - lambda:Get*
              - lambda:List*
              - lambda:Invoke*
            Resource: "*"

          # Allow CloudWatch read operations
          - Sid: AllowCloudWatchRead
            Effect: Allow
            Action:
              - logs:Describe*
              - logs:Get*
              - logs:List*
              - logs:Filter*
              - cloudwatch:Describe*
              - cloudwatch:Get*
              - cloudwatch:List*
            Resource: "*"

          # Allow EC2 and RDS read operations
          - Sid: AllowComputeRead
            Effect: Allow
            Action:
              - ec2:Describe*
              - rds:Describe*
              - ecs:Describe*
              - eks:Describe*
            Resource: "*"

          # Allow SSM operations for instance management
          - Sid: AllowSSMOperations
            Effect: Allow
            Action:
              - ssm:Describe*
              - ssm:Get*
              - ssm:List*
            Resource: "*"

  # Developer Role with Permission Boundary
  DeveloperRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-developer-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Ref DeveloperUserArn
            Action: sts:AssumeRole
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: "true"
      PermissionsBoundary: !Ref DeveloperBoundaryPolicy
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Role
          Value: developer

  # Breakglass Role (Exceeds Permission Boundary)
  BreakglassRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-breakglass-${Environment}"
      Description: Breakglass role for emergency access - requires approval
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Ref EmergencyUserArn
            Action: sts:AssumeRole
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: "true"
              StringEquals:
                aws:PrincipalTag/role: breakglass
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
      MaxSessionDuration: 14400
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Role
          Value: breakglass
        - Key: security:critical
          Value: "true"

Outputs:
  BoundaryPolicyArn:
    Description: ARN of the developer permission boundary policy
    Value: !Ref DeveloperBoundaryPolicy

  DeveloperRoleArn:
    Description: ARN of the developer role
    Value: !GetAtt DeveloperRole.Arn
```

## Example 4: IAM Identity Center (SSO) Permission Sets

Complete SSO configuration with permission sets for different access levels.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: IAM Identity Center permission sets for workforce access

Parameters:
  SSOInstanceArn:
    Type: String
    Description: ARN of the SSO Instance

  TargetAccountId:
    Type: String
    Description: AWS account ID for assignments
    MaxLength: 12
    MinLength: 12

  AdminGroupId:
    Type: String
    Description: SSO Group ID for administrators

  DeveloperGroupId:
    Type: String
    Description: SSO Group ID for developers

  ViewerGroupId:
    Type: String
    Description: SSO Group ID for viewers

  BillingGroupId:
    Type: String
    Description: SSO Group ID for billing access

  ProjectName:
    Type: String
    Default: myproject
    Description: Name of the project

Resources:
  # Administrator Permission Set
  AdminPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${ProjectName}-Administrator"
      Description: Full administrator access for the project
      SessionDuration: PT4H
      ManagedPolicies:
        - arn:aws:iam::aws:policy/AdministratorAccess
      InlinePolicy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AllowBillingRead",
              "Effect": "Allow",
              "Action": [
                "aws-portal:ViewBilling",
                "aws-portal:ViewAccount"
              ],
              "Resource": "*"
            },
            {
              "Sid": "AllowCostExplorer",
              "Effect": "Allow",
              "Action": [
                "ce:GetCostAndUsage",
                "ce:GetCostForecast"
              ],
              "Resource": "*"
            }
          ]
        }

  # Developer Permission Set
  DeveloperPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${ProjectName}-Developer"
      Description: Developer access with write permissions
      SessionDuration: PT8H
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      InlinePolicy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AllowS3ProjectAccess",
              "Effect": "Allow",
              "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
              ],
              "Resource": [
                "arn:aws:s3:::${ProjectName}-*",
                "arn:aws:s3:::${ProjectName}-*/*"
              ]
            },
            {
              "Sid": "AllowDynamoDBProjectAccess",
              "Effect": "Allow",
              "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
              ],
              "Resource": [
                "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${ProjectName}*"
              ]
            },
            {
              "Sid": "AllowLambdaProjectAccess",
              "Effect": "Allow",
              "Action": [
                "lambda:InvokeFunction",
                "lambda:GetFunction",
                "lambda:UpdateFunctionCode"
              ],
              "Resource": [
                "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${ProjectName}*"
              ]
            },
            {
              "Sid": "AllowECRReadWrite",
              "Effect": "Allow",
              "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
              ],
              "Resource": "*"
            },
            {
              "Sid": "AllowLogsReadWrite",
              "Effect": "Allow",
              "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
              ],
              "Resource": "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${ProjectName}*"
            },
            {
              "Sid": "DenyProductionDelete",
              "Effect": "Deny",
              "Action": [
                "s3:DeleteObject",
                "dynamodb:DeleteItem",
                "lambda:DeleteFunction"
              ],
              "Resource": "*",
              "Condition": {
                "StringEquals": {
                  "aws:ResourceTag/environment": "production"
                }
              }
            }
          ]
        }

  # Viewer Permission Set
  ViewerPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${ProjectName}-Viewer"
      Description: Read-only access for stakeholders
      SessionDuration: PT4H
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      InlinePolicy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AllowS3Read",
              "Effect": "Allow",
              "Action": [
                "s3:GetObject",
                "s3:ListBucket"
              ],
              "Resource": [
                "arn:aws:s3:::${ProjectName}-*",
                "arn:aws:s3:::${ProjectName}-*/*"
              ]
            },
            {
              "Sid": "AllowCloudWatchRead",
              "Effect": "Allow",
              "Action": [
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics"
              ],
              "Resource": "*"
            },
            {
              "Sid": "AllowLogsRead",
              "Effect": "Allow",
              "Action": [
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
              ],
              "Resource": "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${ProjectName}*"
            }
          ]
        }

  # Billing Permission Set
  BillingPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${ProjectName}-Billing"
      Description: Access to billing and cost management
      SessionDuration: PT4H
      ManagedPolicies:
        - arn:aws:iam::aws:policy/ViewBilling
      InlinePolicy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "AllowBillingFull",
              "Effect": "Allow",
              "Action": [
                "aws-portal:*Billing",
                "aws-portal:*Usage",
                "billing:*",
                "ce:*",
                "budgets:*"
              ],
              "Resource": "*"
            }
          ]
        }

  # Account Assignments
  AdminAccountAssignment:
    Type: AWS::SSO::AccountAssignment
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetArn: !Ref AdminPermissionSet.PermissionSetArn
      PrincipalId: !Ref AdminGroupId
      PrincipalType: GROUP
      TargetId: !Ref TargetAccountId
      TargetType: AWS_ACCOUNT

  DeveloperAccountAssignment:
    Type: AWS::SSO::AccountAssignment
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetArn: !Ref DeveloperPermissionSet.PermissionSetArn
      PrincipalId: !Ref DeveloperGroupId
      PrincipalType: GROUP
      TargetId: !Ref TargetAccountId
      TargetType: AWS_ACCOUNT

  ViewerAccountAssignment:
    Type: AWS::SSO::AccountAssignment
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetArn: !Ref ViewerPermissionSet.PermissionSetArn
      PrincipalId: !Ref ViewerGroupId
      PrincipalType: GROUP
      TargetId: !Ref TargetAccountId
      TargetType: AWS_ACCOUNT

  BillingAccountAssignment:
    Type: AWS::SSO::AccountAssignment
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetArn: !Ref BillingPermissionSet.PermissionSetArn
      PrincipalId: !Ref BillingGroupId
      PrincipalType: GROUP
      TargetId: !Ref TargetAccountId
      TargetType: AWS_ACCOUNT

Outputs:
  AdminPermissionSetArn:
    Description: ARN of the admin permission set
    Value: !Ref AdminPermissionSet

  DeveloperPermissionSetArn:
    Description: ARN of the developer permission set
    Value: !Ref DeveloperPermissionSet

  ViewerPermissionSetArn:
    Description: ARN of the viewer permission set
    Value: !Ref ViewerPermissionSet

  BillingPermissionSetArn:
    Description: ARN of the billing permission set
    Value: !Ref BillingPermissionSet
```

## Example 5: Service Control Policies for Organization

SCP implementation for enforcing security controls across organizational units.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Service control policies for organizational security

Parameters:
  OrganizationId:
    Type: String
    Description: AWS Organization ID

  ProductionOUId:
    Type: String
    Description: Organizational Unit ID for production accounts

  StagingOUId:
    Type: String
    Description: Organizational Unit ID for staging accounts

  SecurityTeamArn:
    Type: String
    Description: ARN of the security team role

Resources:
  # SCP: Production Guardrails
  ProductionGuardrailsSCP:
    Type: AWS::Organizations::Policy
    Properties:
      Name: !Sub "${AWS::StackName}-production-guardrails"
      Description: Guardrail SCP for production accounts - prevents destructive operations
      Type: SERVICE_CONTROL_POLICY
      Content:
        Version: "2012-10-17"
        Statement:
          # Deny deletion of tagged resources
          - Sid: DenyDeleteTaggedResources
            Effect: Deny
            Action:
              - s3:DeleteBucket
              - s3:DeleteObject
              - dynamodb:DeleteTable
              - dynamodb:DeleteItem
              - rds:DeleteDBInstance
              - rds:DeleteDBCluster
              - lambda:DeleteFunction
              - ec2:TerminateInstances
              - ecs:DeleteCluster
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production

          # Require encryption for all writes
          - Sid: RequireEncryption
            Effect: Deny
            Action:
              - s3:PutObject
              - s3:PutObjectAcl
              - dynamodb:PutItem
              - dynamodb:UpdateItem
              - ebs:StartSnapshot
            Resource: "*"
            Condition:
              StringNotEquals:
                s3:x-amz-server-side-encryption: AES256
              StringNotEquals:
                dynamodb:EnforceSSL: "true"

          # Require MFA for IAM actions
          - Sid: RequireMFAForIAM
            Effect: Deny
            Action:
              - iam:CreateUser
              - iam:DeleteUser
              - iam:AttachUserPolicy
              - iam:DetachUserPolicy
              - iam:CreateRole
              - iam:DeleteRole
              - iam:AttachRolePolicy
              - iam:DetachRolePolicy
              - iam:CreateAccessKey
              - iam:CreateLoginProfile
              - iam:EnableMFADevice
            Resource: "*"
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: "false"

          # Restrict regions for production
          - Sid: RestrictRegions
            Effect: Deny
            Action: "*"
            Resource: "*"
            Condition:
              StringNotEquals:
                aws:RequestedRegion:
                  - us-east-1
                  - us-west-2
                  - eu-west-1
              Bool:
                aws:PrincipalIsAWSService: false

          # Deny root user access
          - Sid: DenyRootUser
            Effect: Deny
            Action:
              - iam:CreateAccessKey
              - iam:CreateLoginProfile
              - iam:EnableMFADevice
            Resource: "*"
            Condition:
              StringEquals:
                aws:PrincipalType: root

          # Require tags on resources
          - Sid: RequireResourceTags
            Effect: Deny
            Action:
              - s3:CreateBucket
              - dynamodb:CreateTable
              - lambda:CreateFunction
              - rds:CreateDBInstance
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: ""
            Condition:
              ForAllValues:StringNotEquals:
                aws:TagKeys:
                  - environment
                  - project
                  - owner

  # SCP: Staging Guardrails
  StagingGuardrailsSCP:
    Type: AWS::Organizations::Policy
    Properties:
      Name: !Sub "${AWS::StackName}-staging-guardrails"
      Description: Guardrail SCP for staging accounts
      Type: SERVICE_CONTROL_POLICY
      Content:
        Version: "2012-10-17"
        Statement:
          # Allow most operations but prevent production access
          - Sid: AllowAllExceptProductionDelete
            Effect: Allow
            Action: "*"
            Resource: "*"
            Condition:
              StringNotEquals:
                aws:ResourceTag/environment: production

          # Deny production resource access
          - Sid: DenyProductionAccess
            Effect: Deny
            Action: "*"
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production

          # Require encryption
          - Sid: RequireEncryption
            Effect: Deny
            Action:
              - s3:PutObject
              - dynamodb:PutItem
            Resource: "*"
            Condition:
              StringNotEquals:
                s3:x-amz-server-side-encryption: AES256

  # SCP: Security Audit Requirements
  SecurityAuditSCP:
    Type: AWS::Organizations::Policy
    Properties:
      Name: !Sub "${AWS::StackName}-security-audit"
      Description: SCP to ensure security audit configuration
      Type: SERVICE_CONTROL_POLICY
      Content:
        Version: "2012-10-17"
        Statement:
          # Require CloudTrail
          - Sid: RequireCloudTrail
            Effect: Deny
            Action:
              - ec2:CreateVpc
              - ec2:CreateSecurityGroup
            Resource: "*"
            Condition:
              Bool:
                aws:Ec2Vpc: vpc-*

          # Require encryption for EBS volumes
          - Sid: RequireEBSEncryption
            Effect: Deny
            Action:
              - ec2:CreateVolume
            Resource: "*"
            Condition:
              StringNotEquals:
                ebs:VolumeType: gp3

  # Policy Attachment to OUs
  ProductionPolicyAttachment:
    Type: AWS::Organizations::PolicyAttachment
    Properties:
      PolicyId: !Ref ProductionGuardrailsSCP
      TargetId: !Ref ProductionOUId
      PolicyType: SERVICE_CONTROL_POLICY

  StagingPolicyAttachment:
    Type: AWS::Organizations::PolicyAttachment
    Properties:
      PolicyId: !Ref StagingGuardrailsSCP
      TargetId: !Ref StagingOUId
      PolicyType: SERVICE_CONTROL_POLICY

Outputs:
  ProductionSCPId:
    Description: ID of the production guardrails SCP
    Value: !Ref ProductionGuardrailsSCP

  StagingSCPId:
    Description: ID of the staging guardrails SCP
    Value: !Ref StagingGuardrailsSCP
```

## Example 6: Complete ECS Task Roles Setup

Complete setup for ECS tasks with task execution role and task role.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECS task roles with proper IAM configuration

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  ProjectName:
    Type: String
    Default: myproject
    Description: Name of the project

Mappings:
  EnvironmentConfig:
    dev:
      LogRetention: 7
      EnableXray: false
    staging:
      LogRetention: 14
      EnableXray: true
    production:
      LogRetention: 30
      EnableXray: true

Resources:
  # ECS Task Execution Role
  ECSTaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-ecs-task-exec-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Policies:
        - PolicyName: !Sub "${ProjectName}-ecr-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ecr:GetDownloadUrlForLayer
                  - ecr:BatchGetImage
                  - ecr:BatchCheckLayerAvailability
                Resource: !Ref EcrRepositoryArn
              - Effect: Allow
                Action:
                  - ecr:GetAuthorizationToken
                Resource: "*"
        - PolicyName: !Sub "${ProjectName}-logs-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:CreateLogGroup
                Resource: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/ecs/${ProjectName}*"
              - Effect: Allow
                Action:
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                  - logs:GetLogEvents
                Resource: "*"
        - PolicyName: !Sub "${ProjectName}-secrets-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${ProjectName}/${Environment}/*"
        - PolicyName: !Sub "${ProjectName}-sm-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - ssm:GetParameters
                  - ssm:GetParameter
                  - ssm:GetParametersByPath
                Resource:
                  - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/${ProjectName}/${Environment}/*"
                  - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/${ProjectName}/common/*"
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # ECS Task Role (Application Role)
  ECSTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-ecs-task-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${ProjectName}-app-sqs-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sqs:ReceiveMessage
                  - sqs:DeleteMessage
                  - sqs:GetQueueAttributes
                  - sqs:GetQueueUrl
                  - sqs:ChangeMessageVisibility
                Resource: !GetAtt ProcessingQueue.Arn
              - Effect: Allow
                Action:
                  - sqs:ListQueues
                Resource: "*"
        - PolicyName: !Sub "${ProjectName}-app-sns-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - sns:Publish
                  - sns:PublishBatch
                Resource: !Ref NotificationTopicArn
        - PolicyName: !Sub "${ProjectName}-app-dynamodb-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource:
                  - !GetAtt AppTable.Arn
                  - !Sub "${GetAtt AppTable.Arn}/index/*"
        - PolicyName: !Sub "${ProjectName}-app-s3-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                  - s3:ListBucket
                Resource:
                  - !Ref DataBucketArn
                  - !Sub "${DataBucketArn}/*"
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # Log Group for ECS
  ECSLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${ProjectName}/${Environment}"
      RetentionInDays: !FindInMap [EnvironmentConfig, !Ref Environment, LogRetention]
      KmsKeyId: !Ref LogsKmsKeyArn

  # ECR Repository
  ECRRepository:
    Type: AWS::ECR::Repository
    Properties:
      RepositoryName: !Sub "${ProjectName}/${Environment}"
      ImageScanningConfiguration:
        ScanOnPush: true
      LifecyclePolicy:
        LifecyclePolicyText: |
          {
            "rules": [
              {
                "rulePriority": 1,
                "description": "Keep last 10 images",
                "selection": {
                  "tagStatus": "any",
                  "countType": "imageCountMoreThan",
                  "countNumber": 10
                },
                "action": {
                  "type": "expire"
                }
              }
            ]
          }
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

  # SQS Queue
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${ProjectName}-processing-${Environment}"
      VisibilityTimeout: 300
      MessageRetentionPeriod: 1209600
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 5
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Dead Letter Queue
  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${ProjectName}-dlq-${Environment}"
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # SNS Topic
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${ProjectName}-notifications-${Environment}"
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # DynamoDB Table
  AppTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${ProjectName}-${Environment}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi1pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: gsi1
          KeySchema:
            - AttributeName: gsi1pk
              KeyType: HASH
            - AttributeName: pk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName

Outputs:
  TaskExecutionRoleArn:
    Description: ARN of the ECS task execution role
    Value: !GetAtt ECSTaskExecutionRole.Arn
    Export:
      Name: !Sub "${ProjectName}-ECSTaskExecutionRoleArn-${Environment}"

  TaskRoleArn:
    Description: ARN of the ECS task role
    Value: !GetAtt ECSTaskRole.Arn
    Export:
      Name: !Sub "${ProjectName}-ECSTaskRoleArn-${Environment}"

  ECRRepositoryUri:
    Description: URI of the ECR repository
    Value: !Sub "${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/${ECRRepository.RepositoryName}"

  ProcessingQueueUrl:
    Description: URL of the processing queue
    Value: !Ref ProcessingQueue
```

## Example 7: Lambda Authorizer with API Gateway

Complete setup for Lambda authorizer with IAM authentication for API Gateway.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Lambda authorizer with IAM authentication for API Gateway

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  ProjectName:
    Type: String
    Default: myproject
    Description: Name of the project

Resources:
  # Authorizer Lambda Function
  AuthorizerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${ProjectName}-authorizer-${Environment}"
      Runtime: python3.11
      Handler: authorizer.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Sub "lambda/${Environment}/authorizer.zip"
      Timeout: 30
      MemorySize: 256
      Role: !GetAtt AuthorizerRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Authorizer Role
  AuthorizerRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-authorizer-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: !Sub "${ProjectName}-cognito-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - cognito-idp:DescribeUserPool
                  - cognito-idp:DescribeUserPoolClient
                  - cognito-idp:ListUserPools
                  - cognito-idp:AdminGetUser
                  - cognito-idp:AdminListGroupsForUser
                Resource: !Ref UserPoolArn
        - PolicyName: !Sub "${ProjectName}-secrets-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${ProjectName}/${Environment}/*"

  # API Gateway Execution Role
  ApiGatewayExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-apigw-exec-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: apigateway.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs
      Policies:
        - PolicyName: !Sub "${ProjectName}-invoke-authorizer-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                  - lambda:InvokeAsync
                Resource: !GetAtt AuthorizerFunction.Arn
        - PolicyName: !Sub "${ProjectName}-invoke-backend-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                  - lambda:InvokeAsync
                Resource: !GetAtt BackendFunction.Arn

  # Backend Lambda Function
  BackendFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${ProjectName}-backend-${Environment}"
      Runtime: python3.11
      Handler: backend.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: !Sub "lambda/${Environment}/backend.zip"
      Timeout: 60
      MemorySize: 512
      Role: !GetAtt BackendRole.Arn
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
          LOG_LEVEL: INFO
          TABLE_NAME: !Ref ApiTableName
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Backend Role
  BackendRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${ProjectName}-backend-role-${Environment}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: !Sub "${ProjectName}-dynamodb-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource: !GetAtt ApiTable.Arn
        - PolicyName: !Sub "${ProjectName}-kms-${Environment}"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:Encrypt
                  - kms:DescribeKey
                Resource: !Ref KmsKeyArn

  # API Gateway REST API
  ApiGatewayRestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${ProjectName}-api-${Environment}"
      Description: REST API with IAM authorization
      EndpointConfiguration:
        Types:
          - REGIONAL
      MinimumCompressionSize: 1024
      Policy:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: "*"
            Action: execute-api:Invoke
            Condition:
              IpAddress:
                aws:SourceIp:
                  - !Ref AllowedCidrBlock
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # API Gateway Resource
  ApiGatewayResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ParentId: !GetAtt ApiGatewayRestApi.RootResourceId
      PathPart: items

  # API Gateway Method
  ApiGatewayMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      ResourceId: !Ref ApiGatewayResource
      HttpMethod: GET
      AuthorizationType: AWS_IAM
      RequestParameters:
        method.request.querystring.limit: false
        method.request.querystring.startkey: false
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${BackendFunction.Arn}/invocations"
        IntegrationResponses:
          - StatusCode: 200
            ResponseParameters:
              method.response.header.Access-Control-Allow-Origin: "'*'"
              method.response.header.Content-Type: "'application/json'"
        PassthroughBehavior: WHEN_NO_MATCH
      MethodResponses:
        - StatusCode: 200
          ResponseModels:
            application/json: Empty
          ResponseParameters:
            method.response.header.Access-Control-Allow-Origin: true
            method.response.header.Content-Type: true

  # API Gateway Authorizer
  ApiGatewayAuthorizer:
    Type: AWS::ApiGateway::Authorizer
    Properties:
      Name: !Sub "${ProjectName}-iam-authorizer-${Environment}"
      Type: REQUEST
      RestApiId: !Ref ApiGatewayRestApi
      AuthorizerUri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AuthorizerFunction.Arn}/invocations"
      AuthorizerCredentials: !GetAtt AuthorizerRole.Arn
      IdentitySource: method.request.header.Authorization
      AuthorizerResultTtlInSeconds: 300

  # API Gateway Deployment
  ApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn: ApiGatewayMethod
    Properties:
      RestApiId: !Ref ApiGatewayRestApi
      StageName: !Ref Environment

  # Lambda Permission for Authorizer
  AuthorizerPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref AuthorizerFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:apigateway:${AWS::Region}:${AWS::AccountId}:restapis/${ApiGatewayRestApi}/authorizers/${ApiGatewayAuthorizer}"

  # DynamoDB Table
  ApiTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Ref ApiTableName
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ApiGatewayRestApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/items"

  AuthorizerRoleArn:
    Description: ARN of the authorizer role
    Value: !GetAtt AuthorizerRole.Arn

  BackendRoleArn:
    Description: ARN of the backend role
    Value: !GetAtt BackendRole.Arn

  ApiGatewayExecutionRoleArn:
    Description: ARN of the API Gateway execution role
    Value: !GetAtt ApiGatewayExecutionRole.Arn
```
