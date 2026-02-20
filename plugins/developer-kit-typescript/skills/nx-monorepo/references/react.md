# React / Next.js / Expo Reference

## React Applications

### Create React App

```bash
# Vite (recommended)
nx g @nx/react:app my-app --style=scss

# Webpack
nx g @nx/react:app my-app --bundler=webpack

# With routing
nx g @nx/react:app my-app --routing

# With standalone mode (React 19+)
nx g @nx/react:app my-app --standalone
```

### React Library

```bash
# Buildable library
nx g @nx/react:lib shared-ui --style=scss

# Publishable npm package
nx g @nx/react:lib design-system --publishable --importPath=@myorg/design-system

# With directory structure
nx g @nx/react:lib ui-components --directory=libs/shared/ui
```

### React Component Generator

```bash
# Basic component
nx g @nx/react:component Button --project=shared-ui

# With all options
nx g @nx/react:component Header \
  --project=web-app \
  --style=scss \
  --export \
  --skipTests \
  --flat
```

### Project Configuration

```json
{
  "name": "web-app",
  "projectType": "application",
  "sourceRoot": "apps/web-app/src",
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "outputs": ["{workspaceRoot}/dist/apps/web-app"],
      "configurations": {
        "production": {
          "mode": "production"
        },
        "development": {
          "mode": "development"
        }
      }
    },
    "serve": {
      "executor": "@nx/vite:dev-server",
      "configurations": {
        "production": {
          "buildTarget": "web-app:build:production"
        }
      }
    },
    "test": {
      "executor": "@nx/vite:test"
    },
    "lint": {
      "executor": "@nx/linter:eslint"
    }
  }
}
```

## Next.js Applications

### Create Next.js App

```bash
# Pages router
nx g @nx/next:app my-next-app

# App directory (Next.js 13+)
nx g @nx/next:app my-next-app --style=scss

# With custom directory
nx g @nx/next:app my-next-app --directory=apps/next
```

### Next.js Project Configuration

```json
{
  "targets": {
    "build": {
      "executor": "@nx/next:build",
      "outputs": ["{workspaceRoot}/dist/apps/next-app"],
      "configurations": {
        "production": {},
        "development": {}
      }
    },
    "serve": {
      "executor": "@nx/next:server"
    },
    "export": {
      "executor": "@nx/next:export"
    }
  }
}
```

### Serve Next.js

```bash
# Development
nx serve my-next-app

# Production build serve
nx start my-next-app
nx serve my-next-app --prod
```

## Expo / React Native

### Create Expo App

```bash
nx g @nx/expo:app my-mobile-app
```

### Serve Expo App

```bash
# Web
nx start my-mobile-app --web

# iOS
nx start my-mobile-app --ios

# Android
nx start my-mobile-app --android
```

## Module Federation

### Micro-Frontend Setup

```bash
# Host application
nx g @nx/react:host shell-app

# Remote application
nx g @nx/react:remote checkout-app --name=checkout --port=4201

# Add remote to host
nx g @nx/react:remote-configuration shell-app \
  --remote=checkout \
  --port=4201 \
  --type=module
```

### Module Federation Config

Webpack configuration for module federation is automatically generated. Key files:

```
apps/shell-app/
├── module-federation.config.ts
└── src/
    ├── app/
    │   ├── app.component.tsx
    │   └── routes.tsx
    └── bootstrap.tsx
```

Load remote module:

```tsx
// routes.tsx
import { loadRemoteModule } from '@angular-architects/module-federation';

export const routes: Routes = [
  {
    path: 'checkout',
    loadChildren: () =>
      loadRemoteModule({
        type: 'module',
        remoteEntry: 'http://localhost:4201/remoteEntry.js',
        exposedModule: './Module'
      }).then(m => m.RemoteModule)
  }
];
```

## Tailwind CSS

### Setup Tailwind

```bash
# React project
nx g @nx/react:setup-tailwind my-app

# With custom stylesheet
nx g @nx/react:setup-tailwind my-app --stylesEntryPoint=apps/my-app/src/styles.scss
```

### Nx React Webpack Plugin

Configure for custom webpack:

```javascript
const { NxReactWebpackPlugin } = require('@nx/react/webpack-plugin');

module.exports = {
  plugins: [
    new NxReactWebpackPlugin({
      svgr: false, // Disable SVGR
    }),
  ],
};
```

## Storybook

### Setup Storybook for Library

```bash
# React library
nx g @nx/react:storybook-configuration shared-ui

# Run Storybook
nx storybook shared-ui

# Build Storybook
nx build-storybook shared-ui
```

### Storybook Composition

For composed Storybooks (multiple libraries):

```bash
# Start individual instances
nx storybook ui-lib-1  # Port: 4400
nx storybook ui-lib-2  # Port: 4401
```

## Testing

### Vitest (Recommended for Vite)

```bash
# Test project
nx test my-react-app

# Watch mode
nx test my-react-app --watch

# UI mode
nx test my-react-app --ui

# Coverage
nx test my-react-app --coverage
```

### Component Testing

```bash
# Component with test
nx g @nx/react:component Button --project=shared-ui
```

Test example:

```tsx
// button.component.spec.tsx
import { render, screen } from '@testing-library/react';
import { Button } from './button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button text="Click me" />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

### E2E Testing

```bash
# Add Cypress to app
nx g @nx/cypress:cypress-project my-app-e2e --bundler=vite

# Run E2E
nx e2e my-app-e2e

# Run with UI
nx e2e my-app-e2e --watch
```

## Common Patterns

### Shared UI Library

```bash
# 1. Create library
nx g @nx/react:lib design-system --style=scss --importPath=@myorg/design-system

# 2. Add components
nx g @nx/react:component Button --project=design-system --export
nx g @nx/react:component Input --project=design-system --export
nx g @nx/react:component Card --project=design-system --export

# 3. Build library
nx run design-system:build

# 4. Use in app
// apps/web-app/src/app/app.tsx
import { Button } from '@myorg/design-system';
```

### Feature Libraries

```bash
# Feature-specific libraries
nx g @nx/react:lib feature-auth --directory=libs/features --tags=scope:auth,type:feature
nx g @nx/react:lib feature-checkout --directory=libs/features --tags=scope:checkout,type:feature
nx g @nx/react:lib feature-catalog --directory=libs/features --tags=scope:catalog,type:feature

# Run tests for all features
nx run-many -t test --projects=tag:type:feature
```

### Library Dependencies

```json
// project.json for web-app
{
  "targets": {
    "build": {
      "dependsOn": [
        { "projects": ["shared-ui"], "target": "build" }
      ]
    }
  }
}
```
