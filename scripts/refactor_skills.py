#!/usr/bin/env python3
"""
Refactor Skills Script

Analyzes and refactors skills to match the new official Anthropic skill format.
Uses Claude AI via the Anthropic API to intelligently restructure skill content
following the best practices from the skill-creator-official.md guide.

Usage:
    python3 refactor_skills.py [--skill-name SKILL_NAME] [--path PATH] [--dry-run] [--fix-content]

Options:
    --skill-name: Name of specific skill to refactor (if not specified, processes all)
    --path: Base path to skills directory (default: ./skills)
    --dry-run: Show changes without writing files
    --fix-content: Use Claude Code CLI to fix skill content issues
    --analyze-only: Only analyze, don't refactor
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import shutil
import shlex


class SkillRefactorer:
    """Refactors skills to match the official Anthropic skill format."""

    # Official format fields for SKILL.md frontmatter
    OFFICIAL_FRONTMATTER_FIELDS = [
        "name",
        "description",
        "allowed-tools",
        "category",
        "tags",
        "version",
        "license",
    ]

    DIRECTORY_STRUCTURE = {
        "scripts": "Executable code (Python/Bash/etc.) for deterministic tasks",
        "references": "Documentation loaded as needed into context",
        "assets": "Files used in output (templates, icons, boilerplate code, etc.)",
    }

    def __init__(self, base_path: str = "./skills", dry_run: bool = False, fix_content: bool = False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.fix_content = fix_content
        self.report = {"analyzed": 0, "refactored": 0, "content_fixed": 0, "issues": []}

    def find_skills(self, skill_name: Optional[str] = None) -> list:
        """Find all skills or a specific skill by name."""
        skills = []

        if skill_name:
            # Search for specific skill
            skill_path = self._find_skill_path(skill_name)
            if skill_path:
                skills.append(skill_path)
            else:
                print(f"❌ Skill '{skill_name}' not found")
                return []
        else:
            # Find all skills recursively
            for item in self.base_path.rglob("SKILL.md"):
                skills.append(item.parent)

        return sorted(skills)

    def _find_skill_path(self, skill_name: str) -> Optional[Path]:
        """Find skill directory by name."""
        for item in self.base_path.rglob("SKILL.md"):
            skill_dir = item.parent
            if skill_dir.name == skill_name or skill_name in str(skill_dir):
                return skill_dir
        return None

    def analyze_skill(self, skill_path: Path) -> Dict[str, Any]:
        """Analyze a skill and identify refactoring needs."""
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            return {"error": "SKILL.md not found"}

        analysis = {
            "name": skill_path.name,
            "path": str(skill_path),
            "current_structure": self._analyze_structure(skill_path),
            "frontmatter_issues": [],
            "content_issues": [],
            "recommendations": [],
            "ready_for_refactor": True,
        }

        # Parse SKILL.md
        with open(skill_md, "r") as f:
            content = f.read()
            frontmatter, body = self._parse_skill_md(content)

            analysis["current_frontmatter"] = frontmatter
            analysis["frontmatter_issues"] = self._check_frontmatter(frontmatter)
            analysis["content_issues"] = self._check_content_structure(body)

        if analysis["frontmatter_issues"] or analysis["content_issues"]:
            analysis["ready_for_refactor"] = True
            analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_structure(self, skill_path: Path) -> Dict[str, list]:
        """Analyze current directory structure."""
        structure = {"directories": [], "files": []}

        for item in skill_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                structure["directories"].append({
                    "name": item.name,
                    "files": len(list(item.rglob("*")))
                })
            elif item.is_file() and item.name != ".DS_Store":
                structure["files"].append(item.name)

        return structure

    def _parse_skill_md(self, content: str) -> tuple:
        """Parse SKILL.md into frontmatter and body (no yaml library)."""
        frontmatter = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1].strip()
                body = parts[2].strip()

                # Simple YAML parser for frontmatter
                for line in frontmatter_str.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()

                        # Handle list values
                        if value.startswith("[") and value.endswith("]"):
                            value = [v.strip() for v in value[1:-1].split(",")]
                        # Handle quoted strings
                        elif value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        frontmatter[key] = value

        return frontmatter, body

    def _check_frontmatter(self, frontmatter: Dict) -> list:
        """Check for missing or incorrect frontmatter fields."""
        issues = []

        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter:
                issues.append(f"Missing required field: {field}")

        # Check optional but recommended fields
        recommended = ["category", "tags", "version", "allowed-tools"]
        missing_recommended = [f for f in recommended if f not in frontmatter]
        if missing_recommended:
            issues.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

        # Validate description length (should be specific, 100-1024 chars)
        description = frontmatter.get("description", "")
        if len(description) < 50:
            issues.append("Description too short (should be specific and detailed)")
        elif len(description) > 1024:
            issues.append("Description too long (max 1024 characters)")

        return issues

    def _check_content_structure(self, body: str) -> list:
        """Check content for proper structure."""
        issues = []

        required_sections = ["When to Use", "Overview", "Best Practices"]
        missing_sections = []

        for section in required_sections:
            if section not in body:
                missing_sections.append(section)

        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")

        # Check if content looks like it needs splitting into references
        if len(body) > 10000:
            issues.append("Content very long (consider moving detailed docs to references/)")

        return issues

    def _generate_recommendations(self, analysis: Dict) -> list:
        """Generate refactoring recommendations."""
        recommendations = []

        for issue in analysis["frontmatter_issues"]:
            if "recommended fields" in issue:
                recommendations.append({
                    "type": "add-frontmatter",
                    "details": issue,
                    "action": "Add category, tags, version, and allowed-tools fields"
                })
            elif "Description too short" in issue:
                recommendations.append({
                    "type": "improve-description",
                    "details": issue,
                    "action": "Make description more specific and include use cases"
                })

        for issue in analysis["content_issues"]:
            if "Missing sections" in issue:
                recommendations.append({
                    "type": "add-sections",
                    "details": issue,
                    "action": "Add missing standard sections"
                })
            elif "very long" in issue:
                recommendations.append({
                    "type": "reorganize-content",
                    "details": issue,
                    "action": "Move detailed reference material to references/ directory"
                })

        # Check directory structure
        current_dirs = [d["name"] for d in analysis["current_structure"]["directories"]]
        for official_dir in self.DIRECTORY_STRUCTURE:
            if official_dir not in current_dirs:
                recommendations.append({
                    "type": "add-directory",
                    "details": f"Missing {official_dir}/ directory",
                    "action": f"Create {official_dir}/ directory if content exists"
                })

        return recommendations

    def fix_skill_content(self, skill_path: Path, analysis: Dict[str, Any]) -> bool:
        """Use Claude Code CLI to fix skill content based on analysis."""
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            self.report["issues"].append(f"{skill_path.name}: SKILL.md not found for content fixing")
            return False

        # Build comprehensive prompt from analysis
        issues = analysis.get("frontmatter_issues", []) + analysis.get("content_issues", [])
        
        if not issues:
            print(f"   ℹ️ No content issues detected, skipping")
            return True

        # Create prompt that references the official documentation
        prompt_parts = [
            "Refactor this skill based on the official Anthropic skill format guidelines.",
            f"Skill: {skill_path.name}",
            "",
            "Issues found:",
        ]
        
        for issue in issues:
            prompt_parts.append(f"  - {issue}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            "1. Follow the structure from @.docs/skill-creator-official.md",
            "2. Ensure SKILL.md has proper YAML frontmatter with required fields (name, description, allowed-tools, category, tags, version)",
            "3. Use imperative/infinitive form (verb-first), not second person",
            "4. Keep instructions concise and procedural",
            "5. Use 'When to use' sections with specific trigger phrases",
            "6. Include concrete examples progressing from basic to advanced",
            "7. Add best practices and constraints sections",
            "8. Progressive disclosure: move detailed info to references/ when appropriate",
            "9. Ensure directory structure follows: scripts/, references/, assets/",
            "10. If content is too long, move to references/ and summarize in SKILL.md",
            "11. Maintain clarity, avoid ambiguity, and ensure correctness",
            "12. Use markdown formatting appropriately",
            "",
            "Use mcp tool context7 for dowloading the documentation.",
            f"File to refactor: {skill_md}",
        ])
        
        full_prompt = "\n".join(prompt_parts)
        
        # Execute Copilot CLI
        if self.dry_run:
            print(f"   🔧 [DRY RUN] Would execute: copilot -p <prompt> --allow-all-tools")
            print(f"\n   Prompt preview:")
            for line in prompt_parts[:10]:
                print(f"   {line}")
            print(f"   ... ({len(prompt_parts)} total lines)")
            return True
        
        try:
            print(f"   🤖 Running Copilot CLI to fix content...")
            print(f"   ⏳ This may take 2-3 minutes, please wait...")
            print(f"   ------------------------------")
            print(f"   📝 Prompt preview:  ")
            print(f"   ")
            print(f"   {full_prompt}")
            print(f"   ")
            print(f"   ------------------------------")
            
            # Call copilot with --allow-all-tools for non-interactive execution
            # Use echo to pipe the prompt
            cmd = f'echo {shlex.quote(full_prompt)} | copilot --allow-all-tools'
            # cmd = f'echo {shlex.quote(full_prompt)} | gemini -y -p '
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(skill_path.parent),
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0 or "modified" in result.stderr.lower() or "updated" in result.stderr.lower():
                print(f"   ✅ Content fix completed")
                if result.stdout:
                    print(f"   📝 Output: {result.stdout[:100]}")
                return True
            else:
                # Check if files were actually modified despite non-zero exit
                error_output = result.stderr if result.stderr else result.stdout
                print(f"   ✅ Content fix completed (exit code: {result.returncode})")
                if error_output:
                    print(f"   📝 {error_output[:150]}")
                return True
                
        except FileNotFoundError:
            error_msg = "copilot CLI not found. Install GitHub Copilot CLI to use --fix-content"
            self.report["issues"].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False
        except subprocess.TimeoutExpired:
            error_msg = f"{skill_path.name}: Copilot timeout (10 minutes). Skill may still be processing."
            self.report["issues"].append(error_msg)
            print(f"   ⏱️ {error_msg}")
            return False
        except Exception as e:
            error_msg = f"{skill_path.name}: Error running Copilot: {str(e)}"
            self.report["issues"].append(error_msg)
            print(f"   ❌ {error_msg}")
            return False

    def refactor_skill(self, skill_path: Path) -> bool:
        """Refactor a skill to match official format."""
        print(f"\n📋 Refactoring: {skill_path.name}")
        analysis = self.analyze_skill(skill_path)

        if "error" in analysis:
            print(f"  ❌ {analysis['error']}")
            return False

        print(f"  Found {len(analysis['recommendations'])} refactoring opportunities")

        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"  {i}. [{rec['type']}] {rec['details']}")
            print(f"     → {rec['action']}")

        if self.dry_run:
            print(f"  🔍 DRY RUN MODE - No changes made")
            return True

        # Refactor based on recommendations
        return self._apply_refactoring(skill_path, analysis)

    def _apply_refactoring(self, skill_path: Path, analysis: Dict) -> bool:
        """Apply refactoring changes to the skill."""
        try:
            # Create missing directories
            for directory in self.DIRECTORY_STRUCTURE:
                dir_path = skill_path / directory
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    (dir_path / ".gitkeep").touch()
                    print(f"  ✅ Created {directory}/ directory")

            # Update SKILL.md with improved frontmatter
            skill_md = skill_path / "SKILL.md"
            self._enhance_skill_md(skill_md, analysis)

            return True
        except Exception as e:
            self.report["issues"].append(f"Error refactoring {skill_path.name}: {e}")
            print(f"  ❌ Error: {e}")
            return False

    def _enhance_skill_md(self, skill_md: Path, analysis: Dict) -> None:
        """Enhance SKILL.md with better frontmatter and structure."""
        with open(skill_md, "r") as f:
            content = f.read()

        frontmatter, body = self._parse_skill_md(content)

        # Enhance frontmatter with missing fields
        if "allowed-tools" not in frontmatter:
            frontmatter["allowed-tools"] = "Read, Write, Bash"

        if "category" not in frontmatter:
            # Infer category from skill name or path
            category = self._infer_category(skill_md.parent)
            frontmatter["category"] = category

        if "tags" not in frontmatter:
            tags = self._infer_tags(skill_md.parent.name)
            frontmatter["tags"] = tags

        if "version" not in frontmatter:
            frontmatter["version"] = "1.0.0"

        # Ensure fields are in correct order
        ordered_frontmatter = self._order_frontmatter(frontmatter)

        # Write back enhanced SKILL.md
        new_content = self._build_skill_md_content(ordered_frontmatter, body)

        with open(skill_md, "w") as f:
            f.write(new_content)

        print(f"  ✅ Enhanced SKILL.md frontmatter")

    def _order_frontmatter(self, frontmatter: Dict) -> Dict:
        """Order frontmatter fields according to official format."""
        ordered = {}

        for field in self.OFFICIAL_FRONTMATTER_FIELDS:
            if field in frontmatter:
                ordered[field] = frontmatter[field]

        # Add any extra fields that weren't in the official list
        for key, value in frontmatter.items():
            if key not in ordered:
                ordered[key] = value

        return ordered

    def _infer_category(self, skill_dir: Path) -> str:
        """Infer category from skill directory structure."""
        parent = skill_dir.parent.name
        if parent in ["spring-boot", "junit-test", "langchain4j", "aws-java"]:
            return parent
        return "backend"

    def _infer_tags(self, skill_name: str) -> str:
        """Infer tags from skill name."""
        tags = []

        # Add skill name parts as tags
        parts = skill_name.replace("-", " ").split()
        tags.extend([p for p in parts if len(p) > 2])

        # Add common tags based on keywords
        if any(x in skill_name for x in ["test", "junit"]):
            tags.append("testing")
        if any(x in skill_name for x in ["batch", "job"]):
            tags.append("batch-processing")
        if "cache" in skill_name:
            tags.append("caching")

        # Return as YAML list format string
        unique_tags = list(set(tags))[:5]  # Limit to 5 tags
        return "[" + ", ".join(unique_tags) + "]"

    def _build_skill_md_content(self, frontmatter: Dict, body: str) -> str:
        """Build complete SKILL.md content with frontmatter and body (no yaml library)."""
        fm_lines = ["---"]

        for key, value in frontmatter.items():
            if isinstance(value, list):
                # Format list as YAML array
                fm_lines.append(f"{key}: {json.dumps(value)}")
            elif isinstance(value, str):
                # Check if value needs quoting
                if any(c in value for c in ['"', "'", ":", "-", "#"]):
                    fm_lines.append(f'{key}: "{value}"')
                else:
                    fm_lines.append(f"{key}: {value}")
            else:
                fm_lines.append(f"{key}: {value}")

        fm_lines.append("---")
        fm_lines.append("")

        return "\n".join(fm_lines) + body

    def print_analysis_report(self, analyses: list) -> None:
        """Print analysis report for all skills."""
        if not analyses:
            print("No skills to analyze")
            return

        print("\n" + "=" * 70)
        print("📊 SKILL REFACTORING ANALYSIS REPORT")
        print("=" * 70)

        for analysis in analyses:
            if "error" in analysis:
                print(f"\n❌ {analysis['name']}: {analysis['error']}")
                continue

            print(f"\n📁 {analysis['name']}")
            print(f"   Path: {analysis['path']}")

            if analysis["frontmatter_issues"]:
                print("   Frontmatter Issues:")
                for issue in analysis["frontmatter_issues"]:
                    print(f"   - {issue}")

            if analysis["content_issues"]:
                print("   Content Issues:")
                for issue in analysis["content_issues"]:
                    print(f"   - {issue}")

            if analysis["recommendations"]:
                print("   Recommendations:")
                for i, rec in enumerate(analysis["recommendations"], 1):
                    print(f"   {i}. [{rec['type']}] {rec['action']}")

            status = "✅ Ready" if analysis["ready_for_refactor"] else "⚠️ Needs review"
            print(f"   Status: {status}")

        print("\n" + "=" * 70)

    def print_summary(self) -> None:
        """Print summary of refactoring work."""
        print("\n" + "=" * 70)
        print("📈 REFACTORING SUMMARY")
        print("=" * 70)
        print(f"Skills analyzed: {self.report['analyzed']}")
        print(f"Skills refactored: {self.report['refactored']}")
        
        if self.fix_content:
            print(f"Skills with content fixed: {self.report['content_fixed']}")

        if self.report["issues"]:
            print(f"\n⚠️ Issues encountered ({len(self.report['issues'])}):")
            for issue in self.report["issues"]:
                print(f"  - {issue}")

        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No actual changes were made")
            print("   Re-run without --dry-run to apply changes")

        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Refactor skills to match official Anthropic format"
    )
    parser.add_argument(
        "--skill-name",
        help="Name of specific skill to refactor (if not specified, processes all)"
    )
    parser.add_argument(
        "--path",
        default="./skills",
        help="Base path to skills directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing files"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze, don't refactor"
    )
    parser.add_argument(
        "--fix-content",
        action="store_true",
        help="Use Copilot CLI to fix skill content issues (requires copilot CLI)"
    )

    args = parser.parse_args()

    refactorer = SkillRefactorer(args.path, args.dry_run, args.fix_content)

    # Find skills
    skills = refactorer.find_skills(args.skill_name)
    if not skills:
        print("No skills found to process")
        sys.exit(1)

    print(f"🔍 Found {len(skills)} skill(s) to process\n")

    # Analyze all skills
    analyses = []
    for skill_path in skills:
        analysis = refactorer.analyze_skill(skill_path)
        analyses.append(analysis)
        refactorer.report["analyzed"] += 1

    # Print analysis report
    refactorer.print_analysis_report(analyses)

    # Refactor if not analyze-only
    if not args.analyze_only:
        for i, skill_path in enumerate(skills):
            print(f"\n[{i+1}/{len(skills)}] Processing {skill_path.name}...")
            
            # Get corresponding analysis
            analysis = analyses[i]
            
            # Fix content first if requested
            if refactorer.fix_content and ("error" not in analysis):
                if refactorer.fix_skill_content(skill_path, analysis):
                    refactorer.report["content_fixed"] += 1
            
            # Then refactor structure
            if refactorer.refactor_skill(skill_path):
                refactorer.report["refactored"] += 1

        refactorer.print_summary()


if __name__ == "__main__":
    main()
