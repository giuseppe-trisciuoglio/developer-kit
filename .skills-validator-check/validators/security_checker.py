#!/usr/bin/env python3
"""
Gen Agent Trust Hub security checker for CI/CD pipelines.

Detects SKILL.md files changed in the current PR and validates them
against the Gen Agent Trust Hub API.

CI-only: not integrated into pre-commit hooks.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

TRUST_HUB_API_URL = "https://ai.gendigital.com/api/scan/lookup"
RAW_GITHUB_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/{repo}/refs/heads/{branch}/{path}"
)


def get_changed_skill_files(base_ref: str) -> list[str]:
    """Return SKILL.md files changed between the PR branch and the base branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"⚠️  Warning: git diff failed: {exc.stderr.strip()}")
        return []

    changed_files = result.stdout.strip().splitlines()
    return [f for f in changed_files if f.endswith("SKILL.md")]


def build_raw_url(repo: str, branch: str, path: str) -> str:
    """Build a raw GitHub content URL for the given file path."""
    return RAW_GITHUB_URL_TEMPLATE.format(repo=repo, branch=branch, path=path)


def check_skill(skill_url: str) -> dict:
    """Call the Trust Hub API for a single skill URL and return the response."""
    payload = json.dumps({"skillUrl": skill_url}).encode("utf-8")
    req = urllib.request.Request(
        TRUST_HUB_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        print(f"⚠️  Warning: Trust Hub API error for {skill_url}: {exc}")
        return {}


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    branch = os.environ.get("GITHUB_HEAD_REF", "")
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")

    if not repo or not branch:
        print("⚠️  Warning: GITHUB_REPOSITORY or GITHUB_HEAD_REF not set. Skipping.")
        return 0

    print(f"🔍 Detecting changed SKILL.md files (base: {base_ref})...")
    changed_skills = get_changed_skill_files(base_ref)

    if not changed_skills:
        print("✅ No SKILL.md files changed in this PR. Nothing to check.")
        return 0

    print(f"📋 Found {len(changed_skills)} changed skill(s):")
    for skill_path in changed_skills:
        print(f"   - {skill_path}")

    has_unsafe = False

    for skill_path in changed_skills:
        skill_url = build_raw_url(repo, branch, skill_path)
        print(f"\n🔐 Checking: {skill_path}")
        print(f"   URL: {skill_url}")

        result = check_skill(skill_url)

        if not result:
            # API error — non-blocking
            print("   ⚠️  Could not get a result from Trust Hub (non-blocking).")
            continue

        status = result.get("status", "unknown")
        print(f"   Status: {status}")

        if status == "unsafe":
            has_unsafe = True
            reason = result.get("reason", "No reason provided")
            print(f"   ❌ UNSAFE — {reason}")
        elif status == "safe":
            print("   ✅ Safe")
        else:
            # Unknown status — treat as non-blocking warning
            print(f"   ⚠️  Unexpected status '{status}' (non-blocking).")

    print()
    if has_unsafe:
        print("❌ Security check FAILED: one or more skills were flagged as unsafe.")
        return 1

    print("✅ Security check passed: all skills are safe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
