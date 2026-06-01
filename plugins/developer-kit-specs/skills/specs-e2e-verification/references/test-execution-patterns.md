# Test Execution Patterns

Reference guide for startup commands, health checks, and test commands per application type.

## Docker-Managed Projects

### Pre-Start Checks
```bash
# Verify Docker daemon is running
docker info >/dev/null 2>&1 || { echo "Docker is not available."; exit 1; }

# Check for port collision
if lsof -i :"${PORT}" >/dev/null 2>&1 || nc -z localhost "${PORT}" 2>/dev/null; then
    echo "Port ${PORT} is already in use."
    # Attempt to detect if it's the same app (reuse) or a conflict
    EXISTING_PID=$(lsof -ti:"${PORT}" | head -n1)
    EXISTING_CMD=$(ps -p "${EXISTING_PID}" -o comm= 2>/dev/null || echo "unknown")
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "${EXISTING_CMD}"; then
        echo "Existing container detected; reusing."
    else
        echo "Port conflict. Free the port and retry."; exit 1
    fi
fi
```

### Startup
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

docker compose up -d --build >> "$STARTUP_LOGS_FILE" 2>&1
```

### Health Check (with timeout)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    # Option A: Docker native health status (supports JSON array and NDJSON)
    if docker compose ps --format json 2>/dev/null | jq -s -e '.[] | select(.Health=="healthy")' >/dev/null 2>&1; then
        READY=true
        break
    fi
    # Option B: Fallback port polling every 3 seconds
    if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
        READY=true
        break
    fi
    sleep 3
done

if [ "$READY" != "true" ]; then
    echo "Startup timeout (${STARTUP_TIMEOUT}s) exceeded."
    docker compose logs --tail=50 >> "$STARTUP_LOGS_FILE" 2>&1
    docker compose down >/dev/null 2>&1 || true
    exit 1
fi
```

### Teardown
```bash
docker compose down
```

---

## Spring Boot (JVM)

### Pre-Start Checks
```bash
# Check for port collision
if lsof -i :"${PORT}" >/dev/null 2>&1 || nc -z localhost "${PORT}" 2>/dev/null; then
    echo "Port ${PORT} is already in use."
    EXISTING_PID=$(lsof -ti:"${PORT}" | head -n1)
    EXISTING_CMD=$(ps -p "${EXISTING_PID}" -o comm= 2>/dev/null || echo "unknown")
    if echo "$EXISTING_CMD" | grep -q "java"; then
        echo "Existing Java process detected; reusing."
    else
        echo "Port conflict. Free the port and retry."; exit 1
    fi
fi
```

### Startup (Maven)
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

./mvnw spring-boot:run -Dspring-boot.run.profiles=e2e >> "$STARTUP_LOGS_FILE" 2>&1 &
STARTUP_PID=$!
```

### Startup (Gradle)
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

./gradlew bootRun --args='--spring.profiles.active=e2e' >> "$STARTUP_LOGS_FILE" 2>&1 &
STARTUP_PID=$!
```

### Health Check (with timeout)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    # Option A: Actuator health endpoint
    if curl -sf "http://localhost:${PORT}/actuator/health" >/dev/null 2>&1; then
        READY=true
        break
    fi
    # Option B: Fallback to raw port readiness
    if nc -z localhost "${PORT}" 2>/dev/null; then
        READY=true
        break
    fi
    # Fail fast if the background process exited early
    if ! kill -0 "$STARTUP_PID" 2>/dev/null; then
        echo "Spring Boot process exited before reaching healthy state."
        break
    fi
    sleep 3
done

if [ "$READY" != "true" ]; then
    echo "Startup timeout (${STARTUP_TIMEOUT}s) exceeded."
    tail -n 100 "$STARTUP_LOGS_FILE" >> "$STARTUP_LOGS_FILE".final 2>&1 || true
    kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
# Find and kill process on target port
lsof -ti:"${PORT}" | xargs kill -TERM 2>/dev/null || true
```

---

## NestJS

### Pre-Start Checks
```bash
# Verify node_modules exists
[ -d "${PROJECT_ROOT}/node_modules" ] || { echo "node_modules not found. Run 'npm install' first."; exit 1; }

# Check for port collision
if lsof -i :"${PORT}" >/dev/null 2>&1 || nc -z localhost "${PORT}" 2>/dev/null; then
    echo "Port ${PORT} is already in use."
    EXISTING_PID=$(lsof -ti:"${PORT}" | head -n1)
    EXISTING_CMD=$(ps -p "${EXISTING_PID}" -o comm= 2>/dev/null || echo "unknown")
    if echo "$EXISTING_CMD" | grep -q "node"; then
        echo "Existing Node.js process detected; reusing."
    else
        echo "Port conflict. Free the port and retry."; exit 1
    fi
fi
```

### Startup
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

cd "${PROJECT_ROOT}" && npm run start:dev >> "$STARTUP_LOGS_FILE" 2>&1 &
STARTUP_PID=$!
```

### Health Check (with timeout)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
        READY=true
        break
    fi
    if nc -z localhost "${PORT}" 2>/dev/null; then
        READY=true
        break
    fi
    if ! kill -0 "$STARTUP_PID" 2>/dev/null; then
        echo "NestJS process exited before reaching healthy state."
        break
    fi
    sleep 3
done

if [ "$READY" != "true" ]; then
    echo "Startup timeout (${STARTUP_TIMEOUT}s) exceeded."
    tail -n 100 "$STARTUP_LOGS_FILE" >> "$STARTUP_LOGS_FILE".final 2>&1 || true
    kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
lsof -ti:"${PORT}" | xargs kill -TERM 2>/dev/null || true
```

### Ready Log Patterns
Common console messages indicating successful startup:
- `Nest application successfully started`
- `Application is running on: http://localhost:${PORT}`

---

## Node / Express / Fastify (Generic API)

### Pre-Start Checks
```bash
# Verify node_modules exists
[ -d "${PROJECT_ROOT}/node_modules" ] || { echo "node_modules not found. Run 'npm install' first."; exit 1; }

# Check for port collision
if lsof -i :"${PORT}" >/dev/null 2>&1 || nc -z localhost "${PORT}" 2>/dev/null; then
    echo "Port ${PORT} is already in use."
    EXISTING_PID=$(lsof -ti:"${PORT}" | head -n1)
    EXISTING_CMD=$(ps -p "${EXISTING_PID}" -o comm= 2>/dev/null || echo "unknown")
    if echo "$EXISTING_CMD" | grep -q "node"; then
        echo "Existing Node.js process detected; reusing."
    else
        echo "Port conflict. Free the port and retry."; exit 1
    fi
fi
```

### Startup
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

if grep -q '"dev"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm run dev >> "$STARTUP_LOGS_FILE" 2>&1 &
elif grep -q '"start"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm start >> "$STARTUP_LOGS_FILE" 2>&1 &
else
    cd "${PROJECT_ROOT}" && node server.js >> "$STARTUP_LOGS_FILE" 2>&1 &
fi
STARTUP_PID=$!
```

### Health Check (with timeout)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
        READY=true
        break
    fi
    if nc -z localhost "${PORT}" 2>/dev/null; then
        READY=true
        break
    fi
    if ! kill -0 "$STARTUP_PID" 2>/dev/null; then
        echo "Node.js process exited before reaching healthy state."
        break
    fi
    sleep 3
done

if [ "$READY" != "true" ]; then
    echo "Startup timeout (${STARTUP_TIMEOUT}s) exceeded."
    tail -n 100 "$STARTUP_LOGS_FILE" >> "$STARTUP_LOGS_FILE".final 2>&1 || true
    kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
lsof -ti:"${PORT}" | xargs kill -TERM 2>/dev/null || true
```

### Ready Log Patterns
Common console messages indicating successful startup:
- `Local: http://localhost:${PORT}/`
- `ready in`
- `Server running on port ${PORT}`

---

## React / Vue / Angular (SPA)

### Pre-Start Checks
```bash
# Verify node_modules exists
[ -d "${PROJECT_ROOT}/node_modules" ] || { echo "node_modules not found. Run 'npm install' first."; exit 1; }

# Check for port collision
if lsof -i :"${PORT}" >/dev/null 2>&1 || nc -z localhost "${PORT}" 2>/dev/null; then
    echo "Port ${PORT} is already in use."
    EXISTING_PID=$(lsof -ti:"${PORT}" | head -n1)
    EXISTING_CMD=$(ps -p "${EXISTING_PID}" -o comm= 2>/dev/null || echo "unknown")
    if echo "$EXISTING_CMD" | grep -q "node"; then
        echo "Existing Node.js process detected; reusing."
    else
        echo "Port conflict. Free the port and retry."; exit 1
    fi
fi
```

### Startup
```bash
STARTUP_LOGS_FILE="$(mktemp)"
STARTUP_TIMEOUT="${TIMEOUT:-120}"
START_TIME="$(date +%s)"

if grep -q '"dev"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm run dev >> "$STARTUP_LOGS_FILE" 2>&1 &
elif grep -q '"start"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm start >> "$STARTUP_LOGS_FILE" 2>&1 &
else
    cd "${PROJECT_ROOT}" && ng serve >> "$STARTUP_LOGS_FILE" 2>&1 &
fi
STARTUP_PID=$!
```

### Health Check (with timeout)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
        READY=true
        break
    fi
    if nc -z localhost "${PORT}" 2>/dev/null; then
        READY=true
        break
    fi
    if ! kill -0 "$STARTUP_PID" 2>/dev/null; then
        echo "SPA dev server exited before reaching healthy state."
        break
    fi
    sleep 3
done

if [ "$READY" != "true" ]; then
    echo "Startup timeout (${STARTUP_TIMEOUT}s) exceeded."
    tail -n 100 "$STARTUP_LOGS_FILE" >> "$STARTUP_LOGS_FILE".final 2>&1 || true
    kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
lsof -ti:"${PORT}" | xargs kill -TERM 2>/dev/null || true
```

### Ready Log Patterns
Common console messages indicating successful startup:
- `Local: http://localhost:${PORT}/`
- `ready in`
- `Angular Live Development Server is listening on localhost:${PORT}`

---

## Python (FastAPI)

### Startup
```bash
uvicorn main:app --reload --port 8000
# or
fastapi dev main.py
```

### Health Check
```bash
curl -sf http://localhost:8000/health || curl -sf http://localhost:8000/docs
```

### Teardown
```bash
lsof -ti:8000 | xargs kill -TERM
```

---

## Python (Django)

### Startup
```bash
python manage.py runserver 8000
```

### Health Check
```bash
curl -sf http://localhost:8000/health || curl -sf http://localhost:8000/admin/login/
```

### Teardown
```bash
lsof -ti:8000 | xargs kill -TERM
```

---

## Python (Flask)

### Startup
```bash
flask run --port 5000
```

### Health Check
```bash
curl -sf http://localhost:5000/health || curl -sf http://localhost:5000
```

### Teardown
```bash
lsof -ti:5000 | xargs kill -TERM
```

---

## Tauri Desktop

### Framework Detection
```bash
if [ -f "${PROJECT_ROOT}/src-tauri/Cargo.toml" ]; then
    DESKTOP_FRAMEWORK="tauri"
fi
```

### Build (Debug)
```bash
cd "${PROJECT_ROOT}" && cargo tauri build --debug >> "$STARTUP_LOGS_FILE" 2>&1
```
- Build failure is captured in `$STARTUP_LOGS_FILE` and reported.
- Abort verification if build exit code is non-zero.

### Launch

**macOS**:
```bash
APP_BUNDLE=$(find "${PROJECT_ROOT}/src-tauri/target/debug/bundle" -name "*.app" -print -quit 2>/dev/null)
if [ -n "$APP_BUNDLE" ]; then
    open "$APP_BUNDLE" >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
else
    DEV_BINARY=$(find "${PROJECT_ROOT}/src-tauri/target/debug" -maxdepth 1 -type f -executable ! -name '*.dylib' ! -name '*.so' -print -quit 2>/dev/null)
    if [ -n "$DEV_BINARY" ]; then
        "$DEV_BINARY" >> "$STARTUP_LOGS_FILE" 2>&1 &
        STARTUP_PID=$!
    else
        cargo tauri dev >> "$STARTUP_LOGS_FILE" 2>&1 &
        STARTUP_PID=$!
    fi
fi
```

**Linux**:
```bash
APP_BINARY=$(find "${PROJECT_ROOT}/src-tauri/target/debug" -maxdepth 1 -type f -executable ! -name '*.so' -print -quit 2>/dev/null)
if [ -n "$APP_BINARY" ]; then
    "$APP_BINARY" >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
else
    cargo tauri dev >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
fi
```

**Windows**:
```bash
# Use a subagent or computer-use; no direct Bash equivalent
# Typical path: src-tauri/target/debug/bundle/msi/*.msi or src-tauri/target/debug/*.exe
```

### Health Check (Process Appearance)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    if [ -n "$STARTUP_PID" ] && kill -0 "$STARTUP_PID" 2>/dev/null; then
        READY=true
        break
    fi
    sleep 3
done
if [ "$READY" != "true" ]; then
    echo "Startup timeout exceeded for Tauri app."
    [ -n "$STARTUP_PID" ] && kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
[ -n "$STARTUP_PID" ] && kill -TERM "$STARTUP_PID" 2>/dev/null || true
killall "$(basename "$APP_BINARY")" 2>/dev/null || true
```

---

## Electron Desktop

### Framework Detection
```bash
if [ -f "${PROJECT_ROOT}/package.json" ] && grep -q '"electron"' "${PROJECT_ROOT}/package.json"; then
    DESKTOP_FRAMEWORK="electron"
fi
```

### Build (if required by project)
```bash
if grep -q '"electron:build"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm run electron:build >> "$STARTUP_LOGS_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Electron build failed."
        exit 1
    fi
fi
```

### Launch
```bash
if grep -q '"electron:dev"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm run electron:dev >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
    STARTUP_COMMAND="npm run electron:dev"
elif grep -q '"start"' "${PROJECT_ROOT}/package.json" 2>/dev/null; then
    cd "${PROJECT_ROOT}" && npm start >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
    STARTUP_COMMAND="npm start"
else
    cd "${PROJECT_ROOT}" && npx electron . >> "$STARTUP_LOGS_FILE" 2>&1 &
    STARTUP_PID=$!
    STARTUP_COMMAND="npx electron ."
fi
```

### Health Check (Process Appearance)
```bash
READY=false
while [ $(( $(date +%s) - START_TIME )) -lt "$STARTUP_TIMEOUT" ]; do
    if [ -n "$STARTUP_PID" ] && kill -0 "$STARTUP_PID" 2>/dev/null; then
        READY=true
        break
    fi
    sleep 3
done
if [ "$READY" != "true" ]; then
    echo "Startup timeout exceeded for Electron app."
    [ -n "$STARTUP_PID" ] && kill -TERM "$STARTUP_PID" 2>/dev/null || true
    exit 1
fi
```

### Teardown
```bash
[ -n "$STARTUP_PID" ] && kill -TERM "$STARTUP_PID" 2>/dev/null || true
killall Electron 2>/dev/null || true
killall "Electron Helper" 2>/dev/null || true
```

---

## Desktop GUI Automation (Computer-use / MCP)

### Tool Availability Check
```bash
GUI_TOOLS_AVAILABLE=false
GUI_TOOL_NAME=""

if [ -n "$CLAUDE_COMPUTER_USE_AVAILABLE" ] || command -v computer-use >/dev/null 2>&1; then
    GUI_TOOLS_AVAILABLE=true
    GUI_TOOL_NAME="computer-use"
fi

if [ -n "$MCP_GUI_SERVER_URL" ] || command -v mcp-gui >/dev/null 2>&1; then
    GUI_TOOLS_AVAILABLE=true
    GUI_TOOL_NAME="mcp-gui"
fi

if [ "$GUI_TOOLS_AVAILABLE" != "true" ]; then
    echo "ERROR: Desktop testing tools are not available."
    echo "Aborting desktop verification."
    exit 1
fi
```

### UI Element Verification Patterns

**Window presence** (computer-use):
- Capture screenshot, analyze for window title or frame matching the expected name.

**Window presence** (MCP accessibility tree):
```bash
# Query for window with title containing expected text
# Response: element found / not found
```

**Button/element presence**:
- computer-use: Look for visual element matching label/shape in screenshot.
- MCP: Query accessibility tree for role=button and name containing expected label.

### Workflow Simulation Patterns

| Workflow Step | computer-use Action | MCP Action |
|---------------|---------------------|------------|
| Click button | Move cursor to button coordinates, click | Send click event to accessible element by name/role |
| Fill input | Click field, type characters | Focus accessible element, send text input |
| Toggle switch | Click toggle visual position | Send click to checkbox/switch accessible element |
| Select dropdown | Click dropdown, click option | Expand combobox, select option by name |
| Navigate menu | Click menu label, click item | Open menu bar, click menu item by name |

### Screenshot Capture (Per Step)

```bash
ARTIFACT_DIR="${SPEC_FOLDER}/e2e-artifacts"
mkdir -p "$ARTIFACT_DIR"

SCREENSHOT_PATH="${ARTIFACT_DIR}/screenshot-$(date +%s)-ac-${AC_ID}-step-${STEP_NUM}.png"
# computer-use: save captured screenshot to SCREENSHOT_PATH
# MCP: invoke screenshot method and save returned image to SCREENSHOT_PATH
```

Screenshots MUST be captured at every step (before action, after action, on assertion).

### Per-Test Timeout Enforcement

```bash
TEST_TIMEOUT_SEC=60
TEST_START_TIME=$(date +%s)

while [ "$TEST_STATUS" = "RUNNING" ]; do
    if [ $(( $(date +%s) - TEST_START_TIME )) -gt "$TEST_TIMEOUT_SEC" ]; then
        echo "FAIL: Test hung and was terminated after ${TEST_TIMEOUT_SEC}s timeout"
        STATUS="FAILED"
        TEST_STATUS="TIMEOUT"
        break
    fi
    # execute next step
done
```

If timeout occurs:
- Mark AC as `FAILED`
- Capture final timeout screenshot
- Record evidence: "Test hung and was terminated after ${TEST_TIMEOUT_SEC}s timeout"
- Reset app state before next AC

### Error Handling

- **No tools available**: Abort with clear error. Do not silently skip.
- **Build failure**: Capture logs, report, abort before launch.
- **App crash during test**: Mark AC `FAILED`, capture logs, attempt restart for next AC.
- **Window/element not found**: Mark AC `FAILED`, capture desktop screenshot.

---

## Playwright Test Execution

### Verify Installation

```bash
PLAYWRIGHT_VERSION=$(npx playwright --version 2>/dev/null || echo "")

if [ -z "$PLAYWRIGHT_VERSION" ]; then
    echo "ERROR: Playwright is not installed."
    echo "Install instructions:"
    echo "  npm install -D @playwright/test"
    echo "  npx playwright install chromium"
    echo ""
    echo "Skipping all Web SPA tests. Mark SPA acceptance criteria as MANUAL CHECK REQUIRED."
    # Do NOT auto-install; report gap and continue with other test categories
fi

echo "Playwright version: $PLAYWRIGHT_VERSION"
```

### Headless Browser Launch and Navigation

Generate a temporary Node.js script and execute it. Browser is **headless by default**.

```bash
DEV_SERVER_URL="http://localhost:${PORT}"
TEST_SCRIPT="$(mktemp /tmp/e2e-spa-XXXXXX.js)"

cat > "$TEST_SCRIPT" << 'PLAYWRIGHT_EOF'
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    userAgent: 'DeveloperKit-E2E/1.0'
  });
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:5173');
    // ... actions and assertions ...
    console.log('RESULT: PASS');
  } catch (error) {
    console.error('RESULT: FAIL:', error.message);
    // Screenshot on failure
    const screenshotPath = '/tmp/e2e-artifacts/screenshot-' + Date.now() + '.png';
    await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
    console.error('SCREENSHOT:', screenshotPath);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
PLAYWRIGHT_EOF

node "$TEST_SCRIPT"
rm -f "$TEST_SCRIPT"
```

### UI Interaction Patterns

| Action | Playwright Code |
|--------|-----------------|
| Click element | `await page.click('[data-testid=refresh]');` |
| Fill input | `await page.fill('#username', 'testuser');` |
| Type into input | `await page.type('input[name=search]', 'query');` |
| Select option | `await page.selectOption('select[name=country]', 'US');` |
| Submit form | `await page.click('button[type=submit]');` |
| Navigate to path | `await page.goto('http://localhost:${PORT}/dashboard');` |
| Hover over element | `await page.hover('.tooltip-trigger');` |
| Scroll to element | `await page.locator('[data-testid=footer]').scrollIntoViewIfNeeded();` |

**Selector precedence** (most stable first):
1. `[data-testid=...]`
2. `#id`
3. `.class-name`
4. `[name=...]`
5. `text=...` (fallback)

### DOM Assertion Patterns

| Assertion | Playwright Code |
|-----------|-----------------|
| Element has exact text | `await expect(page.locator('[data-testid=title]')).toHaveText('Expected Title');` |
| Element contains text | `await expect(page.locator('.message')).toContainText('partial text');` |
| Body contains text | `await expect(page.locator('body')).toContainText('some text');` |
| Table row count | `expect(await page.locator('table tbody tr').count()).toBe(5);` |
| URL is exact | `expect(page.url()).toBe('http://localhost:${PORT}/dashboard');` |
| URL contains fragment | `expect(page.url()).toContain('/settings');` |
| Element is visible | `await expect(page.locator('[data-testid=modal]')).toBeVisible();` |
| Element is hidden | `await expect(page.locator('[data-testid=spinner]')).toBeHidden();` |

### Screenshot Capture on Failure

```javascript
// Inside the catch block of the test script
const screenshotPath = '/path/to/e2e-artifacts/screenshot-' + Date.now() + '-ac-AC-019.png';
await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
console.error('SCREENSHOT:', screenshotPath);
```

Directory preparation:
```bash
ARTIFACT_DIR="${SPEC_FOLDER}/e2e-artifacts"
mkdir -p "$ARTIFACT_DIR"
```

### Per-Test Timeout Enforcement

Each test MUST have a timeout to prevent indefinite hangs (REQ-NR007). Set page-level defaults and wrap execution with the `timeout` command:

```bash
TEST_TIMEOUT_SEC=30

# Inside the generated script
page.setDefaultTimeout(${TEST_TIMEOUT_SEC}000);
page.setDefaultNavigationTimeout(${TEST_TIMEOUT_SEC}000);

# Wrap execution
if timeout --signal=TERM $((TEST_TIMEOUT_SEC + 5)) node "$TEST_SCRIPT"; then
    STATUS="VERIFIED"
else
    EXIT_CODE=$?
    if [ "$EXIT_CODE" -eq 124 ]; then
        echo "FAIL: Test hung and was terminated after ${TEST_TIMEOUT_SEC}s timeout"
    fi
    STATUS="FAILED"
fi
```

### Edge Cases

#### Playwright Not Installed

```bash
if ! npx playwright --version >/dev/null 2>&1; then
    echo "ERROR: Playwright is not installed."
    echo "Suggestion: npm install -D @playwright/test && npx playwright install chromium"
    echo "Skipping SPA tests. Marking ACs as MANUAL CHECK REQUIRED."
    # Do not abort; continue with other test categories
fi
```

#### Dev Server Not Running

If `page.goto()` throws a connection error, the catch block records:
```
RESULT: FAIL: net::ERR_CONNECTION_REFUSED at http://localhost:5173
```

Report to user:
```bash
echo "Dev server not reachable at ${DEV_SERVER_URL}."
echo "Ensure the server is running before verification."
```

#### Browser Launch Failure

If Chromium system dependencies are missing:
```bash
echo "Browser launch failed. Missing system dependencies?"
echo "Suggestion: npx playwright install-deps chromium"
```

### Complete Inline Test Example

```bash
PORT=5173
AC_ID="AC-016"
ARTIFACT_DIR="./e2e-artifacts"
mkdir -p "$ARTIFACT_DIR"

TEST_SCRIPT="$(mktemp /tmp/e2e-spa-XXXXXX.js)"
cat > "$TEST_SCRIPT" << EOF
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.setDefaultTimeout(30000);
  page.setDefaultNavigationTimeout(30000);
  try {
    await page.goto('http://localhost:${PORT}');
    await page.click('[data-testid=refresh]');
    const rowCount = await page.locator('table tbody tr').count();
    if (rowCount === 0) throw new Error('Table has no rows');
    console.log('RESULT: PASS');
  } catch (error) {
    console.error('RESULT: FAIL:', error.message);
    const ss = '${ARTIFACT_DIR}/screenshot-' + Date.now() + '-${AC_ID}.png';
    await page.screenshot({ path: ss, fullPage: true }).catch(() => {});
    console.error('SCREENSHOT:', ss);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
EOF

timeout --signal=TERM 35 node "$TEST_SCRIPT"
rm -f "$TEST_SCRIPT"
```

---

## curl Dependency Check

```bash
# Verify curl is installed
if ! command -v curl >/dev/null 2>&1; then
    echo "ERROR: curl is not installed."
    echo "Install instructions:"
    echo "  macOS:    brew install curl"
    echo "  Ubuntu:   sudo apt-get install curl"
    echo "  Windows:  choco install curl   or   winget install curl"
    exit 1
fi

# Verify jq is installed (optional but recommended for JSON assertions)
if ! command -v jq >/dev/null 2>&1; then
    echo "WARNING: jq is not installed. JSON body assertions will fall back to grep (less precise)."
    echo "Install instructions:"
    echo "  macOS:    brew install jq"
    echo "  Ubuntu:   sudo apt-get install jq"
    echo "  Windows:  choco install jq   or   winget install jqlang.jq"
fi
```

## Auth Credential Discovery

Scan project files for `E2E_AUTH_TOKEN`, `E2E_USERNAME`, `E2E_PASSWORD` (in order):

```bash
# .env files
[ -f "${PROJECT_ROOT}/.env.test" ] && \
  export $(grep -E '^(E2E_AUTH_TOKEN|E2E_USERNAME|E2E_PASSWORD)=' "${PROJECT_ROOT}/.env.test" | xargs)
[ -f "${PROJECT_ROOT}/.env.local" ] && \
  export $(grep -E '^(E2E_AUTH_TOKEN|E2E_USERNAME|E2E_PASSWORD)=' "${PROJECT_ROOT}/.env.local" | xargs)

# Spring Boot YAML
[ -f "${PROJECT_ROOT}/src/main/resources/application-test.yml" ] && {
  E2E_AUTH_TOKEN=$(grep -A2 'e2e:' "${PROJECT_ROOT}/src/main/resources/application-test.yml" | grep 'auth-token:' | sed 's/.*: *//')
  E2E_USERNAME=$(grep -A2 'e2e:' "${PROJECT_ROOT}/src/main/resources/application-test.yml" | grep 'username:' | sed 's/.*: *//')
  E2E_PASSWORD=$(grep -A2 'e2e:' "${PROJECT_ROOT}/src/main/resources/application-test.yml" | grep 'password:' | sed 's/.*: *//')
}

# Spring Boot properties
[ -f "${PROJECT_ROOT}/src/main/resources/application-test.properties" ] && {
  E2E_AUTH_TOKEN=$(grep '^e2e.auth-token=' "${PROJECT_ROOT}/src/main/resources/application-test.properties" | cut -d= -f2-)
  E2E_USERNAME=$(grep '^e2e.username=' "${PROJECT_ROOT}/src/main/resources/application-test.properties" | cut -d= -f2-)
  E2E_PASSWORD=$(grep '^e2e.password=' "${PROJECT_ROOT}/src/main/resources/application-test.properties" | cut -d= -f2-)
}

# JSON credentials file
[ -f "${PROJECT_ROOT}/e2e.credentials.json" ] && {
  E2E_AUTH_TOKEN=$(jq -r '.E2E_AUTH_TOKEN // empty' "${PROJECT_ROOT}/e2e.credentials.json")
  E2E_USERNAME=$(jq -r '.E2E_USERNAME // empty' "${PROJECT_ROOT}/e2e.credentials.json")
  E2E_PASSWORD=$(jq -r '.E2E_PASSWORD // empty' "${PROJECT_ROOT}/e2e.credentials.json")
}
```

## curl Patterns for REST API Testing

### Basic GET (no -X flag)
```bash
curl -s -w "\n%{http_code}" -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/resource"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
echo "Status: ${HTTP_CODE}"
```

### POST with JSON Body
```bash
curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/resource"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

### PUT with JSON Body
```bash
curl -s -w "\n%{http_code}" -X PUT \
  -H "Content-Type: application/json" \
  -d '{"key":"updated"}' \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/resource/123"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

### PATCH with JSON Body
```bash
curl -s -w "\n%{http_code}" -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}' \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/resource/123"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

### DELETE
```bash
curl -s -w "\n%{http_code}" -X DELETE \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/resource/123"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

### Bearer Token Authentication
```bash
curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer ${E2E_AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/protected"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

### Basic Authentication (username/password)
```bash
curl -s -w "\n%{http_code}" \
  -u "${E2E_USERNAME}:${E2E_PASSWORD}" \
  -H "Content-Type: application/json" \
  -o /tmp/e2e_resp.json \
  "http://localhost:${PORT}/api/protected"
HTTP_CODE=$(tail -n 1 /tmp/e2e_resp.json)
```

## Assertion Patterns

### Status Code Assertion
```bash
EXPECTED_STATUS=201
HTTP_CODE=$(curl -s -w "\n%{http_code}" -o /tmp/e2e_resp.json <curl_args> | tail -n 1)
if [ "${HTTP_CODE}" -eq "${EXPECTED_STATUS}" ]; then
    echo "PASS: Status ${HTTP_CODE}"
else
    echo "FAIL: Expected ${EXPECTED_STATUS}, got ${HTTP_CODE}"
    STATUS="FAILED"
fi
```

### Content-Type Header Assertion
```bash
EXPECTED_CT="application/json"
ACTUAL_CT=$(curl -s -o /dev/null -D - <curl_args> | grep -i "Content-Type:" | head -1 | sed 's/Content-Type: //i' | tr -d '\r')
if echo "${ACTUAL_CT}" | grep -qi "${EXPECTED_CT}"; then
    echo "PASS: Content-Type ${ACTUAL_CT}"
else
    echo "FAIL: Expected Content-Type '${EXPECTED_CT}', got '${ACTUAL_CT}'"
    STATUS="FAILED"
fi
```

### JSON Body Assertions (jq)
```bash
# Field exists
jq -e '.fieldName' /tmp/e2e_resp.json >/dev/null && echo "PASS" || echo "FAIL: Missing .fieldName"

# Field equals expected value
jq -e '.fieldName == "expectedValue"' /tmp/e2e_resp.json >/dev/null && echo "PASS" || echo "FAIL: .fieldName mismatch"

# Array is non-empty
jq -e '(.items | length) > 0' /tmp/e2e_resp.json >/dev/null && echo "PASS" || echo "FAIL: .items is empty"

# Nested field exists
jq -e '.data.user.email' /tmp/e2e_resp.json >/dev/null && echo "PASS" || echo "FAIL: Missing .data.user.email"

# Numeric comparison
jq -e '.count >= 1' /tmp/e2e_resp.json >/dev/null && echo "PASS" || echo "FAIL: .count too low"
```

### JSON Body Assertions (grep fallback — no jq)
```bash
# Field presence
grep -q '"fieldName"' /tmp/e2e_resp.json && echo "PASS" || echo "FAIL: Missing fieldName"

# Value presence
grep -q '"expectedValue"' /tmp/e2e_resp.json && echo "PASS" || echo "FAIL: expectedValue not found"
```

## No-Retry Policy

Each curl test is executed **exactly once**. Do NOT wrap curl in retry loops.

```bash
# CORRECT: single execution
HTTP_CODE=$(curl -s -w "\n%{http_code}" -o /tmp/e2e_resp.json <curl_args> | tail -n 1)

# INCORRECT: do NOT use --retry or loops
# curl --retry 3 ...   # FORBIDDEN by REQ-NR008
```

## Manual Check Required

If an `[IMP]` AC lacks a parseable endpoint path or HTTP method, mark it `MANUAL CHECK REQUIRED` and continue:

```bash
if [ -z "$PARSED_PATH" ] || [ -z "$PARSED_METHOD" ]; then
    echo "MANUAL CHECK REQUIRED: AC-${AC_ID} does not contain a parseable endpoint."
    STATUS="MANUAL CHECK REQUIRED"
    continue
fi
```

---

## Port Availability Check

```bash
# Linux/macOS
nc -z localhost ${PORT} && echo "Open" || echo "Closed"

# Alternative
lsof -i:${PORT} >/dev/null 2>&1 && echo "In use" || echo "Free"
```
