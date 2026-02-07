---
description: Show current project status - features progress, recent activity, next priorities
argument-hint: [optional-filter]
allowed-tools: Read, Bash(git log:*), Bash(git status:*)
---

# Long-Running Agent - Project Status

Display a comprehensive status report of the long-running agent project.

## Current Context

- Git Status: !`git status --short`
- Recent Commits: !`git log --oneline -5`

## Your Task

Read the project files and generate a status report.

### Step 1: Read Project Files

1. Read `.lra/feature-list.json`
2. Read `.lra/progress.txt`

### Step 2: Calculate Statistics

From the feature list, calculate:

- Total features
- Features by status (pending, passed, failed)
- Features by priority (critical, high, medium, low)
- Features by category
- Completion percentage

### Step 3: Identify Priorities

Determine:
- Next 3-5 features to work on (highest priority pending)
- Any blocked or failed features that need attention
- Dependencies between pending features

### Step 4: Generate Report

```
╔══════════════════════════════════════════════════════════════╗
║              LONG-RUNNING AGENT - PROJECT STATUS             ║
╠══════════════════════════════════════════════════════════════╣
║  Project: [Name]                                             ║
║  Last Updated: [Date from progress.txt]                      ║
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
💡 Run /developer-kit:devkit.lra.start-session to begin working on the next feature
```

## Quick Commands

Remind the user of available commands:

- `/developer-kit:devkit.lra.start-session` - Begin a new coding session
- `/developer-kit:devkit.lra.add-feature [cat] [pri] [desc]` - Add a new feature
- `/developer-kit:devkit.lra.mark-feature [id] [passed|failed]` - Update feature status
- `/developer-kit:devkit.lra.checkpoint [summary]` - Save session progress

## Execution Instructions

**Agent Selection**: To execute this LRA task, use the following approach:
- Primary: Use `general-purpose` agent with task management and state persistence capabilities
- Or use `plan` agent for complex multi-step workflows
