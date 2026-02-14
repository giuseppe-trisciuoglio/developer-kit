# CLAUDE.md Templates

## Key Principles

- **Concise**: Dense, human-readable content; one line per concept when possible
- **Actionable**: Commands should be copy-paste ready
- **Project-specific**: Document patterns unique to this project, not generic advice
- **Current**: All info should reflect actual codebase state

---

## Recommended Sections

Use only the sections relevant to the project. Not all sections are needed.

### Commands

Document the essential commands for working with the project.

```markdown
## Commands

| Command | Description |
|---------|-------------|
| `<cmd>` | Install dependencies |
| `<cmd>` | Start development server |
| `<cmd>` | Production build |
| `<cmd>` | Run tests |
| `<cmd>` | Lint/format code |
```

### Architecture

Describe the project structure so Claude understands where things live.

```markdown
## Architecture

```
<tree-structure>
```

# <directory-name>

# <directory-name>
```
```

### Key Files

List important files that Claude should know about.

```markdown
## Key Files

- `<path>` - <purpose>
- `<path>` - <purpose>
```

### Code Style

Document project-specific coding conventions.

```markdown
## Code Style

- <convention 1>
- <convention 2>
```

### Environment

Document required environment variables and setup.

```markdown
## Environment

Required:
- `<VAR>` - <purpose>

Setup:
- <setup steps>
```

### Testing

Document testing approach and commands.

```markdown
## Testing

- <approach 1>
- <approach 2>
```

### Gotchas

Document non-obvious patterns, quirks, and warnings.

```markdown
## Gotchas

- <gotcha 1>
- <gotcha 2>
```

### Workflow

Document development workflow patterns.

```markdown
## Workflow

- <workflow pattern>
```

---

## Template: Project Root (Minimal)

```markdown
# <Project Name>

## Commands

| Command | Description |
|---------|-------------|
| `<cmd>` | <description> |

## Architecture

```
<tree>
```

## Gotchas

- <gotcha>
```

---

## Template: Project Root (Comprehensive)

```markdown
# <Project Name>

## Commands

| Command | Description |
|---------|-------------|
| `<cmd>` | <description> |

## Architecture

```
<tree>
```

## Key Files

- `<path>` - <purpose>

## Code Style

- <convention>

## Environment

- `<VAR>` - <purpose>

## Testing

- <approach>

## Gotchas

- <gotcha>
```

---

## Template: Package/Module

For packages within a monorepo or distinct modules.

```markdown
# <Package/Module Name>

## Usage

```<language>
<example>
```

## Key Exports

- `<export>` - <purpose>

## Dependencies

- <dependency>

## Notes

- <note>
```

---

## Template: Monorepo Root

```markdown
# <Monorepo Name>

## Packages

| Package | Description | Path |
|---------|-------------|------|
| `<name>` | <description> | `<path>` |

## Commands

| Command | Description |
|---------|-------------|
| `<cmd>` | <description> |

## Cross-Package Patterns

- <pattern>
```

---

## Update Principles

When updating any CLAUDE.md:

1. **Be specific**: Use actual file paths, real commands from this project
2. **Be current**: Verify info against the actual codebase
3. **Be brief**: One line per concept when possible
4. **Be useful**: Would this help a new Claude session understand the project?
