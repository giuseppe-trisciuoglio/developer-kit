# Deployment Platforms

Platform-specific guides for deploying Next.js applications.

## Vercel (Platform Native)

### Configuration

```json
// vercel.json
{
  "version": 2,
  "buildCommand": "next build",
  "devCommand": "next dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_TELEMETRY_DISABLED": "1"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    }
  ],
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    }
  ]
}
```

### Environment Variables

```bash
# Set via Vercel Dashboard or CLI
vercel env add DATABASE_URL production
vercel env add NEXT_PUBLIC_API_URL production
```

### Preview Deployments

Automatic for all pull requests. Configure in project settings:
- Environment Variables > Preview > Add variables for preview environments

## AWS

### Elastic Container Service (ECS)

```yaml
# ecs-task-definition.json
{
  "family": "nextjs-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "myapp:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "PORT", "value": "3000" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextjs-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Application Load Balancer

```yaml
# alb.yml
Resources:
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: nextjs-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: nextjs-tg
      Port: 3000
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: ip
      HealthCheckPath: /api/health
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3

  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref LoadBalancer
      Port: 443
      Protocol: HTTPS
      Certificates:
        - CertificateArn: !Ref SSLCertificate
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
```

### S3 Static Export

```yaml
# s3-cloudfront.yml
Resources:
  StaticBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-static"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: 404.html

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        DefaultRootObject: index.html
        Origins:
          - DomainName: !GetAtt StaticBucket.RegionalDomainName
            Id: S3Origin
            S3OriginConfig:
              OriginAccessIdentity: ""
            OriginAccessControlId: !GetAtt OriginAccessControl.Id
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods: [GET, HEAD]
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # Managed-CachingOptimized
        CustomErrorResponses:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /404.html
```

Build and deploy:

```bash
# Build static export
NEXT_PUBLIC_API_URL=https://api.example.com npm run build

# Sync to S3
aws s3 sync dist/ s3://my-bucket --delete

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id XYZ --paths "/*"
```

## Google Cloud Platform

### Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--build-arg=GIT_HASH=$SHORT_SHA'
      - '--tag=gcr.io/$PROJECT_ID/nextjs-app:$SHORT_SHA'
      - '--tag=gcr.io/$PROJECT_ID/nextjs-app:latest'
      - '.'

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/nextjs-app:$SHORT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'nextjs-app'
      - '--image=gcr.io/$PROJECT_ID/nextjs-app:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=NODE_ENV=production'
      - '--set-secrets=DATABASE_URL=db-url:latest'

images:
  - 'gcr.io/$PROJECT_ID/nextjs-app:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/nextjs-app:latest'
```

```bash
# Deploy manually
gcloud run deploy nextjs-app \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production"
```

### App Engine

```yaml
# app.yaml
runtime: nodejs20

instance_class: F2

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

env_variables:
  NODE_ENV: 'production'
  NEXT_TELEMETRY_DISABLED: '1'

handlers:
  - url: /static
    static_dir: .next/static

  - url: /_next/static
    static_dir: .next/static

  - url: /.*
    script: auto

health_check:
  enable_health_check: true
  check_interval_sec: 30
  timeout_sec: 5
  unhealthy_threshold: 3
  healthy_threshold: 1
```

## Microsoft Azure

### Container Instances

```bash
# Create container
az container create \
  --resource-group myResourceGroup \
  --name nextjs-app \
  --image myregistry.azurecr.io/nextjs:latest \
  --cpu 1 \
  --memory 2 \
  --ports 3000 \
  --environment-variables 'NODE_ENV=production' \
  --secrets 'database-url=secret-value' \
  --secrets-mount-path /secrets
```

### App Service

```yaml
# docker-compose.azure.yml
version: '3.8'
services:
  app:
    image: myregistry.azurecr.io/nextjs:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
```

## DigitalOcean

### App Platform

```yaml
# .do/app.yaml
name: nextjs-app
services:
  - name: web
    source_dir: /
    github:
      repo: username/repo
      branch: main
      deploy_on_push: true
    build_command: npm run build
    run_command: npm start
    environment_slug: node-js
    instance_count: 2
    instance_size_slug: basic-xs
    envs:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        value: ${db.DATABASE_URL}
        type: SECRET
    health_check:
      http_path: /api/health
      timeout_seconds: 10
      port: 3000
      success_threshold: 1
      failure_threshold: 3

static_sites:
  - name: static
    source_dir: .next/static
    output_dir: /
```

## Railway

```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set NEXT_PUBLIC_API_URL="https://api.example.com"
```

## Render

```yaml
# render.yaml
services:
  - type: web
    name: nextjs-app
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
      - key: NEXT_PUBLIC_API_URL
        value: https://api.example.com
    healthCheckPath: /api/health
    autoDeploy: true

databases:
  - name: postgres
    databaseName: nextjs
    user: nextjs
```

## Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch --dockerfile Dockerfile

# Set secrets
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set NEXT_SERVER_ACTIONS_ENCRYPTION_KEY="..."

# Deploy
fly deploy

# Scale
fly scale count 3
fly scale vm shared-cpu-1x --memory 1024
```

```toml
# fly.toml (auto-generated)
app = "nextjs-app"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "3000"
  NODE_ENV = "production"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

  [http_service.concurrency]
    type = "requests"
    hard_limit = 1000
    soft_limit = 200

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024

[checks]
  [checks.health]
    port = 3000
    type = "http"
    interval = "15s"
    timeout = "5s"
    grace_period = "30s"
    method = "GET"
    path = "/api/health"
```

## Netlify

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"
  NEXT_TELEMETRY_DISABLED = "1"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
```

## Comparison Table

| Platform | Best For | Standalone | Serverless | Price Model |
|----------|----------|------------|------------|-------------|
| Vercel | Next.js native | Partial | Yes | Usage-based |
| AWS ECS | Enterprise | Yes | No | Resource-based |
| GCP Cloud Run | Container scaling | Yes | Yes | Request-based |
| Azure App Service | .NET/Azure shops | Yes | No | Instance-based |
| DigitalOcean | Simplicity | Yes | No | Fixed |
| Railway | Developer UX | Yes | No | Usage-based |
| Render | Full-stack apps | Yes | No | Fixed |
| Fly.io | Edge deployment | Yes | No | Resource-based |
| Netlify | JAMstack | Partial | Yes | Usage-based |

## Platform-Specific Notes

### Vercel
- Native Next.js optimizations
- Automatic preview deployments
- Edge Functions for middleware
- Limits: 4.5MB serverless function size

### AWS
- Full control over infrastructure
- ECS Fargate for containerized apps
- Lambda for serverless (with @sls-next)
- CloudFront for global CDN

### GCP
- Cloud Run: Pay per request
- Automatic scaling to zero
- Built-in Cloud Monitoring
- Cloud CDN integration

### Azure
- App Service: Simple deployment
- Container Instances: Short-lived tasks
- AKS: Kubernetes orchestration
- Static Web Apps: JAMstack
