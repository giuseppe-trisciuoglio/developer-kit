# AWS Architecture Diagrams Skill Guide

This guide covers the `aws-drawio-architecture-diagrams` skill for creating professional AWS architecture diagrams in draw.io XML format.

## Overview

The `aws-drawio-architecture-diagrams` skill creates pixel-perfect AWS architecture diagrams in draw.io XML format using the official AWS4 shape library. These diagrams are production-ready for documentation, Well-Architected reviews, and infrastructure presentations.

## Skill Details

| Property | Value |
|----------|-------|
| **Name** | aws-drawio-architecture-diagrams |
| **Category** | General AWS |
| **Tools** | Read, Write, Bash |

## When to Use This Skill

Use this skill when you need to:
- Create AWS cloud architecture diagrams (VPC, subnets, services)
- Document multi-tier application architectures on AWS
- Design serverless architectures (Lambda, API Gateway, DynamoDB)
- Visualize network topology diagrams with security groups
- Create infrastructure documentation for Well-Architected reviews
- Generate diagrams for architecture presentations and documentation

## Trigger Phrases

- "Create AWS diagram"
- "Draw VPC architecture"
- "Architecture diagram draw.io"
- "AWS architecture diagram"
- "Multi-tier AWS architecture"
- "Serverless diagram"
- "Network topology AWS"
- "AWS icons draw.io"

---

## Core Concepts

### File Structure

Every `.drawio` file follows a standard XML structure:

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="aws-arch-1" name="AWS Architecture">
    <mxGraphModel dx="1434" dy="759" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- AWS shapes and connectors -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Important Rules

1. **Reserved IDs**: "0" and "1" are reserved for root cells
2. **Unique IDs**: Use sequential integer IDs starting from "2"
3. **Landscape orientation**: `pageWidth="1169" pageHeight="827"`
4. **Grid alignment**: All coordinates positive and aligned to grid (multiples of 10)
5. **Parent references**: Parent must reference existing cell ID

---

## Diagram Hierarchy

Follow this nesting structure:

```
AWS Cloud (top-level boundary)
└── Region (us-east-1, eu-west-1, etc.)
    └── VPC (with CIDR block)
        ├── Public Subnet (green border)
        │   └── Services (ALB, NAT Gateway, Internet Gateway)
        ├── Private Subnet (blue border)
        │   └── Services (EC2, ECS, Lambda)
        └── Data Subnet (blue border)
            └── Services (RDS, ElastiCache, DynamoDB)
```

---

## AWS Service Categories and Colors

Each AWS service uses official AWS category colors:

| Category | fillColor | gradientColor | Services |
|----------|-----------|---------------|----------|
| **Compute** | `#D05C17` | `#F78E04` | EC2, ECS, EKS, Fargate, Lambda |
| **Storage** | `#277116` | `#60A337` | S3, EBS, EFS, Glacier |
| **Database** | `#3334B9` | `#4D72F3` | RDS, DynamoDB, Aurora, Redshift |
| **Networking** | `#5A30B5` | `#945DF2` | CloudFront, Route 53, API Gateway, VPC |
| **Security** | `#C7131F` | `#F54749` | IAM, Cognito, KMS, WAF, Shield |
| **App Integration** | `#BC1356` | `#F54749` | SQS, SNS, EventBridge |

**Important**: All `resourceIcon` shapes must use `strokeColor=#ffffff` for proper rendering.

---

## Common Patterns

### Three-Tier Architecture

```xml
<!-- Users (external) -->
<mxCell id="2" value="Users" style="...shape=mxgraph.aws4.users;..." vertex="1" parent="1">
  <mxGeometry x="40" y="340" width="60" height="60" as="geometry" />
</mxCell>

<!-- AWS Cloud -->
<mxCell id="3" value="AWS Cloud" style="...shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;..." vertex="1" parent="1">
  <mxGeometry x="160" y="40" width="960" height="720" as="geometry" />
</mxCell>

<!-- Region -->
<mxCell id="4" value="us-east-1" style="...grIcon=mxgraph.aws4.group_region;..." vertex="1" parent="3">
  <mxGeometry x="20" y="40" width="920" height="660" as="geometry" />
</mxCell>

<!-- VPC -->
<mxCell id="5" value="VPC (10.0.0.0/16)" style="...grIcon=mxgraph.aws4.group_vpc;..." vertex="1" parent="4">
  <mxGeometry x="20" y="40" width="880" height="600" as="geometry" />
</mxCell>
```

### Subnet Types

**Public Subnet** (green border):
```
strokeColor=#7AA116; fillColor=#E9F3D2; fontColor=#248814
```

**Private Subnet** (blue border):
```
strokeColor=#00A4A6; fillColor=#E6F6F7; fontColor=#147EBA
```

### Service Icons

```xml
<!-- Lambda -->
<mxCell id="10" value="Lambda" style="...fillColor=#D05C17;gradientColor=#F78E04;strokeColor=none;shape=mxgraph.aws4.lambda;" vertex="1" parent="5">
  <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
</mxCell>

<!-- S3 -->
<mxCell id="11" value="S3 Bucket" style="...fillColor=#277116;gradientColor=#60A337;strokeColor=#ffffff;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;" vertex="1" parent="5">
  <mxGeometry x="270" y="50" width="60" height="60" as="geometry" />
</mxCell>
```

### Connectors

**Standard data flow**:
```
edgeStyle=orthogonalEdgeStyle;endArrow=open;strokeColor=#545B64;strokeWidth=2;
```

**Encrypted connection** (dashed red):
```
edgeStyle=orthogonalEdgeStyle;endArrow=classic;endFill=1;strokeColor=#DD344C;strokeWidth=2;dashed=1;
```

**Async/event flow**:
```
edgeStyle=orthogonalEdgeStyle;endArrow=open;strokeColor=#E7157B;strokeWidth=2;dashed=1;
```

---

## Layout Best Practices

1. **Hierarchy**: External → Internet → AWS Cloud → Region → VPC → Subnets → Services
2. **Flow direction**: Left-to-right for user traffic, top-to-bottom for tiers
3. **Icon sizes**: 60x60 pixels for service icons
4. **Spacing**: 30-40px between icons, 20px padding inside containers
5. **Labels**: Place below icons (`verticalLabelPosition=bottom`)
6. **Diagram size**: Keep focused (15-20 icons maximum per diagram)

---

## Reference Materials

The skill includes comprehensive reference guides:

| Guide | Description |
|-------|-------------|
| `references/aws-shape-reference.md` | Complete AWS4 shape catalog with styles for 50+ services |
| `references/aws-architecture-templates.md` | Ready-to-use templates (3-tier, serverless, data pipeline) |

---

## Validation Checklist

Before saving any diagram, verify:

- [ ] XML is well-formed (valid XML syntax)
- [ ] All IDs are unique (no duplicates)
- [ ] Parent references point to existing cells
- [ ] All coordinates are positive and grid-aligned
- [ ] AWS4 library shapes used (not legacy aws3)
- [ ] Special characters escaped (`&` → `&amp;`, `<` → `&lt;`)
- [ ] Labels use `&lt;br&gt;` for line breaks

---

## Opening Diagrams

Open generated diagrams in draw.io with AWS libraries:

```
https://app.diagrams.net/?libs=aws4
```

---

## Related Skills

| Skill | Integration |
|-------|-------------|
| **AWS Solution Architect Expert** | Use diagrams for architecture designs |
| **AWS Architecture Review Expert** | Create diagrams for Well-Architected reviews |
| **CloudFormation Skills** | Diagram infrastructure before templating |
| **Cost Optimization** | Visualize architecture for cost analysis |

---

## See Also

- [CloudFormation Skills Guide](./guide-skills-cloudformation.md) - Infrastructure as Code
- [AWS Agents Guide](./guide-agents.md) - AWS specialized agents
- [AWS Official Architecture Icons](https://aws.amazon.com/architecture/icons/) - AWS icon reference
- [Draw.io AWS Library](https://app.diagrams.net/?libs=aws4) - Draw.io with AWS shapes
