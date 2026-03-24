# Security Headers and Configuration

## Express Security Configuration

### Vulnerable: Missing security headers and permissive CORS

```typescript
const app = express();
app.use(cors()); // Allows all origins
```

### Secure: Comprehensive security configuration

```typescript
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';

const app = express();

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
}));

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') ?? [],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
}));

app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
}));
```

## NestJS Security Module

```typescript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

@Module({
  imports: [
    HelmetModule,
    ThrottlerModule.forRoot([{
      ttl: 60000,
      limit: 10,
    }]),
  ],
})
export class SecurityModule {}
```

## Cookie Security Flags

```typescript
// Always set these flags on sensitive cookies
res.cookie('sessionId', sessionId, {
  httpOnly: true,    // Prevents JavaScript access
  secure: true,      // HTTPS only
  sameSite: 'strict', // CSRF protection
  maxAge: 3600000,   // 1 hour expiration
  path: '/',
});
```
