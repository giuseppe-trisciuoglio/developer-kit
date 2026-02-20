# NestJS in Turborepo

## Package Structure

```
apps/
  api/
    package.json
    nest-cli.json
    tsconfig.json
    tsconfig.build.json
    src/
      main.ts
libs/
  shared/
    package.json
    tsconfig.json
    src/
      index.ts
```

## api/package.json

```json
{
  "name": "api",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:cov": "jest --coverage",
    "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
    "test:e2e": "jest --config ./test/jest-e2e.json",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@nestjs/common": "^10.4.7",
    "@nestjs/core": "^10.4.7",
    "@nestjs/platform-express": "^10.4.7",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1",
    "shared": "*"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.4.7",
    "@nestjs/schematics": "^10.2.3",
    "@nestjs/testing": "^10.4.7",
    "@types/express": "^5.0.0",
    "@types/jest": "^29.5.14",
    "@types/node": "^22.10.5",
    "@typescript-eslint/eslint-plugin": "^8.19.1",
    "@typescript-eslint/parser": "^8.19.1",
    "eslint": "^9",
    "jest": "^29.7.0",
    "ts-jest": "^29.2.5",
    "ts-loader": "^9.5.2",
    "ts-node": "^10.9.2",
    "tsconfig-paths": "^4.2.0",
    "typescript": "^5.7.2"
  }
}
```

## turbo.json for NestJS

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "start:dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["$TURBO_DEFAULT$", "jest.config.js"]
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

## nest-cli.json

```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true,
    "webpack": false
  }
}
```

## tsconfig.build.json

```json
{
  "extends": "./tsconfig.json",
  "exclude": ["node_modules", "test", "dist", "**/*spec.ts"]
}
```

## Workspace tsconfig paths

In root `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "api/*": ["./apps/api/src/*"],
      "shared/*": ["./libs/shared/src/*"]
    }
  }
}
```

## Environment Variables

Use `.env` files with Turborepo global dependencies:

```json
{
  "globalDependencies": ["**/.env.*"],
  "globalEnv": ["DATABASE_URL", "JWT_SECRET", "NODE_ENV"]
}
```

## Monorepo package exports

For `libs/shared`:

```json
{
  "name": "shared",
  "version": "0.0.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  }
}
```
