# SonarQube MCP — LLM Tool Selection Guide

Optimized context for LLM agents to select the right MCP tool, map parameters, and interpret responses efficiently.

## Tool Selection Decision Tree

```
User wants to...
├── check if code is ready to merge/deploy
│   └── get_project_quality_gate_status (projectKey + pullRequest)
│
├── find issues in a project or PR
│   └── search_sonar_issues_in_projects (projects + severities + pullRequestId)
│
├── analyze code before committing
│   └── analyze_code_snippet (projectKey + fileContent + language)
│
├── understand why a rule flagged code
│   └── show_rule (key: "<language>:<rule-id>")
│
├── get project health metrics (coverage, bugs, etc.)
│   └── get_component_measures (projectKey + metricKeys)
│
└── accept or dismiss a specific issue
    └── change_sonar_issue_status (key + status + comment)
```

## Tool Quick Reference

### get_project_quality_gate_status

**Purpose:** Verify if a project passes its defined quality gate.

**Required:** one of `projectKey`, `projectId`, or `analysisId`

**Optional:** `pullRequest` (string, PR number as string)

> Note: No `branch` parameter exists on this tool. Without `pullRequest` or `analysisId`, the default branch status is returned.

**Key output fields:**
- `projectStatus.status` — `"OK"` or `"ERROR"` (or `"WARN"` in older versions)
- `projectStatus.conditions[]` — array of conditions, each with `metricKey`, `status`, `actualValue`, `errorThreshold`, `comparator`

**When to use:** Before merge decisions, deployment gates, release checks.

---

### search_sonar_issues_in_projects

**Purpose:** Find and filter issues across projects.

**All parameters optional** — omit `projects` to search all accessible projects.

**Key parameters:**
- `projects` — `["project-key-1", "project-key-2"]`
- `severities` — `["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]`
- `pullRequestId` — string (PR number), not integer
- `p` — page number (start at 1)
- `ps` — page size (default: 100, max: 500)

**Key output fields per issue:**
- `key` — unique issue ID (used in `change_sonar_issue_status`)
- `rule` — rule key (used in `show_rule`); note: field is named `ruleKey` in `analyze_code_snippet` responses
- `severity` — legacy severity value
- `status` — current issue status (display only; use `change_sonar_issue_status` to change it)
- `message` — human-readable description
- `attribute` — clean code attribute
- `category` — `SECURITY`, `RELIABILITY`, `MAINTAINABILITY`
- `component` — file path within the project
- `startLine`, `endLine` — location in the file

**Pagination:** Check `paging.total` and `paging.pageSize` in response; iterate `p` while `paging.pageIndex * paging.pageSize < paging.total`.

**When to use:** Issue triage, PR review, sprint cleanup, security audits.

---

### analyze_code_snippet

**Purpose:** Run SonarQube analysis on a raw code string without CI.

**Required:** `projectKey`, `fileContent` (full file content as string)

**Optional:** `language` (always specify for best accuracy), `codeSnippet` (narrow results to a sub-range of the file)

**Language values:** `javascript`, `typescript`, `python`, `java`, `go`, `php`, `cs` (C#), `cpp`, `kotlin`, `ruby`, `scala`, `swift`

**Key output fields per issue:**
- `ruleKey` — use with `show_rule` for explanation (note: `rule` in `search_sonar_issues_in_projects`, `ruleKey` here)
- `severity` — issue severity
- `cleanCodeAttribute` — clean code attribute
- `impacts` — object mapping quality dimension to severity level
- `startLine` — line number in the file
- `quickFixes` — boolean, whether a quick fix is available

**Limitations:**
- Analyzes file content in isolation, without full project context
- Some rules require cross-file analysis and will not fire
- Results may differ slightly from full CI analysis

**When to use:** Shift-left review, pre-commit checks, code review assistance.

---

### show_rule

**Purpose:** Retrieve full documentation for a SonarQube rule.

**Required:** `key` in format `<language>:<rule-id>`

**Language prefixes:** `java`, `javascript`, `typescript`, `python`, `go`, `php`, `cs`, `cpp`, `kotlin`, `ruby`

**Examples:** `java:S2068`, `typescript:S1082`, `python:S5659`, `go:S4036`

**Key output fields:**
- `name` — human-readable rule name
- `type` — `BUG`, `VULNERABILITY`, `CODE_SMELL`, `SECURITY_HOTSPOT`
- `severity` — legacy severity
- `description` — full explanation of the risk and rationale
- `tags` — standards: `cwe`, `owasp-a1`, `sans-top25`, `cert`
- `remediationEffort` — time estimate for fix (e.g., `"30min"`)
- `codeExamples` — array with `noncompliant` and `compliant` code examples

**When to use:** After finding an unfamiliar rule key, before dismissing an issue, for developer education.

---

### get_component_measures

**Purpose:** Retrieve specific metrics for a project, directory, or file.

**Required:** `projectKey` (project key), `metricKeys` (array)

**Optional:** `pullRequest` (string, for PR-scoped metrics)

> Note: No `branch` parameter exists on this tool.

**Common metric key groups:**

*Overall health:* `bugs`, `vulnerabilities`, `code_smells`, `coverage`, `duplicated_lines_density`, `ncloc`

*Ratings:* `reliability_rating`, `security_rating`, `sqale_rating`

*New code only:* `new_bugs`, `new_vulnerabilities`, `new_coverage`, `new_duplicated_lines_density`

*Complexity:* `complexity`, `cognitive_complexity`

**When to use:** Project health dashboards, sprint reviews, release readiness checks.

---

### change_sonar_issue_status

**Purpose:** Update the status of a specific issue.

**Required:** `key` (issue key from `search_sonar_issues_in_projects` response field `key`), `status`

**Valid status values:** `falsepositive`, `accept`, `reopen`

**Optional:** `comment` (strongly recommended — always document the reason)

**Requires:** SonarQube user permissions to change issue status.

**When to use:** Issue triage sign-off, false positive management, technical debt acknowledgment.

> Never call this tool without explicit user confirmation and a documented reason.

---

## Common Agent Patterns

### Pattern 1: Gate + Issues (PR review)

```
1. get_project_quality_gate_status (projectKey, pullRequest)
2. If status == "ERROR":
   a. search_sonar_issues_in_projects (projects, pullRequestId)
   b. Group by category, present to user
   c. For unfamiliar rules: show_rule (key)
```

### Pattern 2: Shift-Left (pre-commit)

```
1. analyze_code_snippet (projectKey, fileContent, language)
2. For each finding:
   a. show_rule (ruleKey) if severity >= HIGH or rule is unfamiliar
3. Present findings, propose fixes
4. Wait for user to apply fixes before commit
```

### Pattern 3: Project Triage

```
1. search_sonar_issues_in_projects (projects, severities: ["BLOCKER"])
2. For each BLOCKER: show_rule (rule) to get remediation
3. Repeat for HIGH, MEDIUM
4. get_component_measures (projectKey, metricKeys: [...ratings]) for overall health
```

### Pattern 4: Release Gate Check

```
1. get_project_quality_gate_status (projectKey)
2. get_component_measures (projectKey, metricKeys: ["bugs", "vulnerabilities", "coverage"])
3. Report combined gate + metrics summary
```

## Parameter Mapping Cheatsheet

| User Says | Tool | Key Parameter |
|---|---|---|
| "project my-app" | any | `projectKey: "my-app"` |
| "PR #234" | quality gate / search | `pullRequest: "234"` / `pullRequestId: "234"` |
| "on main branch" | quality gate | no branch param; omit `pullRequest` to get default branch |
| "critical issues" | search | `severities: ["BLOCKER", "HIGH"]` |
| "rule java:S2068" | show_rule | `key: "java:S2068"` |
| "issue AY1234" | change_status | `key: "AY1234"` |
| "TypeScript code" | analyze_snippet | `language: "typescript"` |
| "mark as false positive" | change_status | `status: "falsepositive"` |
| "accept as debt" | change_status | `status: "accept"` |

## SonarQube Server vs SonarCloud Differences

| Feature | SonarQube Server | SonarCloud |
|---|---|---|
| Project key format | Usually short slug | `<org>_<repo>` (e.g., `my-org_my-repo`) |
| PR analysis | Supported | Supported |
| Organization parameter | Not applicable | Required for some APIs |
| `analysisId` | Available | Available |
| Branch analysis | Supported | Supported |

If the user's project key contains an underscore and appears to follow `org_repo` format, it is likely a SonarCloud project.
