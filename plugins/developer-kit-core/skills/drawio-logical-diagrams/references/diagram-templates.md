# Diagram Templates

Ready-to-use XML templates for common logical diagram types.

## 1. Microservice Architecture Template

Complete microservice architecture with API gateway, services, message queue, and databases.

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="microservice-1" name="Microservice Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Users -->
        <mxCell id="2" value="Users"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="40" y="350" width="60" height="40" as="geometry" />
        </mxCell>
        <!-- API Gateway -->
        <mxCell id="3" value="API&#xa;Gateway"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="160" y="330" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Service Layer -->
        <mxCell id="4" value="Service Layer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="320" y="200" width="500" height="300" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Order&#xa;Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="4">
          <mxGeometry x="20" y="30" width="100" height="50" as="geometry" />
        </mxCell>
        <mxCell id="6" value="User&#xa;Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="4">
          <mxGeometry x="140" y="30" width="100" height="50" as="geometry" />
        </mxCell>
        <mxCell id="7" value="Payment&#xa;Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="4">
          <mxGeometry x="260" y="30" width="100" height="50" as="geometry" />
        </mxCell>
        <mxCell id="8" value="Notification&#xa;Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="4">
          <mxGeometry x="380" y="30" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Message Queue -->
        <mxCell id="9" value="Message&#xa;Queue"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;"
          vertex="1" parent="4">
          <mxGeometry x="20" y="130" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Data Layer -->
        <mxCell id="10" value="Data Layer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
          vertex="1" parent="1">
          <mxGeometry x="320" y="550" width="500" height="200" as="geometry" />
        </mxCell>
        <mxCell id="11" value="Order&#xa;DB"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="10">
          <mxGeometry x="20" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <mxCell id="12" value="User&#xa;DB"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="10">
          <mxGeometry x="120" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <mxCell id="13" value="Payment&#xa;DB"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="10">
          <mxGeometry x="220" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <mxCell id="14" value="Cache"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#fff3e0;strokeColor=#e65100;fontSize=12;"
          vertex="1" parent="10">
          <mxGeometry x="380" y="30" width="60" height="80" as="geometry" />
        </mxCell>
        <!-- External Systems -->
        <mxCell id="15" value="Payment&#xa;Provider"
          style="shape=cloud;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="900" y="280" width="100" height="60" as="geometry" />
        </mxCell>
        <mxCell id="16" value="Email&#xa;Service"
          style="shape=cloud;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="900" y="380" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="3" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="5" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="7" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="9" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="5" target="11">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="26" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="6" target="12">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="27" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="7" target="13">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="28" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;dashed=1;" edge="1" parent="1" source="5" target="14">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="29" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="7" target="15">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="30" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;" edge="1" parent="1" source="8" target="16">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 2. Event-Driven Architecture Template

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="event-driven-1" name="Event-Driven Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Event Producer -->
        <mxCell id="2" value="Event&#xa;Producer"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="300" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Event Bus -->
        <mxCell id="3" value="Event Bus&#xa;(Kafka/EventGrid)"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="280" y="290" width="120" height="80" as="geometry" />
        </mxCell>
        <!-- Event Consumers -->
        <mxCell id="4" value="Consumer 1"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="480" y="150" width="100" height="60" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Consumer 2"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="480" y="290" width="100" height="60" as="geometry" />
        </mxCell>
        <mxCell id="6" value="Consumer 3"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="480" y="430" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="10" value="Events" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#7b1fa2;strokeWidth=2;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="12" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;" edge="1" parent="1" source="3" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="13" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;" edge="1" parent="1" source="3" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 3. Decision Tree Template

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="decision-tree-1" name="Decision Tree">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1000" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Root Decision -->
        <mxCell id="2" value="Valid&#xa;Input?"
          style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="400" y="50" width="100" height="100" as="geometry" />
        </mxCell>
        <!-- Yes branch -->
        <mxCell id="3" value="Check&#xa;Auth?"
          style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="250" y="200" width="100" height="100" as="geometry" />
        </mxCell>
        <!-- No branch -->
        <mxCell id="4" value="Return&#xa;Error"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="550" y="220" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Auth Yes -->
        <mxCell id="5" value="Process&#xa;Request"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="150" y="360" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Auth No -->
        <mxCell id="6" value="Return&#xa;401"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="350" y="360" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Process Yes -->
        <mxCell id="7" value="Return&#xa;Success"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="150" y="480" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Process No -->
        <mxCell id="8" value="Retry?"
          style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="300" y="460" width="80" height="80" as="geometry" />
        </mxCell>
        <!-- Retry Yes -->
        <mxCell id="9" value="Max&#xa;Retries?"
          style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="250" y="590" width="90" height="90" as="geometry" />
        </mxCell>
        <!-- Retry No -->
        <mxCell id="10" value="Return&#xa;500"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="420" y="590" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="20" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="2" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="3" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="3" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="5" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#d6b656;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="5" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="26" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="8" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="27" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#b85450;strokeWidth=2;fontSize=11;" edge="1" parent="1" source="8" target="10">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 4. Sequence Diagram Template

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="sequence-1" name="Sequence Diagram">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1000" pageHeight="700" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Actors -->
        <mxCell id="2" value="Client"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="80" y="40" width="80" height="40" as="geometry" />
        </mxCell>
        <mxCell id="3" value="API Gateway"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="250" y="40" width="100" height="40" as="geometry" />
        </mxCell>
        <mxCell id="4" value="Auth Service"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="420" y="40" width="100" height="40" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Business Logic"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="590" y="40" width="100" height="40" as="geometry" />
        </mxCell>
        <mxCell id="6" value="Database"
          style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="760" y="40" width="60" height="50" as="geometry" />
        </mxCell>
        <!-- Vertical lines (lifelines) -->
        <mxCell id="10" style="edgeStyle=elbowEdgeStyle;strokeColor=#cccccc;strokeWidth=1;dashed=1;dashPattern=3 3;" edge="1" parent="1" source="2" target="100">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="11" style="edgeStyle=elbowEdgeStyle;strokeColor=#cccccc;strokeWidth=1;dashed=1;" edge="1" parent="1" source="3" target="100">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="12" style="edgeStyle=elbowEdgeStyle;strokeColor=#cccccc;strokeWidth=1;dashed=1;" edge="1" parent="1" source="4" target="100">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="13" style="edgeStyle=elbowEdgeStyle;strokeColor=#cccccc;strokeWidth=1;dashed=1;" edge="1" parent="1" source="5" target="100">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="14" style="edgeStyle=elbowEdgeStyle;strokeColor=#cccccc;strokeWidth=1;dashed=1;" edge="1" parent="1" source="6" target="100">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- Messages -->
        <mxCell id="20" value="1. POST /resource" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" value="2. Validate Token" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="3" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" value="3. Token OK" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="4" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="4. Process Request" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="3" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" value="5. Save Data" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="5" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" value="6. Data Saved" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="6" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="26" value="7. Response" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="5" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="27" value="8. 201 Created" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="3" target="2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 5. Data Flow Diagram (DFD) Template

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="dfd-1" name="Data Flow Diagram">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- External Entities -->
        <mxCell id="2" value="Customer"
          style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="50" y="300" width="80" height="50" as="geometry" />
        </mxCell>
        <mxCell id="3" value="Supplier"
          style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="900" y="300" width="80" height="50" as="geometry" />
        </mxCell>
        <!-- Processes -->
        <mxCell id="4" value="Order&#xa;Processing"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="300" y="150" width="100" height="60" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Inventory&#xa;Management"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="500" y="150" width="100" height="60" as="geometry" />
        </mxCell>
        <mxCell id="6" value="Payment&#xa;Processing"
          style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="400" y="350" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- Data Stores -->
        <mxCell id="7" value="Orders"
          style="shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="300" y="500" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="8" value="Products"
          style="shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="500" y="500" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="9" value="Customers"
          style="shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="500" width="80" height="60" as="geometry" />
        </mxCell>
        <!-- Connectors -->
        <mxCell id="20" value="Order" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="2" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="21" value="Request" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="4" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="22" value="Payment Info" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="4" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="23" value="Order Conf." style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="4" target="2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="24" value="Product Info" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="5" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="25" value="Update" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="8" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="26" value="Confirmation" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="6" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="27" value="Save Order" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="4" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="28" value="Customer Data" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="2" target="9">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```
