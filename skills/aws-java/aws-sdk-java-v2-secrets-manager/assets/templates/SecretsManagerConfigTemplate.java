import com.amazonaws.secretsmanager.caching.SecretCache;
import com.amazonaws.secretsmanager.caching.SecretCacheConfiguration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class {{ConfigClass}} {

    @Value("${aws.secrets.region}")
    private String region;

    @Bean
    public SecretsManagerClient secretsManagerClient() {
        return SecretsManagerClient.builder()
            .region(Region.of(region))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(
                    "${aws.accessKeyId}",
                    "${aws.secretKey}"
                )
            ))
            .build();
    }

    @Bean
    public SecretCache secretCache(SecretsManagerClient secretsClient) {
        SecretCacheConfiguration config = SecretCacheConfiguration.builder()
            .maxCacheSize(100)
            .cacheItemTTL(3600000) // 1 hour
            .build();

        return new SecretCache(secretsClient, config);
    }
}