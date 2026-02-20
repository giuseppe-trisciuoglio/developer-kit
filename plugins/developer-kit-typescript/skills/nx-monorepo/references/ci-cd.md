# CI/CD Reference

## GitHub Actions

### Basic CI Workflow

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  actions: read
  contents: read

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          filter: tree:0
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - uses: nrwl/nx-set-shas@v4

      - run: npx nx affected -t lint test build

      - run: npx nx fix-ci
        if: always()
```

### With Nx Cloud DTE

```yaml
name: Nx Cloud - Main Job
on:
  push:
    branches: [main]
  pull_request:

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          filter: tree:0

      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - uses: nrwl/nx-set-shas@v4

      - name: Initialize Nx Cloud distributed CI run
        run: npx nx-cloud start-ci-run --distribute-on="manual" --stop-agents-after=e2e-ci

      - name: Check formatting
        run: npx nx-cloud record -- nx format:check

      - name: Lint, test, build, and run e2e
        run: npx nx affected -t lint,test,build,e2e-ci --configuration=ci

  agents:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        agent: [1, 2, 3]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - name: Start Nx Agent
        run: npx nx-cloud start-agent
        env:
          NX_AGENT_NAME: ${{ matrix.agent }}
```

### Static Agent Distribution

```yaml
- run: npx nx-cloud start-ci-run --distribute-on="3 linux-medium-js" --stop-agents-after="build"
```

## CircleCI

### Basic Configuration

```yaml
// .circleci/config.yml
version: 2.1
orbs:
  nx: nrwl/nx@1.7.0

jobs:
  main:
    docker:
      - image: cimg/node:lts-browsers
    steps:
      - checkout
      - run: npm ci
      - nx/set-shas:
          main-branch-name: 'main'
      - run:
          command: npx nx affected -t lint test build
      - run:
          command: npx nx fix-ci
          when: on_fail

workflows:
  version: 2
  ci:
    jobs:
      - main
```

### With Nx Cloud DTE

```yaml
version: 2.1
orbs:
  nx: nrwl/nx@1.5.1

jobs:
  main:
    docker:
      - image: cimg/node:lts-browsers
    steps:
      - checkout
      - run: npm ci
      - nx/set-shas
      - run: npx nx-cloud start-ci-run --distribute-on="manual" --stop-agents-after=e2e-ci
      - run: npx nx-cloud record -- nx format:check
      - run: npx nx affected --base=$NX_BASE --head=$NX_HEAD -t lint,test,build,e2e-ci --parallel=2 --configuration=ci

workflows:
  build:
    jobs:
      - agent:
          matrix:
            parameters:
              ordinal: [1, 2, 3]
      - main
```

## Azure Pipelines

### Basic Configuration

```yaml
jobs:
  - job: main
    displayName: Nx Cloud Main Job
    pool:
      vmImage: 'ubuntu-latest'
    steps:
      - checkout: self
        fetchDepth: '0'
        fetchFilter: tree:0
        persistCredentials: true

      - script: npm ci

      - script: npx nx-cloud start-ci-run --distribute-on="manual" --stop-agents-after=e2e-ci

      - script: npx nx-cloud record -- nx format:check

      - script: npx nx affected -t lint,test,build,e2e-ci --configuration=ci
```

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
  agent none
  environment {
    NX_BRANCH = env.BRANCH_NAME.replace('PR-', '')
  }
  stages {
    stage('Pipeline') {
      parallel {
        stage('Main') {
          when {
            branch 'main'
          }
          agent any
          steps {
            sh "npm ci"
            sh "npx nx affected -t lint test build"
          }
        }
        stage('PR') {
          when {
            not { branch 'main' }
          }
          agent any
          steps {
            sh "npm ci"
            sh "npx nx affected -t lint test build --base=origin/main"
          }
        }
      }
    }
  }
}
```

## GitLab CI

### Basic Configuration

```yaml
// .gitlab-ci.yml
image: node:20
variables:
  CI: 'true'

stages:
  - test

test:
  stage: test
  script:
    - npm ci
    - npx nx run-many -t lint test build
  only:
    - main
    - merge_requests
```

### With Nx Cloud DTE

```yaml
image: node:20
clone:
  depth: full

definitions:
  steps:
    - step: &agent
        name: Agent
        script:
          - export NX_BRANCH=$BITBUCKET_PR_ID
          - npm ci
          - npx nx-cloud start-agent

pipelines:
  pull-requests:
    '**':
      - parallel:
          - step:
              name: CI
              script:
                - export NX_BRANCH=$BITBUCKET_PR_ID
                - npm ci
                - npx nx-cloud start-ci-run --distribute-on="manual" --stop-agents-after="e2e-ci"
                - npx nx-cloud record -- nx format:check
                - npx nx affected --target=lint,test,build,e2e-ci --parallel=2
          - step: *agent
          - step: *agent
          - step: *agent
```

## Bitbucket Pipelines

### Basic Configuration

```yaml
image: node:20

pipelines:
  branches:
    main:
      - step:
          name: CI
          script:
            - npm ci
            - npx nx affected -t lint test build
  pull-requests:
    '**':
      - step:
          name: CI
          script:
            - npm ci
            - npx nx affected -t lint test build --base=origin/main
```

## Docker Publishing

### GitHub Actions Docker Workflow

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

## Affected Commands in CI

### Base Branch Configuration

```yaml
- uses: nrwl/nx-set-shas@v4
  with:
    main-branch-name: 'main'
```

### Affected Command Patterns

```bash
# Test affected
npx nx affected -t test

# Lint, test, build affected
npx nx affected -t lint test build

# With configuration
npx nx affected -t build --configuration=production

# Exclude projects
npx nx affected -t build --exclude=legacy-app

# Parallel execution
npx nx affected -t test --parallel=5
```

## Nx Cloud Setup

### Connect Workspace

```bash
nx connect
```

### Self-Healing CI

```yaml
- run: npx nx fix-ci
  if: always()
```

### Record Commands

```bash
# Record specific command
npx nx-cloud record -- nx format:check

# Record with environment variables
npx nx-cloud record --env=MY_VAR=value -- nx test
```

## Cache Configuration

### GitHub Actions Cache

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'
```

### Nx Remote Cache

```bash
# Install Azure cache
nx add @nx/azure-cache

# Install AWS cache (custom setup required)
# See Nx docs for S3-based caching
```

## CI Best Practices

1. **Use affected commands** - Only test/build changed projects
2. **Set SHAs correctly** - Required for affected to work
3. **Enable caching** - Speed up CI with npm cache and Nx cache
4. **Parallel execution** - Use `--parallel` flag where appropriate
5. **Distributed task execution** - For large repos, use Nx Cloud agents
6. **Fix CI** - Use `nx fix-ci` for automatic fixes
7. **Record tasks** - Use `nx-cloud record` for better debugging
