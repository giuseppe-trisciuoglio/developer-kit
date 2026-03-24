# CloudWatch Dashboards

## Dashboard Base Template

### Main Dashboard with Multiple Widgets

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: CloudWatch dashboard

Resources:
  # Main dashboard
  MainDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${AWS::StackName}-main"
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "API Gateway Requests",
                "view": "timeSeries",
                "stacked": false,
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/ApiGateway", "Count", "ApiName", "${ApiName}", "Stage", "${StageName}"],
                  [".", "4XXError", ".", ".", ".", "."],
                  [".", "5XXError", ".", ".", ".", "."]
                ],
                "period": 300,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "API Gateway Latency",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/ApiGateway", "Latency", "ApiName", "${ApiName}", "Stage", "${StageName}", {"stat": "p99"}],
                  [".", ".", ".", ".", ".", ".", {"stat": "Average"}]
                ],
                "period": 300
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 6,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Lambda Invocations",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${LambdaFunction}"],
                  [".", "Errors", ".", "."],
                  [".", "Throttles", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 6,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "Lambda Duration",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/Lambda", "Duration", "FunctionName", "${LambdaFunction}", {"stat": "p99"}],
                  [".", ".", ".", ".", {"stat": "Average"}],
                  [".", ".", ".", ".", {"stat": "Maximum"}]
                ],
                "period": 60
              }
            },
            {
              "type": "log",
              "x": 0,
              "y": 12,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Application Logs",
                "view": "table",
                "region": "${AWS::Region}",
                "logGroupName": "${ApplicationLogGroup}",
                "timeRange": {
                  "type": "relative",
                  "from": 3600
                },
                "filterPattern": "ERROR | WARN"
              }
            }
          ]
        }
```

## Service-Specific Dashboard

### Application Service Dashboard

```yaml
Resources:
  # Dashboard for specific service
  ServiceDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub "${AWS::StackName}-${ServiceName}"
      DashboardBody: !Sub |
        {
          "start": "-PT6H",
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 1,
              "properties": {
                "markdown": "# ${ServiceName} - ${Environment} Dashboard"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 1,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "Request Rate",
                "view": "timeSeries",
                "stacked": false,
                "region": "${AWS::Region}",
                "metrics": [
                  ["${CustomNamespace}", "RequestCount", "Service", "${ServiceName}", "Environment", "${Environment}"]
                ],
                "period": 60,
                "stat": "Sum"
              }
            },
            {
              "type": "metric",
              "x": 8,
              "y": 1,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "Error Rate %",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["${CustomNamespace}", "ErrorCount", "Service", "${ServiceName}"],
                  [".", "RequestCount", ".", "."],
                  [".", "SuccessCount", ".", "."]
                ],
                "period": 60,
                "stat": "Average"
              }
            },
            {
              "type": "metric",
              "x": 16,
              "y": 1,
              "width": 8,
              "height": 6,
              "properties": {
                "title": "P99 Latency",
                "view": "timeSeries",
                "region": "${AWS::Region}",
                "metrics": [
                  ["${CustomNamespace}", "Latency", "Service", "${ServiceName}"]
                ],
                "period": 60,
                "stat": "p99"
              }
            }
          ]
        }
```

## Widget Types

### Metric Widget

```yaml
Resources:
  MetricWidgetDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "CPU Utilization",
                "view": "timeSeries",
                "stacked": false,
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", "InstanceId", "${InstanceId}"]
                ],
                "period": 300,
                "stat": "Average",
                "yAxis": {
                  "left": {
                    "min": 0,
                    "max": 100
                  }
                }
              }
            }
          ]
        }
```

### Log Widget

```yaml
Resources:
  LogWidgetDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "log",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Application Logs",
                "view": "table",
                "region": "${AWS::Region}",
                "logGroupName": "${ApplicationLogGroup}",
                "timeRange": {
                  "type": "relative",
                  "from": 3600
                },
                "filterPattern": "ERROR | WARN",
                "columns": [
                  ["@timestamp"],
                  ["level"],
                  ["message"]
                ],
                "scrollTop": true
              }
            }
          ]
        }
```

### Text Widget

```yaml
Resources:
  TextWidgetDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 2,
              "properties": {
                "markdown": "# Production Dashboard\n\n**Environment:** ${Environment}\n**Region:** ${AWS::Region}\n**Last Updated:** " + new Date().toISOString()
              }
            }
          ]
        }
```

### Single Value Widget

```yaml
Resources:
  SingleValueDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 6,
              "height": 3,
              "properties": {
                "title": "Current Requests",
                "view": "singleValue",
                "metrics": [
                  ["AWS/ApiGateway", "Count", "ApiName", "${ApiName}"]
                ],
                "period": 60,
                "stat": "Sum",
                "region": "${AWS::Region}"
              }
            }
          ]
        }
```

### Alarm Status Widget

```yaml
Resources:
  AlarmStatusDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "alarm",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 3,
              "properties": {
                "title": "Alarm Status",
                "alarms": [
                  {
                    "alarmName": "${AlarmName1}",
                    "region": "${AWS::Region}"
                  },
                  {
                    "alarmName": "${AlarmName2}",
                    "region": "${AWS::Region}"
                  }
                ]
              }
            }
          ]
        }
```

## Advanced Dashboard Features

### Multi-Region Dashboard

```yaml
Resources:
  MultiRegionDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: multi-region-dashboard
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "US-East-1 Metrics",
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", {"region": "us-east-1"}]
                ]
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "US-West-2 Metrics",
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", {"region": "us-west-2"}]
                ]
              }
            }
          ]
        }
```

### Stacked Metrics

```yaml
Resources:
  StackedMetricsDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Stacked Request Types",
                "view": "timeSeries",
                "stacked": true,
                "metrics": [
                  ["AWS/ApiGateway", "Count", "ApiName", "${ApiName}"],
                  [".", "4XXError", ".", "."],
                  [".", "5XXError", ".", "."]
                ],
                "region": "${AWS::Region}",
                "period": 300,
                "stat": "Sum"
              }
            }
          ]
        }
```

### Anomaly Detection Widget

```yaml
Resources:
  AnomalyDetectionDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Request Count with Anomaly Detection",
                "metrics": [
                  ["${CustomNamespace}", "RequestCount", {"id": "m1", "visible": false}],
                  [{"expression": "ANOMALY_DETECTION_BAND(m1, 2)", "label": "RequestCount (expected)", "id": "e1", "region": "${AWS::Region}"}]
                ],
                "region": "${AWS::Region}",
                "period": 300,
                "stat": "Sum"
              }
            }
          ]
        }
```

### Math Expression Widget

```yaml
Resources:
  MathExpressionDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 6,
              "properties": {
                "title": "Error Rate Calculation",
                "metrics": [
                  ["${CustomNamespace}", "Errors", {"id": "m1", "visible": false}],
                  ["${CustomNamespace}", "Requests", {"id": "m2", "visible": false}],
                  [{"expression": "100 * (m1 / m2)", "label": "Error Rate %", "id": "e1"}]
                ],
                "region": "${AWS::Region}",
                "period": 300
              }
            }
          ]
        }
```

## Dashboard Layout Patterns

### Grid Layout

```yaml
Resources:
  GridLayoutDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0, "y": 0,
              "width": 6, "height": 3,
              "properties": {"title": "Widget 1"}
            },
            {
              "type": "metric",
              "x": 6, "y": 0,
              "width": 6, "height": 3,
              "properties": {"title": "Widget 2"}
            },
            {
              "type": "metric",
              "x": 12, "y": 0,
              "width": 6, "height": 3,
              "properties": {"title": "Widget 3"}
            },
            {
              "type": "metric",
              "x": 18, "y": 0,
              "width": 6, "height": 3,
              "properties": {"title": "Widget 4"}
            }
          ]
        }
```

### Row Layout

```yaml
Resources:
  RowLayoutDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: |
        {
          "widgets": [
            # Row 1: Overview
            {
              "type": "metric",
              "x": 0, "y": 0,
              "width": 12, "height": 6,
              "properties": {"title": "CPU"}
            },
            {
              "type": "metric",
              "x": 12, "y": 0,
              "width": 12, "height": 6,
              "properties": {"title": "Memory"}
            },
            # Row 2: Network
            {
              "type": "metric",
              "x": 0, "y": 6,
              "width": 12, "height": 6,
              "properties": {"title": "Network In"}
            },
            {
              "type": "metric",
              "x": 12, "y": 6,
              "width": 12, "height": 6,
              "properties": {"title": "Network Out"}
            }
          ]
        }
```

### Column Layout

```yaml
Resources:
  ColumnLayoutDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: |
        {
          "widgets": [
            # Column 1: Application Metrics
            {
              "type": "metric",
              "x": 0, "y": 0,
              "width": 8, "height": 6,
              "properties": {"title": "Requests"}
            },
            {
              "type": "metric",
              "x": 0, "y": 6,
              "width": 8, "height": 6,
              "properties": {"title": "Errors"}
            },
            # Column 2: Infrastructure
            {
              "type": "metric",
              "x": 8, "y": 0,
              "width": 8, "height": 6,
              "properties": {"title": "CPU"}
            },
            {
              "type": "metric",
              "x": 8, "y": 6,
              "width": 8, "height": 6,
              "properties": {"title": "Memory"}
            },
            # Column 3: Logs
            {
              "type": "log",
              "x": 16, "y": 0,
              "width": 8, "height": 12,
              "properties": {"title": "Logs"}
            }
          ]
        }
```

## Dashboard Variables

### Dynamic Variables

```yaml
Resources:
  DynamicDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "variables": [
            {
              "id": "service",
              "name": "Service",
              "selectedValue": "All",
              "values": ["Service1", "Service2", "Service3"]
            },
            {
              "id": "environment",
              "name": "Environment",
              "selectedValue": "production",
              "values": ["dev", "staging", "production"]
            }
          ],
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  ["AWS/Lambda", "Invocations", {"label": "{{$service}}"}, {"label": "{{$environment}}"}]
                ]
              }
            }
          ]
        }
```

## Dashboard Permissions

### Cross-Account Dashboard Sharing

```yaml
Resources:
  # Dashboard in source account
  SharedDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: shared-dashboard
      DashboardBody: !Ref DashboardBody

  # Resource policy for sharing
  DashboardSharePolicy:
    Type: AWS::CloudWatch::DashboardResourcePolicy
    Properties:
      DashboardName: !Ref SharedDashboard
      PolicyDocument: !Sub |
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "AWS": "arn:aws:iam::${TargetAccountId}:root"
              },
              "Action": [
                "cloudwatch:GetDashboard",
                "cloudwatch:ListDashboards",
                "cloudwatch:DeleteDashboards",
                "cloudwatch:PutDashboard"
              ],
              "Resource": !Sub "arn:aws:cloudwatch::${AWS::AccountId}:dashboard/${SharedDashboard}"
            }
          ]
        }
```

## Dashboard Automation

### Automated Dashboard Updates

```yaml
Resources:
  DashboardUpdater:
    Type: Custom::DashboardUpdater
    Properties:
      ServiceToken: !GetAtt UpdateFunction.Arn
      DashboardName: !Ref MainDashboard
      UpdateSchedule: "rate(1 day)"

  UpdateFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Code:
        ZipFile: |
          const AWS = require('aws-sdk');
          const cloudwatch = new AWS.CloudWatch();

          exports.handler = async (event) => {
            // Update dashboard with latest metrics
            await cloudwatch.putDashboard({
              DashboardName: event.DashboardName,
              DashboardBody: JSON.stringify({
                widgets: generateWidgets()
              })
            }).promise();
          };
```

### Dashboard Export

```yaml
Resources:
  DashboardExporter:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Environment:
        Variables:
          DASHBOARD_NAME: !Ref MainDashboard
          S3_BUCKET: !Ref ExportBucket
      Code:
        ZipFile: |
          const AWS = require('aws-sdk');
          const cloudwatch = new AWS.CloudWatch();
          const s3 = new AWS.S3();

          exports.handler = async () => {
            const dashboard = await cloudwatch.getDashboard({
              DashboardName: process.env.DASHBOARD_NAME
            }).promise();

            await s3.putObject({
              Bucket: process.env.S3_BUCKET,
              Key: `dashboards/${process.env.DASHBOARD_NAME}.json`,
              Body: dashboard.DashboardBody
            }).promise();
          };
```

## Dashboard Best Practices

### Organize by Service Tier

```yaml
Resources:
  ApplicationDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            # Application Layer
            {"type": "metric", "y": 0, "properties": {"title": "Application Requests"}},
            {"type": "metric", "y": 6, "properties": {"title": "Application Errors"}},
            # Database Layer
            {"type": "metric", "y": 12, "properties": {"title": "Database Connections"}},
            {"type": "metric", "y": 18, "properties": {"title": "Database Query Performance"}},
            # Infrastructure Layer
            {"type": "metric", "y": 24, "properties": {"title": "CPU Utilization"}},
            {"type": "metric", "y": 30, "properties": {"title": "Memory Utilization"}}
          ]
        }
```

### Use Consistent Time Ranges

```yaml
Resources:
  TimeRangeDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "start": "-PT6H",
          "end": "now",
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "period": 300,
                "stat": "Average"
              }
            }
          ]
        }
```

### Add Context with Text Widgets

```yaml
Resources:
  ContextDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "text",
              "properties": {
                "markdown": "# Application Monitoring\n\n## Environment: ${Environment}\n## Support Team: team@example.com"
              }
            }
          ]
        }
```
