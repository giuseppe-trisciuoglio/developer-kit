# Long-Running Agent (LRA) Workflow Guide

Structured approach for AI agents to work effectively on complex projects spanning multiple context windows (hours/days). Based on [Anthropic's research](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [LRA Commands](#lra-commands)
4. [Workflow Example](#workflow-example)
5. [File Structure](#file-structure)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### The Problem

AI agents working across multiple context windows face challenges:
- **Context amnesia**: Each session has no memory of previous work
- **One-shot tendency**: Attempting too much at once
- **Incomplete features**: Work spans sessions without clear handoffs
- **Testing gaps**: Features marked complete without proper testing

### The Solution

LRA workflow addresses this with:
1. **Structured initialization**: Feature list, progress tracking, environment setup
2. **Session protocol**: Read context → select feature → test → checkpoint
3. **Atomic features**: One feature per session, fully tested
4. **Clean state**: Always leave codebase in working condition

### Key Benefits

- ✅ Continuity across sessions
- ✅ Progress tracking with atomic features
- ✅ Clean handoffs between sessions
- ✅ Recovery capability from broken states

---

## Quick Start

### 1. Initialize Project

```bash
/devkit.lra.init "Project description"
```

Creates `.lra/` directory with:
- `feature-list.json` - All features with status
- `progress.txt` - Session log
- `init.sh` - Environment setup

### 2. Start Each Session

```bash
/devkit.lra.start-session
```

Protocol executed:
1. Load progress and features
2. Check git status and health
3. Select next feature
4. Display implementation approach

### 3. During Session

Implement ONE feature fully:
- Code implementation
- Unit tests
- Integration tests
- Manual verification

### 4. End Session

```bash
/devkit.lra.mark-feature [feature-id] passed
/devkit.lra.checkpoint "Session summary"
```

---

## LRA Commands

### `/devkit.lra.init`

**Purpose**: Initialize LRA environment for multi-session development.

**Usage:**
```bash
/devkit.lra.init [project-description]
```

**Example:**
```bash
/devkit.lra.init "Chat app with conversation history, user auth, and AI responses"
```

**Creates:**
- Feature list with acceptance criteria
- Progress tracking file
- Environment init script
- Initial git commit

---

### `/devkit.lra.start-session`

**Purpose**: Start coding session with full context restoration.

**Usage:**
```bash
/devkit.lra.start-session
```

**Startup Protocol:**
1. Confirm working directory
2. Load `.lra/progress.txt`
3. Review git commits and status
4. Load `.lra/feature-list.json`
5. Run health checks
6. Display status and next feature

**Output shows:**
- Project progress (X of Y features)
- Last session summary
- Current app state
- Selected feature for this session

---

### `/devkit.lra.add-feature`

**Purpose**: Add discovered feature during development.

**Usage:**
```bash
/devkit.lra.add-feature [category] [priority] [description]
```

**Categories:** `core`, `ui`, `api`, `database`, `auth`, `testing`, `other`

**Priorities:** `critical`, `high`, `medium`, `low`

**Examples:**
```bash
/devkit.lra.add-feature api high "Add user preferences endpoint"
/devkit.lra.add-feature auth critical "Implement 2FA"
/devkit.lra.add-feature testing high "Add E2E checkout tests"
```

---

### `/devkit.lra.mark-feature`

**Purpose**: Mark feature as completed or failed.

**Usage:**
```bash
/devkit.lra.mark-feature [feature-id] [passed|failed]
```

**Example:**
```bash
/devkit.lra.mark-feature F001 passed
/devkit.lra.mark-feature F002 failed
```

---

### `/devkit.lra.checkpoint`

**Purpose**: Create session checkpoint with git commit and progress update.

**Usage:**
```bash
/devkit.lra.checkpoint "[summary-message]"
```

**Example:**
```bash
/devkit.lra.checkpoint "Implemented user auth and JWT tokens"
```

**What it does:**
1. Stage all changes
2. Create git commit
3. Update progress log
4. Tag session milestone

---

### `/devkit.lra.status`

**Purpose**: Display current project status and progress.

**Usage:**
```bash
/devkit.lra.status
```

**Output shows:**
- Total features (completed/pending)
- Completion percentage
- Recent commits
- Active feature details
- Next 3 features to implement

---

### `/devkit.lra.recover`

**Purpose**: Recover from broken state with diagnostics.

**Usage:**
```bash
/devkit.lra.recover [--diagnose|--revert]
```

**Options:**
- `--diagnose`: Analyze issues without changes
- `--revert`: Revert to last known good state

**Example:**
```bash
/devkit.lra.recover --diagnose
/devkit.lra.recover --revert
```

---

## Workflow Example

### Session 1: Initialize & Core Auth

```bash
# Initialize project
/devkit.lra.init "Build chat app with user auth and message history"

# Start first session
/devkit.lra.start-session
# → Selects: F001 - User registration endpoint

# Implement, test, verify
# ... code implementation ...

# Mark feature complete
/devkit.lra.mark-feature F001 passed

# End session
/devkit.lra.checkpoint "Implemented user registration with validation"
```

### Session 2: Add Login

```bash
# Start session 2
/devkit.lra.start-session
# → Reads progress from session 1
# → Selects: F002 - User login endpoint

# Implement, test
# ... code implementation ...

/devkit.lra.mark-feature F002 passed
/devkit.lra.checkpoint "Implemented login and JWT token generation"
```

### Session 3: Discover & Add Feature

```bash
# Start session 3
/devkit.lra.start-session
# → Selects: F003 - Message creation endpoint

# During implementation, discover need for user rate limiting
/devkit.lra.add-feature api high "Rate limiting for message endpoints"

# Complete original feature
/devkit.lra.mark-feature F003 passed
/devkit.lra.checkpoint "Implemented message creation endpoint"

# New feature will be available in next session
```

### Ongoing Sessions

```bash
# Each subsequent session
/devkit.lra.start-session
# → Reads all previous progress
# → Verifies app is working
# → Selects next feature
# → Code → Test → Checkpoint
```

---

## File Structure

### `.lra/feature-list.json`

```json
{
  "project": "Chat Application",
  "description": "Real-time chat with AI responses",
  "created_at": "2026-01-23T14:00:00Z",
  "features": [
    {
      "id": "F001",
      "category": "auth",
      "priority": "critical",
      "description": "User registration endpoint",
      "acceptance_criteria": [
        "POST /api/auth/register with email/password",
        "Validate email format",
        "Hash password before storage",
        "Return JWT token on success"
      ],
      "status": "completed",
      "completed_at": "2026-01-23T16:30:00Z",
      "session": 1,
      "notes": "Added email validation, uses bcrypt"
    },
    {
      "id": "F002",
      "category": "auth",
      "priority": "critical",
      "description": "User login endpoint",
      "acceptance_criteria": [
        "POST /api/auth/login with email/password",
        "Verify credentials",
        "Return JWT token on success",
        "Return 401 on invalid credentials"
      ],
      "status": "in_progress",
      "completed_at": null,
      "session": 2,
      "notes": ""
    }
  ]
}
```

### `.lra/progress.txt`

```
═══════════════════════════════════════════════════
                LRA PROGRESS LOG
═══════════════════════════════════════════════════

Project: Chat Application
Created: 2026-01-23T14:00:00Z
Last Updated: 2026-01-23T17:45:00Z

SUMMARY
───────
Total Features: 42
Completed: 3 (7%)
In Progress: 1
Pending: 38

SESSION 1 (2026-01-23 14:00 - 16:30)
──────────────────────────────────────
Duration: 2h 30m
Features Completed: F001 (User registration)
Features Started: 1
Tests: 8 passed, 0 failed
Commits: 1
Notes: Initial auth setup complete

SESSION 2 (2026-01-23 16:30 - ongoing)
───────────────────────────────────────
Duration: 1h 15m+
Features Working: F002 (User login)
Tests: 5 passed, 0 failed
Notes: JWT integration in progress
```

---

## Best Practices

### 1. One Feature Per Session

- Complete feature fully before ending session
- Include all tests, documentation, and verification
- Don't start second feature if running low on context

### 2. Atomic Features

Write small, testable features:
- ❌ "Build user management system" (too big)
- ✅ "Create user registration endpoint with validation" (atomic)

### 3. Testing Protocol

For each feature:
1. **Unit tests** - Component/function level
2. **Integration tests** - Feature in context
3. **Manual verification** - End-to-end flow

### 4. Clear Checkpoints

```bash
# Good checkpoint message
/devkit.lra.checkpoint "Implemented password reset: endpoint + email template + tests"

# Poor checkpoint message
/devkit.lra.checkpoint "Work"
```

### 5. Health Checks

Always verify before checkpoint:
```bash
# Verify tests pass
npm test

# Verify app starts
npm run dev

# Verify git status
git status
```

### 6. Feature Documentation

Add acceptance criteria during init or add-feature:
```bash
/devkit.lra.add-feature api critical "Get user profile"
# Generates with default criteria
# Update with actual acceptance criteria
```

---

## Troubleshooting

### App Won't Start

```bash
# Check health
/devkit.lra.status

# Diagnose issues
/devkit.lra.recover --diagnose

# View init script
cat .lra/init.sh

# Run it manually
bash .lra/init.sh
```

### Lost Progress

```bash
# Check progress log
cat .lra/progress.txt

# View git history
git log --oneline

# Check feature list
cat .lra/feature-list.json
```

### Broken State

```bash
# Option 1: Diagnose without changes
/devkit.lra.recover --diagnose

# Option 2: Revert to last checkpoint
/devkit.lra.recover --revert

# Option 3: Manual reset
git reset --hard HEAD~1
/devkit.lra.start-session
```

### Feature Takes Too Long

```bash
# Break it down - Add smaller sub-features
/devkit.lra.add-feature [category] [priority] "Sub-feature 1"
/devkit.lra.add-feature [category] [priority] "Sub-feature 2"

# Mark current as failed
/devkit.lra.mark-feature [id] failed

# Checkpoint and note why
/devkit.lra.checkpoint "F001 split into F001a, F001b - too complex"
```

### Mid-Session Context Running Low

```bash
# Save progress immediately
/devkit.lra.checkpoint "Partial: [describe what's done]"

# Note work in feature
# Update .lra/feature-list.json with current state

# Next session will have full context
```

---

## Related Resources

- **Command Reference**: See [guide-commands.md](guide-commands.md) for all LRA commands
- **Anthropic Research**: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- **Agent Guide**: See [guide-agents.md](guide-agents.md) for agent capabilities

---

**Key Principle**: Leave the codebase in a testable, working state at the end of each session.
