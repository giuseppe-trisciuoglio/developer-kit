# DevOps Plugin Agents Guide

This guide provides comprehensive documentation for all DevOps specialized agents available in the Developer Kit DevOps Plugin.

---

## Overview

The DevOps Plugin provides specialized agents for containerization and CI/CD pipeline development. These agents have deep expertise in Docker, GitHub Actions, and DevOps best practices.

### Available Agents

- **Docker**: 1 agent for Docker containerization and orchestration
- **GitHub Actions**: 1 agent for CI/CD pipeline development

---

## DevOps Agents

### `general-docker-expert`

**File**: `agents/general-docker-expert.md`

**Purpose**: Docker containerization and orchestration specialist for building, deploying, and managing containerized applications.

**When to use:**
- Creating Dockerfile for applications
- Designing multi-container setups with Docker Compose
- Optimizing Docker images
- Troubleshooting Docker issues
- Implementing container orchestration

**Key Capabilities:**
- Dockerfile optimization
- Multi-stage builds
- Docker Compose orchestration
- Container networking
- Volume management
- Security best practices

---

### `github-actions-pipeline-expert`

**File**: `agents/github-actions-pipeline-expert.md`

**Purpose**: GitHub Actions CI/CD pipeline development specialist for automating build, test, and deployment workflows.

**When to use:**
- Creating GitHub Actions workflows
- Setting up CI/CD pipelines
- Automating testing and deployment
- Optimizing pipeline performance
- Implementing pipeline best practices

**Key Capabilities:**
- Workflow design and implementation
- Build and test automation
- Deployment automation
- Pipeline optimization
- Security scanning integration
- Custom actions development

---

## Agent Usage Guidelines

### When to Use DevOps Plugin Agents

DevOps Plugin agents are most effective for:
- **Containerization**: Building and managing Docker containers
- **CI/CD**: Creating and optimizing GitHub Actions workflows
- **Automation**: Automating build, test, and deployment processes
- **DevOps Best Practices**: Implementing industry-standard DevOps practices

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the general-docker-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Create Dockerfile | `general-docker-expert` |
| Design Docker Compose setup | `general-docker-expert` |
| Optimize Docker images | `general-docker-expert` |
| Create GitHub Actions workflow | `github-actions-pipeline-expert` |
| Set up CI/CD pipeline | `github-actions-pipeline-expert` |
| Optimize pipeline performance | `github-actions-pipeline-expert` |

---

## See Also

- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [AWS Plugin Documentation](../developer-kit-aws/docs/) - AWS CloudFormation and DevOps guides
