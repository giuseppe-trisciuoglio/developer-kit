---
description: Recover from a broken state - diagnose issues, revert if needed, restore working state
argument-hint: [issue-description]
allowed-tools: Read, Write, Edit, Bash
---

# Long-Running Agent - Recover from Broken State

Use this command when the project is in a broken state and needs recovery.

## Current Context

- Git Status: !`git status`
- Recent Commits: !`git log --oneline -10`

## Recovery Protocol

### Step 1: Diagnose the Problem

First, understand what's broken:

1. **Check for syntax errors**:
   ```bash
   # For JS/TS projects
   npm run lint 2>&1 | head -50
   
   # For Java projects  
   mvn compile 2>&1 | head -50
   
   # For Python projects
   python -m py_compile main.py
   ```

2. **Check for failing tests**:
   ```bash
   npm test 2>&1 | tail -50
   # or
   mvn test 2>&1 | tail -50
   ```

3. **Try to start the app**:
   ```bash
   # Check init script
   cat .lra/init.sh
   ```

4. **Check progress log for context**:
   ```bash
   tail -50 .lra/progress.txt
   ```

### Step 2: Identify the Breaking Change

Look at git history to find when things broke:

```bash
# See recent changes
git log --oneline -10

# See what changed in last commit
git show --stat HEAD

# See diff of specific file
git diff HEAD~1 -- [problematic-file]
```

### Step 3: Recovery Options

Choose the appropriate recovery strategy:

#### Option A: Quick Fix
If the issue is small and obvious:
1. Fix the specific issue
2. Test to confirm fix
3. Commit the fix
4. Update progress.txt with what happened

#### Option B: Revert Last Commit
If the last commit broke things:
```bash
# See what will be reverted
git show HEAD

# Revert (creates new commit)
git revert HEAD --no-edit

# Or soft reset to keep changes staged
git reset --soft HEAD~1
```

#### Option C: Revert to Known Good State
If multiple commits are problematic:
```bash
# Find last working commit
git log --oneline -20

# Reset to that commit (keeps changes)
git reset --soft [commit-hash]

# Or hard reset (discards changes)
git reset --hard [commit-hash]
```

#### Option D: Stash and Investigate
If you need to investigate without losing work:
```bash
git stash
# investigate...
git stash pop  # restore changes
```

### Step 4: Verify Recovery

After applying a fix:

1. **Run tests**:
   ```bash
   npm test
   ```

2. **Start the app**:
   ```bash
   source .lra/init.sh
   ```

3. **Verify core functionality**:
   - Can the app start?
   - Do basic operations work?
   - Are there any console errors?

### Step 5: Document the Recovery

Update `.lra/progress.txt`:

```markdown
---

### Recovery Session - [Date]

**Problem**: [What was broken]
**Cause**: [Why it broke]
**Solution**: [How it was fixed]
**Commits Reverted**: [If any]

**Lessons Learned**:
- [What to avoid in future]

---
```

### Step 6: Update Feature Status

If a feature was incorrectly marked as passed:

```bash
# Use the mark-feature command
/developer-kit:devkit.lra.mark-feature [feature-id] failed [reason for failure]
```

## Output

Provide a recovery report:

```
═══════════════════════════════════════════════════════════
                    RECOVERY COMPLETE
═══════════════════════════════════════════════════════════

🔍 Problem Identified
   Issue: TypeError in auth middleware
   Cause: Undefined variable after refactor
   Affected: F022 - User login flow

🔧 Recovery Action
   Strategy: Quick Fix
   Changes: Fixed undefined check in middleware
   Commit: def5678 - fix(auth): handle undefined user object

✅ Verification
   Tests: All passing (42/42)
   App: Starts successfully
   Core functionality: Working

📝 Updated Records
   - progress.txt: Recovery documented
   - F022 status: Remains passed (fix was minor)

💡 Recommendation
   Continue with normal workflow using /developer-kit:devkit.lra.start-session

═══════════════════════════════════════════════════════════
```

## Important

- **DON'T PANIC**: Git history preserves everything
- **ALWAYS test** after recovery
- **DOCUMENT** what went wrong for future agents
- **UPDATE** feature status if a "passed" feature was actually broken

## Execution Instructions

**Agent Selection**: To execute this LRA task, use the following approach:
- Primary: Use `general-purpose` agent with task management and state persistence capabilities
- Or use `plan` agent for complex multi-step workflows
