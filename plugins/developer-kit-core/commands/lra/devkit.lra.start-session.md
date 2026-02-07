---
description: Start a new coding session - reads progress, chooses next feature, runs basic tests
argument-hint: "[optional-context]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Long-Running Agent - Start Coding Session

You are a **Coding Agent** starting a new session on an ongoing project. Your first priority is to understand the current state before making any changes.

## Session Startup Protocol

Execute these steps IN ORDER:

### Step 1: Orient Yourself

```bash
pwd
```

Confirm you're in the correct project directory.

### Step 2: Read Progress History

Read the progress file to understand what happened in previous sessions:

```bash
cat .lra/progress.txt
```

Pay attention to:
- What was worked on in the last session
- Any issues or blockers mentioned
- Any incomplete work that needs attention

### Step 3: Check Git History

Review recent commits to understand code changes:

```bash
git log --oneline -15
git status
```

If there are uncommitted changes, understand what they are before proceeding.

### Step 4: Read Feature List

Load the feature list and identify what needs to be done:

```bash
cat .lra/feature-list.json
```

Identify:
- Features with `status: "pending"` 
- The highest priority incomplete feature
- Any dependencies between features

### Step 5: Run Environment Check

If an init script exists, consider running it:

```bash
if [ -f .lra/init.sh ]; then
    source .lra/init.sh
fi
```

### Step 6: Basic Health Check

Run a quick test to ensure the app is in a working state:
- Start the development server (if applicable)
- Run existing tests
- Verify core functionality works

**If the app is broken**: Fix existing bugs BEFORE starting new features.

## Session Planning

After completing the startup protocol, provide:

### Session Summary

1. **Project Status**: Overall progress (X of Y features complete)
2. **Last Session**: What was accomplished
3. **Current State**: Is the app working? Any issues?
4. **Selected Feature**: The feature you will work on this session
5. **Approach**: Brief plan for implementing the feature

### Important Rules

- **ONE FEATURE PER SESSION**: Focus on completing one feature fully
- **TEST BEFORE MARKING COMPLETE**: Verify the feature works end-to-end
- **CLEAN STATE**: Leave the codebase in a working state
- **DOCUMENT PROGRESS**: Update progress.txt at session end

## Ready to Code

Once you've completed the startup protocol and planning, you may begin implementation. Remember:

1. Work incrementally with small, tested changes
2. Commit frequently with descriptive messages
3. If you encounter blockers, document them
4. Before ending the session, use `/developer-kit:devkit.lra.checkpoint` to save your progress

## Execution Instructions

**Agent Selection**: To execute this LRA task, use the following approach:
- Primary: Use `general-purpose` agent with task management and state persistence capabilities
- Or use `plan` agent for complex multi-step workflows
