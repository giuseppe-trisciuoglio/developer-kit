# AWS Architecture Diagram Templates

Ready-to-use draw.io XML templates for common AWS architecture patterns.

## Template 1: Three-Tier Web Application

Classic 3-tier architecture with ALB, EC2 Auto Scaling, and RDS Multi-AZ.

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="three-tier-1" name="Three-Tier Web App">
    <mxGraphModel dx="1434" dy="759" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Users -->
        <mxCell id="2" value="Users" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#232F3E;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.users;" vertex="1" parent="1">
          <mxGeometry x="40" y="340" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- AWS Cloud -->
        <mxCell id="3" value="AWS Cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="960" height="720" as="geometry" />
        </mxCell>

        <!-- Region -->
        <mxCell id="4" value="us-east-1" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=1;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="3">
          <mxGeometry x="20" y="40" width="920" height="660" as="geometry" />
        </mxCell>

        <!-- VPC -->
        <mxCell id="5" value="VPC (10.0.0.0/16)" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="4">
          <mxGeometry x="20" y="40" width="880" height="600" as="geometry" />
        </mxCell>

        <!-- Public Subnet AZ-a -->
        <mxCell id="6" value="Public Subnet (10.0.1.0/24) - AZ-a" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#7AA116;fillColor=#E9F3D2;verticalAlign=top;align=left;spacingLeft=30;fontColor=#248814;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="20" y="40" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- Public Subnet AZ-b -->
        <mxCell id="7" value="Public Subnet (10.0.2.0/24) - AZ-b" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#7AA116;fillColor=#E9F3D2;verticalAlign=top;align=left;spacingLeft=30;fontColor=#248814;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="460" y="40" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- Private Subnet AZ-a -->
        <mxCell id="8" value="Private Subnet (10.0.3.0/24) - AZ-a" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="20" y="230" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- Private Subnet AZ-b -->
        <mxCell id="9" value="Private Subnet (10.0.4.0/24) - AZ-b" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="460" y="230" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- Data Subnet AZ-a -->
        <mxCell id="10" value="Data Subnet (10.0.5.0/24) - AZ-a" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="20" y="420" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- Data Subnet AZ-b -->
        <mxCell id="11" value="Data Subnet (10.0.6.0/24) - AZ-b" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=11;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="5">
          <mxGeometry x="460" y="420" width="400" height="160" as="geometry" />
        </mxCell>

        <!-- ALB in Public Subnet -->
        <mxCell id="12" value="Application&lt;br&gt;Load Balancer" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#8C4FFF;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.applicationLoadBalancer;" vertex="1" parent="6">
          <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- EC2 Instance AZ-a -->
        <mxCell id="13" value="EC2 Instance" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;" vertex="1" parent="8">
          <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- EC2 Instance AZ-b -->
        <mxCell id="14" value="EC2 Instance" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;" vertex="1" parent="9">
          <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- RDS Primary AZ-a -->
        <mxCell id="15" value="RDS Primary" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;" vertex="1" parent="10">
          <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- RDS Standby AZ-b -->
        <mxCell id="16" value="RDS Standby" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;" vertex="1" parent="11">
          <mxGeometry x="170" y="50" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Connectors -->
        <mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="1" source="2" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="12" target="13">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="12" target="14">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="TCP 5432" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="13" target="15">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" value="Replication" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#C925D1;strokeWidth=2;dashed=1;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="15" target="16">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Template 2: Serverless API Architecture

API Gateway + Lambda + DynamoDB with Cognito authentication.

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="serverless-1" name="Serverless API">
    <mxGraphModel dx="1434" dy="759" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Mobile Client -->
        <mxCell id="2" value="Mobile App" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#232F3E;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.mobile_client;" vertex="1" parent="1">
          <mxGeometry x="40" y="240" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Users -->
        <mxCell id="3" value="Web Users" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#232F3E;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.users;" vertex="1" parent="1">
          <mxGeometry x="40" y="400" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- AWS Cloud -->
        <mxCell id="4" value="AWS Cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="960" height="700" as="geometry" />
        </mxCell>

        <!-- CloudFront -->
        <mxCell id="5" value="Amazon&lt;br&gt;CloudFront" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudfront;" vertex="1" parent="4">
          <mxGeometry x="40" y="280" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Cognito -->
        <mxCell id="6" value="Amazon&lt;br&gt;Cognito" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cognito;" vertex="1" parent="4">
          <mxGeometry x="250" y="60" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- API Gateway -->
        <mxCell id="7" value="Amazon API&lt;br&gt;Gateway" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway;" vertex="1" parent="4">
          <mxGeometry x="250" y="280" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Lambda Functions -->
        <mxCell id="8" value="GET&lt;br&gt;Lambda" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.lambda_function;" vertex="1" parent="4">
          <mxGeometry x="480" y="180" width="60" height="60" as="geometry" />
        </mxCell>

        <mxCell id="9" value="POST&lt;br&gt;Lambda" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.lambda_function;" vertex="1" parent="4">
          <mxGeometry x="480" y="380" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- DynamoDB -->
        <mxCell id="10" value="Amazon&lt;br&gt;DynamoDB" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;" vertex="1" parent="4">
          <mxGeometry x="720" y="280" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- S3 -->
        <mxCell id="11" value="Amazon S3" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#60A337;gradientDirection=north;fillColor=#277116;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;" vertex="1" parent="4">
          <mxGeometry x="720" y="520" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- CloudWatch -->
        <mxCell id="12" value="Amazon&lt;br&gt;CloudWatch" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;" vertex="1" parent="4">
          <mxGeometry x="480" y="520" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Connectors -->
        <mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="1" source="2" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="1" source="3" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="4" source="5" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="Auth" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#DD344C;strokeWidth=2;dashed=1;fontSize=11;labelBackgroundColor=#FFFFFF;" edge="1" parent="4" source="7" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="4" source="7" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="4" source="7" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="26" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="4" source="8" target="10">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="27" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="4" source="9" target="10">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="28" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="4" source="9" target="11">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="29" value="Logs" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#E7157B;strokeWidth=1;dashed=1;fontSize=10;labelBackgroundColor=#FFFFFF;" edge="1" parent="4" source="8" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Template 3: Event-Driven Data Pipeline

S3 → Lambda → Kinesis → Lambda → DynamoDB + S3 with monitoring.

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="data-pipeline-1" name="Data Pipeline">
    <mxGraphModel dx="1434" dy="759" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- AWS Cloud -->
        <mxCell id="2" value="AWS Cloud" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;labelBackgroundColor=none;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="1080" height="500" as="geometry" />
        </mxCell>

        <!-- Ingestion Layer Label -->
        <mxCell id="3" value="Ingestion" style="text;html=1;align=center;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#3F8624;" vertex="1" parent="2">
          <mxGeometry x="40" y="40" width="100" height="30" as="geometry" />
        </mxCell>

        <!-- Processing Layer Label -->
        <mxCell id="4" value="Processing" style="text;html=1;align=center;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#ED7100;" vertex="1" parent="2">
          <mxGeometry x="350" y="40" width="100" height="30" as="geometry" />
        </mxCell>

        <!-- Storage Layer Label -->
        <mxCell id="5" value="Storage" style="text;html=1;align=center;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#C925D1;" vertex="1" parent="2">
          <mxGeometry x="750" y="40" width="100" height="30" as="geometry" />
        </mxCell>

        <!-- S3 Raw Data -->
        <mxCell id="10" value="S3 Raw&lt;br&gt;Data Bucket" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#60A337;gradientDirection=north;fillColor=#277116;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;" vertex="1" parent="2">
          <mxGeometry x="60" y="120" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Lambda Ingestion -->
        <mxCell id="11" value="Ingestion&lt;br&gt;Lambda" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.lambda_function;" vertex="1" parent="2">
          <mxGeometry x="240" y="120" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Kinesis Data Stream -->
        <mxCell id="12" value="Kinesis&lt;br&gt;Data Streams" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#945DF2;gradientDirection=north;fillColor=#5A30B5;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.kinesis_data_streams;" vertex="1" parent="2">
          <mxGeometry x="440" y="120" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Lambda Processing -->
        <mxCell id="13" value="Processing&lt;br&gt;Lambda" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.lambda_function;" vertex="1" parent="2">
          <mxGeometry x="620" y="120" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- DynamoDB -->
        <mxCell id="14" value="Amazon&lt;br&gt;DynamoDB" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;" vertex="1" parent="2">
          <mxGeometry x="830" y="80" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- S3 Processed -->
        <mxCell id="15" value="S3 Processed&lt;br&gt;Data" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#60A337;gradientDirection=north;fillColor=#277116;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.s3;" vertex="1" parent="2">
          <mxGeometry x="830" y="200" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- SQS Dead Letter Queue -->
        <mxCell id="16" value="SQS DLQ" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sqs;" vertex="1" parent="2">
          <mxGeometry x="620" y="340" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- CloudWatch -->
        <mxCell id="17" value="CloudWatch&lt;br&gt;Monitoring" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch;" vertex="1" parent="2">
          <mxGeometry x="350" y="340" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- SNS Alerts -->
        <mxCell id="18" value="SNS Alerts" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.sns;" vertex="1" parent="2">
          <mxGeometry x="130" y="340" width="60" height="60" as="geometry" />
        </mxCell>

        <!-- Data Flow Connectors -->
        <mxCell id="30" value="S3 Event" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;fontSize=10;labelBackgroundColor=#FFFFFF;" edge="1" parent="2" source="10" target="11">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="31" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="2" source="11" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="32" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="2" source="12" target="13">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="33" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="2" source="13" target="14">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="34" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#545B64;strokeWidth=2;" edge="1" parent="2" source="13" target="15">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="35" value="Errors" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#DD344C;strokeWidth=2;dashed=1;fontSize=10;labelBackgroundColor=#FFFFFF;" edge="1" parent="2" source="13" target="16">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="36" value="Metrics" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#E7157B;strokeWidth=1;dashed=1;fontSize=10;labelBackgroundColor=#FFFFFF;" edge="1" parent="2" source="11" target="17">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="37" value="Alarms" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;endFill=0;strokeColor=#E7157B;strokeWidth=1;dashed=1;fontSize=10;labelBackgroundColor=#FFFFFF;" edge="1" parent="2" source="17" target="18">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## How to Use Templates

1. Copy the XML template above
2. Save as a `.drawio` file
3. Open at: `https://app.diagrams.net/?libs=aws4`
4. Modify service names, labels, and layout to match your architecture
5. Add/remove service icons from the `aws-shape-reference.md` catalog
