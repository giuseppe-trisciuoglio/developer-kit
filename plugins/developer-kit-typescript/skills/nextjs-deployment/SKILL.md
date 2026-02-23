---
name: nextjs-deployment
description: Provides comprehensive patterns for deploying Next.js applications to production. Use when configuring Docker containers, setting up GitHub Actions CI/CD pipelines, managing environment variables, implementing preview deployments, or setting up monitoring and logging for Next.js applications. Covers standalone output, multi-stage Docker builds, health checks, OpenTelemetry instrumentation, and production best practices.
allowed-tools: Read, Write, Edit, Bash
---

# Next.js Deployment

## Overview

Deploy Next.js applications to production with Docker, CI/CD pipelines, and comprehensive monitoring. Covers standalone output, multi-stage Docker builds, environment variables, health checks, and OpenTelemetry.

## When to Use

- "Deploy Next.js", "Dockerize Next.js", "containerize"
- "GitHub Actions", "CI/CD pipeline", "automated deployment"
- "Environment variables", "runtime config", "NEXT_PUBLIC"
- "Preview deployment", "staging environment"
- "Monitoring", "OpenTelemetry", "tracing", "logging"
- "Health checks", "readiness", "liveness"
- "Production build", "standalone output"

## Instructions

1. **Configure Standalone Output**: Set `output: 'standalone'` in next.config.ts
2. **Create Dockerfile**: Use multi-stage build with node:20-alpine
3. **Set Up CI/CD**: Create GitHub Actions workflow for build and deploy
4. **Manage Env Vars**: Separate build-time (NEXT_PUBLIC_) from runtime variables
5. **Add Health Checks**: Create `/api/health` route handler
6. **Set Up Monitoring**: Configure OpenTelemetry instrumentation
7. **Handle Server Actions Key**: Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` for multi-server

## Examples

### Output Modes

| Mode | Use Case | Command |
|------|----------|---------|
| `standalone` | Docker/container deployment | `output: 'standalone'` |
| `export` | Static site (no server) | `output: 'export'` |
| (default) | Node.js server deployment | `next start` |

### Environment Variable Types

| Prefix | Availability | Use Case |
|--------|--------------|----------|
| `NEXT_PUBLIC_` | Build-time + Browser | Public API keys, feature flags |
| (no prefix) | Server-only | Database URLs, secrets |

### Standalone Config

```typescript
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  generateBuildId: async () => process.env.GIT_HASH || 'build',
}

export default nextConfig
```

### Health Check Endpoint

```typescript
// src/app/api/health/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET() {
  const used = process.memoryUsage()
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || 'unknown',
    uptime: process.uptime(),
    memory: `${Math.round(used.heapUsed / 1024 / 1024)}MB`,
  })
}
```

## Constraints and Warnings

- Standalone output requires Node.js 18+
- Server Actions encryption key must be consistent across all instances
- **Never** use `NEXT_PUBLIC_` prefix for sensitive values
- Runtime env vars don't work with static export (`output: 'export'`)
- Without health checks, orchestrators may send traffic to unhealthy instances

## Best Practices

1. Use multi-stage Docker builds to minimize final image size
2. Set proper permissions with non-root user in Docker
3. Cache dependencies in CI/CD for faster builds
4. Use same Docker image across all environments
5. Inject runtime configuration via environment variables
6. Disable telemetry in production: `NEXT_TELEMETRY_DISABLED=1`

## References

Consult these files for detailed patterns:

- **[references/docker-patterns.md](references/docker-patterns.md)** - Multi-stage Dockerfile, optimization, multi-arch builds
- **[references/github-actions.md](references/github-actions.md)** - Complete CI/CD workflows, preview deployments, security scanning
- **[references/monitoring.md](references/monitoring.md)** - OpenTelemetry setup, structured logging, alerting
- **[references/deployment-platforms.md](references/deployment-platforms.md)** - Platform-specific guides (Vercel, AWS, GCP, Azure)
