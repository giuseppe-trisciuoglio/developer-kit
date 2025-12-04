---
description: Create a checkpoint - commit changes, update progress log, leave clean state for next session
allowed-tools: Read, Write, Edit, Bash(git:*)
argument-hint: [summary-of-work-done]
---

# Long-Running Agent - Create Checkpoint

Create a checkpoint at the end of a coding session. This ensures the next agent can pick up where you left off.

## Summary of Work Done

$ARGUMENTS

## Checkpoint Protocol

Execute these steps to leave the environment in a clean state:

### Step 1: Verify Clean State

Before creating a checkpoint, ensure:

1. **No broken tests**: Run the test suite
2. **App runs**: Start the dev server and verify basic functionality
3. **No syntax errors**: Code compiles/lints without errors

If there are issues, FIX THEM before proceeding.

### Step 2: Stage and Commit Changes

Review what changed:

```bash
git status
git diff --stat
```

Create a descriptive commit:

```bash
git add -A
git commit -m "feat: [brief description of main change]

- Detail 1
- Detail 2
- Detail 3

Session checkpoint - app in working state"
```

### Step 3: Update Progress Log

Append to `.lra/progress.txt`:

```markdown
---

### Session [N] - [Date] - [Brief Title]

**Feature Worked On**: [Feature ID] - [Description]

**Accomplished**:
- [What was done]
- [What was done]

**Status**: [Complete / In Progress / Blocked]

**Notes for Next Session**:
- [Important context]
- [Any gotchas or warnings]
- [Suggested next steps]

**Commits This Session**:
- [commit hash] - [message]
```

### Step 4: Final Git Status

Confirm everything is committed:

```bash
git status
git log --oneline -5
```

## Output

Provide a session summary:

```
═══════════════════════════════════════════════════════════
                    SESSION CHECKPOINT
═══════════════════════════════════════════════════════════

📋 Session Summary
   Feature: F012 - User authentication flow
   Status: COMPLETE ✓

📝 Changes Made
   - Implemented login endpoint
   - Added JWT token generation
   - Created auth middleware
   - Added unit tests for auth service

📊 Project Progress
   Features: 12/42 completed (29%)
   
   By Priority:
   - Critical: 4/5 done
   - High: 6/15 done
   - Medium: 2/18 done
   - Low: 0/4 done

💾 Git Status
   Commit: abc1234 - feat(auth): implement user login flow
   Branch: main
   Working tree: clean

📌 Notes for Next Agent
   - Auth is working, next implement password reset
   - Redis session store not yet configured
   - See .lra/progress.txt for full history

═══════════════════════════════════════════════════════════
                    READY FOR NEXT SESSION
═══════════════════════════════════════════════════════════
```

## Important

- **NEVER leave the codebase in a broken state**
- **ALWAYS update progress.txt with context for the next agent**
- **ALWAYS commit with descriptive messages**
- This checkpoint allows context window transitions to be seamless

## Execution Instructions

**Agent Selection**: To execute this LRA task, use the following approach:
- Primary: Use `general-purpose` agent with task management and state persistence capabilities
- Or use `plan` agent for complex multi-step workflows
