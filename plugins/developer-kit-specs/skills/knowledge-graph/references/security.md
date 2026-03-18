# Security - Knowledge Graph

Security considerations and best practices for Knowledge Graph operations.

## Core Security Principles

### 1. Path Validation

**Principle:** Only read KG from `docs/specs/[ID]/` paths.

**Why:** Prevents path traversal attacks and unauthorized file access.

**Implementation:**
```python
def validate_kg_path(path):
    """
    Validate that KG path is within docs/specs/ directory.
    """
    # Must start with docs/specs/
    if not path.startswith("docs/specs/"):
        raise ValueError(f"Invalid KG path: {path}")

    # No path traversal allowed
    if ".." in path:
        raise ValueError(f"Path traversal not allowed: {path}")

    # Resolve to absolute path
    real_path = Path(path).resolve()
    project_root = Path.cwd()

    # Must be within project root
    if not str(real_path).startswith(str(project_root)):
        raise ValueError(f"Path outside project: {path}")

    return real_path
```

**What this prevents:**
- Path traversal: `../../etc/passwd`
- Absolute path escape: `/etc/passwd`
- Symbolic link attacks: `symlink-to-sensitive-file`

---

### 2. JSON Injection Prevention

**Principle:** Validate all updates before merging into KG.

**Why:** Prevents malicious JSON from corrupting KG or causing unexpected behavior.

**Implementation:**
```python
import json

def validate_json_structure(data):
    """
    Validate that data matches expected KG structure.
    """
    # Must be a dict
    if not isinstance(data, dict):
        raise ValueError("KG data must be a dictionary")

    # Must have required top-level keys
    required_keys = ['metadata', 'patterns', 'components', 'apis']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    # Validate metadata structure
    if 'version' in data['metadata']:
        # Version should be a string like "1.0"
        if not isinstance(data['metadata']['version'], str):
            raise ValueError("Version must be a string")

    # Validate arrays are arrays
    array_keys = ['patterns', 'components', 'apis', 'provides']
    for key in array_keys:
        if key in data and key != 'metadata':
            if not isinstance(data[key], dict):
                raise ValueError(f"{key} must be a dictionary")

    return True
```

**What this prevents:**
- Malformed JSON structures
- Unexpected data types
- Missing required fields
- Invalid nested structures

---

### 3. Secrets Exclusion

**Principle:** KG should NOT contain passwords, API keys, tokens, or other sensitive data.

**Why:** KG files are committed to git and should not contain secrets.

**What to exclude:**
- Passwords
- API keys
- Access tokens
- Session IDs
- Private keys
- Database connection strings
- Credentials of any kind

**Implementation:**
```python
import re

SENSITIVE_PATTERNS = [
    r'password\s*[:=]\s*\S+',  # password: secret, password=secret
    r'api[_-]?key\s*[:=]\s*\S+',  # api_key: xxx
    r'token\s*[:=]\s*\S+',  # token: xxx
    r'secret\s*[:=]\s*\S+',  # secret: xxx
    r'-----BEGIN\s+(PRIVATE\s+KEY|RSA\s+PRIVATE)-----',  # Private keys
]

def contains_secrets(text):
    """
    Check if text contains potential secrets.
    """
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def validate_no_secrets(data):
    """
    Validate that KG data doesn't contain secrets.
    """
    # Convert to JSON string for checking
    json_str = json.dumps(data)

    if contains_secrets(json_str):
        raise ValueError("KG data appears to contain secrets")

    return True
```

**What to store instead:**
- Component names (not passwords)
- API endpoints (not keys)
- Configuration structure (not values)
- Schema definitions (not data)

---

### 4. Git Safety

**Principle:** KG files are designed to be committed to git (no sensitive data by design).

**What's safe to commit:**
- Architecture patterns
- Component names and locations
- API endpoint definitions
- Conventions and best practices
- Technology stack information

**What's NOT safe to commit:**
- Credentials (already prevented by secrets exclusion)
- User data
- Sensitive configuration values
- Production secrets

**Verification:**
```bash
# Check if KG would add sensitive data to git
git add docs/specs/*/knowledge-graph.json
git diff --cached --check  # Fails if sensitive data detected
```

---

### 5. Source Code Safety

**Principle:** Knowledge Graph skill does NOT modify source code files.

**What it DOES:**
- Create/update `knowledge-graph.json` files
- Read source files for analysis
- Query source files for validation

**What it does NOT do:**
- Modify `.java`, `.ts`, `.py` files
- Write to source directories
- Delete source files
- Execute code in source files

**Enforcement:**
```python
SAFE_EXTENSIONS = {'.json', '.md'}  # Only safe file extensions

def validate_operation(target_file):
    """
    Validate that operation only targets safe files.
    """
    ext = Path(target_file).suffix.lower()

    if ext not in SAFE_EXTENSIONS:
        raise PermissionError(
            f"Cannot modify {ext} files. "
            f"Knowledge Graph only creates JSON and Markdown files."
        )

    # Must be knowledge-graph.json or similar
    if 'knowledge-graph' not in target_file:
        raise PermissionError(
            f"Can only create knowledge-graph files, not {target_file}"
        )

    return True
```

---

## Security Threats and Mitigations

### Threat 1: Path Traversal

**Attack:** User provides path like `../../etc/passwd` to access system files.

**Mitigation:**
- Validate paths start with `docs/specs/`
- Disallow `..` in paths
- Resolve to absolute path and check it's within project root

**Example:**
```python
# Attack attempt
update_kg("../../../etc/passwd", malicious_data)

# Defense
validate_kg_path("../../../etc/passwd")
# Raises: ValueError("Path traversal not allowed")
```

---

### Threat 2: JSON Injection

**Attack:** Malicious JSON with unexpected structure causes exploit.

**Mitigation:**
- Validate JSON structure before parsing
- Use schema validation
- Reject unexpected keys or types

**Example:**
```python
# Attack attempt
malicious_json = '{"__proto__": {"polluted": true}}'

# Defense
validate_json_structure(json.loads(malicious_json))
# Raises: ValueError("Invalid JSON structure")
```

---

### Threat 3: Secrets Leakage

**Attack:** User tries to store passwords/tokens in KG.

**Mitigation:**
- Scan for secret patterns before writing
- Reject updates containing secrets
- Warn user about sensitive data

**Example:**
```python
# Attack attempt
data = {"api": {"credentials": {"password": "secret123"}}}

# Defense
validate_no_secrets(data)
# Raises: ValueError("KG data appears to contain secrets")
```

---

### Threat 4: Code Execution

**Attack:** User tries to make KG skill execute arbitrary code.

**Mitigation:**
- KG skill never executes source code
- Only reads files for analysis
- Never writes to source directories

**Example:**
```python
# Attack attempt
extract_and_execute("malicious.java")

# Defense
# KG skill doesn't have execute capability
# Only has Read, Write, Edit, Grep, Glob, Bash tools
# Write tool validates it only creates .json files
```

---

### Threat 5: Data Exfiltration

**Attack:** Use KG to extract sensitive codebase information.

**Mitigation:**
- KG only stores structural information (patterns, components)
- Doesn't store actual code
- Doesn't store sensitive configuration values
- Validate no secrets before writing

**What's stored:**
- ✅ "UserService class exists in src/auth/UserService.ts"
- ❌ "UserService contains password validation logic with secret key: abc123"

---

## Secure Implementation Guidelines

### 1. Input Validation

**Always validate:**
- File paths (must be within docs/specs/)
- JSON structure (must match schema)
- Data types (must be expected types)
- Array lengths (prevent DoS via huge arrays)

**Example:**
```python
def validate_update(updates):
    # Validate structure
    validate_json_structure(updates)

    # Validate no secrets
    validate_no_secrets(updates)

    # Validate array sizes (prevent DoS)
    for key in updates:
        if isinstance(updates[key], list):
            if len(updates[key]) > 10000:
                raise ValueError(f"Array too large: {key}")

    return True
```

---

### 2. Principle of Least Privilege

**KG skill capabilities:**
- ✅ Read source files for analysis
- ✅ Create/update KG JSON files
- ✅ Query KG for information
- ❌ Modify source code
- ❌ Execute arbitrary code
- ❌ Access files outside project

---

### 3. Defense in Depth

**Multiple layers of security:**
1. Path validation (prevent path traversal)
2. JSON validation (prevent injection)
3. Secrets detection (prevent leakage)
4. File type restrictions (prevent code modification)
5. Operation scope (prevent unintended actions)

---

### 4. Fail Securely

**On error:**
- Don't write partial/corrupted data
- Don't reveal internal paths
- Don't expose error details that aid attacks
- Log security events for audit

**Example:**
```python
try:
    update_kg(path, data)
except ValueError as e:
    # Log detailed error internally
    logger.error(f"KG update failed: {e}", exc_info=True)
    # Return generic error to user
    raise ValueError("Invalid KG data provided")
```

---

## Security Best Practices

### 1. Never Store Credentials

**Bad:**
```json
{
  "database": {
    "password": "secret123"
  }
}
```

**Good:**
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "mydb"
  }
}
```

---

### 2. Validate All Inputs

**Bad:**
```python
def update_kg(path, data):
    write(path, data)  # No validation!
```

**Good:**
```python
def update_kg(path, data):
    validate_path(path)
    validate_json_structure(data)
    validate_no_secrets(data)
    write(path, data)
```

---

### 3. Use Whitelists, Not Blacklists

**Bad:**
```python
# Blacklist approach (misses new threats)
if path not in ['etc/passwd', 'etc/shadow']:
    process(path)
```

**Good:**
```python
# Whitelist approach (only allows safe paths)
if path.startswith('docs/specs/'):
    process(path)
```

---

### 4. Log Security Events

**What to log:**
- Invalid path attempts
- Secret detection events
- JSON validation failures
- Unusual operations

**Example:**
```python
logger.warning(f"Security: Invalid path attempt: {path}")
logger.error(f"Security: Secrets detected in KG update")
logger.info(f"Security: KG update validated successfully")
```

---

## Security Checklist

Before writing to KG:

- [ ] Path validated (starts with docs/specs/)
- [ ] JSON structure validated
- [ ] No secrets detected
- [ ] File type validated (.json only)
- [ ] Operation within scope (read/create/update KG)
- [ ] Size reasonable (< 1 MB)
- [ ] Arrays not suspiciously large
- [ ] No executable code in data

---

## Security Auditing

### Regular Audits

**What to check:**
1. All KG files in git contain no secrets
2. No KG files outside docs/specs/
3. No KG files with suspicious content
4. All KG operations follow security rules

**Audit script:**
```bash
#!/bin/bash
# Audit KG files for security

echo "Auditing Knowledge Graph files..."

# Find all KG files
find docs/specs -name "knowledge-graph.json" | while read file; do
    echo "Checking: $file"

    # Check for secrets
    if grep -iE "password|api[_-]?key|token|secret" "$file"; then
        echo "⚠️  WARNING: Possible secrets in $file"
    fi

    # Check file location
    if [[ ! "$file" == docs/specs/*/knowledge-graph.json ]]; then
        echo "⚠️  WARNING: Unusual KG location: $file"
    fi

    # Check file size
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    if [ $size -gt 1048576 ]; then
        echo "⚠️  WARNING: Large KG file (>1MB): $file"
    fi
done

echo "Audit complete."
```

---

## Summary

**Core security principles:**
1. Path validation (only docs/specs/)
2. JSON injection prevention (validate structure)
3. Secrets exclusion (no credentials)
4. Git safety (no sensitive data)
5. Source code safety (no modifications)

**Key threats mitigated:**
- Path traversal attacks
- JSON injection
- Secrets leakage
- Code execution
- Data exfiltration

**Security best practices:**
- Validate all inputs
- Use whitelists over blacklists
- Fail securely
- Log security events
- Regular security audits

**Remember:** Knowledge Graph stores structural information only, never credentials or sensitive data.
