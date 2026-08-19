---
name: pr-review-comments
description: Provides a workflow for posting review findings from a JSON file as inline GitHub Pull Request comments attached to exact files and lines. Use when structured findings include file paths, line numbers, and messages that must be published on a PR. Triggers include "post these review comments on the PR", "associate comments to files in the PR", and "publish review findings to PR #N".
allowed-tools: Read, Write, Bash
---

# PR Review Comments

## Overview

Publish a JSON array of review findings as inline comments on a GitHub Pull Request,
each anchored to its file and line. Uses the GitHub API through the authenticated
`gh` CLI, so no token handling is needed.

## When to Use

Use this skill when structured review findings already have file paths and line
numbers and must become inline comments on an existing GitHub Pull Request.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). The script auto-detects the
  repo with `gh repo view`; pass `--repo OWNER/REPO` to override.
- The PR number to comment on.
- A JSON file: an **array** of objects. Required keys per object: `file`, `line`.
  Message comes from `summary` and/or `failure_scenario` (combined into the body), or an
  explicit `body`. See [references/json-schema.md](references/json-schema.md) for the full
  schema and a sample.

## Key constraint: only diff lines are commentable

GitHub only accepts an inline comment if the target line is part of the PR's diff.
`line` is the line number in the **new** file (use `side: "LEFT"` for removed lines).
The script fetches the PR diff, validates every finding against the actual hunks, and
**skips** any whose line is outside the diff — reporting them at the end so nothing is
lost silently. There is no way to attach a line comment to an unchanged, undiffed line.

## Instructions

1. Confirm the JSON path and the PR number. If the repo isn't obvious, run `gh repo view`.
2. **Dry-run first** to see what will be posted and what gets skipped:
   ```bash
   scripts/post_pr_comments.py --pr <N> --json <path> --dry-run
   ```
3. Review the "Postable" / "Skipped" counts with the user. If lines were skipped because
   the diff moved, the line numbers in the JSON may be stale — reconcile before posting.
4. Post for real, choosing the mode (see below):
   ```bash
   # Grouped (default): one PR review bundling all comments
   scripts/post_pr_comments.py --pr <N> --json <path> --event COMMENT

   # Individual: one separate inline comment per finding
   scripts/post_pr_comments.py --pr <N> --json <path> --mode individual
   ```
5. Report back the created review/comment URLs and the list of any skipped findings.

## Examples

- Dry-run a JSON findings file before posting it.
- Publish validated findings as one grouped `COMMENT` review.
- Publish individual findings when each needs its own notification thread.

## Best Practices

- Dry-run every findings file before posting.
- Reconcile stale line numbers against the current PR diff.
- Prefer one grouped `COMMENT` review to reduce notifications.

## Constraints and Warnings

- Posting comments changes external Pull Request state.
- Confirm the repository, PR number, findings file, and postable count first.
- GitHub accepts inline comments only on lines included in the PR diff.

## Choosing the mode

| Mode | Endpoint | Use when |
|------|----------|----------|
| `grouped` (default) | `POST /pulls/{n}/reviews` | Publishing a set of findings as one review. One notification; can set `--event APPROVE \| REQUEST_CHANGES \| COMMENT`. |
| `individual` | `POST /pulls/{n}/comments` | Adding standalone comments incrementally, or when each finding should be its own thread/notification. |

Default to `grouped` with `--event COMMENT` unless the user wants a verdict or separate threads.

## Options reference

```
--pr N              PR number (required)
--json PATH         JSON array of findings (required)
--repo OWNER/REPO   Override auto-detected repo
--mode grouped|individual   Default: grouped
--event COMMENT|APPROVE|REQUEST_CHANGES   Grouped-mode verdict (default COMMENT)
--review-body TEXT  Top-level summary body for the grouped review
--commit SHA        Commit to anchor to (default: PR head SHA)
--dry-run           Validate and print payloads without posting
```

## Notes

- Multi-line range comments: include `start_line` (and optional `start_side`) in the JSON
  object alongside `line`; the script passes them through.
- Always `--dry-run` before a real post on an unfamiliar PR — stale line numbers are the
  most common failure and the dry-run surfaces them as "skipped" without side effects.
- The script is the reliable path; don't hand-roll `gh api` calls for this — it handles
  diff validation, repo/commit detection, and body assembly consistently.
