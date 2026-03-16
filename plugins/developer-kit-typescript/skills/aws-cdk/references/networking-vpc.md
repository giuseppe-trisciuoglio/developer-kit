# AWS CDK Networking & VPC

## Table of Contents

- [VPC Design](#vpc-design)
- [Subnets](#subnets)
- [NAT Gateways](#nat-gateways)
- [Security Groups](#security-groups)
- [Network ACLs](#network-acls)
- [VPC Endpoints](#vpc-endpoints)
- [VPC Peering](#vpc-peering)
- [Importing Existing VPCs](#importing-existing-vpcs)
- [Complete VPC Pattern](#complete-vpc-pattern)

---

## VPC Design

### Basic VPC

```typescript
import * as ec2 from 'aws-cdk-lib/aws-ec2';

const vpc = new ec2.Vpc(this, 'AppVpc', {
  maxAzs: 2,
  ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
});
```

### Production VPC with Custom Subnets

```typescript
const vpc = new ec2.Vpc(this, 'ProdVpc', {
  maxAzs: 3,
  ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
  subnetConfiguration: [
    {
      cidrMask: 24,
      name: 'Public',
      subnetType: ec2.SubnetType.PUBLIC,
    },
    {
      cidrMask: 24,
      name: 'Private',
      subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
    },
    {
      cidrMask: 28,
      name: 'Isolated',
      subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
    },
  ],
});
```

---

## Subnets

### Subnet Types

| Type | Internet Access | NAT Gateway | Use Case |
|------|----------------|-------------|----------|
| `PUBLIC` | Direct (IGW) | No | Load balancers, bastion hosts |
| `PRIVATE_WITH_EGRESS` | Outbound only (NAT) | Yes | Application servers, Lambda |
| `PRIVATE_ISOLATED` | None | No | Databases, internal services |

### Selecting Subnets

```typescript
// Select specific subnet types for resource placement
const publicSubnets = vpc.selectSubnets({
  subnetType: ec2.SubnetType.PUBLIC,
});

const privateSubnets = vpc.selectSubnets({
  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
});

// Place Lambda in private subnets
new lambda.Function(this, 'PrivateFn', {
  vpc,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
});
```

---

## NAT Gateways

### Cost Optimization

```typescript
// One NAT Gateway per AZ (high availability, higher cost)
const prodVpc = new ec2.Vpc(this, 'ProdVpc', {
  natGateways: 3,  // One per AZ
  maxAzs: 3,
});

// Single NAT Gateway (lower cost, single AZ risk)
const devVpc = new ec2.Vpc(this, 'DevVpc', {
  natGateways: 1,
  maxAzs: 2,
});

// No NAT Gateways (isolated or public-only architectures)
const isolatedVpc = new ec2.Vpc(this, 'IsolatedVpc', {
  natGateways: 0,
  subnetConfiguration: [
    { cidrMask: 24, name: 'Public', subnetType: ec2.SubnetType.PUBLIC },
    { cidrMask: 24, name: 'Isolated', subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
  ],
});
```

---

## Security Groups

### Basic Security Group

```typescript
const webSg = new ec2.SecurityGroup(this, 'WebSG', {
  vpc,
  description: 'Security group for web servers',
  allowAllOutbound: true,
});

webSg.addIngressRule(
  ec2.Peer.anyIpv4(),
  ec2.Port.tcp(443),
  'Allow HTTPS traffic',
);

webSg.addIngressRule(
  ec2.Peer.anyIpv4(),
  ec2.Port.tcp(80),
  'Allow HTTP traffic',
);
```

### Security Group Chaining (Multi-Tier)

```typescript
const albSg = new ec2.SecurityGroup(this, 'AlbSG', {
  vpc, description: 'ALB security group',
});

const appSg = new ec2.SecurityGroup(this, 'AppSG', {
  vpc, description: 'Application security group',
});

const dbSg = new ec2.SecurityGroup(this, 'DbSG', {
  vpc, description: 'Database security group',
});

// ALB accepts HTTPS from internet
albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443));

// App accepts traffic only from ALB
appSg.addIngressRule(albSg, ec2.Port.tcp(8080), 'From ALB');

// DB accepts traffic only from App
dbSg.addIngressRule(appSg, ec2.Port.tcp(5432), 'From App');
```

### Lambda Security Groups

```typescript
const lambdaSg = new ec2.SecurityGroup(this, 'LambdaSG', {
  vpc,
  description: 'Lambda function security group',
  allowAllOutbound: true,
});

// Allow Lambda to reach RDS
dbSg.addIngressRule(lambdaSg, ec2.Port.tcp(5432), 'Lambda to RDS');
```

---

## Network ACLs

```typescript
const nacl = new ec2.NetworkAcl(this, 'CustomNacl', {
  vpc,
  subnetSelection: { subnetType: ec2.SubnetType.PUBLIC },
});

nacl.addEntry('AllowHTTPS', {
  cidr: ec2.AclCidr.anyIpv4(),
  ruleNumber: 100,
  traffic: ec2.AclTraffic.tcpPort(443),
  direction: ec2.TrafficDirection.INGRESS,
  ruleAction: ec2.Action.ALLOW,
});

nacl.addEntry('AllowEphemeral', {
  cidr: ec2.AclCidr.anyIpv4(),
  ruleNumber: 200,
  traffic: ec2.AclTraffic.tcpPortRange(1024, 65535),
  direction: ec2.TrafficDirection.EGRESS,
  ruleAction: ec2.Action.ALLOW,
});
```

---

## VPC Endpoints

Eliminate NAT costs for AWS service traffic by using VPC endpoints.

### Gateway Endpoints (S3, DynamoDB)

```typescript
// Free — no hourly charge
vpc.addGatewayEndpoint('S3Endpoint', {
  service: ec2.GatewayVpcEndpointAwsService.S3,
});

vpc.addGatewayEndpoint('DynamoEndpoint', {
  service: ec2.GatewayVpcEndpointAwsService.DYNAMODB,
});
```

### Interface Endpoints (Other AWS Services)

```typescript
// Per-hour charge — add only services you use
vpc.addInterfaceEndpoint('SecretsManagerEndpoint', {
  service: ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
  subnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
});

vpc.addInterfaceEndpoint('SqsEndpoint', {
  service: ec2.InterfaceVpcEndpointAwsService.SQS,
});

vpc.addInterfaceEndpoint('LambdaEndpoint', {
  service: ec2.InterfaceVpcEndpointAwsService.LAMBDA,
});
```

---

## VPC Peering

```typescript
const vpcA = new ec2.Vpc(this, 'VpcA', {
  ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
});

const vpcB = new ec2.Vpc(this, 'VpcB', {
  ipAddresses: ec2.IpAddresses.cidr('10.1.0.0/16'),
});

const peering = new ec2.CfnVPCPeeringConnection(this, 'Peering', {
  vpcId: vpcA.vpcId,
  peerVpcId: vpcB.vpcId,
});

// Add routes in both directions
vpcA.privateSubnets.forEach((subnet, i) => {
  new ec2.CfnRoute(this, `AtoB${i}`, {
    routeTableId: subnet.routeTable.routeTableId,
    destinationCidrBlock: '10.1.0.0/16',
    vpcPeeringConnectionId: peering.ref,
  });
});
```

---

## Importing Existing VPCs

```typescript
// Look up by VPC ID (requires explicit env)
const existingVpc = ec2.Vpc.fromLookup(this, 'ImportedVpc', {
  vpcId: 'vpc-0123456789abcdef0',
});

// Look up by tags
const taggedVpc = ec2.Vpc.fromLookup(this, 'TaggedVpc', {
  tags: { Environment: 'production' },
});

// Import by attributes (no context lookup needed)
const importedVpc = ec2.Vpc.fromVpcAttributes(this, 'AttrVpc', {
  vpcId: 'vpc-abc123',
  availabilityZones: ['us-east-1a', 'us-east-1b'],
  publicSubnetIds: ['subnet-pub1', 'subnet-pub2'],
  privateSubnetIds: ['subnet-priv1', 'subnet-priv2'],
});
```

---

## Complete VPC Pattern

Production-ready three-tier VPC:

```typescript
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export class NetworkStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new ec2.Vpc(this, 'MainVpc', {
      maxAzs: 3,
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      natGateways: 2,
      subnetConfiguration: [
        { cidrMask: 22, name: 'Public', subnetType: ec2.SubnetType.PUBLIC },
        { cidrMask: 22, name: 'Private', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
        { cidrMask: 24, name: 'Isolated', subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
      ],
      flowLogs: {
        default: {
          destination: ec2.FlowLogDestination.toCloudWatchLogs(),
          trafficType: ec2.FlowLogTrafficType.REJECT,
        },
      },
    });

    // Gateway endpoints (free)
    this.vpc.addGatewayEndpoint('S3', {
      service: ec2.GatewayVpcEndpointAwsService.S3,
    });
    this.vpc.addGatewayEndpoint('DynamoDB', {
      service: ec2.GatewayVpcEndpointAwsService.DYNAMODB,
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', { value: this.vpc.vpcId });
    new cdk.CfnOutput(this, 'PublicSubnets', {
      value: this.vpc.publicSubnets.map(s => s.subnetId).join(','),
    });
    new cdk.CfnOutput(this, 'PrivateSubnets', {
      value: this.vpc.privateSubnets.map(s => s.subnetId).join(','),
    });
  }
}
```
