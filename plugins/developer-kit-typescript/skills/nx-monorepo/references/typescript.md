# TypeScript Packages Reference

## TypeScript Library Setup

### Create Buildable Library

```bash
# Basic buildable library
nx g @nx/js:lib utils --buildable

# With directory
nx g @nx/js:lib date-fns --directory=libs/shared/utils

# With import path (publishable)
nx g @nx/js:lib logger --importPath=@myorg/logger
```

### Publishable Package

```bash
# Publishable library
nx g @nx/js:lib my-package --publishable --importPath=@myorg/my-package

# With version configuration
nx g @nx/js:lib my-package --publishable --importPath=@myorg/my-package
```

## Package Configuration

### Buildable Library package.json

For buildable libraries, configure `package.json` with proper exports:

```json
{
  "name": "@acme/pkg1",
  "version": "0.0.1",
  "type": "commonjs",
  "exports": {
    "./package.json": "./package.json",
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    }
  }
}
```

### project.json for Buildable Lib

```json
{
  "name": "utils",
  "projectType": "library",
  "sourceRoot": "libs/utils/src",
  "targets": {
    "build": {
      "executor": "@nx/js:tsc",
      "outputs": ["{workspaceRoot}/dist/libs/utils"],
      "options": {
        "assets": ["libs/utils/*.md"],
        "main": "libs/utils/src/index.ts",
        "tsConfig": "libs/utils/tsconfig.lib.json"
      }
    },
    "test": {
      "executor": "@nx/jest:jest"
    },
    "lint": {
      "executor": "@nx/linter:eslint"
    }
  }
}
```

### Non-Buildable Library

For libraries that don't need compilation (consumed via TS paths):

```json
{
  "name": "utils",
  "projectType": "library",
  "sourceRoot": "libs/utils/src",
  "targets": {
    "lint": {
      "executor": "@nx/linter:eslint"
    },
    "test": {
      "executor": "@nx/jest:jest"
    }
  }
}
```

## TypeScript Config

### tsconfig.base.json

Root TypeScript configuration with path mappings:

```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "rootDir": ".",
    "sourceMap": true,
    "declaration": false,
    "moduleResolution": "node",
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022"],
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "resolveJsonModule": true
  },
  "exclude": ["node_modules", "tmp"]
}
```

### Library tsconfig.lib.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "module": "commonjs",
    "outDir": "../../dist/libs/utils",
    "declaration": true,
    "types": ["node"]
  },
  "include": ["**/*.ts"],
  "exclude": ["**/*.spec.ts", "**/*.test.ts"]
}
```

## Path Aliases

### Using Import Path

```bash
# Create library with import path
nx g @nx/js:lib logger --importPath=@myorg/logger
```

Usage:

```typescript
// apps/web-app/src/app/app.ts
import { Logger } from '@myorg/logger';
```

### TS Path Mapping

Manual path mapping in `tsconfig.base.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@myorg/utils": ["libs/utils/src/index.ts"],
      "@myorg/ui": ["libs/ui/src/index.ts"]
    }
  }
}
```

## Publishing Packages

### Nx Release Commands

```bash
# Version all projects
nx release version --version=1.0.0

# Version specific projects
nx release version --projects=my-lib --version=1.2.3

# Create changelog
nx release changelog

# Publish to npm
nx release publish
```

### GitHub Actions Docker Publishing

```yaml
name: Docker Publish
on:
  push:
    branches: [main]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20
      - name: Install dependencies
        run: npm ci
      - name: Build applications
        run: npx nx run-many -t build
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      - name: Build and tag Docker images
        run: npx nx release version --dockerVersionScheme=production
      - name: Publish Docker images
        run: npx nx release publish
```

## Testing TypeScript Packages

### Vitest

```bash
# Library with Vitest
nx g @nx/js:lib my-lib --unitTestRunner=vitest

# Run tests
nx test my-lib

# Watch mode
nx test my-lib --watch
```

### Jest

```bash
# Library with Jest
nx g @nx/js:lib my-lib --unitTestRunner=jest

# Run tests
nx test my-lib

# Coverage
nx test my-lib --coverage
```

### Example Test

```typescript
// libs/utils/src/lib/utils.spec.ts
import { formatDate } from './utils';

describe('formatDate', () => {
  it('should format date correctly', () => {
    const date = new Date('2024-01-01');
    expect(formatDate(date)).toBe('2024-01-01');
  });
});
```

## Common Patterns

### Shared Utilities Library

```bash
# Create utilities library
nx g @nx/js:lib utils --directory=libs/shared

# Add utility functions
# libs/shared/utils/src/lib/date.ts
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

// libs/shared/utils/src/lib/string.ts
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// libs/shared/utils/src/index.ts
export * from './lib/date';
export * from './lib/string';
```

### Type Definitions Library

```bash
# Create types library
nx g @nx/js:lib types --directory=libs/shared

// libs/shared/types/src/index.ts
export interface User {
  id: string;
  email: string;
  name: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
}
```

### Constants Library

```bash
nx g @nx/js:lib constants --directory=libs/shared

// libs/shared/constants/src/index.ts
export const API_URL = 'https://api.example.com';
export const MAX_RETRY_ATTEMPTS = 3;
export const TIMEOUT_MS = 5000;
```

### Multi-Package Monorepo

```bash
# Create multiple packages
nx g @nx/js:lib pkg1 --importPath=@myorg/pkg1
nx g @nx/js:lib pkg2 --importPath=@myorg/pkg2
nx g @nx/js:lib pkg3 --importPath=@myorg/pkg3

# Build all packages
nx run-many -t build --projects=pkg1,pkg2,pkg3

# Test all packages
nx run-many -t test --projects=pkg*
```

## Dependencies Between Packages

### Local Dependencies

```json
// libs/pkg2/package.json
{
  "name": "@myorg/pkg2",
  "dependencies": {
    "@myorg/pkg1": "*"
  }
}
```

```json
// libs/pkg2/project.json
{
  "targets": {
    "build": {
      "dependsOn": ["pkg1^build"]
    }
  }
}
```

### Import from Local Package

```typescript
// libs/pkg2/src/index.ts
import { something } from '@myorg/pkg1';

export function useSomething() {
  return something();
}
```

## tsconfig Paths Generator

Nx automatically generates `tsconfig.base.json` paths based on project configuration.

To manually regenerate:

```bash
nx g @nx/js:ts-config
```
