# Language-Specific Cleanup Patterns

Reference for language-specific formatter commands, import ordering, and search patterns.

## Formatters & Linters

| Language | Format | Lint |
|----------|--------|------|
| Java | `./mvnw spotless:apply` | `./mvnw checkstyle:check spotless:check` |
| TypeScript | `npm run format` / `npx prettier --write` | `npm run lint` / `npx eslint --fix` |
| Python | `black .` / `ruff format` | `ruff check . && black --check .` |

## Import Ordering

**Java**: `java.*` → `jakarta.*`/`javax.*` → third-party → project imports  
**TypeScript**: external libraries → internal absolute (`@/...`) → internal relative (`./...`)

## Common Search Patterns

Use Grep to find technical debt:

```bash
# JavaScript/TypeScript
grep -rn "console.log" --include="*.ts" --include="*.tsx" [files]
grep -rn "// DEBUG:" --include="*.ts" [files]

# Java
grep -rn "System.out.println" --include="*.java" [files]

# Python
grep -rn "print(" --include="*.py" [files]
```
