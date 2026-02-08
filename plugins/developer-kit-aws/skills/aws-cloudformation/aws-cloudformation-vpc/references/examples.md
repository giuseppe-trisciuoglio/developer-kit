# AWS CloudFormation VPC - Examples

This file contains comprehensive examples for VPC infrastructure patterns with CloudFormation.

## Example 1: Multi-AZ VPC with Public/Private Subnets

Complete production-ready VPC with multiple availability zones.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Production VPC with public and private subnets across 3 AZs

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    Description: Environment name for resource tagging
    AllowedValues:
      - development
      - staging
      - production

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: CIDR block for the VPC
    AllowedPattern: ^([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$

  NumberOfAZs:
    Type: Number
    Default: 2
    Description: Number of Availability Zones to use
    MinValue: 1
    MaxValue: 3

  CreateNatGateways:
    Type: String
    Default: true
    Description: Whether to create NAT Gateways
    AllowedValues:
      - true
      - false

Conditions:
  UseThreeAZs: !Equals [!Ref NumberOfAZs, 3]
  ShouldCreateNat: !Equals [!Ref CreateNatGateways, true]

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc
        - Key: Environment
          Value: !Ref EnvironmentName

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw
        - Key: Environment
          Value: !Ref EnvironmentName

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # NAT Gateway EIPs
  NatGatewayEIP1:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Condition: ShouldCreateNat
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-eip-1

  NatGatewayEIP2:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Condition: ShouldCreateNat
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-eip-2

  # Public Subnet 1
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-1
        - Key: SubnetType
          Value: Public

  # Public Subnet 2
  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-2
        - Key: SubnetType
          Value: Public

  # Public Subnet 3 (conditional)
  PublicSubnet3:
    Type: AWS::EC2::Subnet
    Condition: UseThreeAZs
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.3.0/24
      AvailabilityZone: !Select [2, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-3
        - Key: SubnetType
          Value: Public

  # Private Subnet 1
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-1
        - Key: SubnetType
          Value: Private

  # Private Subnet 2
  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.11.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-2
        - Key: SubnetType
          Value: Private

  # Private Subnet 3 (conditional)
  PrivateSubnet3:
    Type: AWS::EC2::Subnet
    Condition: UseThreeAZs
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.12.0/24
      AvailabilityZone: !Select [2, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-3
        - Key: SubnetType
          Value: Private

  # NAT Gateway 1
  NatGateway1:
    Type: AWS::EC2::NatGateway
    Condition: ShouldCreateNat
    Properties:
      AllocationId: !GetAtt NatGatewayEIP1.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-1

  # NAT Gateway 2
  NatGateway2:
    Type: AWS::EC2::NatGateway
    Condition: ShouldCreateNat
    Properties:
      AllocationId: !GetAtt NatGatewayEIP2.AllocationId
      SubnetId: !Ref PublicSubnet2
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-nat-2

  # Public Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-rt

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnetRouteTableAssociation1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnetRouteTableAssociation2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

  PublicSubnetRouteTableAssociation3:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Condition: UseThreeAZs
    Properties:
      SubnetId: !Ref PublicSubnet3
      RouteTableId: !Ref PublicRouteTable

  # Private Route Table 1
  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-rt-1

  DefaultPrivateRoute1:
    Type: AWS::EC2::Route
    Condition: ShouldCreateNat
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnetRouteTableAssociation1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable1

  # Private Route Table 2
  PrivateRouteTable2:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-rt-2

  DefaultPrivateRoute2:
    Type: AWS::EC2::Route
    Condition: ShouldCreateNat
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway2

  PrivateSubnetRouteTableAssociation2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable2

  # Private Route Table 3 (conditional)
  PrivateRouteTable3:
    Type: AWS::EC2::RouteTable
    Condition: UseThreeAZs
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-private-rt-3

  DefaultPrivateRoute3:
    Type: AWS::EC2::Route
    Condition: ShouldCreateNat
    Properties:
      RouteTableId: !Ref PrivateRouteTable3
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway2

  PrivateSubnetRouteTableAssociation3:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Condition: UseThreeAZs
    Properties:
      SubnetId: !Ref PrivateSubnet3
      RouteTableId: !Ref PrivateRouteTable3

Outputs:
  VpcId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VpcId

  InternetGatewayId:
    Description: Internet Gateway ID
    Value: !Ref InternetGateway
    Export:
      Name: !Sub ${EnvironmentName}-InternetGatewayId

  PublicSubnetIds:
    Description: Comma-separated public subnet IDs
    Value: !Join
      - ","
      - - !Ref PublicSubnet1
        - !Ref PublicSubnet2
        - !If [UseThreeAZs, !Ref PublicSubnet3, !Ref "AWS::NoValue"]
    Export:
      Name: !Sub ${EnvironmentName}-PublicSubnetIds

  PrivateSubnetIds:
    Description: Comma-separated private subnet IDs
    Value: !Join
      - ","
      - - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
        - !If [UseThreeAZs, !Ref PrivateSubnet3, !Ref "AWS::NoValue"]
    Export:
      Name: !Sub ${EnvironmentName}-PrivateSubnetIds

  AvailabilityZones:
    Description: Comma-separated availability zones
    Value: !Join
      - ","
      - - !Select [0, !GetAZs '']
        - !Select [1, !GetAZs '']
        - !If [UseThreeAZs, !Select [2, !GetAZs ''], !Ref "AWS::NoValue"]
```

## Example 2: VPC Peering Configuration

Create VPC peering between two VPCs.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC peering configuration

Parameters:
  PeerVpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC to peer with

  LocalVpcId:
    Type: AWS::EC2::VPC::Id
    Description: Local VPC ID

Resources:
  VPCPeeringConnection:
    Type: AWS::EC2::VPCPeeringConnection
    Properties:
      PeerVpcId: !Ref PeerVpcId
      VpcId: !Ref LocalVpcId
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-peering

  # Update route tables in local VPC
  LocalRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref LocalVpcId

  PeerRoute:
    Type: AWS::EC2::Route
    DependsOn: VPCPeeringConnection
    Properties:
      RouteTableId: !Ref LocalRouteTable
      DestinationCidrBlock: 10.1.0.0/16
      VpcPeeringConnectionId: !Ref VPCPeeringConnection

Outputs:
  PeeringConnectionId:
    Description: VPC Peering Connection ID
    Value: !Ref VPCPeeringConnection
```

## Example 3: VPC with VPC Endpoints

Private connectivity to AWS services without internet traversal.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC with Gateway and Interface endpoints

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnet IDs for interface endpoints

Resources:
  # Gateway Endpoints (no charge)
  S3GatewayEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.s3
      RouteTableIds:
        - !Ref PrivateRouteTable

  DynamoDbGatewayEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.dynamodb
      RouteTableIds:
        - !Ref PrivateRouteTable

  # Interface Endpoints (charge per hour + data)
  SecretsManagerEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.secretsmanager
      SubnetIds: !Ref PrivateSubnetIds
      PrivateDnsEnabled: true

  SsmEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssm
      SubnetIds: !Ref PrivateSubnetIds
      PrivateDnsEnabled: true

  EcrApiEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ecr.api
      SubnetIds: !Ref PrivateSubnetIds
      PrivateDnsEnabled: true

  EcrDkrEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ecr.dkr
      SubnetIds: !Ref PrivateSubnetIds
      PrivateDnsEnabled: true

  CloudWatchLogsEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: !Ref VpcId
      ServiceName: !Sub com.amazonaws.${AWS::Region}.logs
      SubnetIds: !Ref PrivateSubnetIds
      PrivateDnsEnabled: true

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VpcId
```

## Example 4: VPC with Network ACLs

Enhanced security with both Security Groups and NACLs.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC with Network ACLs for additional security

Parameters:
  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  # Public NACL - Allow HTTP/HTTPS from anywhere
  PublicNetworkAcl:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-public-nacl

  PublicInboundNetworkAclEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref PublicNetworkAcl
      RuleNumber: 100
      Protocol: 6
      RuleAction: allow
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 80
        To: 443

  PublicInboundNaclEntry2:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref PublicNetworkAcl
      RuleNumber: 110
      Protocol: 6
      RuleAction: allow
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 1024
        To: 65535

  PublicOutboundNetworkAclEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref PublicNetworkAcl
      RuleNumber: 100
      Protocol: 6
      RuleAction: allow
      Egress: true
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 1024
        To: 65535

  PublicSubnetNetworkAclAssociation:
    Type: AWS::EC2::SubnetNetworkAclAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      NetworkAclId: !Ref PublicNetworkAcl

  # Private NACL - Allow only from VPC
  PrivateNetworkAcl:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-private-nacl

  PrivateInboundNetworkAclEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref PrivateNetworkAcl
      RuleNumber: 100
      Protocol: 6
      RuleAction: allow
      CidrBlock: !Ref VpcCidr
      PortRange:
        From: 5432
        To: 5432

  PrivateSubnetNetworkAclAssociation:
    Type: AWS::EC2::SubnetNetworkAclAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet
      NetworkAclId: !Ref PrivateNetworkAcl
```

## Example 5: Modular VPC with Nested Stacks

Use nested stacks for reusable VPC modules.

```yaml
# vpc-master.yaml - Master stack
AWSTemplateFormatVersion: 2010-09-09
Description: Master VPC stack with nested stacks

Parameters:
  EnvironmentName:
    Type: String
    Default: production

Resources:
  # VPC core resources
  VPCStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./vpc-core.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName

  # Public subnets
  PublicSubnetsStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: VPCStack
    Properties:
      TemplateURL: ./vpc-public-subnets.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VpcId: !GetAtt VPCStack.Outputs.VpcId

  # Private subnets
  PrivateSubnetsStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: VPCStack
    Properties:
      TemplateURL: ./vpc-private-subnets.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VpcId: !GetAtt VPCStack.Outputs.VpcId

Outputs:
  VpcId:
    Value: !GetAtt VPCStack.Outputs.VpcId

  PublicSubnetIds:
    Value: !GetAtt PublicSubnetsStack.Outputs.SubnetIds

  PrivateSubnetIds:
    Value: !GetAtt PrivateSubnetsStack.Outputs.SubnetIds
```

```yaml
# vpc-core.yaml - Core VPC with IGW
AWSTemplateFormatVersion: 2010-09-09
Description: Core VPC resources

Parameters:
  EnvironmentName:
    Type: String

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VpcId

  InternetGatewayId:
    Value: !Ref InternetGateway
```

## Example 6: VPC with VPN Connection

Site-to-site VPN connection for hybrid connectivity.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC with Site-to-Site VPN connection

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  CustomerGatewayIp:
    Type: String
    Description: Public IP address of customer gateway
    AllowedPattern: ^([0-9]{1,3}\.){3}[0-9]{1,3}$

  CustomerGatewayAsn:
    Type: Number
    Default: 65001
    Description: Customer gateway ASN

Resources:
  CustomerGateway:
    Type: AWS::EC2::CustomerGateway
    Properties:
      BgpAsn: !Ref CustomerGatewayAsn
      IpAddress: !Ref CustomerGatewayIp
      Type: ipsec.1
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-cgw

  VPNGateway:
    Type: AWS::EC2::VPNGateway
    Properties:
      Type: ipsec.1
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-vpn-gw

  VPNGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VpcId
      VpnGatewayId: !Ref VPNGateway

  VPNConnection:
    Type: AWS::EC2::VPNConnection
    DependsOn: VPNGatewayAttachment
    Properties:
      Type: ipsec.1
      CustomerGatewayId: !Ref CustomerGateway
      VpnGatewayId: !Ref VPNGateway
      StaticRoutesOnly: true
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-vpn

  VPNConnectionRoute:
    Type: AWS::EC2::VPNConnectionRoute
    DependsOn: VPNConnection
    Properties:
      DestinationCidrBlock: 192.168.0.0/16
      VpnConnectionId: !Ref VPNConnection

Outputs:
  VPNConnectionId:
    Value: !Ref VPNConnection
    Description: VPN Connection ID

  CustomerGatewayIP:
    Value: !Ref CustomerGatewayIp
    Description: Customer gateway public IP
```

## Example 7: VPC Flow Logs

Monitor network traffic with Flow Logs.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: VPC with Flow Logs for traffic monitoring

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  LogDestinationType:
    Type: String
    Default: cloud-watch-logs
    AllowedValues:
      - cloud-watch-logs
      - s3
      - kinesis-data-firehose

Resources:
  # Flow Log IAM Role
  FlowLogsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: vpc-flow-logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: FlowLogsPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                Resource: !GetAtt FlowLogGroup.Arn

  # CloudWatch Logs Group
  FlowLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub /aws/vpc/${AWS::StackName}-flow-logs
      RetentionInDays: 30

  # Flow Log
  FlowLog:
    Type: AWS::EC2::FlowLog
    Properties:
      ResourceId: !Ref VpcId
      ResourceType: VPC
      TrafficType: ALL
      LogDestinationType: !Ref LogDestinationType
      LogGroupName: !Ref FlowLogGroup
      DeliverLogsPermissionArn: !GetAtt FlowLogsRole.Arn

Outputs:
  FlowLogId:
    Value: !Ref FlowLog
    Description: Flow Log ID

  LogGroupName:
    Value: !Ref FlowLogGroup
    Description: CloudWatch Logs group name
```

## Example 8: Complete Network Stack with All Components

Full-featured network stack with VPC, subnets, gateways, security groups, and endpoints.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete network stack with all components

Parameters:
  EnvironmentName:
    Type: String
    Default: production

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc
        - Key: Environment
          Value: !Ref EnvironmentName

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Security Group for Public ALB
  PublicAlbSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for public ALB
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-alb-sg

  # Security Group for Private Instances
  PrivateInstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for private instances
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref PublicAlbSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref PublicAlbSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-instance-sg

  # Security Group for Database
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for database
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref PrivateInstanceSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-db-sg

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VpcId

  PublicAlbSecurityGroupId:
    Value: !Ref PublicAlbSecurityGroup
    Export:
      Name: !Sub ${EnvironmentName}-PublicAlbSecurityGroupId

  PrivateInstanceSecurityGroupId:
    Value: !Ref PrivateInstanceSecurityGroup
    Export:
      Name: !Sub ${EnvironmentName}-PrivateInstanceSecurityGroupId

  DatabaseSecurityGroupId:
    Value: !Ref DatabaseSecurityGroup
    Export:
      Name: !Sub ${EnvironmentName}-DatabaseSecurityGroupId
```
