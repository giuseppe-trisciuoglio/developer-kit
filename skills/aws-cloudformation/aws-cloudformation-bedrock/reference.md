# AWS CloudFormation Bedrock - Reference

This reference guide contains detailed information about AWS CloudFormation resources, intrinsic functions, and configurations for Amazon Bedrock infrastructure.

## AWS::Bedrock::Agent

Creates a Bedrock agent that can be used to build AI-powered applications with conversational capabilities.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AgentName | String | Yes | The name of the agent |
| Description | String | No | Description of the agent's purpose |
| FoundationModel | String | Yes | The foundation model to use |
| AgentResourceRoleArn | String | Yes | ARN of the IAM role for the agent |
| IdleSessionTTLInSeconds | Integer | No | Session timeout in seconds (300-3600) |
| AutoPrepare | Boolean | No | Whether to auto-prepare the agent |
| KnowledgeBases | List of KnowledgeBaseConfig | No | Knowledge bases to associate |
| ActionGroups | List of ActionGroupConfig | No | Action groups to configure |

### KnowledgeBaseConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| KnowledgeBaseId | String | Yes | ID of the knowledge base |
| Description | String | No | Description of the knowledge base |

### ActionGroupConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ActionGroupName | String | Yes | Name of the action group |
| Description | String | No | Description of the action group |
| ActionGroupExecutor | ActionGroupExecutor | No | Executor configuration |
| ApiSchema | ApiSchema | No | API schema for the action group |
| SkipModelsInExecution | Boolean | No | Whether to skip model execution |

### ActionGroupExecutor Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Lambda | String | Yes | Lambda function ARN |
| Custom | String | No | Custom executor ARN |

### ApiSchema Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| S3 | S3Location | No | S3 location of the schema |
| Payload | Json | No | Inline OpenAPI schema |

### S3Location Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| S3BucketName | String | Yes | S3 bucket name |
| S3ObjectKey | String | Yes | S3 object key |

### Example

```yaml
Resources:
  MyAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-support-agent"
      Description: Agent for customer support
      FoundationModel: anthropic.claude-v3:5
      AgentResourceRoleArn: !GetAtt AgentRole.Arn
      AutoPrepare: true
      IdleSessionTTLInSeconds: 1800
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| AgentId | The ID of the agent |
| AgentName | The name of the agent |
| AgentArn | The ARN of the agent |
| LatestAgentAliasId | The latest alias ID of the agent |

## AWS::Bedrock::AgentAlias

Creates an alias for a Bedrock agent for versioning and deployment.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AgentId | String | Yes | ID of the agent |
| AgentAliasName | String | Yes | Name of the alias |
| Description | String | No | Description of the alias |
| RoutingConfiguration | List of RoutingConfiguration | No | Routing configuration |

### RoutingConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AgentVersion | String | Yes | Agent version to route to |
| AgentVariant | String | No | Variant of the agent |

### Example

```yaml
Resources:
  AgentAlias:
    Type: AWS::Bedrock::AgentAlias
    Properties:
      AgentId: !Ref MyAgent
      AgentAliasName: production
      Description: Production alias
      RoutingConfiguration:
        - AgentVersion: 2
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| AgentAliasId | The ID of the agent alias |
| AgentAliasArn | The ARN of the agent alias |

## AWS::Bedrock::AgentActionGroup

Configures an action group for a Bedrock agent.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| AgentId | String | Yes | ID of the agent |
| AgentVersion | String | Yes | Version of the agent (DRAFT or version number) |
| ActionGroupName | String | Yes | Name of the action group |
| Description | String | No | Description of the action group |
| ActionGroupExecutor | ActionGroupExecutor | Yes | Executor for the action group |
| ApiSchema | ApiSchema | Yes | API schema for the action group |
| SkipModelsInExecution | Boolean | No | Whether to skip model execution |

### Example

```yaml
Resources:
  MyActionGroup:
    Type: AWS::Bedrock::AgentActionGroup
    Properties:
      AgentId: !Ref MyAgent
      AgentVersion: DRAFT
      ActionGroupName: ApiActionGroup
      Description: API action group
      ActionGroupExecutor:
        Lambda: !Ref ActionGroupFunction
      ApiSchema:
        S3:
          S3BucketName: !Ref SchemaBucket
          S3ObjectKey: api-schema.json
```

## AWS::Bedrock::KnowledgeBase

Creates a knowledge base for Retrieval-Augmented Generation (RAG).

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| KnowledgeBaseName | String | Yes | Name of the knowledge base |
| Description | String | No | Description of the knowledge base |
| EmbeddingModelArn | String | Yes | ARN of the embedding model |
| KnowledgeBaseConfiguration | KnowledgeBaseConfiguration | Yes | Configuration for the knowledge base |
| RoleArn | String | Yes | ARN of the IAM role |

### KnowledgeBaseConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Type of knowledge base (VECTOR) |
| VectorKnowledgeBaseConfiguration | VectorKnowledgeBaseConfiguration | Yes | Vector store configuration |

### VectorKnowledgeBaseConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| VectorStoreConfiguration | VectorStoreConfiguration | Yes | Vector store configuration |

### VectorStoreConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| OpensearchServerlessConfiguration | OpensearchServerlessConfiguration | Cond | OpenSearch Serverless config |
| PineconeConfiguration | PineconeConfiguration | Cond | Pinecone config |
| PgvectorConfiguration | PgvectorConfiguration | Cond | pgvector config |
| RedisEnterpriseCloudConfiguration | RedisEnterpriseCloudConfiguration | Cond | Redis config |

### OpensearchServerlessConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CollectionArn | String | Yes | ARN of the OpenSearch collection |
| VectorIndexName | String | Yes | Name of the vector index |
| FieldMapping | FieldMapping | Yes | Field mapping configuration |

### FieldMapping Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| VectorField | String | Yes | Name of the vector field |
| TextField | String | Yes | Name of the text field |
| MetadataField | String | Yes | Name of the metadata field |

### PineconeConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ConnectionString | String | Yes | Pinecone connection string |
| CredentialsSecretArn | String | Yes | ARN of the secret with credentials |
| Namespace | String | No | Pinecone namespace |
| FieldMapping | PineconeFieldMapping | Yes | Field mapping configuration |

### PineconeFieldMapping Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| TextField | String | Yes | Name of the text field |
| MetadataField | String | Yes | Name of the metadata field |

### PgvectorConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ConnectionString | String | Yes | PostgreSQL connection string |
| TableName | String | Yes | Name of the table |
| ColumnName | String | Yes | Name of the vector column |
| FieldMapping | FieldMapping | Yes | Field mapping configuration |

### Example

```yaml
Resources:
  MyKnowledgeBase:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      KnowledgeBaseName: !Sub "${AWS::StackName}-kb"
      Description: Knowledge base for documents
      EmbeddingModelArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/amazon.titan-embed-text-v1"
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          VectorStoreConfiguration:
            OpensearchServerlessConfiguration:
              CollectionArn: !GetAtt Collection.Arn
              VectorIndexName: kb-index
              FieldMapping:
                VectorField: vector
                TextField: text
                MetadataField: metadata
      RoleArn: !GetAtt KnowledgeBaseRole.Arn
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| KnowledgeBaseId | The ID of the knowledge base |
| KnowledgeBaseArn | The ARN of the knowledge base |

## AWS::Bedrock::DataSource

Creates a data source for a knowledge base.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| KnowledgeBaseId | String | Yes | ID of the knowledge base |
| DataSourceName | String | Yes | Name of the data source |
| Description | String | No | Description of the data source |
| DataSourceConfiguration | DataSourceConfiguration | Yes | Configuration for the data source |
| VectorIngestionConfiguration | VectorIngestionConfiguration | No | Vector ingestion configuration |

### DataSourceConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Type of data source (S3, WEB, CUSTOM) |
| S3Configuration | S3Configuration | Cond | S3 configuration |
| WebConfiguration | WebConfiguration | Cond | Web crawl configuration |

### S3Configuration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| BucketArn | String | Yes | ARN of the S3 bucket |
| InclusionPrefixes | List of String | No | Prefixes to include |
| ExclusionPrefixes | List of String | No | Prefixes to exclude |

### WebConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| SourceUrl | String | Yes | URL to crawl |
| CrawlScope | String | No | Crawl scope (HOST_ONLY, SUBDOMAINS) |
| InclusionFilters | List of String | No | URL patterns to include |
| ExclusionFilters | List of String | No | URL patterns to exclude |
| ExtractionEngine | String | No | Extraction engine (NONE, CHANGE0, BEDROCK_FAST_CHUNKER) |

### VectorIngestionConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ChunkingConfiguration | ChunkingConfiguration | Yes | Chunking configuration |

### ChunkingConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ChunkingStrategy | String | Yes | Strategy (FIXED_SIZE, NONE, HIERARCHICAL) |
| FixedSizeChunking | FixedSizeChunking | Cond | Fixed size configuration |
| HierarchicalChunking | HierarchicalChunking | Cond | Hierarchical configuration |

### FixedSizeChunking Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| MaxTokens | Integer | Yes | Maximum tokens per chunk |
| OverlapPercentage | Integer | No | Overlap percentage (0-25) |

### HierarchicalChunking Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Level1MaxTokens | Integer | Yes | Max tokens for level 1 |
| Level2MaxTokens | Integer | Yes | Max tokens for level 2 |
| OverlapTokens | Integer | No | Overlap tokens |

### Example

```yaml
Resources:
  MyDataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref KnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-datasource"
      Description: S3 data source for documents
      DataSourceConfiguration:
        Type: S3
        S3Configuration:
          BucketArn: !Ref DocumentBucket
          InclusionPrefixes:
            - documents/
            - pdfs/
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: FIXED_SIZE
          FixedSizeChunking:
            MaxTokens: 512
            OverlapPercentage: 20
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| DataSourceId | The ID of the data source |

## AWS::Bedrock::Guardrail

Creates a guardrail for content moderation.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GuardrailName | String | Yes | Name of the guardrail |
| Description | String | No | Description of the guardrail |
| TopicPolicy | TopicPolicy | No | Topic policy configuration |
| ContentPolicy | ContentPolicy | No | Content policy configuration |
| WordPolicy | WordPolicy | No | Word policy configuration |
| SensitiveInformationPolicy | SensitiveInformationPolicy | No | Sensitive info policy |

### TopicPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Topics | List of Topic | Yes | List of topics |

### Topic Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the topic |
| Definition | String | Yes | Definition of the topic |
| Examples | List of String | No | Examples of the topic |
| Type | String | Yes | Type (DENIED) |

### ContentPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Filters | List of ContentFilter | Yes | Content filters |

### ContentFilter Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Filter type (PROFANITY, HATE, SEXUAL, VIOLENCE) |
| InputStrength | String | No | Input strength (NONE, LOW, MEDIUM, HIGH) |
| OutputStrength | String | No | Output strength (NONE, LOW, MEDIUM, HIGH) |

### WordPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Words | List of Word | No | Custom words |
| ManagedWordLists | List of ManagedWordList | No | Managed word lists |

### Word Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Text | String | Yes | Word text |
| InputAction | String | No | Input action (BLOCK, MASK) |
| OutputAction | String | No | Output action (BLOCK, MASK) |

### ManagedWordList Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Type (PROFANITY) |

### SensitiveInformationPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| PiiEntities | List of PiiEntity | No | PII entities |
| Regexes | List of Regex | No | Custom regex patterns |

### PiiEntity Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | PII type name |
| Action | String | Yes | Action (BLOCK, MASK) |

### Regex Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Regex name |
| Pattern | String | Yes | Regex pattern |
| Action | String | Yes | Action (BLOCK, MASK) |

### ContextualGroundingPolicy Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Filters | List of GroundingFilter | Yes | Grounding filters |

### GroundingFilter Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Filter type (GROUNDING, RELEVANCE) |
| Threshold | Double | Yes | Threshold value (0-1) |

### Example

```yaml
Resources:
  MyGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      GuardrailName: !Sub "${AWS::StackName}-guardrail"
      Description: Content moderation guardrail
      TopicPolicy:
        Topics:
          - Name: FinancialAdvice
            Definition: Personalized financial investment advice
            Type: DENIED
      ContentPolicy:
        Filters:
          - Type: PROFANITY
            InputStrength: LOW
            OutputStrength: LOW
          - Type: HATE
            InputStrength: MEDIUM
            OutputStrength: HIGH
      WordPolicy:
        Words:
          - Text: "spam"
            Action: BLOCK
        ManagedWordLists:
          - Type: PROFANITY
      SensitiveInformationPolicy:
        PiiEntities:
          - Name: EMAIL
            Action: MASK
          - Name: SSN
            Action: BLOCK
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| GuardrailId | The ID of the guardrail |
| GuardrailVersion | The version of the guardrail |
| GuardrailArn | The ARN of the guardrail |

## AWS::Bedrock::GuardrailVersion

Creates a version of a guardrail.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| GuardrailId | String | Yes | ID of the guardrail |
| Description | String | No | Description of the version |

### Attributes

| Attribute | Description |
|-----------|-------------|
| GuardrailVersion | The version of the guardrail |

## AWS::Bedrock::Prompt

Creates a prompt template for reuse.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the prompt |
| Description | String | No | Description of the prompt |
| DefaultVariant | String | No | Default variant name |
| Variants | List of PromptVariant | Yes | Prompt variants |

### PromptVariant Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Variant name |
| Description | String | No | Variant description |
| Text | String | Yes | Prompt text |
| InferenceConfiguration | InferenceConfiguration | No | Model configuration |

### InferenceConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Temperature | Double | No | Temperature (0-1) |
| TopP | Double | No | Top P (0-1) |
| MaxTokens | Integer | No | Max tokens |
| StopSequences | List of String | No | Stop sequences |

### Example

```yaml
Resources:
  MyPrompt:
    Type: AWS::Bedrock::Prompt
    Properties:
      Name: !Sub "${AWS::StackName}-support-prompt"
      Description: Customer support prompt
      DefaultVariant: empathetic
      Variants:
        - Name: empathetic
          Description: Empathetic response style
          Text: |
            You are a helpful customer support agent.
            Always be empathetic and understanding.
            User query: {{query}}
          InferenceConfiguration:
            Temperature: 0.7
            MaxTokens: 1000
        - Name: professional
          Description: Professional response style
          Text: |
            You are a professional customer support agent.
            Provide factual and concise responses.
            User query: {{query}}
          InferenceConfiguration:
            Temperature: 0.3
            MaxTokens: 800
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The ID of the prompt |
| Arn | The ARN of the prompt |

## AWS::Bedrock::Flow

Creates a flow for workflow orchestration.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Name of the flow |
| Description | String | No | Description of the flow |
| ExecutionRoleArn | String | Yes | ARN of the execution role |
| Definition | FlowDefinition | Yes | Flow definition |
| DefinitionS3Location | S3Location | No | S3 location of definition |

### FlowDefinition Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| StartAt | String | Yes | Name of the starting node |
| Nodes | Map of FlowNode | Yes | Map of nodes |
| Connections | List of Connection | No | Connections between nodes |

### FlowNode Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Type | String | Yes | Node type |
| Name | String | Yes | Node name |
| Description | String | No | Node description |
| Configuration | FlowNodeConfiguration | No | Node configuration |
| Transitions | Transitions | No | Node transitions |
| IsEnd | Boolean | No | Whether this is an end node |

### FlowNodeConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| BedrockClassifierConfiguration | ClassifierConfiguration | Cond | Classifier config |
| BedrockModelConfiguration | ModelConfiguration | Cond | Model config |
| KnowledgeBaseConfiguration | FlowKnowledgeBaseConfiguration | Cond | Knowledge base config |
| LambdaConfiguration | LambdaConfiguration | Cond | Lambda config |

### ClassifierConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| BedrockClassifierConfiguration | BedrockClassifierConfiguration | Yes | Bedrock classifier config |

### BedrockClassifierConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| BedrockFoundationModelConfiguration | BedrockFoundationModelConfiguration | Yes | Model config |
| InputConfiguration | ClassifierInputConfiguration | Yes | Input config |
| OutputConfiguration | ClassifierOutputConfiguration | Yes | Output config |

### ModelConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ModelId | String | Yes | Model ID |
| InferenceConfiguration | InferenceConfiguration | No | Inference config |

### Transitions Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Next | String | No | Next node name |
| Conditional | List of ConditionalTransition | No | Conditional transitions |

### ConditionalTransition Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Next | String | Yes | Next node name |
| Condition | String | Yes | Condition expression |

### Connection Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | String | Yes | Connection name |
| Source | String | Yes | Source node name |
| Target | String | Yes | Target node name |
| Type | String | Yes | Connection type |

### Example

```yaml
Resources:
  MyFlow:
    Type: AWS::Bedrock::Flow
    Properties:
      Name: !Sub "${AWS::StackName}-processing-flow"
      Description: Customer request processing flow
      ExecutionRoleArn: !GetAtt FlowRole.Arn
      Definition:
        StartAt: Classifier
        Nodes:
          Classifier:
            Type: Classifier
            Name: Classifier
            Configuration:
              BedrockClassifierConfiguration:
                BedrockFoundationModelConfiguration:
                  ModelId: anthropic.claude-v3:5
                InputConfiguration:
                  TextInput:
                    Name: input
                OutputConfiguration:
                  StructuredOutput:
                    Name: intent
            Transitions:
              Next:
                Support: intent.support
                Sales: intent.sales
                General: "*"
          Support:
            Type: KnowledgeBase
            Name: SupportKnowledgeBase
            Configuration:
              KnowledgeBaseConfiguration:
                KnowledgeBaseId: !Ref SupportKB
            Transitions:
              Next: ResponseGenerator
          Sales:
            Type: Model
            Name: SalesModel
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
            Transitions:
              Next: ResponseGenerator
          General:
            Type: Model
            Name: GeneralModel
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
            Transitions:
              Next: ResponseGenerator
          ResponseGenerator:
            Type: Model
            Name: ResponseGenerator
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
            IsEnd: true
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The ID of the flow |
| Arn | The ARN of the flow |
| Status | The status of the flow |

## AWS::Bedrock::ApplicationInferenceProfile

Creates an application inference profile for optimized model access.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ApplicationInferenceProfileName | String | Yes | Name of the profile |
| Description | String | No | Description of the profile |
| ModelSource | ModelSource | Yes | Source model configuration |
| InferenceConfiguration | InferenceConfiguration | No | Inference configuration |

### ModelSource Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| CopyFrom | String | Yes | ARN to copy from |

### InferenceConfiguration Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Text | Map of TextConfig | No | Text model configurations |

### TextConfig Structure

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Temperature | Double | No | Temperature (0-1) |
| MaxTokens | Integer | No | Max tokens |
| TopP | Double | No | Top P (0-1) |

### Example

```yaml
Resources:
  MyProfile:
    Type: AWS::Bedrock::ApplicationInferenceProfile
    Properties:
      ApplicationInferenceProfileName: !Sub "${AWS::StackName}-profile"
      Description: Production inference profile
      ModelSource:
        CopyFrom: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:application-inference-profile/*"
      InferenceConfiguration:
        Text:
          anthropic.claude-v3:5:
            Temperature: 0.7
            MaxTokens: 4096
          anthropic.claude-sonnet-4-20250514:
            Temperature: 0.7
            MaxTokens: 4096
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| Id | The ID of the inference profile |
| Arn | The ARN of the inference profile |

## Intrinsic Functions Reference

### !Ref

Returns the value of the specified parameter or resource.

```yaml
# Reference a parameter
AgentName: !Ref AgentNameParam

# Reference a resource (returns the physical ID)
AgentId: !Ref MyAgent
```

### !GetAtt

Returns the value of an attribute from a Bedrock resource.

```yaml
# Get the agent ID
AgentId: !GetAtt MyAgent.AgentId

# Get the agent ARN
AgentArn: !GetAtt MyAgent.AgentArn

# Get knowledge base ID
KnowledgeBaseId: !GetAtt KnowledgeBase.KnowledgeBaseId

# Get guardrail ID
GuardrailId: !GetAtt Guardrail.GuardrailId
```

### !Sub

Substitutes variables in an input string.

```yaml
# With variable substitution
AgentName: !Sub "${AWS::StackName}-agent"

# With multiple variables
ModelArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/${ModelId}"
```

### !ImportValue

Imports values exported by other stacks.

```yaml
# Import from another stack
AgentId: !ImportValue
  Fn::Sub: "${BedrockStackName}-AgentId"
```

### !FindInMap

Returns the value from a mapping.

```yaml
# Find in mapping
Temperature: !FindInMap [ModelConfig, !Ref Model, Temperature]
```

### !If

Returns one value if condition is true, another if false.

```yaml
# Conditional model selection
ModelId: !If [UseClaude, anthropic.claude-v3:5, amazon.titan-text-express-v1]
```

## IAM Policy Examples for Bedrock

### Bedrock Agent Invoke Policy

```yaml
Policies:
  - PolicyName: BedrockAgentInvoke
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeAgent
          Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:agent/*"
```

### Bedrock Model Invoke Policy

```yaml
Policies:
  - PolicyName: BedrockModelInvoke
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeModel
            - bedrock:InvokeModelWithResponseStream
          Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/*"
```

### Knowledge Base Access Policy

```yaml
Policies:
  - PolicyName: KnowledgeBaseAccess
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - bedrock:Retrieve
            - bedrock:RetrieveAndGenerate
          Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/*"
```

### Guardrail Policy

```yaml
Policies:
  - PolicyName: GuardrailPolicy
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - bedrock:ApplyGuardrail
          Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:guardrail/*"
```

## Supported Foundation Models

| Model Provider | Model ID | Description |
|----------------|----------|-------------|
| Anthropic | anthropic.claude-v2:1 | Claude 2.1 |
| Anthropic | anthropic.claude-v3:5 | Claude 3.5 Sonnet |
| Anthropic | anthropic.claude-sonnet-4-20250514 | Claude Sonnet 4 |
| Anthropic | anthropic.claude-haiku-3-20250514 | Claude Haiku 3 |
| Amazon | amazon.titan-text-express-v1 | Titan Text Express |
| Amazon | amazon.titan-text-lite-v1 | Titan Text Lite |
| Amazon | amazon.titan-embed-text-v1 | Titan Embeddings |
| Amazon | amazon.titan-embed-text-v2:0 | Titan Embeddings v2 |
| Meta | meta.llama3-70b-instruct-v1:0 | Llama 3 70B |
| Meta | meta.llama3-8b-instruct-v1:0 | Llama 3 8B |
| Meta | meta.llama3.1-70b-instruct-v1:0 | Llama 3.1 70B |
| Cohere | cohere.command-text-v14:0 | Command |
| Cohere | cohere.embed-multilingual-v3:0 | Multilingual Embeddings |
| Stability AI | stability.stable-diffusion-xl-v1 | Stable Diffusion XL |

## Limits and Quotas

### Bedrock Agent Limits

| Resource | Default Limit |
|----------|---------------|
| Agents per account | 50 |
| Aliases per agent | 20 |
| Action groups per agent | 20 |
| Knowledge bases per agent | 10 |
| Agent session duration | 30 minutes |

### Knowledge Base Limits

| Resource | Default Limit |
|----------|---------------|
| Knowledge bases per account | 100 |
| Data sources per knowledge base | 10 |
| Documents per data source | 10,000,000 |
| Vector dimensions (Titan) | 1536 |
| Chunk size (max tokens) | 3000 |

### Guardrail Limits

| Resource | Default Limit |
|----------|---------------|
| Guardrails per account | 20 |
| Topics per guardrail | 10 |
| Words per guardrail | 1000 |
| PII types per guardrail | 50 |
| Regex patterns per guardrail | 10 |

### Flow Limits

| Resource | Default Limit |
|----------|---------------|
| Flows per account | 100 |
| Nodes per flow | 50 |
| Connections per flow | 100 |
| Flow execution duration | 30 minutes |

## Common Tags for Bedrock

```yaml
Resources:
  MyAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: team@example.com
        - Key: ManagedBy
          Value: CloudFormation
        - Key: Version
          Value: "1.0.0"
```

## Related Resources

- [AWS::IAM::Role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)
- [AWS::S3::Bucket](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html)
- [AWS::OpenSearchServerless::Collection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-opensearchserverless-collection.html)
- [AWS::Lambda::Function](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)
- [AWS::SecretsManager::Secret](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-secretsmanager-secret.html)
