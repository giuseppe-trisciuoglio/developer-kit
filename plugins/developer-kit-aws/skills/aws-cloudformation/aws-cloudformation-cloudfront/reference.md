# AWS CloudFormation CloudFront - Reference

Questa guida di riferimento contiene informazioni dettagliate sulle risorse AWS CloudFormation, le funzioni intrinseche e le configurazioni per l'infrastruttura CloudFront CDN.

## AWS::CloudFront::Distribution

Crea una distribuzione CloudFront per servire contenuti da origini multiple.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| DistributionConfig | DistributionConfig | Si | Configurazione della distribuzione |
| Tags | List di Tag | No | Tag per la distribuzione |

### DistributionConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CallerReference | String | Si | Identificatore univoco per la distribuzione |
| Comment | String | No | Commento per la distribuzione |
| CustomErrorResponses | List | No | Risposte di errore personalizzate |
| DefaultRootObject | String | No | Oggetto predefinito per richieste root |
| Enabled | Boolean | Si | Se la distribuzione e abilitata |
| HttpVersion | String | No | Versione HTTP supportata |
| IPV6Enabled | Boolean | No | Se IPv6 e abilitato |
| Logging | LoggingConfig | No | Configurazione logging |
| OriginGroups | List | No | Gruppi di origini per failover |
| Origins | List | Si | Lista delle origini |
| PriceClass | String | No | Classe di prezzo (PriceClass_All, PriceClass_100, PriceClass_200) |
| Restrictions | GeoRestriction | No | Restrizioni geografiche |
| ViewerCertificate | ViewerCertificate | No | Certificato per HTTPS |
| WebACLId | String | No | ID del Web ACL WAF |
| DefaultCacheBehavior | CacheBehavior | Si | Comportamento cache predefinito |
| CacheBehaviors | List | No | Comportamenti cache aggiuntivi |
| RealTimeConfig | RealTimeConfig | No | Configurazione log real-time |

### Origins Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Id | String | Si | Identificatore univoco per l'origine |
| DomainName | String | Si | Nome di dominio dell'origine |
| OriginPath | String | No | Percorso opzionale nell'origine |
| CustomOriginConfig | CustomOrigin | No | Configurazione per origini personalizzate |
| S3OriginConfig | S3Origin | No | Configurazione per origini S3 |
| ConnectionAttempts | Integer | No | Numero di tentativi di connessione |
| ConnectionTimeout | Integer | No | Timeout connessione in secondi |
| OriginShield | OriginShield | No | Configurazione Origin Shield |
| OriginKeepaliveTimeout | Integer | No | Timeout keepalive in secondi |
| OriginReadTimeout | Integer | No | Timeout lettura in secondi |

### CustomOrigin Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| HTTPPort | Integer | No | Porta HTTP (default: 80) |
| HTTPSPort | Integer | No | Porta HTTPS (default: 443) |
| OriginProtocolPolicy | String | Si | Politica protocollo (http-only, https-only, match-viewer) |
| OriginSSLProtocols | List | No | Protocolli SSL supportati |
| OriginReadTimeout | Integer | No | Timeout lettura (4-60 secondi) |
| OriginKeepaliveTimeout | Integer | No | Timeout keepalive (1-60 secondi) |

### S3Origin Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| OriginAccessIdentity | String | No | ID dell'OAI per accesso al bucket |

### CacheBehavior Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| AllowedMethods | List | Si | Metodi HTTP permessi |
| CachePolicyId | String | No | ID della cache policy |
| Compress | Boolean | No | Se abilitare compressione |
| DefaultTTL | Integer | No | TTL default in secondi |
| FieldLevelEncryptionId | String | No | ID crittografia campo |
| ForwardedValues | ForwardedValues | Si | Valori inoltrati all'origine |
| FunctionAssociations | List | No | Associazioni CloudFront Functions |
| LambdaFunctionAssociations | List | No | Associazioni Lambda@Edge |
| MaxTTL | Integer | No | TTL massimo in secondi |
| MinTTL | Integer | No | TTL minimo in secondi |
| OriginRequestPolicyId | String | No | ID della origin request policy |
| PathPattern | String | Si | Pattern percorso |
| ResponseHeadersPolicyId | String | No | ID della response headers policy |
| TargetOriginId | String | Si | ID dell'origine target |
| TrustedSigners | List | No | Account AWS autorizzati |
| ViewerProtocolPolicy | String | Si | Politica protocollo viewer |

### ForwardedValues Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Cookies | Cookies | Si | Configurazione cookie |
| Headers | List | No | Lista header da inoltrare |
| QueryString | Boolean | No | Se inoltrare query string |
| QueryStringCacheKeys | List | No | Chiavi query string da cachare |

### Cookies Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Forward | String | Si | none, whitelist, all |

### ViewerCertificate Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| AcmCertificateArn | String | No | ARN certificato ACM |
| CloudFrontDefaultCertificate | Boolean | No | Usa certificato default |
| IamCertificateId | String | No | ID certificato IAM |
| MinimumProtocolVersion | String | No | Versione minima TLS |
| SslSupportMethod | String | No | sni-only, vip |

### Esempio

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"
        Comment: !Sub "CloudFront distribution"
        Enabled: true
        IPV6Enabled: true
        PriceClass: PriceClass_All
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt StaticBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
        ViewerCertificate:
          AcmCertificateArn: !Ref CertificateArn
          MinimumProtocolVersion: TLSv1.2_2021
          SslSupportMethod: sni-only
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| DomainName | Nome dominio della distribuzione |
| Id | ID della distribuzione |
| ARN | ARN della distribuzione |

## AWS::CloudFront::CloudFrontOriginAccessIdentity

Crea un Origin Access Identity per permettere a CloudFront di accedere a bucket S3 privati.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CloudFrontOriginAccessIdentityConfig | OriginAccessIdentityConfig | Si | Configurazione OAI |

### OriginAccessIdentityConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Comment | String | No | Commento per l'OAI |

### Esempio

```yaml
Resources:
  CloudFrontOAI:
    Type: AWS::CloudFront::CloudFrontOriginAccessIdentity
    Properties:
      CloudFrontOriginAccessIdentityConfig:
        Comment: !Sub "OAI for ${StaticBucket}"

  S3BucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref StaticBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              CanonicalUser: !GetAtt CloudFrontOAI.S3CanonicalUserId
            Action: s3:GetObject
            Resource: !Sub "${StaticBucket.Arn}/*"
```

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| S3CanonicalUserId | ID canonico utente S3 |
| Arn | ARN dell'OAI |

## AWS::CloudFront::CachePolicy

Crea una policy di cache per configurare come CloudFront gestisce la cache.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CachePolicyConfig | CachePolicyConfig | Si | Configurazione della policy |

### CachePolicyConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome della policy |
| DefaultTTL | Integer | Si | TTL default in secondi |
| MaxTTL | Integer | Si | TTL massimo in secondi |
| MinTTL | Integer | Si | TTL minimo in secondi |
| ParametersInCacheKeyAndForwardedToOrigin | ParametersInCacheKeyAndForwardedToOrigin | Si | Parametri inclusi nella chiave di cache |

### ParametersInCacheKeyAndForwardedToOrigin Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CookiesConfig | CookiesConfig | Si | Configurazione cookie |
| EnableAcceptEncodingBrotli | Boolean | No | Se abilitare compressione Brotli |
| EnableAcceptEncodingGzip | Boolean | No | Se abilitare compressione Gzip |
| HeadersConfig | HeadersConfig | Si | Configurazione header |
| QueryStringsConfig | QueryStringsConfig | Si | Configurazione query string |

### CookiesConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CookieBehavior | String | Si | none, whitelist, all |

### HeadersConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| HeaderBehavior | String | Si | none, whitelist, all |
| Headers | List | Cond | Lista header (richiesto se whitelist) |

### QueryStringsConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| QueryStringBehavior | String | Si | none, whitelist, all, allExcept |
| QueryStrings | List | Cond | Lista query string (richiesto se whitelist/allExcept) |

### Esempio

```yaml
Resources:
  StaticAssetsCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-static-assets-policy"
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 0
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: none
          QueryStringsConfig:
            QueryStringBehavior: none
          EnableAcceptEncodingBrotli: true
          EnableAcceptEncodingGzip: true

  ApiCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub "${AWS::StackName}-api-cache-policy"
        DefaultTTL: 300
        MaxTTL: 600
        MinTTL: 60
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: all
          HeadersConfig:
            HeaderBehavior: whitelist
            Headers:
              - Authorization
              - Content-Type
          QueryStringsConfig:
            QueryStringBehavior: all
```

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| Id | ID della policy |

## AWS::CloudFront::OriginRequestPolicy

Crea una policy per le richieste all'origine.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| OriginRequestPolicyConfig | OriginRequestPolicyConfig | Si | Configurazione della policy |

### OriginRequestPolicyConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome della policy |
| CookiesConfig | CookiesConfig | Si | Configurazione cookie |
| HeadersConfig | HeadersConfig | Si | Configurazione header |
| QueryStringsConfig | QueryStringsConfig | Si | Configurazione query string |

### Esempio

```yaml
Resources:
  ApiOriginRequestPolicy:
    Type: AWS::CloudFront::OriginRequestPolicy
    Properties:
      OriginRequestPolicyConfig:
        Name: !Sub "${AWS::StackName}-api-origin-request"
        CookiesConfig:
          CookieBehavior: all
        HeadersConfig:
          HeaderBehavior: whitelist
          Headers:
            - Authorization
            - Content-Type
            - X-Request-ID
        QueryStringsConfig:
          QueryStringBehavior: all
```

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| Id | ID della policy |

## AWS::CloudFront::ResponseHeadersPolicy

Crea una policy per gli header di risposta, utile per implementare security headers.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| ResponseHeadersPolicyConfig | ResponseHeadersPolicyConfig | Si | Configurazione della policy |

### ResponseHeadersPolicyConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Name | String | Si | Nome della policy |
| SecurityHeadersConfig | SecurityHeadersConfig | No | Configurazione security headers |
| CorsConfig | CorsConfig | No | Configurazione CORS |
| CustomHeadersConfig | CustomHeadersConfig | No | Header personalizzati |
| ServerTimingHeadersConfig | ServerTimingHeadersConfig | No | Configurazione header Server-Timing |

### SecurityHeadersConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| ContentTypeOptions | ContentTypeOptions | No | Header X-Content-Type-Options |
| FrameOptions | FrameOptions | No | Header X-Frame-Options |
| ReferrerPolicy | ReferrerPolicy | No | Header Referrer-Policy |
| StrictTransportSecurity | StrictTransportSecurity | No | Header Strict-Transport-Security |
| XSSProtection | XSSProtection | No | Header X-XSS-Protection |

### ContentTypeOptions Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Override | Boolean | Si | Se sovrascrivere header esistenti |

### FrameOptions Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| FrameOption | String | Si | DENY, SAMEORIGIN |
| Override | Boolean | Si | Se sovrascrivere |

### ReferrerPolicy Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| ReferrerPolicy | String | Si | Valore del referrer policy |
| Override | Boolean | Si | Se sovrascrivere |

### StrictTransportSecurity Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| AccessControlMaxAgeSec | Integer | Si | Max age in secondi |
| IncludeSubdomains | Boolean | No | Se includere subdomain |
| Override | Boolean | Si | Se sovrascrivere |
| Preload | Boolean | No | Se abilitare preload |

### XSSProtection Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| ModeBlock | Boolean | No | Se bloccare in modalita block |
| Override | Boolean | Si | Se sovrascrivere |
| Protection | Boolean | Si | Se abilitare protezione |

### CorsConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| AccessControlAllowCredentials | Boolean | No | Se允许 credenziali |
| AccessControlAllowHeaders | AccessControlAllowHeaders | No | Header permessi |
| AccessControlAllowMethods | AccessControlAllowMethods | No | Metodi permessi |
| AccessControlAllowOrigins | AccessControlAllowOrigins | No | Origini permesse |
| AccessControlMaxAgeSec | Integer | No | Max age per preflight |
| AccessControlExposeHeaders | AccessControlExposeHeaders | No | Header esposti |
| OriginOverride | Boolean | Si | Se sovrascrivere header origin |

### Esempio

```yaml
Resources:
  SecurityHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub "${AWS::StackName}-security-headers"
        SecurityHeadersConfig:
          ContentTypeOptions:
            Override: true
          FrameOptions:
            FrameOption: DENY
            Override: true
          ReferrerPolicy:
            ReferrerPolicy: strict-origin-when-cross-origin
            Override: true
          StrictTransportSecurity:
            AccessControlMaxAgeSec: 31536000
            IncludeSubdomains: true
            Override: true
            Preload: true
          XSSProtection:
            ModeBlock: true
            Override: true
            Protection: true
        CorsConfig:
          AccessControlAllowCredentials: false
          AccessControlAllowHeaders:
            Items:
              - "*"
          AccessControlAllowMethods:
            Items:
              - GET
              - HEAD
              - OPTIONS
          AccessControlAllowOrigins:
            Items:
              - https://example.com
          AccessControlMaxAgeSec: 600
          OriginOverride: true
```

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| Id | ID della policy |

## AWS::CloudFront::Function

Crea una funzione CloudFront per operazioni leggere sul edge.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| AutoPublish | Boolean | No | Se pubblicare automaticamente |
| FunctionCode | String | Si | Codice della funzione |
| FunctionRuntime | String | Si | Runtime della funzione |
| Name | String | Si | Nome della funzione |
| Comment | String | No | Commento |

### Runtime Supportati

| Runtime | Descrizione |
|---------|-------------|
| cloudfront-js-1.0 | CloudFront Functions JavaScript |

### Esempio

```yaml
Resources:
  RewritePathFunction:
    Type: AWS::CloudFront::Function
    Properties:
      Name: !Sub "${AWS::StackName}-rewrite-path"
      FunctionCode: |
        function handler(event) {
          var request = event.request;
          var uri = request.uri;

          if (uri.endsWith('/')) {
            request.uri = uri.substring(0, uri.length - 1);
          }

          if (!uri.includes('.') && !uri.endsWith('/')) {
            request.uri = uri + '.html';
          }

          return request;
        }
      Runtime: cloudfront-js-1.0
      AutoPublish: true

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: Origin
            DomainName: !Ref OriginDomainName
            CustomOriginConfig:
              HTTPPort: 443
              HTTPSPort: 443
              OriginProtocolPolicy: https-only
        DefaultCacheBehavior:
          TargetOriginId: Origin
          FunctionAssociations:
            - FunctionARN: !GetAtt RewritePathFunction.FunctionARN
              EventType: viewer-request
```

### Eventi Function Association

| Evento | Descrizione |
|--------|-------------|
| viewer-request | Prima della richiesta del viewer |
| viewer-response | Dopo la risposta al viewer |
| origin-request | Prima della richiesta all'origine |
| origin-response | Dopo la risposta dall'origine |

### Attributi

| Attributo | Descrizione |
|-----------|-------------|
| FunctionARN | ARN della funzione |

## AWS::WAFv2::WebACL

Crea un Web ACL WAF per proteggere CloudFront.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| DefaultAction | DefaultAction | Si | Azione default |
| Name | String | Si | Nome del Web ACL |
| Rules | List | No | Lista delle regole |
| Scope | String | Si | CLOUDFRONT o REGIONAL |
| VisibilityConfig | VisibilityConfig | Si | Configurazione visibilita |

### DefaultAction Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Allow | AllowAction | No | Azione allow |
| Block | BlockAction | No | Azione block |

### VisibilityConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| CloudWatchMetricsEnabled | Boolean | Si | Se abilitare metriche CloudWatch |
| MetricName | String | Si | Nome metrica |
| SampledRequestsEnabled | Boolean | Si | Se abilitare sampling |

### Esempio

```yaml
Resources:
  CloudFrontWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${AWS::StackName}-waf-acl"
      Scope: CLOUDFRONT
      DefaultAction:
        Allow: {}
      Rules:
        - Name: AWSCommonRule
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: AWSCommonRule
      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: CloudFrontWAFACL
```

## AWS::GlobalAccelerator::EndpointGroup

Crea un endpoint group per VPC Origins.

### Proprieta

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| EndpointGroupRegion | String | Si | Regione del endpoint group |
| EndpointConfigurations | List | No | Configurazioni endpoint |
| ListenerArn | String | Si | ARN del listener |
| TrafficDialPercentage | Integer | No | Percentuale traffico |

### EndpointConfiguration Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| EndpointId | String | Si | ID dell'endpoint |
| Weight | Integer | No | Peso per traffic routing |

### Esempio

```yaml
Resources:
  VPCOriginEndpoint:
    Type: AWS::GlobalAccelerator::EndpointGroup
    Properties:
      EndpointGroupRegion: !Ref VPCOriginRegion
      ListenerArn: !Ref AcceleratorListener
      EndpointConfigurations:
        - EndpointId: !Ref VPCEndpointService
          Weight: 128
```

## GeoRestriction Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Locations | List | Cond | Lista codici paese (whitelist/blacklist) |
| RestrictionType | String | Si | none, blacklist, whitelist |

## LoggingConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Bucket | String | Si | S3 bucket per log |
| IncludeCookies | Boolean | No | Se includere cookie |
| Prefix | String | No | Prefisso per log |

## RealTimeConfig Structure

| Proprieta | Tipo | Richiesta | Descrizione |
|-----------|------|-----------|-------------|
| Endpoint | String | Si | ARN del Kinesis stream |
| Fields | List | Si | Campi da includere |
| RoleArn | String | Si | ARN del ruolo IAM |

## Funzioni Intrinseche di Riferimento

### !GetAtt

Restituisce il valore di un attributo da una risorsa CloudFront.

```yaml
# Get distribution domain name
DistributionDomainName: !GetAtt CloudFrontDistribution.DomainName

# Get distribution ID
DistributionId: !Ref CloudFrontDistribution

# Get OAI canonical user ID
CanonicalUserId: !GetAtt CloudFrontOAI.S3CanonicalUserId

# Get S3 bucket regional domain name
BucketDomainName: !GetAtt StaticBucket.RegionalDomainName
```

### !Sub

Sostituisce variabili in una stringa.

```yaml
# With variable substitution
CallerReference: !Sub "${AWS::StackName}-${AWS::AccountId}"

# Origin access identity path
OriginAccessIdentity: !Sub "origin-access-identity/cloudfront/${CloudFrontOAI}"
```

### !ImportValue

Importa valori esportati da altri stack.

```yaml
# Import from another stack
BucketDomainName: !ImportValue
  !Sub "${NetworkStackName}-StaticAssetsBucketRegionalDomainName"
```

## Limiti e Quote

### CloudFront Limits

| Risorsa | Limite Default |
|---------|----------------|
| Distribuzioni per account | 200 |
| Origini per distribuzione | 25 |
| Cache behaviors per distribuzione | 25 |
| Certificate per account | 2000 |
| TTL massimo | 31536000 secondi (1 anno) |
| Size request body | 20 MB (edge), 5 MB (viewer) |
| Numero di OAI | 100 per account |
| Lunghezza dominio personalizzato | 253 caratteri |

### CloudFront Functions Limits

| Risorsa | Limite |
|---------|--------|
| Tempo esecuzione | 1 ms |
| Memory | 2 MB |
| Size request/response | 10 KB |
| Size function code | 10 KB |

### Lambda@Edge Limits

| Risorso | Limite |
|---------|--------|
| Memory | 128 MB |
| Timeout | 30 secondi |
| Size deployment package | 1 MB |
| Size response body | 1 MB |

## Managed Cache Policies

AWS fornisce managed policies predefinite:

| Policy ID | Nome | Descrizione |
|-----------|------|-------------|
| 658327ea-f89d-4fab-a63d-7e88639e58f6 | Managed-CachingOptimized | Ottimizzato per caching |
| 5cc3b908-e619-4b99-88e5-2cf7a4592e4c | Managed-Elemental-MediaPackage | Per MediaPackage |
| b2884449-e4de-46a7-ac21-5511b5d11b5f | Managed-Amplify | Per Amplify |

## Managed Origin Request Policies

| Policy ID | Nome | Descrizione |
|-----------|------|-------------|
| 33f36d7e-f398-4d50-aaf9-1a26f4830ef3 | Managed-CORS-S3Origin | CORS per S3 |
| 10c336ab-3b4b-4e2b-a38b-5b4a20d0a1e2 | Managed-AllView | Forward tutto |

## Tag Comuni per CloudFront

```yaml
Resources:
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        Origins: []
        DefaultCacheBehavior:
          TargetOriginId: Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none
          MinTTL: 0
          DefaultTTL: 86400
          MaxTTL: 31536000
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: team@example.com
        - Key: ManagedBy
          Value: CloudFormation
        - Key: CostCenter
          Value: "12345"
        - Key: Version
          Value: "1.0.0"
```
