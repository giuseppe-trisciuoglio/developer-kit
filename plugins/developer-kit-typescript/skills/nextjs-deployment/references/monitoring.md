# Monitoring and Logging for Next.js

Comprehensive observability patterns for Next.js applications.

## OpenTelemetry Setup

### Basic Configuration

```typescript
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./instrumentation.node')
  }
}
```

```typescript
// instrumentation.node.ts
import { NodeSDK } from '@opentelemetry/sdk-node'
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http'
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics'
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-node'
import { resourceFromAttributes } from '@opentelemetry/resources'
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
  ATTR_DEPLOYMENT_ENVIRONMENT
} from '@opentelemetry/semantic-conventions'

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'next-app',
    [ATTR_SERVICE_VERSION]: process.env.npm_package_version || '1.0.0',
    [ATTR_DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  spanProcessor: new SimpleSpanProcessor(
    new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
      headers: {
        'x-api-key': process.env.OTEL_API_KEY || '',
      },
    })
  ),
  metricReader: new PeriodicExportingMetricReader({
    exportIntervalMillis: 60000,
    exporter: new OTLPMetricExporter({
      url: process.env.OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
      headers: {
        'x-api-key': process.env.OTEL_API_KEY || '',
      },
    }),
  }),
})

sdk.start()

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk
    .shutdown()
    .then(() => console.log('OpenTelemetry terminated'))
    .catch((err) => console.error('OpenTelemetry termination error', err))
    .finally(() => process.exit(0))
})
```

### Vercel OTel (Simplified)

```typescript
// instrumentation.ts
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel({
    serviceName: process.env.OTEL_SERVICE_NAME || 'next-app',
  })
}
```

### Custom Span Creation

```typescript
// src/lib/tracing.ts
import { trace, Span, context, SpanStatusCode } from '@opentelemetry/api'

const tracer = trace.getTracer('next-app')

export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T>,
  attributes?: Record<string, string | number | boolean>
): Promise<T> {
  return tracer.startActiveSpan(name, async (span) => {
    if (attributes) {
      Object.entries(attributes).forEach(([key, value]) => {
        span.setAttribute(key, value)
      })
    }

    try {
      const result = await fn(span)
      span.setStatus({ code: SpanStatusCode.OK })
      return result
    } catch (error) {
      span.recordException(error as Error)
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: (error as Error).message,
      })
      throw error
    } finally {
      span.end()
    }
  })
}

// Usage in API routes
import { withSpan } from '@/lib/tracing'

export async function GET() {
  return withSpan(
    'fetch-users',
    async (span) => {
      const users = await db.user.findMany()
      span.setAttribute('user.count', users.length)
      return NextResponse.json(users)
    },
    { 'db.table': 'users' }
  )
}
```

## Structured Logging

### JSON Logger

```typescript
// src/lib/logger.ts
type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogContext {
  requestId?: string
  userId?: string
  path?: string
  method?: string
  [key: string]: unknown
}

interface LogEntry {
  level: LogLevel
  message: string
  timestamp: string
  service: string
  version: string
  context?: LogContext
  error?: {
    message: string
    stack?: string
    code?: string
  }
}

class Logger {
  private service: string
  private version: string

  constructor() {
    this.service = process.env.OTEL_SERVICE_NAME || 'next-app'
    this.version = process.env.npm_package_version || '1.0.0'
  }

  private log(level: LogLevel, message: string, context?: LogContext, error?: Error) {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      service: this.service,
      version: this.version,
      ...(context && { context }),
      ...(error && {
        error: {
          message: error.message,
          stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
          code: (error as { code?: string }).code,
        },
      }),
    }

    if (process.env.NODE_ENV === 'production') {
      console.log(JSON.stringify(entry))
    } else {
      const color = this.getColor(level)
      console.log(
        `${color}[${level.toUpperCase()}]${'\x1b[0m'} ${message}`,
        context || '',
        error || ''
      )
    }
  }

  private getColor(level: LogLevel): string {
    const colors: Record<LogLevel, string> = {
      debug: '\x1b[36m',  // Cyan
      info: '\x1b[32m',   // Green
      warn: '\x1b[33m',   // Yellow
      error: '\x1b[31m',  // Red
    }
    return colors[level]
  }

  debug(message: string, context?: LogContext) {
    if (process.env.LOG_LEVEL === 'debug') {
      this.log('debug', message, context)
    }
  }

  info(message: string, context?: LogContext) {
    this.log('info', message, context)
  }

  warn(message: string, context?: LogContext) {
    this.log('warn', message, context)
  }

  error(message: string, error?: Error, context?: LogContext) {
    this.log('error', message, context, error)
  }
}

export const logger = new Logger()

// Request-scoped logger
export function createRequestLogger(requestId: string, context?: Omit<LogContext, 'requestId'>) {
  return {
    debug: (message: string, extra?: Record<string, unknown>) =>
      logger.debug(message, { requestId, ...context, ...extra }),
    info: (message: string, extra?: Record<string, unknown>) =>
      logger.info(message, { requestId, ...context, ...extra }),
    warn: (message: string, extra?: Record<string, unknown>) =>
      logger.warn(message, { requestId, ...context, ...extra }),
    error: (message: string, error?: Error, extra?: Record<string, unknown>) =>
      logger.error(message, error, { requestId, ...context, ...extra }),
  }
}
```

### Middleware for Request Logging

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { createRequestLogger } from '@/lib/logger'

export function middleware(request: NextRequest) {
  const requestId = crypto.randomUUID()
  const start = Date.now()

  const logger = createRequestLogger(requestId, {
    path: request.nextUrl.pathname,
    method: request.method,
    userAgent: request.headers.get('user-agent'),
  })

  logger.info('Request started')

  const response = NextResponse.next({
    request: {
      headers: new Headers(request.headers),
    },
  })

  response.headers.set('x-request-id', requestId)

  const duration = Date.now() - start
  logger.info('Request completed', { duration: `${duration}ms` })

  return response
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

## Error Tracking

### Sentry Integration

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,

  // Adjust sampling rates
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  integrations: [
    Sentry.replayIntegration({
      maskAllText: false,
      blockAllMedia: false,
    }),
  ],
})
```

```typescript
// sentry.server.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
})
```

```typescript
// src/lib/errors.ts
import * as Sentry from '@sentry/nextjs'
import { logger } from './logger'

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public context?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export function handleError(error: Error, context?: Record<string, unknown>) {
  // Log locally
  logger.error(error.message, error, context)

  // Send to Sentry
  Sentry.withScope((scope) => {
    if (context) {
      Object.entries(context).forEach(([key, value]) => {
        scope.setExtra(key, value)
      })
    }
    Sentry.captureException(error)
  })
}
```

## Health Checks

### Basic Health Endpoint

```typescript
// src/app/api/health/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

interface HealthCheck {
  name: string
  check: () => Promise<{ status: 'ok' | 'error'; details?: unknown }>
}

const checks: HealthCheck[] = [
  {
    name: 'memory',
    check: async () => {
      const used = process.memoryUsage()
      const threshold = 1024 * 1024 * 1024 // 1GB

      return {
        status: used.heapUsed < threshold ? 'ok' : 'error',
        details: {
          heapUsed: `${Math.round(used.heapUsed / 1024 / 1024)}MB`,
          heapTotal: `${Math.round(used.heapTotal / 1024 / 1024)}MB`,
          rss: `${Math.round(used.rss / 1024 / 1024)}MB`,
        },
      }
    },
  },
  {
    name: 'uptime',
    check: async () => ({
      status: 'ok',
      details: { uptime: `${Math.round(process.uptime())}s` },
    }),
  },
]

// Add database check if needed
// checks.push({
//   name: 'database',
//   check: async () => {
//     try {
//       await db.$queryRaw`SELECT 1`
//       return { status: 'ok' }
//     } catch {
//       return { status: 'error', details: 'Database connection failed' }
//     }
//   },
// })

export async function GET() {
  const results = await Promise.all(
    checks.map(async ({ name, check }) => ({
      name,
      ...(await check()),
    }))
  )

  const isHealthy = results.every((r) => r.status === 'ok')

  return NextResponse.json(
    {
      status: isHealthy ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version,
      buildId: process.env.GIT_HASH,
      checks: results,
    },
    { status: isHealthy ? 200 : 503 }
  )
}
```

### Readiness/Liveness Probes

```typescript
// src/app/api/health/ready/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET() {
  // Check critical dependencies
  // const dbReady = await checkDatabase()
  // const cacheReady = await checkCache()

  const ready = true // dbReady && cacheReady

  return NextResponse.json(
    { status: ready ? 'ready' : 'not ready' },
    { status: ready ? 200 : 503 }
  )
}
```

```typescript
// src/app/api/health/live/route.ts
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET() {
  // Simple liveness check - process is running
  return NextResponse.json({ status: 'alive' })
}
```

## Metrics Collection

### Custom Metrics

```typescript
// src/lib/metrics.ts
import { metrics, ValueType } from '@opentelemetry/api'

const meter = metrics.getMeter('next-app')

// Counters
export const requestCounter = meter.createCounter('http.requests.total', {
  description: 'Total HTTP requests',
  valueType: ValueType.INT,
})

export const errorCounter = meter.createCounter('http.errors.total', {
  description: 'Total HTTP errors',
  valueType: ValueType.INT,
})

// Histograms
export const requestDuration = meter.createHistogram('http.request.duration', {
  description: 'HTTP request duration in milliseconds',
  valueType: ValueType.DOUBLE,
  unit: 'ms',
})

// UpDownCounter
export const activeConnections = meter.createUpDownCounter('http.connections.active', {
  description: 'Number of active connections',
  valueType: ValueType.INT,
})

// Usage
export function recordRequest(method: string, route: string, status: number, duration: number) {
  const attributes = { method, route, status: status.toString() }

  requestCounter.add(1, attributes)
  requestDuration.record(duration, attributes)

  if (status >= 400) {
    errorCounter.add(1, { ...attributes, error_type: status >= 500 ? 'server' : 'client' })
  }
}
```

### Metrics Middleware

```typescript
// src/middleware.ts (updated)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { recordRequest } from '@/lib/metrics'

export function middleware(request: NextRequest) {
  const start = Date.now()

  const response = NextResponse.next()

  const duration = Date.now() - start
  recordRequest(
    request.method,
    request.nextUrl.pathname,
    response.status,
    duration
  )

  return response
}
```

## Dashboard Queries

### Grafana/Prometheus Examples

```promql
# Request rate
sum(rate(http_requests_total[5m])) by (route)

# Error rate
sum(rate(http_errors_total[5m])) by (error_type)

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_bucket[5m])) by (le, route))

# Memory usage
process_resident_memory_bytes{service="next-app"}
```

### Logging Queries (Loki)

```logql
# Error logs
{service="next-app"} |= "error"

# Slow requests
{service="next-app"} |= "duration" | json | duration > "1000ms"

# Requests by user
{service="next-app"} | json | userId != ""
```
