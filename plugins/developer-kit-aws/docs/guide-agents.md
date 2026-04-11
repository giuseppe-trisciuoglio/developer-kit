# AWS Plugin Agents Guide

This guide provides comprehensive documentation for all AWS specialized agents available in the Developer Kit AWS Plugin.

---

## Table of Contents

1. [Overview](#overview)
2. [Available Agents](#available-agents)
3. [Agent Reference](#agent-reference)
4. [Agent Selection Guide](#agent-selection-guide)
5. [See Also](#see-also)

---

## Overview

The AWS Plugin provides 3 specialized agents for AWS architecture design, CloudFormation infrastructure as code, and AWS Well-Architected Framework review. These agents have deep expertise in AWS services and help with architecture design, infrastructure implementation, and best practices compliance.

### Available Agents

| Agent | Purpose | Category |
|-------|---------|----------|
| `aws-solution-architect-expert` | AWS architecture design specialist | Architecture |
| `aws-architecture-review-expert` | Well-Architected Framework review | Architecture |
| `aws-cloudformation-devops-expert` | CloudFormation IaC specialist | DevOps |

---

## Agent Reference

### `aws-solution-architect-expert`

**Purpose**: Design scalable, secure, and cost-effective AWS cloud solutions.

**When to use:**
- Designing new AWS architectures from scratch
- Planning cloud migrations to AWS
- Architecting multi-region or hybrid solutions
- Designing serverless architectures (Lambda, Step Functions)
- Planning high availability and disaster recovery

**Key Capabilities:**
- AWS service selection and architecture design
- Well-Architected Framework application
- Cost optimization strategies
- Security and compliance design
- Performance and scalability planning

---

### `aws-architecture-review-expert`

**Purpose**: Review existing AWS architectures against Well-Architected Framework pillars.

**When to use:**
- Reviewing existing AWS architectures
- Validating against Well-Architected Framework
- Identifying architectural risks and anti-patterns
- Optimizing AWS costs and resource usage
- Improving security and compliance posture

**Key Capabilities:**
- Well-Architected Framework review (all 6 pillars)
- Security best practices validation
- Cost optimization recommendations
- Performance efficiency analysis
- Operational excellence assessment
- Reliability and resilience evaluation

---

### `aws-cloudformation-devops-expert`

**Purpose**: Build, deploy, and manage AWS infrastructure using CloudFormation.

**When to use:**
- Creating CloudFormation templates from scratch
- Implementing Infrastructure as Code best practices
- Automating AWS deployments
- Managing CloudFormation stacks
- Building CI/CD pipelines for AWS infrastructure
- Migrating existing resources to CloudFormation

**Key Capabilities:**
- CloudFormation template design and optimization
- IaC best practices implementation
- Stack deployment and lifecycle management
- Resource orchestration patterns
- CI/CD pipeline integration (GitHub Actions, CodePipeline)
- Drift detection and management

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|-------------------|
| Design new AWS architecture | `aws-solution-architect-expert` |
| Review existing architecture | `aws-architecture-review-expert` |
| Create CloudFormation templates | `aws-cloudformation-devops-expert` |
| Optimize AWS costs | `aws-architecture-review-expert` |
| Plan cloud migration | `aws-solution-architect-expert` |
| Implement IaC pipelines | `aws-cloudformation-devops-expert` |
| Security review | `aws-architecture-review-expert` |
| Design serverless solutions | `aws-solution-architect-expert` |

### How to Invoke Agents

1. **Automatic Selection**: Claude automatically selects the appropriate agent based on task context
2. **Direct Invocation**: Use agent name in conversation (e.g., "Ask the aws-solution-architect-expert...")
3. **Tool Selection**: When using the Task tool, specify the subagent_type parameter

---

## See Also

- [CloudFormation Skills Guide](./guide-skills-cloudformation.md) - Infrastructure as Code patterns
- [AWS CLI Skills Guide](./guide-skills-aws-cli.md) - Advanced command line operations
- [AWS SAM Bootstrap Guide](./guide-skills-aws-sam.md) - Serverless Application Model
- [Cost Optimization Guide](./guide-skills-cost-optimization.md) - AWS cost management
- [Core Agent Guide](../../developer-kit-core/docs/guide-agents.md) - All agents across plugins
- [Java AWS Skills Guide](../../developer-kit-java/docs/guide-skills-aws-java.md) - AWS SDK for Java
