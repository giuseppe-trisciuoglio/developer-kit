# Nx Basics Reference

## Workspace Creation

### New Workspace with Presets

```bash
npx create-nx-workspace@latest
```

Interactive prompts guide you through:
- Workspace name
- Package manager (npm, yarn, pnpm, bun)
- Preset selection (React, Angular, Node, TypeScript, etc.)

### Initialize Nx in Existing Project

For projects with existing `package.json`:

```bash
nx@latest init
```

For npm workspace projects, create `package.json` first:

```json
{
  "name": "my-workspace",
  "version": "1.0.0",
  "private": true,
  "workspaces": ["packages/*", "apps/*"]
}
```

Then run `nx@latest init`.

## Project Structure

### Standard Layout

```
my-workspace/
├── apps/                    # Deployable applications
│   ├── web-app/            # React app
│   └── api/                # NestJS API
├── libs/                    # Shared libraries
│   ├── shared-ui/          # UI components
│   └── utils/              # Utilities
├── tools/                   # Workspace tools
├── nx.json                  # Nx workspace config
├── tsconfig.base.json       # Base TS config
└── package.json             # Root package.json
```

### Configuration Files

**nx.json** - Workspace-level configuration:

```json
{
  "namedInputs": {
    "default": ["{projectRoot}/**/*"],
    "production": [
      "default",
      "!{projectRoot}/**/*.spec.ts",
      "!{projectRoot}/**/*.test.ts"
    ]
  },
  "targetDefaults": {
    "build": {
      "cache": true,
      "dependsOn": ["^build"]
    }
  }
}
```

**project.json** - Project-level configuration (per project):

```json
{
  "name": "my-app",
  "projectType": "application",
  "sourceRoot": "apps/my-app/src",
  "targets": {
    "build": { "executor": "@nx/react:webpack" },
    "serve": { "executor": "@nx/react:dev-server" },
    "test": { "executor": "@nx/vite:test" },
    "lint": { "executor": "@nx/linter:eslint" }
  }
}
```

## Essential Commands

### Running Tasks

```bash
# Run specific target on project
nx run <project>:<target>

# Run target with configuration
nx run <project>:<target> --configuration=production

# Run task for all affected projects
nx affected -t <target>

# Run multiple targets for affected projects
nx affected -t lint test build

# Run task across specific projects
nx run-many -t <target> -p <proj1> <proj2>

# Run task across all projects
nx run-many -t <target>

# Run with parallel control
nx run-many -t build --parallel=3

# Run sequentially
nx run-many -t build --parallel=false
```

### Project Operations

```bash
# List all projects
nx show projects

# Show project graph
nx graph

# Show project details
nx show project <project-name>

# Show dependencies
nx show project <project-name> --web=false --json
```

### Generator Shortcuts

```bash
# g = generate
nx g <collection>:<generator>

# Examples
nx g @nx/react:component my-component
nx g @nx/js:lib shared-utils
```

## Installation

### Install Nx Plugins

```bash
# React plugin
nx add @nx/react

# Angular plugin
nx add @nx/angular

# Node/NestJS plugin
nx add @nx/node

# JavaScript/TypeScript plugin
nx add @nx/js
```

Ensure plugin version matches Nx version.

### Global Installation (Optional)

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:nrwl/nx
sudo apt update
sudo apt install nx

# Use globally
nx build my-project
nx generate application
nx graph
```

## Common Workflows

### New Feature Development

```bash
# 1. Generate feature library
nx g @nx/js:lib feature-a --directory=libs/features

# 2. Add component/service
nx g @nx/react:component button --project=feature-a

# 3. Run tests
nx run-many -t test --projects=feature-a

# 4. Build affected
nx affected -t build

# 5. Update dependency graph
nx graph
```

### Debugging Task Execution

```bash
# Show what would run without running
nx affected -t build --dry-run

# Show task graph
nx affected -t build --graph

# Verbose output
nx run my-app:build --verbose

# Skip cache
nx run my-app:build --skip-nx-cache
```
