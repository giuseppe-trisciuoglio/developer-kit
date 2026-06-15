# Findings JSON schema

The input is a JSON **array**. Each element is one inline comment.

| Key | Required | Default | Meaning |
|-----|----------|---------|---------|
| `file` | yes | — | Path relative to repo root (matches the path in the diff). |
| `line` | yes | — | Line number in the **new** file (or old file if `side` is `LEFT`). |
| `summary` | no* | — | Short headline; used to build the comment body. |
| `failure_scenario` | no* | — | Longer explanation; appended under **Failure scenario:**. |
| `body` | no* | — | Explicit Markdown body. Overrides `summary` + `failure_scenario`. |
| `side` | no | `RIGHT` | `RIGHT` = added/unchanged line, `LEFT` = removed line. |
| `start_line` | no | — | First line of a multi-line range comment. |
| `start_side` | no | `side` | Side of `start_line`. |

\* At least one of `body`, `summary`, or `failure_scenario` must be present, otherwise
the item is skipped with reason "empty body".

## Body assembly

When `body` is absent, the comment body is built as:

```
<summary>

**Failure scenario:** <failure_scenario>
```

Either part is omitted if its source field is missing.

## Sample

```json
[
  {
    "file": "libs/shared/procedure-dto/src/lib/status-update.dto.ts",
    "line": 148,
    "summary": "Adding `skip_email?: boolean` while keeping `email` required makes the 'Salta invio' feature return 400 from the controller.",
    "failure_scenario": "User clicks 'Salta invio' -> client POSTs without `email`; the ValidationPipe validates the first union member where `email` is `@ValidateNested()` with no `@IsOptional`, so the request is rejected with 400 before reaching the service."
  },
  {
    "file": "libs/server/procedure-feature/src/lib/services/procedure-data.service.ts",
    "line": 1770,
    "body": "`sanifiedSize(0)` returns undefined because of `if (!size) return undefined;`, so a valid numeric `0` size is reported as missing."
  }
]
```

## Skipped items

An item is skipped (and reported, never posted) when:

- `file` or `line` is missing.
- The computed body is empty.
- `file` is not part of the PR diff.
- `line` (for the given `side`) is not inside any diff hunk — typically because the line
  number is stale relative to the current PR head, or the line is unchanged context
  outside the diff window.
