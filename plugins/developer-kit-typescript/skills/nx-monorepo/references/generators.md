# Nx Generators Reference

## Application Generators

### React Application

```bash
# Using Vite
nx g @nx/react:app my-app --style=css

# Using Webpack
nx g @nx/react:app my-app --bundler=webpack

# With specific directory
nx g @nx/react:app my-app --directory=apps/web

# With TypeScript strict mode
nx g @nx/react:app my-app --strict

# With routing
nx g @nx/react:app my-app --routing

# Options: style (css|scss|stylus|less|sass)
nx g @nx/react:app my-app --style=scss
```

### Next.js Application

```bash
# Basic Next.js app
nx g @nx/next:app my-next-app

# With custom directory
nx g @nx/next:app my-next-app --directory=apps/next

# With TypeScript
nx g @nx/next:app my-next-app --tsConfig=tsconfig.base.json
```

### NestJS Application

```bash
# NestJS app
nx g @nx/node:app my-api --framework=nest

# Or using NestJS plugin directly
nx g @nx/nest:app my-api

# With directory
nx g @nx/nest:app my-api --directory=apps/api
```

### Express Application

```bash
nx g @nx/node:app my-express-api --framework=express
```

## Library Generators

### React Library

```bash
# Buildable library (creates build target)
nx g @nx/react:lib shared-ui

# Publishable library
nx g @nx/react:lib shared-ui --publishable

# With directory
nx g @nx/react:lib shared-ui --directory=libs/shared/ui

# Import path (importable as @myorg/shared-ui)
nx g @nx/react:lib shared-ui --importPath=@myorg/shared-ui
```

### TypeScript/JavaScript Library

```bash
# Basic library
nx g @nx/js:lib utils

# Buildable with entry point
nx g @nx/js:lib utils --buildable

# With directory structure
nx g @nx/js:lib utils --directory=libs/shared/utils

# Set import path
nx g @nx/js:lib date-fns --importPath=@myorg/date-fns
```

### Node Library

```bash
nx g @nx/node:lib my-node-lib
```

## Component Generators

### React Component

```bash
# In specific project
nx g @nx/react:component button --project=shared-ui

# With directory in project
nx g @nx/react:component header --project=web-app --path=apps/web-app/src/components

# With styling
nx g @nx/react:component card --project=shared-ui --style=scss

# With export (barrel export)
nx g @nx/react:component button --project=shared-ui --export

# With flat structure
nx g @nx/react:component button --project=shared-ui --flat

# Skip tests
nx g @nx/react:component button --project=shared-ui --skipTests
```

### Angular Component

```bash
nx g @nx/angular:component header --project=my-app
```

## Service/Class Generators

### NestJS Services

```bash
# Module in NestJS app
nx g @nx/nest:module users --project=my-api

# Controller
nx g @nx/nest:controller users --project=my-api

# Service
nx g @nx/nest:service users --project=my-api

# All at once (module + controller + service)
nx g @nx/nest:resource users --project=my-api
```

### TypeScript Interfaces/Classes

```bash
# Interface
nx g @nx/js:interface user --project=utils

# Class
nx g @nx/js:class validator --project=utils
```

## Specialized Generators

### Module Federation

```bash
# Host application
nx g @nx/react:host host-app

# Remote application
nx g @nx/react:remote remote-app --name=remote1

# Add remote to host
nx g @nx/react:remote-configuration host-app --remote=remote1 --port=4201
```

### Storybook Setup

```bash
# For React library
nx g @nx/react:storybook-configuration shared-ui

# For Angular library
nx g @nx/angular:storybook-configuration shared-ui
```

### Tailwind CSS

```bash
# React project
nx g @nx/react:setup-tailwind my-app

# With custom stylesheet
nx g @nx/react:setup-tailwind my-app --stylesEntryPoint=apps/my-app/src/styles.scss
```

### Testing Setup

```bash
# Cypress E2E
nx g @nx/cypress:cypress-project my-app-e2e --bundler=vite

# Playwright E2E
nx g @nx/playwright:project my-app-e2e

# Jest unit tests
nx g @nx/jest:project my-lib
```

## Generator Options Reference

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--directory` | Output directory | `--directory=libs/shared` |
| `--tags` | Project tags | `--tags=type:ui,scope:frontend` |
| `--style` | Styling approach | `--style=scss` |
| `--skipTests` | Skip test files | `--skipTests` |
| `--flat` | Flat directory structure | `--flat` |
| `--export` | Export from index | `--export` |
| `--strict` | Enable strict mode | `--strict` |

### Path Modes

Nx supports two path modes for generators:

**As-provided** (recommended):
```bash
nx g lib my-lib           # apps/my-lib
nx g lib my-lib --directory=libs/shared
                           # libs/shared/my-lib
```

**Derived** (legacy):
```bash
nx g lib my-lib           # Creates directory based on workspace config
```

## Workflow Examples

### Create New Feature Library

```bash
# 1. Create library
nx g @nx/react:lib feature-auth --directory=libs/features --importPath=@myorg/feature-auth

# 2. Add components
nx g @nx/react:component LoginForm --project=feature-auth --export
nx g @nx/react:component LoginButton --project=feature-auth --export

# 3. Build library
nx run feature-auth:build
```

### Add E2E Tests to App

```bash
# Add Cypress to existing app
nx g @nx/cypress:cypress-project web-app-e2e --bundler=vite --project=web-app
```

### Migrate Component

```bash
# Move component to library
nx g @nx/react:component button --project=shared-ui --export --flat
```
