# SonarQube Severity Levels Reference

Complete reference for Sonar severity levels, impact categories, and clean code attributes.

## Legacy Severity Levels

The traditional SonarQube severity model used five levels:

| Severity | Priority | Action Required |
|---|---|---|
| `BLOCKER` | Critical — must fix immediately | Block merge/deployment; fix before any release |
| `CRITICAL` | High — fix in current sprint | Address before merging to main |
| `MAJOR` | Medium — schedule for near term | Fix in next sprint or iteration |
| `MINOR` | Low — fix when convenient | Address in routine maintenance |
| `INFO` | Informational | Review and document if accepted |

## New Severity Model (SonarQube 10+)

Newer versions use a Clean Code taxonomy with **impact** (severity on quality) and **likelihood** dimensions.

### Impact Categories

**HIGH** — Significant negative effect; must be addressed promptly
**MEDIUM** — Moderate effect; should be scheduled for resolution
**LOW** — Minor effect; can be deferred to routine maintenance

### Quality Dimensions

| Dimension | Description | Affected By |
|---|---|---|
| `SECURITY` | Resistance to attack and data breaches | Vulnerabilities, hotspots |
| `RELIABILITY` | Code runs as expected without failures | Bugs, error handling |
| `MAINTAINABILITY` | Ease of change and understanding | Code smells, complexity |

### Clean Code Attributes

Issues are also tagged with a clean code attribute explaining why the code is problematic:

| Attribute | Meaning |
|---|---|
| `CONVENTIONAL` | Does not follow established conventions |
| `FORMATTED` | Poor formatting affecting readability |
| `IDENTIFIABLE` | Poor naming or identification |
| `CLEAR` | Logic is hard to understand |
| `LOGICAL` | Contains logical errors |
| `COMPLETE` | Missing error handling or validation |
| `EFFICIENT` | Performance or resource inefficiency |
| `FOCUSED` | Does more than it should |
| `MODULAR` | Poor separation of concerns |
| `TESTED` | Lacks tests |
| `LAWFUL` | License or legal compliance issue |
| `TRUSTWORTHY` | Security or trust concern |

## Filtering by Severity in MCP Tools

**Use ONLY these values in the `severities` API parameter** for `search_sonar_issues_in_projects`:

```json
{
  "severities": ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]
}
```

> Important: The legacy labels `CRITICAL`, `MAJOR`, `MINOR` may appear in display text and older Sonar documentation, but they are **not valid filter values** for the `severities` API parameter. `CRITICAL` → use `HIGH`, `MAJOR` → use `MEDIUM`, `MINOR` → use `LOW`.

## Triage Decision Matrix

Use this matrix to decide how to handle each issue:

| Severity | Action |
|---|---|
| BLOCKER | Fix immediately — do not merge until resolved |
| CRITICAL / HIGH | Fix before merging to main branch |
| MAJOR / MEDIUM | Add to backlog with defined deadline |
| MINOR / LOW | Fix in routine cleanup or document as accepted debt |
| INFO | Review and close if informational only |

## Issue Statuses for `change_sonar_issue_status`

The `key` parameter is the issue's `key` field from `search_sonar_issues_in_projects`.

| Status Value | When to Use |
|---|---|
| `falsepositive` | Issue flagged by Sonar is not actually a problem in this context |
| `accept` | Issue acknowledged but accepted as technical debt (replaces legacy `WONT-FIX`) |
| `reopen` | Reset issue to open state |

> Always require explicit user confirmation before changing issue status. Document the reason in the `comment` field.

## Security Rule Tags

Security-related rules are tagged with industry standard references:

| Tag | Standard |
|---|---|
| `owasp-a1` through `owasp-a10` | OWASP Top 10 |
| `cwe` | Common Weakness Enumeration |
| `sans-top25` | SANS Top 25 Most Dangerous Software Errors |
| `cert` | CERT Secure Coding Standards |
| `pci-dss` | Payment Card Industry Data Security Standard |

Use `show_rule` with the rule key to see all tags and their implications.

## Example Issue Response

```json
{
  "key": "AY1234",
  "rule": "java:S2068",
  "project": "payment-service",
  "component": "src/main/java/PaymentService.java",
  "severity": "BLOCKER",
  "status": "OPEN",
  "message": "Remove this hard-coded password",
  "attribute": "TRUSTWORTHY",
  "category": "SECURITY",
  "startLine": 45,
  "endLine": 45,
  "created": "2025-01-15T10:30:00Z"
}
```

**Reading this response:**
- `severity: BLOCKER` + `category: SECURITY` → must fix before any release
- `rule: java:S2068` → use `show_rule` with key `java:S2068` to get remediation guidance
- `attribute: TRUSTWORTHY` → clean code violation related to security trustworthiness
