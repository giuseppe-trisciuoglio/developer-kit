---
globs: "**/*.ts"
---
# Rule: Nx Monorepo Conventions

## Context
Enforce consistent structure and boundaries in Nx monorepo workspaces to maintain separation between frontend, backend, and shared concerns.

## Guidelines

### Three-Zone Library Organization
Organize libraries into three strict zones based on their runtime target:

```
apps/
├── api/              # NestJS backend application
├── client/           # Customer-facing React SPA
├── backoffice/       # Internal staff React SPA
├── api-e2e/          # API end-to-end tests
├── client-e2e/       # Client E2E tests
└── backoffice-e2e/   # Backoffice E2E tests

libs/
├── server/           # NestJS feature modules (backend-only)
├── client/           # React feature libraries (frontend-only)
└── shared/           # DTOs, types, enums (used by BOTH FE and BE)
```

- **`libs/server/`**: NestJS modules, controllers, services — never imported by frontend apps
- **`libs/client/`**: React components, hooks, pages — never imported by backend apps
- **`libs/shared/`**: DTOs, enums, types, utilities — imported by both frontend and backend

### Feature Library Internal Structure

**Server feature libraries:**
```
libs/server/{feature-name}/src/
├── index.ts                          # Barrel export
└── lib/
    ├── {feature-name}.module.ts     # NestJS module
    ├── {feature-name}-options.ts    # Options interface + injection token
    ├── controllers/
    │   ├── index.ts
    │   └── {resource}.controller.ts
    ├── services/
    │   ├── index.ts
    │   └── {resource}.service.ts
    ├── test/                         # Test seeds and env
    └── utils/
```

**Client feature libraries:**
```
libs/client/{feature-name}/src/
├── index.ts                         # Barrel export
└── lib/
    ├── components/                  # React components
    ├── data-access/                 # Data fetching hooks
    ├── pages/                       # Page-level components
    ├── routes.tsx                   # React Router route definitions
    └── utils/
```

### Path Alias Conventions
Define all library aliases in `tsconfig.base.json` using a project namespace:

```json
{
  "compilerOptions": {
    "paths": {
      "@myproject/server/{feature}": ["libs/server/{feature}/src/index.ts"],
      "@myproject/client-{feature}": ["libs/client/{feature}/src/index.ts"],
      "@myproject/shared/{feature}": ["libs/shared/{feature}/src/index.ts"],
      "@myproject/core-ui": ["libs/client/core-ui/src/index.ts"],
      "@myproject/database": ["libs/server/database/src/index.ts"]
    }
  }
}
```

### Module Boundary Enforcement
Use `@nx/enforce-module-boundaries` ESLint rule to prevent incorrect cross-zone imports:

- Server libs MUST NOT import from `libs/client/`
- Client libs MUST NOT import from `libs/server/`
- Shared libs MUST NOT import from `libs/server/` or `libs/client/`
- Apps import from their respective zone and `libs/shared/`

### Barrel Exports
Every library MUST have a single `src/index.ts` barrel export. Consumers import only from the library root alias:

```typescript
// ✅ Import from barrel
import { ProcedureDto } from '@myproject/shared/procedure-dto';

// ❌ Never deep-import into library internals
import { ProcedureDto } from '../../../shared/procedure-dto/src/lib/procedure.dto';
```

Internal subdirectories also use `index.ts` barrels for clean intra-library imports.

### NestJS Module Configuration — forRootAsync Pattern
Every server feature module uses the `forRootAsync()` static method for configuration injection:

```typescript
@Module({})
export class FeatureModule {
  static forRootAsync(options: {
    useFactory: (...args: Array<any>) => FeatureModuleOptions | Promise<FeatureModuleOptions>;
    inject: any[];
  }) {
    return {
      global: true,
      module: FeatureModule,
      imports: [/* ... */],
      controllers: [/* ... */],
      providers: [
        /* services */,
        {
          provide: FEATURE_MODULE_OPTIONS,
          useFactory: options.useFactory,
          inject: options.inject,
        },
      ],
    };
  }
}
```

## Examples

### ✅ Good
```typescript
// Cross-library imports via aliases
import { UserDto } from '@myproject/shared/user-dto';
import { Button } from '@myproject/core-ui';
import { DatabaseModule } from '@myproject/database';
import { AuthGuard } from '@myproject/server/authentication-feature';

// Intra-library imports use relative paths
import { UserService } from '../services';
import { FEATURE_OPTIONS } from './feature-options';
```

### ❌ Bad
```typescript
// Reaching into library internals
import { UserDto } from 'libs/shared/user-dto/src/lib/user.dto';

// Frontend importing backend code
import { UserService } from '@myproject/server/user-feature'; // In a React component

// Importing without alias
import { Button } from '../../../../libs/client/core-ui/src/lib/button';
```
