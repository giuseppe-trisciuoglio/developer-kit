# Logical Diagram Examples

Detailed XML examples for logical diagrams in draw.io format.

## Example 1: Simple Order Processing Flow

**User Request:**
"Create a logical flow diagram showing order processing: customer submits order, system validates, if valid then processes payment and ships, if invalid notifies customer."

**Generated XML:**
```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="order-flow-1" name="Order Processing">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Start -->
        <mxCell id="2" value="Start"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="80" y="50" width="80" height="40" as="geometry" />
        </mxCell>
        <!-- Submit Order -->
        <mxCell id="3" value="Submit Order"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="60" y="130" width="120" height="60" as="geometry" />
        </mxCell>
        <!-- Validate -->
        <mxCell id="4" value="Validate&#xa;Order?"
          style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="80" y="230" width="80" height="80" as="geometry" />
        </mxCell>
        <!-- Invalid: Notify -->
        <mxCell id="5" value="Notify&#xa;Customer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="220" y="240" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Valid: Process Payment -->
        <mxCell id="6" value="Process&#xa;Payment"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="60" y="350" width="120" height="60" as="geometry" />
        </mxCell>
        <!-- Ship -->
        <mxCell id="7" value="Ship Order"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="60" y="450" width="120" height="60" as="geometry" />
        </mxCell>
        <!-- End -->
        <mxCell id="8" value="End"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="80" y="550" width="80" height="40" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="12" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="4" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="13" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="4" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="14" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="6" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="15" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="7" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="16" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;" edge="1" parent="1" source="5" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Example 2: Three-Tier Logical Architecture

**User Request:**
"Create a logical architecture diagram for a web application with presentation, business logic, and data tiers."

**Generated XML:**
```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="three-tier-1" name="Three-Tier Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- User -->
        <mxCell id="2" value="User"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="40" y="340" width="60" height="40" as="geometry" />
        </mxCell>
        <!-- Presentation Layer -->
        <mxCell id="3" value="Presentation Layer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="160" y="40" width="300" height="180" as="geometry" />
        </mxCell>
        <mxCell id="4" value="Web&#xa;Browser"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="3">
          <mxGeometry x="20" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Mobile&#xa;App"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="3">
          <mxGeometry x="120" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <mxCell id="6" value="API&#xa;Client"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="3">
          <mxGeometry x="200" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <!-- Application Layer -->
        <mxCell id="7" value="Application Layer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="160" y="260" width="300" height="180" as="geometry" />
        </mxCell>
        <mxCell id="8" value="API&#xa;Gateway"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="7">
          <mxGeometry x="20" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <mxCell id="9" value="Business&#xa;Logic"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="7">
          <mxGeometry x="110" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <mxCell id="10" value="Auth&#xa;Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="7">
          <mxGeometry x="200" y="30" width="80" height="50" as="geometry" />
        </mxCell>
        <!-- Data Layer -->
        <mxCell id="11" value="Data Layer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="160" y="480" width="300" height="180" as="geometry" />
        </mxCell>
        <mxCell id="12" value="Primary&#xa;Database"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="11">
          <mxGeometry x="20" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <mxCell id="13" value="Read&#xa;Replica"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="11">
          <mxGeometry x="100" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <mxCell id="14" value="Cache&#xa;(Redis)"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#fff3e0;strokeColor=#e65100;fontSize=12;"
          vertex="1" parent="11">
          <mxGeometry x="180" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="2" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="4" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="8" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="9" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" value="query" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=open;endFill=0;strokeColor=#666666;strokeWidth=1;fontSize=10;dashed=1;" edge="1" parent="1" source="9" target="14">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="9" target="13">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Example 3: Microservice Communication Flow

**User Request:**
"Create a logical diagram showing microservice architecture with API gateway, multiple services, and message queue for async communication."

**Reference:** See [diagram-templates.md](diagram-templates.md) for complete microservice template.
