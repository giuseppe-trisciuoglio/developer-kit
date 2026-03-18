---
name: drawio-logical-diagrams
description: 'Creates professional logical flow diagrams and logical system architecture diagrams using draw.io XML format (.drawio files). Use when creating: (1) logical flow diagrams showing data/process flow between system components, (2) logical architecture diagrams representing system structure without cloud provider specifics, (3) BPMN process diagrams, (4) UML diagrams (class, sequence, activity), (5) data flow diagrams (DFD), (6) decision flowcharts, or (7) system interaction diagrams. This skill focuses on generic/abstract representations, not AWS/Azure-specific architectures (use aws-drawio-architecture-diagrams for cloud diagrams).'
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
- Visualizing system interactions and sequences
- Documenting logical system design without cloud specifics

**Do NOT use for:**
- AWS/Azure/GCP architecture diagrams (use `aws-drawio-architecture-diagrams`)
- Infrastructure-specific diagrams

## Instructions

### Creating a Logical Diagram

1. **Analyze the request**: Understand the system/process to diagram
2. **Choose diagram type**: Flowchart, architecture, BPMN, UML, DFD, etc.
3. **Identify elements**: Determine actors, processes, data stores, connectors
4. **Draft XML structure**: Create the mxGraphModel with proper root cells
5. **Add shapes**: Create mxCell elements with appropriate styles
6. **Add connectors**: Link elements with edge elements
7. **Validate XML**: Ensure all tags are closed and IDs are unique
8. **Output**: Write the .drawio file for the user

### Key XML Components

- `mxfile`: Root element with host and version
- `diagram`: Contains the diagram definition
- `mxGraphModel`: Canvas settings (grid, page size)
- `root`: Container for all cells (must include id="0" and id="1")
- `mxCell`: Individual shapes (vertices) or connectors (edges)

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
| Parallelogram | `shape=ext;double=1;rounded=0;whiteSpace=wrap;html=1;` |

### Standard Color Palette

See [references/color-palette.md](references/color-palette.md) for complete color palette with usage guidelines.

### Connector Styles

**Standard flow:**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;strokeColor=#666666;strokeWidth=2;
```

**Dashed (alternative/optional):**
```
edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=5 5;strokeColor=#666666;
```

**Arrow head styles:**
- `endArrow=classic;endFill=1` - Filled triangle
- `endArrow=open;endFill=0` - Open arrow
- `endArrow=blockThin;endFill=1` - Block arrow

## Diagram Types

See [references/diagram-types-detailed.md](references/diagram-types-detailed.md) for comprehensive descriptions of all diagram types:
- Logical Flow Diagrams
- Logical Architecture Diagrams
- BPMN Process Diagrams
- UML Sequence Diagrams
- Data Flow Diagrams (DFD)
- Decision Flowcharts
- System Interaction Diagrams

## Shape Examples

See [references/shape-examples.md](references/shape-examples.md) for complete XML examples of:
- Basic shapes (Process, Decision, Start/End, Data Store)
- Connectors and arrows
- Labels and annotations
- Style variations

## Layout Best Practices

See [references/layout-best-practices.md](references/layout-best-practices.md) for detailed guidance on:
- Flow direction and consistency
- Spacing and alignment
- Grid alignment
- Label placement
- Container grouping
- Visual balance and composition

## Reference Files

For detailed information, see:
- [shape-styles.md](references/shape-styles.md) - Complete shape and style reference
- [diagram-templates.md](references/diagram-templates.md) - Ready-to-use templates
- [color-palette.md](references/color-palette.md) - Standard color palette
- [diagram-types-detailed.md](references/diagram-types-detailed.md) - All diagram types explained
- [shape-examples.md](references/shape-examples.md) - XML examples for common shapes
- [layout-best-practices.md](references/layout-best-practices.md) - Layout and composition guidelines
- [constraints-warnings.md](references/constraints-warnings.md) - Constraints and troubleshooting

## Best Practices

1. **Consistent colors**: Use the same colors for the same element types throughout a diagram
2. **Clear labeling**: Include text labels for all shapes
3. **Grid alignment**: Keep elements aligned to grid (multiples of 10)
4. **Minimal bends**: Use straight connectors with minimal bends
5. **High contrast**: Ensure text is readable against background colors
6. **Accessible design**: Don't rely solely on color to convey meaning

## Examples

### Input/Output Examples

**Simple Flow Diagram Request:**
```
Input: "Create a flow diagram showing user login"
Output: <mxfile>...</mxfile> (generates .drawio XML with user → login page → auth service → database flow)
```

**Architecture Diagram Request:**
```
Input: "Create a 3-tier architecture diagram"
Output: <mxfile>...</mxfile> (generates .drawio XML with presentation, application, and data layers)
```

See [references/diagram-templates.md](references/diagram-templates.md) for complete XML templates.

## Constraints and Warnings

See [references/constraints-warnings.md](references/constraints-warnings.md) for:
- Critical constraints (XML validity, unique IDs, valid references, positive coordinates)
- Common warnings and how to avoid them
- Validation checklist
- Troubleshooting guide
