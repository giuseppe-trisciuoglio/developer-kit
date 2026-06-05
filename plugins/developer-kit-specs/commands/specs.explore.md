---
description: "Explore and investigate ideas before committing to a change. Use when: understanding current architecture, comparing approaches, clarifying requirements — before any proposal or spec is written. Output: docs/specs/{id}/exploration.md"
argument-hint: '[--lang=<framework>] [--spec <path>] <topic>'
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, TodoWrite
---

# specs.explore

Investigate the codebase before committing to a change. Reads relevant files, identifies affected areas, compares approaches, and returns a structured analysis with recommendations.

**This is investigation only — no code is written or modified.**

## Usage

```bash
# Explore a topic (standalone — result inline only)
/developer-kit-specs:specs.explore "authentication patterns in the codebase"

# Explore with a spec folder (saves to docs/specs/{id}/)
/developer-kit-specs:specs.explore --spec=docs/specs/001-add-jwt-auth "JWT token handling"

# Specify language/framework
/developer-kit-specs:specs.explore --lang=spring --spec=docs/specs/001-add-jwt-auth "JWT token handling"
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<topic>` | Yes      | Topic or feature to explore |
| `--spec`  | No       | Path to spec folder for artifact persistence |
| `--lang`  | No       | Language/framework: `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `php`, `general` |

## Output

| Mode | Output |
|------|--------|
| With `--spec` | `{spec}/exploration.md` |
| Without `--spec` | Inline result only |

## Workflow Integration

```
specs.explore → specs.brainstorm → specs.spec-to-tasks → ...
   (investigate)   (WHAT)
```

## Steps to Execute

### Step 1: Parse Request

Understand what the user wants to explore:
- Is this a new feature? Bug fix? Refactor?
- What domain does it touch?

### Step 2: Investigate the Codebase

Read relevant code:
```
INVESTIGATE:
├── Read entry points and key files
├── Search for related functionality (Grep)
├── Check existing tests (Glob)
├── Look for patterns already in use
└── Identify dependencies and coupling
```

### Step 3: Analyze Options

If multiple approaches exist, compare them:

| Approach | Pros | Cons | Complexity |
|----------|------|------|------------|
| Option A | ... | ... | Low/Med/High |
| Option B | ... | ... | Low/Med/High |

### Step 4: Persist Artifact (if `--spec` is provided)

If `--spec` is specified, write to `{spec}/exploration.md`:

```markdown
## Exploration: {topic}

### Current State
{How the system works today relevant to this topic}

### Affected Areas
- `path/to/file.ext` — {why it's affected}
- `path/to/other.ext` — {why it's affected}

### Approaches
1. **{Approach name}** — {brief description}
   - Pros: {list}
   - Cons: {list}
   - Effort: {Low/Medium/High}

2. **{Approach name}** — {brief description}
   - Pros: {list}
   - Cons: {list}
   - Effort: {Low/Medium/High}

### Recommendation
{Your recommended approach and why}

### Risks
- {Risk 1}
- {Risk 2}

### Ready for Proposal
{Yes/No — and what the user should know}
```

### Step 5: Return Result

Return the same structured analysis (inline), plus:

**Status Report:**
- **status**: `done` | `blocked` | `partial`
- **executive_summary**: 1-sentence description of what was explored and key recommendation
- **artifact**: `{spec}/exploration.md` (if `--spec` provided) or "none"
- **next_recommended**: `specs.brainstorm` (if spec provided) or `none` (if standalone)
- **risks**: risks discovered, or "None"

---

## Rules

- DO NOT modify any existing code or files
- ALWAYS read real code — never guess about the codebase
- Keep analysis CONCISE — summary, not a novel
- If you can't find enough information, say so clearly
- If the request is too vague, ask for clarification