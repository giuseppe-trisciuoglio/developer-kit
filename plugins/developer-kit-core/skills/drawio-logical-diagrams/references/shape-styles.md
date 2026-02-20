# Shape Styles Reference

Complete reference for draw.io shapes and styles used in logical diagrams.

## Basic Shapes

### Rectangle
```xml
style="rounded=0;whiteSpace=wrap;html=1;"
```

### Rounded Rectangle
```xml
style="rounded=1;whiteSpace=wrap;html=1;"
```

### Ellipse (Circle/Oval)
```xml
style="ellipse;whiteSpace=wrap;html=1;"
```

### Diamond (Rhombus)
```xml
style="rhombus;whiteSpace=wrap;html=1;"
```

### Cylinder (Database)
```xml
style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;"
```

### Hexagon
```xml
style="shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;"
```

### Parallelogram
```xml
style="shape=ext;double=1;rounded=0;whiteSpace=wrap;html=1;"
```

### Cloud (External System)
```xml
style="shape=cloud;whiteSpace=wrap;html=1;"
```

### Folder
```xml
style="shape=folder;whiteSpace=wrap;html=1;"
```

## Style Properties

### Fill Colors
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Light Blue | `#dae8fc` | Process/Service |
| Light Yellow | `#fff2cc` | Decision/Gateway |
| Light Green | `#d5e8d4` | Start/End/Success |
| Light Cyan | `#e1f5fe` | Data Store |
| Light Purple | `#f3e5f5` | External System |
| Light Red | `#f8cecc` | Error/Stop |
| Light Orange | `#ffe0b2` | Actor/User |
| Light Gray | `#f5f5f5` | Container |

### Border Colors
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Blue | `#6c8ebf` | Process border |
| Yellow | `#d6b656` | Decision border |
| Green | `#82b366` | Start/End border |
| Cyan | `#0277bd` | Data store border |
| Purple | `#7b1fa2` | External system border |
| Red | `#b85450` | Error/Stop border |
| Orange | `#f57c00` | Actor border |
| Gray | `#666666` | Container border |

### Font Settings
```xml
fontFamily=Segoe UI
fontSize=10-14
fontColor=#333333
fontStyle=0 (normal), 1 (bold), 2 (italic)
```

## Complete Shape Examples

### Process Box
```xml
<mxCell id="2" value="Process Name"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

### Decision Diamond
```xml
<mxCell id="3" value="Decision?"
  style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="280" y="200" width="80" height="80" as="geometry" />
</mxCell>
```

### Start/End Oval
```xml
<mxCell id="4" value="Start"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="300" width="80" height="40" as="geometry" />
</mxCell>
```

### Data Store (Cylinder)
```xml
<mxCell id="5" value="Database"
  style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#e1f5fe;strokeColor=#0277bd;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="60" height="80" as="geometry" />
</mxCell>
```

### External System (Cloud)
```xml
<mxCell id="6" value="External API"
  style="shape=cloud;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#7b1fa2;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="400" y="100" width="100" height="60" as="geometry" />
</mxCell>
```

### Actor/User
```xml
<mxCell id="7" value="User"
  style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffe0b2;strokeColor=#f57c00;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="50" y="200" width="60" height="40" as="geometry" />
</mxCell>
```

### Error State
```xml
<mxCell id="8" value="Error"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;fontFamily=Segoe UI;"
  vertex="1" parent="1">
  <mxGeometry x="300" y="200" width="100" height="50" as="geometry" />
</mxCell>
```

## Connector Styles

### Standard Arrow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;"
```

### Dashed Arrow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;dashPattern=5 5;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;"
```

### Open Arrow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=open;endFill=0;strokeColor=#666666;strokeWidth=2;"
```

### Block Arrow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=blockThin;endFill=1;strokeColor=#666666;strokeWidth=2;"
```

### Curved Arrow
```xml
style="edgeStyle=curvedEdgeStyle;rounded=0;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;"
```

### Edge with Label
```xml
<mxCell id="10" value="Label"
  style="text;html=1;align=center;verticalAlign=middle;fontSize=11;fontColor=#333333;labelBackgroundColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="250" y="160" width="40" height="20" as="geometry" />
</mxCell>
```

## Container Styles

### Simple Container
```xml
<mxCell id="20" value="Container Name"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="50" width="400" height="300" as="geometry" />
</mxCell>
```

### Dashed Container (Boundary)
```xml
<mxCell id="21" value="Boundary"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;dashPattern=8 4;fontSize=14;fontStyle=1;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="50" width="400" height="300" as="geometry" />
</mxCell>
```

## Child Elements in Containers

When placing elements inside a container, reference the container ID in the `parent` attribute:

```xml
<!-- Container -->
<mxCell id="20" value="Layer"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="50" width="400" height="300" as="geometry" />
</mxCell>

<!-- Child element inside container -->
<mxCell id="21" value="Service"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
  vertex="1" parent="20">
  <mxGeometry x="20" y="30" width="100" height="50" as="geometry" />
</mxCell>
```

## Special Characters

| Character | Entity |
|-----------|--------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| Line break | `&#xa;` or `<br>` with html=1 |

## Coordinate Guidelines

### Element Sizes
| Element Type | Width | Height |
|-------------|-------|--------|
| Process Box | 100-150 | 50-70 |
| Decision Diamond | 70-100 | 70-100 |
| Start/End | 70-100 | 35-50 |
| Data Store | 50-70 | 70-90 |
| Actor | 50-70 | 40-50 |

### Spacing
- Between elements: 40-60px
- Inside containers: 15-25px
- Connector to element: 10-15px
