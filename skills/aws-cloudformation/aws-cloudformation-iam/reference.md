# AWS CloudFormation IAM - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for IAM infrastructure.

## AWS::IAM::User

Creates an IAM user for your AWS account.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| UserName | String | Yes | The name of the user |
| Path | String | No | The path for the user name |
| Groups | List of String | No | A list of group names to associate with the user |
| ManagedPolicyArns | List of String | No | A list of managed policy ARNs to attach to the user |
| PermissionsBoundary | String | No | The ARN of the policy used to set the permissions boundary |
| Policies | List of Policy | No | A list of embedded policies to attach to the user |
| Tags | List of Tag | No | A list of tags to attach to the user |

### Policy Structure

```yaml
Policy:
  PolicyName: String
  PolicyDocument: PolicyDocument
```

### PolicyDocument Structure

```yaml
PolicyDocument:
  Version: String
  Statement: List of Statement
```

### Statement Structure

```yaml
Statement:
  - Sid: String
    Effect: String
    Principal: Principal
    NotPrincipal: Principal
    Action: List of String or String
    NotAction: List of String or String
    Resource: List of String or String
    NotResource: List of String or String
    Condition: Condition
```

### Example

```yaml
Resources:
  AppUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${AWS::StackName}-app-user"
      Path: /applications/
      Groups:
        - !Ref AppUserGroup
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/ReadOnlyAccess
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-custom-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Ref DataBucketArn
                  - !Sub "${DataBucketArn}/*"
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the user |
| UserId | The unique identifier for the user |

---

## AWS::IAM::Role

Creates an IAM role that you can assume to delegate permissions.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| RoleName | String | No | The name of the role |
| AssumeRolePolicyDocument | PolicyDocument | Yes | The policy that grants an entity permission to assume the role |
| ManagedPolicyArns | List of String | No | A list of managed policy ARNs to attach to the role |
| MaxSessionDuration | Integer | No | The maximum session duration in seconds (900-43200) |
| PermissionsBoundary | String | No | The ARN of the policy used to set the permissions boundary |
| Policies | List of Policy | No | A list of embedded policies to attach to the role |
| Description | String | No | A description for the role |
| Tags | List of Tag | No | A list of tags to attach to the role |

### Principal Types

```yaml
Principal:
  Service: List of String or String
  AWS: List of String or String
  Federated: List of String or String
```

### Example with Service Principal

```yaml
Resources:
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      MaxSessionDuration: 3600
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-dynamodb-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                Resource: !GetAtt DataTable.Arn
```

### Example with AWS Principal

```yaml
Resources:
  CrossAccountRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-crossaccount"
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
      Policies:
        - PolicyName: ReadOnly
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource: "*"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the role |
| RoleId | The unique identifier for the role |

---

## AWS::IAM::Policy

Creates an IAM policy for an IAM user, group, or role.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PolicyName | String | Yes | The name of the policy |
| Groups | List of String | No | A list of group names to attach the policy to |
| Roles | List of String | No | A list of role names to attach the policy to |
| Users | List of String | No | A list of user names to attach the policy to |
| ManagedPolicyArns | List of String | No | A list of additional managed policy ARNs to attach |
| PolicyDocument | PolicyDocument | Yes | The policy document |

### Example

```yaml
Resources:
  S3ReadPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-s3-read"
      Groups:
        - !Ref ReadOnlyGroup
      Roles:
        - !Ref ReadOnlyRole
      Users:
        - !Ref ReadOnlyUser
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action:
              - s3:GetObject
              - s3:GetObjectVersion
              - s3:ListBucket
            Resource:
              - !Ref DataBucketArn
              - !Sub "${DataBucketArn}/*"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the policy |

---

## AWS::IAM::ManagedPolicy

Creates a managed policy that you can attach to multiple users, groups, or roles.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ManagedPolicyName | String | No | The name of the managed policy |
| Description | String | No | A description of the managed policy |
| Path | String | No | The path for the policy name |
| Groups | List of String | No | A list of group names to attach the policy to |
| Roles | List of String | No | A list of role names to attach the policy to |
| Users | List of String | No | A list of user names to attach the policy to |
| PolicyDocument | PolicyDocument | Yes | The policy document |

### Example

```yaml
Resources:
  CustomReadOnlyPolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      ManagedPolicyName: !Sub "${AWS::StackName}-custom-readonly"
      Description: Custom read-only access policy
      Path: /custom/
      Groups:
        - !Ref AppGroup
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
              - dynamodb:Get*
              - dynamodb:Query
              - dynamodb:Scan
            Resource: "*"
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the managed policy |

---

## AWS::IAM::UserLoginProfile

Creates a password for an IAM user. The password allows access to the AWS Management Console.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| UserName | String | Yes | The name of the IAM user |
| Password | String | No | The password for the IAM user |
| PasswordResetRequired | Boolean | No | Whether the user is required to reset their password |

### Example

```yaml
Resources:
  ConsoleUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${AWS::StackName}-console-user"

  UserLoginProfile:
    Type: AWS::IAM::UserLoginProfile
    Properties:
      UserName: !Ref ConsoleUser
      Password: !Ref InitialPassword
      PasswordResetRequired: true
```

---

## AWS::IAM::AccessKey

Creates an access key and secret key for an IAM user.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| UserName | String | Yes | The name of the IAM user |
| Status | String | No | The status of the access key (Active or Inactive) |
| Serial | Integer | No | The serial number for the access key |

### Example

```yaml
Resources:
  AppUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${AWS::StackName}-app-user"

  UserAccessKey:
    Type: AWS::IAM::AccessKey
    Properties:
      UserName: !Ref AppUser
      Status: Active
      Serial: 1

  UserSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${AWS::StackName}/credentials"
      SecretString: !Sub |
        {
          "access_key": "${UserAccessKey.Ref}",
          "secret_key": "{{resolve:secretsmanager:${UserAccessKey.SecretAccessKey}}}"
        }
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| SecretAccessKey | The secret key for the access key |
| Ref | The access key ID |

---

## AWS::IAM::InstanceProfile

Creates an instance profile that can be used to pass an IAM role to an EC2 instance.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| InstanceProfileName | String | No | The name of the instance profile |
| Roles | List of String | Yes | A list of role names to associate with the instance profile |
| Path | String | No | The path for the instance profile name |

### Example

```yaml
Resources:
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-ec2-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub "${AWS::StackName}-profile"
      Roles:
        - !Ref EC2Role

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      IamInstanceProfile: !Ref EC2InstanceProfile
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the instance profile |

---

## AWS::IAM::UserToGroupAddition

Adds an IAM user to an IAM group.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GroupName | String | Yes | The name of the group |
| Users | List of String | Yes | A list of user names to add to the group |

### Example

```yaml
Resources:
  DevelopersGroup:
    Type: AWS::IAM::Group
    Properties:
      GroupName: !Sub "${AWS::StackName}-developers"
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/ReadOnlyAccess

  AppUser:
    Type: AWS::IAM::User
    Properties:
      UserName: !Sub "${AWS::StackName}-developer"

  UserGroupMembership:
    Type: AWS::IAM::UserToGroupAddition
    Properties:
      GroupName: !Ref DevelopersGroup
      Users:
        - !Ref AppUser
        - !Ref AnotherUser
```

---

## AWS::IAM::ServerCertificate

Uploads a server certificate and saves it in IAM.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ServerCertificateName | String | No | The name for the server certificate |
| CertificateBody | String | Yes | The certificate body |
| PrivateKey | String | Yes | The private key |
| CertificateChain | String | No | The certificate chain |
| Path | String | No | The path for the server certificate |

### Example

```yaml
Resources:
  SSLCertificate:
    Type: AWS::IAM::ServerCertificate
    Properties:
      ServerCertificateName: !Sub "${AWS::StackName}-ssl-cert"
      CertificateBody: |
        -----BEGIN CERTIFICATE-----
        MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
        BAYTAlVTMRUwEwYDVQQIDAxDYWxpZm9ybmlhMRYwFAYDVQQHDA1TYW4gRnJhbmNp
        c2NvMRAwDgYDVQQKDAdFeGFtcGxlMRswGQYJKoZIhvcNAQkBFgx1c2VyQGV4YW1w
        bGUuY29tMB4XDTIzMDEwMTAwMDAwMFoXDTI0MDEwMTAwMDAwMFowRTELMAkGA1UE
        BhMCVVMxFTATBgNVBAgMDENhbGlmb3JuaWExFjAUBgNVBAcMDVNhbiBGcmFuY2lz
        Y28xEDAOBgNVBAoMB0V4YW1wbGUxGzAZBgkqhkiG9w0BCQEWDHVzZXJAZXhhbXBs
       ZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7fRXEe2x0qJqx
        hE4GjKqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        DeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG
        8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        DeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG
        8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        AgMBAAGjUzBRMB0GA1UdDgQWBBTBBXcvR1q3c1B1jZfYvLrYQ5GfAfGA8wDgYD
        VR0PAQH/BAQDAgeAMBMGA1UdIwQMMAoECE31k7i4q5+rMA0GCSqGSIb3DQEBCwUA
        A4IBAQCk0pHvp8pwh3hUBDqK3x2j5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5
        V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9
        w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w
        3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3
        d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d
        -----END CERTIFICATE-----
      PrivateKey: |
        -----BEGIN RSA PRIVATE KEY-----
        MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8h+3hY0J8dC4a4b4e8c9f0e1d2
        c3b4a5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t2u3v4w5x6y7z8A9B0C1D2E3
        F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3Z4A5B6C7D8E9F0G1H2I3J4
        K5L6M7N8O9P0Q1R2S3T4U5V6W7X8Y9Z0A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5
        P6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6
        U7V8W9X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R0S1T2U3V4W5X6Y7
        Z8A9B0C1D2E3F4G5H6I7J8K9L0M1N2O3P4Q5R6S7T8U9V0W1X2Y3Z4A5B6C7D8
        E9F0G1H2I3J4K5L6M7N8O9P0Q1R2S3T4U5V6W7X8Y9Z0A1B2C3D4E5F6G7H8I9
        J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0
        O1P2Q3R4S5T6U7V8W9X0Y1Z2A3B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R0S1
        -----END RSA PRIVATE KEY-----
      CertificateChain: |
        -----BEGIN CERTIFICATE-----
        MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
        BAYTAlVTMRUwEwYDVQQIDAxDYWxpZm9ybmlhMRYwFAYDVQQHDA1TYW4gRnJhbmNp
        c2NvMRAwDgYDVQQKDAdFeGFtcGxlMRswGQYJKoZIhvcNAQkBFgx1c2VyQGV4YW1w
        bGUuY29tMB4XDTIzMDEwMTAwMDAwMFoXDTI0MDEwMTAwMDAwMFowRTELMAkGA1UE
        BhMCVVMxFTATBgNVBAgMDENhbGlmb3JuaWExFjAUBgNVBAcMDVNhbiBGcmFuY2lz
        Y28xEDAOBgNVBAoMB0V4YW1wbGUxGzAZBgkqhkiG9w0BCQEWDHVzZXJAZXhhbXBs
        ZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC7fRXEe2x0qJqx
        hE4GjKqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        DeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG
        8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        DeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG
        8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJDeU3Q8hZG8U8XjLqPJ
        AgMBAAGjUzBRMB0GA1UdDgQWBBTBBXcvR1q3c1B1jZfYvLrYQ5GfAfGA8wDgYD
        VR0PAQH/BAQDAgeAMBMGA1UdIwQMMAoECE31k7i4q5+rMA0GCSqGSIb3DQEBCwUA
        A4IBAQCk0pHvp8pwh3hUBDqK3x2j5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5
        V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9
        w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w
        3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3
        d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d5x3E5V9w3d
        -----END CERTIFICATE-----
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the server certificate |

---

## AWS::Organizations::Policy

Creates a policy in an organization or in an organizational unit.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | The name of the policy |
| Description | String | No | A description of the policy |
| Type | String | Yes | The type of policy (SERVICE_CONTROL_POLICY, TAG_POLICY, BACKUP_POLICY, AI_SERVICES_OPT_OUT_POLICY) |
| Content | JSON | Yes | The policy content as JSON |
| TargetIds | List of String | No | A list of organizational unit IDs or account IDs to attach the policy to |

### Example with SCP

```yaml
Resources:
  RestrictiveSCP:
    Type: AWS::Organizations::Policy
    Properties:
      Name: !Sub "${AWS::StackName}-restrictive"
      Description: SCP to restrict dangerous operations
      Type: SERVICE_CONTROL_POLICY
      Content:
        Version: "2012-10-17"
        Statement:
          - Sid: DenyDeleteProduction
            Effect: Deny
            Action:
              - s3:DeleteBucket
              - dynamodb:DeleteTable
              - rds:DeleteDBInstance
            Resource: "*"
            Condition:
              StringEquals:
                aws:ResourceTag/environment: production
          - Sid: RequireEncryption
            Effect: Deny
            Action:
              - s3:PutObject
            Resource: "*"
            Condition:
              StringNotEquals:
                s3:x-amz-server-side-encryption: AES256
```

---

## AWS::SSO::PermissionSet

Creates a permission set that you can assign to your workforce identities.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| InstanceArn | String | Yes | The ARN of the SSO instance |
| PermissionSetName | String | Yes | The name of the permission set |
| Description | String | No | A description of the permission set |
| SessionDuration | String | No | The duration of the session (ISO 8601 duration format) |
| RelayStateType | String | No | The relay state URL |
| ManagedPolicies | List of String | No | A list of managed policy ARNs |
| InlinePolicy | String | No | An inline policy document |

### Example

```yaml
Resources:
  AdminPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${AWS::StackName}-admin"
      Description: Administrator access permission set
      SessionDuration: PT8H
      ManagedPolicies:
        - arn:aws:iam::aws:policy/AdministratorAccess
      InlinePolicy: |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": ["aws-portal:*Billing"],
              "Resource": "*"
            }
          ]
        }
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| PermissionSetArn | The ARN of the permission set |

---

## AWS::SSO::AccountAssignment

Assigns access to a principal in a specific AWS account using a permission set.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| InstanceArn | String | Yes | The ARN of the SSO instance |
| PermissionSetArn | String | Yes | The ARN of the permission set |
| PrincipalId | String | Yes | The ID of the principal |
| PrincipalType | String | Yes | The type of principal (USER or GROUP) |
| TargetId | String | Yes | The ID of the AWS account |
| TargetType | String | Yes | The type of target (AWS_ACCOUNT) |

### Example

```yaml
Resources:
  AdminPermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetName: !Sub "${AWS::StackName}-admin"
      ManagedPolicies:
        - arn:aws:iam::aws:policy/AdministratorAccess

  AdminAssignment:
    Type: AWS::SSO::AccountAssignment
    Properties:
      InstanceArn: !Ref SSOInstanceArn
      PermissionSetArn: !Ref AdminPermissionSet.PermissionSetArn
      PrincipalId: !Ref AdminGroupId
      PrincipalType: GROUP
      TargetId: !Ref TargetAccountId
      TargetType: AWS_ACCOUNT
```

---

## AWS::IAM::ServiceLinkedRole

Creates an IAM service-linked role for an AWS service.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AWSServiceName | String | Yes | The service name for which the role is created |
| Description | String | No | A description of the role |
| CustomSuffix | String | No | A custom suffix for the role name |
| SupportedServices | List of String | No | A list of services that can assume the role |

### Example

```yaml
Resources:
  AutoScalingServiceRole:
    Type: AWS::IAM::ServiceLinkedRole
    Properties:
      AWSServiceName: autoscaling.amazonaws.com
      Description: Service-linked role for Auto Scaling
      CustomSuffix: auto-scaling
```

---

## AWS::IAM::SAMLProvider

Creates an IAM SAML identity provider.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| SAMLMetadataDocument | String | Yes | The XML metadata document |
| Name | String | No | The name of the SAML provider |

### Example

```yaml
Resources:
  SAMLProvider:
    Type: AWS::IAM::SAMLProvider
    Properties:
      Name: !Sub "${AWS::StackName}-saml"
      SAMLMetadataDocument: !Ref MetadataDocument
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Arn | The ARN of the SAML provider |

---

## AWS::IAM::OIDCProvider

Creates an IAM OpenID Connect provider.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Url | String | Yes | The URL for the OIDC provider |
| ClientIdList | List of String | No | A list of client IDs |
| ThumbprintList | List of String | No | A list of thumbprints |
| Tags | List of Tag | No | A list of tags to attach |

### Example

```yaml
Resources:
  OIDCProvider:
    Type: AWS::IAM::OIDCProvider
    Properties:
      Url: !Sub "https://${OidcProviderEndpoint}"
      ClientIdList:
        - !Ref ClientId
      ThumbprintList:
        - !Ref Thumbprint
```

---

## Condition Keys Reference

### AWS-Specific Condition Keys

| Condition Key | Type | Description |
|---------------|------|-------------|
| aws:SourceIp | IP address | Source IP address of the requester |
| aws:RequestedRegion | String | AWS region requested |
| aws:ResourceTag/tag-key | String | Tag value on the resource |
| aws:PrincipalTag/tag-key | String | Tag value on the principal |
| aws:MultiFactorAuthPresent | Boolean | Whether MFA was used |
| aws:MultiFactorAuthAge | Numeric | Age of the MFA session |
| aws:EpochTime | Numeric | Time of the request |
| aws:CurrentTime | Date | Current time |
| aws:SecureTransport | Boolean | Whether SSL was used |

### S3-Specific Condition Keys

| Condition Key | Type | Description |
|---------------|------|-------------|
| s3:prefix | String | Prefix for ListBucket |
| s3:Delimiter | String | Delimiter for ListBucket |
| s3:x-amz-server-side-encryption | String | Server-side encryption algorithm |
| s3:x-amz-acl | String | Access control list |
| s3:ExistingObjectTag/tag-key | String | Tag on existing object |
| s3:RequestObjectTag/tag-key | String | Tag on object being uploaded |

### DynamoDB-Specific Condition Keys

| Condition Key | Type | Description |
|---------------|------|-------------|
| dynamodb:TableName | String | Name of the table |
| dynamodb:Select | String | Select type |
| dynamodb:Attributes | List | Attributes to return |
| dynamodb:ReturnValues | String | Return values type |
| dynamodb:QueryFilter | Map | Query filter conditions |

### IAM-Specific Condition Keys

| Condition Key | Type | Description |
|---------------|------|-------------|
| iam:ResourceTag/tag-key | String | Tag on IAM resource |
| iam:PrincipalTag/tag-key | String | Tag on principal |
| iam:AWSServiceName | String | Service name for service roles |
| sts:Externalid | String | External ID for role assumption |
| sts:SourceIdentity | String | Source identity |

### KMS-Specific Condition Keys

| Condition Key | Type | Description |
|---------------|------|-------------|
| kms:EncryptionContext:key | String | Encryption context |
| kms:ViaService | String | Service that can use the key |
| kms:GrantConstraintType | String | Type of grant constraint |
| kms:GrantOperations | List | Operations allowed by grant |

---

## Intrinsic Functions

### Fn::GetAtt

Returns the value of an attribute from a resource.

```yaml
RoleArn: !GetAtt MyRole.Arn
RoleId: !GetAtt MyRole.RoleId
UserArn: !GetAtt MyUser.Arn
```

### Ref

Returns the value of the specified parameter or resource.

```yaml
UserName: !Ref MyUser
RoleName: !Ref MyRole
```

### Fn::Sub

Substitutes variables in an input string.

```yaml
RoleArn: !Sub "arn:aws:iam::${AWS::AccountId}:role/${RoleName}"
PolicyDocument: !Sub |
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BucketName}/*"
    }]
  }
```

### Fn::Join

Concatenates values into a single string.

```yaml
ResourceArns: !Join
  - ","
  - - !GetAtt Table1.Arn
    - !GetAtt Table2.Arn
```

### Fn::Select

Returns a single object from a list.

```yaml
FirstRoleArn: !Select [0, !Ref RoleArns]
```

### Condition Functions

```yaml
# Fn::If
PermissionsBoundary: !If
  - HasBoundary
  - !Ref BoundaryPolicyArn
  - !Ref AWS::NoValue

# Fn::Equals
IsProduction: !Equals [!Ref Environment, production]

# Fn::Not
IsNotDev: !Not [!Equals [!Ref Environment, dev]]

# Fn::And
IsProdAndLarge: !And
  - !Equals [!Ref Environment, production]
  - !Equals [!Ref InstanceSize, large]

# Fn::Or
IsDevOrStaging: !Or
  - !Equals [!Ref Environment, dev]
  - !Equals [!Ref Environment, staging]
```

---

## Common AWS Managed Policies

### Lambda Execution

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole | Basic Lambda execution with CloudWatch Logs |
| arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole | Lambda VPC network access |
| arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole | Lambda SQS polling |
| arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole | Lambda Kinesis streaming |

### EC2

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore | SSM agent access |
| arn:aws:iam::aws:policy/AmazonSSMFullAccess | Full SSM access |
| arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess | EC2 read-only access |
| arn:aws:iam::aws:policy/AmazonEC2FullAccess | Full EC2 access |

### S3

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess | S3 read-only access |
| arn:aws:iam::aws:policy/AmazonS3FullAccess | Full S3 access |
| arn:aws:iam::aws:policy/AmazonS3ObjectReadOnlyAccess | S3 object read-only |

### Database

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess | DynamoDB read-only |
| arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess | Full DynamoDB |
| arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess | RDS read-only |
| arn:aws:iam::aws:policy/AmazonRDSFullAccess | Full RDS |

### Read-Only and Security

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/ReadOnlyAccess | All read-only access |
| arn:aws:iam::aws:policy/SecurityAudit | Security audit access |
| arn:aws:iam::aws:policy/ViewBilling | View billing information |

### Container

| Policy ARN | Description |
|------------|-------------|
| arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy | ECS task execution |
| arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy | EKS worker nodes |
| arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy | EKS CNI plugin |
| arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly | ECR read-only |

---

## Limits and Quotas

### IAM Limits

| Resource | Default Limit |
|----------|---------------|
| Users per account | 5000 |
| Groups per account | 300 |
| Roles per account | 1000 |
| Policies per account | 1500 |
| Access keys per user | 2 |
| Managed policies attached to role/user/group | 10 |
| Size of inline policy | 10240 characters |
| Size of managed policy | 6144 characters |
| Session duration (roles) | 1-12 hours |

### Policy Document Limits

| Element | Limit |
|---------|-------|
| Statements per policy | 10 |
| Characters per policy document | 10240 |
| Actions per statement | 100 |
| Resources per statement | 100 |
| Condition keys per statement | 10 |

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| AccessDenied | Insufficient permissions | Add required actions to policy |
| MalformedPolicyDocument | Invalid policy syntax | Validate JSON syntax |
| ValidationError | Invalid parameter value | Check parameter constraints |
| LimitExceeded | Resource limit reached | Request increase or clean up |
| NoSuchEntity | Resource not found | Verify resource name/ARN |
| ServiceFailure | AWS service error | Retry with backoff |

### Validation Tools

```bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Check for IAM issues
aws iam get-account-password-policy
aws iam get-account-summary
```

---

## Best Practices Reference

### Policy Writing

1. Use least privilege: Start restrictive, add permissions as needed
2. Use wildcards sparingly: Prefer specific actions
3. Use conditions: Restrict by IP, time, tags
4. Use resource-level restrictions: Specify ARNs when possible
5. Use separate policies: Easier to audit and modify
6. Version policies: Use "2012-10-17" version

### Role Configuration

1. Trust relationships: Limit to required principals
2. Session duration: Set based on use case
3. Permissions boundary: Prevent privilege escalation
4. External ID: Use for cross-account access
5. Conditions: Add IP and MFA requirements

### Security Recommendations

1. Enable MFA for all users
2. Rotate access keys regularly
3. Use roles instead of long-term credentials
4. Delete unused users and access keys
5. Review policies quarterly
6. Use CloudTrail for audit logging
7. Enable IAM Access Analyzer
