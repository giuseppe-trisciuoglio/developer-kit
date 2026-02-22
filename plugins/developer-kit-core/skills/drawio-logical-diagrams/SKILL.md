---
name: drawio-logical-diagrams
description: 'Creates professional logical flow diagrams and logical system architecture diagrams using draw.io XML format (.drawio files). Use when creating: (1) logical flow diagrams showing data/process flow between system components, (2) logical architecture diagrams representing system structure without cloud provider specifics, (3) BPMN process diagrams, (4) UML diagrams (class, sequence, activity), (5) data flow diagrams (DFD), (6) decision flowcharts, or (7) system interaction diagrams. This skill focuses on generic/abstract representations, not AWS/Azure-specific architectures (use aws-drawio-architecture-diagrams for cloud diagrams).'
category: core
tags: [drawio, diagrams, flowchart, uml, bpmn, architecture, visualization]
allowed-tools: Read, Write, Bash
---

# Draw.io Logical Diagrams Creation

## Overview

Create professional logical diagrams in draw.io's native XML format. This skill enables generation of production-ready `.drawio` files for logical flow diagrams, system architecture visualizations, and abstract process representations using generic shapes and symbols.

## When to Use

Use this skill when:
- Creating logical flow diagrams showing data flow between system components
- Designing logical architecture diagrams (abstract system structure)
- Building BPMN process diagrams for business processes
- Drawing UML diagrams (class, sequence, activity, state)
- Creating data flow diagrams (DFD) for system analysis
- Making decision flowcharts with branching logic

**Do NOT use for:**
- AWS/Azure/GCP architecture diagrams (use `aws-drawio-architecture-diagrams`)

## Instructions

### Creating a Logical Diagram

1. **Analyze the request**: Understand the system/process to diagram
2. **Choose diagram type**: Flowchart, architecture, BPMN, UML, DFD, etc.
3. **Identify elements**: Determine actors, processes, data stores, connectors
4. **Draft XML structure**: Create the mxGraphModel with proper root cells
5. **Add shapes**: Create mxCell elements with appropriate styles
6. **Add connectors**: Link elements with edge elements
7. **Validate XML**: Ensure all tags are closed and IDs are unique
8. **Output**: Write the .drawio file

## Draw.io XML Structure

Every `.drawio` file follows this XML structure:

```xml
<mxfile host="app.diagrams.net" agent="Claude" version="24.7.17">
  <diagram id="logical-flow-1" name="Logical Flow">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Shapes and connectors here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Key rules:**
- IDs "0" and "1" are reserved for root cells
- Use sequential integer IDs starting from "2"
- Use landscape orientation for architecture diagrams
- All coordinates must be positive and aligned to grid (multiples of 10)

## Generic Shapes and Styles

### Basic Shape Types

| Shape | Style |
|-------|-------|
| Rectangle | `rounded=0;whiteSpace=wrap;html=1;` |
| Rounded Rectangle | `rounded=1;whiteSpace=wrap;html=1;` |
| Ellipse/Circle | `ellipse;whiteSpace=wrap;html=1;` |
| Diamond | `rhombus;whiteSpace=wrap;html=1;` |
| Cylinder | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;` |

### Standard Color Palette

| Element Type | Fill Color | Border Color | Usage |
|--------------|------------|--------------|-------|
| Process | `#dae8fc` | `#6c8ebf` | Operations/actions |
| Decision | `#fff2cc` | `#d6b656` | Conditional branches |
| Start/End | `#d5e8d4` | `#82b366` | Terminal states |
| Data/Store | `#e1f5fe` | `#0277bd` | Databases/files |
| Entity | `#f3e5f5` | `#7b1fa2` | External systems |
| Error/Stop | `#f8cecc` | `#b85450` | Error states |
| Actor/User | `#ffe0b2` | `#f57c00` | Users/actors |
| Container | `#f5f5f5` | `#666666` | Grouping areas |

### Connector Styles

**Standard flow:**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;
```

**Dashed (optional/alternative):** Add `dashed=1;dashPattern=5 5;`

**Arrow heads:** `endArrow=classic;endFill=1` (filled), `endArrow=open;endFill=0` (open), `endArrow=blockThin;endFill=1` (block)

## Diagram Types

### 1. Logical Flow Diagram
Shows logical flow of data/processes: Actors (orange) -> Services (blue) -> Data Stores (cyan), with External Systems (purple) and solid arrows for data flows.

### 2. Logical Architecture Diagram
Abstract layers: Presentation Layer -> Application Layer -> Data Layer, using containers for grouping.

### 3. BPMN Process Diagram
Circle (Start/End Event), Rounded Rectangle (Activity/Task), Diamond (Gateway/Decision), Arrow (Sequence Flow).

### 4. UML Sequence Diagram
Interaction between components with lifelines and numbered messages.

### 5. Data Flow Diagram (DFD)
External Entity (square), Process (circle/rounded), Data Store (open rectangle), Data Flow (arrow).

## Shape Examples

### Process Box
```xml
<mxCell id="2" value="Process Name"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="200" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

### Decision Diamond
```xml
<mxCell id="3" value="Decision?"
  style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;"
  vertex="1" parent="1">
  <mxGeometry x="280" y="200" width="80" height="80" as="geometry" />
</mxCell>
```

### Connector/Arrow
```xml
<mxCell id="10"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;"
  edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## Layout Best Practices

1. **Flow direction**: Left-to-right or top-to-bottom consistently
2. **Spacing**: 40-60px between elements, 20px inside containers
3. **Grid alignment**: All coordinates in multiples of 10
4. **Label placement**: Above horizontal arrows, right of vertical arrows
5. **Container grouping**: Use rounded rectangles for logical groupings

## Constraints and Warnings

1. **XML validity**: Always close tags properly and escape special characters
2. **Unique IDs**: All cell IDs must be unique (except parent "0" and "1")
3. **Valid references**: Source/target must reference existing cell IDs
4. **Positive coordinates**: All x, y values must be >= 0

## Best Practices

1. **Start with a skeleton**: Define containers first, then add elements inside
2. **Consistent styling**: Use the same color palette across the diagram
3. **Meaningful labels**: Every element and arrow should have a clear label
4. **Keep it simple**: Max 15-20 elements per diagram for readability

## Examples

### Simple Flow: Start -> Process -> End

```xml
<!-- Input: Create a basic 3-step flow diagram -->
<mxGraphModel>
  <root>
    <mxCell id="0"/><mxCell id="1" parent="0"/>
    <mxCell id="2" value="Start" style="ellipse;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="40" y="100" width="80" height="40" as="geometry"/>
    </mxCell>
    <mxCell id="3" value="Process Data" style="rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="180" y="90" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="4" value="End" style="ellipse;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
      <mxGeometry x="360" y="100" width="80" height="40" as="geometry"/>
    </mxCell>
    <mxCell id="5" style="edgeStyle=orthogonalEdgeStyle;endArrow=classic;" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
    <mxCell id="6" style="edgeStyle=orthogonalEdgeStyle;endArrow=classic;" edge="1" source="3" target="4" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
  </root>
</mxGraphModel>
<!-- Output: A horizontal flow diagram: green Start -> blue Process -> red End -->
```

See [references/examples.md](references/examples.md) for complete examples (Order Processing, Three-Tier Architecture, Microservice Flow).

## Reference Files

For detailed templates and shape references, see:
- [shape-styles.md](references/shape-styles.md) - Complete shape and style reference
- [diagram-templates.md](references/diagram-templates.md) - Ready-to-use templates (microservice, event-driven, decision tree, sequence, DFD)
- [examples.md](references/examples.md) - Full XML examples with step-by-step walkthrough
