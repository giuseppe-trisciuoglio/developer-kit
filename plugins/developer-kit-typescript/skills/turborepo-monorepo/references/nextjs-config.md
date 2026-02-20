# Next.js in Turborepo

## Package Structure

```
apps/
  web/
    package.json
    next.config.js
    tsconfig.json
    next-env.d.ts
libs/
  ui/
    package.json
    tsconfig.json
    index.ts
```

## web/package.json

```json
{
  "name": "web",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "ui": "*"
  },
  "devDependencies": {
    "@next/eslint-plugin-next": "^15.1.0",
    "typescript": "^5.7.2",
    "eslint": "^9",
    "eslint-config-next": "^15.1.0"
  }
}
```

## turbo.json for Next.js

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_*"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "outputs": []
    }
  }
}
```

## With app router

```json
{
  "pipeline": {
    "build": {
      "outputs": [
        ".next/**",
        "!.next/cache/**",
        ".next/server/**"
      ]
    }
  }
}
```

## Incremental Static Regeneration (ISR)

For ISR with Next.js, exclude fetch cache from outputs:

```json
{
  "pipeline": {
    "build": {
      "outputs": [
        ".next/**",
        "!.next/cache/**",
        "!.next/server/pages/**/_buildManifest.js"
      ]
    }
  }
}
```

## Image optimization

Next.js image optimization cache should be excluded:

```json
{
  "pipeline": {
    "build": {
      "outputs": [
        ".next/**",
        "!.next/cache/**",
        "!.next/static/media/**"
      ]
    }
  }
}
```
