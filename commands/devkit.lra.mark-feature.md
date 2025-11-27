---
description: Mark a feature as completed (passed) or failed
allowed-tools: Read, Write, Edit
argument-hint: [feature-id] [passed|failed] [optional-notes]
---

# Long-Running Agent - Mark Feature Status

Update the status of a feature in the feature list.

## Arguments

- **$1** (feature-id): The feature ID (e.g., F012)
- **$2** (status): `passed` or `failed`
- **$3+** (notes): Optional notes about the completion or failure

## Example Usage

```
/lra:mark-feature F012 passed
/lra:mark-feature F015 failed API rate limiting not yet implemented
/lra:mark-feature F023 passed Implemented with Redis caching
```

## Your Task

1. Read `.lra/feature-list.json`

2. Find the feature with ID = `$1`
   - If not found, report error and list available IDs

3. Update the feature:

**If marking as `passed`:**
```json
{
  "status": "passed",
  "completed_at": "ISO timestamp",
  "notes": "$3 (if provided)"
}
```

**If marking as `failed`:**
```json
{
  "status": "failed",
  "completed_at": null,
  "notes": "$3 (required - explain why it failed)"
}
```

4. Save the updated feature-list.json

## Important Rules

- **ONLY mark as passed after TESTING the feature end-to-end**
- **It is UNACCEPTABLE to mark features as passed without verification**
- **Do NOT remove or edit the feature description or acceptance criteria**
- **Failed features should include clear notes about what went wrong**

## Output

Confirm the status update:

```
✅ Feature Updated

ID: F012
Description: User can create a new account
Status: passed ✓
Completed: 2024-01-15T14:32:00Z
Notes: Implemented with email verification

Progress: 6/42 features completed (14%)
```

Or for failures:

```
⚠️ Feature Marked as Failed

ID: F015
Description: API rate limiting per user
Status: failed ✗
Notes: API rate limiting not yet implemented - needs Redis setup first

This feature remains in the backlog for future implementation.
```
