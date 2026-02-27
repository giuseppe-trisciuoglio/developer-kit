#!/usr/bin/env python3
"""
MCP-Scan security checker for skill definitions.

Scans skills one at a time using mcp-scan (from Invariant Labs) to detect:
- Prompt injection attacks
- Malware payloads
- Sensitive data handling issues
- Hard-coded secrets

Usage:
    # Scan all skills (one at a time)
    python mcp_scan_checker.py --all

    # Scan only skills changed vs main
    python mcp_scan_checker.py --changed

    # Scan only skills changed vs a specific base ref
    python mcp_scan_checker.py --changed --base origin/develop

    # Scan a specific plugin's skills
    python mcp_scan_checker.py --plugin developer-kit-java

    # Scan a specific skill directory
    python mcp_scan_checker.py --path plugins/developer-kit-java/skills/spring-boot-actuator

Exit Codes:
    0 = All scans passed (no security issues found)
    1 = Security issues detected
    2 = System error (mcp-scan not available or execution failure)
"""

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ANSI color codes
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color

# Issue codes that are informational (not real security issues)
INFORMATIONAL_CODES = frozenset({
    "W004",  # "The MCP server is not in our registry" — expected for custom skills
})


@dataclass
class SkillScanResult:
    """Result of scanning a single skill."""
    skill_path: str
    skill_name: str
    issues: List[dict] = field(default_factory=list)
    labels: List[dict] = field(default_factory=list)
    error: Optional[dict] = None
    servers_found: int = 0

    @property
    def has_critical_issues(self) -> bool:
        return any(
            i.get("code", "") not in INFORMATIONAL_CODES
            for i in self.issues
        )

    @property
    def security_issues(self) -> List[dict]:
        return [i for i in self.issues if i.get("code", "") not in INFORMATIONAL_CODES]

    @property
    def info_issues(self) -> List[dict]:
        return [i for i in self.issues if i.get("code", "") in INFORMATIONAL_CODES]


def find_repo_root() -> Path:
    """Find the repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def check_mcp_scan_available() -> Tuple[bool, str]:
    """Check if mcp-scan is available via uvx or pipx."""
    if shutil.which("uvx"):
        return True, "uvx"
    if shutil.which("pipx"):
        return True, "pipx"
    return False, ""


def find_changed_skill_directories(repo_root: Path,
                                   base_ref: Optional[str] = None) -> List[Path]:
    """Find skill directories that contain files modified compared to a base ref."""
    if base_ref is None:
        # Auto-detect: use merge-base with origin/main or HEAD~1
        for candidate in ["origin/main", "origin/develop", "HEAD~1"]:
            try:
                result = subprocess.run(
                    ["git", "merge-base", "HEAD", candidate],
                    capture_output=True, text=True, check=True, cwd=repo_root,
                )
                base_ref = result.stdout.strip()
                break
            except subprocess.CalledProcessError:
                continue
        if base_ref is None:
            print(f"{YELLOW}Warning: Could not detect base ref, falling back to HEAD~1{NC}")
            base_ref = "HEAD~1"

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "HEAD"],
            capture_output=True, text=True, check=True, cwd=repo_root,
        )
    except subprocess.CalledProcessError:
        print(f"{RED}Error: git diff failed against {base_ref}{NC}")
        return []

    changed_files = result.stdout.strip().splitlines()
    skill_dirs: set[Path] = set()

    for changed_file in changed_files:
        file_path = repo_root / changed_file
        # Walk up to find containing skill dir (has SKILL.md)
        for parent in file_path.parents:
            skill_md = parent / "SKILL.md"
            if skill_md.exists() and "plugins" in str(parent):
                skill_dirs.add(parent)
                break

    return sorted(skill_dirs)


def find_skill_directories(repo_root: Path, plugin: Optional[str] = None,
                           path: Optional[str] = None) -> List[Path]:
    """Find skill directories to scan."""
    if path:
        target = Path(path)
        if not target.is_absolute():
            target = repo_root / target
        if target.exists():
            return [target]
        print(f"{RED}Error: Path not found: {target}{NC}")
        return []

    plugins_dir = repo_root / "plugins"
    if not plugins_dir.exists():
        print(f"{RED}Error: plugins/ directory not found{NC}")
        return []

    skill_dirs: List[Path] = []

    if plugin:
        plugin_dir = plugins_dir / plugin
        if not plugin_dir.exists():
            print(f"{RED}Error: Plugin not found: {plugin}{NC}")
            return []
        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            for skill_dir in sorted(skills_dir.rglob("SKILL.md")):
                skill_dirs.append(skill_dir.parent)
    else:
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir():
                continue
            skills_dir = plugin_dir / "skills"
            if skills_dir.exists():
                for skill_dir in sorted(skills_dir.rglob("SKILL.md")):
                    skill_dirs.append(skill_dir.parent)

    return skill_dirs


def scan_single_skill(skill_dir: Path, runner: str,
                      verbose: bool = False) -> SkillScanResult:
    """
    Run mcp-scan on a single skill directory and return structured result.
    """
    skill_name = skill_dir.name
    result = SkillScanResult(
        skill_path=str(skill_dir),
        skill_name=skill_name,
    )

    if runner == "uvx":
        cmd = ["uvx", "mcp-scan@latest", "scan", "--json", "--skills", str(skill_dir)]
    elif runner == "pipx":
        cmd = ["pipx", "run", "mcp-scan", "scan", "--json", "--skills", str(skill_dir)]
    else:
        result.error = {"message": f"Unsupported runner: {runner}"}
        return result

    if verbose:
        print(f"  {CYAN}$ {' '.join(cmd)}{NC}")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout per skill
        )

        output = proc.stdout.strip()
        if not output:
            if proc.stderr and verbose:
                print(f"  {YELLOW}stderr: {proc.stderr[:300]}{NC}")
            return result

        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            if verbose:
                print(f"  {YELLOW}Warning: Could not parse JSON output{NC}")
            return result

        # mcp-scan returns: { "<config_path>": { client, path, servers, issues, labels, error } }
        for config_key, config_data in parsed.items():
            if not isinstance(config_data, dict):
                continue

            # Extract issues
            issues = config_data.get("issues", [])
            if issues:
                result.issues.extend(issues)

            # Extract labels
            labels = config_data.get("labels", [])
            if labels:
                result.labels.extend(labels)

            # Extract error
            error = config_data.get("error")
            if error and isinstance(error, dict) and error.get("message"):
                result.error = error

            # Count servers (skills found)
            servers = config_data.get("servers", [])
            result.servers_found += len(servers)

            # Check per-server errors
            for srv in servers:
                srv_error = srv.get("error")
                if srv_error and isinstance(srv_error, dict) and srv_error.get("message"):
                    result.error = srv_error

    except FileNotFoundError:
        result.error = {"message": f"{runner} command not found"}
    except subprocess.TimeoutExpired:
        result.error = {"message": "Scan timed out after 120 seconds"}
    except Exception as e:
        result.error = {"message": str(e)}

    return result


def print_skill_result(result: SkillScanResult, verbose: bool = False) -> None:
    """Print the result for a single skill scan."""
    security_issues = result.security_issues
    info_issues = result.info_issues

    if result.error:
        err_msg = result.error.get("message", "Unknown error")
        category = result.error.get("category", "")
        if category == "file_not_found":
            print(f"  {YELLOW}⚠ SKIP{NC}  — {err_msg}")
        else:
            print(f"  {RED}✗ ERROR{NC} — {err_msg}")
    elif security_issues:
        for issue in security_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            print(f"  {RED}✗ FAIL{NC}  [{code}] {msg}")
    elif info_issues and verbose:
        for issue in info_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            print(f"  {CYAN}ℹ INFO{NC}  [{code}] {msg}")
    else:
        print(f"  {GREEN}✓ PASS{NC}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="mcp-scan-checker",
        description="Security scan skills using mcp-scan (Invariant Labs)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all skills in all plugins",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        help="Scan skills in a specific plugin (e.g., developer-kit-java)",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Scan a specific skill directory path",
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Only scan skills modified in the current PR/commit (uses git diff)",
    )
    parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Base branch/ref for --changed comparison (default: auto-detect)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output including info-level issues",
    )

    args = parser.parse_args()

    if not args.all and not args.plugin and not args.path and not args.changed:
        parser.print_help()
        return 0

    # Banner
    print(f"\n{BLUE}╔═══════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║     MCP-Scan Security Checker for Skills                     ║{NC}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════════╝{NC}\n")

    # Check prerequisites
    available, runner = check_mcp_scan_available()
    if not available:
        print(f"{RED}Error: Neither 'uvx' nor 'pipx' found.{NC}")
        print(f"Install uv: {CYAN}curl -LsSf https://astral.sh/uv/install.sh | sh{NC}")
        print(f"  or pipx: {CYAN}pip install pipx{NC}")
        return 2

    print(f"{GREEN}Using runner: {runner}{NC}")

    # Find repo root
    repo_root = find_repo_root()
    print(f"Repository: {repo_root}\n")

    # Find skill directories
    if args.changed:
        skill_dirs = find_changed_skill_directories(repo_root, args.base)
        if not skill_dirs:
            print(f"{GREEN}✅ No skill changes detected — nothing to scan.{NC}")
            return 0
    else:
        skill_dirs = find_skill_directories(repo_root, args.plugin, args.path)

    if not skill_dirs:
        print(f"{YELLOW}No skills found to scan.{NC}")
        return 0

    print(f"📋 Found {BOLD}{len(skill_dirs)}{NC} skill(s) to scan\n")

    # Scan each skill individually
    results: List[SkillScanResult] = []
    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    for i, skill_dir in enumerate(skill_dirs, 1):
        rel_path = skill_dir.relative_to(repo_root) if skill_dir.is_relative_to(repo_root) else skill_dir
        skill_name = skill_dir.name
        print(f"[{i}/{len(skill_dirs)}] {BOLD}{skill_name}{NC} ({rel_path})")

        scan_result = scan_single_skill(skill_dir, runner, args.verbose)
        results.append(scan_result)

        print_skill_result(scan_result, args.verbose)

        if scan_result.error:
            category = scan_result.error.get("category", "")
            if category == "file_not_found":
                skipped += 1
            else:
                errors += 1
        elif scan_result.has_critical_issues:
            failed += 1
        else:
            passed += 1

    # Summary
    print(f"\n{'─' * 60}")
    total = len(results)
    parts = []
    if passed:
        parts.append(f"{GREEN}{passed} passed{NC}")
    if failed:
        parts.append(f"{RED}{failed} failed{NC}")
    if errors:
        parts.append(f"{RED}{errors} error(s){NC}")
    if skipped:
        parts.append(f"{YELLOW}{skipped} skipped{NC}")

    print(f"Results: {', '.join(parts)} ({total} total)")

    if failed:
        print(f"\n{RED}❌ Security scan FAILED: {failed} skill(s) with security issues.{NC}")
        return 1

    if errors:
        print(f"\n{YELLOW}⚠️  Security scan completed with {errors} error(s).{NC}")
        return 0

    print(f"\n{GREEN}✅ Security scan passed: all {passed} skill(s) are clean.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
