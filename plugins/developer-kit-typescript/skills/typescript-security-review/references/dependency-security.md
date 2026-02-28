# Dependency Security and Supply Chain Guide

## npm Audit

### Running Security Audits

```bash
# Check for known vulnerabilities
npm audit

# Get machine-readable output
npm audit --json

# Fix automatically where possible
npm audit fix

# Fix with major version bumps (review carefully)
npm audit fix --force

# Only show critical/high severity
npm audit --audit-level=high
```

### CI Pipeline Integration

```yaml
# GitHub Actions example
- name: Security audit
  run: |
    npm audit --audit-level=high
    if [ $? -ne 0 ]; then
      echo "::error::npm audit found high/critical vulnerabilities"
      exit 1
    fi
```

## Dependency Management Best Practices

### Lock Files
Always commit `package-lock.json` to ensure reproducible builds and prevent supply chain attacks.

```bash
# Install from lock file only (CI environments)
npm ci

# Never use in CI:
# npm install  ← Can resolve different versions
```

### Minimal Dependencies
Every dependency is an attack surface. Review before adding:

```bash
# Check package details before installing
npm info <package> | grep -E 'description|homepage|repository|maintainers'

# Check download stats and maintenance
npx npm-check-updates --doctor
```

### Questions Before Adding a Dependency
1. Is this actively maintained? (check last commit date, open issues)
2. How many transitive dependencies does it add? (`npm ls <package>`)
3. Can I implement this with the standard library instead?
4. Does the maintainer have 2FA enabled? (check npm profile)
5. Is there a more popular/trusted alternative?

## Automated Dependency Scanning

### GitHub Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
```

### Socket.dev
Detects supply chain attacks that npm audit misses:
- Typosquatting (similar package names)
- Install scripts that execute code during `npm install`
- Obfuscated code
- Network access during install
- Excessive permissions

### Snyk
Provides deeper vulnerability analysis and fix PRs:

```bash
# Install and authenticate
npm install -g snyk
snyk auth

# Test for vulnerabilities
snyk test

# Monitor project continuously
snyk monitor
```

## Supply Chain Attack Vectors

### Typosquatting
Attackers publish packages with names similar to popular ones.

```bash
# ❌ Easy mistake
npm install expres  # Not "express"
npm install lodahs  # Not "lodash"

# ✅ Double-check package names
npm info express | head -5
```

### Install Script Attacks
Malicious packages run code during `npm install`.

```bash
# Check for install scripts before installing
npm show <package> scripts

# Audit install scripts in your dependencies
npx can-i-ignore-scripts
```

### Dependency Confusion
Attackers publish public packages with the same name as internal packages.

**Prevention:**
```bash
# Use scoped packages for internal libraries
npm install @my-org/internal-lib

# Configure .npmrc for private registry
registry=https://registry.npmjs.org/
@my-org:registry=https://npm.my-company.com/
```

## Reviewing New Dependencies

### Security Checklist for New Packages

- [ ] **Popularity**: >1000 weekly downloads or well-known organization
- [ ] **Maintenance**: Updated within last 6 months
- [ ] **License**: Compatible with your project (MIT, Apache-2.0, BSD)
- [ ] **Dependencies**: Minimal transitive dependencies
- [ ] **Install scripts**: No suspicious preinstall/postinstall scripts
- [ ] **Source code**: Repository matches published package
- [ ] **Maintainers**: Multiple maintainers, 2FA enabled
- [ ] **TypeScript**: Has type definitions (DefinitelyTyped or built-in)
- [ ] **CVE history**: Check for past vulnerabilities on Snyk/NVD

### Evaluating Package Health

```bash
# Check package size and dependencies
npx packagephobia <package>

# Check bundle size impact
npx bundlephobia <package>

# List all transitive dependencies
npm ls <package> --all

# Check for known vulnerabilities
npx audit-ci --config audit-ci.json
```

## Responding to Vulnerabilities

### Severity Assessment

| Severity | Response Time | Action |
|----------|--------------|--------|
| Critical | Immediate | Patch or remove dependency |
| High | Within 1 week | Upgrade to fixed version |
| Medium | Within 1 month | Plan upgrade in next sprint |
| Low | Next quarter | Include in regular maintenance |

### When a Fix is Not Available

1. **Check if vulnerability is exploitable** in your usage context
2. **Apply workarounds** (disable affected feature, add input validation)
3. **Fork and patch** the dependency if critical
4. **Replace** with an alternative package
5. **Accept risk** with documented justification (last resort)

```typescript
// Document accepted risk in code
// SECURITY: CVE-2024-XXXXX in package-x v1.2.3
// Risk accepted: We don't use the affected XML parser feature
// Review date: 2024-06-01
// Ticket: JIRA-1234
```

## Environment Variable Security

### Validation at Startup

```typescript
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  API_KEY: z.string().min(16),
  PORT: z.coerce.number().default(3000),
});

const env = envSchema.parse(process.env);
export default env;
```

### .env Files

```bash
# .gitignore — ALWAYS ignore env files
.env
.env.local
.env.*.local

# .env.example — template without secrets (DO commit this)
NODE_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JWT_SECRET=<generate-with-openssl-rand-hex-32>
```

### Prevent Client Exposure

```typescript
// Next.js: Only NEXT_PUBLIC_ vars are exposed to client
// ❌ Exposed to client bundle
NEXT_PUBLIC_API_KEY=secret  // Don't put secrets here!

// ✅ Server-only (not in client bundle)
DATABASE_URL=postgresql://...
JWT_SECRET=...
```
