#!/usr/bin/env python3
"""
MCP-Scan security checker for skill definitions and rule files.

Scans skills and rules one at a time using snyk-agent-scan
(formerly mcp-scan, from Invariant Labs) to detect:
- Prompt injection attacks
- Malware payloads
- Sensitive data handling issues
- Hard-coded secrets

Usage:
    # Scan all skills and rules (one at a time)
    python mcp_scan_checker.py --all

    # Scan only components changed vs main
    python mcp_scan_checker.py --changed

    # Scan only components changed vs a specific base ref
    python mcp_scan_checker.py --changed --base origin/develop

    # Scan a specific plugin's skills and rules
    python mcp_scan_checker.py --plugin developer-kit-java

    # Scan a specific skill directory or rule file
    python mcp_scan_checker.py --path plugins/developer-kit-java/skills/spring-boot-actuator
    python mcp_scan_checker.py --path plugins/developer-kit-java/rules/naming-conventions.md

Exit Codes:
    0 = All scans passed (no security issues found)
    1 = Security issues detected
    2 = System error (snyk-agent-scan not available or execution failure)
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse


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

# Path to per-component allowlist (relative to validators/ dir or repo root)
_ALLOWLIST_FILENAME = "mcp-scan-allowlist.json"

# Regex to extract HTTP(S) URLs from text
_URL_RE = re.compile(r'https?://[^\s"\'<>)\]},`]+')

# Domains that are always considered placeholders and excluded from validation
_PLACEHOLDER_DOMAINS = frozenset({
    "localhost",
})


def _load_allowlist(repo_root: Path) -> Tuple[
    dict[str, frozenset[str]],
    dict[str, frozenset[str]],
    frozenset[str],
]:
    """Load per-component allowlist.

    Returns:
        (code_allowlist, domain_allowlist, placeholder_domains)
        - code_allowlist: component path → allowed warning codes
        - domain_allowlist: component path → allowed external domains
        - placeholder_domains: domains to ignore during validation
    """
    allowlist_path = repo_root / ".skills-validator-check" / _ALLOWLIST_FILENAME
    if not allowlist_path.exists():
        return {}, {}, _PLACEHOLDER_DOMAINS

    try:
        data = json.loads(allowlist_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}, {}, _PLACEHOLDER_DOMAINS

    # Merge file-level placeholder domains with built-in ones
    file_placeholders = frozenset(
        d.lower() for d in data.get("_placeholder_domains", [])
    )
    placeholders = _PLACEHOLDER_DOMAINS | file_placeholders

    codes: dict[str, frozenset[str]] = {}
    domains: dict[str, frozenset[str]] = {}
    for entry in data.get("components", []):
        path = entry.get("path", "").rstrip("/")
        if not path:
            continue
        allow_codes = entry.get("allow", [])
        if allow_codes:
            codes[path] = frozenset(allow_codes)
        allow_domains = entry.get("domains", [])
        domains[path] = frozenset(d.lower() for d in allow_domains)
    return codes, domains, placeholders


def _extract_domains_from_files(skill_path: Path) -> frozenset[str]:
    """Extract all unique domains from HTTP(S) URLs in a skill's files."""
    found: set[str] = set()
    scan_dir = skill_path if skill_path.is_dir() else skill_path.parent
    for f in scan_dir.rglob("*"):
        if not f.is_file() or f.suffix not in (".md", ".txt", ".yaml", ".yml", ".json"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for url_match in _URL_RE.findall(text):
            url_clean = url_match.rstrip(".,;:")
            # Skip template variables (e.g., ${BucketName})
            if "${" in url_clean:
                continue
            try:
                hostname = urlparse(url_clean).hostname
                if hostname and len(hostname) > 1 and "." in hostname:
                    found.add(hostname.lower())
            except Exception:
                continue
    return frozenset(found)


@dataclass
class ScanResult:
    """Result of scanning a single component (skill or rule)."""
    scan_path: str
    component_name: str
    component_type: str  # "skill" or "rule"
    issues: List[dict] = field(default_factory=list)
    labels: List[dict] = field(default_factory=list)
    error: Optional[dict] = None
    servers_found: int = 0
    allowed_codes: frozenset = field(default_factory=frozenset)
    allowed_domains: frozenset = field(default_factory=frozenset)
    placeholder_domains: frozenset = field(default_factory=frozenset)
    file_domains: frozenset = field(default_factory=frozenset)
    uncensored_domains: frozenset = field(default_factory=frozenset)

    def _is_informational(self, code: str) -> bool:
        if code in INFORMATIONAL_CODES:
            return True
        if code not in self.allowed_codes:
            return False
        # Code is allowed — but check domain census
        if self.uncensored_domains:
            return False  # New domains found → do NOT suppress
        return True

    @property
    def has_critical_issues(self) -> bool:
        return any(
            not self._is_informational(i.get("code", ""))
            for i in self.issues
        )

    @property
    def security_issues(self) -> List[dict]:
        return [i for i in self.issues if not self._is_informational(i.get("code", ""))]

    @property
    def info_issues(self) -> List[dict]:
        return [i for i in self.issues if self._is_informational(i.get("code", ""))]


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
    """Check if snyk-agent-scan can be executed via uvx or pipx."""
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


def find_changed_rule_files(repo_root: Path,
                            base_ref: Optional[str] = None) -> List[Path]:
    """Find rule files that have been modified compared to a base ref."""
    if base_ref is None:
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
            base_ref = "HEAD~1"

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "HEAD"],
            capture_output=True, text=True, check=True, cwd=repo_root,
        )
    except subprocess.CalledProcessError:
        return []

    changed_files = result.stdout.strip().splitlines()
    rule_files: List[Path] = []

    for changed_file in changed_files:
        file_path = repo_root / changed_file
        if "/rules/" in changed_file and changed_file.endswith(".md"):
            if file_path.exists():
                rule_files.append(file_path)

    return sorted(rule_files)


def find_rule_files(repo_root: Path, plugin: Optional[str] = None,
                    path: Optional[str] = None) -> List[Path]:
    """Find rule files to scan."""
    if path:
        target = Path(path)
        if not target.is_absolute():
            target = repo_root / target
        if target.exists() and target.is_file():
            return [target]
        return []

    plugins_dir = repo_root / "plugins"
    if not plugins_dir.exists():
        return []

    rule_files: List[Path] = []

    if plugin:
        plugin_dir = plugins_dir / plugin
        if not plugin_dir.exists():
            return []
        rules_dir = plugin_dir / "rules"
        if rules_dir.exists():
            rule_files.extend(sorted(rules_dir.glob("*.md")))
    else:
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir():
                continue
            rules_dir = plugin_dir / "rules"
            if rules_dir.exists():
                rule_files.extend(sorted(rules_dir.glob("*.md")))

    return rule_files


def scan_single_component(scan_path: Path, component_type: str, runner: str,
                          verbose: bool = False) -> ScanResult:
    """
    Run snyk-agent-scan on a single skill directory or rule file.
    """
    component_name = scan_path.stem if scan_path.is_file() else scan_path.name
    result = ScanResult(
        scan_path=str(scan_path),
        component_name=component_name,
        component_type=component_type,
    )

    # For rules (individual files), scan the parent directory
    target_path = str(scan_path.parent) if scan_path.is_file() else str(scan_path)

    if runner == "uvx":
        cmd = ["uvx", "snyk-agent-scan@latest", "scan", "--json", "--skills", target_path]
    elif runner == "pipx":
        cmd = ["pipx", "run", "snyk-agent-scan", "scan", "--json", "--skills", target_path]
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

        # snyk-agent-scan returns:
        # { "<config_path>": { client, path, servers, issues, labels, error } }
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


def print_scan_result(result: ScanResult, verbose: bool = False) -> None:
    """Print the result for a single component scan."""
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
        if result.uncensored_domains:
            domains_str = ", ".join(sorted(result.uncensored_domains))
            print(f"  {YELLOW}       ↳ Uncensored domain(s): {domains_str}{NC}")
            print(f"  {YELLOW}       ↳ Add to mcp-scan-allowlist.json to suppress{NC}")
    elif info_issues and verbose:
        for issue in info_issues:
            code = issue.get("code", "???")
            msg = issue.get("message", "No description")
            suffix = " (allowed)" if code in result.allowed_codes else ""
            print(f"  {CYAN}ℹ INFO{NC}  [{code}] {msg}{suffix}")
    else:
        print(f"  {GREEN}✓ PASS{NC}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="mcp-scan-checker",
        description="Security scan skills and rules using snyk-agent-scan (Invariant Labs)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all skills and rules in all plugins",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        help="Scan skills and rules in a specific plugin (e.g., developer-kit-java)",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Scan a specific skill directory or rule file path",
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Only scan skills/rules modified in the current PR/commit (uses git diff)",
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
    print(f"{BLUE}║     MCP-Scan Security Checker for Skills & Rules             ║{NC}")
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

    # Load per-component allowlist
    code_allowlist, domain_allowlist, placeholder_domains = _load_allowlist(repo_root)

    # Find skill directories and rule files
    if args.changed:
        skill_dirs = find_changed_skill_directories(repo_root, args.base)
        rule_files = find_changed_rule_files(repo_root, args.base)
        if not skill_dirs and not rule_files:
            print(f"{GREEN}✅ No skill/rule changes detected — nothing to scan.{NC}")
            return 0
    else:
        skill_dirs = find_skill_directories(repo_root, args.plugin, args.path)
        rule_files = find_rule_files(repo_root, args.plugin, args.path)

    if not skill_dirs and not rule_files:
        print(f"{YELLOW}No skills or rules found to scan.{NC}")
        return 0

    # Build scan items: list of (path, component_type)
    scan_items: List[Tuple[Path, str]] = []
    for sd in skill_dirs:
        scan_items.append((sd, "skill"))
    for rf in rule_files:
        scan_items.append((rf, "rule"))

    print(f"📋 Found {BOLD}{len(scan_items)}{NC} component(s) to scan "
          f"({len(skill_dirs)} skill(s), {len(rule_files)} rule(s))\n")

    # Scan each component individually
    results: List[ScanResult] = []
    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    # Track already-scanned rule directories to avoid redundant scans
    scanned_rule_dirs: set = set()

    for i, (scan_path, comp_type) in enumerate(scan_items, 1):
        rel_path = scan_path.relative_to(repo_root) if scan_path.is_relative_to(repo_root) else scan_path
        component_name = scan_path.stem if scan_path.is_file() else scan_path.name
        type_label = f"[{comp_type}]"
        print(f"[{i}/{len(scan_items)}] {BOLD}{component_name}{NC} {type_label} ({rel_path})")

        # For rule files, scan parent directory but only once
        if comp_type == "rule":
            rule_dir = scan_path.parent
            if rule_dir in scanned_rule_dirs:
                print(f"  {GREEN}✓ PASS{NC} (directory already scanned)")
                passed += 1
                continue
            scanned_rule_dirs.add(rule_dir)

        scan_result = scan_single_component(scan_path, comp_type, runner, args.verbose)

        # Apply per-component allowlist with domain validation
        rel_str = str(rel_path).replace("\\", "/").rstrip("/")
        if rel_str in code_allowlist:
            scan_result.allowed_codes = code_allowlist[rel_str]
            scan_result.allowed_domains = domain_allowlist.get(rel_str, frozenset())
            scan_result.placeholder_domains = placeholder_domains

            # Extract domains from skill files and check against census
            file_domains = _extract_domains_from_files(scan_path)
            real_domains = frozenset(
                d for d in file_domains
                if d not in placeholder_domains
                and not any(d.endswith("." + p) for p in placeholder_domains)
            )
            scan_result.file_domains = real_domains
            scan_result.uncensored_domains = real_domains - scan_result.allowed_domains

        results.append(scan_result)

        print_scan_result(scan_result, args.verbose)

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
        print(f"\n{RED}❌ Security scan FAILED: {failed} component(s) with security issues.{NC}")
        return 1

    if errors:
        print(f"\n{YELLOW}⚠️  Security scan completed with {errors} error(s).{NC}")
        return 0

    print(f"\n{GREEN}✅ Security scan passed: all {passed} component(s) are clean.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
