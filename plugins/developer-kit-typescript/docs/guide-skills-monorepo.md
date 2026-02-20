# Monorepo Skills Guide

Quick reference to monorepo management skills for TypeScript/JavaScript projects.

---

## Skills Overview

| Skill                  | Purpose                                                                 |
|------------------------|-------------------------------------------------------------------------|
| **nx-monorepo**        | Nx monorepo management with generators, affected commands, Module Federation |
| **turborepo-monorepo** | Turborepo monorepo management with turbo.json, framework integration, caching |

---

## nx-monorepo

**File**: `skills/nx-monorepo/SKILL.md`

Provides comprehensive guidance for working with Nx monorepos in TypeScript/JavaScript projects. Nx is a smart build system with advanced caching, affected command execution, and powerful generators for React, Next.js, NestJS, and more.

### When to use

- Creating a new Nx workspace or initializing Nx in an existing project
- Generating applications, libraries, or components with Nx generators
- Running affected commands or executing tasks across multiple projects
- Setting up CI/CD pipelines for Nx projects
- Configuring Module Federation with React or Next.js
- Implementing NestJS backend applications within Nx
- Setting up remote caching or Nx Cloud

### Key Features

#### Workspace Creation

```bash
# Interactive setup
npx create-nx-workspace@latest

# Initialize in existing project
nx@latest init

# Specific preset
npx create-nx-workspace@latest my-workspace --preset=react
```

#### Project Generation

```bash
# React application
nx g @nx/react:app my-app

# Library
nx g @nx/react:lib my-lib
nx g @nx/js:lib my-util

# Component in lib
nx g @nx/react:component my-comp --project=my-lib

# NestJS backend
nx g @nx/nest:app my-api
```

#### Task Execution

```bash
# Affected projects only
nx affected -t lint test build

# All projects
nx run-many -t build

# Specific projects
nx run-many -t test -p=my-app,my-lib

# Single project target
nx run my-app:build

# Dependency graph
nx graph
```

#### Module Federation

```bash
# Generate remote (micro-frontend)
nx g @nx/react:remote checkout --host=dashboard

# Generate host
nx g @nx/react:host dashboard
```

### Project Configuration

Each project has a `project.json` defining targets, executor, and configurations:

```json
{
  "name": "my-app",
  "projectType": "application",
  "sourceRoot": "apps/my-app/src",
  "targets": {
    "build": {
      "executor": "@nx/react:webpack",
      "outputs": ["{workspaceRoot}/dist/apps/my-app"],
      "configurations": {
        "production": { "optimization": true }
      }
    },
    "test": {
      "executor": "@nx/vite:test"
    }
  },
  "tags": ["type:app", "scope:frontend"]
}
```

### CI/CD Setup

```yaml
# .github/workflows/ci.yml
- run: npx nx affected -t lint --parallel
- run: npx nx affected -t test --parallel
- run: npx nx affected -t build --parallel
```

### Reference Files

| Topic | Reference File |
|-------|----------------|
| Workspace setup, basic commands | [references/basics.md](../skills/nx-monorepo/references/basics.md) |
| Generators (app, lib, component) | [references/generators.md](../skills/nx-monorepo/references/generators.md) |
| React, Next.js, Expo patterns | [references/react.md](../skills/nx-monorepo/references/react.md) |
| NestJS backend patterns | [references/nestjs.md](../skills/nx-monorepo/references/nestjs.md) |
| TypeScript packages | [references/typescript.md](../skills/nx-monorepo/references/typescript.md) |
| CI/CD (GitHub, CircleCI, etc.) | [references/ci-cd.md](../skills/nx-monorepo/references/ci-cd.md) |
| Caching, affected, advanced | [references/advanced.md](../skills/nx-monorepo/references/advanced.md) |

### Best Practices

- **Always use `nx affected` in CI** to only test/build changed projects
- **Organize libs by domain/business capability**, not by technical layer
- **Use tags consistently** (`type:app|lib`, `scope:frontend|backend|shared`)
- **Prevent circular dependencies** by configuring `workspaceLayout` boundaries in `nx.json`
- **Enable remote caching** with Nx Cloud for team productivity
- **Leverage generators** instead of manual file creation for consistency

---

## turborepo-monorepo

**File**: `skills/turborepo-monorepo/SKILL.md`

Provides comprehensive guidance for working with Turborepo monorepos in TypeScript/JavaScript projects. Turborepo is a high-performance build system written in Rust that optimizes task execution through intelligent caching, parallelization, and dependency graph analysis.

### When to use

- Creating a new Turborepo workspace or initializing in an existing project
- Configuring `turbo.json` tasks with proper dependencies and outputs
- Setting up Next.js or NestJS applications in a monorepo
- Configuring Vitest or Jest testing pipelines
- Implementing CI/CD workflows
- Setting up remote caching or Vercel Remote Cache
- Optimizing build times and cache hit ratios

### Key Features

#### Workspace Creation

```bash
# Using pnpm (recommended)
pnpm create turbo@latest my-workspace

# Initialize in existing project
pnpm add -D -w turbo
```

#### turbo.json Configuration

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    }
  }
}
```

#### Task Execution

```bash
# Run task for all packages
turbo run build

# Run multiple tasks
turbo run lint test build

# Run for specific package
turbo run build --filter=web

# Affected tests
turbo run test --filter=[HEAD^]
```

#### Framework Integration

**Next.js:**
```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_*"]
    }
  }
}
```

**NestJS:**
```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "start:dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Task Properties Reference

| Property | Description | Example |
|----------|-------------|---------|
| `dependsOn` | Tasks that must complete first | `["^build"]` - dependencies first |
| `outputs` | Files/folders to cache | `["dist/**"]` |
| `inputs` | Files for cache hash | `["src/**/*.ts"]` |
| `env` | Environment variables affecting hash | `["DATABASE_URL"]` |
| `cache` | Enable/disable caching | `true` or `false` |
| `persistent` | Long-running task | `true` for dev servers |

### Filter Syntax

| Filter | Description |
|--------|-------------|
| `web` | Only web package |
| `web...` | web + all dependencies |
| `...web` | web + all dependents |
| `...web...` | web + deps + dependents |
| `[HEAD^]` | Packages changed since last commit |
| `./apps/*` | All packages in apps/ |

### Reference Files

| Topic | Reference File |
|-------|----------------|
| turbo.json template | [references/turbo.json](../skills/turborepo-monorepo/references/turbo.json) |
| Next.js integration | [references/nextjs-config.md](../skills/turborepo-monorepo/references/nextjs-config.md) |
| NestJS integration | [references/nestjs-config.md](../skills/turborepo-monorepo/references/nestjs-config.md) |
| Vitest/Jest/Playwright | [references/testing-config.md](../skills/turborepo-monorepo/references/testing-config.md) |
| GitHub/CircleCI/GitLab CI | [references/ci-cd.md](../skills/turborepo-monorepo/references/ci-cd.md) |
| Package configurations | [references/package-configs.md](../skills/turborepo-monorepo/references/package-configs.md) |

### Best Practices

#### Performance Optimization

1. **Use specific outputs** - Only cache what's needed
2. **Fine-tune inputs** - Exclude files that don't affect output
3. **Transit nodes** - Enable parallel type checking
4. **Remote cache** - Share cache across team/CI
5. **Package configurations** - Customize per-package behavior

#### Task Organization

- **Independent tasks** - No `dependsOn`: lint, format, spellcheck
- **Build tasks** - `dependsOn: ["^build"]`: build, compile
- **Test tasks** - `dependsOn: ["build"]`: test, e2e
- **Dev tasks** - `cache: false, persistent: true`: dev, watch

---

## Technology Stack

- **TypeScript**: 5.x+
- **Node.js**: 18+
- **Nx**: 17+ for Nx monorepo
- **Turborepo**: 2.x+ for Turborepo
- **Package Managers**: pnpm (recommended), npm, yarn

---

**Note**: For complete patterns and examples, see the respective skill files:
- `skills/nx-monorepo/SKILL.md`
- `skills/turborepo-monorepo/SKILL.md`
