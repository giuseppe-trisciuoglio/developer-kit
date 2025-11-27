---
description: Initialize environment for long-running agent workflow (creates feature list, progress file, init.sh)
allowed-tools: Read, Write, Edit, Bash(git:*), Bash(mkdir:*), Bash(chmod:*)
argument-hint: [project-description]
---

# Long-Running Agent - Initialize Environment

You are an **Initializer Agent** setting up the environment for a long-running coding project. Your job is to create all necessary scaffolding so that future coding agents can work effectively across multiple context windows.

## Project Description

$ARGUMENTS

## Your Tasks

### 1. Create the LRA Directory Structure

Create the `.lra/` directory in the project root with the following structure:

```
.lra/
├── feature-list.json      # Structured list of all features
├── progress.txt           # Session-by-session progress log
└── init.sh                # Script to start the development environment
```

### 2. Create feature-list.json

Based on the project description, create a comprehensive JSON file with ALL features needed. Each feature should be atomic and testable.

**Format:**
```json
{
  "project": "Project Name",
  "description": "Brief project description",
  "created_at": "ISO timestamp",
  "features": [
    {
      "id": "F001",
      "category": "core|ui|api|database|auth|testing|other",
      "priority": "critical|high|medium|low",
      "description": "Clear description of the feature",
      "acceptance_criteria": [
        "Step 1 to verify",
        "Step 2 to verify"
      ],
      "status": "pending",
      "completed_at": null,
      "notes": ""
    }
  ]
}
```

**Guidelines:**
- Break down the project into 20-50+ atomic features minimum
- Each feature should be completable in one coding session
- Order features by dependency (foundational features first)
- Use `status: "pending"` for all features initially
- Include setup/configuration features
- Include testing features

### 3. Create progress.txt

Initialize the progress file:

```
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
```

### 4. Create init.sh

Create a shell script that future agents can run to start the development environment:

```bash
#!/bin/bash
# Long-Running Agent - Environment Initialization Script
# This script starts the development server and prepares the environment

echo "🚀 Starting Long-Running Agent Environment..."

# Add project-specific commands here:
# - Start development server
# - Run database migrations
# - Start required services
# - etc.

echo "✅ Environment ready!"
```

Make the script executable with `chmod +x .lra/init.sh`.

### 5. Create Initial Git Commit

After creating all files:

1. Add all `.lra/` files to git
2. Create a commit with message: `chore(lra): initialize long-running agent environment`

## Output

After completing all tasks, provide a summary:

1. Number of features identified
2. Feature breakdown by category
3. Feature breakdown by priority
4. Next steps for the first coding session
