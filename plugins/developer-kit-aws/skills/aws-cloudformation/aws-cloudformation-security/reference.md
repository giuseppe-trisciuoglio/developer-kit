# AWS CloudFormation Security - Reference

This reference guide contains detailed information about AWS CloudFormation resources and configurations for infrastructure security, encryption, and secrets management.

## AWS::KMS::Key

Creates a customer master key (CMK) in AWS Key Management Service.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| KeyPolicy | Json | Yes | The key policy document |
| Description | String | No | Description of the key |
| KeyUsage | String | No | Key usage (ENCRYPT_DECRYPT or SIGN_VERIFY) |
| EnableKeyRotation | Boolean | No | Enable automatic key rotation |
| PendingWindowInDays | Integer | No | Pending deletion window (7-30 days) |
| MultiRegion | Boolean | No | Enable multi-region key |

### Key Policy Structure

```yaml
KeyPolicy:
  Version: "2012-10-17"
  Id: "key-policy-identifier"
  Statement:
    - Sid: "EnableIAMPolicies"
      Effect: Allow
      Principal:
        AWS: "arn:aws:iam::account-id:role/role-name"
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
      Resource: "*"
    - Sid: "AllowCryptographicOperations"
      Effect: Allow
      Principal:
        AWS: "arn:aws:iam::account-id:role/role-name"
      Action:
        - kms:Encrypt
        - kms:Decrypt
        - kms:GenerateDataKey*
        - kms:ReEncrypt*
      Resource: "*"
```

### Key Policy Conditions

```yaml
Conditions:
  - StringEquals:
      aws:PrincipalOrgID: "o-organization-id"
  - StringEquals:
      aws:SourceAccount: !Ref AWS::AccountId
  - ArnEquals:
      aws:SourceArn: "arn:aws:lambda:region:account:function:function-name"
```

### Example

```yaml
Resources:
  SecureKmsKey:
    Type: AWS::KMS::Key
    Properties:
      Description: "KMS Key for sensitive data encryption"
      KeyPolicy:
        Version: "2012-10-17"
        Id: "secure-key-policy"
        Statement:
          - Sid: "EnableIAMPolicies"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AdminRole"
            Action: kms:*
            Resource: "*"
          - Sid: "AllowCryptographicOperations"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AppRole"
            Action:
              - kms:Encrypt
              - kms:Decrypt
              - kms:GenerateDataKey*
            Resource: "*"
          - Sid: "AllowAWSServiceAccess"
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
      EnableKeyRotation: true
      PendingWindowInDays: 30
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the key |
| KeyId | The unique identifier of the key |

## AWS::KMS::Alias

Creates an alias for a KMS key.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AliasName | String | Yes | The alias name (must start with 'alias/') |
| TargetKeyId | String | Yes | The key ID to associate with the alias |

### Example

```yaml
Resources:
  KmsKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "alias/application-${Environment}"
      TargetKeyId: !Ref SecureKmsKey
```

## AWS::SecretsManager::Secret

Creates a secret in AWS Secrets Manager.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | The name of the secret |
| Description | String | No | Description of the secret |
| SecretString | String | No | The secret value |
| SecretStringTemplate | String | No | JSON template for secret values |
| GenerateSecretString | SecretGenerator | No | Generate secret automatically |
| KmsKeyId | String | No | KMS key ID for encryption |
| RotationRules | RotationRules | No | Automatic rotation configuration |
| RotationLambdaARN | String | No | Lambda function ARN for rotation |
| ResourcePolicy | Json | No | Resource-based policy |

### SecretGenerator Structure

```yaml
GenerateSecretString:
  SecretStringTemplate: '{"username": "admin"}'
  GenerateSecretKey: "password"
  PasswordLength: 32
  ExcludeCharacters: '"@/\\'
  ExcludeLowercase: false
  ExcludeUppercase: false
  ExcludeNumbers: false
  ExcludePunctuation: true
```

### RotationRules Structure

```yaml
RotationRules:
  AutomaticallyAfterDays: 30
  Duration: 8h
  ScheduleExpression: "rate(30 days)"
```

### Resource Policy Example

```yaml
ResourcePolicy:
  Version: "2012-10-17"
  Statement:
    - Sid: "AllowLambdaAccess"
      Effect: Allow
      Principal:
        AWS: "arn:aws:iam::account-id:role/LambdaRole"
      Action:
        - secretsmanager:GetSecretValue
        - secretsmanager:DescribeSecret
      Resource: "*"
      Condition:
        StringEquals:
          aws:ResourceTag/Environment: "production"
```

### Example

```yaml
Resources:
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/database/credentials"
      Description: "Database credentials with automatic rotation"
      SecretString: !Sub |
        {
          "username": "${DBUsername}",
          "password": "${DBPassword}",
          "host": "${DBHost}",
          "port": "${DBPort}"
        }
      KmsKeyId: !Ref SecretsKmsKeyId
      RotationRules:
        AutomaticallyAfterDays: 30
      ResourcePolicy:
        Version: "2012-10-17"
        Statement:
          - Sid: "AllowAppAccess"
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:role/AppRole"
            Action:
              - secretsmanager:GetSecretValue
            Resource: "*"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the secret |
| Name | The name of the secret |

## AWS::SSM::Parameter

Creates a parameter in AWS Systems Manager Parameter Store.

### Parameter Types

| Type | Description |
|------|-------------|
| String | Plain text parameter |
| StringList | Comma-separated list |
| SecureString | Encrypted parameter |

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | No | The parameter name |
| Type | String | Yes | Parameter type (String, StringList, SecureString) |
| Value | String | Yes | The parameter value |
| Description | String | No | Description of the parameter |
| AllowedPattern | String | No | Regex pattern for validation |
| NoEcho | Boolean | No | Hide value in console |

### Example

```yaml
Parameters:
  DBCredentials:
    Type: AWS::SSM::Parameter::Value<SecureString>
    NoEcho: true
    Description: Database credentials
    Value: "/app/database/credentials"

  ApiEndpoint:
    Type: AWS::SSM::Parameter::Value<String>
    Description: API endpoint URL
    Value: "https://api.example.com"

  AllowedIPs:
    Type: AWS::SSM::Parameter::Value<StringList>
    Description: List of allowed IP addresses
    Value: "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

Resources:
  CustomParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Name: !Sub "/${AWS::StackName}/custom/setting"
      Type: SecureString
      Value: "sensitive-value"
      Description: "Custom secure parameter"
      AllowedPattern: "^[a-zA-Z0-9_-]+$"
```

## AWS::IAM::Role

Creates an IAM role for AWS services or cross-account access.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| RoleName | String | No | The name of the role |
| AssumeRolePolicyDocument | Json | Yes | Trust policy document |
| ManagedPolicyArns | List | No | AWS managed policies |
| Policies | List | No | Inline policies |
| PermissionsBoundary | String | No | Permissions boundary ARN |
| MaxSessionDuration | Integer | No | Max session duration (3600-43200) |
| Description | String | No | Description of the role |

### Assume Role Policy Examples

```yaml
# Service role for Lambda
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

# Cross-account role
AssumeRolePolicyDocument:
  Version: "2012-10-17"
  Statement:
    - Effect: Allow
      Principal:
        AWS:
          - !Sub "arn:aws:iam::account-id:root"
      Action: sts:AssumeRole
      Condition:
        StringEquals:
          aws:PrincipalAccount: "trusted-account-id"
        Bool:
          aws:MultiFactorAuthPresent: true
```

### Example

```yaml
Resources:
  SecureRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-secure-role"
      Description: "IAM role with least privilege"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      MaxSessionDuration: 3600
      PermissionsBoundary: !Ref PermissionsBoundary
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SecretsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref SecretArn
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the role |
| RoleName | The name of the role |

## AWS::EC2::SecurityGroup

Creates a security group for VPC resources.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GroupName | String | No | The name of the security group |
| GroupDescription | String | Yes | Description of the group |
| VpcId | String | No | VPC ID (required for non-default VPC) |
| SecurityGroupIngress | List | No | Inbound rules |
| SecurityGroupEgress | List | No | Outbound rules |
| Tags | List | No | Tags for the group |

### Security Group Rule Structure

```yaml
SecurityGroupIngress:
  - IpProtocol: tcp
    FromPort: 443
    ToPort: 443
    CidrIp: 0.0.0.0/0
    Description: "HTTPS from internet"
  - IpProtocol: tcp
    FromPort: 5432
    ToPort: 5432
    SourceSecurityGroupId: !Ref AppSecurityGroup
    Description: "PostgreSQL from app tier"
```

### Example

```yaml
Resources:
  SecureSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${AWS::StackName}-secure-sg"
      GroupDescription: "Security group with restricted rules"
      VpcId: !Ref VPCId
      Tags:
        - Key: Environment
          Value: !Ref Environment
      SecurityGroupIngress:
        # HTTPS from ALB
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: "HTTPS from ALB"

        # SSH from bastion only
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          SourceSecurityGroupId: !Ref BastionSecurityGroup
          Description: "SSH from bastion host"

      SecurityGroupEgress:
        # HTTPS outbound
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: "HTTPS outbound"
```

## AWS::CertificateManager::Certificate

Creates an SSL/TLS certificate in AWS Certificate Manager.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| DomainName | String | Yes | Primary domain name |
| SubjectAlternativeNames | List | No | Additional domain names |
| DomainValidationOptions | List | No | Domain validation settings |
| ValidationMethod | String | No | Validation method (DNS or EMAIL) |
| Options | CertificateOptions | No | Additional certificate options |

### CertificateOptions Structure

```yaml
Options:
  CertificateTransparencyLoggingPreference: ENABLED | DISABLED
```

### Example

```yaml
Resources:
  SSLCertificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: example.com
      SubjectAlternativeNames:
        - "*.example.com"
        - "api.example.com"
      ValidationMethod: DNS
      DomainValidationOptions:
        - DomainName: example.com
          Route53HostedZoneId: !Ref HostedZoneId
        - DomainName: "*.example.com"
          Route53HostedZoneId: !Ref HostedZoneId
      Options:
        CertificateTransparencyLoggingPreference: ENABLED
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the certificate |
| DomainName | The primary domain name |

## AWS::WAFv2::WebACL

Creates a Web ACL for AWS WAF.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | The name of the Web ACL |
| Scope | String | Yes | CLOUDFRONT or REGIONAL |
| DefaultAction | Action | Yes | Default action for unmatched requests |
| Rules | List | No | List of rules |
| VisibilityConfig | VisibilityConfig | Yes | CloudWatch metrics configuration |

### Rule Structure

```yaml
Rules:
  - Name: "RateLimitRule"
    Priority: 1
    Statement:
      RateBasedStatement:
        Limit: 2000
        EvaluationWindowSec: 60
        AggregationKeyType: IP
    Action:
      Block:
        CustomResponse:
          ResponseCode: 429
          ResponseBody: "Too many requests"
    VisibilityConfig:
      SampledRequestsEnabled: true
      CloudWatchMetricsEnabled: true
      MetricName: RateLimitRule
```

### Action Types

```yaml
Action:
  Block:
    CustomResponse:
      ResponseCode: 403
      ResponseBody: "Request blocked"
      ResponseHeaders:
        - Name: X-Frame-Options
          Value: DENY
  Allow:
    CustomRequestHandling:
      InsertHeaders:
        - Name: X-Content-Type-Options
          Value: nosniff
  Count: {}
```

### Example

```yaml
Resources:
  SecureWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-waf"
      Scope: REGIONAL
      DefaultAction:
        Allow: {}
      Rules:
        - Name: BlockSQLInjection
          Priority: 1
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
                ResponseBody: "Request blocked - SQL injection detected"
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: BlockSQLInjection

        - Name: BlockXSS
          Priority: 2
          Statement:
            XssMatchStatement:
              FieldToMatch:
                QueryString:
                  OversizeHandling: CONTINUE
          Action:
            Block:
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: BlockXSS

        - Name: ManagedRuleSet
          Priority: 3
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
              Version: Version_1.0
              ExcludedRules:
                - Name: SizeRestrictions_BODY
          Action:
            Count: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: ManagedRuleSet

      VisibilityConfig:
        CloudWatchMetricsEnabled: true
        MetricName: !Sub "${AWS::StackName}-WAF"
        SampledRequestsEnabled: true
```

## AWS::Logs::LogGroup

Creates a CloudWatch Logs log group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| LogGroupName | String | Yes | The name of the log group |
| RetentionInDays | Integer | No | Retention period in days |
| KmsKeyId | String | No | KMS key ID for encryption |
| LogGroupClass | String | No | Log group class (STANDARD or INFREQUENT_ACCESS) |

### Example

```yaml
Resources:
  EncryptedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/${AWS::StackName}/application"
      RetentionInDays: 30
      KmsKeyId: !Ref ApplicationKmsKey
      LogGroupClass: STANDARD
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the log group |

## AWS::EC2::VPCEndpoint

Creates a VPC endpoint for private connectivity to AWS services.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| VpcId | String | Yes | The VPC ID |
| ServiceName | String | Yes | The service name |
| VpcEndpointType | String | No | Interface or Gateway |
| Subnets | List | Cond | Subnets for interface endpoints |
| SecurityGroups | List | Cond | Security groups for interface endpoints |
| PrivateDnsEnabled | Boolean | No | Enable private DNS |

### Example

```yaml
Resources:
  SecretsManagerEndpoint:
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

  S3Endpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VPCId
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.s3"
      VpcEndpointType: Gateway
      RouteTableIds:
        - !Ref PrivateRouteTable1
        - !Ref PrivateRouteTable2
```

## Intrinsic Functions per Security

### !GetAtt per Risorse di Sicurezza

```yaml
# Get KMS key ARN
KmsKeyArn: !GetAtt ApplicationKmsKey.Arn

# Get secret ARN
SecretArn: !Ref DatabaseSecret

# Get security group ID
SecurityGroupId: !Ref ApplicationSecurityGroup

# Get log group ARN
LogGroupArn: !GetAtt EncryptedLogGroup.Arn
```

### !Sub con Variabili AWS

```yaml
# Construct ARN with account and region
RoleArn: !Sub "arn:aws:iam::${AWS::AccountId}:role/${RoleName}"

# Construct secret name
SecretName: !Sub "${AWS::StackName}/${Service}/${Environment}"
```

### !ImportValue per Cross-Stack References

```yaml
# Import from network stack
VPCId: !ImportValue !Sub "${NetworkStackName}-VPCId"

# Import with function
SecurityGroupId: !ImportValue
  Fn::Sub: "${NetworkStackName}-SecurityGroupId"
```

## Condition Functions per Security

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  EnableDetailedMonitoring: !Equals [!Ref Environment, production]
  UseCustomKMS: !Not [!Equals [!Ref KMSKeyId, ""]]
  EnableCrossAccount: !Equals [!Ref EnableCrossAccountAccess, true]

Resources:
  # Conditional KMS key
  ConditionalKmsKey:
    Type: AWS::KMS::Key
    Condition: UseCustomKMS
    Properties:
      Description: "Conditional KMS key"
      KeyPolicy: !Ref KeyPolicy

  # Conditional encryption
  EncryptedResource:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: !If [UseCustomKMS, aws:kms, AES256]
              KMSMasterKeyID: !If [UseCustomKMS, !Ref CustomKmsKey, !Ref AWS::NoValue]
```

## KMS Key States

| State | Description |
|-------|-------------|
| Enabled | Key is available for use |
| Disabled | Key is not available for use |
| PendingDeletion | Key is scheduled for deletion |
| PendingImport | Key is being imported |
| Unavailable | Key is unavailable |

## Secrets Manager Limits

| Resource | Limit |
|----------|-------|
| Secrets per account | 500,000 |
| Secret size | 65,536 bytes |
| Version stages | 20 per version |
| Rotation attempts | 3 per day |

## Security Group Limits

| Resource | Limit |
|----------|-------|
| Rules per security group | 60 inbound + 60 outbound |
| Security groups per VPC | 2,500 |
| Security groups per instance | 5 |

## Common Security Tags

```yaml
Resources:
  SecureResource:
    Type: AWS::KMS::Key
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: ManagedBy
          Value: CloudFormation
        - Key: SecurityClassification
          Value: "confidential"
        - Key: Compliance
          Value: "SOC2,ISO27001"
        - Key: Owner
          Value: "security-team@example.com"
```
