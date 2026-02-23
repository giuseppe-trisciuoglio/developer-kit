# Developer Kit Jira

Jira integration with Atlassian MCP Server for automated SDLC workflows.

## Overview

The `developer-kit-jira` plugin provides seamless integration between Git workflows and Jira using the official Atlassian MCP Server. It enables automatic inference of Jira tickets from git context (branch names, commits, PRs) and manages ticket state transitions with user confirmation.

## Agents

None - this plugin provides commands and skills only.

## Commands

### Ticket Management

- `devkit.jira.ticket.view` - View Jira ticket details including summary, status, assignee, and description
- `devkit.jira.ticket.comment` - Add comments to tickets
- `devkit.jira.ticket.transition` - Manage ticket status transitions

### Workflow Commands

- `devkit.jira.workflow.start` - Start development on a ticket (branch creation + Jira update)
- `devkit.jira.workflow.commit` - Commit with Jira reference + add comment
- `devkit.jira.workflow.push` - Push branch + update Jira
- `devkit.jira.workflow.pr-create` - Create PR + transition to "In Review"
- `devkit.jira.workflow.pr-ready` - Mark PR ready + transition to "Reviewing"
- `devkit.jira.workflow.pr-merge` - Merge PR + transition to "Done"
- `devkit.jira.workflow.status` - Show combined git and Jira status

## Skills

- **jira-mcp-workflow** - Comprehensive workflow management with MCP integration, including ticket inference from branch names, automated Jira updates, and complete SDLC workflow automation

## Dependencies

- `developer-kit` (required)
- Atlassian MCP Server (user-configured)
- GitHub CLI (`gh`) for PR operations

## Setup

### MCP Configuration

To use this plugin, you need to configure the Atlassian MCP Server in your `claude_mcp_settings.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-remote", "https://mcp.atlassian.com/v1/mcp"],
      "env": {}
    }
  }
}
```

### Authentication

The Atlassian MCP Server uses OAuth 2.1 (3LO) flow:
1. First connection will prompt for Atlassian login
2. Grant permissions for Jira access
3. Session-based tokens are managed automatically

### Key Features

- **Automatic ticket inference** from branch names (feature/PROJECT-123)
- **Atlassian MCP Server integration** for all Jira operations
- **User confirmations** before all state changes
- **Git-Jira synchronization** for complete SDLC workflow
- **Input validation** with regex pattern `[A-Z]+-[0-9]+`
- **Branch name sanitization** to prevent injection
