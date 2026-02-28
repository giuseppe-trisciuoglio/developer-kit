# AWS CloudFormation Bedrock - Examples

This file contains comprehensive examples for Amazon Bedrock patterns with CloudFormation.

## Example 1: Complete Bedrock Agent with Action Groups and Knowledge Base

Complete agent implementation with Lambda action group and knowledge base for RAG.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Complete Bedrock agent with action group and knowledge base

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - production

  AgentName:
    Type: String
    Default: customer-support-agent

  FoundationModel:
    Type: String
    Default: anthropic.claude-v3:5

Mappings:
  EnvironmentConfig:
    dev:
      IdleTTL: 1800
      AutoPrepare: true
    staging:
      IdleTTL: 1800
      AutoPrepare: true
    production:
      IdleTTL: 3600
      AutoPrepare: true

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Resources:
  # Agent Resource Role
  AgentResourceRole:
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
        - PolicyName: !Sub "${AWS::StackName}-agent-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/*"
              - Effect: Allow
                Action:
                  - bedrock:Retrieve
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/*"
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource: !GetAtt ActionGroupFunction.Arn

  # Action Group Lambda Function
  ActionGroupFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-action-group"
      Runtime: python3.11
      Handler: handler.handler
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/action-group.zip
      Timeout: 30
      Role: !GetAtt LambdaExecutionRole.Arn

  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-lambda-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  # OpenSearch Serverless Collection
  OpenSearchCollection:
    Type: AWS::OpenSearchServerless::Collection
    Properties:
      Name: !Sub "${AWS::StackName}-kb-collection"
      Type: SEARCH

  # Access Policy for OpenSearch
  OpenSearchAccessPolicy:
    Type: AWS::OpenSearchServerless::AccessPolicy
    Properties:
      Name: !Sub "${AWS::StackName}-aoss-access"
      Policy: !Sub |
        [
          {
            "Rules": [
              {
                "Resource": ["collection/${OpenSearchCollection.id}"],
                "Permission": ["aoss:*"]
              },
              {
                "Resource": ["index/collection/${OpenSearchCollection.id}/*"],
                "Permission": ["aoss:*"]
              }
            ],
            "Principal": ["${AgentResourceRole.Arn}"]
          }
        ]
      Type: data

  # Security Policy for OpenSearch
  OpenSearchSecurityPolicy:
    Type: AWS::OpenSearchServerless::SecurityPolicy
    Properties:
      Name: !Sub "${AWS::StackName}-aoss-security"
      Policy: !Sub |
        {
          "Rules": [
            {
              "Resource": ["collection/${OpenSearchCollection.id}"],
              "ResourceType": "collection"
            }
          ],
          "Principal": ["*"]
        }
      Type: encryption

  # Knowledge Base Role
  KnowledgeBaseRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-kb-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-kb-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - aoss:APIAccessAll
                Resource: !GetAtt OpenSearchCollection.Arn
              - Effect: Allow
                Action:
                  - s3:GetObject
                Resource: !Sub "${DocumentBucket.Arn}/*"

  # Knowledge Base
  SupportKnowledgeBase:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      KnowledgeBaseName: !Sub "${AWS::StackName}-support-kb"
      Description: Knowledge base for customer support
      EmbeddingModelArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/amazon.titan-embed-text-v1"
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          VectorStoreConfiguration:
            OpensearchServerlessConfiguration:
              CollectionArn: !GetAtt OpenSearchCollection.Arn
              VectorIndexName: kb-index
              FieldMapping:
                VectorField: vector
                TextField: text
                MetadataField: metadata
      RoleArn: !GetAtt KnowledgeBaseRole.Arn

  # Knowledge Base Data Source
  KnowledgeBaseDataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref SupportKnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-s3-ds"
      Description: S3 data source for support documents
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !Ref DocumentBucket
          InclusionPrefixes:
            - support/
            - faq/
            - policies/
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: FIXED_SIZE
          FixedSizeChunking:
            MaxTokens: 512
            OverlapPercentage: 20

  # Document Bucket
  DocumentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-documents-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled

  # API Schema Bucket
  ApiSchemaBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-schema-${AWS::AccountId}-${AWS::Region}"

  # Bedrock Agent
  CustomerSupportAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AgentName}-${Environment}"
      Description: Customer support agent with knowledge base
      FoundationModel: !Ref FoundationModel
      AgentResourceRoleArn: !GetAtt AgentResourceRole.Arn
      IdleSessionTTLInSeconds: !FindInMap [EnvironmentConfig, !Ref Environment, IdleTTL]
      AutoPrepare: !FindInMap [EnvironmentConfig, !Ref Environment, AutoPrepare]
      KnowledgeBases:
        - KnowledgeBaseId: !Ref SupportKnowledgeBase
          Description: Support documentation knowledge base

  # Action Group
  ApiActionGroup:
    Type: AWS::Bedrock::AgentActionGroup
    Properties:
      AgentId: !Ref CustomerSupportAgent
      AgentVersion: DRAFT
      ActionGroupName: CustomerActions
      Description: Action group for customer operations
      ActionGroupExecutor:
        Lambda: !GetAtt ActionGroupFunction.Arn
      ApiSchema:
        S3:
          S3BucketName: !Ref ApiSchemaBucket
          S3ObjectKey: api-schema.json

Outputs:
  AgentId:
    Description: ID of the Bedrock agent
    Value: !GetAtt CustomerSupportAgent.AgentId
    Export:
      Name: !Sub "${AWS::StackName}-AgentId"

  AgentAliasId:
    Description: Alias ID of the Bedrock agent
    Value: !GetAtt CustomerSupportAgent.LatestAgentAliasId
    Export:
      Name: !Sub "${AWS::StackName}-AgentAliasId"

  AgentArn:
    Description: ARN of the Bedrock agent
    Value: !GetAtt CustomerSupportAgent.AgentArn
    Export:
      Name: !Sub "${AWS::StackName}-AgentArn"

  KnowledgeBaseId:
    Description: ID of the knowledge base
    Value: !GetAtt SupportKnowledgeBase.KnowledgeBaseId
    Export:
      Name: !Sub "${AWS::StackName}-KnowledgeBaseId"
```

## Example 2: Guardrail with Comprehensive Content Moderation

Complete guardrail implementation with topic policy, content filters, and sensitive information protection.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Comprehensive guardrail for content moderation

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # Guardrail for content moderation
  ContentGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      GuardrailName: !Sub "${AWS::StackName}-guardrail"
      Description: Comprehensive content moderation guardrail

      # Topic Policy - Block sensitive topics
      TopicPolicy:
        Topics:
          - Name: MedicalDiagnosis
            Definition: Providing medical diagnosis or treatment recommendations
            Examples:
              - "What could be causing my headache?"
              - "Do I need to see a doctor for this?"
              - "What medication should I take?"
            Type: DENIED
          - Name: LegalAdvice
            Definition: Providing legal advice or representation recommendations
            Examples:
              - "Can I sue my employer?"
              - "What are my legal rights in this situation?"
              - "Should I get a lawyer?"
            Type: DENIED
          - Name: FinancialInvestment
            Definition: Personalized financial investment recommendations
            Examples:
              - "What stocks should I buy?"
              - "Is crypto a good investment?"
              - "Should I move my 401k?"
            Type: DENIED
          - Name: HazardousActivities
            Definition: Instructions for dangerous or illegal activities
            Examples:
              - "How to make a weapon"
              - "How to hack someone's account"
            Type: DENIED

      # Content Policy - Filter harmful content
      ContentPolicy:
        Filters:
          - Type: PROFANITY
            InputStrength: LOW
            OutputStrength: LOW
          - Type: HATE
            InputStrength: MEDIUM
            OutputStrength: HIGH
          - Type: SEXUAL
            InputStrength: LOW
            OutputStrength: MEDIUM
          - Type: VIOLENCE
            InputStrength: MEDIUM
            OutputStrength: HIGH
          - Type: HARASSMENT
            InputStrength: MEDIUM
            OutputStrength: HIGH

      # Word Policy - Custom blocked words
      WordPolicy:
        Words:
          - Text: "offensive-term-1"
            InputAction: BLOCK
            OutputAction: BLOCK
          - Text: "offensive-term-2"
            InputAction: MASK
            OutputAction: MASK
        ManagedWordLists:
          - Type: PROFANITY

      # Sensitive Information Policy - PII protection
      SensitiveInformationPolicy:
        PiiEntities:
          - Name: EMAIL
            Action: MASK
          - Name: PHONE_NUMBER
            Action: MASK
          - Name: SSN
            Action: BLOCK
          - Name: CREDIT_DEBIT_NUMBER
            Action: BLOCK
          - Name: BANK_ACCOUNT_NUMBER
            Action: BLOCK
          - Name: IP_ADDRESS
            Action: MASK
          - Name: DATE_OF_BIRTH
            Action: MASK
          - Name: DRIVERS_LICENSE
            Action: BLOCK
          - Name: PASSPORT
            Action: BLOCK
        Regexes:
          - Name: CustomApiKeyPattern
            Pattern: "(api|secret|key)-[a-zA-Z0-9]{32}"
            Action: BLOCK
          - Name: PrivateKeyPattern
            Pattern: "-----BEGIN PRIVATE KEY-----"
            Action: BLOCK

      # Contextual Grounding Policy
      ContextualGroundingPolicy:
        Filters:
          - Type: GROUNDING
            Threshold: 0.7
          - Type: RELEVANCE
            Threshold: 0.7

  # Guardrail Version
  GuardrailVersion:
    Type: AWS::Bedrock::GuardrailVersion
    Properties:
      GuardrailId: !Ref ContentGuardrail
      Description: Production version of the guardrail

Outputs:
  GuardrailId:
    Description: ID of the guardrail
    Value: !Ref ContentGuardrail
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailId"

  GuardrailVersion:
    Description: Version of the guardrail
    Value: !GetAtt GuardrailVersion.GuardrailVersion
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailVersion"

  GuardrailArn:
    Description: ARN of the guardrail
    Value: !GetAtt ContentGuardrail.GuardrailArn
    Export:
      Name: !Sub "${AWS::StackName}-GuardrailArn"
```

## Example 3: Knowledge Base with Multiple Data Sources

Knowledge base with S3 and web crawl data sources.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Knowledge base with multiple data sources

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # OpenSearch Collection
  VectorCollection:
    Type: AWS::OpenSearchServerless::Collection
    Properties:
      Name: !Sub "${AWS::StackName}-kb-collection"
      Type: SEARCH

  # Access Policy
  AccessPolicy:
    Type: AWS::OpenSearchServerless::AccessPolicy
    Properties:
      Name: !Sub "${AWS::StackName}-access"
      Policy: !Sub |
        [
          {
            "Rules": [
              {
                "Resource": ["collection/${VectorCollection.id}"],
                "Permission": ["aoss:*"]
              }
            ],
            "Principal": ["${KnowledgeBaseRole.Arn}"]
          }
        ]
      Type: data

  # Knowledge Base Role
  KnowledgeBaseRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-kb-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-kb-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - aoss:APIAccessAll
                Resource: !GetAtt VectorCollection.Arn
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Ref DocumentsBucket
                  - !Sub "${DocumentsBucket.Arn}/*"

  # Knowledge Base
  ProductKnowledgeBase:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      KnowledgeBaseName: !Sub "${AWS::StackName}-product-kb"
      Description: Product documentation knowledge base
      EmbeddingModelArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/amazon.titan-embed-text-v1"
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          VectorStoreConfiguration:
            OpensearchServerlessConfiguration:
              CollectionArn: !GetAtt VectorCollection.Arn
              VectorIndexName: product-kb-index
              FieldMapping:
                VectorField: vector
                TextField: text
                MetadataField: metadata
      RoleArn: !GetAtt KnowledgeBaseRole.Arn

  # S3 Data Source - Documents
  S3DataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref ProductKnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-s3-ds"
      Description: S3 data source for product documents
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !Ref DocumentsBucket
          InclusionPrefixes:
            - product-docs/
            - user-guides/
            - api-reference/
          ExclusionPrefixes:
            - archive/
            - temp/
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: FIXED_SIZE
          FixedSizeChunking:
            MaxTokens: 1000
            OverlapPercentage: 10

  # S3 Data Source - Knowledge Articles
  KnowledgeArticlesDataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref ProductKnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-articles-ds"
      Description: S3 data source for knowledge articles
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !Ref ArticlesBucket
          InclusionPrefixes:
            - articles/
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: HIERARCHICAL
          HierarchicalChunking:
            Level1MaxTokens: 2000
            Level2MaxTokens: 500
            OverlapTokens: 100

  # Web Data Source - Documentation Website
  # SECURITY: Validate and restrict crawl URLs to trusted internal domains only.
  # Web-crawled content is untrusted and may contain prompt injection payloads.
  # Use CrawlScope: HOST_ONLY and strict InclusionFilters to limit exposure.
  WebDataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref ProductKnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-web-ds"
      Description: Web data source for online documentation
      DataSourceConfiguration:
        WebConfiguration:
          SourceUrl: "https://docs.example.com"
          CrawlScope: HOST_ONLY
          InclusionFilters:
            - "https://docs.example.com/*"
          ExtractionEngine: BEDROCK_FAST_CHUNKER
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: FIXED_SIZE
          FixedSizeChunking:
            MaxTokens: 512
            OverlapPercentage: 15

  # Documents Bucket
  DocumentsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-documents-${AWS::AccountId}-${AWS::Region}"

  # Articles Bucket
  ArticlesBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-articles-${AWS::AccountId}-${AWS::Region}"

Outputs:
  KnowledgeBaseId:
    Description: ID of the knowledge base
    Value: !Ref ProductKnowledgeBase

  KnowledgeBaseArn:
    Description: ARN of the knowledge base
    Value: !GetAtt ProductKnowledgeBase.KnowledgeBaseArn
```

## Example 4: Bedrock Flow for Multi-Turn Conversation

Flow with classifier, knowledge base, and Lambda nodes for complex conversation handling.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Bedrock Flow for multi-turn conversation handling

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Flow Execution Role
  FlowRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-flow-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-flow-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/*"
              - Effect: Allow
                Action:
                  - bedrock:Retrieve
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/*"
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource:
                  - !GetAtt OrderStatusFunction.Arn
                  - !GetAtt ProductLookupFunction.Arn

  # Order Status Lambda
  OrderStatusFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-order-status"
      Runtime: python3.11
      Handler: handler.check_status
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/order-status.zip
      Role: !GetAtt LambdaBasicRole.Arn

  # Product Lookup Lambda
  ProductLookupFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${AWS::StackName}-product-lookup"
      Runtime: python3.11
      Handler: handler.lookup_product
      Code:
        S3Bucket: !Ref CodeBucket
        S3Key: lambda/product-lookup.zip
      Role: !GetAtt LambdaBasicRole.Arn

  # Lambda Basic Role
  LambdaBasicRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  # Processing Flow
  CustomerServiceFlow:
    Type: AWS::Bedrock::Flow
    Properties:
      Name: !Sub "${AWS::StackName}-customer-service"
      Description: Multi-turn customer service flow
      ExecutionRoleArn: !GetAtt FlowRole.Arn
      Definition:
        StartAt: IntentClassifier
        Nodes:
          # Classifier Node - Routes to appropriate handler
          IntentClassifier:
            Type: Classifier
            Name: IntentClassifier
            Description: Classifies customer intent
            Configuration:
              BedrockClassifierConfiguration:
                BedrockFoundationModelConfiguration:
                  ModelId: anthropic.claude-v3:5
                  InferenceConfiguration:
                    Temperature: 0.0
                    MaxTokens: 500
                InputConfiguration:
                  TextInput:
                    Name: user_input
                OutputConfiguration:
                  StructuredOutput:
                    Name: intent
                    Description: Classified intent
                    JsonOutputSchema:
                      properties:
                        intent:
                          type: string
                          enum:
                            - order_status
                            - product_info
                            - return_request
                            - account_update
                            - general_inquiry
                        confidence:
                          type: number
                        entities:
                          type: array
            Transitions:
              Next:
                OrderStatus: intent.order_status
                ProductInfo: intent.product_info
                ReturnRequest: intent.return_request
                AccountUpdate: intent.account_update
                GeneralInquiry: "*"

          # Order Status Node
          OrderStatus:
            Type: LambdaFunction
            Name: OrderStatusHandler
            Description: Checks order status
            Configuration:
              LambdaConfiguration:
                LambdaArn: !GetAtt OrderStatusFunction.Arn
                Input:
                  text: "{{user_input}}"
                Output:
                  Name: order_result
            Transitions:
              Next: ResponseFormatter

          # Product Info Node - Uses Knowledge Base
          ProductInfo:
            Type: KnowledgeBase
            Name: ProductKnowledgeBase
            Description: Retrieves product information
            Configuration:
              KnowledgeBaseConfiguration:
                KnowledgeBaseId: !Ref ProductKnowledgeBase
                ModelId: anthropic.claude-v3:5
                RetrievalConfiguration:
                  VectorSearchConfiguration:
                    NumberOfResults: 5
            Transitions:
              Next: ResponseFormatter

          # Return Request Node
          ReturnRequest:
            Type: LambdaFunction
            Name: ReturnRequestHandler
            Description: Processes return requests
            Configuration:
              LambdaConfiguration:
                LambdaArn: !GetAtt OrderStatusFunction.Arn
                Input:
                  text: "{{user_input}}"
                Output:
                  Name: return_result
            Transitions:
              Next: ResponseFormatter

          # Account Update Node
          AccountUpdate:
            Type: Model
            Name: AccountUpdater
            Description: Handles account updates
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
                InferenceConfiguration:
                  Temperature: 0.3
                  MaxTokens: 1000
                  System:
                    - Text: "You are handling a customer account update request. Gather necessary information and confirm changes."
            Transitions:
              Next: ResponseFormatter

          # General Inquiry Node
          GeneralInquiry:
            Type: Model
            Name: GeneralAssistant
            Description: Answers general questions
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
                InferenceConfiguration:
                  Temperature: 0.7
                  MaxTokens: 1500
            Transitions:
              Next: ResponseFormatter

          # Response Formatter Node
          ResponseFormatter:
            Type: Model
            Name: ResponseFormatter
            Description: Formats the final response
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
                InferenceConfiguration:
                  Temperature: 0.5
                  MaxTokens: 2000
                  System:
                    - Text: "You are a customer service response formatter. Provide a clear, helpful, and concise response to the customer."
            Transitions:
              Next: ResponseValidator

          # Response Validator Node
          ResponseValidator:
            Type: Model
            Name: ResponseValidator
            Description: Validates response before sending
            Configuration:
              BedrockModelConfiguration:
                ModelId: anthropic.claude-v3:5
                InferenceConfiguration:
                  Temperature: 0.0
                  MaxTokens: 500
            Transitions:
              Next:
                SendResponse: "*"
                RetryFormatting: ResponseFormatter
            IsEnd: true

Outputs:
  FlowId:
    Description: ID of the flow
    Value: !Ref CustomerServiceFlow

  FlowArn:
    Description: ARN of the flow
    Value: !GetAtt CustomerServiceFlow.Arn
```

## Example 5: Application Inference Profile

Inference profile for optimized multi-model access.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Application inference profile for optimized model access

Parameters:
  ProfileName:
    Type: String
    Default: production-profile

  Environment:
    Type: String
    Default: production

Mappings:
  ModelConfig:
    dev:
      Temperature: 0.9
      MaxTokens: 4096
    staging:
      Temperature: 0.7
      MaxTokens: 4096
    production:
      Temperature: 0.5
      MaxTokens: 8192

Resources:
  # Application Inference Profile
  ProductionInferenceProfile:
    Type: AWS::Bedrock::ApplicationInferenceProfile
    Properties:
      ApplicationInferenceProfileName: !Sub "${ProfileName}-${Environment}"
      Description: Production inference profile for customer service
      ModelSource:
        CopyFrom: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:application-inference-profile/*"
      InferenceConfiguration:
        Text:
          anthropic.claude-v3:5:
            Temperature: !FindInMap [ModelConfig, !Ref Environment, Temperature]
            MaxTokens: !FindInMap [ModelConfig, !Ref Environment, MaxTokens]
            TopP: 0.999
            StopSequences:
              - "\n\nHuman:"
          anthropic.claude-sonnet-4-20250514:
            Temperature: !FindInMap [ModelConfig, !Ref Environment, Temperature]
            MaxTokens: !FindInMap [ModelConfig, !Ref Environment, MaxTokens]
            TopP: 0.999

Outputs:
  InferenceProfileId:
    Description: ID of the inference profile
    Value: !Ref ProductionInferenceProfile

  InferenceProfileArn:
    Description: ARN of the inference profile
    Value: !GetAtt ProductionInferenceProfile.Arn
```

## Example 6: Agent with Guardrail Integration

Bedrock agent with integrated guardrail for safe interactions.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Bedrock agent with guardrail integration

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # Agent Resource Role with Guardrail permissions
  AgentResourceRole:
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
        - PolicyName: !Sub "${AWS::StackName}-agent-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/*"
              - Effect: Allow
                Action:
                  - bedrock:ApplyGuardrail
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:guardrail/*"

  # Guardrail for content moderation
  SafetyGuardrail:
    Type: AWS::Bedrock::Guardrail
    Properties:
      GuardrailName: !Sub "${AWS::StackName}-safety"
      Description: Safety guardrail for agent interactions
      TopicPolicy:
        Topics:
          - Name: DangerousContent
            Definition: Content promoting harm or illegal activities
            Type: DENIED
      ContentPolicy:
        Filters:
          - Type: PROFANITY
            InputStrength: LOW
            OutputStrength: LOW
          - Type: HATE
            InputStrength: MEDIUM
            OutputStrength: HIGH
          - Type: VIOLENCE
            InputStrength: MEDIUM
            OutputStrength: HIGH
      WordPolicy:
        ManagedWordLists:
          - Type: PROFANITY
      SensitiveInformationPolicy:
        PiiEntities:
          - Name: EMAIL
            Action: MASK
          - Name: SSN
            Action: BLOCK

  # Guardrail Version
  GuardrailVersion:
    Type: AWS::Bedrock::GuardrailVersion
    Properties:
      GuardrailId: !Ref SafetyGuardrail
      Description: Version 1 of safety guardrail

  # Bedrock Agent
  SafeAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-safe-agent"
      Description: Safe agent with guardrail protection
      FoundationModel: anthropic.claude-v3:5
      AgentResourceRoleArn: !GetAtt AgentResourceRole.Arn
      IdleSessionTTLInSeconds: 1800
      AutoPrepare: true

  # Agent Alias with Guardrail
  SafeAgentAlias:
    Type: AWS::Bedrock::AgentAlias
    Properties:
      AgentId: !Ref SafeAgent
      AgentAliasName: production
      Description: Production alias with guardrail
      RoutingConfiguration:
        - AgentVersion: DRAFT

  # Note: Guardrails are applied during runtime via the ApplyGuardrail API
  # The guardrail is not directly attached to the agent resource
  # but is used in the application code when invoking the agent

Outputs:
  AgentId:
    Description: ID of the agent
    Value: !Ref SafeAgent

  AgentAliasId:
    Description: ID of the agent alias
    Value: !Ref SafeAgentAlias

  GuardrailId:
    Description: ID of the guardrail
    Value: !Ref SafetyGuardrail

  GuardrailArn:
    Description: ARN of the guardrail
    Value: !GetAtt SafetyGuardrail.GuardrailArn
```

## Example 7: Prompt Management with Versions

Bedrock Prompt resource with multiple variants and versions.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: Bedrock Prompt with multiple variants

Parameters:
  Environment:
    Type: String
    Default: dev

Mappings:
  Config:
    dev:
      Temperature: 0.9
      MaxTokens: 2048
    staging:
      Temperature: 0.7
      MaxTokens: 4096
    production:
      Temperature: 0.5
      MaxTokens: 4096

Resources:
  # Customer Support Prompt
  CustomerSupportPrompt:
    Type: AWS::Bedrock::Prompt
    Properties:
      Name: !Sub "${AWS::StackName}-support-prompt"
      Description: Customer support prompt with multiple variants
      DefaultVariant: empathetic
      Variants:
        # Empathetic Variant
        - Name: empathetic
          Description: Empathetic and understanding tone
          Text: |
            You are a highly empathetic customer support agent. Your goal is to:

            1. Acknowledge the customer's feelings and concerns with genuine empathy
            2. Listen actively to understand their full situation
            3. Provide clear, actionable solutions
            4. Follow up to ensure satisfaction

            Customer message: {{customer_message}}
            Conversation history: {{conversation_history}}

            Respond with empathy, using phrases like "I understand how frustrating this must be" and "I appreciate your patience".
          InferenceConfiguration:
            Temperature: !FindInMap [Config, !Ref Environment, Temperature]
            MaxTokens: !FindInMap [Config, !Ref Environment, MaxTokens]

        # Professional Variant
        - Name: professional
          Description: Professional and efficient tone
          Text: |
            You are a professional customer support agent. Your goal is to:

            1. Address the customer's issue efficiently
            2. Provide accurate information
            3. Offer clear next steps
            4. Maintain a courteous tone

            Customer message: {{customer_message}}
            Conversation history: {{conversation_history}}

            Respond in a professional manner with clear, concise language.
          InferenceConfiguration:
            Temperature: 0.3
            MaxTokens: 2048
            TopP: 0.9

        # Technical Variant
        - name: technical
          Description: Technical support focused tone
          Text: |
            You are a technical support specialist. Your goal is to:

            1. Understand the technical issue in detail
            2. Provide step-by-step troubleshooting
            3. Include relevant technical information
            4. Suggest preventive measures

            Customer message: {{customer_message}}
            System information: {{system_info}}
            Error logs: {{error_logs}}

            Respond with detailed technical information and clear instructions.
          InferenceConfiguration:
            Temperature: 0.2
            MaxTokens: 4096

Outputs:
  PromptId:
    Description: ID of the prompt
    Value: !Ref CustomerSupportPrompt

  PromptArn:
    Description: ARN of the prompt
    Value: !GetAtt CustomerSupportPrompt.Arn
```

## Example 8: Complete RAG Implementation with Cross-Stack References

Multi-stack architecture with separate network, data, and application stacks.

```yaml
# Stack 1: Network and Infrastructure Stack
AWSTemplateFormatVersion: 2010-09-09
Description: Network infrastructure for Bedrock resources

Resources:
  # OpenSearch Serverless Collection
  VectorCollection:
    Type: AWS::OpenSearchServerless::Collection
    Properties:
      Name: !Sub "${AWS::StackName}-vector-collection"
      Type: SEARCH

  # Access Policy
  VectorAccessPolicy:
    Type: AWS::OpenSearchServerless::AccessPolicy
    Properties:
      Name: !Sub "${AWS::StackName}-vector-access"
      Policy: !Sub |
        [
          {
            "Rules": [
              {
                "Resource": ["collection/${VectorCollection.id}"],
                "Permission": ["aoss:*"]
              }
            ],
            "Principal": ["*"]
          }
        ]
      Type: data

Outputs:
  VectorCollectionArn:
    Description: ARN of the vector collection
    Value: !GetAtt VectorCollection.Arn
    Export:
      Name: !Sub "${AWS::StackName}-VectorCollectionArn"

  VectorCollectionEndpoint:
    Description: Endpoint of the vector collection
    Value: !GetAtt VectorCollection.Endpoint
    Export:
      Name: !Sub "${AWS::StackName}-VectorCollectionEndpoint"
```

```yaml
# Stack 2: Data Stack - Knowledge Base
AWSTemplateFormatVersion: 2010-09-09
Description: Knowledge base stack

Parameters:
  NetworkStackName:
    Type: String
    Default: bedrock-network

  Environment:
    Type: String
    Default: dev

Resources:
  # Knowledge Base Role
  KnowledgeBaseRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AWS::StackName}-kb-role"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${AWS::StackName}-kb-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - aoss:APIAccessAll
                Resource: !ImportValue
                  !Sub "${NetworkStackName}-VectorCollectionArn"
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Ref DocumentBucket
                  - !Sub "${DocumentBucket.Arn}/*"

  # Knowledge Base
  KnowledgeBase:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      KnowledgeBaseName: !Sub "${AWS::StackName}-kb-${Environment}"
      Description: Knowledge base for RAG
      EmbeddingModelArn: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:foundation-model/amazon.titan-embed-text-v1"
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          VectorStoreConfiguration:
            OpensearchServerlessConfiguration:
              CollectionArn: !ImportValue
                !Sub "${NetworkStackName}-VectorCollectionArn"
              VectorIndexName: kb-index
              FieldMapping:
                VectorField: vector
                TextField: text
                MetadataField: metadata
      RoleArn: !GetAtt KnowledgeBaseRole.Arn

  # Data Source
  DataSource:
    Type: AWS::Bedrock::DataSource
    Properties:
      KnowledgeBaseId: !Ref KnowledgeBase
      DataSourceName: !Sub "${AWS::StackName}-ds"
      DataSourceConfiguration:
        S3Configuration:
          BucketArn: !Ref DocumentBucket
      VectorIngestionConfiguration:
        ChunkingConfiguration:
          ChunkingStrategy: FIXED_SIZE
          FixedSizeChunking:
            MaxTokens: 512
            OverlapPercentage: 20

  # Document Bucket
  DocumentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-documents-${AWS::AccountId}-${AWS::Region}"

Outputs:
  KnowledgeBaseId:
    Description: ID of the knowledge base
    Value: !Ref KnowledgeBase
    Export:
      Name: !Sub "${AWS::StackName}-KnowledgeBaseId"

  KnowledgeBaseArn:
    Description: ARN of the knowledge base
    Value: !GetAtt KnowledgeBase.KnowledgeBaseArn
    Export:
      Name: !Sub "${AWS::StackName}-KnowledgeBaseArn"
```

```yaml
# Stack 3: Application Stack - Agent
AWSTemplateFormatVersion: 2010-09-09
Description: Application stack with Bedrock agent

Parameters:
  DataStackName:
    Type: String
    Default: bedrock-data

  Environment:
    Type: String
    Default: dev

Resources:
  # Agent Resource Role
  AgentResourceRole:
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
        - PolicyName: !Sub "${AWS::StackName}-agent-policy"
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: "*"
              - Effect: Allow
                Action:
                  - bedrock:Retrieve
                Resource: !Sub "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/*"

  # Bedrock Agent with Knowledge Base
  RAGAgent:
    Type: AWS::Bedrock::Agent
    Properties:
      AgentName: !Sub "${AWS::StackName}-agent-${Environment}"
      Description: RAG-enabled agent
      FoundationModel: anthropic.claude-v3:5
      AgentResourceRoleArn: !GetAtt AgentResourceRole.Arn
      AutoPrepare: true
      KnowledgeBases:
        - KnowledgeBaseId: !ImportValue
            !Sub "${DataStackName}-KnowledgeBaseId"
          Description: Knowledge base for RAG

  # Agent Alias
  AgentAlias:
    Type: AWS::Bedrock::AgentAlias
    Properties:
      AgentId: !Ref RAGAgent
      AgentAliasName: !Ref Environment
      Description: Alias for environment
      RoutingConfiguration:
        - AgentVersion: DRAFT

Outputs:
  AgentId:
    Description: ID of the agent
    Value: !Ref RAGAgent
    Export:
      Name: !Sub "${AWS::StackName}-AgentId"

  AgentAliasId:
    Description: ID of the agent alias
    Value: !Ref AgentAlias
    Export:
      Name: !Sub "${AWS::StackName}-AgentAliasId"

  AgentArn:
    Description: ARN of the agent
    Value: !GetAtt RAGAgent.AgentArn
    Export:
      Name: !Sub "${AWS::StackName}-AgentArn"
```
