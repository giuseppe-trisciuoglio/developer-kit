The Spring Framework provides support for transparently adding caching
to an application. At its core, the abstraction applies caching to
methods, thus reducing the number of executions based on the information
available in the cache. The caching logic is applied transparently,
without any interference to the invoker. Spring Boot auto-configures the
cache infrastructure as long as caching support is enabled by using the
`org.springframework.cache.annotation.EnableCaching`[format=annotation]
annotation.

> [!NOTE]
> Check the {url-spring-framework-docs}/integration/cache.html[relevant
> section] of the Spring Framework reference for more details.

In a nutshell, to add caching to an operation of your service add the
relevant annotation to its method, as shown in the following example:

include-code::MyMathService[]

This example demonstrates the use of caching on a potentially costly
operation. Before invoking `computePiDecimal`, the abstraction looks for
an entry in the `piDecimals` cache that matches the `precision`
argument. If an entry is found, the content in the cache is immediately
returned to the caller, and the method is not invoked. Otherwise, the
method is invoked, and the cache is updated before returning the value.

> [!CAUTION]
> You can also use the standard JSR-107 (JCache) annotations (such as
> `javax.cache.annotation.CacheResult`[format=annotation])
> transparently. However, we strongly advise you to not mix and match
> the Spring Cache and JCache annotations.

If you do not add any specific cache library, Spring Boot
auto-configures a [simple
provider](io/caching.xml#io.caching.provider.simple) that uses
concurrent maps in memory. When a cache is required (such as
`piDecimals` in the preceding example), this provider creates it for
you. The simple provider is not really recommended for production usage,
but it is great for getting started and making sure that you understand
the features. When you have made up your mind about the cache provider
to use, please make sure to read its documentation to figure out how to
configure the caches that your application uses. Nearly all providers
require you to explicitly configure every cache that you use in the
application. Some offer a way to customize the default caches defined by
the configprop:spring.cache.cache-names[] property.

> [!TIP]
> It is also possible to transparently
> {url-spring-framework-docs}/integration/cache/annotations.html#cache-annotations-put[update]
> or
> {url-spring-framework-docs}/integration/cache/annotations.html#cache-annotations-evict[evict]
> data from the cache.

# Supported Cache Providers

The cache abstraction does not provide an actual store and relies on
abstraction materialized by the
`org.springframework.cache.Cache[] and
`org.springframework.cache.CacheManager[] interfaces.

If you have not defined a bean of type
`org.springframework.cache.CacheManager[] or a
`org.springframework.cache.interceptor.CacheResolver[] named
`cacheResolver` (see
`org.springframework.cache.annotation.CachingConfigurer[]),
Spring Boot tries to detect the following providers (in the indicated
order):

1.  [io/caching.xml](io/caching.xml#io.caching.provider.generic)

2.  [io/caching.xml](io/caching.xml#io.caching.provider.jcache) (EhCache
    3, Hazelcast, Infinispan, and others)

3.  [io/caching.xml](io/caching.xml#io.caching.provider.hazelcast)

4.  [io/caching.xml](io/caching.xml#io.caching.provider.infinispan)

5.  [io/caching.xml](io/caching.xml#io.caching.provider.couchbase)

6.  [io/caching.xml](io/caching.xml#io.caching.provider.redis)

7.  [io/caching.xml](io/caching.xml#io.caching.provider.caffeine)

8.  [io/caching.xml](io/caching.xml#io.caching.provider.cache2k)

9.  [io/caching.xml](io/caching.xml#io.caching.provider.simple)

Additionally, {url-spring-boot-for-apache-geode-site}[Spring Boot for
Apache Geode] provides
{url-spring-boot-for-apache-geode-docs}#geode-caching-provider[auto-configuration
for using Apache Geode as a cache provider].

> [!TIP]
> If the `org.springframework.cache.CacheManager[] is
> auto-configured by Spring Boot, it is possible to *force* a particular
> cache provider by setting the configprop:spring.cache.type[]
> property. Use this property if you need to [use no-op
> caches](io/caching.xml#io.caching.provider.none) in certain
> environments (such as tests).

> [!TIP]
> Use the `spring-boot-starter-cache` starter to quickly add basic
> caching dependencies. The starter brings in `spring-context-support`.
> If you add dependencies manually, you must include
> `spring-context-support` in order to use the JCache or Caffeine
> support.

If the `org.springframework.cache.CacheManager[] is
auto-configured by Spring Boot, you can further tune its configuration
before it is fully initialized by exposing a bean that implements the
`org.springframework.boot.autoconfigure.cache.CacheManagerCustomizer[]
interface. The following example sets a flag to say that `null` values
should not be passed down to the underlying map:

include-code::MyCacheManagerConfiguration[]

> [!NOTE]
> In the preceding example, an auto-configured
> `org.springframework.cache.concurrent.ConcurrentMapCacheManager[]
> is expected. If that is not the case (either you provided your own
> config or a different cache provider was auto-configured), the
> customizer is not invoked at all. You can have as many customizers as
> you want, and you can also order them by using
> `org.springframework.core.annotation.Order`[format=annotation]
> or `org.springframework.core.Ordered[].

## Generic

Generic caching is used if the context defines *at least* one
`org.springframework.cache.Cache[] bean. A
`org.springframework.cache.CacheManager[] wrapping all beans of
that type is created.

## JCache (JSR-107)

[JCache](https://jcp.org/en/jsr/detail?id=107) is bootstrapped through
the presence of a `javax.cache.spi.CachingProvider[] on the
classpath (that is, a JSR-107 compliant caching library exists on the
classpath), and the
`org.springframework.cache.jcache.JCacheCacheManager[] is
provided by the `spring-boot-starter-cache` starter. Various compliant
libraries are available, and Spring Boot provides dependency management
for Ehcache 3, Hazelcast, and Infinispan. Any other compliant library
can be added as well.

It might happen that more than one provider is present, in which case
the provider must be explicitly specified. Even if the JSR-107 standard
does not enforce a standardized way to define the location of the
configuration file, Spring Boot does its best to accommodate setting a
cache with implementation details, as shown in the following example:

        # Only necessary if more than one provider is present
        spring:
          cache:
            jcache:
              provider: "com.example.MyCachingProvider"
              config: "classpath:example.xml"

> [!NOTE]
> When a cache library offers both a native implementation and JSR-107
> support, Spring Boot prefers the JSR-107 support, so that the same
> features are available if you switch to a different JSR-107
> implementation.

> [!TIP]
> Spring Boot has [general support for Hazelcast](io/hazelcast.xml). If
> a single `com.hazelcast.core.HazelcastInstance[] is
> available, it is automatically reused for the
> `javax.cache.CacheManager[] as well, unless the
> configprop:spring.cache.jcache.config[] property is specified.

There are two ways to customize the underlying
`javax.cache.CacheManager[]:

- Caches can be created on startup by setting the
  configprop:spring.cache.cache-names[] property. If a custom
  `javax.cache.configuration.Configuration[] bean is defined,
  it is used to customize them.

- `org.springframework.boot.autoconfigure.cache.JCacheManagerCustomizer[]
  beans are invoked with the reference of the
  `javax.cache.CacheManager[] for full customization.

> [!TIP]
> If a standard `javax.cache.CacheManager[] bean is defined, it
> is wrapped automatically in an
> `org.springframework.cache.CacheManager[] implementation that
> the abstraction expects. No further customization is applied to it.

## Hazelcast

Spring Boot has [general support for Hazelcast](io/hazelcast.xml). If a
`com.hazelcast.core.HazelcastInstance[] has been
auto-configured and `com.hazelcast:hazelcast-spring` is on the
classpath, it is automatically wrapped in a
`org.springframework.cache.CacheManager[].

> [!NOTE]
> Hazelcast can be used as a JCache compliant cache or as a Spring
> `org.springframework.cache.CacheManager[] compliant cache.
> When setting configprop:spring.cache.type[] to `hazelcast`, Spring
> Boot will use the `org.springframework.cache.CacheManager[]
> based implementation. If you want to use Hazelcast as a JCache
> compliant cache, set configprop:spring.cache.type[] to `jcache`. If
> you have multiple JCache compliant cache providers and want to force
> the use of Hazelcast, you have to [explicitly set the JCache
> provider](io/caching.xml#io.caching.provider.jcache).

## Infinispan

[Infinispan](https://infinispan.org/) has no default configuration file
location, so it must be specified explicitly. Otherwise, the default
bootstrap is used.

    spring:
      cache:
        infinispan:
          config: "infinispan.xml"

Caches can be created on startup by setting the
configprop:spring.cache.cache-names[] property. If a custom
`org.infinispan.configuration.cache.ConfigurationBuilder[] bean
is defined, it is used to customize the caches.

To be compatible with Spring Boot’s Jakarta EE 9 baseline, Infinispan’s
`-jakarta` modules must be used. For every module with a `-jakarta`
variant, the variant must be used in place of the standard module. For
example, `infinispan-core-jakarta` and `infinispan-commons-jakarta` must
be used in place of `infinispan-core` and `infinispan-commons`
respectively.

## Couchbase

If Spring Data Couchbase is available and Couchbase is
[configured](data/nosql.xml#data.nosql.couchbase), a
`org.springframework.data.couchbase.cache.CouchbaseCacheManager[]
is auto-configured. It is possible to create additional caches on
startup by setting the configprop:spring.cache.cache-names[] property
and cache defaults can be configured by using `spring.cache.couchbase.*`
properties. For instance, the following configuration creates `cache1`
and `cache2` caches with an entry *expiration* of 10 minutes:

    spring:
      cache:
        cache-names: "cache1,cache2"
        couchbase:
          expiration: "10m"

If you need more control over the configuration, consider registering a
`org.springframework.boot.autoconfigure.cache.CouchbaseCacheManagerBuilderCustomizer[]
bean. The following example shows a customizer that configures a
specific entry expiration for `cache1` and `cache2`:

include-code::MyCouchbaseCacheManagerConfiguration[]

## Redis

If [Redis](https://redis.io/) is available and configured, a
`org.springframework.data.redis.cache.RedisCacheManager[] is
auto-configured. It is possible to create additional caches on startup
by setting the configprop:spring.cache.cache-names[] property and
cache defaults can be configured by using `spring.cache.redis.*`
properties. For instance, the following configuration creates `cache1`
and `cache2` caches with a *time to live* of 10 minutes:

    spring:
      cache:
        cache-names: "cache1,cache2"
        redis:
          time-to-live: "10m"

> [!NOTE]
> By default, a key prefix is added so that, if two separate caches use
> the same key, Redis does not have overlapping keys and cannot return
> invalid values. We strongly recommend keeping this setting enabled if
> you create your own
> `org.springframework.data.redis.cache.RedisCacheManager[].

> [!TIP]
> You can take full control of the default configuration by adding a
> `org.springframework.data.redis.cache.RedisCacheConfiguration[]
> `org.springframework.context.annotation.Bean`[format=annotation]
> of your own. This can be useful if you need to customize the default
> serialization strategy.

If you need more control over the configuration, consider registering a
`org.springframework.boot.autoconfigure.cache.RedisCacheManagerBuilderCustomizer[]
bean. The following example shows a customizer that configures a
specific time to live for `cache1` and `cache2`:

include-code::MyRedisCacheManagerConfiguration[]

## Caffeine

[Caffeine](https://github.com/ben-manes/caffeine) is a Java 8 rewrite of
Guava’s cache that supersedes support for Guava. If Caffeine is present,
a `org.springframework.cache.caffeine.CaffeineCacheManager[]
(provided by the `spring-boot-starter-cache` starter) is
auto-configured. Caches can be created on startup by setting the
configprop:spring.cache.cache-names[] property and can be customized
by one of the following (in the indicated order):

1.  A cache spec defined by `spring.cache.caffeine.spec`

2.  A `com.github.benmanes.caffeine.cache.CaffeineSpec[] bean
    is defined

3.  A `com.github.benmanes.caffeine.cache.Caffeine[] bean is
    defined

For instance, the following configuration creates `cache1` and `cache2`
caches with a maximum size of 500 and a *time to live* of 10 minutes

    spring:
      cache:
        cache-names: "cache1,cache2"
        caffeine:
          spec: "maximumSize=500,expireAfterAccess=600s"

If a `com.github.benmanes.caffeine.cache.CacheLoader[] bean is
defined, it is automatically associated to the
`org.springframework.cache.caffeine.CaffeineCacheManager[].
Since the `com.github.benmanes.caffeine.cache.CacheLoader[] is
going to be associated with *all* caches managed by the cache manager,
it must be defined as `CacheLoader<Object, Object>`. The
auto-configuration ignores any other generic type.

## Cache2k

[Cache2k](https://cache2k.org/) is an in-memory cache. If the Cache2k
spring integration is present, a `SpringCache2kCacheManager` is
auto-configured.

Caches can be created on startup by setting the
configprop:spring.cache.cache-names[] property. Cache defaults can be
customized using a
`org.springframework.boot.autoconfigure.cache.Cache2kBuilderCustomizer[]
bean. The following example shows a customizer that configures the
capacity of the cache to 200 entries, with an expiration of 5 minutes:

include-code::MyCache2kDefaultsConfiguration[]

## Simple

If none of the other providers can be found, a simple implementation
using a `java.util.concurrent.ConcurrentHashMap[] as the cache
store is configured. This is the default if no caching library is
present in your application. By default, caches are created as needed,
but you can restrict the list of available caches by setting the
`cache-names` property. For instance, if you want only `cache1` and
`cache2` caches, set the `cache-names` property as follows:

    spring:
      cache:
        cache-names: "cache1,cache2"

If you do so and your application uses a cache not listed, then it fails
at runtime when the cache is needed, but not on startup. This is similar
to the way the "real" cache providers behave if you use an undeclared
cache.

## None

When
`org.springframework.cache.annotation.EnableCaching`[format=annotation]
is present in your configuration, a suitable cache configuration is
expected as well. If you have a custom `
org.springframework.cache.CacheManager`, consider defining it in a
separate
`org.springframework.context.annotation.Configuration`[format=annotation]
class so that you can override it if necessary. None uses a no-op
implementation that is useful in tests, and slice tests use that by
default via
`org.springframework.boot.test.autoconfigure.core.AutoConfigureCache`[format=annotation].

If you need to use a no-op cache rather than the auto-configured cache
manager in a certain environment, set the cache type to `none`, as shown
in the following example:

    spring:
      cache:
        type: "none"
