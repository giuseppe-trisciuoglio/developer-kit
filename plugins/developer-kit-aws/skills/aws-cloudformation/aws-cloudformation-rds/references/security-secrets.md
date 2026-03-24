# RDS Security and Secrets Management

## Using Secrets Manager for Credentials

```yaml
Resources:
  DBCredentialsSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${AWS::StackName}/rds/credentials
      Description: RDS database credentials
      SecretString: !Sub |
        {
          "username": "${MasterUsername}",
          "password": "${MasterUserPassword}",
          "host": !GetAtt DBInstance.Endpoint.Address,
          "port": !GetAtt DBInstance.Endpoint.Port,
          "dbname": "mydb"
        }

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: mysql
      MasterUsername: !Sub "{{resolve:secretsmanager:${DBCredentialsSecret}:SecretString:username}}"
      MasterUserPassword: !Sub "{{resolve:secretsmanager:${DBCredentialsSecret}:SecretString:password}}"
```

## Secrets Manager with Auto Rotation

```yaml
Resources:
  DBCredentialsSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${AWS::StackName}/rds/credentials
      Description: RDS database credentials with automatic rotation
      SecretString: !Sub '{"username":"${MasterUsername}","password":"${MasterUserPassword}"}'
      GenerateSecretString:
        SecretStringTemplate: '{"username": "{{username}}"}'
        GenerateStringKey: "password"
        PasswordLength: 30
        ExcludeCharacters: '"@/\'
      RotationRules:
        AutomaticallyAfterDays: 30

  RotationLambda:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: index.lambda_handler
      Role: !GetAtt RotationLambdaRole.Arn
      Timeout: 120
      Code:
        S3Bucket: !Ref SecretsBucket
        S3Key: lambda/rotation-function.zip

  RotationSchedule:
    Type: AWS::SecretsManager::RotationSchedule
    Properties:
      SecretId: !Ref DBCredentialsSecret
      RotationLambdaARN: !GetAtt RotationLambda.Arn
      RotationRules:
        AutomaticallyAfterDays: 30
```

## VPC Security Groups (Recommended)

For VPC deployment, use EC2 security groups:

```yaml
Resources:
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPCId
      GroupName: !Sub ${AWS::StackName}-rds-sg
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-rds-sg

  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application
      VpcId: !Ref VPCId
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          DestinationSecurityGroupId: !Ref DBSecurityGroup
```

## PostgreSQL Security Group

```yaml
Resources:
  PostgreSQLSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for PostgreSQL RDS
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup
```

## Multi-Tier Security Groups

```yaml
Resources:
  # Web tier
  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web servers
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  # Application tier
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application servers
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref WebSecurityGroup
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          DestinationSecurityGroupId: !Ref DBSecurityGroup

  # Database tier
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for PostgreSQL RDS
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup
```

## Encryption at Rest

```yaml
Resources:
  EncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for RDS encryption
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow RDS Service
            Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action:
              - 'kms:Encrypt'
              - 'kms:Decrypt'
              - 'kms:ReEncrypt*'
              - 'kms:GenerateDataKey*'
              - 'kms:DescribeKey'
            Resource: '*'

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: mysql
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterUserPassword
      StorageEncrypted: true
      KmsKeyId: !Ref EncryptionKey
```

## Encryption in Transit

```yaml
Resources:
  # Force SSL/TLS for PostgreSQL
  PostgreSQLParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Force SSL for PostgreSQL
      Family: postgres16
      Parameters:
        rds.force_ssl: "1"

  # MySQL SSL requirement
  MySQLParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: SSL settings for MySQL
      Family: mysql8.0
      Parameters:
        require_secure_transport: "ON"
```

## IAM Database Authentication

```yaml
Resources:
  # Enable IAM database authentication for RDS
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EnableIAMDatabaseAuthentication: true

  # IAM policy for database access
  DatabaseAccessPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: RDSDatabaseAccess
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - 'rds-db:connect'
            Resource:
              - !Sub 'arn:aws:rds-db:${AWS::Region}:${AWS::AccountId}:dbuser:${DBInstanceResourceLogicalId}/${DBUsername}'
      Roles:
        - !Ref ApplicationRole
```

## Network Isolation

```yaml
Resources:
  # Private subnets only - no public access
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Private subnets for RDS
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  # Ensure no public IP assignment
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      PubliclyAccessible: false
```

## VPC Endpoints for Secrets Manager

```yaml
Resources:
  # VPC endpoint for Secrets Manager (private access)
  SecretsManagerEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub com.amazonaws.${AWS::Region}.secretsmanager
      VpcEndpointType: Interface
      VpcId: !Ref VPCId
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      SecurityGroupIds:
        - !Ref VPCEndpointSecurityGroup

  VPCEndpointSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for VPC endpoints
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref AppSecurityGroup
```

## Audit Logging

```yaml
Resources:
  # Enable CloudWatch Logs exports for PostgreSQL
  PostgreSQLInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: "16.1"
      EnableCloudwatchLogsExports:
        - postgresql
        - upgrade

  # Enable CloudWatch Logs exports for MySQL
  MySQLInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: mysql
      EnableCloudwatchLogsExports:
        - audit
        - error
        - general
        - slowquery
```

## Security Best Practices

### Principle of Least Privilege

```yaml
Resources:
  # Only allow specific application security group
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Least privilege database access
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup
```

### Separate Credentials per Application

```yaml
Resources:
  # Web application credentials
  WebAppCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${AWS::StackName}/webapp/credentials
      SecretString: !Sub '{"username":"webapp_user","password":"${WebAppPassword}"}'

  # API service credentials
  APIServiceCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${AWS::StackName}/api/credentials
      SecretString: !Sub '{"username":"api_user","password":"${APIPassword}"}'
```

### Rotation Schedule

```yaml
Resources:
  # High security - rotate every 7 days
  ProductionCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: prod/db/credentials
      SecretString: !Sub '{"username":"admin","password":"${Password}"}'
      RotationRules:
        AutomaticallyAfterDays: 7

  # Standard security - rotate every 30 days
  DevelopmentCredentials:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: dev/db/credentials
      SecretString: !Sub '{"username":"admin","password":"${Password}"}'
      RotationRules:
        AutomaticallyAfterDays: 30
```
