# Shape Examples - XML Reference

Complete XML examples for common shapes in draw.io format.

## Simple Process Box

```xml
<mxCell id="2" value="Process Name"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

**Attributes:**
- `rounded=1` - Rounded corners (use 0 for square corners)
- `whiteSpace=wrap` - Text wraps within shape
- `html=1` - Enable HTML formatting
- `fillColor` - Background color
- `strokeColor` - Border color
- `fontSize` - Text size in pixels

## Decision Diamond

```xml
<mxCell id="3" value="Decision?"
  style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="280" y="200" width="80" height="80" as="geometry" />
</mxCell>
```

**Note:** Diamonds should be square (width = height) for best appearance.

## Start/End Oval

```xml
<mxCell id="4" value="Start"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="300" width="80" height="40" as="geometry" />
</mxCell>
```

**Style tip:** Use green for start points, red for end points.

## Data Store (Cylinder)

```xml
<mxCell id="5" value="Database"
  style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="60" height="80" as="geometry" />
</mxCell>
```

**Shape-specific attributes:**
- `shape=cylinder3` - Use cylinder shape
- `boundedLbl=1` - Keep label within cylinder bounds

## Process/Document (Parallelogram)

```xml
<mxCell id="6" value="Input Data"
  style="shape=ext;double=1;rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="200" width="120" height="60" as="geometry" />
</mxCell>
```

**Attributes:**
- `shape=ext` - Extended shape
- `double=1` - Creates parallelogram effect

## Container (Grouping Box)

```xml
<mxCell id="7" value="Subsystem"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="50" width="400" height="300" as="geometry" />
</mxCell>
```

**Usage:** Groups related elements together.

## Connector/Arrow (Standard Flow)

```xml
<mxCell id="10"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;"
  edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Attributes:**
- `edgeStyle=orthogonalEdgeStyle` - Right-angle bends
- `endArrow=classic` - Filled triangle arrowhead
- `endFill=1` - Solid arrowhead
- `strokeWidth=2` - Line thickness

## Dashed Connector (Alternative Flow)

```xml
<mxCell id="11"
  style="edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=5 5;strokeColor=#666666;"
  edge="1" parent="1" source="2" target="4">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Usage:** Shows optional or alternative flows.

## Label on Connector

```xml
<mxCell id="12" value="Data"
  style="text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#333333;labelBackgroundColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="250" y="160" width="40" height="20" as="geometry" />
</mxCell>
```

**Tip:** Position labels near the midpoint of connectors for clarity.

## Actor/User Symbol

```xml
<mxCell id="13" value="User"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="40" y="340" width="60" height="40" as="geometry" />
</mxCell>
```

**Color:** Orange indicates external actors/users.

## Error/Stop Symbol

```xml
<mxCell id="14" value="Error"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="300" width="80" height="40" as="geometry" />
</mxCell>
```

**Color:** Red indicates errors or exceptional conditions.

## Style Quick Reference

| Purpose | Style String |
|---------|--------------|
| Basic rectangle | `rounded=0;whiteSpace=wrap;html=1;` |
| Rounded rectangle | `rounded=1;whiteSpace=wrap;html=1;` |
| Circle/Ellipse | `ellipse;whiteSpace=wrap;html=1;` |
| Diamond | `rhombus;whiteSpace=wrap;html=1;` |
| Cylinder | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;` |
| Parallelogram | `shape=ext;double=1;rounded=0;whiteSpace=wrap;html=1;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;` |

## Geometry Tips

**Positioning:**
- Always use positive coordinates (x, y >= 0)
- Align to grid (multiples of 10)
- Allow 40-60px spacing between elements

**Sizing:**
- Process boxes: 100-140px wide, 50-70px high
- Diamonds: square (width = height)
- Cylinders: 60-80px wide, 80-100px high
- Labels on connectors: 30-50px wide, 20px high
