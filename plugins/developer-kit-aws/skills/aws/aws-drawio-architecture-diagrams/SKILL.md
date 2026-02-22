---
name: aws-drawio-architecture-diagrams
description: Provides professional AWS architecture diagram creation in draw.io XML format (.drawio files) using official AWS Architecture Icons (aws4 library). Use when creating AWS cloud architecture diagrams, infrastructure diagrams, network topology diagrams, serverless architectures, multi-tier application diagrams, VPC layouts, or any AWS visual diagram in draw.io format.
category: aws
tags: [aws, drawio, architecture, diagrams, infrastructure, cloud, visualization]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS Architecture Diagram Creation with Draw.io

## Overview

Create professional, pixel-perfect AWS architecture diagrams in draw.io's native XML format using the official AWS Architecture Icons (aws4 shape library). This skill enables generation of production-ready `.drawio` files that can be opened directly in [diagrams.net](https://app.diagrams.net/?libs=aws4).

## When to Use

Use this skill when:
- Creating AWS cloud architecture diagrams (VPC, subnets, services)
- Designing multi-tier application architectures on AWS
- Drawing serverless architecture diagrams (Lambda, API Gateway, DynamoDB)
- Visualizing network topologies with VPCs, subnets, and security groups
- Creating infrastructure diagrams for AWS Well-Architected reviews
- Documenting existing AWS infrastructure as visual diagrams

## Instructions

### Draw.io File Structure

Every `.drawio` file follows this XML structure:

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="aws-arch-1" name="AWS Architecture">
    <mxGraphModel dx="1434" dy="759" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- AWS shapes and connectors here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Key rules:**
- IDs "0" and "1" are reserved for root cells
- Use sequential integer IDs starting from "2"
- Use landscape orientation (`pageWidth="1169" pageHeight="827"`) for architecture diagrams
- All coordinates must be positive and aligned to grid (multiples of 10)

### AWS4 Group Containers

Groups are containers that visually organize AWS resources. They use `container=1` and child shapes reference the group via `parent="groupId"`.

**AWS Cloud (top-level boundary):**
```xml
<mxCell id="2" value="AWS Cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="40" width="1000" height="700" as="geometry" />
</mxCell>
```

**Region:** `grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fontColor=#147EBA;dashed=1;`
**VPC:** `grIcon=mxgraph.aws4.group_vpc;strokeColor=#8C4FFF;fontColor=#AAB7B8;`
**Public Subnet:** `grIcon=mxgraph.aws4.group_security_group;strokeColor=#7AA116;fillColor=#E9F3D2;fontColor=#248814;`
**Private Subnet:** `grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7;fontColor=#147EBA;`

### AWS4 Service Icons

Service icons use `shape=mxgraph.aws4.resourceIcon` with `resIcon` for the specific service, or dedicated shape names.

**CRITICAL: `strokeColor=#ffffff` is required** for all `resourceIcon` shapes. This makes the icon glyph render as **white** on the colored background.

**Standard service icon pattern:**
```xml
<mxCell id="10" value="Amazon S3" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#60A337;gradientDirection=north;fillColor=#277116;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="60" height="60" as="geometry" />
</mxCell>
```

**Note:** Dedicated shapes like `lambda_function`, `applicationLoadBalancer`, `users` do NOT use `resourceIcon` and should keep `strokeColor=none`.

### AWS Service Color Codes

Each AWS service category uses official colors. All `resourceIcon` shapes **must** use `strokeColor=#ffffff` and `gradientDirection=north`.

| Category | fillColor | gradientColor | Services |
|----------|-----------|---------------|----------|
| **Compute** | `#D05C17` | `#F78E04` | EC2, ECS, EKS, Fargate |
| **Storage** | `#277116` | `#60A337` | S3, EBS, EFS, Glacier |
| **Database** | `#3334B9` | `#4D72F3` | RDS, DynamoDB, ElastiCache, Aurora |
| **Networking** | `#5A30B5` | `#945DF2` | CloudFront, Route 53, API Gateway |
| **Security** | `#C7131F` | `#F54749` | IAM, Cognito, KMS, WAF |
| **App Integration** | `#BC1356` | `#F54749` | SQS, SNS, EventBridge, Step Functions |
| **ML** | `#116D5B` | `#4AB29A` | SageMaker, Bedrock, Comprehend |
| **Dedicated shapes** | `#ED7100` / `#8C4FFF` | none | Lambda, ALB (use `strokeColor=none`) |

### Connector Styles

**Standard data flow:**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;
```

**Secure/encrypted:** Add `endArrow=classic;endFill=1;strokeColor=#DD344C;dashed=1;dashPattern=5 5;`
**Async/event-driven:** Add `strokeColor=#E7157B;dashed=1;`

### Layout Best Practices

1. **Hierarchy**: External users -> AWS Cloud -> Region -> VPC -> Subnets -> Services
2. **Left-to-right flow**: User traffic enters from the left
3. **Standard sizes**: Service icons 60x60, group containers follow nesting
4. **Spacing**: 30-40px between service icons, 20px padding inside containers
5. **Grid alignment**: All coordinates in multiples of 10
6. **Labels**: Place below icons (`verticalLabelPosition=bottom;verticalAlign=top;`)

### Opening Diagrams

Always include: `Open in draw.io with AWS libraries: https://app.diagrams.net/?libs=aws4`

## Examples

### Minimal AWS Service Icon

```xml
<!-- Input: A single EC2 instance inside an AWS Cloud container -->
<mxGraphModel>
  <root>
    <mxCell id="0"/><mxCell id="1" parent="0"/>
    <mxCell id="2" value="AWS Cloud" style="points=[];outlineConnect=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud;strokeColor=#AAB7B8;fillColor=none;verticalAlign=top;fontStyle=1;fontSize=14;" vertex="1" parent="1">
      <mxGeometry x="20" y="20" width="200" height="150" as="geometry"/>
    </mxCell>
    <mxCell id="3" value="EC2" style="sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;" vertex="1" parent="2">
      <mxGeometry x="70" y="40" width="60" height="60" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
<!-- Output: Draw.io diagram with EC2 icon inside AWS Cloud group -->
```

See [references/examples.md](references/examples.md) for complete multi-service examples (Three-Tier, Serverless).

## Constraints and Warnings

1. **XML must be well-formed**: Close all tags, escape special characters (`&` -> `&amp;`, `<` -> `&lt;`)
2. **ID uniqueness is mandatory**: IDs "0"/"1" reserved, all others unique integers from "2"
3. **Coordinates**: All positive, multiples of 10 for grid alignment
4. **AWS4 library only**: Only `mxgraph.aws4.*` shapes supported (not aws3)
5. **Valid parent references**: `parent` attribute must reference existing cell ID

## Best Practices

1. **Always use official AWS4 shapes** for professional look
2. **Follow AWS color codes** per service category
3. **Use proper nesting** - AWS Cloud -> Region -> VPC -> Subnet -> Services
4. **Label everything** - Service names, CIDR blocks, ports, protocols
5. **Keep diagrams focused** - Max 15-20 service icons per diagram

## Reference Files

See the `references/` directory for:
- [aws-shape-reference.md](references/aws-shape-reference.md) - Complete AWS4 shape catalog (50+ services)
- [aws-architecture-templates.md](references/aws-architecture-templates.md) - Ready-to-use templates (3-tier, serverless, data pipeline)
- [examples.md](references/examples.md) - Full XML examples with step-by-step walkthrough
