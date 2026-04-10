# TDD Workflow — Test-Driven Development with SDD

This guide covers the TDD integration within the Specification-Driven Development workflow.

## Overview

TDD in SDD follows the classic RED/GREEN cycle, integrated into the task implementation workflow:

```
brainstorm → spec-to-tasks → task-tdd (RED) → task-implementation (GREEN) → task-review → code-cleanup
```

The key difference from traditional TDD: tests are generated from the specification's acceptance criteria, ensuring tests validate the documented requirements.

## RED Phase

Generate failing tests before writing any production code.

### Command

```bash
/specs:task-tdd --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-002.md"
```

### What Happens

1. **Task Parsing** (`specs-task-tdd-parser.py` hook)
   - Reads the task file
   - Extracts acceptance criteria and contracts (provides/expects)
   - Identifies the target class/module to test

2. **Test Skeleton Generation** (`specs-task-tdd-generator.py` hook)
   - Creates a test file using the language-specific template
   - Generates test methods for each acceptance criterion
   - Each test asserts the expected behavior from the spec

3. **RED Phase Verification** (`specs-task-tdd-red-phase.py` hook)
   - Runs the generated tests
   - Confirms all tests FAIL (expected — no implementation yet)
   - Saves verification results

4. **Task File Update** (`specs-task-tdd-updater.py` hook)
   - Adds test file references to the task
   - Records RED phase completion status

5. **Implementation Handoff** (`specs-task-tdd-handoff.py` hook)
   - Creates a handoff artifact in `_drift/tdd-handoff-TASK-XXX.md`
   - Lists the test file, failing tests, and implementation hints

### Example Output

For a Spring Boot JWT token service task:

```java
// Generated: src/test/java/com/example/auth/JwtTokenServiceTest.java

class JwtTokenServiceTest {

    private JwtTokenService jwtTokenService;

    @BeforeEach
    void setUp() {
        jwtTokenService = new JwtTokenService(secretKey, expirationMs);
    }

    // AC-01: Generate valid JWT token from user credentials
    @Test
    void shouldGenerateValidJwtToken() {
        // Given
        UserDetails user = User.builder()
            .username("testuser")
            .password("encoded-password")
            .roles("USER")
            .build();

        // When
        String token = jwtTokenService.generateToken(user);

        // Then
        assertThat(token).isNotNull();
        assertThat(jwtTokenService.extractUsername(token)).isEqualTo("testuser");
    }

    // AC-02: Validate token and return user details
    @Test
    void shouldValidateTokenAndReturnUsername() {
        // ... failing test
    }

    // AC-03: Reject expired tokens
    @Test
    void shouldRejectExpiredTokens() {
        // ... failing test
    }

    // AC-04: Support token refresh within grace period
    @Test
    void shouldSupportTokenRefreshWithinGracePeriod() {
        // ... failing test
    }
}
```

All tests fail because `JwtTokenService` doesn't exist yet.

### Supported Languages and Templates

| Language | Framework | Test File Pattern | Template |
|----------|-----------|-------------------|----------|
| Spring | JUnit 5 + Mockito | `*Test.java` | `spring-test-template.java` |
| Java | JUnit 5 | `*Test.java` | `java-test-template.java` |
| NestJS | Jest | `*.spec.ts` | `nestjs-test-template.spec.ts` |
| TypeScript | Jest / Mocha | `*.spec.ts` | `typescript-test-template.spec.ts` |
| React | Jest + RTL | `*.test.tsx` | `react-test-template.test.tsx` |
| Node.js | Jest | `*.test.ts` | `nodejs-test-template.test.ts` |
| Python | pytest | `test_*.py` | `python-test-template.py` |
| PHP | PHPUnit | `*Test.php` | `php-test-template.php` |

Templates are located at: `hooks/test-templates/`

## GREEN Phase

Implement production code to make the failing tests pass.

### Command

```bash
/specs:task-implementation --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-002.md"
```

### What Happens

The implementation command detects the TDD handoff artifact and:
1. Reads the test file and handoff notes
2. Implements the minimal code to make tests pass
3. Runs all tests to verify GREEN status
4. Continues with the standard implementation verification

### Example

After implementing `JwtTokenService`:

```bash
# Tests now pass
./mvnw test -Dtest=JwtTokenServiceTest

# Results:
# Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
# GREEN ✓
```

## Complete TDD Example: NestJS Notification Service

### Setup

```bash
# Already have specification and tasks generated
/specs:spec-to-tasks --lang=nestjs docs/specs/002-notification-system/
```

### Task: Implement Template Engine (TASK-002)

```yaml
---
id: TASK-002
title: Implement notification template engine
lang: nestjs
status: pending
provides: [TemplateEngineService, RenderedTemplate]
expects: [TemplateRepository]
---
```

**Acceptance Criteria:**
- [ ] Parse template with variable placeholders `{{variable}}`
- [ ] Render template with provided context data
- [ ] Support conditional blocks `{{#if condition}}...{{/if}}`
- [ ] Cache compiled templates for performance

### RED Phase

```bash
/specs:task-tdd --lang=nestjs --task="docs/specs/002-notification/tasks/TASK-002.md"
```

Generates:

```typescript
// src/template-engine/template-engine.service.spec.ts

describe('TemplateEngineService', () => {
  let service: TemplateEngineService;

  beforeEach(() => {
    service = new TemplateEngineService();
  });

  // AC-01: Parse template with variable placeholders
  it('should parse template with variable placeholders', () => {
    const template = 'Hello {{name}}, welcome to {{platform}}!';
    const context = { name: 'Alice', platform: 'Developer Kit' };

    const result = service.render(template, context);

    expect(result).toBe('Hello Alice, welcome to Developer Kit!');
  });

  // AC-02: Handle missing variables gracefully
  it('should handle missing variables gracefully', () => {
    const template = 'Hello {{name}}!';
    const context = {};

    const result = service.render(template, context);

    expect(result).toBe('Hello !');
  });

  // AC-03: Support conditional blocks
  it('should support conditional blocks', () => {
    const template = 'Order {{#if premium}}priority{{/if}} shipping';
    const context = { premium: true };

    const result = service.render(template, context);

    expect(result).toBe('Order priority shipping');
  });

  // AC-04: Cache compiled templates
  it('should cache compiled templates', () => {
    const template = 'Hello {{name}}!';

    // First render compiles
    service.render(template, { name: 'Alice' });
    // Second render uses cache
    const result = service.render(template, { name: 'Bob' });

    expect(result).toBe('Hello Bob!');
    expect(service.getCacheSize()).toBe(1);
  });
});
```

Tests fail: `TemplateEngineService` doesn't exist.

### GREEN Phase

```bash
/specs:task-implementation --lang=nestjs --task="docs/specs/002-notification/tasks/TASK-002.md"
```

Claude implements:

```typescript
// src/template-engine/template-engine.service.ts

@Injectable()
export class TemplateEngineService {
  private compiledTemplates = new Map<string, CompiledTemplate>();

  render(template: string, context: Record<string, any>): string {
    const compiled = this.getOrCompile(template);
    return compiled(context);
  }

  getCacheSize(): number {
    return this.compiledTemplates.size;
  }

  private getOrCompile(template: string): CompiledTemplate {
    if (!this.compiledTemplates.has(template)) {
      this.compiledTemplates.set(template, this.compile(template));
    }
    return this.compiledTemplates.get(template)!;
  }

  private compile(template: string): CompiledTemplate {
    // Compile variable placeholders and conditionals
    // ...
  }
}
```

Tests pass. Proceed to review.

### Review

```bash
/specs:task-review --lang=nestjs docs/specs/002-notification/tasks/TASK-002.md
```

### Cleanup

```bash
/developer-kit-specs:specs-code-cleanup --lang=nestjs --task="docs/specs/002-notification/tasks/TASK-002.md"
```

## When to Use TDD vs Direct Implementation

| Scenario | Approach |
|----------|----------|
| Complex business logic | TDD (RED first) |
| Security-sensitive code | TDD (RED first) |
| Algorithm implementation | TDD (RED first) |
| Simple CRUD endpoints | Direct implementation |
| Boilerplate code | Direct implementation |
| UI components | Direct implementation |

TDD adds ~30% overhead per task but catches design issues early. Use it for tasks with complexity ≥50.
