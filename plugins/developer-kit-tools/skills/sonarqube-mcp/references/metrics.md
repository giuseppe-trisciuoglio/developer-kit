# SonarQube Metrics Reference

Common SonarQube metrics used in quality gate conditions and component measures.

## Reliability Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `bugs` | Number of detected bugs | Count |
| `new_bugs` | New bugs introduced since last version | Count |
| `reliability_rating` | Rating based on bugs (A–E) | Rating |
| `new_reliability_rating` | Reliability rating on new code | Rating |

## Security Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `vulnerabilities` | Number of security vulnerabilities | Count |
| `new_vulnerabilities` | New vulnerabilities on new code | Count |
| `security_rating` | Rating based on vulnerabilities (A–E) | Rating |
| `new_security_rating` | Security rating on new code | Rating |
| `security_hotspots` | Security hotspots requiring review | Count |
| `new_security_hotspots` | New security hotspots | Count |
| `security_hotspots_reviewed` | Percentage of hotspots reviewed | % |
| `new_security_hotspots_reviewed` | Hotspots reviewed on new code | % |

## Maintainability Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `code_smells` | Number of code smells | Count |
| `new_code_smells` | New code smells on new code | Count |
| `sqale_rating` | Maintainability rating (A–E) | Rating |
| `new_maintainability_rating` | Maintainability rating on new code | Rating |
| `sqale_debt_ratio` | Technical debt ratio (%) | % |
| `new_sqale_debt_ratio` | Debt ratio on new code | % |
| `sqale_index` | Technical debt in minutes | Minutes |

## Coverage Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `coverage` | Combined line and branch coverage | % |
| `new_coverage` | Coverage on new code | % |
| `line_coverage` | Percentage of lines covered by tests | % |
| `new_line_coverage` | Line coverage on new code | % |
| `branch_coverage` | Percentage of branches covered | % |
| `new_branch_coverage` | Branch coverage on new code | % |
| `uncovered_lines` | Number of uncovered lines | Count |
| `uncovered_conditions` | Number of uncovered branches | Count |
| `tests` | Number of unit tests | Count |
| `test_failures` | Number of test failures | Count |
| `test_errors` | Number of test errors | Count |
| `skipped_tests` | Number of skipped tests | Count |

## Duplication Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `duplicated_lines_density` | Percentage of duplicated lines | % |
| `new_duplicated_lines_density` | Duplication on new code | % |
| `duplicated_lines` | Number of duplicated lines | Count |
| `duplicated_blocks` | Number of duplicated blocks | Count |
| `duplicated_files` | Number of duplicated files | Count |

## Size and Complexity Metrics

| Metric Key | Description | Unit |
|---|---|---|
| `ncloc` | Non-commenting lines of code | Count |
| `lines` | Total lines (including comments and blanks) | Count |
| `statements` | Number of executable statements | Count |
| `functions` | Number of functions | Count |
| `classes` | Number of classes | Count |
| `files` | Number of files | Count |
| `complexity` | Cyclomatic complexity | Count |
| `cognitive_complexity` | Cognitive complexity score | Count |

## Rating Scale

Ratings are assigned from A (best) to E (worst):

| Rating | Bugs / Vulnerabilities |
|---|---|
| A | 0 |
| B | At least 1 Minor |
| C | At least 1 Major |
| D | At least 1 Critical |
| E | At least 1 Blocker |

## Quality Gate Condition Operators

When interpreting quality gate conditions:

| Comparator | Meaning |
|---|---|
| `GT` | Actual value greater than threshold (fails if exceeded) |
| `LT` | Actual value less than threshold (fails if below minimum) |

## Example Quality Gate Response

```json
{
  "projectStatus": {
    "status": "ERROR",
    "conditions": [
      {
        "status": "ERROR",
        "metricKey": "new_coverage",
        "comparator": "LT",
        "errorThreshold": "80",
        "actualValue": "65.2"
      },
      {
        "status": "OK",
        "metricKey": "new_bugs",
        "comparator": "GT",
        "errorThreshold": "0",
        "actualValue": "0"
      },
      {
        "status": "ERROR",
        "metricKey": "new_duplicated_lines_density",
        "comparator": "GT",
        "errorThreshold": "3",
        "actualValue": "5.8"
      }
    ]
  }
}
```

**Reading the response:**
- `new_coverage` failed: actual 65.2% is below the required 80% minimum
- `new_bugs` passed: 0 new bugs, gate requires 0
- `new_duplicated_lines_density` failed: 5.8% duplication exceeds 3% threshold
