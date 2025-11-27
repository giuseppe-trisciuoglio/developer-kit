# Long-Running Agent (LRA) Workflow Guide

This guide provides comprehensive documentation for the Long-Running Agent workflow commands, based on Anthropic's
research on effective harnesses for agents working across multiple context windows.

---

## Table of Contents

1. [Overview](#overview)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [LRA Commands Reference](#lra-commands-reference)
5. [Workflow Examples](#workflow-examples)
6. [File Structure](#file-structure)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Long-Running Agent (LRA) workflow is a structured approach for AI agents to work effectively on complex projects
that span multiple context windows (hours or days of work). It implements the patterns described in Anthropic's research
article ["Effective harnesses for long-running agents"](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

### Key Benefits

- **Continuity across sessions**: Each agent session can pick up where the previous one left off
- **Incremental progress**: Work is broken into atomic, testable features
- **Clean handoffs**: The codebase is always left in a working state
- **Progress tracking**: Clear visibility into what's done and what remains
- **Recovery capability**: Easy recovery from broken states

---

## The Problem

When AI agents work on complex projects, they face several challenges:

### 1. Context Window Amnesia

Each new session begins with no memory of what came before. Imagine a software project staffed by engineers working in
shifts, where each new engineer arrives with no memory of what happened on the previous shift.

### 2. One-Shot Tendency

Agents tend to try to do too much at once—essentially attempting to one-shot an entire app. This often leads to:

- Running out of context mid-implementation
- Features left half-implemented and undocumented
- Next sessions having to guess what happened

### 3. Premature Completion

After some progress, agents may look around, see that progress has been made, and declare the job done prematurely.

### 4. Insufficient Testing

Agents tend to mark features as complete without proper end-to-end testing, leading to bugs that compound over sessions.

---

## The Solution

The LRA workflow addresses these problems with a two-part approach:

### 1. Initializer Agent (`/devkit.lra.init`)

The first session uses a specialized prompt that sets up:

- A comprehensive **feature list** with all requirements broken down
- A **progress file** for session-by-session logging
- An **init.sh script** for environment setup
- An initial **git commit** establishing the baseline

### 2. Coding Agent (`/devkit.lra.start-session`)

Every subsequent session follows a structured protocol:

1. Read progress files and git history
2. Run basic health checks
3. Choose ONE feature to work on
4. Implement with testing
5. Create checkpoint before ending

---

## LRA Commands Reference

### `/devkit.lra.init`

**Description**: Initialize environment for long-running agent workflow. Creates the complete scaffolding for
multi-session development.

**When to use:**

- Starting a new complex project
- Setting up LRA workflow for existing project
- Onboarding a project for autonomous agent development

**Arguments:**

```bash
/devkit.lra.init [project-description]
```

**Practical examples:**

```bash
# Initialize for a web application
/devkit.lra.init Build a clone of claude.ai with chat interface, conversation history, and user authentication

# Initialize for an API project
/devkit.lra.init Create a REST API for inventory management with CRUD operations, search, and reporting

# Initialize for a CLI tool
/devkit.lra.init Build a CLI tool for managing Docker containers with start, stop, logs, and monitoring commands
```

**What it creates:**

```
.lra/
├── feature-list.json      # All features with status tracking
├── progress.txt           # Session-by-session progress log
└── init.sh                # Environment startup script
```

**Feature list format:**

```json
{
  "project": "Claude.ai Clone",
  "description": "Web chat application with AI integration",
  "created_at": "2024-01-15T10:00:00Z",
  "features": [
    {
      "id": "F001",
      "category": "core",
      "priority": "critical",
      "description": "User can open a new chat and send a message",
      "acceptance_criteria": [
        "Navigate to main interface",
        "Click 'New Chat' button",
        "Type message and press enter",
        "See AI response appear"
      ],
      "status": "pending",
      "completed_at": null,
      "notes": ""
    }
  ]
}
```

---

### `/devkit.lra.start-session`

**Description**: Start a new coding session with the structured startup protocol. Reads progress, checks health, and
selects next feature.

**When to use:**

- Beginning any coding session on an LRA project
- After context window reset
- Resuming work after a break

**Arguments:**

```bash
/devkit.lra.start-session
```

**Startup protocol executed:**

1. **Orient** - Confirm working directory
2. **Read Progress** - Load `.lra/progress.txt`
3. **Check Git** - Review recent commits and status
4. **Read Features** - Load `.lra/feature-list.json`
5. **Environment Check** - Run `init.sh` if exists
6. **Health Check** - Verify app is working

**Output includes:**

- Project status (X of Y features complete)
- Last session summary
- Current app state
- Selected feature for this session
- Implementation approach

**Real-world use case:**

```bash
# Starting a new session
/devkit.lra.start-session

# Expected output:
# ═══════════════════════════════════════════════════════
#                    SESSION STARTUP
# ═══════════════════════════════════════════════════════
#
# 📍 Working Directory: /projects/claude-clone
#
# 📊 Project Status: 12/42 features complete (29%)
#
# 📝 Last Session (Session 11):
#    - Implemented user login flow
#    - Added JWT token generation
#    - All tests passing
#
# ✅ Health Check: App starts successfully
#
# 🎯 Selected Feature: F013 - Password reset flow
#    Priority: HIGH
#    Category: auth
#
# 📋 Approach:
#    1. Create password reset request endpoint
#    2. Generate secure reset token
#    3. Create reset confirmation endpoint
#    4. Add email sending (mock for now)
#    5. Test end-to-end flow
```

---

### `/devkit.lra.add-feature`

**Description**: Add a new feature to the project's feature list.

**When to use:**

- Discovering new requirements during development
- Breaking down complex features into smaller ones
- Adding features from stakeholder feedback

**Arguments:**

```bash
/devkit.lra.add-feature [category] [priority] [description]
```

**Categories:**

- `core` - Core application functionality
- `ui` - User interface features
- `api` - API endpoints
- `database` - Database and data layer
- `auth` - Authentication/authorization
- `testing` - Test infrastructure
- `other` - Miscellaneous

**Priorities:**

- `critical` - Must have for MVP
- `high` - Important for release
- `medium` - Nice to have
- `low` - Future consideration

**Practical examples:**

```bash
# Add a high-priority API feature
/devkit.lra.add-feature api high Add endpoint to retrieve user preferences

# Add a medium-priority UI feature
/devkit.lra.add-feature ui medium Implement dark mode toggle in settings

# Add a critical auth feature
/devkit.lra.add-feature auth critical Implement two-factor authentication

# Add a testing feature
/devkit.lra.add-feature testing high Add end-to-end tests for checkout flow
```

**Output:**

```
✅ Feature Added

ID: F043
Category: api
Priority: high
Description: Add endpoint to retrieve user preferences

Acceptance Criteria:
- GET /api/users/{id}/preferences returns user preferences
- Response includes all preference categories
- Unauthorized requests return 401
- Invalid user ID returns 404

Total features: 43 (38 pending, 5 completed)
```

---

### `/devkit.lra.mark-feature`

**Description**: Mark a feature as completed (passed) or failed.

**When to use:**

- After successfully implementing and testing a feature
- When a feature cannot be completed due to blockers
- To track implementation status

**Arguments:**

```bash
/devkit.lra.mark-feature [feature-id] [passed|failed] [optional-notes]
```

**Practical examples:**

```bash
# Mark feature as passed
/devkit.lra.mark-feature F012 passed

# Mark feature as passed with notes
/devkit.lra.mark-feature F023 passed Implemented with Redis caching for performance

# Mark feature as failed with explanation
/devkit.lra.mark-feature F015 failed API rate limiting requires Redis setup first
```

**Important rules:**

- **ONLY mark as passed after TESTING the feature end-to-end**
- **It is UNACCEPTABLE to mark features as passed without verification**
- **Do NOT remove or edit the feature description or acceptance criteria**
- **Failed features should include clear notes about what went wrong**

**Output for passed:**

```
✅ Feature Updated

ID: F012
Description: User can create a new account
Status: passed ✓
Completed: 2025-11-15T14:32:00Z
Notes: Implemented with email verification

Progress: 6/42 features completed (14%)
```

**Output for failed:**

```
⚠️ Feature Marked as Failed

ID: F015
Description: API rate limiting per user
Status: failed ✗
Notes: API rate limiting requires Redis setup first

This feature remains in the backlog for future implementation.
```

---

### `/devkit.lra.checkpoint`

**Description**: Create a checkpoint at the end of a coding session. Commits changes, updates progress log, and ensures
clean state.

**When to use:**

- At the end of every coding session
- Before context window reset
- After completing a feature
- Before taking a break

**Arguments:**

```bash
/devkit.lra.checkpoint [summary-of-work-done]
```

**Practical examples:**

```bash
# Simple checkpoint
/devkit.lra.checkpoint Implemented user authentication flow

# Detailed checkpoint
/devkit.lra.checkpoint Completed F012 user registration with email verification and password hashing

# Checkpoint with blockers noted
/devkit.lra.checkpoint Partial progress on rate limiting - blocked by Redis setup
```

**Checkpoint protocol:**

1. **Verify Clean State**
    - Run test suite
    - Start dev server
    - Check for syntax errors

2. **Stage and Commit**
    - Review changes
    - Create descriptive commit

3. **Update Progress Log**
    - Append session summary to `progress.txt`
    - Document accomplishments
    - Note blockers and next steps

4. **Final Verification**
    - Confirm clean git status
    - Verify working tree is clean

**Output:**

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

---

### `/devkit.lra.status`

**Description**: Display comprehensive project status with progress metrics, priorities, and recent activity.

**When to use:**

- To get an overview of project progress
- Planning which feature to work on next
- Reporting status to stakeholders
- Understanding project health

**Arguments:**

```bash
/devkit.lra.status
```

**Output:**

```
╔══════════════════════════════════════════════════════════════╗
║              LONG-RUNNING AGENT - PROJECT STATUS             ║
╠══════════════════════════════════════════════════════════════╣
║  Project: Claude.ai Clone                                    ║
║  Last Updated: 2025-11-15                                    ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[████████████░░░░░░░░░░░░░░░░░░] 38% (16/42 features)

✅ Passed:  16
⏳ Pending: 24
❌ Failed:   2

📈 BY PRIORITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical [████████████████████] 100% (5/5)
High     [████████████░░░░░░░░]  60% (9/15)
Medium   [████░░░░░░░░░░░░░░░░]  20% (2/10)
Low      [░░░░░░░░░░░░░░░░░░░░]   0% (0/12)

📁 BY CATEGORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core:     8/10 ✓
API:      4/8
UI:       2/12
Database: 2/4 ✓
Auth:     0/5
Testing:  0/3

🎯 NEXT PRIORITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [F023] HIGH - Implement password reset flow
2. [F024] HIGH - Add email verification
3. [F025] HIGH - Create user profile endpoint
4. [F031] MEDIUM - Add pagination to list endpoints
5. [F032] MEDIUM - Implement search functionality

⚠️ ATTENTION NEEDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ [F018] FAILED - Rate limiting (needs Redis setup)
❌ [F019] FAILED - WebSocket connections (timeout issues)

📝 RECENT ACTIVITY (Last 3 Sessions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Session 8 (2024-01-15): Completed F022 - User login flow
• Session 7 (2024-01-14): Completed F021 - Database migrations
• Session 6 (2024-01-13): Completed F020 - API error handling

💻 GIT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Branch: main
Working tree: clean
Last commit: abc1234 - feat(auth): implement login flow

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Run /devkit.lra.start-session to begin working on the next feature
```

---

### `/devkit.lra.recover`

**Description**: Recover from a broken state by diagnosing issues, reverting if needed, and restoring a working state.

**When to use:**

- App doesn't start
- Tests are failing unexpectedly
- Code is in an inconsistent state
- Previous session left things broken

**Arguments:**

```bash
/devkit.lra.recover
```

**Recovery protocol:**

1. **Diagnose the Problem**
    - Check for syntax errors
    - Run failing tests
    - Try to start the app
    - Review progress log

2. **Identify Breaking Change**
    - Review git history
    - Find last working commit
    - Identify problematic changes

3. **Choose Recovery Strategy**
    - **Quick Fix**: Small, obvious issues
    - **Revert Last Commit**: Recent breaking change
    - **Revert to Known Good**: Multiple problematic commits
    - **Stash and Investigate**: Need to explore without losing work

4. **Verify Recovery**
    - Run tests
    - Start the app
    - Verify core functionality

5. **Document Recovery**
    - Update progress.txt
    - Note lessons learned

6. **Update Feature Status**
    - Mark incorrectly passed features as failed

**Output:**

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
   Continue with normal workflow using /devkit.lra.start-session

═══════════════════════════════════════════════════════════
```

---

## Workflow Examples

### Complete Project Workflow

```bash
# Day 1: Initialize the project
/devkit.lra.init Build a task management application with user accounts, projects, tasks, and team collaboration features

# Day 1: Start first coding session
/devkit.lra.start-session

# Work on first feature...
# ... implement ...
# ... test ...

# End of Day 1: Create checkpoint
/devkit.lra.checkpoint Completed project setup and user registration feature

# Day 2: Start new session
/devkit.lra.start-session

# Mark previous feature complete
/devkit.lra.mark-feature F001 passed User registration working with email validation

# Work on next feature...

# Add discovered requirement
/devkit.lra.add-feature api high Add password strength validation endpoint

# End of Day 2
/devkit.lra.checkpoint Completed login and added password validation

# Day 3: Check status before starting
/devkit.lra.status

# Continue development...
/devkit.lra.start-session

# Something broke!
/devkit.lra.recover

# Continue after recovery...
```

### Typical Session Flow

```bash
# 1. Start session (always first)
/devkit.lra.start-session

# 2. Agent reads context, selects feature, begins work
# ... coding happens ...

# 3. After completing feature, mark it
/devkit.lra.mark-feature F015 passed

# 4. Optionally add new features discovered
/devkit.lra.add-feature testing medium Add integration tests for user endpoints

# 5. Create checkpoint before ending
/devkit.lra.checkpoint Implemented user profile endpoints with full test coverage
```

### Recovery Workflow

```bash
# 1. Something is broken
/devkit.lra.recover

# 2. After recovery, resume normal workflow
/devkit.lra.start-session

# 3. If a feature was wrongly marked as passed
/devkit.lra.mark-feature F012 failed Login fails when special characters in password
```

---

## File Structure

### `.lra/` Directory

```
.lra/
├── feature-list.json      # Master list of all features
├── progress.txt           # Session-by-session progress log
└── init.sh                # Environment startup script
```

### feature-list.json Schema

```json
{
  "project": "string - Project name",
  "description": "string - Brief description",
  "created_at": "ISO 8601 timestamp",
  "features": [
    {
      "id": "string - F001, F002, etc.",
      "category": "core|ui|api|database|auth|testing|other",
      "priority": "critical|high|medium|low",
      "description": "string - What the feature does",
      "acceptance_criteria": [
        "array of verification steps"
      ],
      "status": "pending|passed|failed",
      "completed_at": "ISO 8601 timestamp or null",
      "notes": "string - Additional context"
    }
  ]
}
```

### progress.txt Format

```markdown
# Long-Running Agent Progress Log

# Project: [Name]

# Created: [Date]

## Session History

### Session 1 - [Date] - Initialization

- Created project scaffolding
- Generated feature list with X features
- Created init.sh script
- Initial git commit

---

### Session 2 - [Date] - [Title]

**Feature Worked On**: F001 - [Description]

**Accomplished**:

- [What was done]
- [What was done]

**Status**: Complete

**Notes for Next Session**:

- [Important context]
- [Suggested next steps]

**Commits This Session**:

- abc1234 - feat: implement user registration

---
```

### init.sh Template

```bash
#!/bin/bash
# Long-Running Agent - Environment Initialization Script

echo "🚀 Starting Long-Running Agent Environment..."

# Project-specific setup
cd "$(dirname "$0")/.."

# Start development server (customize per project)
# npm run dev &
# mvn spring-boot:run &
# python manage.py runserver &

# Run database migrations
# npm run migrate
# mvn flyway:migrate
# python manage.py migrate

# Start required services
# docker-compose up -d

echo "✅ Environment ready!"
```

---

## Best Practices

### 1. Feature Granularity

**Good feature:**

```json
{
  "description": "User can reset password via email link",
  "acceptance_criteria": [
    "Click 'Forgot Password' shows email form",
    "Submitting email sends reset link",
    "Clicking link shows new password form",
    "Submitting new password updates account"
  ]
}
```

**Too large:**

```json
{
  "description": "Complete authentication system"
}
```

**Too small:**

```json
{
  "description": "Add onClick handler to button"
}
```

### 2. Session Discipline

- **Always start with** `/devkit.lra.start-session`
- **Always end with** `/devkit.lra.checkpoint`
- **Work on ONE feature** per session
- **Test before marking** features as passed
- **Document blockers** in notes

### 3. Progress Documentation

- Write progress notes for the **next agent**, not yourself
- Include **specific file names** and **function names**
- Document **what works** and **what doesn't**
- Note any **environment quirks**

### 4. Git Hygiene

- Commit **frequently** with descriptive messages
- Use **conventional commits** (feat:, fix:, etc.)
- Never leave **uncommitted changes** at session end
- The working tree should be **clean** after checkpoint

### 5. Testing Philosophy

- Run **basic health check** at session start
- **Fix bugs before** implementing new features
- Use **end-to-end testing** when possible (browser automation)
- Don't mark features passed based on unit tests alone

---

## Troubleshooting

### LRA Files Not Found

```bash
# Check if .lra directory exists
ls -la .lra/

# If not, initialize the project
/devkit.lra.init [project-description]
```

### Feature List Corrupted

```bash
# Check JSON validity
cat .lra/feature-list.json | python -m json.tool

# If invalid, check git history
git log --oneline .lra/feature-list.json
git show HEAD~1:.lra/feature-list.json
```

### App Won't Start After Session

```bash
# Use recovery command
/devkit.lra.recover

# Or manually check last commits
git log --oneline -5
git diff HEAD~1
```

### Lost Track of Progress

```bash
# Check status
/devkit.lra.status

# Review progress log
cat .lra/progress.txt

# Review git history
git log --oneline -20
```

### Feature Marked Wrong Status

```bash
# Mark as failed with explanation
/devkit.lra.mark-feature F012 failed Feature was not properly tested

# Then work on it again in next session
```

---

## Command Quick Reference

| Command                                      | Purpose                    | When to Use                 |
|----------------------------------------------|----------------------------|-----------------------------|
| `/devkit.lra.init [desc]`                    | Initialize LRA environment | First time setup            |
| `/devkit.lra.start-session`                  | Begin coding session       | Start of every session      |
| `/devkit.lra.add-feature [cat] [pri] [desc]` | Add new feature            | New requirements discovered |
| `/devkit.lra.mark-feature [id] [status]`     | Update feature status      | After implementing/testing  |
| `/devkit.lra.checkpoint [summary]`           | Save session progress      | End of every session        |
| `/devkit.lra.status`                         | View project status        | Anytime                     |
| `/devkit.lra.recover`                        | Fix broken state           | When app/tests fail         |

---

## References

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Claude 4 Prompting Guide - Multi-context window workflows](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices#multi-context-window-workflows)


