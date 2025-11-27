---
description: Add a new feature to the feature list
allowed-tools: Read, Write, Edit
argument-hint: [category] [priority] [description]
---

# Long-Running Agent - Add Feature

Add a new feature to the project's feature list.

## Arguments

- **$1** (category): core | ui | api | database | auth | testing | other
- **$2** (priority): critical | high | medium | low  
- **$3+** (description): Description of the feature

## Example Usage

```
/lra:add-feature api high Add endpoint to retrieve user preferences
/lra:add-feature ui medium Implement dark mode toggle in settings
```

## Your Task

1. Read the current `.lra/feature-list.json`

2. Determine the next feature ID:
   - Find the highest existing ID (e.g., F042)
   - Increment by 1 (e.g., F043)

3. Create the new feature object:

```json
{
  "id": "F[next_number]",
  "category": "$1",
  "priority": "$2",
  "description": "$3 (and remaining arguments)",
  "acceptance_criteria": [
    "Generate 2-4 reasonable acceptance criteria based on the description"
  ],
  "status": "pending",
  "completed_at": null,
  "notes": ""
}
```

4. Add the feature to the `features` array in the appropriate position:
   - Critical priority: near the top (after other critical)
   - High priority: after critical features
   - Medium/Low: at the end

5. Save the updated feature-list.json

## Output

Confirm the feature was added:

```
✅ Feature Added

ID: F043
Category: api
Priority: high
Description: Add endpoint to retrieve user preferences

Acceptance Criteria:
- GET /api/users/{id}/preferences returns user preferences
- Response includes all preference categories
- Unauthorized requests return 401

Total features: 43 (38 pending, 5 completed)
```
