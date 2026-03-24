# AWS Bedrock Constraints and Limitations

## Resource Limits

### Agent and Knowledge Base Limits

```yaml
# Agent limits vary by region
# Knowledge bases have document and storage limits
# Guardrails have account-level limits

Parameters:
  MaxKnowledgeBaseDocuments:
    Type: Number
    Default: 10000
    Description: Expected number of documents in knowledge base

  MaxGuardrails:
    Type: Number
    Default: 10
    Description: Expected number of guardrails
```

## Model Availability Constraints

### Regional Model Availability

```yaml
# Not all foundation models available in all regions
# Check model availability before deployment

Parameters:
  ModelRegion:
    Type: String
    Default: us-east-1
    AllowedValues:
      - us-east-1
      - us-west-2
      - eu-west-1
      - eu-central-1
      - ap-southeast-1
      - ap-northeast-1
    Description: Region for model deployment

Resources:
  BedrockAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-agent"
      AgentResourceRoleArn: !Ref AgentRole
      FoundationModel: !Sub "${ModelRegion}.amazon.${FoundationModel}"
```

### Model-Specific Constraints

```yaml
# Different models have different token limits
# Rate limiting varies by model

Parameters:
  FoundationModel:
    Type: String
    Default: anthropic.claude-3-sonnet-20240229-v1:0
    AllowedValues:
      - anthropic.claude-3-sonnet-20240229-v1:0
      - anthropic.claude-3-haiku-20240307-v1:0
      - anthropic.claude-3-opus-20240229-v1:0
      - amazon.titan-text-express-v1
      - ai21.jamba-1-2-ultra-v1:0
    Description: Foundation model identifier

  MaxTokens:
    Type: Number
    Default: 4096
    MaxValue: 100000
    Description: Maximum tokens per request
```

## Operational Constraints

### Agent Initialization

```yaml
# AutoPrepare agents may take time to initialize
# Plan for cold start delays

Resources:
  BedrockAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-agent"
      AutoPrepare: true
      # Agent initialization may take several minutes
```

### Knowledge Base Sync

```yaml
# Data source synchronization is not instantaneous
# Plan for sync delays when using S3 or web crawl

Resources:
  DataSource:
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
      # S3 sync is near-instant but web crawl takes time
```

## Security Constraints

### PII Protection

```yaml
# Sensitive information may not be detected in all formats
# Implement additional validation as needed

Resources:
  Guardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      Name: pii-protection
      SensitiveInformationPolicyConfig:
        PIIEntitiesConfig:
          - Name: EmailAddress
            Type: EMAIL
          - Name: SSN
            Type: CUSTOM_ID
            # Additional PII types as needed
```

### Web Crawl Security

```yaml
# Web-crawled content is untrusted and may contain prompt injection payloads
# Always restrict to trusted domains and validate content

Resources:
  WebCrawlDataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref KnowledgeBase
      Name: web-crawl-source
      Type: WEB
      DataSourceConfiguration:
        WebConfiguration:
          SeedUrls:
            - !Ref TrustedUrl
          # CRITICAL: Restrict to trusted internal domains only
          InclusionFilters:
            - FilterType: DOMAIN
              Pattern: !Sub ".*\\.${TrustedDomain}"
          ExclusionFilters:
            # Exclude potentially malicious content
            - FilterType: CONTENT_TYPE
              Pattern: "application/x-executable"
            - FilterType: PATTERN
              Pattern: "<script>"
      # NEVER crawl public websites without validation
```

### Nested Template Security

```yaml
# Always use parameterized TemplateURL values
# NEVER hardcode S3 URLs for nested stack templates

Parameters:
  TemplateBucket:
    Type: AWS::S3::Bucket::Name
    Description: Trusted S3 bucket for templates

Resources:
  NestedStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "https://${TemplateBucket}.s3.${AWS::Region}.amazonaws.com/bedrock-nested.yaml"
      # CORRECT: Parameterized with !Sub
      # WRONG: TemplateURL: "https://my-bucket.s3.us-east-1.amazonaws.com/template.yaml"
```

### Input Validation

```yaml
# Validate content ingested through knowledge bases before indexing
# Implement validation filters for S3 and web crawl sources

Resources:
  S3DataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref KnowledgeBase
      Name: validated-s3-source
      Type: S3
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !GetAtt DataBucket.Arn
          # Validate files before syncing
          InclusionPrefixes:
            - validated/
      # Implement Lambda function to validate content before sync
```

## Cost Considerations

### Token Usage Optimization

```yaml
# RAG implementations increase token consumption
# Use chunking and filtering strategies

Parameters:
  ChunkSize:
    Type: Number
    Default: 300
    AllowedValues:
      - 100
      - 300
      - 500
      - 1000
    Description: Chunk size for documents (affects token usage)

  MaxChunks:
    Type: Number
    Default: 20
    Description: Maximum chunks to retrieve
```

### Knowledge Base Costs

```yaml
# Storing and syncing large datasets increases costs
# Use appropriate storage classes

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
          # Storage and sync costs apply
```

## Best Practices to Avoid Constraints

### Use Appropriate Models

```yaml
# Select models based on use case requirements
# Use smaller models for simple tasks

Parameters:
  ModelType:
    Type: String
    Default: claude-3-haiku
    AllowedValues:
      - claude-3-haiku      # Fast, cost-effective
      - claude-3-sonnet     # Balanced performance
      - claude-3-opus       # Most capable
    Description: Model selection based on task complexity
```

### Optimize Knowledge Base Queries

```yaml
# Use filtering to reduce token usage
# Implement relevance scoring

Resources:
  BedrockAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: optimized-agent
      Instruction: |
        Use knowledge base retrieval filtering to reduce costs.
        Only retrieve relevant documents for the query.
      KnowledgeBaseIds:
        - !Ref KnowledgeBase
      KnowledgeBaseConfiguration:
        KnowledgeBaseState: ENABLED
        RetrievalConfiguration:
          VectorSearchConfiguration:
            NumberOfResults: 5  # Limit retrieved documents
```

### Monitor Token Consumption

```yaml
# Set up budget alerts for Bedrock usage

Resources:
  BedrockBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetLimit:
          Amount: 100
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon Bedrock
```

## Quota Management

### Request Quota Increases

```yaml
# Service quotas can be increased via AWS Support
# Document requirements in stack outputs

Outputs:
  QuotaIncreaseRequest:
    Description: Link to request quota increase
    Value: !Sub "https://console.aws.amazon.com/support/home#/case/create?issueType=service-limit-increase&serviceCode=amazon-bedrock"
```
