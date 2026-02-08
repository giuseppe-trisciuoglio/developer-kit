---
allowed-tools: Read, Write, Bash, Edit, Grep, Glob
argument-hint: "[review-type] [file/directory-path] [options]"
description: Provides comprehensive TypeScript monorepo code review for Nx workspaces including NestJS backend, React web, and React Native mobile apps. Use when reviewing architecture, boundaries, security, performance, CI/CD and Nx-specific practices.
model: inherit
---

# TypeScript Monorepo Code Review - Nx / NestJS / React / React Native

## Overview

Provides comprehensive TypeScript monorepo code review for Nx workspaces including NestJS backend, React web, and React
Native mobile apps. Use when reviewing architecture, boundaries, security, performance, CI/CD and Nx-specific practices.

## Usage

```
/devkit.typescript.code-review $ARGUMENTS
```

## Arguments

| Argument     | Description                              |
|--------------|------------------------------------------|
| `$ARGUMENTS` | Combined arguments passed to the command |

## Examples

```bash
/devkit.typescript.code-review example-input
```

## Current Context

- **Current Git Branch**: !`git branch --show-current`
- **Git Status**: !`git status --porcelain`
- **Recent Commits**: !`git log --oneline -5`
- **Modified Files**: !`git diff --name-only HEAD~1`
- **Nx Affected Projects**: !
  `[ -f nx.json ] && npx nx show projects --affected --base=HEAD~1 2>/dev/null || echo "Nx not detected"`

## Review Configuration

The review will analyze: **$ARGUMENTS**

**Available review types:**

- `full` - Complete 360° review (default)
- `security` - Focus on vulnerabilities, secrets, access control
- `performance` - Build/runtime and resource usage
- `architecture` - Boundaries, module ownership, dependency graph
- `testing` - Tests, coverage, e2e strategies
- `ci` - CI/CD, caching and Nx Cloud usage
- `best-practices` - TypeScript/Monorepo best practices

## Phase 1: Identify Review Scope and Workspace

### 1.1 Detect scope

IF "$1" IS PROVIDED
THEN Analyze specific file or project: $ARGUMENTS
ELSE Analyze affected and recently modified projects in workspace
ENDIF

### 1.2 Base Workspace Metrics

- **Nx Workspace**: nx.json, workspace.json or project.json layout
- **Packages Layout**: apps/, libs/, packages/ (check for custom layout)
- **Node/TS Versions**: Check engines and package.json
- **Build System**: Nx builders, Vite, Metro, Webpack
- **Package Manager**: npm / yarn / pnpm (pnpm recommended for monorepos)

## Phase 2: Monorepo & Nx Best Practices

### 2.1 Project Boundaries

- Verify clear separation apps vs libs
- Enforce tags and implicitDependencies in project.json and nx.json
- Prefer small, focused, reusable libs (feature, ui, util, data)
- Check for barrel exports and public-api.ts in libs
- Validate path mappings (tsconfig.base.json -> paths)

### 2.2 Dependency Graph and Affected Changes

- Use `npx nx dep-graph --file=depgraph.svg` to visualize
- Ensure libs have minimal incoming dependencies
- Identify circular dependencies and large fan-in nodes
- Validate proper use of buildable/libs-with-build-targets where needed

### 2.3 Workspace Tooling

- nx.json: targetDefaults, implicitDependencies, cacheableOperations
- CI cache: Nx Cloud or local caching configured
- Script hygiene: package.json scripts use nx run-commands or nx commands

## Phase 3: Backend (NestJS) Review

### 3.1 Project Structure & Modules

- Prefer domain/feature libs for core business logic, keep NestJS adapters thin
- Modules should be cohesive and small; avoid god modules
- Use constructor injection, avoid dynamic module misuse

### 3.2 DTOs, Validation, Pipes, Guards

- Use class-validator and class-transformer on DTOs; prefer readonly properties
- Validate DTOs globally with ValidationPipe and whitelist=true
- Implement Guards, Interceptors, ExceptionFilters for cross-cutting concerns

### 3.3 Database & Repositories

- Check TypeORM/Prisma/Sequelize usage consistency across services
- Prevent raw string concatenation in queries, prefer parameterized queries or Prisma client
- Use repository pattern in libs to decouple from framework

### 3.4 Security (NestJS)

- Properly configure CORS, CSP, security headers
- Secure cookies, tokens, and refresh token rotation if applicable
- Validate JWT usage, revocation strategy, and token scopes

## Phase 4: Frontend (React / React Native) Review

### 4.1 Component Libraries & Reuse

- Component libs (ui) should be framework-agnostic where possible
- Use storybook or similar for visual regression and component catalog
- Ensure shared hooks and utilities live in libs and avoid app duplication

### 4.2 State Management & Data Fetching

- Prefer local state in components, lift state to libs as needed
- Validate consistent data fetching strategy (React Query, SWR, or custom)
- Check for serialization issues when sharing code between web and native

### 4.3 Performance & Native Integration

- Optimize bundle size (route-based code splitting, lazy loading)
- For RN, validate Metro config, native module usage, and Hermes support
- Check for heavy synchronous operations on UI thread

## Phase 5: Build, CI, and Release

### 5.1 Nx Build Targets

- Verify build/test/lint targets defined for each project
- Use `nx affected:test` and `nx affected:build` in CI
- Prefer buildable libs for publishable packages

### 5.2 CI/CD and Caching

- Check Nx Cloud or remote caching configuration
- Ensure CI uses cacheableOperations and restores cache correctly
- Use incremental builds and selective E2E execution for speed

### 5.3 Release Strategy

- Check versioning strategy (independent vs fixed) if publishing packages
- Validate changelog, automated release pipeline, and tagging

## Phase 6: Security and Vulnerability Assessment

- Run dependency audits (npm audit, yarn audit, pnpm audit) and Snyk/Dependabot
- Check for hardcoded secrets, API keys, and unsafe env handling
- Review usage of eval, insecure deserialization, SSRF vectors
- Cross-origin and XSS protections in React apps (sanitize inputs, escape output)

## Phase 7: Testing Strategy

- Unit tests: Jest for backend and frontend (ts-jest / babel-jest), aim for fast, isolated tests
- Integration tests: Web API integration (supertest / Pact) and DB with Testcontainers (if applicable)
- E2E: Cypress or Playwright for web, Detox or Appium for React Native
- CI: Run affected tests first, full test suite on main branch

## Phase 8: Linting, Formatting, and Type Safety

- ESLint with project references and overrides for apps/libs
- Strict TypeScript compiler options (noImplicitAny, strictNullChecks)
- Prettier consistent formatting; pre-commit hooks (lint-staged, husky)
- Validate path aliases match tsconfig and build tooling

## Phase 9: Observability and Runtime

- Logging standardization (pino/winston) and correlation IDs
- Metrics and tracing (OpenTelemetry, Prometheus exporters)
- Health checks and graceful shutdowns for NestJS services

## Phase 10: Final Review Report

### Critical Issues (P0 - Fix Immediately)

- Secrets checked into repo, open auth bypass, critical dependency vulnerability
- Production-breaking build or release pipeline failure

### High Priority (P1 - Next Release)

- Circular dependencies in libs, large monolithic libs that block CI
- Missing tests for public API of shared libs
- Performance regressions and large bundles

### Medium Priority (P2 - Next Sprint)

- Inconsistent linting/config mismatches
- Minor architectural refactors to split oversized libs

### Low Priority (P3 - Backlog)

- Cosmetic naming, docs, README improvements

## Quality Metrics

- Unit Test Target: > 80% for critical libs
- Integration Test Target: > 60% for services
- CI Time: keep fast feedback loops (< 10m for affected changes)
- Bundle Size Targets: enforce budgets per app

## Recommended Actions

1. Immediate: Remove secrets, patch critical vulnerabilities
2. Short term: Add strict TS rules, centralize shared libs, enable Nx Cloud
3. Next sprint: Break down large libs, add component catalog and e2e stability
4. Backlog: Continuous improvement and technical debt reduction

## Integrated Support Tools

- Nx (affected, dep-graph), Nx Cloud (caching)
- SonarQube / CodeQL for static analysis
- Snyk / Dependabot for dependency scanning
- Jest, Cypress / Playwright, Detox for tests
- Storybook for UI components

---

## Execution Instructions

**Agent Selection**: To execute this code review, use the following agent with fallback:

- Primary: `developer-kit-typescript:typescript-software-architect-review`
- If not available: `developer-kit:typescript-software-architect-review` fallback to
  `developer-kit:general-code-reviewer`, if not available use `general-purpose`

**Run context**:

- Use `npx nx show projects --affected --base=HEAD~1` to limit scope (only if Nx workspace detected)
- Provide `$1` as `full` or `security` etc., and optional path to a project or file
