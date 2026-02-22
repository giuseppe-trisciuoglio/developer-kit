---
name: aws-cloudformation-bedrock
description: Provides AWS CloudFormation patterns for Amazon Bedrock resources including agents, knowledge bases, data sources, guardrails, prompts, flows, and inference profiles. Use when creating Bedrock agents with action groups, implementing RAG with knowledge bases, configuring vector stores, setting up content moderation guardrails, managing prompts, orchestrating workflows with flows, and configuring inference profiles for model optimization.
category: aws
tags: [aws, cloudformation, bedrock, ai, ml, agents, knowledge-base, rag, guardrail, inference, infrastructure, iaac]
version: 2.2.0
allowed-tools: Read, Write, Bash
---

# AWS CloudFormation Amazon Bedrock

## Overview

Create production-ready AI infrastructure using AWS CloudFormation templates for Amazon Bedrock. This skill covers Bedrock agents, knowledge bases for RAG implementations, data source connectors, guardrails for content moderation, prompt management, workflow orchestration with flows, and inference profiles for optimized model access.

## When to Use

Use this skill when:
- Creating Bedrock agents with action groups and function definitions
- Implementing Retrieval-Augmented Generation (RAG) with knowledge bases
- Configuring data sources (S3, web crawl, custom connectors)
- Setting up vector store configurations (OpenSearch, Pinecone, pgvector)
- Creating content moderation guardrails
- Managing prompt templates and versions
- Orchestrating AI workflows with Bedrock Flows
- Configuring inference profiles for multi-model access
- Organizing templates with Parameters, Outputs, Mappings, Conditions
- Implementing cross-stack references with export/import

## Instructions

1. **Define Agent Parameters**: Specify foundation model, agent name, and description
2. **Create Agent Resource Role**: Configure IAM role with `bedrock:InvokeModel` permissions scoped to specific models
3. **Set Up Knowledge Base**: Define vector store configuration (OpenSearch/Pinecone/pgvector) and embedding model
4. **Configure Data Sources**: Connect S3 buckets or other data sources with chunking configuration
5. **Add Guardrails**: Implement topic policies, PII filters, content filters, word policies, and grounding checks
6. **Create Action Groups**: Define Lambda functions for agent API operations with API schemas
7. **Configure Flows**: Build workflow orchestration with classifier, model, knowledge base, and Lambda nodes
8. **Set Up Inference Profiles**: Configure multi-model access for optimized routing
9. **Export Outputs**: Export AgentId, KnowledgeBaseId, GuardrailId for cross-stack references

## Best Practices

### Security
- Use IAM roles with minimum necessary permissions for Bedrock operations
- Enable encryption for all knowledge base data and vectors
- Use guardrails for content moderation in production
- Use AWS Secrets Manager for API keys (e.g., Pinecone)
- Audit Bedrock API calls with CloudTrail

### Performance
- Choose appropriate embedding models based on use case
- Optimize chunking strategies (FIXED_SIZE with MaxTokens 512-1000, OverlapPercentage 10-20)
- Use inference profiles for consistent latency across models
- Configure appropriate timeouts for long-running operations

### Cost Optimization
- Use on-demand pricing for variable workloads
- Implement caching for frequent model invocations
- Choose appropriate model sizes for task requirements
- Monitor and optimize token consumption

## Examples

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Bedrock agent with knowledge base

Resources:
  AgentRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-agent-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: BedrockInvoke
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}::foundation-model/*"

  BedrockAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-agent"
      FoundationModel: anthropic.claude-sonnet-4-20250514
      AgentResourceRoleArn: !GetAtt AgentRole.Arn
      AutoPrepare: true

  ContentGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      GuardrailName: !Sub "${AWS::StackName}-guardrail"
      TopicPolicy:
        Topics:
          - Name: FinancialAdvice
            Definition: Providing financial investment advice
            Type: DENIED
      SensitiveInformationPolicy:
        PiiEntities:
          - Name: SSN
            Action: BLOCK

Outputs:
  AgentId:
    Value: !GetAtt BedrockAgent.AgentId
    Export:
      Name: !Sub "${AWS::StackName}-AgentId"
```

## Constraints and Warnings

- **Regional Availability**: Not all foundation models are available in all regions
- **Agent Preparation**: AutoPrepare agents may take time to initialize
- **Knowledge Base Sync**: Data source synchronization is not instantaneous
- **Vector Store Limits**: Vector dimension limits vary by provider
- **Rate Limiting**: API rate limits vary by model and can affect agent performance
- **Token Limits**: Different models have different token limits for input and output
- **Guardrail Coverage**: Guardrails cannot intercept all types of harmful content
- **On-Demand Pricing**: Model invocation costs can accumulate quickly with agents

## References

For complete production-ready examples, see [Examples](references/examples.md).
For detailed property reference for all Bedrock CloudFormation resources, see [Reference](references/reference.md).
