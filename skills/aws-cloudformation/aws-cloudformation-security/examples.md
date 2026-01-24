# AWS CloudFormation Security - Examples

This file contains comprehensive examples for AWS CloudFormation security patterns with production-ready configurations.

## Example 1: Complete KMS Security Stack

Complete KMS key setup with encryption, key rotation, and proper access policies.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete KMS security configuration with key rotation and policies

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  OrganizationId:
    Type: String
    Description: AWS Organization ID for condition

Mappings:
  KeyPolicyConfig:
    dev:
      EnableKeyRotation: true
      PendingWindowDays: 7
    staging:
      EnableKeyRotation: true
      PendingWindowDays: 14
    production:
      EnableKeyRotation: true
      PendingWindowDays: 30

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  # Master KMS Key per applicazione
  ApplicationKmsKey:
    Type: AWS::KMS::Key
    Properties:
      Description: !Sub "Master encryption key for ${Environment} environment"
      KeyPolicy:
        Version: "2012-10-17"
        Id: !Sub "${AWS::StackName}-key-policy"
        Statement:
          # Enable IAM policies for key administration
          - Sid: "EnableIAMPolicies"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action:
              - kms:Create*
              - kms:Describe*
              - kms:Enable*
              - kms:List*
              - kms:Put*
              - kms:Update*
              - kms:Revoke*
              - kms:Disable*
              - kms:Get*
              - kms:Delete*
              - kms:TagResource
              - kms:UntagResource
              - kms:CancelKeyDeletion
              - kms:ScheduleKeyDeletion
            Resource: "*"
            Condition:
              StringEquals:
                aws:PrincipalOrgID: !Ref OrganizationId

          # Allow cryptographic operations for application roles
          - Sid: "AllowCryptographicOperations"
            Effect: Allow
            Principal:
              AWS:
                - !Sub "arn:aws:iam::${AWS::AccountId}:role/LambdaExecutionRole"
                - !Sub "arn:aws:iam::${AWS::AccountId}:role/ECSTaskRole"
                - !Sub "arn:aws:iam::${AWS::AccountId}:role/RDSInstanceRole"
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
              - kms:ReEncrypt*
              - kms:DescribeKey
            Resource: "*"

          # Allow S3 to use key for bucket encryption
          - Sid: "AllowS3Encryption"
            Effect: Allow
            Principal:
              Service: s3.amazonaws.com
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"
            Condition:
              StringEquals:
                aws:SourceAccount: !Ref AWS::AccountId

          # Allow RDS to use key for database encryption
          - Sid: "AllowRDSEncryption"
            Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"
            Condition:
              StringEquals:
                aws:SourceAccount: !Ref AWS::AccountId

          # Deny access to all principals not in the organization
          - Sid: "DenyOutsideOrganization"
            Effect: Deny
            Principal: "*"
            Action: kms:*
            Resource: "*"
            Condition:
              StringNotEquals:
                aws:PrincipalOrgID: !Ref OrganizationId

      KeyUsage: ENCRYPT_DECRYPT
      EnableKeyRotation: !FindInMap [KeyPolicyConfig, !Ref Environment, EnableKeyRotation]
      PendingWindowInDays: !FindInMap [KeyPolicyConfig, !Ref Environment, PendingWindowDays]
      MultiRegion: !Ref IsProduction

  # Alias per la chiave
  ApplicationKmsKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "alias/application-${Environment}"
      TargetKeyId: !Ref ApplicationKmsKey

  # S3 Bucket Encryption Key
  S3EncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "KMS Key for S3 bucket encryption"
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "EnableIAMAdmin"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action: kms:*
            Resource: "*"
          - Sid: "AllowS3Service"
            Effect: Allow
            Principal:
              Service: s3.amazonaws.com
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"
      EnableKeyRotation: true

  # RDS Encryption Key
  RdsEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "KMS Key for RDS database encryption"
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "EnableIAMAdmin"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action: kms:*
            Resource: "*"
          - Sid: "AllowRDSService"
            Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"

  # Secrets Manager Encryption Key
  SecretsEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "KMS Key for Secrets Manager encryption"
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "EnableIAMAdmin"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action: kms:*
            Resource: "*"
          - Sid: "AllowSecretsManager"
            Effect: Allow
            Principal:
              Service: secretsmanager.amazonaws.com
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"

Outputs:
  ApplicationKeyArn:
    Description: ARN of the application KMS key
    Value: !GetAtt ApplicationKmsKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-AppKeyArn"

  S3KeyArn:
    Description: ARN of the S3 encryption KMS key
    Value: !GetAtt S3EncryptionKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-S3KeyArn"

  RdsKeyArn:
    Description: ARN of the RDS encryption KMS key
    Value: !GetAtt RdsEncryptionKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-RdsKeyArn"

  SecretsKeyArn:
    Description: ARN of the Secrets Manager encryption KMS key
    Value: !GetAtt SecretsEncryptionKey.Arn
    Export:
      Name: !Sub "${AWS::StackName}-SecretsKeyArn"
```

## Example 2: Secrets Manager con Rotazione Automatica

Complete secrets configuration with automatic rotation and resource policies.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Secrets Manager configuration with automatic rotation

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  DBUsername:
    Type: String
    Description: Database username
    Default: appuser

  DBHost:
    Type: String
    Description: Database host

  DBName:
    Type: String
    Description: Database name

Resources:
  # Database credentials secret
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/database/credentials"
      Description: "Database credentials for ${Environment} environment"
      SecretString: !Sub |
        {
          "username": "${DBUsername}",
          "password": "${DBPassword}",
          "host": "${DBHost}",
          "port": "5432",
          "dbname": "${DBName}",
          "engine": "postgresql"
        }
      KmsKeyId: !GetAtt SecretsEncryptionKey.Arn
      RotationRules:
        AutomaticallyAfterDays: 30
      ResourcePolicy:
        Version: "2012-10-17"
        Statement:
          # Allow application roles to read secret
          - Sid: "AllowAppReadAccess"
            Effect: Allow
            Principal:
              AWS:
                - !Sub "arn:aws:iam::${AWS::AccountId}:role/LambdaExecutionRole"
                - !Sub "arn:aws:iam::${AWS::AccountId}:role/ECSTaskRole"
            Action:
              - secretsmanager:GetSecretValue
              - secretsmanager:DescribeSecret
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/Environment: !Ref Environment

          # Allow rotation lambda to manage secret
          - Sid: "AllowRotationAccess"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/SecretRotationRole"
            Action:
              - secretsmanager:GetSecretValue
              - secretsmanager:PutSecretValue
              - secretsmanager:DescribeSecret
            Resource: "*"

          # Deny access without encryption context
          - Sid: "DenyUnencryptedAccess"
            Effect: Deny
            Principal: "*"
            Action:
              - secretsmanager:GetSecretValue
            Resource: "*"
            Condition:
              StringNotEquals:
                kms:ViaService: !Sub "secretsmanager.${AWS::Region}.amazonaws.com"
              StringNotEquals:
                kms:EncryptContext: !Sub "secret:${AWS::StackName}"

      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation
        - Key: RotationEnabled
          Value: "true"

  # API credentials secret
  ApiCredentialsSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/api/credentials"
      Description: "External API credentials"
      SecretString: !Sub |
        {
          "api_key": "${ExternalApiKey}",
          "api_secret": "${ExternalApiSecret}",
          "api_endpoint": "https://api.example.com"
        }
      KmsKeyId: !GetAtt SecretsEncryptionKey.Arn
      ResourcePolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "AllowAppAccess"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/LambdaExecutionRole"
            Action:
              - secretsmanager:GetSecretValue
            Resource: "*"

  # Generated secret for service accounts
  ServiceAccountSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/service/account"
      Description: "Generated service account credentials"
      GenerateSecretString:
        SecretStringTemplate: '{"username": "service_account"}'
        GenerateSecretKey: "password"
        PasswordLength: 64
        ExcludeCharacters: '"@/\\'
      KmsKeyId: !GetAtt SecretsEncryptionKey.Arn
      RotationRules:
        AutomaticallyAfterDays: 90
      ResourcePolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "AllowServiceAccess"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/ServiceRole"
            Action:
              - secretsmanager:GetSecretValue
            Resource: "*"

  # Cross-account shared secret
  SharedSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/shared/cross-account"
      Description: "Secret shared with partner account"
      SecretString: "{}"
      KmsKeyId: !GetAtt SecretsEncryptionKey.Arn
      ResourcePolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "AllowPartnerAccess"
            Effect: Allow
            Principal:
              AWS:
                - !Sub "arn:aws:iam::${PartnerAccountId}:role/PartnerSecretReader"
            Action:
              - secretsmanager:GetSecretValue
              - secretsmanager:DescribeSecret
            Resource: "*"
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: true

  # Secrets Manager VPC Endpoint
  SecretsManagerVPCEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPCId
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.secretsmanager"
      VpcEndpointType: Interface
      Subnets:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      SecurityGroups:
        - !Ref AppSecurityGroup
      PrivateDnsEnabled: true

Outputs:
  DatabaseSecretArn:
    Description: ARN of the database secret
    Value: !Ref DatabaseSecret

  ApiSecretArn:
    Description: ARN of the API credentials secret
    Value: !Ref ApiCredentialsSecret
```

## Example 3: IAM Security con Least Privilege

Complete IAM configuration with granular permissions, permissions boundaries, and conditions.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: IAM security configuration with least privilege

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  # Permissions Boundary Policy
  PermissionsBoundaryPolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      Description: "Permissions boundary for application roles"
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          # Deny all actions not explicitly allowed
          - Sid: "DenyAllOutsideSpecifiedResources"
            Effect: Deny
            Action:
              - "*"
            Resource: "*"
            Condition:
              StringNotEqualsIfExists:
                aws:ResourceTag/Environment: !Ref Environment
              ArnNotEqualsIfExists:
                aws:SourceArn: !Sub "arn:aws:s3:::${DataBucketName}/*"

          # Deny modification of security-critical resources
          - Sid: "DenySecurityModification"
            Effect: Deny
            Action:
              - iam:DeleteUserPolicy
              - iam:DeleteRolePolicy
              - iam:DeleteGroupPolicy
              - iam:PutUserPolicy
              - iam:PutRolePolicy
              - iam:PutGroupPolicy
              - iam:AttachUserPolicy
              - iam:AttachRolePolicy
              - iam:AttachGroupPolicy
              - iam:DetachUserPolicy
              - iam:DetachRolePolicy
              - iam:DetachGroupPolicy
            Resource: "*"
            Condition:
              Bool:
                aws:MultiFactorAuthPresent: false

  # Lambda Execution Role con permessi minimi
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-role"
      Description: "Lambda execution role with least privilege"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                aws:SourceAccount: !Ref AWS::AccountId
                lambda:SourceFunctionArn: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:${AWS::StackName}-*"
      PermissionsBoundary: !Ref PermissionsBoundaryPolicy
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      Policies:
        # Secrets access policy
        - PolicyName: SecretsAccessPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                  - secretsmanager:DescribeSecret
                Resource:
                  - !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${AWS::StackName}/*"
                  - !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${Environment}/*"
                Condition:
                  StringEquals:
                    secretsmanager:SecretTarget: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${AWS::StackName}/database/*"

        # S3 access policy
        - PolicyName: S3AccessPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource:
                  - !Sub "${DataBucket.Arn}/*"
                Condition:
                  StringEquals:
                    s3:ResourceAccount: !Ref AWS::AccountId
                  IpAddress:
                    aws:SourceIp: !If [IsProduction, !Ref AllowedIPRange, "0.0.0.0/0"]

              - Effect: Deny
                Action:
                  - s3:DeleteObject*
                Resource:
                  - !Sub "${DataBucket.Arn}/*"
                Condition:
                  Bool:
                    aws:MultiFactorAuthPresent: false

        # CloudWatch Logs policy
        - PolicyName: CloudWatchLogsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogStreams
                Resource:
                  - !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:/aws/lambda/${AWS::StackName}-*"
                Condition:
                  StringEquals:
                    aws:ResourceTag/Environment: !Ref Environment

        # DynamoDB access policy
        - PolicyName: DynamoDBPolicy
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
                  - !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${AWS::StackName}-table"
                  - !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${AWS::StackName}-table/index/*"
                Condition:
                  ForAllValue:StringEquals:
                    dynamodb:Attributes: !Ref AllowedAttributes
                  ForAnyValue:StringLike:
                    dynamodb:Select: SPECIFIC_ATTRIBUTES

      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: LeastPrivilege
          Value: "true"

  # Cross-account access role
  CrossAccountRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-cross-account-role"
      Description: "Role for cross-account access with MFA requirement"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS:
                - !Sub "arn:aws:iam::${ProductionAccountId}:root"
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                aws:PrincipalAccount: !Ref ProductionAccountId
              Bool:
                aws:MultiFactorAuthPresent: true
      MaxSessionDuration: 3600
      Policies:
        - PolicyName: CrossAccountReadOnlyPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject*
                  - s3:List*
                Resource:
                  - !Sub "${SharedBucket.Arn}"
                  - !Sub "${SharedBucket.Arn}/*"

              - Effect: Allow
                Action:
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:GetItem
                Resource:
                  - !Sub "${SharedTable.Arn}"
                  - !Sub "${SharedTable.Arn}/index/*"

              - Effect: Deny
                Action:
                  - s3:DeleteObject*
                  - s3:PutObject*
                  - dynamodb:DeleteItem*
                  - dynamodb:PutItem*
                  - dynamodb:UpdateItem*
                Resource:
                  - !Sub "${SharedBucket.Arn}/*"
                  - !Sub "${SharedTable.Arn}"

  # IAM User with access keys
  ServiceUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${AWS::StackName}-service-user"
      Groups:
        - !Ref ServiceUserGroup

  ServiceUserGroup:
    Type: AWS::IAM::Group
    Properties:
      GroupName: !Sub "${AWS::StackName}-service-group"
      Policies:
        - PolicyName: ServiceUserPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:GetObject
                Resource:
                  - !Sub "${UploadBucket.Arn}/*"

Outputs:
  LambdaRoleArn:
    Description: ARN of the Lambda execution role
    Value: !GetAtt LambdaExecutionRole.Arn

  CrossAccountRoleArn:
    Description: ARN of the cross-account role
    Value: !GetAtt CrossAccountRole.Arn

  ServiceUserArn:
    Description: ARN of the service user
    Value: !GetAtt ServiceUser.Arn
```

## Example 4: VPC Security Groups Configuration

Complete security group configuration with layered security.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC security groups with defense in depth

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  # Security Group per ALB (front-end)
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-alb-sg"
      GroupDescription: "Security group for application load balancer"
      VpcId: !Ref VPCId
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-alb-sg"
        - Key: Environment
          Value: !Ref Environment
        - Key: Tier
          Value: "front-end"

      SecurityGroupIngress:
        # HTTP from internet
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: "HTTP from internet (redirect to HTTPS)"

        # HTTPS from internet
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: "HTTPS from internet"

      SecurityGroupEgress:
        # Only to application security group
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: "HTTP to application tier"

        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: "HTTPS to application tier"

  # Security Group per Application tier
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-app-sg"
      GroupDescription: "Security group for application tier"
      VpcId: !Ref VPCId
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-app-sg"
        - Key: Environment
          Value: !Ref Environment
        - Key: Tier
          Value: "application"

      SecurityGroupIngress:
        # From ALB only
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: "Application port from ALB"

        # From bastion for SSH (if needed)
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          SourceSecurityGroupId: !Ref BastionSecurityGroup
          Description: "SSH from bastion host"

        # ICMP for health checks
        - IpProtocol: icmp
          FromPort: -1
          ToPort: -1
          SourceSecurityGroupId: !Ref BastionSecurityGroup
          Description: "ICMP from bastion"

      SecurityGroupEgress:
        # HTTPS for external API calls
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: "HTTPS for external APIs"

        # DNS for name resolution
        - IpProtocol: udp
          FromPort: 53
          ToPort: 53
          CidrIp: 10.0.0.0/16
          Description: "DNS for VPC resolution"

        # To database tier
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref DatabaseSecurityGroup
          Description: "PostgreSQL to database tier"

  # Security Group per Database tier
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-db-sg"
      GroupDescription: "Security group for database tier"
      VpcId: !Ref VPCId
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-db-sg"
        - Key: Environment
          Value: !Ref Environment
        - Key: Tier
          Value: "database"

      SecurityGroupIngress:
        # From application tier only
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: "PostgreSQL from application tier"

        # From bastion for administration (with MFA)
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref BastionSecurityGroup
          Description: "PostgreSQL from bastion for admin"

      SecurityGroupEgress:
        # Minimal outbound - only for security updates
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: "HTTPS for security patches"

  # Security Group per Cache tier (Redis/Memcached)
  CacheSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-cache-sg"
      GroupDescription: "Security group for cache tier"
      VpcId: !Ref VPCId
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-cache-sg"
        - Key: Environment
          Value: !Ref Environment
        - Key: Tier
          Value: "cache"

      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 6379
          ToPort: 6379
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: "Redis from application tier"

      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: "HTTPS for updates"

  # Bastion Security Group
  BastionSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-bastion-sg"
      GroupDescription: "Security group for bastion host"
      VpcId: !Ref VPCId
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-bastion-sg"
        - Key: Environment
          Value: !Ref Environment
        - Key: Tier
          Value: "bastion"

      SecurityGroupIngress:
        # SSH from corporate VPN or specific IPs
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHIP
          Description: "SSH from allowed IP range"

      SecurityGroupEgress:
        # To all internal tiers
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: "SSH to application"

        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref DatabaseSecurityGroup
          Description: "SSH to database for tunneling"

Outputs:
  ALBSecurityGroupId:
    Description: ID of the ALB security group
    Value: !Ref ALBSecurityGroup
    Export:
      Name: !Sub "${AWS::StackName}-ALBSGId"

  AppSecurityGroupId:
    Description: ID of the application security group
    Value: !Ref AppSecurityGroup
    Export:
      Name: !Sub "${AWS::StackName}-AppSGId"

  DatabaseSecurityGroupId:
    Description: ID of the database security group
    Value: !Ref DatabaseSecurityGroup
    Export:
      Name: !Sub "${AWS::StackName}-DBSGId"
```

## Example 5: TLS/SSL con ACM e API Gateway

Complete SSL certificate setup with API Gateway and custom domain.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: SSL certificates and API Gateway with TLS enforcement

Parameters:
  DomainName:
    Type: String
    Description: Primary domain name

  HostedZoneId:
    Type: AWS::Route53::HostedZone::Id
    Description: Route 53 hosted zone ID

  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

Resources:
  # SSL Certificate with DNS validation
  SSLCertificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: !Ref DomainName
      SubjectAlternativeNames:
        - !Sub "*.${DomainName}"
        - !Sub "api.${DomainName}"
        - !Sub "${Environment}.${DomainName}"
      ValidationMethod: DNS
      DomainValidationOptions:
        - DomainName: !Ref DomainName
          Route53HostedZoneId: !Ref HostedZoneId
        - DomainName: !Sub "*.${DomainName}"
          Route53HostedZoneId: !Ref HostedZoneId
      Options:
        CertificateTransparencyLoggingPreference: ENABLED
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation

  # Regional certificate for API Gateway
  RegionalCertificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: !Sub "${Environment}.${DomainName}"
      ValidationMethod: DNS
      DomainValidationOptions:
        - DomainName: !Sub "${Environment}.${DomainName}"
          Route53HostedZoneId: !Ref HostedZoneId

  # Secure API Gateway
  SecureApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${AWS::StackName}-api-${Environment}"
      Description: "Secure REST API with TLS enforcement"
      EndpointConfiguration:
        Types:
          - REGIONAL
      MinimumCompressionSize: 2048

      # Policy to deny non-SSL access
      Policy:
        Version: "2012-10-17"
        Statement:
          - Effect: Deny
            Principal: "*"
            Action: execute-api:Invoke
            Resource: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${SecureApiGateway}/*"
            Condition:
              Bool:
                aws:SecureTransport: "false"
          - Effect: Allow
            Principal: "*"
            Action: execute-api:Invoke
            Resource: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${SecureApiGateway}/*"

  # API Gateway Deployment
  ApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn:
      - ApiGatewayMethodGet
    Properties:
      RestApiId: !Ref SecureApiGateway
      StageName: !Ref Environment

  # API Gateway Stage
  ApiGatewayStage:
    Type: AWS::ApiGateway::Stage
    Properties:
      RestApiId: !Ref SecureApiGateway
      StageName: !Ref Environment
      DeploymentId: !Ref ApiGatewayDeployment
      StageDescription:
        LoggingLevel: INFO
        DataTraceEnabled: false
        ThrottlingRateLimit: 1000
        ThrottlingBurstLimit: 2000
      MethodSettings:
        - ResourcePath: "/*"
          HttpMethod: "*"
          LoggingLevel: INFO
          DataTraceEnabled: false
          ThrottlingRateLimit: 1000
          ThrottlingBurstLimit: 2000

  # API Gateway Domain
  ApiGatewayDomain:
    Type: AWS::ApiGateway::DomainName
    Properties:
      DomainName: !Sub "api.${DomainName}"
      RegionalCertificateArn: !Ref RegionalCertificate
      EndpointConfiguration:
        Types:
          - REGIONAL

  # API Gateway Base Path Mapping
  ApiBasePathMapping:
    Type: AWS::ApiGateway::BasePathMapping
    Properties:
      DomainName: !Ref ApiGatewayDomain
      RestApiId: !Ref SecureApiGateway
      Stage: !Ref Environment

  # Route 53 DNS records for API domain
  ApiGatewayDNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      Name: !Sub "api.${DomainName}."
      Type: A
      AliasTarget:
        DNSName: !GetAtt ApiGatewayDomain.RegionalHostname
        HostedZoneId: !GetAtt ApiGatewayDomain.RegionalHostedZoneId
        EvaluateTargetHealth: true
      HostedZoneId: !Ref HostedZoneId

  # Lambda Function URL con IAM authentication
  SecureLambdaUrl:
    Type: AWS::Lambda::Url
    Properties:
      AuthType: AWS_IAM
      TargetFunctionArn: !GetAtt LambdaFunction.Arn
      Cors:
        AllowCredentials: true
        AllowHeaders:
          - Authorization
          - Content-Type
          - X-Request-ID
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        AllowOrigins:
          - !Sub "https://${DomainName}"
          - !Sub "https://${Environment}.${DomainName}"
        MaxAge: 86400
      InvokeMode: BUFFERED

  # Lambda Permission for URL
  LambdaPermissionForUrl:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref LambdaFunction
      Action: lambda:InvokeFunctionUrl
      Principal: "*"

  # WAF Web ACL for API Gateway
  WebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-waf"
      Scope: REGIONAL
      DefaultAction:
        Allow: {}
      Rules:
        - Name: AWSManagedRulesCommonRuleSet
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: CommonRuleSet

        - Name: RateLimit
          Priority: 2
          Statement:
            RateBasedStatement:
              Limit: 2000
              EvaluationWindowSec: 60
              AggregationKeyType: IP
          Action:
            Block:
              CustomResponse:
                ResponseCode: 429
                ResponseBody: "Rate limit exceeded"
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: RateLimitRule

        - Name: BlockSQLi
          Priority: 3
          Statement:
            SqliMatchStatement:
              FieldToMatch:
                Body:
                  OversizeHandling: CONTINUE
              SensitivityLevel: HIGH
          Action:
            Block:
              CustomResponse:
                ResponseCode: 403
                ResponseBody: "Invalid request"
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: BlockSQLi

      VisibilityConfig:
        CloudWatchMetricsEnabled: true
        MetricName: !Sub "${AWS::StackName}-WebACL"
        SampledRequestsEnabled: true

  # Associate WAF with API Gateway
  WafAssociation:
    Type: AWS::WAFv2::WebACLAssociation
    Properties:
      WebACLArn: !GetAtt WebACL.Arn
      ResourceArn: !Sub "arn:aws:apigateway:${AWS::Region}::/restapis/${SecureApiGateway}/stages/${Environment}"

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${SecureApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"

  ApiDomainUrl:
    Description: Custom domain URL for API
    Value: !Sub "https://api.${DomainName}/${Environment}"

  CertificateArn:
    Description: ARN of the SSL certificate
    Value: !Ref SSLCertificate
```

## Example 6: Complete Encrypted Infrastructure Stack

Complete production-ready infrastructure with encryption at rest and in transit.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete encrypted infrastructure with defense in depth

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  VPCId:
    Type: AWS::EC2::VPC::Id

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  # KMS Key for encryption
  MasterKmsKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "Master encryption key for ${Environment}"
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "EnableIAMAdmin"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action: kms:*
            Resource: "*"
          - Sid: "AllowAppEncryption"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AppRole"
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"
      EnableKeyRotation: true

  # S3 Bucket con encryption
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "secure-data-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref MasterKmsKey
            BucketKeyEnabled: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: ArchiveOldVersions
            Status: Enabled
            NoncurrentVersionExpiration:
              NoncurrentDays: 90

  # Encrypted RDS Instance
  DatabaseInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub "${AWS::StackName}-db-${Environment}"
      DBInstanceClass: !FindInMap [InstanceTypes, !Ref Environment, DBInstanceClass]
      Engine: postgres
      EngineVersion: "15.4"
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      DBName: !Ref DBName
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      StorageEncrypted: true
      KmsKeyId: !Ref MasterKmsKey
      BackupRetentionPeriod: 35
      MultiAZ: !Ref IsProduction
      AutoMinorVersionUpgrade: true
      DeletionProtection: !Ref IsProduction
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Encrypted
          Value: "true"

  # Encrypted ElastiCache Redis
  CacheCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupId: !Sub "${AWS::StackName}-redis-${Environment}"
      ReplicationGroupDescription: "Redis cluster for ${Environment}"
      Engine: redis
      CacheNodeType: !FindInMap [InstanceTypes, !Ref Environment, CacheNodeType]
      NumNodeGroups: !If [IsProduction, 2, 1]
      ReplicasPerNodeGroup: !If [IsProduction, 1, 0]
      AutomaticFailoverEnabled: !Ref IsProduction
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      SecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true
      AuthToken: !Ref RedisAuthToken
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Encrypted
          Value: "true"

  # Encrypted DynamoDB Table
  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-table-${Environment}"
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
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      SSESpecification:
        SSEEnabled: true
        SSEType: KMS
        KMSMasterKeyId: !Ref MasterKmsKey
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Encrypted
          Value: "true"

  # Encrypted CloudWatch Log Group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/${AWS::StackName}/${Environment}"
      RetentionInDays: 90
      KmsKeyId: !Ref MasterKmsKey

  # Encrypted SQS Queue
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-queue-${Environment}"
      VisibilityTimeout: 300
      MessageRetentionPeriod: 1209600
      KmsMasterKeyId: !Ref MasterKmsKey
      KmsDataKeyReusePeriodSeconds: 300
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 5

  # Dead Letter Queue
  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-dlq-${Environment}"
      KmsMasterKeyId: !Ref MasterKmsKey

  # Encrypted SNS Topic
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${AWS::StackName}-notifications-${Environment}"
      KmsMasterKeyId: !Ref MasterKmsKey

  # Security Groups
  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-app-sg"
      GroupDescription: "Application security group"
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup

  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-db-sg"
      GroupDescription: "Database security group"
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref ApplicationSecurityGroup

  # VPC Endpoints per accesso privato
  S3VPCEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPCId
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.s3"
      VpcEndpointType: Gateway
      RouteTableIds: !Ref PrivateRouteTableIds

  SecretsManagerVPCEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPCId
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.secretsmanager"
      VpcEndpointType: Interface
      Subnets: !Ref PrivateSubnetIds
      SecurityGroups:
        - !Ref ApplicationSecurityGroup

Outputs:
  DataBucketName:
    Description: Name of the encrypted data bucket
    Value: !Ref DataBucket

  DatabaseEndpoint:
    Description: Database connection endpoint
    Value: !GetAtt DatabaseInstance.Endpoint.Address

  CacheEndpoint:
    Description: Redis cluster endpoint
    Value: !GetAtt CacheCluster.PrimaryEndPoint.Address

  TableName:
    Description: DynamoDB table name
    Value: !Ref DataTable

  QueueUrl:
    Description: SQS queue URL
    Value: !Ref ProcessingQueue
```
