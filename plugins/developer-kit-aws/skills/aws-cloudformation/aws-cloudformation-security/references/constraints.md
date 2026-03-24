# AWS Security Constraints and Limitations

## Resource Limits

### Security Group Limits

```yaml
# Maximum 60 inbound and 60 outbound rules per security group
Parameters:
  MaxSecurityGroupRules:
    Type: Number
    Default: 50
    MaxValue: 60
    Description: Maximum rules per security group direction
    ConstraintDescription: Cannot exceed 60 rules per direction

Resources:
  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        # Up to 60 inbound rules
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
      SecurityGroupEgress:
        # Up to 60 outbound rules
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
```

### VPC and Network Limits

```yaml
# Maximum 500 security groups per VPC (soft limit)
# Maximum 5 VPCs per region (soft limit, can be increased)

Parameters:
  ExpectedVPCCount:
    Type: Number
    Default: 3
    MaxValue: 5
    Description: Expected number of VPCs in region

  ExpectedSecurityGroups:
    Type: Number
    Default: 50
    MaxValue: 500
    Description: Expected number of security groups

# Request quota increase if needed
Resources:
  VPCQuotaRequest:
    Type: AWS::SupportApp::SlackChannelConfiguration
    Properties:
      # Notify when approaching limits
      SlackChannelId: !Ref SlackChannelId
```

### NACL Limits

```yaml
# Maximum 20 inbound and 20 outbound rules per NACL per subnet
Resources:
  ApplicationNACL:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC

  # NACL entries (max 20 per direction)
  NACLEntry:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref ApplicationNACL
      RuleNumber: 100
      Protocol: "-1"  # All traffic
      RuleAction: allow
      Egress: false
      CidrBlock: 0.0.0.0/0
```

## Security Constraints

### Default Security Groups

```yaml
# Default security groups cannot be deleted
# Create custom security groups instead

Resources:
  # Custom security group (recommended)
  CustomSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Custom application security group
      GroupName: !Sub "${AWS::StackName}-custom-sg"
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: CustomSecurityGroup

  # Avoid using default security group
  # The default security group is created automatically but cannot be deleted
```

### Security Group References

```yaml
# Security group references cannot span VPC peering in some cases
# Use CIDR ranges for peering scenarios

Resources:
  # Security group reference within same VPC (works)
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web server security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup  # Same VPC

  # For VPC peering, use CIDR instead
  PeeredVPCSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Peered VPC security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: !Ref PeeredVPC CIDR  # Use CIDR for peering
```

### NACL Stateless Behavior

```yaml
# NACLs are stateless; return traffic must be explicitly allowed
# Unlike security groups which are stateful

Resources:
  ApplicationNACL:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC

  # Allow inbound traffic
  InboundRule:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref ApplicationNACL
      RuleNumber: 100
      Protocol: "6"  # TCP
      RuleAction: allow
      Egress: false
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 443
        To: 443

  # Must also allow return traffic (stateless)
  OutboundRule:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      NetworkAclId: !Ref ApplicationNACL
      RuleNumber: 100
      Protocol: "6"  # TCP
      RuleAction: allow
      Egress: true
      CidrBlock: 0.0.0.0/0
      PortRange:
        From: 1024
        To: 65535  # Ephemeral ports
```

## Operational Constraints

### CIDR Overlap

```yaml
# VPC CIDR blocks cannot overlap with peered VPCs or on-prem networks
# Plan CIDR ranges carefully

Parameters:
  VPCCIDR:
    Type: String
    Default: "10.0.0.0/16"
    AllowedPattern: "^(([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2})$"
    Description: VPC CIDR block (must not overlap with peered networks)

  OnPremCIDR:
    Type: String
    Default: "10.1.0.0/16"
    Description: On-premises network CIDR (for VPN/DirectConnect)

# Validation using custom resource
CIDRValidator:
    Type: Custom::CIDRValidator
    Properties:
      ServiceToken: !GetAtt ValidationFunction.Arn
      VPCCIDR: !Ref VPCCIDR
      OnPremCIDR: !Ref OnPremCIDR
```

### ENI Limits

```yaml
# Each instance type has maximum ENI limits
# This affects scaling and high availability

Parameters:
  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues:
      - t3.medium      # 3 ENIs max
      - t3.large       # 3 ENIs max
      - m5.large       # 4 ENIs max
      - m5.xlarge      # 8 ENIs max
    Description: Instance type (affects ENI limits)

Resources:
  # Check ENI requirements before scaling
  ENIRequirementCheck:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: eni-requirement-check
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        ZipFile: |
          const ENI_LIMITS = {
            't3.medium': 3,
            't3.large': 3,
            'm5.large': 4,
            'm5.xlarge': 8
          };

          exports.handler = async (event) => {
            const instanceType = event.InstanceType;
            const required = event.RequiredENIs;
            const limit = ENI_LIMITS[instanceType];

            if (required > limit) {
              throw new Error(`Instance type ${instanceType} supports max ${limit} ENIs, but ${required} required`);
            }
          };
```

### Elastic IP Limits

```yaml
# Each account has limited number of Elastic IPs
# Use NAT Gateway or private subnets to reduce need

Parameters:
  RequireElasticIPs:
    Type: Number
    Default: 2
    Description: Number of Elastic IPs required

Conditions:
  UseNATGateway: !Equals [!Ref RequireElasticIPs, 0]

Resources:
  # Prefer NAT Gateway over Elastic IPs for outbound internet access
  NATGateway:
    Type: AWS::EC2::NatGateway
    Condition: UseNATGateway
    Properties:
      SubnetId: !Ref PublicSubnet
      AllocationId: !Ref NATElasticIP
      Tags:
        - Key: Name
          Value: !Sub "${AWS::StackName}-nat"

  # Elastic IP for NAT Gateway
  NATElasticIP:
    Type: AWS::EC2::EIP
    Condition: UseNATGateway
    Properties:
      Domain: vpc
```

## Network Constraints

### Transit Gateway Limits

```yaml
# Transit Gateway attachments have per-AZ and per-account limits
# Plan attachment strategy accordingly

Parameters:
  ExpectedTransitGatewayAttachments:
    Type: Number
    Default: 2
    MaxValue: 20  # Typical limit per TGW
    Description: Expected number of VPC attachments

Resources:
  TransitGateway:
    Type: AWS::EC2::TransitGateway
    Properties:
      AmazonSideAsn: 64512
      AutoAcceptSharedAttachments: enable
      DefaultRouteTableAssociation: enable
      DefaultRouteTablePropagation: enable
      DnsSupport: enable
      VpnEcmpSupport: enable

  TransitGatewayAttachment:
    Type: AWS::EC2::TransitGatewayAttachment
    Properties:
      TransitGatewayId: !Ref TransitGateway
      VpcId: !Ref VPC
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

### VPN Connection Limits

```yaml
# VPN connections have bandwidth limitations
# Consider AWS Direct Connect for higher bandwidth

Resources:
  VPNConnection:
    Type: AWS::EC2::VPNConnection
    Properties:
      Type: ipsec.1
      CustomerGatewayId: !Ref CustomerGateway
      VpnGatewayId: !Ref VPNGateway
      StaticRoutesOnly: false
      TransitGatewayId: !Ref TransitGateway

# VPN limitations:
# - Bandwidth: Up to 1.25 Gbps per tunnel
# - Latency: Dependent on internet path
# - Reliability: Dependent on internet service provider
```

## Cost Considerations

### NAT Gateway Costs

```yaml
# NAT gateways incur hourly costs plus data processing costs
# ~$0.045 per hour + $0.045 per GB data processing (US-East-1)

Parameters:
  EnableNATGateway:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false
    Description: Enable NAT Gateway (adds cost)

Resources:
  NATGateway:
    Type: AWS::EC2::NatGateway
    Condition: UseNATGateway
    Properties:
      SubnetId: !Ref PublicSubnet
      AllocationId: !Ref NATElasticIP

# Budget alert for NAT Gateway costs
Resources:
  NATGatewayBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetLimit:
          Amount: 100  # Monthly budget
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon EC2
          UsageType:
            - NAT-Gateway-Hours
            - NAT-Gateway-Bytes
```

### Traffic Mirroring Costs

```yaml
# Traffic mirroring doubles data transfer costs
# Use selectively for security monitoring

Parameters:
  EnableTrafficMirroring:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false
    Description: Enable traffic mirroring (doubles data transfer costs)

Resources:
  TrafficMirrorSession:
    Type: AWS::EC2::TrafficMirrorSession
    Condition: EnableTrafficMirroring
    Properties:
      NetworkInterfaceId: !Ref PrimaryInterface
      TrafficMirrorTargetId: !Ref TrafficMirrorTarget
      SessionNumber: 1
      VirtualNetworkId: 12345
```

### Flow Logs Costs

```yaml
# Flow logs storage and analysis add significant costs
# ~$0.50 per GB ingested + storage costs

Parameters:
  EnableFlowLogs:
    Type: String
    Default: true
    AllowedValues:
      - true
      - false
    Description: Enable VPC Flow Logs (adds CloudWatch Logs cost)

  FlowLogsRetention:
    Type: Number
    Default: 7
    AllowedValues:
      - 1
      - 3
      - 7
      - 14
      - 30
    Description: Flow logs retention (longer = more expensive)

Resources:
  FlowLogGroup:
    Type: AWS::Logs::LogGroup
    Condition: EnableFlowLogs
    Properties:
      LogGroupName: !Sub "/aws/vpc/flowlogs/${VPC}"
      RetentionInDays: !Ref FlowLogsRetention

  VPCFlowLogs:
    Type: AWS::EC2::FlowLog
    Condition: EnableFlowLogs
    Properties:
      ResourceType: VPC
      ResourceId: !Ref VPC
      TrafficType: ALL
      LogDestinationType: cloud-watch-logs
      LogGroupName: !Ref FlowLogGroup
      DeliverLogsPermissionArn: !GetAtt FlowLogsRole.Arn
```

### PrivateLink Costs

```yaml
# Interface VPC endpoints incur hourly and data processing costs
# ~$0.01 per hour per AZ + $0.01 per GB data processing

Parameters:
  EnableInterfaceEndpoints:
    Type: String
    Default: false
    AllowedValues:
      - true
      - false
    Description: Enable interface endpoints (adds cost)

Conditions:
  UseInterfaceEndpoints: !Equals [!Ref EnableInterfaceEndpoints, true]

Resources:
  # Gateway endpoints (free)
  S3GatewayEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.s3"
      VpcId: !Ref VPC
      VpcEndpointType: Gateway

  # Interface endpoints (paid)
  ECRInterfaceEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Condition: UseInterfaceEndpoints
    Properties:
      ServiceName: !Sub "com.amazonaws.${AWS::Region}.ecr.api"
      VpcId: !Ref VPC
      VpcEndpointType: Interface
      PrivateDnsEnabled: true
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      SecurityGroupIds:
        - !Ref EndpointSecurityGroup
```

## Access Control Constraints

### IAM vs Resource Policies

```yaml
# Some services require both IAM and resource-based policies

Resources:
  # S3 bucket policy (resource-based policy)
  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref DataBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action:
              - s3:GetObject
            Resource: !Sub "${DataBucket.Arn}/*"

  # IAM policy (identity-based policy)
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DataBucket.Arn}/*"

# Some services like S3 require both policies for cross-account access
```

### Permission Boundaries

```yaml
# Permission boundaries do not limit service actions
# They only limit the permissions that can be assigned

Resources:
  PermissionBoundaryPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: !Sub "${AWS::StackName}-permission-boundary"
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Deny
            Action:
              - iam:CreateUser
              - iam:CreateAccessKey
            Resource: "*"
      Description: Permission boundary for developers

  DeveloperRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Ref DeveloperAccount
            Action: sts:AssumeRole
      PermissionsBoundary: !Ref PermissionBoundaryPolicy
      Policies:
        - PolicyName: DeveloperActions
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DataBucket.Arn}/*"
```

### Session Policies

```yaml
# Session policies cannot grant more permissions than IAM policies
# They can only restrict existing permissions

Resources:
  RoleAssumptionPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: RoleAssumption
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action:
              - sts:AssumeRole
            Resource: !Sub "${RestrictedRole.Arn}"
      Roles:
        - !Ref BaseUserRole

  # Session policy passed during AssumeRole
  # Limits permissions even if IAM policy allows more
```

## Best Practices to Avoid Constraints

### Use Security Groups Over NACLs

```yaml
# Security groups are stateful and easier to manage
# Use NACLs only when necessary (e.g., blocking IPs at subnet level)

Resources:
  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
      # Stateful: return traffic automatically allowed
```

### Use VPC Peering Strategically

```yaml
# Plan VPC CIDR ranges to avoid overlap
# Use Transit Gateway for multi-VPC architectures (beyond 3 VPCs)

Resources:
  ProductionVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: "10.0.0.0/16"
      EnableDnsHostnames: true
      EnableDnsSupport: true

  DevelopmentVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: "10.1.0.0/16"  # Non-overlapping
      EnableDnsHostnames: true
      EnableDnsSupport: true

  VPCPeering:
    Type: AWS::EC2::VPCPeering
    Properties:
      PeerVpcId: !Ref ProductionVPC
      PeerRegion: !Ref AWS::Region
      VpcId: !Ref DevelopmentVPC
```

### Monitor Security Resource Limits

```yaml
# Set up alarms for security group limits

Resources:
  SecurityGroupCountAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: security-group-count-alarm
      AlarmDescription: Alert when approaching security group limit
      MetricName: ResourceCount
      Namespace: AWS/Usage
      Statistic: Maximum
      Period: 86400  # Daily
      EvaluationPeriods: 1
      Threshold: 450  # Alert at 90% of 500 limit
      ComparisonOperator: GreaterThanThreshold
```

## Quota Management

### Request Quota Increases

```yaml
# Service quota increases for security resources
Parameters:
  RequestSecurityGroupQuota:
    Type: Number
    Default: 500
    Description: Requested security group quota per VPC

  RequestNACLQuota:
    Type: Number
    Default: 20
    Description: Requested NACL rules per subnet

# Use AWS Support API or Console to request increases
# Document requested quotas in stack outputs

Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=amazon-vpc"
```
