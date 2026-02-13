# AWS4 Draw.io Shape Reference

Complete catalog of AWS Architecture Icon shapes for use in draw.io diagrams.

## Group Containers

All group containers share the base points array and these common properties:
```
outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;
shape=mxgraph.aws4.group;labelBackgroundColor=none;container=1;pointerEvents=0;
collapsible=0;recursiveResize=0;
```

| Group | grIcon | strokeColor | fillColor | fontColor |
|-------|--------|-------------|-----------|-----------|
| AWS Cloud | `group_aws_cloud_alt` | `#232F3E` | none | `#232F3E` |
| Region | `group_region` | `#00A4A6` | none | `#147EBA` |
| Availability Zone | `group_availability_zone` | `#007CBD` | none | `#007CBD` |
| VPC | `group_vpc` | `#8C4FFF` | none | `#AAB7B8` |
| Public Subnet | `group_security_group` | `#7AA116` | `#E9F3D2` | `#248814` |
| Private Subnet | `group_security_group` | `#00A4A6` | `#E6F6F7` | `#147EBA` |
| Security Group | `group_security_group` | `#DD344C` | `#F2DEDE` | `#DD344C` |
| Auto Scaling | `group_auto_scaling_group` | `#ED7100` | none | `#ED7100` |
| Account | `group_account` | `#CD2264` | none | `#CD2264` |
| Corporate Data Center | `group_corporate_data_center` | `#232F3E` | none | `#232F3E` |

## Compute Services

### EC2 Instance
```xml
<mxCell id="ID" value="Amazon EC2" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="60" height="60" as="geometry" />
</mxCell>
```

### Lambda Function
```xml
style="...fillColor=#ED7100;...shape=mxgraph.aws4.lambda_function;"
```

### ECS Service
```xml
style="...fillColor=#ED7100;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ecs;"
```

### EKS
```xml
style="...fillColor=#ED7100;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eks;"
```

### Fargate
```xml
style="...fillColor=#ED7100;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.fargate;"
```

### Auto Scaling
```xml
style="...fillColor=#ED7100;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.auto_scaling2;"
```

## Networking Services

### Elastic Load Balancer (ALB)
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_load_balancing;"
```

### Application Load Balancer
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.applicationLoadBalancer;"
```

### Network Load Balancer
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.networkLoadBalancer;"
```

### API Gateway
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway;"
```

### CloudFront
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudfront;"
```

### Route 53
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.route_53;"
```

### NAT Gateway
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.nat_gateway;"
```

### Internet Gateway
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.internet_gateway;"
```

### VPN Gateway
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.vpn_gateway;"
```

## Storage Services

### Amazon S3
```xml
style="...fillColor=#3F8624;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;"
```

### EBS (Elastic Block Store)
```xml
style="...fillColor=#3F8624;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_block_store;"
```

### EFS (Elastic File System)
```xml
style="...fillColor=#3F8624;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_file_system;"
```

### S3 Glacier
```xml
style="...fillColor=#3F8624;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.glacier;"
```

## Database Services

### Amazon RDS
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;"
```

### Aurora
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.aurora;"
```

### DynamoDB
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;"
```

### ElastiCache
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elasticache;"
```

### Redshift
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.redshift;"
```

## Security Services

### IAM
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.identity_and_access_management;"
```

### Cognito
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cognito;"
```

### KMS
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.key_management_service;"
```

### WAF
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.waf;"
```

### Shield
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.shield;"
```

### Secrets Manager
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.secrets_manager;"
```

### Certificate Manager
```xml
style="...fillColor=#DD344C;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.certificate_manager;"
```

## Application Integration

### SQS
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sqs;"
```

### SNS
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sns;"
```

### EventBridge
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.eventbridge;"
```

### Step Functions
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.step_functions;"
```

## Analytics

### Kinesis Data Streams
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.kinesis_data_streams;"
```

### Kinesis Data Firehose
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.kinesis_data_firehose;"
```

### Athena
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.athena;"
```

### Glue
```xml
style="...fillColor=#8C4FFF;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.glue;"
```

## Machine Learning

### SageMaker
```xml
style="...fillColor=#01A88D;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sagemaker;"
```

### Bedrock
```xml
style="...fillColor=#01A88D;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.bedrock;"
```

### Comprehend
```xml
style="...fillColor=#01A88D;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.comprehend;"
```

### Lex
```xml
style="...fillColor=#01A88D;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lex;"
```

### Rekognition
```xml
style="...fillColor=#01A88D;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rekognition;"
```

## Management & Monitoring

### CloudWatch
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;"
```

### CloudFormation
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudformation;"
```

### Systems Manager
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.systems_manager;"
```

### CloudTrail
```xml
style="...fillColor=#E7157B;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudtrail;"
```

## Developer Tools

### CodePipeline
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.codepipeline;"
```

### CodeBuild
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.codebuild;"
```

### CodeDeploy
```xml
style="...fillColor=#C925D1;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.codedeploy;"
```

## External Actors

### Users
```xml
style="...fillColor=#232F3E;...shape=mxgraph.aws4.users;"
```

### User (Single)
```xml
style="...fillColor=#232F3E;...shape=mxgraph.aws4.user;"
```

### Corporate Data Center
```xml
style="...fillColor=#232F3E;...shape=mxgraph.aws4.corporate_data_center;"
```

### Mobile Client
```xml
style="...fillColor=#232F3E;...shape=mxgraph.aws4.mobile_client;"
```

### IoT Device (Generic)
```xml
style="...fillColor=#232F3E;...shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.iot_core;"
```

## Common Points Array (for all service icons)

All AWS4 resource icons share this points array (abbreviated as `...` in examples above):

```
points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]]
```

## Standard Icon Size

- **Service icons**: 60x60 (use `aspect=fixed;`)
- **Small icons**: 40x40 (for inline/detail views)
- **Large icons**: 78x78 (for overview diagrams)

## Connector Styles

### Standard Data Flow
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;
```

### Elbow Data Flow
```
edgeStyle=elbowEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;
```

### Labeled Connector (with protocol)
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;
```

### Async / Event Flow
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#E7157B;strokeWidth=2;dashed=1;
```

### Secure / Encrypted
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#DD344C;strokeWidth=2;dashed=1;dashPattern=5 5;
```
