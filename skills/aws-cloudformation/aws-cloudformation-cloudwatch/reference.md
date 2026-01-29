# AWS CloudFormation CloudWatch - Riferimento Dettagliato

## Indice

- [Risorse CloudWatch](#risorse-cloudwatch)
- [Proprieta Comuni](#proprieta-comuni)
- [Alarm Configuration](#alarm-configuration)
- [Dashboard Widgets](#dashboard-widgets)
- [Log Group Configuration](#log-group-configuration)
- [Metric Properties](#metric-properties)

---

## Risorse CloudWatch

### AWS::CloudWatch::Alarm

Risorsa principale per creare CloudWatch alarms.

#### Proprieta Principali

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| AlarmName | String | No | Nome univoco dell'alarm (max 255 chars) |
| AlarmDescription | String | No | Descrizione dell'alarm |
| MetricName | String | Si | Nome della metrica |
| Namespace | String | No | Namespace della metrica |
| Dimensions | List | No | Dimensioni per la metrica |
| Statistic | String | No | Statistica (SampleCount, Average, Sum, Minimum, Maximum) |
| ExtendedStatistic | String | No | Statistica percentile (es. p99) |
| Period | Number | No | Periodo in secondi (default: 300) |
| EvaluationPeriods | Number | Si | Numero di periodi di valutazione |
| Threshold | Number | Si | Soglia per l'alarm |
| ComparisonOperator | String | Si | Operatore di confronto |
| TreatMissingData | String | No | Come trattare dati mancanti |
| AlarmActions | List | No | ARN delle azioni da eseguire |
| InsufficientDataActions | List | No | Azioni per dati insufficienti |
| OKActions | List | No | Azioni quando l'alarm torna OK |

#### Valori di ComparisonOperator

```yaml
ComparisonOperator:
  - GreaterThanThreshold
  - GreaterThanOrEqualToThreshold
  - LessThanThreshold
  - LessThanOrEqualToThreshold
  - GreaterThanUpperBound
  - LessThanLowerBound
```

#### Valori di TreatMissingData

```yaml
TreatMissingData:
  # Treat as breaching (alarm goes to ALARM)
  - breaching
  # Treat as not breaching (alarm goes to OK)
  - notBreaching
  # Treat as missing (alarm goes to INSUFFICIENT_DATA)
  - missing
  # Maintain current state
  - ignore
```

#### Esempio Completo

```yaml
Resources:
  CompleteAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: production-error-alarm
      AlarmDescription: Alert on production errors exceeding threshold
      MetricName: Errors
      Namespace: MyApplication/Production
      Dimensions:
        - Name: Service
          Value: api-service
        - Name: Region
          Value: us-east-1
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      DatapointsToAlarm: 3
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Ref AlarmTopic
        - !Ref PagerDutyTopic
      InsufficientDataActions:
        - !Ref AlarmTopic
      OKActions:
        - !Ref RecoveryTopic
      Tags:
        - Key: Environment
          Value: production
        - Key: Severity
          Value: critical
```

---

### AWS::CloudWatch::CompositeAlarm

Combina multiple alarms in una singola espressione logica.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| AlarmName | String | Si | Nome dell'alarm composito |
| AlarmDescription | String | No | Descrizione |
| AlarmRule | String | Si | Regola che combina altri alarm |
| ActionsEnabled | Boolean | No | Se le azioni sono abilitate |
| AlarmActions | List | No | Azioni da eseguire |
| OKActions | List | No | Azioni quando OK |

#### Operatori per AlarmRule

```yaml
AlarmRule: !Or
  - !Ref Alarm1
  - !Ref Alarm2
  - !And
    - !Ref Alarm3
    - !Ref Alarm4
  - !Not
    - !Ref Alarm5
```

---

### AWS::CloudWatch::AnomalyDetector

Configura anomaly detection per metriche.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| MetricName | String | Si | Nome della metrica |
| Namespace | String | Si | Namespace della metrica |
| Dimensions | List | No | Dimensioni |
| Statistic | String | Si | Statistica |
| Configuration | Configuration | No | Configurazione anomaly detector |

#### Configuration

```yaml
Configuration:
  ExcludedTimeRanges:
    - StartTime: "2023-12-25T00:00:00"
      EndTime: "2023-12-26T00:00:00"
  MetricTimeZone: UTC
```

---

### AWS::CloudWatch::Dashboard

Crea dashboard CloudWatch per visualizzazione metriche.

#### DashboardBody Structure

```yaml
DashboardBody:
  "start": "-PT6H"
  "end": "P0D"
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Widget Title",
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "metrics": [
          ["Namespace", "MetricName", "Dimension1", "Value1"],
          [".", ".", ".", "."]
        ],
        "period": 300,
        "stat": "Sum",
        "annotations": {
          "horizontal": [
            {
              "value": 100,
              "label": "Threshold",
              "color": "#ff7f0e"
            }
          ]
        }
      }
    }
  ]
```

#### Tipi di View

```yaml
view:
  - timeSeries    # Line chart
  - bar           # Bar chart
  - pie           # Pie chart
  - singleValue   # Single value display
  - table         # Tabular view
```

---

### AWS::Logs::LogGroup

Crea gruppi di log CloudWatch.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| LogGroupName | String | Si | Nome del log group |
| RetentionInDays | Number | No | Giorni di retention (1-3650) |
| KmsKeyId | String | No | ARN della KMS key per encryption |
| Tags | List | No | Tags per il log group |

#### Retention Values

```yaml
RetentionInDays:
  - 1        # 1 day
  - 3        # 3 days
  - 5        # 5 days
  - 7        # 1 week
  - 14       # 2 weeks
  - 30       # 1 month
  - 60       # 2 months
  - 90       # 3 months
  - 120      # 4 months
  - 150      # 5 months
  - 180      # 6 months
  - 365      # 1 year
  - 400      # 13 months
  - 545      # 18 months
  - 731      # 2 years
  - 1095     # 3 years
  - 1827     # 5 years
  - 2190     # 6 years
  - 2555     # 7 years
  - 2922     # 8 years
  - 3285     # 9 years
  - 3650     # 10 years
```

---

### AWS::Logs::MetricFilter

Estrae metriche da pattern di log.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| FilterPattern | String | Si | Pattern per filtrare log |
| LogGroupName | String | Si | Nome del log group |
| MetricTransformations | List | Si | Trasformazioni in metriche |

#### MetricTransformation

```yaml
MetricTransformations:
  - MetricValue: "1"
    MetricNamespace: MyApp/Logs
    MetricName: ErrorCount
    DefaultValue: 0.0
```

---

### AWS::Logs::SubscriptionFilter

Invia log a destinazioni esterne (Kinesis, Lambda, ES).

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| DestinationArn | String | Si | ARN della destinazione |
| FilterPattern | String | Si | Pattern per filtrare log |
| LogGroupName | String | Si | Nome del log group |
| RoleArn | String | Si | ARN del role per accesso |

---

### AWS::Logs::QueryDefinition

Salva query Log Insights.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome della query |
| QueryString | String | Si | Query Log Insights |

---

### AWS::Synthetics::Canary

Crea synthesized canaries per synthetic monitoring.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome del canary |
| ArtifactS3Location | String | Si | S3 location per artifacts |
| Code | Code | Si | Configurazione codice |
| ExecutionRoleArn | String | Si | ARN del role |
| RuntimeVersion | String | Si | Runtime version |
| Schedule | Schedule | Si | Schedule di esecuzione |
| SuccessRetentionPeriodInDays | Number | No | Retention per successi |
| FailureRetentionPeriodInDays | Number | No | Retention per fallimenti |

#### Runtime Versions

```yaml
RuntimeVersion:
  - syn-python-selenium-1.1
  - syn-python-selenium-1.0
  - syn-nodejs-puppeteer-6.0
  - syn-nodejs-puppeteer-5.0
  - syn-nodejs-puppeteer-4.0
```

#### Schedule Expression

```yaml
Schedule:
  Expression: "rate(5 minutes)"
  DurationInSeconds: 120
```

---

### AWS::CloudWatch::ServiceLevelIndicator

Definisce SLI per service health.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome dello SLI |
| Monitor | Monitor | Si | Monitor di riferimento |
| Metric | Metric | Si | Configurazione metrica |
| OperationName | String | No | Nome operazione |

---

### AWS::CloudWatch::ServiceLevelObjective

Definisce SLO basati su SLI.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome dello SLO |
| Description | String | No | Descrizione |
| Monitor | Monitor | Si | Monitor di riferimento |
| SliMetric | SliMetric | Si | Metrica SLI |
| Target | Target | Si | Target obiettivo |
| Goal | Goal | No | Goal configurazione |

---

### AWS::CloudWatch::ApplicationMonitor

Configura Application Signals per APM.

#### Proprieta

| Proprieta | Tipo | Richiesto | Descrizione |
|-----------|------|-----------|-------------|
| MonitorName | String | Si | Nome del monitor |
| MonitorType | String | Si | Tipo (CW_MONITOR) |
| Telemetry | List | No | Configurazione telemetry |

---

## Proprieta Comuni

### Dimensions

```yaml
Dimensions:
  - Name: DimensionName1
    Value: DimensionValue1
  - Name: DimensionName2
    Value: DimensionValue2
```

### Tags

```yaml
Tags:
  - Key: Environment
    Value: production
  - Key: Service
    Value: api
  - Key: CostCenter
    Value: engineering
```

---

## Alarm Configuration

### Statistic Types

```yaml
Statistic:
  - SampleCount    # Numero di datapoints
  - Average        # Media
  - Sum            # Somma
  - Minimum        # Minimo
  - Maximum        # Massimo
```

### Extended Statistics

```yaml
ExtendedStatistic: "p99"        # 99th percentile
ExtendedStatistic: "p95"        # 95th percentile
ExtendedStatistic: "p50"        # Median
ExtendedStatistic: "tc99"       # Trimmed mean 99%
ExtendedStatistic: "wm99"       # Winsorized mean 99%
```

### Metric Selectors

```yaml
# Single metric
MetricName: Errors
Namespace: AWS/Lambda

# Multiple metrics with dimensions
metrics:
  - ["AWS/Lambda", "Invocations", "FunctionName", "MyFunction"]
  - [".", "Errors", ".", "."]
  - [".", "Duration", ".", ".", {"stat": "p99"}]

# Math expression
metrics:
  - ["AWS/Lambda", "Errors", "FunctionName", "MyFunction"]
  - [".", "Invocations", ".", "."]
  - expression: Errors / Invocations * 100
    label: Error Rate (%)
    id: errorRate
```

---

## Dashboard Widgets

### Metric Widget

```yaml
{
  "type": "metric",
  "x": 0,
  "y": 0,
  "width": 12,
  "height": 6,
  "properties": {
    "title": "API Gateway Metrics",
    "view": "timeSeries",
    "stacked": false,
    "region": "us-east-1",
    "metrics": [
      ["AWS/ApiGateway", "Count", "ApiName", "MyApi", "Stage", "prod"]
    ],
    "period": 300,
    "stat": "Sum",
    "legend": {
      "position": "bottom"
    },
    "liveData": true,
    "annotations": {
      "horizontal": [
        {
          "value": 1000,
          "label": "Warning Threshold",
          "color": "#ff7f0e"
        }
      ],
      "vertical": [
        {
          "value": "2023-12-31T00:00:00Z",
          "label": "Deployment",
          "color": "#2ca02c"
        }
      ]
    }
  }
}
```

### Text Widget

```yaml
{
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 12,
  "height": 3,
  "properties": {
    "markdown": "# Production Dashboard\nLast updated: `date`"
  }
}
```

### Log Widget

```yaml
{
  "type": "log",
  "x": 0,
  "y": 12,
  "width": 24,
  "height": 6,
  "properties": {
    "title": "Application Errors",
    "view": "table",
    "region": "us-east-1",
    "logGroupName": "/aws/applications/prod/app",
    "timeRange": {
      "type": "relative",
      "from": 3600
    },
    "filterPattern": "ERROR | WARN",
    "columns": ["@timestamp", "@message", "@logStream"]
  }
}
```

### Alarm Status Widget

```yaml
{
  "type": "alarm",
  "x": 0,
  "y": 0,
  "width": 6,
  "height": 6,
  "properties": {
    "title": "Alarm Status",
    "alarms": [
      "arn:aws:cloudwatch:us-east-1:123456789:alarm:ErrorAlarm",
      "arn:aws:cloudwatch:us-east-1:123456789:alarm:LatencyAlarm"
    ]
  }
}
```

---

## Log Group Configuration

### Retention Policy Examples

```yaml
# Development - short retention
DevLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/applications/dev/app
    RetentionInDays: 7

# Production - long retention
ProdLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/applications/prod/app
    RetentionInDays: 90
    KmsKeyId: !Ref ProdLogKmsKey
```

### Encryption Configuration

```yaml
Resources:
  EncryptedLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/applications/prod/encrypted
      RetentionInDays: 30
      KmsKeyId: !Ref LogEncryptionKey

  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Key for log encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: logs.us-east-1.amazonaws.com
            Action:
              - kms:Encrypt*
              - kms:Decrypt*
              - kms:ReEncrypt*
              - kms:GenerateDataKey*
              - kms:Describe*
            Resource: "*"
            Condition:
              ArnEquals:
                aws:SourceArn: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:log-group:*"
```

---

## Metric Properties

### Common Namespace Patterns

```yaml
Namespace:
  # AWS services
  - AWS/Lambda
  - AWS/ApiGateway
  - AWS/EC2
  - AWS/RDS
  - AWS/ECS
  - AWS/EKS
  - AWS/DynamoDB
  - AWS/S3
  - AWS/SNS
  - AWS/SQS
  - AWS/ElastiCache
  - AWS/ElasticLoadBalancing

  # Custom namespaces
  - MyApplication/Production
  - MyService/Metrics
  - CustomMetrics/Business
```

### Common Metric Names

```yaml
MetricName:
  # Lambda
  - Invocations
  - Errors
  - Throttles
  - Duration
  - ConcurrentExecutions
  - UnreservedConcurrentExecutions

  # API Gateway
  - Count
  - Latency
  - 4XXError
  - 5XXError
  - IntegrationLatency
  - CacheHitCount
  - CacheMissCount

  # EC2
  - CPUUtilization
  - NetworkIn
  - NetworkOut
  - DiskReadOps
  - DiskWriteOps
  - StatusCheckFailed

  # RDS
  - DatabaseConnections
  - ReadLatency
  - WriteLatency
  - ReadIOPS
  - WriteIOPS
  - FreeStorageSpace
  - CPUUtilization

  # Custom
  - RequestCount
  - ErrorCount
  - SuccessCount
  - Latency
  - ResponseSize
  - QueueSize
  - ProcessingTime
```

---

## Nested Stack References

### Cross-Stack Import

```yaml
# Import da network stack
Parameters:
  NetworkStackName:
    Type: String
    Description: Network stack name

Resources:
  # Import VPC ID
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue
        !Sub "${NetworkStackName}-VPCId"
      GroupDescription: Security group for monitoring

# Import log group name
LogGroupName:
  Fn::ImportValue:
    !Sub "${MonitoringStackName}-LogGroupName"
```

---

## Condition Functions

### Intrinsic Functions

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  IsStaging: !Equals [!Ref Environment, staging]
  EnableAnomaly: !Not [!Equals [!Ref Environment, dev]]
  CreateAlarms: !Or [!Equals [!Ref Environment, staging], !Equals [!Ref Environment, production]]

Resources:
  ProdAlarm:
    Condition: IsProduction
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: prod-errors
      MetricName: Errors
      Namespace: MyApp
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
```

---

## Best Practices Summary

### Alarm Configuration

| Scenario | Period | EvaluationPeriods | DatapointsToAlarm |
|----------|--------|-------------------|-------------------|
| High traffic metrics | 60s | 5 | 3 |
| Latency (P99) | 60s | 3 | 2 |
| Error rate | 60s | 5 | 3 |
| Resource utilization | 300s | 3 | 2 |
| Cost metrics | 3600s | 2 | 1 |

### Log Retention

| Log Type | Retention | Encryption |
|----------|-----------|------------|
| Application logs | 30 days | Required |
| Audit logs | 365 days | Required |
| Lambda logs | 30 days | Optional |
| VPC flow logs | 90 days | Recommended |
| Security logs | 365+ days | Required |

### Dashboard Design

- Use 6-hour default time range for operational dashboards
- Group related metrics in widgets
- Add threshold annotations for critical values
- Use alarm status widgets for quick health check
- Limit widgets per dashboard for performance
