# Testing in Turborepo

## Vitest Configuration

### Installation

```bash
pnpm add -D -w vitest @vitest/ui
pnpm add -D vitest
```

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.ts',
        '**/*.d.ts'
      ]
    }
  }
})
```

### package.json scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  }
}
```

### turbo.json for Vitest

```json
{
  "pipeline": {
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["$TURBO_DEFAULT$", "vitest.config.ts"],
      "outputs": []
    },
    "test:watch": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## Jest Configuration

### Installation

```bash
pnpm add -D -w jest @types/jest
pnpm add -D jest ts-jest @types/jest
```

### jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.interface.ts',
    '!src/main.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html']
}
```

### turbo.json for Jest

```json
{
  "pipeline": {
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["$TURBO_DEFAULT$", "jest.config.js"]
    },
    "test:watch": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## Playwright Configuration

### Installation

```bash
pnpm add -D -w @playwright/test
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  webServer: {
    command: 'pnpm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
})
```

### turbo.json for Playwright

```json
{
  "pipeline": {
    "test:e2e": {
      "dependsOn": ["build"],
      "outputs": ["playwright-report/**"],
      "inputs": ["$TURBO_DEFAULT$", "playwright.config.ts"]
    }
  }
}
```

## Testing Strategies

### Unit Tests (fast, isolated)

```json
{
  "pipeline": {
    "test:unit": {
      "outputs": [],
      "inputs": ["src/**/*.ts", "test/unit/**/*.ts"]
    }
  }
}
```

### Integration Tests (slower, dependencies)

```json
{
  "pipeline": {
    "test:integration": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    }
  }
}
```

### E2E Tests (slowest, full system)

```json
{
  "pipeline": {
    "test:e2e": {
      "dependsOn": ["^build"],
      "outputs": ["playwright-report/**"]
    }
  }
}
```

## Running Tests by Type

```bash
# Run all tests
turbo run test

# Run only unit tests
turbo run test:unit

# Run tests for affected packages
turbo run test --filter=[HEAD^]

# Run tests with coverage
turbo run test:coverage
```

## CI/CD Testing

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pnpm run test --filter=[HEAD^]

- name: Run E2E tests
  run: pnpm run test:e2e --filter=[HEAD^]
```

## Test Monorepo Patterns

### Testing library changes

When a library changes, only test packages that depend on it:

```bash
turbo run test --filter=[HEAD^]
```

### Testing only changed packages

```bash
turbo run test --filter=...[HEAD]
```

### Parallel test execution

Turborepo automatically runs tests in parallel based on dependencies:

```json
{
  "pipeline": {
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```
