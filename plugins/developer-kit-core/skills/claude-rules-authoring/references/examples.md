# Rule Examples

One complete example per rule shape. Copy the closest one and adapt it to the
target codebase. All examples use real symbols/paths to model the expected level
of specificity — generic placeholders are a smell in an actual rule.

## Table of Contents

- [Shape A — Policy / safety rule (with frontmatter)](#shape-a--policy--safety-rule)
- [Shape B — Convention rule (no frontmatter)](#shape-b--convention-rule)
- [Shape C — Pattern / guide rule](#shape-c--pattern--guide-rule)

---

## Shape A — Policy / safety rule

Filename: `00-no-commits-push.md`. Short, imperative, always loaded.

```markdown
---
description: Prevent direct commits and pushes to git
globs: "**/*"
alwaysApply: true
priority: 00
---

# No Direct Git Commits and Pushes

## Rule

- **NEVER execute `git commit` or `git push` commands directly.**
- Always ask the human user to perform commits and pushes.
- Inform the user about the changes ready to be committed.

## Rationale

Direct commits and pushes bypass human review and can introduce errors to the
shared remote repository. Human oversight is essential for repository integrity.

## Workflow

1. After completing changes, tell the user they are ready and list modified files.
2. Wait for the user to explicitly approve and execute the commit/push.
3. Provide a clear commit message suggestion if asked.
```

A scoped variant: `00a-git-file-moves.md` adds an `## Exceptions` section
("plain `mv` is acceptable ONLY for untracked files") instead of a workflow.

---

## Shape B — Convention rule

Filename: `02-typescript.md`. No frontmatter; domain sections; references the
real config file. Note how it cites exact compiler flags rather than "use strict
mode generally".

```markdown
# TypeScript Best Practices

## Configuration

- **Target** ES2022, module `esnext`, `strictPropertyInitialization: false`
  (see `tsconfig.base.json`).
- Single quotes for strings (Prettier); 2-space indent (EditorConfig).
- `strict: true`, `noImplicitOverride: true`, `experimentalDecorators: true`.

## Type Conventions

- Prefer `interface` for DTO contracts, `type` for unions/intersections.
- ❌ explicit `any` → ✅ a precise type or `unknown` with narrowing.
- Declare return types of public functions, especially NestJS services.

## Code Organization

- Barrel files (`index.ts`) export everything public for the module.
- Path aliases live in `tsconfig.base.json` under `compilerOptions.paths`.
```

The key move: each bullet names a concrete file, flag, or alias from the repo,
and the ✅/❌ pair makes the preferred form unmistakable.

---

## Shape C — Pattern / guide rule

Filename: `06-new-api-guide.md` or `04-nestjs-modules.md`. Overview + structure
tree + procedure + worked example. Used for multi-step "how we build X here"
knowledge that an agent would otherwise re-derive each time.

```markdown
# NestJS — Modules

## Overview

Each `libs/server/{feature}-feature` is a self-contained NestJS module wired via
`forRootAsync`. New features follow this anatomy exactly.

## Structure

\`\`\`
src/lib/
  controllers/      → {entity}.controller.ts + index.ts
  services/         → {entity}.service.ts + {entity}.service.spec.ts + index.ts
  interfaces/       → local DTOs (non-shared) + index.ts
  test/             → db-seed*.util.ts
  {module-name}.module.ts
\`\`\`

## Procedure

1. Generate the lib with the Nx generator (see `19-nx-library-generator.md`).
2. Export module options with an injection token:

   \`\`\`ts
   export const ORDERS_MODULE_OPTIONS = 'ORDERS_MODULE_OPTIONS';
   export const InjectOrdersModuleOptions = () => Inject(ORDERS_MODULE_OPTIONS);
   \`\`\`

3. Register controllers/services and re-export the public surface from `index.ts`.

> Related: see `04-nestjs-controllers.md`, `04-nestjs-services.md`.
```

The structure tree and the exact injection-token naming are what make this rule
worth its tokens: the agent reproduces the house pattern instead of inventing one.
