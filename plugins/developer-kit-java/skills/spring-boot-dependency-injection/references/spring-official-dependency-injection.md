# Spring Framework Official Guidance: Dependency Injection (Clean Excerpt)

Source: https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html (retrieved via `u2m -v` on current date).

## Key Highlights
- Emphasize constructor-based dependency injection to make collaborators explicit and enable immutable design.
- Use setter injection only for optional dependencies or when a dependency can change after initialization.
- Field injection is supported but discouraged because it hides dependencies and complicates testing.
- The IoC container resolves constructor arguments by type, name, and order; prefer unique types or qualify arguments with `@Qualifier` or XML attributes when ambiguity exists.
- Static factory methods behave like constructors for dependency injection and can receive collaborators through arguments.

## Constructor-Based DI
```java
public class SimpleMovieLister {
    private final MovieFinder movieFinder;

    public SimpleMovieLister(MovieFinder movieFinder) {
        this.movieFinder = movieFinder;
    }
}
```
- The container selects the matching constructor and provides dependencies by type.
- When argument types are ambiguous, specify indexes (`@ConstructorProperties`, XML `index` attribute) or qualifiers.

## Setter-Based DI
```java
public class SimpleMovieLister {
    private MovieFinder movieFinder;

    @Autowired
    public void setMovieFinder(MovieFinder movieFinder) {
        this.movieFinder = movieFinder;
    }
}
```
- Invoke only when a collaborator is optional or changeable.
- Use `@Autowired(required = false)` or `ObjectProvider<T>` to guard optional collaborators.

## Reference Snippets
```xml
<bean id="exampleBean" class="examples.ExampleBean">
    <constructor-arg ref="anotherExampleBean"/>
    <constructor-arg ref="yetAnotherBean"/>
    <constructor-arg value="1"/>
</bean>

<bean id="exampleBean" class="examples.ExampleBean">
    <property name="beanOne" ref="anotherExampleBean"/>
    <property name="beanTwo" ref="yetAnotherBean"/>
</bean>
```
- Spring treats constructor-arg entries as positional parameters unless `index` or `type` is provided.
- Setter injection uses `<property>` elements mapped by name.

## Additional Notes
- Combine configuration classes with `@Import` to wire dependencies declared in different modules.
- Lazy initialization (`@Lazy`) delays bean creation but defers error detection; prefer eager initialization unless startup time is critical.
- Profiles (`@Profile`) activate different wiring scenarios per environment (for example, `@Profile("test")`).
- Testing support allows constructor injection in production code while wiring mocks manually (no container required) or relying on the TestContext framework for integration tests.
