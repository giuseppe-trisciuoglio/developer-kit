---
name: pr-review-comments
description: Creates inline comments on a GitHub Pull Request from a JSON findings file, attaching each comment to its file and line. Use when you have a list/JSON of review findings (each with a file path, line number, and a message such as summary/failure_scenario) and want them published on a PR as inline review comments. Triggers include "post these review comments on the PR", "associate comments to files in the PR", "publish review findings to PR #N", or having a JSON array of {file, line, summary} to turn into PR comments.
allowed-tools: Read, Write, Bash
---

# PR Review Comments

Publish a JSON array of review findings as inline comments on a GitHub Pull Request,
each anchored to its file and line. Uses the GitHub API through the authenticated
`gh` CLI, so no token handling is needed.

## Overview

This skill takes a JSON array of review findings and turns them into inline comments on a
GitHub Pull Request. For each finding it validates the target line against the PR's actual
diff, anchors the comment to the matching file and line, and posts it via the GitHub API
using the authenticated `gh` CLI. Findings whose line falls outside the diff are reported
and skipped rather than lost — nothing is posted without the user's awareness.

It distinguishes two posting modes: a `grouped` mode that bundles all comments into a
single PR review, and an `individual` mode that posts each finding as its own separate
inline comment.

## When to Use

Use this skill whenever you have a set of review findings and need them published on a
Pull Request as inline, line-anchored comments:

- After a code review pass produces a JSON report and you want the findings visible on the PR.
- When a list of `{file, line, summary}` items should become per-file, per-line threads.
- To attach approval/request-changes verdicts to a review together with the findings.
- Typical prompts: "post these review comments on the PR", "associate comments to files in the PR", "publish review findings to PR #N".

Do not use it for ad-hoc `gh api` calls to comment on a PR — the bundled script validates
diff hunks and assembles bodies consistently, so hand-rolling is more error-prone.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). The script auto-detects the
  repo with `gh repo view`; pass `--repo OWNER/REPO` to override.
- The PR number to comment on.
- A JSON file: an **array** of objects. Required keys per object: `file`, `line`.
  Message comes from `summary` and/or `failure_scenario` (combined into the body), or an
  explicit `body`. See [references/json-schema.md](references/json-schema.md) for the full
  schema and a sample.

## Instructions

### 1. Confirm the inputs

Confirm the JSON path and the PR number. If the repo isn't obvious, run `gh repo view`.

### 2. Dry-run first

Always validate before posting to see what will be posted and what gets skipped:

```bash
scripts/post_pr_comments.py --pr <N> --json <path> --dry-run
```

Review the "Postable" / "Skipped" counts with the user. If lines were skipped because the
diff moved, the line numbers in the JSON may be stale — reconcile before posting.

### 3. Post for real

Choose the mode (see the table below):

```bash
# Grouped (default): one PR review bundling all comments
scripts/post_pr_comments.py --pr <N> --json <path> --event COMMENT

# Individual: one separate inline comment per finding
scripts/post_pr_comments.py --pr <N> --json <path> --mode individual
```

### 4. Report the result

Report back the created review/comment URLs and the list of any skipped findings so the
user can reconcile skipped items.

### Choosing the mode

| Mode | Endpoint | Use when |
|------|----------|----------|
| `grouped` (default) | `POST /pulls/{n}/reviews` | Publishing a set of findings as one review. One notification; can set `--event APPROVE \| REQUEST_CHANGES \| COMMENT`. |
| `individual` | `POST /pulls/{n}/comments` | Adding standalone comments incrementally, or when each finding should be its own thread/notification. |

Default to `grouped` with `--event COMMENT` unless the user wants a verdict or separate threads.

### Options reference

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

## Examples

### Grouped review — dry-run then post with a verdict

**Input** (`findings.json`):

```json
[
  {
    "file": "libs/shared/procedure-dto/src/lib/status-update.dto.ts",
    "line": 148,
    "summary": "Keeping email required while adding skip_email returns 400 from the controller.",
    "failure_scenario": "Client POSTs without email; the request is rejected with 400 before reaching the service."
  },
  {
    "file": "libs/server/procedure-feature/src/lib/services/procedure-data.service.ts",
    "line": 1770,
    "body": "sanifiedSize(0) returns undefined because of `if (!size) return undefined;`."
  }
]
```

**Run**:

```bash
scripts/post_pr_comments.py --pr 203 --json findings.json --dry-run
scripts/post_pr_comments.py --pr 203 --json findings.json --event REQUEST_CHANGES --review-body "Two blocking issues found"
```

**Output**:

```
Postable: 2 | Skipped: 0
Review created: https://github.com/OWNER/REPO/pull/203#pullrequestreview-123
```

Each finding becomes a comment anchored to its file and line in the PR diff.

### Multi-line range comment

**Input** (single item):

```json
[
  {
    "file": "src/api/route.ts",
    "line": 40,
    "start_line": 35,
    "summary": "Extract this branch into a dedicated handler.",
    "side": "RIGHT"
  }
]
```

**Run**:

```bash
scripts/post_pr_comments.py --pr 203 --json range.json --mode individual
```

**Output**:

```
Postable: 1 | Skipped: 0
Comment created: https://github.com/OWNER/REPO/pull/203#discussion_r-456
```

The comment spans lines 35–40 (`start_line` is the first line of the range).

## Best Practices

- **Always `--dry-run` first** on an unfamiliar PR — stale line numbers are the most common
  failure, and the dry-run surfaces them as "skipped" without side effects.
- **Reconcile skipped lines** with the user before posting: skipped findings usually mean
  the JSON line numbers are stale relative to the PR head.
- **Prefer `grouped` with `--event COMMENT`** unless the user explicitly wants a verdict or
  per-thread notifications.
- **Use the bundled script**, not hand-rolled `gh api` calls — it handles diff validation,
  repo/commit detection, and body assembly consistently.
- **Keep messages actionable**: a short `summary` headline plus a `failure_scenario` that
  explains the trigger and impact reads best in a diff thread.

## Constraints and Warnings

- **Only diff lines are commentable.** GitHub only accepts an inline comment if the target
  line is part of the PR's diff. `line` is the line number in the **new** file (use
  `side: "LEFT"` for removed lines). There is no way to attach a line comment to an
  unchanged, undiffed line.
- **Skipped items can appear silently** if a finding's line falls outside a diff hunk. The
  script always reports them at the end, but you must reconcile stale line numbers before
  a real post.
- **Multi-line comments need explicit range fields**: include `start_line` (and optional
  `start_side`) alongside `line` or the request is treated as a single-line comment.
- **Grouped reviews carry a verdict**: `--event APPROVE` or `REQUEST_CHANGES` signals a
  decision, not just a comment — use `COMMENT` when you only want to share findings.