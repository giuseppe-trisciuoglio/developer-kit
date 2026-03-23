# SonarQube MCP Best Practices

Workflows and patterns for integrating SonarQube quality checks into the development lifecycle.

## PR Quality Gate Workflow

The recommended workflow for checking code quality before merging a pull request.

### Step 1: Trigger PR Analysis

SonarQube analyzes PRs automatically when integrated with CI/CD. After CI runs, check the gate:

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "my-service",
    "pullRequest": "<pr-number>"
  }
}
```

### Step 2: Evaluate Gate Status

If `status: "OK"` → safe to proceed with merge review.

If `status: "ERROR"`:
1. Extract failing conditions from the `conditions` array
2. For each failing condition, identify the metric and gap (actual vs threshold)
3. Use `search_sonar_issues_in_projects` filtered by PR to surface the specific issues

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-service"],
    "pullRequestId": "<pr-number>",
    "severities": ["BLOCKER", "HIGH", "MEDIUM"],
    "p": 1,
    "ps": 100
  }
}
```

### Step 3: Triage Issues

Group found issues by:
- **Security** (`category: SECURITY`) → highest priority
- **Reliability** (`category: RELIABILITY`) → bugs that affect behavior
- **Maintainability** (`category: MAINTAINABILITY`) → code smells

Present categorized summary to the developer before requesting changes.

### Step 4: Verify Fix

After the developer pushes fixes, re-check the quality gate using the updated PR number or trigger a new analysis via CI.

---

## Pre-Commit Analysis (Shift Left)

Catch issues before they reach the CI pipeline using `analyze_code_snippet`.

### When to Use

- Before committing new functions or classes
- When refactoring security-sensitive code
- Before adding a new external dependency integration

### Workflow

1. **Extract the snippet** — identify the function or module to analyze
2. **Specify the language** — always pass the `language` parameter for accuracy
3. **Review findings** — address CRITICAL and HIGH issues before committing
4. **Learn from rules** — use `show_rule` to understand unfamiliar findings

### Multi-Language Examples

**TypeScript (SQL injection check):**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-app",
    "fileContent":"async function getUser(id: string) {\n  const query = `SELECT * FROM users WHERE id = ${id}`;\n  return db.execute(query);\n}",
    "language": "typescript"
  }
}
```

**Java (hardcoded credentials):**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-java-app",
    "fileContent":"public class DatabaseConfig {\n  private static final String PASSWORD = \"myS3cr3t\";\n  public Connection connect() { ... }\n}",
    "language": "java"
  }
}
```

**Python (deserialization risk):**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-python-app",
    "fileContent":"import pickle\n\ndef load_session(data):\n    return pickle.loads(data)",
    "language": "python"
  }
}
```

**Go (error ignored):**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-go-service",
    "fileContent":"func readFile(path string) []byte {\n  data, _ := os.ReadFile(path)\n  return data\n}",
    "language": "go"
  }
}
```

---

## Issue Triage Workflow

Systematic approach to clearing a backlog of Sonar issues.

### Step 1: Prioritize by Severity

Always start with BLOCKER issues, then CRITICAL/HIGH:

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-project"],
    "severities": ["BLOCKER"],
    "p": 1,
    "ps": 100
  }
}
```

### Step 2: Understand Each Issue

For each unfamiliar rule, retrieve documentation:

```json
{
  "name": "show_rule",
  "arguments": {
    "key": "java:S2068"
  }
}
```

### Step 3: Fix or Document

**Fix:** Implement the recommended fix from rule documentation.

**Accept (with reason):**

```json
{
  "name": "change_sonar_issue_status",
  "arguments": {
    "key": "AY1234",
    "status": "falsepositive",
    "comment": "This pattern is safe because input is validated upstream at the API boundary."
  }
}
```

### Step 4: Verify Progress

After fixes, check the project health:

```json
{
  "name": "get_component_measures",
  "arguments": {
    "projectKey": "my-project",
    "metricKeys": ["bugs", "vulnerabilities", "code_smells", "security_rating", "reliability_rating"]
  }
}
```

---

## Continuous Quality Monitoring

For ongoing projects, establish a monitoring routine:

| Frequency | Check | Tool |
|---|---|---|
| Every PR | Quality gate status | `get_project_quality_gate_status` |
| Weekly | New BLOCKER/CRITICAL issues | `search_sonar_issues_in_projects` |
| Sprint review | Overall project health | `get_component_measures` |
| Before release | Full gate check on main | `get_project_quality_gate_status` |

---

## Security-Focused Workflow

When working on security-sensitive code (auth, payments, user data):

1. Run pre-commit analysis on every modified function
2. Check for OWASP-tagged issues after CI analysis
3. Review all `category: SECURITY` issues regardless of severity
4. Never mark security issues as `FALSE-POSITIVE` without team review

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-service"],
    "pullRequestId": "<pr-number>",
    "p": 1,
    "ps": 100
  }
}
```

Then filter the response for `"category": "SECURITY"` entries and review all of them, starting from BLOCKER.

---

## Quality Gate Failure Resolution Checklist

When a quality gate fails on a PR:

- [ ] Identify all failing conditions in `conditions` array
- [ ] Search issues filtered by PR to find root causes
- [ ] Group issues by category (Security, Reliability, Maintainability)
- [ ] Fix BLOCKER and CRITICAL/HIGH issues
- [ ] For MEDIUM/LOW: fix if quick, else document in PR description
- [ ] Re-run CI to trigger new Sonar analysis
- [ ] Re-check quality gate status after fix
- [ ] Do not merge until `status: "OK"`
