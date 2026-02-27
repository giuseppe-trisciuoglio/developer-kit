#!/usr/bin/env python3
"""
MCP-Scan security checker for skill definitions.

Scans skills using mcp-scan (from Invariant Labs) to detect:
- Prompt injection attacks
- Malware payloads
- Sensitive data handling issues
- Hard-coded secrets

Usage:
    # Scan all skills
    python mcp_scan_checker.py --all

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
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# ANSI color codes
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color


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
    """Check if mcp-scan is available via uvx or npx."""
    # Check for uvx (preferred)
    if shutil.which("uvx"):
        return True, "uvx"

    # Check for pipx
    if shutil.which("pipx"):
        return True, "pipx"

    return False, ""


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


def run_mcp_scan(skill_dirs: List[Path], runner: str,
                 verbose: bool = False) -> Tuple[int, List[dict]]:
    """
    Run mcp-scan on the given skill directories.

    Returns:
        Tuple of (exit_code, findings_list)
    """
    if not skill_dirs:
        print(f"{YELLOW}No skill directories found to scan.{NC}")
        return 0, []

    # Build the command
    paths_str = " ".join(str(d) for d in skill_dirs)

    if runner == "uvx":
        cmd = ["uvx", "mcp-scan@latest", "scan", "--json", "--skills"]
    elif runner == "pipx":
        cmd = ["pipx", "run", "mcp-scan", "scan", "--json", "--skills"]
    else:
        print(f"{RED}Error: No supported runner found.{NC}")
        return 2, []

    # Add skill paths as positional arguments
    cmd.extend([str(d) for d in skill_dirs])

    if verbose:
        print(f"{CYAN}Running: {' '.join(cmd)}{NC}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        findings: List[dict] = []

        # Try to parse JSON output
        output = result.stdout.strip()
        if output:
            try:
                parsed = json.loads(output)
                if isinstance(parsed, list):
                    findings = parsed
                elif isinstance(parsed, dict):
                    findings = parsed.get("findings", [parsed])
            except json.JSONDecodeError:
                # If JSON parsing fails, treat output as text
                if verbose:
                    print(f"{YELLOW}Warning: Could not parse JSON output{NC}")
                    print(f"stdout: {result.stdout[:500]}")

        # Also capture stderr for error messages
        if result.stderr and verbose:
            print(f"{YELLOW}stderr: {result.stderr[:500]}{NC}")

        return result.returncode, findings

    except FileNotFoundError:
        print(f"{RED}Error: {runner} command not found.{NC}")
        print(f"Install with: pip install uv  (for uvx)")
        return 2, []
    except subprocess.TimeoutExpired:
        print(f"{RED}Error: mcp-scan timed out after 300 seconds.{NC}")
        return 2, []
    except Exception as e:
        print(f"{RED}Error running mcp-scan: {e}{NC}")
        return 2, []


def format_findings(findings: List[dict], verbose: bool = False) -> str:
    """Format scan findings into a readable report."""
    if not findings:
        return f"{GREEN}✅ No security issues found.{NC}"

    lines = []
    critical_count = 0
    warning_count = 0

    for finding in findings:
        severity = finding.get("severity", "unknown").upper()
        message = finding.get("message", finding.get("description", "No description"))
        file_path = finding.get("file", finding.get("path", "unknown"))
        category = finding.get("category", finding.get("type", "general"))

        if severity in ("CRITICAL", "HIGH", "ERROR"):
            color = RED
            critical_count += 1
            icon = "❌"
        elif severity in ("MEDIUM", "WARNING"):
            color = YELLOW
            warning_count += 1
            icon = "⚠️"
        else:
            color = CYAN
            warning_count += 1
            icon = "ℹ️"

        lines.append(f"  {icon} {color}[{severity}]{NC} {message}")
        lines.append(f"     File: {file_path}")
        if category:
            lines.append(f"     Category: {category}")
        lines.append("")

    # Summary
    summary_parts = []
    if critical_count:
        summary_parts.append(f"{RED}{critical_count} critical{NC}")
    if warning_count:
        summary_parts.append(f"{YELLOW}{warning_count} warning(s){NC}")

    header = f"\n{RED}🔐 Security findings: {', '.join(summary_parts)}{NC}\n"
    return header + "\n".join(lines)


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
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output",
    )

    args = parser.parse_args()

    if not args.all and not args.plugin and not args.path:
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
    skill_dirs = find_skill_directories(repo_root, args.plugin, args.path)

    if not skill_dirs:
        print(f"{YELLOW}No skills found to scan.{NC}")
        return 0

    print(f"📋 Found {len(skill_dirs)} skill(s) to scan:")
    for d in skill_dirs:
        rel_path = d.relative_to(repo_root) if d.is_relative_to(repo_root) else d
        print(f"   - {rel_path}")
    print()

    # Run mcp-scan
    print(f"🔍 Running mcp-scan...\n")
    exit_code, findings = run_mcp_scan(skill_dirs, runner, args.verbose)

    if exit_code == 2:
        return 2

    # Format and display results
    report = format_findings(findings, args.verbose)
    print(report)

    # Determine final status
    has_critical = any(
        f.get("severity", "").upper() in ("CRITICAL", "HIGH", "ERROR")
        for f in findings
    )

    if has_critical:
        print(f"\n{RED}❌ Security scan FAILED: critical issues found.{NC}")
        return 1

    if findings:
        print(f"\n{YELLOW}⚠️  Security scan passed with warnings.{NC}")
        return 0

    print(f"\n{GREEN}✅ Security scan passed: all skills are clean.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
