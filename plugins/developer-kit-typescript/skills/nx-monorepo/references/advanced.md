# Advanced Nx Reference

## Task Orchestration

### Dependencies

Define task dependencies in `project.json`:

```json
{
  "targets": {
    "build": {
      "dependsOn": [
        { "projects": ["shared-ui"], "target": "build" },
        { "projects": ["api"], "target": "build", "params": "ignore" }
      ]
    }
  }
}
```

### Target Defaults

Configure default behavior in `nx.json`:

```json
{
  "targetDefaults": {
    "build": {
      "cache": true,
      "dependsOn": ["^build"],
      "inputs": ["production", "^production"]
    },
    "test": {
      "cache": true,
      "inputs": ["default", "^production"]
    },
    "lint": {
      "cache": true
    }
  }
}
```

## Caching

### Local Cache

Enabled by default. Cache location:

```
.nx/cache
```

### Bypass Cache

```bash
# Single run
nx run my-app:build --skip-nx-cache

# Reset cache
nx reset
```

### Remote Cache

```bash
# Install Azure cache
nx add @nx/azure-cache

# Generates activation key saved to .nx/key/key.ini
# Set as environment variable: NX_KEY
```

Configuration in `nx.json`:

```json
{
  "nxCloudId": "your-workspace-id",
  "nxCloudUrl": "https://cloud.nx.app"
}
```

## Affected Commands

### Base Configuration

```yaml
# GitHub Actions
- uses: nrwl/nx-set-shas@v4
  with:
    main-branch-name: 'main'
```

### Affected Patterns

```bash
# Basic affected
nx affected -t build

# With base/head
nx affected -t build --base=origin/main~1 --head=HEAD

# With files
nx affected -t build --files=libs/shared/*

# Exclude projects
nx affected -t build --exclude=legacy-app

# Run multiple targets
nx affected -t lint test build

# Parallel execution
nx affected -t build --parallel=5
```

## Project Graph

### Visualize Graph

```bash
# Open in browser
nx graph

# Output as JSON
nx graph --json=output.json

# Output as static HTML
nx graph --file=graph.html

# Watch mode
nx graph --watch
```

### Query Projects

```bash
# List all projects
nx show projects

# List projects with specific tags
nx show projects --tags=type:ui

# Show project details
nx show project my-app

# Show dependencies (JSON)
nx show project my-app --json

# Show affected projects
nx show projects --affected
```

## Module Federation

### Micro-Frontends Architecture

```
host-app (Shell)
├── remote1 (Checkout)
├── remote2 (Catalog)
└── remote3 (User Profile)
```

### Setup Host

```bash
nx g @nx/react:host shell-app
```

### Setup Remote

```bash
nx g @nx/react:remote checkout --name=remote1 --port=4201
```

### Add Remote to Host

```bash
nx g @nx/react:remote-configuration shell-app \
  --remote=remote1 \
  --port=4201 \
  --type=module
```

### Module Federation Config

```typescript
// apps/shell-app/module-federation.config.ts
module.exports = {
  name: 'shell',
  remotes: {
    remote1: 'remote1@http://localhost:4201/remoteEntry.js',
  },
};
```

## Named Inputs

### Configuration in nx.json

```json
{
  "namedInputs": {
    "default": ["{projectRoot}/**/*"],
    "production": [
      "default",
      "!{projectRoot}/**/*.spec.ts",
      "!{projectRoot}/**/*.test.ts",
      "!{projectRoot}/**/*.stories.ts"
    ],
    "nonProduction": [
      "default",
      "{projectRoot}/**/*.spec.ts",
      "{projectRoot}/**/*.test.ts"
    ]
  },
  "targetDefaults": {
    "build": {
      "inputs": ["production", "^production"]
    },
    "test": {
      "inputs": ["default", "^production"]
    }
  }
}
```

## Workspace Layout

### Integrated Layout

```
my-workspace/
├── apps/
├── libs/
└── tools/
```

### Standalone Projects

```
my-workspace/
├── packages/
│   ├── app1/
│   └── lib1/
```

Set in `nx.json`:

```json
{
  "workspaceLayout": {
    "appsDir": "packages",
    "libsDir": "packages"
  }
}
```

## Plugins

### Use Plugins

```json
// nx.json
{
  "plugins": [
    {
      "plugin": "@nx/react"
    },
    {
      "plugin": "@nx/js",
      "options": {
        "buildTargetName": "build",
        "testTargetName": "test"
      }
    }
  ]
}
```

### Custom Plugin Options

```json
{
  "plugins": [
    {
      "plugin": "@nx/dotnet",
      "options": {
        "build": {
          "targetName": "compile",
          "configurations": {
            "production": { "optimization": true }
          }
        },
        "test": {
          "targetName": "unit-test",
          "dependsOn": ["build"]
        }
      }
    }
  ]
}
```

## Generators

### Custom Workspace Generator

```bash
# Create generator
nx g workspace-generator my-generator

# Run generator
nx workspace-generator my-generator
```

### Sync Generator

Run automatically after `npm install` / `yarn`:

```bash
nx g @nx/js:lib my-lib --sync
```

## Release

### Version Projects

```bash
# Version all
nx release version --version=1.0.0

# Version specific projects
nx release version --projects=my-lib --version=1.2.3

# Interactive
nx release version
```

### Publish

```bash
# Dry run
nx release publish --dry-run

# Publish
nx release publish

# With first release
nx release publish --firstRelease
```

### Changelog

```bash
# Generate changelog
nx release changelog

# For specific version
nx release changelog --version=1.0.0
```

## Conformance

### Install Conformance

```bash
nx add @nx/conformance
```

### Configuration

```json
// nx.json
{
  "conformance": {
    "rules": [
      {
        "rule": "@nx/conformance/enforce-project-boundaries",
        "options": {},
        "projects": ["*"]
      }
    ]
  }
}
```

## Owners

### GitHub CODEOWNERS

```json
// nx.json
{
  "owners": {
    "format": "github",
    "outputPath": "CODEOWNERS",
    "patterns": [
      {
        "description": "Frontend team owns UI projects",
        "projects": ["tag:type:ui"],
        "owners": ["@frontend-team"]
      },
      {
        "description": "Backend team owns API",
        "projects": ["api"],
        "owners": ["@backend-team"]
      },
      {
        "description": "DevOps owns workflows",
        "files": [".github/workflows/**/*"],
        "owners": ["@devops"]
      }
    ]
  }
}
```

## Performance

### Task Runner Options

```json
// nx.json
{
  "targetDefaults": {
    "build": {
      "parallel": true,
      "maxParallel": 4
    }
  }
}
```

### Cache Encryption

```json
// nx.json
{
  "encryptionKey": "your-encryption-key"
}
```

## Agent Configuration (Nx Cloud)

### Launch Templates

```yaml
// .nx/workflows/agents.yaml
launch-templates:
  my-linux-medium-js:
    resource-class: 'docker_linux_amd64/medium'
    image: 'ubuntu22.04-node20.11-v9'
    init-steps:
      - name: Checkout
        uses: 'nrwl/nx-cloud-workflows/v5/workflow-steps/checkout/main.yaml'
      - name: Install Node Modules
        uses: 'nrwl/nx-cloud-workflows/v5/workflow-steps/install-node-modules/main.yaml'
```

### Start CI Run

```bash
# Manual distribution
npx nx-cloud start-ci-run --distribute-on="manual"

# Static distribution
npx nx-cloud start-ci-run --distribute-on="3 linux-medium-js"

# Stop agents after specific tasks
npx nx-cloud start-ci-run --stop-agents-after="e2e-ci"
```

## Troubleshooting

### Debug Task Execution

```bash
# Dry run
nx affected -t build --dry-run

# Verbose output
nx run my-app:build --verbose

# Show task graph
nx affected -t build --graph=stdout

# Skip cache
nx run my-app:build --skip-nx-cache
```

### Common Issues

**"Project X not found"**
- Check project name in `project.json` or `workspace.json`

**"Circular dependency detected"**
- Check `dependsOn` configuration
- Use `nx graph` to visualize dependencies

**Cache not working**
- Check `outputs` paths in `project.json`
- Verify cache directory permissions
