---
name: aws-cloudformation-bedrock
description: Provides AWS CloudFormation patterns for Amazon Bedrock resources including agents, knowledge bases, data sources, guardrails, prompts, flows, and inference profiles. Use when creating Bedrock agents with action groups, implementing RAG with knowledge bases, configuring vector stores, setting up content moderation guardrails, managing prompts, orchestrating workflows with flows, and configuring inference profiles for model optimization.
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
- Setting up application inference profiles for optimized model routing
- Organizing templates with Parameters, Outputs, Mappings, Conditions
- Implementing cross-stack references with export/import

## Instructions

Follow these steps to create Bedrock infrastructure with CloudFormation:

### 1. Define Agent Parameters

Specify foundation model, agent name, and description:

```yaml
Parameters:
  FoundationModel:
    Type: String
    Default: anthropic.claude-3-sonnet-20240229-v1:0
    AllowedValues:
      - anthropic.claude-3-sonnet-20240229-v1:0
      - anthropic.claude-3-haiku-20240307-v1:0
      - amazon.titan-text-express-v1
    Description: Foundation model for agent

  AgentName:
    Type: String
    Default: bedrock-agent
    Description: Name of the Bedrock agent
```

### 2. Create Agent Resource Role

Configure IAM role with bedrock:InvokeModel permissions:

```yaml
Resources:
  AgentRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: BedrockPermissions
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}::foundation-model/${FoundationModel}"
```

### 3. Set Up Knowledge Base

Define vector store configuration and embedding model:

```yaml
Resources:
  KnowledgeBase:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      Name: !Sub "${AWS::StackName}-kb"
      RoleArn: !Ref KnowledgeBaseRole
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          EmbeddingModelArn: !Ref EmbeddingModel
```

### 4. Configure Data Sources

Connect S3 buckets or other data sources to knowledge base:

```yaml
Resources:
  S3DataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref KnowledgeBase
      Name: s3-data-source
      Type: S3
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !GetAtt DataBucket.Arn
          InclusionPrefixes:
            - documents/
```

### 5. Add Guardrails

Implement content moderation policies:

```yaml
Resources:
  Guardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      Name: content-moderation
      BlockedInputMessaging:
        Text: "I cannot help with that request."
      ContentPolicyConfig:
        FiltersConfig:
          HarmfulContent: {}
```

### 6. Create Action Groups

Define Lambda functions for agent API operations:

```yaml
Resources:
  ActionGroup:
    Type: AWS::Bedrock::AgentActionGroup
    Properties:
      ActionGroupName: api-operations
      ActionGroupState: ENABLED
      ParentAgentId: !Ref BedrockAgent
      FunctionSchema:
        Functions:
          - Name: GetInventory
            Description: Get current inventory status
            Parameters:
              type: object
        ActionExecutor:
          Lambda: !Ref ActionLambdaFunction
```

### 7. Configure Flows

Build workflow orchestration:

```yaml
Resources:
  Flow:
    Type: AWS::Bedrock::Flow
    Properties:
      Name: !Sub "${AWS::StackName}-flow"
      Definition:
        entities:
          - id: agent-1
            type: Agent
            name: DataProcessor
          - id: lambda-1
            type: Lambda
            name: DataValidator
        connections:
          - from: lambda-1
            to: agent-1
```

## Best Practices

### Security

- Restrict web crawl data sources to trusted internal domains only
- Validate content before ingesting into knowledge bases
- Use parameterized TemplateURL values for nested stacks
- Implement guardrails for content moderation
- Apply least privilege IAM policies to agent roles
- Encrypt sensitive data in knowledge bases
- Monitor for prompt injection in web-crawled content

### Cost Optimization

- Use appropriate model selection for task complexity
- Implement knowledge base retrieval filtering
- Set chunk size limits to control token usage
- Monitor token consumption with CloudWatch
- Use auto-prepare agents strategically
- Implement batch processing for non-real-time workloads
- Use knowledge base filtering to reduce costs

### Performance

- Optimize chunk size for embedding quality vs. cost
- Use vector store optimization (OpenSearch, Pinecone)
- Implement caching for frequently accessed knowledge base content
- Configure appropriate knowledge base sync intervals
- Use provisioned throughput for vector databases
- Monitor agent initialization and cold start times
- Implement graceful degradation for rate limiting

### Data Management

- Use appropriate inclusion/exclusion filters for data sources
- Implement document validation before indexing
- Use versioning for knowledge base updates
- Configure appropriate sync intervals for data sources
- Implement content deduplication in knowledge bases
- Use metadata filtering for improved retrieval accuracy
- Monitor knowledge base size and document limits

## References

For detailed implementation guidance, see:

- **[constraints.md](references/constraints.md)** - Resource limits (agent limits, knowledge base limits, guardrail limits, flow limits), model availability constraints (regional availability, model updates, rate limiting, token limits), operational constraints (agent initialization, knowledge base sync, vector store limits, RAG accuracy), security constraints (PII protection, agent permissions, VPC endpoints, environment variable security, web crawl security, nested template security, input validation), and cost considerations (on-demand pricing, knowledge base storage, guardrail usage, token usage)

## Related Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/)
- [Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html)
