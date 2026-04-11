#!/usr/bin/env python3
"""
Task KPI Analyzer Hook

Automatically calculates quality KPIs when TASK-*.md files are modified.
Saves results to TASK-XXX--kpi.json for use by evaluator-agent and agents_loop.

Usage:
    python3 task-kpi-analyzer.py <task-file-path>
    
Environment:
    CLAUDE_CHANGED_FILE - Alternative way to pass the file path

Output:
    Creates/updates docs/specs/[ID]/tasks/TASK-XXX--kpi.json
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any


def get_changed_file() -> str:
    """Get the changed file path from arguments or environment."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.environ.get('CLAUDE_CHANGED_FILE', '')


def is_task_file(filepath: str) -> bool:
    """Check if file is a task file (TASK-*.md)."""
    return bool(re.match(r'TASK-\d+\.md$', os.path.basename(filepath)))


@dataclass
class KPIScore:
    category: str
    weight: int
    score: float
    metrics: Dict[str, float]
    evidence: List[str]
    
    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "weight": self.weight,
            "score": round(self.score, 2),
            "weighted_score": round((self.score * self.weight) / 100, 2),
            "metrics": self.metrics,
            "evidence": self.evidence
        }


class TaskKPIAnalyzer:
    """Analyzes task implementation quality with objective KPIs."""
    
    DEFAULT_THRESHOLD = 7.5
    
    def __init__(self, task_path: str):
        self.task_path = Path(task_path)
        self.spec_path = self.task_path.parent.parent
        self.task_data = {}
        self.code_files = []
        self.test_files = []
        
    def analyze(self) -> dict:
        """Run full analysis and return KPI report as dict."""
        self._load_task()
        self._find_implemented_files()
        
        kpi_scores = [
            self._analyze_spec_compliance(),
            self._analyze_code_quality(),
            self._analyze_test_coverage(),
            self._analyze_contract_fulfillment(),
        ]
        
        overall = sum((k.score * k.weight) / 100 for k in kpi_scores)
        passed = overall >= self.DEFAULT_THRESHOLD
        
        recommendations = self._generate_recommendations(kpi_scores)
        
        return {
            "task_id": self.task_data.get("id", "unknown"),
            "evaluated_at": datetime.now().isoformat(),
            "overall_score": round(overall, 2),
            "passed_threshold": passed,
            "threshold": self.DEFAULT_THRESHOLD,
            "kpi_scores": [k.to_dict() for k in kpi_scores],
            "recommendations": recommendations,
            "summary": f"Score: {overall:.1f}/10 - {'PASSED' if passed else 'FAILED'}"
        }
    
    def _load_task(self):
        """Load and parse task file."""
        try:
            with open(self.task_path, 'r') as f:
                content = f.read()
        except Exception as e:
            self.task_data = {"error": str(e)}
            return
        
        self.task_data = {"content": content}
        
        # Parse frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for field in ["id", "title", "status", "lang", "dependencies"]:
                match = re.search(rf'^{field}:\s*(.+)$', frontmatter, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if field == "dependencies":
                        value = [v.strip().strip('"\'') for v in value.strip("[]").split(",") if v.strip()]
                    self.task_data[field] = value
        
        # Extract acceptance criteria
        ac_match = re.search(r'##\s*Acceptance Criteria\s*\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if ac_match:
            ac_content = ac_match.group(1)
            checked = len(re.findall(r'- \[x\]', ac_content, re.IGNORECASE))
            total = len(re.findall(r'- \[([ x])\]', ac_content, re.IGNORECASE))
            self.task_data["acceptance_criteria"] = {"checked": checked, "total": total}
        
        # Extract provides/expects
        self.task_data["provides"] = self._extract_contract_section(content, "provides")
        self.task_data["expects"] = self._extract_contract_section(content, "expects")
    
    def _extract_contract_section(self, content: str, section: str) -> List[dict]:
        """Extract provides/expects from task frontmatter."""
        pattern = rf'^{section}:\s*\n((?:  - .+\n)+)'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            items = []
            for line in match.group(1).strip().split('\n'):
                if 'file:' in line:
                    items.append({"file": line.split('file:')[1].strip().strip('"\'')})
            return items
        return []
    
    def _find_implemented_files(self):
        """Find files created/modified for this task."""
        content = self.task_data.get("content", "")
        
        # Extract from "Files to Create" section
        ftc_match = re.search(
            r'##\s*Implementation Details.*?\*\*Files to Create\*\*:\s*\n(.*?)(?=\*\*|$)',
            content, re.DOTALL | re.IGNORECASE
        )
        if ftc_match:
            for line in ftc_match.group(1).strip().split('\n'):
                if line.strip().startswith('-'):
                    path_match = re.search(r'`([^`]+)`', line)
                    if path_match:
                        file_path = path_match.group(1)
                        if self._is_test_file(file_path):
                            self.test_files.append(file_path)
                        else:
                            self.code_files.append(file_path)
    
    def _is_test_file(self, path: str) -> bool:
        """Check if path is a test file."""
        test_patterns = ["test", "spec", "__tests__", ".test.", ".spec."]
        return any(p in path.lower() for p in test_patterns)
    
    def _analyze_spec_compliance(self) -> KPIScore:
        """Analyze how well implementation matches specification."""
        metrics = {}
        evidence = []
        
        # Acceptance Criteria Coverage
        ac = self.task_data.get("acceptance_criteria", {})
        if ac.get("total", 0) > 0:
            coverage = (ac.get("checked", 0) / ac.get("total", 1)) * 10
        else:
            coverage = 5
        metrics["acceptance_criteria_met"] = round(min(10, coverage), 2)
        evidence.append(f"Acceptance criteria: {ac.get('checked', 0)}/{ac.get('total', 0)} checked")
        
        # Requirements Coverage
        req_coverage = self._check_requirements_coverage()
        metrics["requirements_coverage"] = round(req_coverage, 2)
        evidence.append(f"Requirements coverage: {req_coverage}/10")
        
        # No Scope Creep
        expected_files = len(self.code_files) + len(self.test_files)
        actual_files = len([f for f in self.code_files if os.path.exists(f)])
        scope_score = 10 if expected_files == 0 else min(10, (actual_files / max(1, expected_files)) * 10)
        metrics["no_scope_creep"] = round(scope_score, 2)
        evidence.append(f"Files implemented: {actual_files}/{expected_files}")
        
        score = sum(metrics.values()) / len(metrics)
        
        return KPIScore(
            category="Spec Compliance",
            weight=30,
            score=score,
            metrics=metrics,
            evidence=evidence
        )
    
    def _analyze_code_quality(self) -> KPIScore:
        """Analyze code quality."""
        metrics = {}
        evidence = []
        
        if not self.code_files:
            return KPIScore(
                category="Code Quality",
                weight=25,
                score=5.0,
                metrics={"no_code": 5.0},
                evidence=["No code files detected"]
            )
        
        lang = self.task_data.get("lang", "").lower()
        
        # Static Analysis
        static_score = self._run_static_analysis(lang)
        metrics["static_analysis"] = round(static_score, 2)
        evidence.append(f"Static analysis: {static_score}/10")
        
        # Complexity
        complexity_score = self._check_complexity(lang)
        metrics["complexity"] = round(complexity_score, 2)
        evidence.append(f"Complexity: {complexity_score}/10")
        
        # Patterns
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
        
        # Unit Tests Present
        unit_test_score = min(10, len(self.test_files) * 5)
        metrics["unit_tests"] = round(unit_test_score, 2)
        evidence.append(f"Test files: {len(self.test_files)}")
        
        # Test/Code Ratio
        code_count = len(self.code_files)
        test_count = len(self.test_files)
        ratio = test_count / max(1, code_count)
        ratio_score = min(10, ratio * 10)
        metrics["test_code_ratio"] = round(ratio_score, 2)
        evidence.append(f"Test-to-code ratio: {test_count}:{code_count}")
        
        # Coverage
        coverage_score = self._check_coverage_reports()
        metrics["coverage_percentage"] = round(coverage_score, 2)
        evidence.append(f"Coverage: {coverage_score}/10")
        
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
        
        # Provides Verified
        if provides:
            verified = sum(1 for p in provides if os.path.exists(p.get("file", "")))
            provides_score = (verified / len(provides)) * 10
        else:
            provides_score = 10
        metrics["provides_verified"] = round(provides_score, 2)
        evidence.append(f"Provides verified: {provides_score}/10")
        
        # Expects Satisfied
        if expects:
            satisfied = sum(1 for e in expects if os.path.exists(e.get("file", "")))
            expects_score = (satisfied / len(expects)) * 10
        else:
            expects_score = 10
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
    
    def _check_requirements_coverage(self) -> float:
        """Check requirements coverage from traceability matrix."""
        matrix_path = self.spec_path / "traceability-matrix.md"
        if not matrix_path.exists():
            return 5.0
        
        try:
            with open(matrix_path, 'r') as f:
                content = f.read()
            task_id = self.task_data.get("id", "")
            if task_id:
                matches = len(re.findall(rf'\b{task_id}\b', content))
                return min(10, matches * 2)
        except:
            pass
        return 5.0
    
    def _run_static_analysis(self, lang: str) -> float:
        """Run language-specific static analysis."""
        scores = []
        
        if lang in ["java", "spring"] and os.path.exists("pom.xml"):
            try:
                result = subprocess.run(
                    ["./mvnw", "checkstyle:check", "-q"],
                    capture_output=True, text=True, timeout=60
                )
                scores.append(10 if result.returncode == 0 else 5)
            except:
                pass
        
        elif lang in ["typescript", "nestjs", "react"] and os.path.exists("package.json"):
            try:
                result = subprocess.run(
                    ["npm", "run", "lint", "--silent"],
                    capture_output=True, text=True, timeout=60
                )
                scores.append(10 if result.returncode == 0 else 5)
            except:
                pass
        
        elif lang == "python":
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
        long_functions = 0
        
        for file_path in self.code_files:
            if not os.path.exists(file_path):
                continue
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if lang in ["java", "spring"]:
                        long_functions += len(re.findall(r'(public|private|protected).*\{[^}]{500,}\}', content))
                    elif lang in ["typescript", "nestjs"]:
                        long_functions += len(re.findall(r'function\s+\w+.*?\{[^}]{500,}\}', content, re.DOTALL))
            except:
                pass
        
        complexity_ratio = long_functions / max(1, len(self.code_files))
        return max(0, 10 - (complexity_ratio * 5))
    
    def _check_patterns_alignment(self) -> float:
        """Check alignment with project patterns."""
        kg_path = self.spec_path / "knowledge-graph.json"
        if not kg_path.exists():
            return 5.0
        
        try:
            with open(kg_path, 'r') as f:
                kg = json.load(f)
            if kg.get("patterns", {}).get("architectural", []):
                return 8.0
        except:
            pass
        return 5.0
    
    def _check_coverage_reports(self) -> float:
        """Check for coverage reports."""
        coverage_paths = [
            "coverage/lcov-report/index.html",
            "target/site/jacoco/index.html",
            ".coverage",
            "coverage.xml"
        ]
        
        for path in coverage_paths:
            if os.path.exists(path):
                try:
                    if path.endswith(".xml"):
                        with open(path, 'r') as f:
                            content = f.read()
                            match = re.search(r'line-rate="([\d.]+)"', content)
                            if match:
                                return min(10, float(match.group(1)) * 10)
                except:
                    pass
                return 7.0
        return 3.0
    
    def _generate_recommendations(self, kpi_scores: List[KPIScore]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        for kpi in kpi_scores:
            if kpi.score < 5:
                recommendations.append(f"{kpi.category}: Critical improvement needed")
            elif kpi.score < 7:
                recommendations.append(f"{kpi.category}: Moderate improvements possible")
        
        return recommendations


def update_kpi_file(task_path: str) -> bool:
    """Update KPI file for the given task."""
    path = Path(task_path)
    if not path.exists():
        print(f"⚠️  File not found: {task_path}", file=sys.stderr)
        return False
    
    # Analyze
    analyzer = TaskKPIAnalyzer(task_path)
    report = analyzer.analyze()
    
    # Save to KPI file
    kpi_file = path.parent / f"{path.stem}--kpi.json"
    
    try:
        with open(kpi_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ KPI analysis saved: {kpi_file.name} (Score: {report['overall_score']}/10)")
        return True
    except Exception as e:
        print(f"⚠️  Error saving KPI file: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Main entry point."""
    filepath = get_changed_file()
    
    if not filepath:
        return 0
    
    if not is_task_file(filepath):
        return 0
    
    try:
        update_kpi_file(filepath)
        return 0
    except Exception as e:
        print(f"⚠️  Error in task-kpi-analyzer: {e}", file=sys.stderr)
        return 0


if __name__ == '__main__':
    sys.exit(main())
