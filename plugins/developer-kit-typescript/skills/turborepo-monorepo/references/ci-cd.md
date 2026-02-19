# CI/CD con Turborepo

## GitHub Actions

### Basic workflow

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-test:
    name: Build and test
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install

      - name: Run lint
        run: pnpm run lint --filter=[HEAD^]

      - name: Run type check
        run: pnpm run typecheck --filter=[HEAD^]

      - name: Run tests
        run: pnpm run test --filter=[HEAD^]

      - name: Build
        run: pnpm run build --filter=[HEAD^]
```

### Con Turborepo Remote Cache

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    # Output from turbo's `pack` command
    outputs:
      artifact-hash: ${{ steps.pack.outputs.hash }}

    env:
      TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
      TURBO_TEAM: ${{ secrets.TURBO_TEAM }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install

      - name: Build & test
        run: pnpm run build test

      - name: Pack cache
        id: pack
        run: |
          tar -czf cache.tar.gz .turbo/cache
          echo "hash=$(sha256sum cache.tar.gz | cut -c1-10)" >> $GITHUB_OUTPUT

      - name: Upload cache
        uses: actions/cache/save@v4
        with:
          path: .turbo/cache
          key: turbo-${{ runner.os }}-${{ steps.pack.outputs.hash }}
```

### Workflow con affected packages

```yaml
name: Affected CI

on:
  pull_request:

jobs:
  affected:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install

      - name: Lint affected
        run: pnpm run lint --filter=[HEAD^]

      - name: Test affected
        run: pnpm run test --filter=[HEAD^]

      - name: Build affected
        run: pnpm run build --filter=[HEAD^]
```

## CircleCI

```yaml
version: 2.1

orbs:
  node: circleci/node@5.1

executors:
  node-executor:
    docker:
      - image: cimg/node:20.11
    resource_class: medium

jobs:
  build-and-test:
    executor: node-executor
    steps:
      - checkout
      - node/install-packages:
          pkg-manager: pnpm
          cache-version: v1
      - run:
          name: Lint affected
          command: pnpm run lint --filter=[HEAD^]
      - run:
          name: Test affected
          command: pnpm run test --filter=[HEAD^]
      - run:
          name: Build affected
          command: pnpm run build --filter=[HEAD^]

workflows:
  build-test:
    jobs:
      - build-and-test:
          context:
            - turbo-secrets
```

## GitLab CI

```yaml
stages:
  - validate
  - test
  - build

variables:
  PNPM_VERSION: "9"
  NODE_VERSION: "20"
  TURBO_TOKEN: ${TURBO_TOKEN}
  TURBO_TEAM: ${TURBO_TEAM}

.cache_config:
  cache:
    key:
      files:
        - pnpm-lock.yaml
    paths:
      - .pnpm-store
      - node_modules

lint:
  stage: validate
  image: node:${NODE_VERSION}
  extends: .cache_config
  script:
    - corepack enable
    - corepack prepare pnpm@${PNPM_VERSION} --activate
    - pnpm install --frozen-lockfile
    - pnpm run lint --filter=[HEAD^]

test:
  stage: test
  image: node:${NODE_VERSION}
  extends: .cache_config
  script:
    - corepack enable
    - corepack prepare pnpm@${PNPM_VERSION} --activate
    - pnpm install --frozen-lockfile
    - pnpm run test --filter=[HEAD^]

build:
  stage: build
  image: node:${NODE_VERSION}
  extends: .cache_config
  script:
    - corepack enable
    - corepack prepare pnpm@${PNPM_VERSION} --activate
    - pnpm install --frozen-lockfile
    - pnpm run build --filter=[HEAD^]
```

## Deployment Pipeline

### Deploy changed apps

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm and Node
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Install dependencies
        run: pnpm install

      - name: Build
        run: pnpm run build --filter=[HEAD^]

      - name: Deploy Next.js app
        if: contains(steps.turbo.outputs.apps, 'web')
        run: pnpm --filter web deploy

      - name: Deploy NestJS API
        if: contains(steps.turbo.outputs.apps, 'api')
        run: pnpm --filter api deploy
```

## Best Practices CI/CD

1. **Usa sempre `--filter=[HEAD^]`** nelle PR per testare solo i pacchetti modificati

2. **Cache delle dipendenze** per velocizzare il setup

3. **Paralellizza** i task dove possibile

4. **Usa turbo-ignore** per skipare le build inutili:

```bash
pnpm add -D -w turbo-ignore
```

```json
{
  "scripts": {
    "check": "turbo-ignore"
  }
}
```

5. **Fallback cache locale** se remote cache non è disponibile

6. **Timeout appropriati** per evitare job bloccati

7. **Artifact caching** tra jobs:

```yaml
- name: Save build artifacts
  uses: actions/upload-artifact@v4
  with:
    name: build
    path: apps/*/dist

- name: Load build artifacts
  uses: actions/download-artifact@v4
  with:
    name: build
```

## Turbo in Docker

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app

# Setup pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./
COPY pnpm-workspace.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY . .

# Build with turbo
RUN pnpm run build

# Production stage
FROM node:20-alpine AS prod
WORKDIR /app
COPY --from=build /app/apps/api/dist ./dist
COPY --from=build /app/apps/api/package.json ./
CMD ["node", "dist/main.js"]
```
