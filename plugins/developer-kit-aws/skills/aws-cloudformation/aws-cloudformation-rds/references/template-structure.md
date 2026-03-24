# CloudFormation Template Structure for RDS

## Template Sections Overview

AWS CloudFormation templates are JSON or YAML files with specific sections.

```yaml
AWSTemplateFormatVersion: 2010-09-09  # Required
Description: Optional description string

# Section order
Mappings: {}       # Static configuration tables
Metadata: {}       # Additional information about resources
Parameters: {}     # Input values for customization
Rules: {}          # Parameter validation rules
Conditions: {}     # Conditional resource creation
Transform: {}      # Macro processing
Resources: {}      # AWS resources to create (REQUIRED)
Outputs: {}        # Return values after stack creation
```

## Parameters

### AWS-Specific Parameter Types

```yaml
Parameters:
  DBInstanceClass:
    Type: AWS::RDS::DBInstance::InstanceType
    Description: RDS instance class
    Default: db.t3.micro

  EngineVersion:
    Type: AWS::RDS::DBInstance::Version
    Description: Database engine version
    Default: 8.0

  VPCSecurityGroups:
    Type: List<AWS::EC2::SecurityGroup::Id>
    Description: Security groups for RDS instance
```

### Parameter Constraints

```yaml
Parameters:
  DBInstanceIdentifier:
    Type: String
    Description: Database instance identifier
    Default: mydatabase
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"
    ConstraintDescription: Must begin with a letter; contain only alphanumeric characters
    MinLength: 1
    MaxLength: 63

  MasterUsername:
    Type: String
    Description: Master username
    Default: admin
    AllowedPattern: "^[a-zA-Z][a-zA-Z0-9]*$"
    MinLength: 1
    MaxLength: 16
    NoEcho: true

  MasterUserPassword:
    Type: String
    Description: Master user password
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: "[a-zA-Z0-9]*"

  AllocatedStorage:
    Type: Number
    Description: Allocated storage in GB
    Default: 20
    MinValue: 20
    MaxValue: 65536

  DBPort:
    Type: Number
    Description: Database port
    Default: 3306
    MinValue: 1150
    MaxValue: 65535
```

### Engine and Version Parameters

```yaml
Parameters:
  Engine:
    Type: String
    Description: Database engine
    Default: mysql
    AllowedValues:
      - mysql
      - postgres
      - oracle-ee
      - oracle-se2
      - sqlserver-ee
      - sqlserver-se
      - sqlserver-ex
      - sqlserver-web
      - aurora
      - aurora-mysql
      - aurora-postgresql
      - mariadb

  EngineVersion:
    Type: String
    Description: Database engine version
    Default: 8.0.35

  DBFamily:
    Type: String
    Description: Parameter group family
    Default: mysql8.0
    AllowedValues:
      - mysql5.6
      - mysql5.7
      - mysql8.0
      - postgres11
      - postgres12
      - postgres13
      - postgres14
      - postgres15
      - postgres16
      - aurora5.6
      - aurora-mysql5.7
      - aurora-mysql8.0
      - aurora-postgresql11
      - aurora-postgresql14
```

### SSM Parameter Types

```yaml
Parameters:
  LatestMySQLVersion:
    Type: AWS::SSM::Parameter::Value<String>
    Description: Latest MySQL version from SSM
    Default: /rds/mysql/latest/version

  LatestPostgreSQLVersion:
    Type: AWS::SSM::Parameter::Value<String>
    Description: Latest PostgreSQL version from SSM
    Default: /rds/postgres/latest/version
```

### NoEcho for Sensitive Data

```yaml
Parameters:
  MasterUserPassword:
    Type: String
    Description: Master user password
    NoEcho: true
    MinLength: 8
    MaxLength: 41
```

## Mappings

Use `Mappings` for static configuration data based on regions or instance types.

```yaml
Mappings:
  InstanceTypeConfig:
    db.t3.micro:
      CPU: 2
      MemoryGiB: 1
      StorageGB: 20
    db.t3.small:
      CPU: 2
      MemoryGiB: 2
      StorageGB: 20
    db.t3.medium:
      CPU: 2
      MemoryGiB: 4
      StorageGB: 20
    db.m5.large:
      CPU: 2
      MemoryGiB: 8
      StorageGB: 100

  RegionDatabasePort:
    us-east-1:
      MySQL: 3306
      PostgreSQL: 5432
    us-west-2:
      MySQL: 3306
      PostgreSQL: 5432
    eu-west-1:
      MySQL: 3306
      PostgreSQL: 5432

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: !FindInMap [InstanceTypeConfig, !Ref DBInstanceClass, CPU]
      Engine: mysql
```

## Conditions

Use `Conditions` to conditionally create resources based on parameters.

```yaml
Parameters:
  EnableMultiAZ:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false

  EnableEncryption:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false

  Environment:
    Type: String
    Default: development
    AllowedValues:
      - development
      - staging
      - production

Conditions:
  IsMultiAZ: !Equals [!Ref EnableMultiAZ, true]
  IsEncrypted: !Equals [!Ref EnableEncryption, true]
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      MultiAZ: !Ref EnableMultiAZ
      StorageEncrypted: !Ref EnableEncryption
      BackupRetentionPeriod: !If [IsProduction, 35, 7]
      DeletionProtection: !If [IsProduction, true, false]
```

### Condition Functions

```yaml
Conditions:
  IsDev: !Equals [!Ref Environment, development]
  IsStaging: !Equals [!Ref Environment, staging]
  IsProduction: !Equals [!Ref Environment, production]
  HasLicense: !Not [!Condition IsDev]

Resources:
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      LicenseModel: !If [HasLicense, "license-included", "bring-your-own-license"]
      StorageType: !If [IsProduction, "io1", "gp3"]
      Iops: !If [IsProduction, 3000, !Ref AWS::NoValue]
```

## Transform

Use `Transform` for macros like AWS::Serverless for SAM templates.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31
Description: Serverless RDS application template

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11

Resources:
  RDSFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: function/
      Policies:
        - RDSFullAccessPolicy:
            DBInstanceIdentifier: !Ref DBInstanceIdentifier
      Environment:
        Variables:
          DB_HOST: !GetAtt DBInstance.Endpoint.Address
          DB_NAME: !Ref DBName
          DB_USER: !Ref MasterUsername
```

## Metadata

Use `Metadata` for additional information about resources or parameters.

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Database Configuration
        Parameters:
          - DBInstanceIdentifier
          - Engine
          - DBInstanceClass
      - Label:
          default: Credentials
        Parameters:
          - MasterUsername
          - MasterUserPassword
      - Label:
          default: Network
        Parameters:
          - DBSubnetGroupName
          - VPCSecurityGroups
    ParameterLabels:
      DBInstanceIdentifier:
        default: Database Instance ID
      MasterUsername:
        default: Master Username
```

## Outputs and Cross-Stack References

### Basic Outputs

```yaml
Outputs:
  DBInstanceId:
    Description: Database Instance ID
    Value: !Ref DBInstance

  DBInstanceEndpoint:
    Description: Database endpoint address
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: Database port
    Value: !GetAtt DBInstance.Endpoint.Port

  DBInstanceArn:
    Description: Database Instance ARN
    Value: !GetAtt DBInstance.Arn

  DBInstanceClass:
    Description: Database Instance Class
    Value: !Ref DBInstanceClass
```

### Exporting Values for Cross-Stack References

```yaml
Outputs:
  DBInstanceId:
    Description: Database Instance ID for other stacks
    Value: !Ref DBInstance
    Export:
      Name: !Sub ${AWS::StackName}-DBInstanceId

  DBInstanceEndpoint:
    Description: Database endpoint for application stacks
    Value: !GetAtt DBInstance.Endpoint.Address
    Export:
      Name: !Sub ${AWS::StackName}-DBEndpoint

  DBInstancePort:
    Description: Database port for application stacks
    Value: !GetAtt DBInstance.Endpoint.Port
    Export:
      Name: !Sub ${AWS::StackName}-DBPort

  DBConnectionString:
    Description: Full connection string for applications
    Value: !Sub jdbc:mysql://${DBInstanceEndpoint}:${DBInstancePort}/${DBName}
    Export:
      Name: !Sub ${AWS::StackName}-DBConnectionString
```

### Importing Values in Another Stack

```yaml
Parameters:
  DBInstanceId:
    Type: AWS::RDS::DBInstance::Id
    Description: RDS instance ID from database stack

  DBEndpoint:
    Type: String
    Description: Database endpoint address

Resources:
  ApplicationDatabaseConfig:
    Type: AWS::SSM::Parameter
    Properties:
      Name: /app/database/endpoint
      Value: !Ref DBEndpoint
      Type: String
```

### Cross-Stack Reference Pattern

Create a dedicated database stack that exports values:

```yaml
# database-stack.yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Database infrastructure stack

Parameters:
  EnvironmentName:
    Type: String
    Default: production

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: !Sub Subnet group for ${EnvironmentName}
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.medium
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      MultiAZ: true
      StorageEncrypted: true

Outputs:
  DBInstanceId:
    Value: !Ref DBInstance
    Export:
      Name: !Sub ${EnvironmentName}-DBInstanceId

  DBEndpoint:
    Value: !GetAtt DBInstance.Endpoint.Address
    Export:
      Name: !Sub ${EnvironmentName}-DBEndpoint

  DBArn:
    Value: !GetAtt DBInstance.Arn
    Export:
      Name: !Sub ${EnvironmentName}-DBArn

  DBSubnetGroupName:
    Value: !Ref DBSubnetGroup
    Export:
      Name: !Sub ${EnvironmentName}-DBSubnetGroupName
```

Application stack imports these values:

```yaml
# application-stack.yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Application stack that imports from database stack

Parameters:
  DatabaseStackName:
    Type: String
    Description: Name of the database stack
    Default: database-stack

Resources:
  ApplicationConfig:
    Type: AWS::SSM::Parameter
    Properties:
      Name: /app/database/endpoint
      Value: !ImportValue
        Fn::Sub: ${DatabaseStackName}-DBEndpoint
      Type: String

  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: app.handler
      Environment:
        Variables:
          DB_ENDPOINT: !ImportValue
            Fn::Sub: ${DatabaseStackName}-DBEndpoint
```
