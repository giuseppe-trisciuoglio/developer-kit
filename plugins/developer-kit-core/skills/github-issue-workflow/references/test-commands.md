# Test Commands - Comprehensive Reference

Complete test command reference for all project types and quality checks.

## Test Suite Commands

### JavaScript/TypeScript (Node.js)

```bash
# Detect: package.json exists
# Command:
npm test

# With coverage:
npm test -- --coverage

# Watch mode:
npm test -- --watch

# Specific test file:
npm test -- path/to/test.spec.ts
```

### Java (Maven)

```bash
# Detect: pom.xml exists
# Command:
./mvnw clean verify

# Skip tests (not recommended):
./mvnw clean install -DskipTests

# Run specific test class:
./mvnw test -Dtest=TestClass

# Run specific test method:
./mvnw test -Dtest=TestClass#testMethod
```

### Java (Gradle)

```bash
# Detect: build.gradle or build.gradle.kts exists
# Command:
./gradlew build

# Run tests only:
./gradlew test

# Run specific test:
./gradlew test --tests TestClass

# With coverage:
./gradlew test jacocoTestReport
```

### Python

```bash
# Detect: pyproject.toml or setup.py exists
# Command:
python -m pytest

# With coverage:
python -m pytest --cov

# Verbose output:
python -m pytest -v

# Specific test file:
python -m pytest path/to/test_file.py
```

### Go

```bash
# Detect: go.mod exists
# Command:
go test ./...

# With verbose output:
go test -v ./...

# With coverage:
go test -cover ./...

# Specific package:
go test ./path/to/package
```

### PHP

```bash
# Detect: composer.json exists
# Command:
composer test

# PHPUnit (if configured):
./vendor/bin/phpunit

# With coverage:
./vendor/bin/phpunit --coverage-html coverage
```

### Makefile

```bash
# Detect: Makefile exists
# Command:
make test

# Specific target:
make test-unit
make test-integration
```

## Linter and Static Analysis Commands

### JavaScript/TypeScript

```bash
# ESLint:
npm run lint

# TypeScript type checking:
npx tsc --noEmit

# Prettier check:
npx prettier --check .

# Prettier format:
npx prettier --write .

# Combined:
npm run lint && npx tsc --noEmit && npx prettier --check .
```

### Java (Maven)

```bash
# Checkstyle:
./mvnw checkstyle:check

# SpotBugs:
./mvnw spotbugs:check

# PMD:
./mvnw pmd:check

# Combined:
./mvnw checkstyle:check spotbugs:check pmd:check
```

### Java (Gradle)

```bash
# All checks:
./gradlew check

# Individual checks:
./gradlew checkstyleMain
./gradlew spotbugsMain
./gradlew pmdMain
```

### Python

```bash
# Ruff linter:
python -m ruff check .

# Ruff formatter:
python -m ruff format --check .

# MyPy type checker:
python -m mypy .

# Combined:
python -m ruff check . && python -m mypy . && python -m ruff format --check .
```

### Go

```bash
# Vet:
go vet ./...

# Format check:
gofmt -l .

# Lint (requires golangci-lint):
golangci-lint run

# Combined:
go vet ./... && gofmt -l .
```

### PHP

```bash
# PHPCS:
composer lint

# PHPStan:
./vendor/bin/phpstan analyse

# Psalm:
./vendor/bin/psalm

# Combined:
composer lint && ./vendor/bin/phpstan analyse
```

## Code Formatting Checks

### JavaScript/TypeScript

```bash
# Check formatting:
npx prettier --check .

# Format files:
npx prettier --write .

# Specific directory:
npx prettier --check src/
```

### Python

```bash
# Check formatting:
python -m ruff format --check .

# Format files:
python -m ruff format .

# Specific directory:
python -m ruff format --check src/
```

### Go

```bash
# Check formatting:
gofmt -l .

# Format files:
gofmt -w .

# Specific directory:
gofmt -l src/
```

## Security Scanning

### JavaScript/TypeScript

```bash
# npm audit:
npm audit

# npm audit fix:
npm audit fix

# Yarn audit:
yarn audit

# Snyk (if installed):
npx snyk test
```

### Python

```bash
# Safety:
safety check

# Bandit:
bandit -r .

# Pip-audit:
pip-audit
```

### Dependency Check

```bash
# OWASP Dependency Check (if installed):
dependency-check --scan .
```

## Multi-Language Detection Script

```bash
#!/bin/bash
# Comprehensive test runner for Phase 5

# Detect and run the FULL test suite
if [ -f "package.json" ]; then
    echo "Detected Node.js project"
    npm test 2>&1 || true
elif [ -f "pom.xml" ]; then
    echo "Detected Maven project"
    ./mvnw clean verify 2>&1 || true
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "Detected Gradle project"
    ./gradlew build 2>&1 || true
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    echo "Detected Python project"
    python -m pytest 2>&1 || true
elif [ -f "go.mod" ]; then
    echo "Detected Go project"
    go test ./... 2>&1 || true
elif [ -f "composer.json" ]; then
    echo "Detected PHP project"
    composer test 2>&1 || true
elif [ -f "Makefile" ]; then
    echo "Detected Makefile project"
    make test 2>&1 || true
else
    echo "No known test configuration found"
    exit 1
fi
```

## Multi-Language Linter Script

```bash
#!/bin/bash
# Comprehensive linter for Phase 5

# Detect and run ALL available linters/formatters
if [ -f "package.json" ]; then
    echo "Detected Node.js project"
    npm run lint 2>&1 || true
    npx tsc --noEmit 2>&1 || true  # TypeScript type checking
elif [ -f "pom.xml" ]; then
    echo "Detected Maven project"
    ./mvnw checkstyle:check 2>&1 || true
    ./mvnw spotbugs:check 2>&1 || true
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "Detected Gradle project"
    ./gradlew check 2>&1 || true
elif [ -f "pyproject.toml" ]; then
    echo "Detected Python project"
    python -m ruff check . 2>&1 || true
    python -m mypy . 2>&1 || true
elif [ -f "go.mod" ]; then
    echo "Detected Go project"
    go vet ./... 2>&1 || true
elif [ -f "composer.json" ]; then
    echo "Detected PHP project"
    composer lint 2>&1 || true
fi
```

## Multi-Language Format Check Script

```bash
#!/bin/bash
# Code formatting check for Phase 5

# Detect and run formatting checks
if [ -f "package.json" ]; then
    echo "Checking Node.js project formatting"
    npx prettier --check . 2>&1 || true
elif [ -f "pyproject.toml" ]; then
    echo "Checking Python project formatting"
    python -m ruff format --check . 2>&1 || true
elif [ -f "go.mod" ]; then
    echo "Checking Go project formatting"
    gofmt -l . 2>&1 || true
fi
```

## Test Result Interpretation

### Exit Codes

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | All tests passed | Proceed to next phase |
| 1-4 | Tests failed | Fix failures, re-run |
| 127 | Command not found | Install test framework |
| 130 | Interrupted (Ctrl+C) | Re-run tests |

### Common Test Failures

| Failure Type | Common Cause | Fix |
|--------------|--------------|-----|
| Unit test failure | Logic error | Fix code |
| Compilation error | Syntax error | Fix syntax |
| Import error | Missing dependency | Install dependency |
| Type error | Type mismatch | Fix types |
| Lint error | Style violation | Fix style |

## Continuous Integration Integration

### GitHub Actions

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
```

### GitLab CI

```yaml
test:
  script:
    - npm ci
    - npm test
```

### Jenkins

```groovy
pipeline {
    stages {
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

## Best Practices

1. **Run full test suite** - Don't skip tests
2. **Check coverage** - Ensure adequate test coverage
3. **Fix failures immediately** - Don't accumulate test debt
4. **Keep tests fast** - Use mocks for slow operations
5. **Test in isolation** - Each test should be independent
6. **Use descriptive names** - Test names should explain what they test
7. **Test edge cases** - Don't just test the happy path
8. **Mock external dependencies** - Don't rely on external services
