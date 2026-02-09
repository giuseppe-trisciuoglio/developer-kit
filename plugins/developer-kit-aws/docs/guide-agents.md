# AWS Plugin Agents Guide

This guide provides comprehensive documentation for all AWS specialized agents available in the Developer Kit AWS Plugin.

---

## Table of Contents

1. [Overview](#overview)
2. [AWS Architecture Agents](#aws-architecture-agents)
3. [AWS DevOps Agents](#aws-devops-agents)
4. [Agent Usage Guidelines](#agent-usage-guidelines)
5. [See Also](#see-also)

---

## Overview

The AWS Plugin provides specialized agents for AWS architecture design, CloudFormation infrastructure as code, and AWS Well-Architected Framework review. These agents have deep expertise in AWS services and can help with architecture design, infrastructure implementation, and best practices compliance.

### Available Agents

- **AWS Architecture Agents**: 2 agents for solution architecture and architecture review
- **AWS DevOps Agents**: 1 agent for CloudFormation and DevOps automation

---

## AWS Architecture Agents

### `aws-solution-architect-expert`

**File**: `agents/aws-solution-architect-expert.md`

**Purpose**: AWS solution architecture design specialist for building scalable, secure, and cost-effective cloud solutions.

**When to use:**
- Designing new AWS architectures
- Planning cloud migrations
- Architecting multi-region solutions
- Designing serverless architectures
- Planning high availability and disaster recovery

**Key Capabilities:**
- AWS service selection and architecture
- Well-Architected Framework application
- Cost optimization strategies
- Security and compliance design
- Performance and scalability planning

---

### `aws-architecture-review-expert`

**File**: `agents/aws-architecture-review-expert.md`

**Purpose**: AWS architecture review against Well-Architected Framework covering operational excellence, security, reliability, performance efficiency, and cost optimization.

**When to use:**
- Reviewing existing AWS architectures
- Validating against Well-Architected Framework
- Identifying architectural risks
- Optimizing AWS costs
- Improving security and compliance

**Key Capabilities:**
- Well-Architected Framework review
- Security best practices validation
- Cost optimization recommendations
- Performance optimization
- Operational excellence assessment

---

## AWS DevOps Agents

### `aws-cloudformation-devops-expert`

**File**: `agents/aws-cloudformation-devops-expert.md`

**Purpose**: CloudFormation infrastructure as code specialist for building, deploying, and managing AWS resources.

**When to use:**
- Creating CloudFormation templates
- Implementing IaC best practices
- Automating AWS deployments
- Managing AWS infrastructure
- Building CI/CD pipelines for AWS

**Key Capabilities:**
- CloudFormation template design
- IaC best practices implementation
- Stack deployment and management
- Resource orchestration
- CI/CD pipeline integration

---

## Agent Usage Guidelines

### When to Use AWS Plugin Agents

AWS Plugin agents are most effective for:
- **Architecture Design**: Designing new AWS solutions and architectures
- **Architecture Review**: Validating existing architectures against best practices
- **Infrastructure as Code**: Building CloudFormation templates and IaC solutions
- **Cloud Migration**: Planning and executing cloud migrations
- **Cost Optimization**: Optimizing AWS costs and resource usage
- **Security**: Implementing AWS security best practices

### How to Invoke Agents

Agents can be invoked in several ways:

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the aws-solution-architect-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

### Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Design AWS architecture | `aws-solution-architect-expert` |
| Review AWS architecture | `aws-architecture-review-expert` |
| Create CloudFormation templates | `aws-cloudformation-devops-expert` |
| Optimize AWS costs | `aws-architecture-review-expert` |
| Plan cloud migration | `aws-solution-architect-expert` |
| Implement IaC | `aws-cloudformation-devops-expert` |

---

## See Also

- [CloudFormation Skills Guide](./guide-skills-cloudformation.md) - AWS CloudFormation skills
- [Core Agent Guide](../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [Java AWS Skills Guide](../developer-kit-java/docs/guide-skills-aws-java.md) - AWS Java SDK skills

---

## Cross-Plugin References

The AWS plugin contains CloudFormation skills for infrastructure as code. For AWS SDK integration from Java applications, see:

- **[Java AWS Skills Guide](../developer-kit-java/docs/guide-skills-aws-java.md)** - AWS SDK integration from Java
