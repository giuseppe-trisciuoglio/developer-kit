# KPI Evaluation — Quality Metrics System

The KPI Evaluation system provides objective, quantitative quality metrics for task implementations. It removes evaluator bias by using pre-calculated data instead of subjective assessments.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: HOOK (automatic)                                   │
│  Trigger: PostToolUse on TASK-*.md files                    │
│  Script: hooks/task-kpi-analyzer.py                         │
│  Output: tasks/TASK-XXX--kpi.json                           │
├─────────────────────────────────────────────────────────────┤
│  Step 2: EVALUATOR AGENT                                    │
│  Input: tasks/TASK-XXX--kpi.json                            │
│  Action: Data-driven pass/fail decision                     │
│  Output: tasks/TASK-XXX--evaluation.md                      │
└─────────────────────────────────────────────────────────────┘
```

**You don't run KPI analysis manually.** The hook fires automatically every time a task file is saved. The Evaluator Agent reads the results during task review.

## KPI Categories

### 1. Spec Compliance (30% weight)

Measures how well the implementation matches the specification.

| Metric | Calculation | Max Score |
|--------|------------|-----------|
| **Acceptance Criteria Met** | `(checked / total) × 10` | 10 |
| **Requirements Coverage** | Count of REQ-IDs covered by implementation | 10 |
| **No Scope Creep** | `(implemented_files / expected_files) × 10` | 10 |

**Example:**
```
Task: Implement JWT token service
Acceptance Criteria: 4 defined, 4 checked → score: 10.0
Requirements: REQ-05, REQ-06 covered → score: 10.0
Scope: 3 files expected, 3 implemented → score: 10.0
Weighted: 10.0 × 0.30 = 3.0
```

### 2. Code Quality (25% weight)

Measures implementation quality against language-specific standards.

| Metric | Calculation | Max Score |
|--------|------------|-----------|
| **Static Analysis** | Tool results (ESLint, Checkstyle, etc.) | 10 |
| **Complexity** | Function length analysis | 10 |
| **Patterns Alignment** | Knowledge Graph pattern matching | 10 |

**Example:**
```
Static Analysis: 0 errors, 2 warnings → score: 9.0
Complexity: All functions <20 lines → score: 10.0
Patterns: Follows project conventions → score: 9.5
Weighted: 9.5 × 0.25 = 2.375
```

### 3. Test Coverage (25% weight)

Measures testing completeness.

| Metric | Calculation | Max Score |
|--------|------------|-----------|
| **Unit Tests** | `min(10, test_files × 5)` | 10 |
| **Test/Code Ratio** | `(test_count / code_count) × 10` | 10 |
| **Coverage Percentage** | Coverage report / 10 | 10 |

**Example:**
```
Unit Tests: 2 test files for 1 source file → score: 10.0
Ratio: 120 test LOC / 95 code LOC = 1.26 → score: 10.0
Coverage: 87% → score: 8.7
Weighted: 9.57 × 0.25 = 2.39
```

### 4. Contract Fulfillment (20% weight)

Measures whether task contracts (provides/expects) are satisfied.

| Metric | Calculation | Max Score |
|--------|------------|-----------|
| **Provides Verified** | Symbols from `provides` found in code | 10 |
| **Expects Satisfied** | Dependencies from `expects` exist | 10 |

**Example:**
```
Provides: [JwtTokenService, TokenPair] — both found → score: 10.0
Expects: [UserDetails, SecretKey] — both exist → score: 10.0
Weighted: 10.0 × 0.20 = 2.0
```

## Overall Score Calculation

```
Overall = (Spec Compliance × 0.30) +
          (Code Quality × 0.25) +
          (Test Coverage × 0.25) +
          (Contract Fulfillment × 0.20)
```

### Example Calculation

| Category | Raw Score | Weight | Weighted |
|----------|-----------|--------|----------|
| Spec Compliance | 10.0 | 30% | 3.00 |
| Code Quality | 9.5 | 25% | 2.38 |
| Test Coverage | 9.57 | 25% | 2.39 |
| Contract Fulfillment | 10.0 | 20% | 2.00 |
| **Overall** | | | **9.77/10** |

## Thresholds

### Decision Protocol

| Decision | Condition |
|----------|-----------|
| **APPROVE** | `score ≥ threshold` AND `critical_issues == 0` |
| **CONDITIONAL APPROVE** | `score ≥ threshold - 0.5` AND `critical_issues == 0` |
| **REQUEST FIXES** | `score < threshold` OR `critical_issues > 0` |

### Default Threshold

**7.5/10** — configurable per project type.

### Recommended Thresholds

| Project Type | Threshold | Rationale |
|--------------|-----------|-----------|
| Production MVP | 8.0 | High quality required for production |
| Internal Tool | 7.0 | Good enough for internal use |
| Prototype | 6.0 | Functional over perfect |
| Critical System | 8.5 | No compromises (payments, security, medical) |

## Quality Levels

| Score Range | Level | Action |
|-------------|-------|--------|
| 9.0 - 10.0 | Exceptional | Approve, document best practices |
| 8.0 - 8.9 | Good | Approve with minor notes |
| 7.0 - 7.9 | Acceptable | Approve (if meets threshold) |
| 6.0 - 6.9 | Below Standard | Request specific improvements |
| < 6.0 | Poor | Significant rework required |

## KPI File Format

Auto-generated at `tasks/TASK-XXX--kpi.json`:

```json
{
  "task_id": "TASK-002",
  "spec_id": "001-user-auth",
  "evaluated_at": "2026-04-10T14:30:00Z",
  "overall_score": 8.2,
  "passed_threshold": true,
  "threshold": 7.5,
  "kpi_scores": [
    {
      "category": "spec_compliance",
      "weight": 0.30,
      "score": 9.0,
      "weighted_score": 2.70,
      "metrics": {
        "acceptance_criteria_met": 10.0,
        "requirements_coverage": 8.0,
        "no_scope_creep": 9.0
      }
    },
    {
      "category": "code_quality",
      "weight": 0.25,
      "score": 8.0,
      "weighted_score": 2.00,
      "metrics": {
        "static_analysis": 8.5,
        "complexity": 8.0,
        "patterns_alignment": 7.5
      }
    },
    {
      "category": "test_coverage",
      "weight": 0.25,
      "score": 7.5,
      "weighted_score": 1.875,
      "metrics": {
        "unit_tests": 8.0,
        "test_code_ratio": 7.0,
        "coverage_percentage": 7.5
      }
    },
    {
      "category": "contract_fulfillment",
      "weight": 0.20,
      "score": 8.1,
      "weighted_score": 1.62,
      "metrics": {
        "provides_verified": 10.0,
        "expects_satisfied": 6.2
      }
    }
  ],
  "critical_issues": [],
  "recommendations": [
    "Add more integration tests for expects contracts",
    "Consider reducing function complexity in JwtTokenService.validateToken()"
  ],
  "summary": "Score: 8.2/10 - PASSED"
}
```

## Evaluator Agent

The Evaluator Agent (`evaluator-agent`) is a specialized subagent that reads KPI files and makes data-driven decisions.

### Core Principle

**"Don't trust your gut — trust the data."**

The Evaluator Agent counters LLM leniency bias by grounding decisions in quantitative metrics.

### Evaluation Workflow

1. **Read KPI file** (mandatory first step)
2. **Read task and specification** for qualitative validation
3. **Compare KPI evidence** with actual implementation
4. **Generate evaluation report** at `TASK-XXX--evaluation.md`
5. **Make decision** based on scores and critical issues

### When the Evaluator Can Override KPI Scores

The Evaluator can only lower scores (never raise) with documented justification:
- Critical security vulnerability discovered during code review
- Completely wrong implementation that passes metrics by coincidence
- Missing error handling that metrics couldn't detect

### Evaluation Report

Output at `tasks/TASK-XXX--evaluation.md`:

```markdown
# Task Evaluation: TASK-002

## Decision: APPROVED

## Scores
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Spec Compliance | 9.0 | 30% | 2.70 |
| Code Quality | 8.0 | 25% | 2.00 |
| Test Coverage | 7.5 | 25% | 1.88 |
| Contract Fulfillment | 8.1 | 20% | 1.62 |
| **Overall** | | | **8.2/10** |

## Critical Issues
None

## Recommendations
1. Add integration tests for expects contracts (score: 6.2/10)
2. Reduce complexity in JwtTokenService.validateToken()

## Evidence
- KPI data source: TASK-002--kpi.json (evaluated 2026-04-10T14:30:00Z)
- Code review: passed with minor notes
- Spec compliance: 4/4 acceptance criteria verified
```

## Integration with Ralph Loop

The Ralph Loop uses KPI evaluation to decide whether to retry failed tasks:

```
implementation → review → (read KPI score)
                          ├─ score ≥ threshold → cleanup → sync
                          └─ score < threshold → fix → implementation (retry)
                                                    └─ max 3 retries
```

## Reading KPI Files Manually

```bash
# View KPI scores for a task
cat docs/specs/001-user-auth/tasks/TASK-002--kpi.json | python3 -m json.tool

# Quick summary
cat docs/specs/001-user-auth/tasks/TASK-002--kpi.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"Score: {data['overall_score']}/10\")
print(f\"Status: {'PASSED' if data['passed_threshold'] else 'FAILED'}\")
print(f\"Threshold: {data['threshold']}\")
for kpi in data['kpi_scores']:
    print(f\"  {kpi['category']}: {kpi['score']}/10 (weight: {kpi['weight']})\")
"
```
