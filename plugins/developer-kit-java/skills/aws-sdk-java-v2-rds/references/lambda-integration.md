# AWS Lambda Integration with RDS

## Lambda RDS Connection Patterns

### 1. Traditional Lambda + RDS Connection

```java
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class RdsLambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent event, Context context) {
        APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();

        try {
            // Get environment variables
            String host = System.getenv("ProxyHostName");
            String port = System.getenv("Port");
            String dbName = System.getenv("DBName");
            String username = System.getenv("DBUserName");
            String password = System.getenv("DBPassword");

            // Create connection string
            String connectionString = String.format(
                "jdbc:mysql://%s:%s/%s?useSSL=true&requireSSL=true",
                host, port, dbName
            );

            // Execute query
            String sql = "SELECT COUNT(*) FROM users";

            try (Connection connection = DriverManager.getConnection(connectionString, username, password);
                 PreparedStatement statement = connection.prepareStatement(sql);
                 ResultSet resultSet = statement.executeQuery()) {

                if (resultSet.next()) {
                    int count = resultSet.getInt(1);
                    response.setStatusCode(200);
                    response.setBody("{\"count\": " + count + "}");
                }
            }
        } catch (Exception e) {
            response.setStatusCode(500);
            response.setBody("{\"error\": \"" + e.getMessage() + "\"}");
        }

        return response;
    }
}
```

### 2. Lambda with Connection Pooling

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import javax.sql.DataSource;

public class RdsLambdaConfig {

    private static DataSource dataSource;

    public static synchronized DataSource getDataSource() {
        if (dataSource == null) {
            HikariConfig config = new HikariConfig();

            String host = System.getenv("ProxyHostName");
            String port = System.getenv("Port");
            String dbName = System.getenv("DBName");
            String username = System.getenv("DBUserName");
            String password = System.getenv("DBPassword");

            config.setJdbcUrl(String.format("jdbc:mysql://%s:%s/%s", host, port, dbName));
            config.setUsername(username);
            config.setPassword(password);

            // Connection pool settings
            config.setMaximumPoolSize(5);
            config.setMinimumIdle(2);
            config.setIdleTimeout(30000);
            config.setConnectionTimeout(20000);
            config.setMaxLifetime(1800000);

            // MySQL-specific settings
            config.addDataSourceProperty("useSSL", true);
            config.addDataSourceProperty("requireSSL", true);
            config.addDataSourceProperty("serverSslCertificate", "rds-ca-2019");
            config.addDataSourceProperty("connectTimeout", "30");

            dataSource = new HikariDataSource(config);
        }
        return dataSource;
    }
}
```

### 3. Using AWS Secrets Manager for Credentials

```java
import com.amazonaws.services.secretsmanager.AWSSecretsManager;
import com.amazonaws.services.secretsmanager.AWSSecretsManagerClientBuilder;
import com.amazonaws.services.secretsmanager.model.GetSecretValueRequest;
import com.amazonaws.services.secretsmanager.model.GetSecretValueResult;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

public class RdsSecretsHelper {

    private static final String SECRET_NAME = "prod/rds/db_credentials";
    private static final String REGION = "us-east-1";

    public static Map<String, String> getRdsCredentials() {
        AWSSecretsManager client = AWSSecretsManagerClientBuilder.standard()
            .withRegion(REGION)
            .build();

        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(SECRET_NAME)
            .build();

        GetSecretValueResult result = client.getSecretValue(request);

        // Parse secret JSON
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, Object> secretMap = objectMapper.readValue(result.getSecretString(), HashMap.class);

        Map<String, String> credentials = new HashMap<>();
        secretMap.forEach((key, value) -> {
            credentials.put(key, value.toString());
        });

        return credentials;
    }
}
```

### 4. Lambda with AWS SDK for RDS

```java
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsClient;
import software.amazon.awssdk.services.rds.model.*;

public class RdsManagementLambda implements RequestHandler<ApiRequest, ApiResponse> {

    @Override
    public ApiResponse handleRequest(ApiRequest request, Context context) {
        RdsClient rdsClient = RdsClient.builder()
            .region(Region.US_EAST_1)
            .build();

        try {
            switch (request.getAction()) {
                case "list-instances":
                    return listInstances(rdsClient);
                case "create-snapshot":
                    return createSnapshot(rdsClient, request.getInstanceId(), request.getSnapshotId());
                case "describe-instance":
                    return describeInstance(rdsClient, request.getInstanceId());
                default:
                    return new ApiResponse(400, "Unknown action: " + request.getAction());
            }
        } catch (Exception e) {
            context.getLogger().log("Error: " + e.getMessage());
            return new ApiResponse(500, "Error: " + e.getMessage());
        } finally {
            rdsClient.close();
        }
    }

    private ApiResponse listInstances(RdsClient rdsClient) {
        DescribeDbInstancesResponse response = rdsClient.describeDBInstances();
        return new ApiResponse(200, response.toString());
    }

    private ApiResponse createSnapshot(RdsClient rdsClient, String instanceId, String snapshotId) {
        CreateDbSnapshotRequest request = CreateDbSnapshotRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .dbSnapshotIdentifier(snapshotId)
            .build();

        CreateDbSnapshotResponse response = rdsClient.createDBSnapshot(request);
        return new ApiResponse(200, "Snapshot created: " + response.dbSnapshot().dbSnapshotIdentifier());
    }

    private ApiResponse describeInstance(RdsClient rdsClient, String instanceId) {
        DescribeDbInstancesRequest request = DescribeDbInstancesRequest.builder()
            .dbInstanceIdentifier(instanceId)
            .build();

        DescribeDbInstancesResponse response = rdsClient.describeDBInstances(request);
        return new ApiResponse(200, response.toString());
    }
}

class ApiRequest {
    private String action;
    private String instanceId;
    private String snapshotId;
    // getters and setters
}

class ApiResponse {
    private int statusCode;
    private String body;
    // constructor, getters
}
```

## Best Practices for Lambda + RDS

### 1. Security Configuration

**IAM Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Security Group:**
- Use security groups to restrict access
- Only allow Lambda function IP ranges
- Use VPC endpoints for private connections

### 2. Environment Variables

```bash
# Environment variables for Lambda
DB_HOST=mydb.abc123.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=mydatabase
DB_USERNAME=admin
DB_PASSWORD=${DB_PASSWORD}
DB_CONNECTION_STRING=jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
```

### 3. Error Handling

```java
import com.amazonaws.services.lambda.runtime.LambdaLogger;

public class LambdaErrorHandler {

    public static void handleRdsError(Exception e, LambdaLogger logger) {
        if (e instanceof RdsException) {
            RdsException rdsException = (RdsException) e;
            logger.log("RDS Error: " + rdsException.awsErrorDetails().errorCode());

            switch (rdsException.awsErrorDetails().errorCode()) {
                case "DBInstanceNotFoundFault":
                    logger.log("Database instance not found");
                    break;
                case "InvalidParameterValueException":
                    logger.log("Invalid parameter provided");
                    break;
                case "InstanceAlreadyExistsFault":
                    logger.log("Instance already exists");
                    break;
                default:
                    logger.log("Unknown RDS error: " + rdsException.getMessage());
            }
        } else {
            logger.log("Non-RDS error: " + e.getMessage());
        }
    }
}
```

### 4. Performance Optimization

**Cold Start Mitigation:**
```java
import javax.sql.DataSource;
import java.sql.Connection;

public class RdsConnectionHelper {
    private static DataSource dataSource;
    private static long lastConnectionTime = 0;
    private static final long CONNECTION_TIMEOUT = 300000; // 5 minutes

    public static Connection getConnection() throws SQLException {
        long currentTime = System.currentTimeMillis();

        if (dataSource == null || (currentTime - lastConnectionTime) > CONNECTION_TIMEOUT) {
            dataSource = createDataSource();
            lastConnectionTime = currentTime;
        }

        return dataSource.getConnection();
    }

    private static DataSource createDataSource() {
        // Connection pool creation
    }
}
```

**Batch Processing:**
```java
public class RdsBatchProcessor {

    public void processBatch(List<String> userIds) {
        String sql = "SELECT * FROM users WHERE user_id IN (?)";

        try (Connection connection = getConnection();
             PreparedStatement statement = connection.prepareStatement(sql)) {

            // Convert list to SQL IN clause
            String placeholders = userIds.stream()
                .map(id -> "?")
                .collect(Collectors.joining(","));

            String finalSql = sql.replace("?", placeholders);

            // Set parameters
            for (int i = 0; i < userIds.size(); i++) {
                statement.setString(i + 1, userIds.get(i));
            }

            ResultSet resultSet = statement.executeQuery();
            // Process results

        } catch (SQLException e) {
            LambdaErrorHandler.handleRdsError(e, logger);
        }
    }
}
```

### 5. Monitoring and Logging

```java
import com.amazonaws.services.cloudwatch.AmazonCloudWatch;
import com.amazonaws.services.cloudwatch.AmazonCloudWatchClientBuilder;
import com.amazonaws.services.cloudwatch.model.MetricDatum;
import com.amazonaws.services.cloudwatch.model.PutMetricDataRequest;

public class RdsMetricsPublisher {

    private static final String NAMESPACE = "RDS/Lambda";
    private AmazonCloudWatch cloudWatch;

    public RdsMetricsPublisher() {
        this.cloudWatch = AmazonCloudWatchClientBuilder.defaultClient();
    }

    public void publishMetric(String metricName, double value) {
        MetricDatum datum = new MetricDatum()
            .withMetricName(metricName)
            .withUnit("Count")
            .withValue(value)
            .withTimestamp(new Date());

        PutMetricDataRequest request = new PutMetricDataRequest()
            .withNamespace(NAMESPACE)
            .withMetricData(Collections.singletonList(datum));

        cloudWatch.putMetricData(request);
    }
}
```