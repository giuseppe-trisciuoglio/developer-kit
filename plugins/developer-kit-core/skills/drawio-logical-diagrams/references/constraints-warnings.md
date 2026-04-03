# Constraints and Warnings for Draw.io Logical Diagrams

## Critical Constraints

### 1. XML Validity

**Rule:** All XML tags must be properly closed and escaped.

**What to check:**
- Every `<mxCell>` has a closing `</mxCell>` tag
- Special characters in values are escaped: `&amp;` for `&`, `&lt;` for `<`, `&gt;` for `>`
- All attributes are quoted: `attribute="value"`
- Proper nesting of elements

**Example of proper escaping:**
```xml
<!-- Good -->
<mxCell value="A &amp; B Process" />

<!-- Bad -->
<mxCell value="A & B Process" />
```

### 2. Unique IDs

**Rule:** All cell IDs must be unique (except parent cells "0" and "1").

**ID assignment:**
- ID "0" is reserved for root container
- ID "1" is reserved for main parent
- Use sequential integers starting from "2" for all other cells
- Never duplicate an ID within the same diagram

**Example:**
```xml
<!-- Good -->
<mxCell id="2" ... />
<mxCell id="3" ... />
<mxCell id="4" ... />

<!-- Bad -->
<mxCell id="2" ... />
<mxCell id="2" ... />  <!-- Duplicate! -->
```

### 3. Valid References

**Rule:** Source and target attributes must reference existing cell IDs.

**What to check:**
- Every `source="X"` must have a corresponding cell with `id="X"`
- Every `target="Y"` must have a corresponding cell with `id="Y"`
- Parent references must point to valid parent cells

**Example:**
```xml
<!-- Good -->
<mxCell id="2" value="Box A" vertex="1" parent="1" />
<mxCell id="3" value="Box B" vertex="1" parent="1" />
<mxCell id="10" edge="1" parent="1" source="2" target="3" />

<!-- Bad -->
<mxCell id="10" edge="1" parent="1" source="99" target="100" />
<!-- IDs 99 and 100 don't exist! -->
```

### 4. Positive Coordinates

**Rule:** All x, y values must be >= 0.

**What to check:**
- `x` attribute in mxGeometry: must be >= 0
- `y` attribute in mxGeometry: must be >= 0
- Width and height must be > 0

**Example:**
```xml
<!-- Good -->
<mxGeometry x="100" y="200" width="120" height="60" />

<!-- Bad -->
<mxGeometry x="-50" y="100" width="120" height="60" />
<!-- Negative x will place element off-screen -->
```

## Warnings

### 1. XML Well-Formedness

**Warning:** XML files must be well-formed or will fail to open in draw.io.

**Symptoms:**
- File won't open in draw.io
- Error message about invalid XML
- Missing elements or corrupted layout

**Prevention:**
- Use XML validation tools
- Check for proper tag closure
- Escape special characters
- Validate structure before saving

### 2. Invalid Parent References

**Warning:** Invalid parent references cause elements to disappear.

**Symptoms:**
- Some elements don't appear in diagram
- Elements appear in wrong location
- Hierarchy is broken

**Prevention:**
- Ensure parent="1" for top-level elements
- For child elements, parent should match container's ID
- Verify parent IDs exist in the diagram

### 3. Negative Coordinates

**Warning:** Negative coordinates place elements outside visible canvas.

**Symptoms:**
- Elements not visible when diagram opens
- Need to zoom out or pan to find elements
- Layout appears broken

**Prevention:**
- Always use x >= 0, y >= 0
- Set canvas size appropriately
- Check element positions before saving

### 4. ID Conflicts

**Warning:** Duplicate IDs cause unpredictable behavior.

**Symptoms:**
- Connectors attach to wrong elements
- Elements appear/disappear randomly
- Saving/loading corrupts the diagram

**Prevention:**
- Use sequential integers: 2, 3, 4, 5, ...
- Never reuse an ID
- Track used IDs in complex diagrams

### 5. Missing Required Attributes

**Warning:** Missing required attributes causes rendering issues.

**Required for vertices (shapes):**
- `id` - Unique identifier
- `value` - Display text (can be empty)
- `style` - Visual styling
- `vertex="1"` - Marks as vertex
- `parent` - Parent cell ID
- `mxGeometry` - Position and size

**Required for edges (connectors):**
- `id` - Unique identifier
- `style` - Connector styling
- `edge="1"` - Marks as edge
- `parent` - Parent cell ID
- `source` - Starting cell ID
- `target` - Ending cell ID
- `mxGeometry` - Path information

### 6. Style String Errors

**Warning:** Malformed style strings prevent proper rendering.

**Common errors:**
- Missing semicolons between style properties
- Invalid property names
- Misspelled values

**Example:**
```xml
<!-- Good -->
<style>rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;</style>

<!-- Bad -->
<style>rounded=1 whiteSpace=wrap</style>  <!-- Missing semicolons -->
<style>rounded=1;invalidProperty=value;</style>  <!-- Invalid property -->
```

### 7. Canvas Size Issues

**Warning:** Elements placed outside canvas bounds may be clipped.

**Prevention:**
- Set appropriate `pageWidth` and `pageHeight` in mxGraphModel
- Ensure all elements fit within canvas
- Leave margin around edges (at least 50px)

**Example:**
```xml
<mxGraphModel dx="1200" dy="800"
  pageWidth="1169" pageHeight="827"
  ...>
```

## Validation Checklist

Before finalizing a diagram, verify:

- [ ] All XML tags properly closed
- [ ] Special characters escaped (&, <, >)
- [ ] All cell IDs unique (sequential 2, 3, 4...)
- [ ] All source/target IDs reference existing cells
- [ ] All coordinates >= 0
- [ ] All required attributes present
- [ ] Style strings properly formatted
- [ ] Elements fit within canvas bounds
- [ ] Parent references are valid
- [ ] No duplicate IDs

## Troubleshooting

**Problem:** Diagram won't open
- Check XML well-formedness
- Verify all tags are closed
- Check for special characters that need escaping

**Problem:** Elements missing
- Verify parent references are valid
- Check for negative coordinates
- Ensure elements are within canvas bounds

**Problem:** Connectors broken
- Verify source and target IDs exist
- Check for duplicate IDs
- Ensure edge has proper geometry

**Problem:** Layout appears wrong
- Check all element coordinates
- Verify canvas size is adequate
- Ensure consistent spacing and alignment
