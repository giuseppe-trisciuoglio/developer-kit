#!/usr/bin/env python3
"""Post review comments from a JSON file as inline comments on a GitHub PR.

Reads a JSON array of comment objects and posts each one against the file/line
it references, using the GitHub API via the authenticated `gh` CLI.

Comment JSON schema (per item):
  {
    "file": "path/relative/to/repo/root.ts",   # required
    "line": 148,                                  # required (line in the NEW file)
    "summary": "short headline",                  # optional
    "failure_scenario": "longer explanation",     # optional
    "body": "...",                                # optional, overrides summary+scenario
    "side": "RIGHT",                              # optional, default RIGHT (LEFT = removed)
    "start_line": 140                             # optional, for multi-line ranges
  }
At least one of body / summary / failure_scenario must be present.

Only lines that appear in the PR diff can receive an inline comment. Comments
whose target line is not part of the diff are SKIPPED and listed in a report.

Usage:
  post_pr_comments.py --pr 42 --json comments.json [options]

Options:
  --pr N                PR number (required)
  --json PATH           Path to the JSON file of comments (required)
  --repo OWNER/REPO     Repo slug (default: auto-detected from `gh repo view`)
  --mode grouped|individual   grouped = one review with all comments (default);
                              individual = one inline comment per item
  --event COMMENT|APPROVE|REQUEST_CHANGES   Review event for grouped mode (default COMMENT)
  --review-body TEXT    Top-level body for the grouped review (optional)
  --commit SHA          Commit to attach comments to (default: PR head SHA)
  --dry-run             Validate and print what would be posted, post nothing
"""
import argparse
import json
import re
import subprocess
import sys


def gh_api(path, method="GET", fields=None, input_json=None):
    """Call `gh api`. Returns parsed JSON (or None). Raises on failure."""
    cmd = ["gh", "api", "-H", "Accept: application/vnd.github+json"]
    if method != "GET":
        cmd += ["-X", method]
    for key, val in (fields or {}).items():
        cmd += ["-f", f"{key}={val}"]
    if input_json is not None:
        cmd += ["--input", "-"]
    proc = subprocess.run(
        cmd + [path],
        input=json.dumps(input_json) if input_json is not None else None,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"gh api {path} failed:\n{proc.stderr.strip()}")
    out = proc.stdout.strip()
    return json.loads(out) if out else None


def detect_repo():
    proc = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Could not detect repo: {proc.stderr.strip()}")
    return proc.stdout.strip()


def get_head_sha(repo, pr):
    commits = gh_api(f"/repos/{repo}/pulls/{pr}/commits?per_page=100")
    if not commits:
        raise RuntimeError("PR has no commits")
    return commits[-1]["sha"]


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def diff_line_index(repo, pr):
    """Map each changed file to the sets of commentable line numbers.

    Returns: { path: {"RIGHT": set(new_lines), "LEFT": set(old_lines)} }
    A line is commentable if it appears in a hunk (added/removed/context).
    """
    files = gh_api(f"/repos/{repo}/pulls/{pr}/files?per_page=100")
    index = {}
    for f in files or []:
        path = f["filename"]
        patch = f.get("patch")
        right, left = set(), set()
        if not patch:  # binary or too-large file: no inline comments possible
            index[path] = {"RIGHT": right, "LEFT": left}
            continue
        new_ln = old_ln = 0
        for raw in patch.splitlines():
            m = HUNK_RE.match(raw)
            if m:
                old_ln = int(m.group(1))
                new_ln = int(m.group(3))
                continue
            if raw.startswith("+"):
                right.add(new_ln)
                new_ln += 1
            elif raw.startswith("-"):
                left.add(old_ln)
                old_ln += 1
            else:  # context line (also "\ No newline at end of file" -> harmless)
                right.add(new_ln)
                left.add(old_ln)
                new_ln += 1
                old_ln += 1
        index[path] = {"RIGHT": right, "LEFT": left}
    return index


def build_body(item):
    if item.get("body"):
        return item["body"]
    parts = []
    if item.get("summary"):
        parts.append(item["summary"])
    if item.get("failure_scenario"):
        parts.append(f"**Failure scenario:** {item['failure_scenario']}")
    return "\n\n".join(parts)


def validate(items, index):
    """Split items into postable comments and skipped ones (with reason)."""
    postable, skipped = [], []
    for item in items:
        path = item.get("file")
        line = item.get("line")
        side = item.get("side", "RIGHT").upper()
        body = build_body(item)
        if not path or line is None:
            skipped.append((item, "missing file or line"))
            continue
        if not body:
            skipped.append((item, "empty body (no summary/failure_scenario/body)"))
            continue
        if path not in index:
            skipped.append((item, "file not part of the PR diff"))
            continue
        if line not in index[path][side]:
            skipped.append((item, f"line {line} ({side}) not in the diff hunks"))
            continue
        comment = {"path": path, "line": line, "side": side, "body": body}
        if item.get("start_line") is not None:
            comment["start_line"] = item["start_line"]
            comment["start_side"] = item.get("start_side", side)
        postable.append(comment)
    return postable, skipped


def post_grouped(repo, pr, commit, comments, event, review_body, dry_run):
    payload = {"commit_id": commit, "event": event, "comments": comments}
    if review_body:
        payload["body"] = review_body
    if dry_run:
        print(json.dumps(payload, indent=2))
        return
    res = gh_api(f"/repos/{repo}/pulls/{pr}/reviews", method="POST", input_json=payload)
    print(f"✅ Created review #{res.get('id')} with {len(comments)} comment(s): {res.get('html_url','')}")


def post_individual(repo, pr, commit, comments, dry_run):
    for c in comments:
        payload = dict(c, commit_id=commit)
        if dry_run:
            print(json.dumps(payload, indent=2))
            continue
        res = gh_api(f"/repos/{repo}/pulls/{pr}/comments", method="POST", input_json=payload)
        print(f"  ✅ {c['path']}:{c['line']} -> {res.get('html_url','')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pr", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--repo")
    ap.add_argument("--mode", choices=["grouped", "individual"], default="grouped")
    ap.add_argument("--event", choices=["COMMENT", "APPROVE", "REQUEST_CHANGES"], default="COMMENT")
    ap.add_argument("--review-body", default="")
    ap.add_argument("--commit")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.json) as fh:
        items = json.load(fh)
    if not isinstance(items, list):
        sys.exit("JSON must be an array of comment objects")

    repo = args.repo or detect_repo()
    commit = args.commit or get_head_sha(repo, args.pr)
    index = diff_line_index(repo, args.pr)
    postable, skipped = validate(items, index)

    print(f"Repo: {repo}  PR: #{args.pr}  Commit: {commit[:12]}")
    print(f"Postable: {len(postable)}   Skipped: {len(skipped)}\n")

    if postable:
        if args.mode == "grouped":
            post_grouped(repo, args.pr, commit, postable, args.event, args.review_body, args.dry_run)
        else:
            post_individual(repo, args.pr, commit, postable, args.dry_run)
    else:
        print("No commentable items found.")

    if skipped:
        print(f"\n⚠️  Skipped {len(skipped)} comment(s) (line not in diff or invalid):")
        for item, reason in skipped:
            print(f"  - {item.get('file')}:{item.get('line')} — {reason}")


if __name__ == "__main__":
    main()
