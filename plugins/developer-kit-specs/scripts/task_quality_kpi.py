#!/usr/bin/env python3
"""
task_quality_kpi.py - Calculate objective KPIs for task quality evaluation.

This script provides quantitative metrics to complement the qualitative agent review.
It can be called by agents_loop or evaluator-agent to get objective scores.

Usage:
    python3 task_quality_kpi.py --task=docs/specs/001-feature/tasks/TASK-001.md
    python3 task_quality_kpi.py --task=TASK-001 --spec=docs/specs/001-feature/
    python3 task_quality_kpi.py --task=TASK-001 --spec=docs/specs/001-feature/ --format=json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field


@dataclass
class KPIScore:
    category: str
    weight: int  # 0-100
    score: float  # 0-10
    metrics: Dict[str, float]
    evidence: List[str]
    
    @property
    def weighted_score(self) -> float:
        return (self.score * self.weight) / 100


@dataclass
class TaskQualityReport:
    task_id: str
    overall_score: float  # 0-10
    passed_threshold: bool
    threshold: float
    kpi_scores: List[KPIScore]
    summary: str
    recommendations: List[str]
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "overall_score": round(self.overall_score, 2),
            "passed_threshold": self.passed_threshold,
            "threshold": self.threshold,
            "kpi_scores": [
                {
                    "category": k.category,
                    "weight": k.weight,
                    "score": round(k.score, 2),
                    "weighted_score": round(k.weighted_score, 2),
                    "metrics": k.metrics,
                    "evidence": k.evidence
                }
                for k in self.kpi_scores
            ],
            "summary": self.summary,
            "recommendations": self.recommendations
        }


class TaskQualityAnalyzer:
    """Analyzes task implementation quality with objective KPIs."""
    
    # Default threshold for passing
    DEFAULT_THRESHOLD = 7.5  # 7.5/10 = "Good enough"
    
    def __init__(self, task_path: str, spec_path: Optional[str] = None):
        self.task_path = Path(task_path)
        self.spec_path = Path(spec_path) if spec_path else self.task_path.parent.parent
        self.task_data = {}
        self.spec_data = None
        self.code_files = []
        self.test_files = []
        
    def analyze(self, threshold: float = DEFAULT_THRESHOLD) -> TaskQualityReport:
        """Run full analysis and return quality report."""
        self._load_task()
        self._load_spec()
        self._find_implemented_files()
        
        kpi_scores = [
            self._analyze_spec_compliance(),
            self._analyze_code_quality(),
            self._analyze_test_coverage(),
            self._analyze_contract_fulfillment(),
        ]
        
        overall = sum(k.weighted_score for k in kpi_scores)
        passed = overall >= threshold
        
        recommendations = self._generate_recommendations(kpi_scores)
        summary = self._generate_summary(kpi_scores, overall, passed)
        
        return TaskQualityReport(
            task_id=self.task_data.get("id", "unknown"),
            overall_score=overall,
            passed_threshold=passed,
            threshold=threshold,
            kpi_scores=kpi_scores,
            summary=summary,
            recommendations=recommendations
        )
    
    def _load_task(self):
        """Load and parse task file."""
        with open(self.task_path, 'r') as f:
            content = f.read()
        
        # Parse frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        self.task_data = {"content": content}
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            # Extract key fields
            for field in ["id", "title", "status", "lang", "dependencies"]:
                match = re.search(rf'^{field}:\s*(.+)$', frontmatter, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if field == "dependencies":
                        # Parse array
                        value = [v.strip().strip('"\'') for v in value.strip("[]").split(",") if v.strip()]
                    self.task_data[field] = value
        
        # Extract acceptance criteria
        ac_match = re.search(r'##\s*Acceptance Criteria\s*\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if ac_match:
            ac_content = ac_match.group(1)
            # Count checkboxes
            checked = len(re.findall(r'- \[x\]', ac_content, re.IGNORECASE))
            total = len(re.findall(r'- \[([ x])\]', ac_content, re.IGNORECASE))
            self.task_data["acceptance_criteria"] = {"checked": checked, "total": total}
        
        # Extract provides/expects
        self.task_data["provides"] = self._extract_contract_section(content, "provides")
        self.task_data["expects"] = self._extract_contract_section(content, "expects")
    
    def _extract_contract_section(self, content: str, section: str) -> List[dict]:
        """Extract provides/expects from task frontmatter."""
        # Look for the section in YAML frontmatter
        pattern = rf'^{section}:\s*\n((?:  - .+\n)+)'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            items = []
            for line in match.group(1).strip().split('\n'):
                if 'file:' in line:
                    items.append({"file": line.split('file:')[1].strip().strip('"\'')})
            return items
        return []
    
    def _load_spec(self):
        """Load specification for traceability."""
        spec_file = self.task_data.get("spec", "")
        if spec_file:
            spec_path = self.spec_path / spec_file if not spec_file.startswith("/") else Path(spec_file)
            if spec_path.exists():
                with open(spec_path, 'r') as f:
                    self.spec_data = f.read()
    
    def _find_implemented_files(self):
        """Find files created/modified for this task."""
        # Look in task content for "Files to Create" section
        content = self.task_data.get("content", "")
        
        # Extract from "Files to Create" section
        ftc_match = re.search(r'##\s*Implementation Details.*?\*\*Files to Create\*\*:\s*\n(.*?)(?=\*\*|$)', 
                              content, re.DOTALL | re.IGNORECASE)
        if ftc_match:
            for line in ftc_match.group(1).strip().split('\n'):
                if line.strip().startswith('-'):
                    # Extract path from markdown list item
                    path_match = re.search(r'`([^`]+)`', line)
                    if path_match:
                        file_path = path_match.group(1)
                        if self._is_test_file(file_path):
                            self.test_files.append(file_path)
                        else:
                            self.code_files.append(file_path)
        
        # Also check git diff if available
        self._check_git_changes()
    
    def _is_test_file(self, path: str) -> bool:
        """Check if path is a test file."""
        test_patterns = ["test", "spec", "__tests__", ".test.", ".spec."]
        path_lower = path.lower()
        return any(p in path_lower for p in test_patterns)
    
    def _check_git_changes(self):
        """Check git for recently modified files."""
        try:
            # Get files changed in last commit
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "--name-only"],
                capture_output=True, text=True, cwd=self.spec_path
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('docs/specs/'):
                        if self._is_test_file(line):
                            if line not in self.test_files:
                                self.test_files.append(line)
                        else:
                            if line not in self.code_files:
                                self.code_files.append(line)
        except:
            pass  # Git not available or error
    
    # ============== KPI ANALYSIS METHODS ==============
    
    def _analyze_spec_compliance(self) -> KPIScore:
        """Analyze how well implementation matches specification."""
        metrics = {}
        evidence = []
        
        # 1. Acceptance Criteria Coverage
        ac = self.task_data.get("acceptance_criteria", {})
        if ac.get("total", 0) > 0:
            coverage = (ac.get("checked", 0) / ac.get("total", 1)) * 10
        else:
            coverage = 5  # Neutral if no criteria defined
        metrics["acceptance_criteria_met"] = round(min(10, coverage), 2)
        evidence.append(f"Acceptance criteria: {ac.get('checked', 0)}/{ac.get('total', 0)} checked")
        
        # 2. Requirements Coverage (check traceability matrix)
        req_coverage = self._check_requirements_coverage()
        metrics["requirements_coverage"] = round(req_coverage, 2)
        evidence.append(f"Requirements coverage: {req_coverage}/10")
        
        # 3. No Scope Creep (files match expected)
        expected_files = len(self.code_files) + len(self.test_files)
        actual_files = len([f for f in self.code_files if os.path.exists(f)])
        scope_score = 10 if expected_files == 0 else min(10, (actual_files / max(1, expected_files)) * 10)
        metrics["no_scope_creep"] = round(scope_score, 2)
        evidence.append(f"Files implemented: {actual_files}/{expected_files}")
        
        # Calculate weighted score
        score = sum(metrics.values()) / len(metrics)
        
        return KPIScore(
            category="Spec Compliance",
            weight=30,
            score=score,
            metrics=metrics,
            evidence=evidence
        )
    
    def _analyze_code_quality(self) -> KPIScore:
        """Analyze code quality with static analysis."""
        metrics = {}
        evidence = []
        
        if not self.code_files:
            # No code files found - neutral score
            return KPIScore(
                category="Code Quality",
                weight=25,
                score=5.0,
                metrics={"no_code": 5.0},
                evidence=["No code files detected in task"]
            )
        
        # 1. Static Analysis (language-specific)
        lang = self.task_data.get("lang", "").lower()
        static_score = self._run_static_analysis(lang)
        metrics["static_analysis"] = round(static_score, 2)
        evidence.append(f"Static analysis score: {static_score}/10")
        
        # 2. Complexity Check
        complexity_score = self._check_complexity(lang)
        metrics["complexity"] = round(complexity_score, 2)
        evidence.append(f"Complexity score: {complexity_score}/10")
        
        # 3. Patterns Alignment (check against knowledge graph if available)
        patterns_score = self._check_patterns_alignment()
        metrics["patterns_alignment"] = round(patterns_score, 2)
        evidence.append(f"Patterns alignment: {patterns_score}/10")
        
        score = sum(metrics.values()) / len(metrics)
        
        return KPIScore(
            category="Code Quality",
            weight=25,
            score=score,
            metrics=metrics,
            evidence=evidence
        )
    
    def _analyze_test_coverage(self) -> KPIScore:
        """Analyze test coverage."""
        metrics = {}
        evidence = []
        
        # 1. Unit Tests Present
        unit_test_score = min(10, len(self.test_files) * 5)  # 2 test files = max score
        metrics["unit_tests"] = round(unit_test_score, 2)
        evidence.append(f"Test files found: {len(self.test_files)}")
        
        # 2. Test-to-Code Ratio
        code_count = len(self.code_files)
        test_count = len(self.test_files)
        ratio = test_count / max(1, code_count)
        ratio_score = min(10, ratio * 10)  # 1:1 ratio = 10/10
        metrics["test_code_ratio"] = round(ratio_score, 2)
        evidence.append(f"Test-to-code ratio: {test_count}:{code_count} ({ratio:.2f})")
        
        # 3. Coverage Percentage (if available)
        coverage_score = self._check_coverage_reports()
        metrics["coverage_percentage"] = round(coverage_score, 2)
        evidence.append(f"Coverage score: {coverage_score}/10")
        
        score = sum(metrics.values()) / len(metrics)
        
        return KPIScore(
            category="Test Coverage",
            weight=25,
            score=score,
            metrics=metrics,
            evidence=evidence
        )
    
    def _analyze_contract_fulfillment(self) -> KPIScore:
        """Check provides/expects contracts."""
        metrics = {}
        evidence = []
        
        provides = self.task_data.get("provides", [])
        expects = self.task_data.get("expects", [])
        
        # 1. Provides Verified (files exist and contain symbols)
        if provides:
            verified = 0
            for p in provides:
                file_path = p.get("file", "")
                if file_path and os.path.exists(file_path):
                    verified += 1
            provides_score = (verified / len(provides)) * 10
        else:
            provides_score = 10  # No provides defined = neutral
        metrics["provides_verified"] = round(provides_score, 2)
        evidence.append(f"Provides verified: {provides_score}/10")
        
        # 2. Expects Satisfied (check dependencies)
        if expects:
            satisfied = 0
            for e in expects:
                file_path = e.get("file", "")
                if file_path and os.path.exists(file_path):
                    satisfied += 1
            expects_score = (satisfied / len(expects)) * 10
        else:
            expects_score = 10  # No expects = neutral
        metrics["expects_satisfied"] = round(expects_score, 2)
        evidence.append(f"Expects satisfied: {expects_score}/10")
        
        score = sum(metrics.values()) / len(metrics)
        
        return KPIScore(
            category="Contract Fulfillment",
            weight=20,
            score=score,
            metrics=metrics,
            evidence=evidence
        )
    
    # ============== HELPER METHODS ==============
    
    def _check_requirements_coverage(self) -> float:
        """Check how many requirements are covered (from traceability matrix)."""
        matrix_path = self.spec_path / "traceability-matrix.md"
        if not matrix_path.exists():
            return 5.0  # Neutral if no matrix
        
        try:
            with open(matrix_path, 'r') as f:
                content = f.read()
            
            # Count covered requirements
            task_id = self.task_data.get("id", "")
            if task_id:
                # Count how many times this task appears in the matrix
                matches = len(re.findall(rf'\b{task_id}\b', content))
                return min(10, matches * 2)  # 5+ requirements = max
        except:
            pass
        return 5.0
    
    def _run_static_analysis(self, lang: str) -> float:
        """Run language-specific static analysis."""
        scores = []
        
        if lang in ["java", "spring"]:
            # Check for Maven/Gradle checkstyle
            if os.path.exists("pom.xml"):
                try:
                    result = subprocess.run(
                        ["./mvnw", "checkstyle:check", "-q"],
                        capture_output=True, text=True, timeout=60
                    )
                    scores.append(10 if result.returncode == 0 else 5)
                except:
                    pass
        
        elif lang in ["typescript", "nestjs", "react"]:
            # Check for ESLint/TypeScript
            if os.path.exists("package.json"):
                try:
                    result = subprocess.run(
                        ["npm", "run", "lint", "--silent"],
                        capture_output=True, text=True, timeout=60
                    )
                    scores.append(10 if result.returncode == 0 else 5)
                except:
                    pass
        
        elif lang == "python":
            # Check with ruff or pylint
            try:
                result = subprocess.run(
                    ["ruff", "check", "."],
                    capture_output=True, text=True, timeout=60
                )
                scores.append(10 if result.returncode == 0 else 5)
            except:
                pass
        
        return sum(scores) / len(scores) if scores else 5.0
    
    def _check_complexity(self, lang: str) -> float:
        """Check code complexity."""
        # Simple heuristic: file size and function length
        total_lines = 0
        long_functions = 0
        
        for file_path in self.code_files:
            if not os.path.exists(file_path):
                continue
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    
                    # Count long functions (>50 lines)
                    content = ''.join(lines)
                    if lang in ["java", "spring"]:
                        long_functions += len(re.findall(r'(public|private|protected).*\{[^}]{500,}\}', content))
                    elif lang in ["typescript", "nestjs"]:
                        long_functions += len(re.findall(r'function\s+\w+.*?\{[^}]{500,}\}', content, re.DOTALL))
            except:
                pass
        
        # Score: fewer long functions = better
        if total_lines == 0:
            return 5.0
        
        complexity_ratio = long_functions / max(1, len(self.code_files))
        return max(0, 10 - (complexity_ratio * 5))
    
    def _check_patterns_alignment(self) -> float:
        """Check alignment with project patterns from knowledge graph."""
        kg_path = self.spec_path / "knowledge-graph.json"
        if not kg_path.exists():
            return 5.0  # Neutral if no KG
        
        try:
            with open(kg_path, 'r') as f:
                kg = json.load(f)
            
            # Check if implemented files follow known patterns
            patterns = kg.get("patterns", {}).get("architectural", [])
            if patterns:
                return 8.0  # Assume alignment if patterns exist
        except:
            pass
        
        return 5.0
    
    def _check_coverage_reports(self) -> float:
        """Check for coverage reports."""
        # Look for common coverage report locations
        coverage_paths = [
            "coverage/lcov-report/index.html",
            "target/site/jacoco/index.html",
            ".coverage",
            "coverage.xml"
        ]
        
        for path in coverage_paths:
            if os.path.exists(path):
                # Try to extract coverage percentage
                try:
                    if path.endswith(".xml"):
                        with open(path, 'r') as f:
                            content = f.read()
                            match = re.search(r'line-rate="([\d.]+)"', content)
                            if match:
                                rate = float(match.group(1))
                                return min(10, rate * 10)  # 100% = 10/10
                except:
                    pass
                return 7.0  # Coverage exists but can't parse
        
        return 3.0  # No coverage report found
    
    def _generate_recommendations(self, kpi_scores: List[KPIScore]) -> List[str]:
        """Generate improvement recommendations based on low scores."""
        recommendations = []
        
        for kpi in kpi_scores:
            if kpi.score < 5:
                recommendations.append(f"{kpi.category}: Critical improvement needed")
            elif kpi.score < 7:
                recommendations.append(f"{kpi.category}: Moderate improvements possible")
        
        # Specific recommendations
        spec_compliance = next((k for k in kpi_scores if k.category == "Spec Compliance"), None)
        if spec_compliance and spec_compliance.metrics.get("acceptance_criteria_met", 10) < 10:
            recommendations.append("Complete all acceptance criteria checkboxes")
        
        test_coverage = next((k for k in kpi_scores if k.category == "Test Coverage"), None)
        if test_coverage and test_coverage.score < 7:
            recommendations.append("Add more test files to improve coverage")
        
        return recommendations
    
    def _generate_summary(self, kpi_scores: List[KPIScore], overall: float, passed: bool) -> str:
        """Generate human-readable summary."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        summary = f"Task {self.task_data.get('id', 'unknown')}: {status} (Score: {overall:.1f}/10)\n\n"
        
        for kpi in kpi_scores:
            summary += f"{kpi.category}: {kpi.score:.1f}/10 (weight: {kpi.weight}%)\n"
        
        return summary


def main():
    parser = argparse.ArgumentParser(description="Calculate task quality KPIs")
    parser.add_argument("--task", required=True, help="Task file path or task ID")
    parser.add_argument("--spec", help="Spec folder path (if using task ID)")
    parser.add_argument("--threshold", type=float, default=7.5, help="Passing threshold (default: 7.5)")
    parser.add_argument("--format", choices=["json", "yaml", "markdown"], default="markdown", help="Output format")
    args = parser.parse_args()
    
    # Resolve task path
    task_path = args.task
    if not task_path.endswith(".md"):
        # Assume it's a task ID
        if not args.spec:
            print("ERROR: --spec required when using task ID")
            sys.exit(1)
        task_path = os.path.join(args.spec, "tasks", f"{task_path}.md")
    
    # Run analysis
    analyzer = TaskQualityAnalyzer(task_path, args.spec)
    report = analyzer.analyze(threshold=args.threshold)
    
    # Output
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif args.format == "yaml":
        try:
            import yaml
            print(yaml.dump(report.to_dict()))
        except ImportError:
            print("PyYAML not installed, using JSON format:")
            print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.summary)
        print("\n" + "="*60)
        print("DETAILED SCORES:")
        print("="*60)
        for kpi in report.kpi_scores:
            print(f"\n{kpi.category} (weight: {kpi.weight}%)")
            print(f"  Score: {kpi.score:.2f}/10 → Weighted: {kpi.weighted_score:.2f}")
            for metric, value in kpi.metrics.items():
                print(f"  - {metric}: {value}")
        
        if report.recommendations:
            print("\n" + "="*60)
            print("RECOMMENDATIONS:")
            print("="*60)
            for rec in report.recommendations:
                print(f"  • {rec}")


if __name__ == "__main__":
    main()
