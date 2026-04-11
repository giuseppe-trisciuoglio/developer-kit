# Layout Best Practices for Draw.io Diagrams

## Flow Direction

1. **Consistent direction**: Choose left-to-right OR top-to-bottom and stick with it
2. **Primary flow**: Main process flows left-to-right or top-to-bottom
3. **Return loops**: Route return paths below (for L-R) or to the right (for T-B)

**Example:**
```
Left-to-Right:    Top-to-Bottom:
  A → B → C          A
  │   ↓   │          ↓ B
  └───D───┘          ↓ C
                     ↓ D
```

## Spacing Guidelines

| Element | Spacing |
|---------|---------|
| Between elements (horizontal) | 40-60px |
| Between elements (vertical) | 40-60px |
| Inside containers | 20px margin from edges |
| Between grouped elements | 20-30px |
| Label from arrow | 15-20px |

## Grid Alignment

1. **Snap to grid**: All coordinates in multiples of 10
2. **Center alignment**: Center elements on their midpoint
3. **Edge alignment**: Align edges of related elements

**Example:**
```
Good:                Bad:
┌────┐  ┌────┐       ┌────┐
│ A  │  │ B  │       │ A  │  ┌────┐
└────┘  └────┘       └────┘  │ B  │
                             └────┘
```

## Label Placement

| Arrow Direction | Label Position |
|----------------|----------------|
| Horizontal (→) | Above the arrow |
| Vertical (↓)   | Right of the arrow |
| Diagonal       | At the midpoint, offset slightly |

**Tips:**
- Use white background for labels on arrows: `labelBackgroundColor=#ffffff`
- Keep labels short (1-3 words)
- Use fontSize 10-11 for connector labels

## Container Grouping

1. **Purpose**: Group related elements visually
2. **Style**: Use rounded rectangles with gray fill
3. **Hierarchy**: Nest containers for sub-groups

**Example:**
```
┌─────────────────────────────────┐
│     Service Layer               │
│  ┌──────────┐  ┌──────────┐    │
│  │ Service A│  │ Service B│    │
│  └──────────┘  └──────────┘    │
└─────────────────────────────────┘
```

## Balance and Composition

1. **Center the diagram**: Keep main flow centered on canvas
2. **Avoid extreme whitespace**: Don't leave large empty areas
3. **Symmetry**: Use symmetrical layouts for parallel processes
4. **Weight distribution**: Balance elements visually

## Connector Routing

1. **Minimize bends**: Use straight lines when possible
2. **Orthogonal routing**: Use right-angle bends (orthogonalEdgeStyle)
3. **Avoid crossings**: Route connectors to minimize crossings
4. **Clear direction**: Arrowheads should clearly show flow direction

## Visual Hierarchy

1. **Size hierarchy**: Important elements can be slightly larger
2. **Color coding**: Use consistent colors for element types
3. **Font sizing**: 12-14px for primary labels, 10-11px for annotations
4. **Bold for emphasis**: Use `fontStyle=1` for important elements

## Accessibility

1. **High contrast**: Ensure text is readable against background
2. **Don't rely on color alone**: Use symbols and labels
3. **Text size**: Minimum 10-11px for readability
4. **Labels on all shapes**: Every shape should have a clear label

## Common Layout Patterns

### Sequential Flow
```
A → B → C → D
```
Simple left-to-right or top-to-bottom flow.

### Branching Flow
```
    A
    ↓
   ┌──┴──┐
   B     C
   └──┬──┘
     ↓
     D
```
Diamond decision point with branches.

### Parallel Processes
```
  A
┌─┴─┐
B   C
└─┬─┘
  D
```
Parallel activities that converge.

### Layered Architecture
```
┌───────────┐
│  Layer 1  │
├───────────┤
│  Layer 2  │
├───────────┤
│  Layer 3  │
└───────────┘
```
Horizontal layers with vertical flow.

### Hub and Spoke
```
    ┌─B─┐
    │   │
  A-─HUB─┐D
    │   │
    └─C─┘
```
Central component with connections.

## Canvas Size

**Standard sizes:**
- A4 Landscape: 1169 x 827 px
- A4 Portrait: 827 x 1169 px
- A3 Landscape: 1654 x 1169 px
- Letter Landscape: 1100 x 850 px

**Tip:** Set `pageWidth` and `pageHeight` in mxGraphModel to match your needs.

## Common Mistakes to Avoid

1. ❌ Inconsistent flow direction
2. ❌ Elements too close together
3. ❌ Misaligned connectors
4. ❌ Labels overlapping elements
5. ❌ Too many crossing connectors
6. ❌ Inconsistent element sizes
7. ❌ Poor color contrast
8. ❌ Missing labels on shapes
