# Spring Data Neo4j - Examples

This document provides comprehensive, real-world examples of Spring Data Neo4j patterns and implementations.

## Table of Contents

1. [Complete Movie Database Example](#complete-movie-database-example)
2. [Social Network Example](#social-network-example)
3. [E-Commerce Product Catalog](#e-commerce-product-catalog)
4. [Custom Query Examples](#custom-query-examples)
5. [Reactive Neo4j Examples](#reactive-neo4j-examples)
6. [Testing Examples](#testing-examples)

## Complete Movie Database Example

### Entity Classes

```java
@Node("Movie")
public class Movie {
    
    @Id
    private final String imdbId;
    
    private final String title;
    
    @Property("tagline")
    private final String description;
    
    private final Integer releaseYear;
    
    private final List<String> genres;
    
    @Relationship(type = "ACTED_IN", direction = Direction.INCOMING)
    private List<ActedIn> actors;
    
    @Relationship(type = "DIRECTED", direction = Direction.INCOMING)
    private List<Person> directors;
    
    public Movie(String imdbId, String title, String description, 
                 Integer releaseYear, List<String> genres) {
        this.imdbId = imdbId;
        this.title = title;
        this.description = description;
        this.releaseYear = releaseYear;
        this.genres = genres;
        this.actors = new ArrayList<>();
        this.directors = new ArrayList<>();
    }
    
    // Getters
    public String getImdbId() { return imdbId; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public Integer getReleaseYear() { return releaseYear; }
    public List<String> getGenres() { return genres; }
    public List<ActedIn> getActors() { return actors; }
    public List<Person> getDirectors() { return directors; }
}

@Node("Person")
public class Person {
    
    @Id @GeneratedValue
    private Long id;
    
    private final String name;
    
    private final Integer birthYear;
    
    @Relationship(type = "ACTED_IN", direction = Direction.OUTGOING)
    private List<ActedIn> actedIn;
    
    @Relationship(type = "DIRECTED", direction = Direction.OUTGOING)
    private List<Movie> directed;
    
    public Person(String name, Integer birthYear) {
        this.name = name;
        this.birthYear = birthYear;
        this.actedIn = new ArrayList<>();
        this.directed = new ArrayList<>();
    }
    
    public Person withId(Long id) {
        if (this.id != null && this.id.equals(id)) {
            return this;
        }
        Person newPerson = new Person(this.name, this.birthYear);
        newPerson.id = id;
        return newPerson;
    }
    
    // Getters
    public Long getId() { return id; }
    public String getName() { return name; }
    public Integer getBirthYear() { return birthYear; }
    public List<ActedIn> getActedIn() { return actedIn; }
    public List<Movie> getDirected() { return directed; }
}

@RelationshipProperties
public class ActedIn {
    
    @Id @GeneratedValue
    private Long id;
    
    @TargetNode
    private final Movie movie;
    
    private final List<String> roles;
    
    private final Integer screenTime;  // in minutes
    
    public ActedIn(Movie movie, List<String> roles, Integer screenTime) {
        this.movie = movie;
        this.roles = roles;
        this.screenTime = screenTime;
    }
    
    // Getters
    public Long getId() { return id; }
    public Movie getMovie() { return movie; }
    public List<String> getRoles() { return roles; }
    public Integer getScreenTime() { return screenTime; }
}
```

### Repository Interfaces

```java
@Repository
public interface MovieRepository extends Neo4jRepository<Movie, String> {
    
    // Simple query derivation
    Optional<Movie> findByTitle(String title);
    
    List<Movie> findByReleaseYear(Integer year);
    
    List<Movie> findByReleaseYearBetween(Integer startYear, Integer endYear);
    
    List<Movie> findByGenresContaining(String genre);
    
    // Custom queries
    @Query("MATCH (m:Movie) WHERE m.title CONTAINS $keyword RETURN m")
    List<Movie> searchByTitle(@Param("keyword") String keyword);
    
    @Query("MATCH (m:Movie)-[:ACTED_IN]-(p:Person) " +
           "WHERE p.name = $actorName " +
           "RETURN m ORDER BY m.releaseYear DESC")
    List<Movie> findMoviesByActor(@Param("actorName") String actorName);
    
    @Query("MATCH (m:Movie)-[:DIRECTED]-(p:Person) " +
           "WHERE p.name = $directorName " +
           "RETURN m ORDER BY m.releaseYear")
    List<Movie> findMoviesByDirector(@Param("directorName") String directorName);
    
    @Query("MATCH (m:Movie) " +
           "WHERE $genre IN m.genres AND m.releaseYear >= $minYear " +
           "RETURN m ORDER BY m.releaseYear DESC")
    List<Movie> findRecentMoviesByGenre(@Param("genre") String genre, 
                                         @Param("minYear") Integer minYear);
    
    @Query("MATCH (m:Movie)<-[:ACTED_IN]-(p:Person) " +
           "WHERE m.imdbId = $imdbId " +
           "RETURN p.name AS name, p.birthYear AS birthYear")
    List<PersonProjection> findActorsByMovie(@Param("imdbId") String imdbId);
}

@Repository
public interface PersonRepository extends Neo4jRepository<Person, Long> {
    
    Optional<Person> findByName(String name);
    
    List<Person> findByBirthYearBetween(Integer startYear, Integer endYear);
    
    @Query("MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) " +
           "WHERE p.name = $name " +
           "RETURN m, r " +
           "ORDER BY m.releaseYear DESC")
    List<Movie> findMoviesActedInByPerson(@Param("name") String name);
    
    @Query("MATCH (p1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(p2:Person) " +
           "WHERE p1.name = $actorName AND p1 <> p2 " +
           "RETURN DISTINCT p2")
    List<Person> findCoActors(@Param("actorName") String actorName);
    
    @Query("MATCH (p:Person)-[:ACTED_IN]->(m:Movie) " +
           "WHERE p.name = $name " +
           "RETURN COUNT(m) AS movieCount")
    Integer countMoviesForPerson(@Param("name") String name);
}

// Projection interface
public interface PersonProjection {
    String getName();
    Integer getBirthYear();
}
```

### Service Layer

```java
@Service
public class MovieService {
    
    private final MovieRepository movieRepository;
    private final PersonRepository personRepository;
    
    public MovieService(MovieRepository movieRepository, 
                       PersonRepository personRepository) {
        this.movieRepository = movieRepository;
        this.personRepository = personRepository;
    }
    
    public MovieDTO getMovieByTitle(String title) {
        Movie movie = movieRepository.findByTitle(title)
            .orElseThrow(() -> new MovieNotFoundException(title));
        return mapToDTO(movie);
    }
    
    public List<MovieDTO> searchMoviesByKeyword(String keyword) {
        return movieRepository.searchByTitle(keyword).stream()
            .map(this::mapToDTO)
            .collect(Collectors.toList());
    }
    
    public List<MovieDTO> getMoviesByGenreAndYear(String genre, Integer minYear) {
        return movieRepository.findRecentMoviesByGenre(genre, minYear).stream()
            .map(this::mapToDTO)
            .collect(Collectors.toList());
    }
    
    public MovieDTO createMovie(CreateMovieRequest request) {
        Movie movie = new Movie(
            request.imdbId(),
            request.title(),
            request.description(),
            request.releaseYear(),
            request.genres()
        );
        
        Movie saved = movieRepository.save(movie);
        return mapToDTO(saved);
    }
    
    private MovieDTO mapToDTO(Movie movie) {
        return new MovieDTO(
            movie.getImdbId(),
            movie.getTitle(),
            movie.getDescription(),
            movie.getReleaseYear(),
            movie.getGenres(),
            extractActorNames(movie.getActors()),
            extractDirectorNames(movie.getDirectors())
        );
    }
    
    private List<String> extractActorNames(List<ActedIn> actors) {
        return actors.stream()
            .map(ActedIn::getMovie)
            .map(Movie::getTitle)
            .collect(Collectors.toList());
    }
    
    private List<String> extractDirectorNames(List<Person> directors) {
        return directors.stream()
            .map(Person::getName)
            .collect(Collectors.toList());
    }
}
```

### DTOs

```java
public record MovieDTO(
    String imdbId,
    String title,
    String description,
    Integer releaseYear,
    List<String> genres,
    List<String> actors,
    List<String> directors
) {}

public record CreateMovieRequest(
    String imdbId,
    String title,
    String description,
    Integer releaseYear,
    List<String> genres
) {
    public CreateMovieRequest {
        Objects.requireNonNull(imdbId, "IMDB ID is required");
        Objects.requireNonNull(title, "Title is required");
        if (releaseYear != null && releaseYear < 1888) {
            throw new IllegalArgumentException("Invalid release year");
        }
    }
}
```

## Social Network Example

### Entity Classes

```java
@Node("User")
public class User {
    
    @Id
    private final String username;
    
    private final String email;
    
    private final String fullName;
    
    private final LocalDateTime joinedAt;
    
    @Relationship(type = "FOLLOWS", direction = Direction.OUTGOING)
    private Set<User> following;
    
    @Relationship(type = "FOLLOWS", direction = Direction.INCOMING)
    private Set<User> followers;
    
    @Relationship(type = "POSTED", direction = Direction.OUTGOING)
    private List<Post> posts;
    
    public User(String username, String email, String fullName) {
        this.username = username;
        this.email = email;
        this.fullName = fullName;
        this.joinedAt = LocalDateTime.now();
        this.following = new HashSet<>();
        this.followers = new HashSet<>();
        this.posts = new ArrayList<>();
    }
    
    public void follow(User user) {
        this.following.add(user);
    }
    
    public void unfollow(User user) {
        this.following.remove(user);
    }
    
    // Getters
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public String getFullName() { return fullName; }
    public LocalDateTime getJoinedAt() { return joinedAt; }
    public Set<User> getFollowing() { return following; }
    public Set<User> getFollowers() { return followers; }
    public List<Post> getPosts() { return posts; }
}

@Node("Post")
public class Post {
    
    @Id @GeneratedValue
    private Long id;
    
    private final String content;
    
    private final LocalDateTime createdAt;
    
    private Integer likes;
    
    @Relationship(type = "POSTED", direction = Direction.INCOMING)
    private User author;
    
    @Relationship(type = "TAGGED", direction = Direction.OUTGOING)
    private List<Hashtag> hashtags;
    
    public Post(String content) {
        this.content = content;
        this.createdAt = LocalDateTime.now();
        this.likes = 0;
        this.hashtags = new ArrayList<>();
    }
    
    public void incrementLikes() {
        this.likes++;
    }
    
    // Getters omitted
}

@Node("Hashtag")
public class Hashtag {
    
    @Id
    private final String tag;
    
    private Integer usageCount;
    
    @Relationship(type = "TAGGED", direction = Direction.INCOMING)
    private List<Post> posts;
    
    public Hashtag(String tag) {
        this.tag = tag;
        this.usageCount = 0;
        this.posts = new ArrayList<>();
    }
    
    public void incrementUsage() {
        this.usageCount++;
    }
    
    // Getters omitted
}
```

### Repository with Advanced Queries

```java
@Repository
public interface UserRepository extends Neo4jRepository<User, String> {
    
    Optional<User> findByEmail(String email);
    
    @Query("MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User) " +
           "RETURN following")
    List<User> findFollowing(@Param("username") String username);
    
    @Query("MATCH (u:User {username: $username})<-[:FOLLOWS]-(follower:User) " +
           "RETURN follower")
    List<User> findFollowers(@Param("username") String username);
    
    @Query("MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual:User)" +
           "<-[:FOLLOWS]-(u2:User {username: $username2}) " +
           "RETURN mutual")
    List<User> findMutualFollowing(@Param("username1") String username1,
                                    @Param("username2") String username2);
    
    @Query("MATCH (u:User {username: $username})-[:FOLLOWS*2..3]->(suggested:User) " +
           "WHERE NOT (u)-[:FOLLOWS]->(suggested) AND u <> suggested " +
           "RETURN DISTINCT suggested " +
           "LIMIT $limit")
    List<User> findSuggestedUsers(@Param("username") String username,
                                   @Param("limit") Integer limit);
    
    @Query("MATCH (u:User {username: $username})-[:POSTED]->(p:Post) " +
           "RETURN COUNT(p)")
    Integer countPostsByUser(@Param("username") String username);
    
    @Query("MATCH (u:User {username: $username})-[:FOLLOWS]->(following)-[:POSTED]->(p:Post) " +
           "RETURN p ORDER BY p.createdAt DESC LIMIT $limit")
    List<Post> getFeed(@Param("username") String username,
                       @Param("limit") Integer limit);
}

@Repository
public interface PostRepository extends Neo4jRepository<Post, Long> {
    
    @Query("MATCH (p:Post)-[:TAGGED]->(h:Hashtag {tag: $tag}) " +
           "RETURN p ORDER BY p.createdAt DESC LIMIT $limit")
    List<Post> findByHashtag(@Param("tag") String tag,
                             @Param("limit") Integer limit);
    
    @Query("MATCH (p:Post) " +
           "WHERE p.createdAt >= $since " +
           "RETURN p ORDER BY p.likes DESC LIMIT $limit")
    List<Post> findTrendingPosts(@Param("since") LocalDateTime since,
                                  @Param("limit") Integer limit);
}
```

## E-Commerce Product Catalog

### Entity Classes

```java
@Node("Product")
public class Product {
    
    @Id
    private final String sku;
    
    private final String name;
    
    private final String description;
    
    private final BigDecimal price;
    
    @Relationship(type = "BELONGS_TO", direction = Direction.OUTGOING)
    private Category category;
    
    @Relationship(type = "SIMILAR_TO", direction = Direction.UNDIRECTED)
    private List<Product> similarProducts;
    
    @Relationship(type = "PURCHASED_WITH", direction = Direction.UNDIRECTED)
    private List<PurchasedWith> frequentlyBoughtTogether;
    
    public Product(String sku, String name, String description, BigDecimal price) {
        this.sku = sku;
        this.name = name;
        this.description = description;
        this.price = price;
        this.similarProducts = new ArrayList<>();
        this.frequentlyBoughtTogether = new ArrayList<>();
    }
    
    // Getters omitted
}

@Node("Category")
public class Category {
    
    @Id @GeneratedValue
    private Long id;
    
    private final String name;
    
    @Relationship(type = "PARENT_CATEGORY", direction = Direction.OUTGOING)
    private Category parent;
    
    @Relationship(type = "PARENT_CATEGORY", direction = Direction.INCOMING)
    private List<Category> subcategories;
    
    public Category(String name) {
        this.name = name;
        this.subcategories = new ArrayList<>();
    }
    
    // Getters omitted
}

@RelationshipProperties
public class PurchasedWith {
    
    @Id @GeneratedValue
    private Long id;
    
    @TargetNode
    private final Product product;
    
    private Integer purchaseCount;
    
    public PurchasedWith(Product product) {
        this.product = product;
        this.purchaseCount = 1;
    }
    
    public void incrementCount() {
        this.purchaseCount++;
    }
    
    // Getters omitted
}
```

### Repository with Recommendation Queries

```java
@Repository
public interface ProductRepository extends Neo4jRepository<Product, String> {
    
    List<Product> findByNameContaining(String keyword);
    
    List<Product> findByPriceBetween(BigDecimal minPrice, BigDecimal maxPrice);
    
    @Query("MATCH (p:Product)-[:BELONGS_TO]->(c:Category {name: $categoryName}) " +
           "RETURN p ORDER BY p.price")
    List<Product> findByCategoryName(@Param("categoryName") String categoryName);
    
    @Query("MATCH (p:Product)-[:BELONGS_TO]->(c:Category)" +
           "-[:PARENT_CATEGORY*0..]->(parent:Category {name: $parentCategory}) " +
           "RETURN p")
    List<Product> findByParentCategory(@Param("parentCategory") String parentCategory);
    
    @Query("MATCH (p:Product {sku: $sku})-[:SIMILAR_TO]->(similar:Product) " +
           "RETURN similar LIMIT $limit")
    List<Product> findSimilarProducts(@Param("sku") String sku,
                                      @Param("limit") Integer limit);
    
    @Query("MATCH (p:Product {sku: $sku})-[r:PURCHASED_WITH]->(related:Product) " +
           "RETURN related ORDER BY r.purchaseCount DESC LIMIT $limit")
    List<Product> findFrequentlyBoughtTogether(@Param("sku") String sku,
                                                @Param("limit") Integer limit);
    
    @Query("MATCH (p1:Product {sku: $sku1})<-[:PURCHASED_WITH]-(p2:Product)" +
           "-[:PURCHASED_WITH]->(recommended:Product) " +
           "WHERE recommended.sku <> $sku1 " +
           "RETURN recommended, COUNT(*) AS score " +
           "ORDER BY score DESC LIMIT $limit")
    List<Product> findRecommendedProducts(@Param("sku1") String sku1,
                                          @Param("limit") Integer limit);
}
```

## Custom Query Examples

### Pagination and Sorting

```java
@Repository
public interface MovieRepository extends Neo4jRepository<Movie, String> {
    
    // Using Pageable
    Page<Movie> findByGenresContaining(String genre, Pageable pageable);
    
    // Using Sort
    List<Movie> findByReleaseYearBetween(Integer start, Integer end, Sort sort);
    
    // Custom query with pagination
    @Query("MATCH (m:Movie) WHERE $genre IN m.genres " +
           "RETURN m ORDER BY m.releaseYear DESC SKIP $skip LIMIT $limit")
    List<Movie> findByGenrePaginated(@Param("genre") String genre,
                                     @Param("skip") Integer skip,
                                     @Param("limit") Integer limit);
}

// Usage
public class MovieService {
    
    public Page<MovieDTO> getMoviesByGenre(String genre, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, 
                                          Sort.by("releaseYear").descending());
        return movieRepository.findByGenresContaining(genre, pageable)
            .map(this::mapToDTO);
    }
}
```

### Aggregation Queries

```java
@Repository
public interface StatisticsRepository extends Neo4jRepository<Movie, String> {
    
    @Query("MATCH (m:Movie) WHERE m.releaseYear = $year " +
           "RETURN COUNT(m) AS count")
    Long countMoviesByYear(@Param("year") Integer year);
    
    @Query("MATCH (m:Movie) " +
           "RETURN m.releaseYear AS year, COUNT(m) AS count " +
           "ORDER BY year DESC")
    List<YearStatistics> getMovieCountByYear();
    
    @Query("MATCH (p:Person)-[:ACTED_IN]->(m:Movie) " +
           "RETURN p.name AS actor, COUNT(m) AS movieCount " +
           "ORDER BY movieCount DESC LIMIT $limit")
    List<ActorStatistics> getMostProlificActors(@Param("limit") Integer limit);
    
    @Query("MATCH (m:Movie) " +
           "RETURN AVG(m.releaseYear) AS averageYear, " +
           "MIN(m.releaseYear) AS oldestYear, " +
           "MAX(m.releaseYear) AS newestYear")
    MovieYearStatistics getYearStatistics();
}

// Projection interfaces
public interface YearStatistics {
    Integer getYear();
    Long getCount();
}

public interface ActorStatistics {
    String getActor();
    Long getMovieCount();
}

public interface MovieYearStatistics {
    Double getAverageYear();
    Integer getOldestYear();
    Integer getNewestYear();
}
```

## Reactive Neo4j Examples

### Reactive Repository

```java
@Repository
public interface ReactiveMovieRepository 
        extends ReactiveNeo4jRepository<Movie, String> {
    
    Mono<Movie> findByTitle(String title);
    
    Flux<Movie> findByReleaseYear(Integer year);
    
    @Query("MATCH (m:Movie) WHERE m.title CONTAINS $keyword RETURN m")
    Flux<Movie> searchByTitle(@Param("keyword") String keyword);
    
    @Query("MATCH (m:Movie)-[:ACTED_IN]-(p:Person {name: $actorName}) " +
           "RETURN m ORDER BY m.releaseYear DESC")
    Flux<Movie> findMoviesByActor(@Param("actorName") String actorName);
}
```

### Reactive Service

```java
@Service
public class ReactiveMovieService {
    
    private final ReactiveMovieRepository movieRepository;
    
    public ReactiveMovieService(ReactiveMovieRepository movieRepository) {
        this.movieRepository = movieRepository;
    }
    
    public Mono<MovieDTO> getMovieByTitle(String title) {
        return movieRepository.findByTitle(title)
            .map(this::mapToDTO)
            .switchIfEmpty(Mono.error(
                new MovieNotFoundException("Movie not found: " + title)));
    }
    
    public Flux<MovieDTO> searchMovies(String keyword) {
        return movieRepository.searchByTitle(keyword)
            .map(this::mapToDTO);
    }
    
    public Mono<MovieDTO> createMovie(CreateMovieRequest request) {
        Movie movie = new Movie(
            request.imdbId(),
            request.title(),
            request.description(),
            request.releaseYear(),
            request.genres()
        );
        
        return movieRepository.save(movie)
            .map(this::mapToDTO);
    }
    
    private MovieDTO mapToDTO(Movie movie) {
        return new MovieDTO(
            movie.getImdbId(),
            movie.getTitle(),
            movie.getDescription(),
            movie.getReleaseYear(),
            movie.getGenres(),
            List.of(),
            List.of()
        );
    }
}
```

### Reactive Controller

```java
@RestController
@RequestMapping("/api/movies")
public class ReactiveMovieController {
    
    private final ReactiveMovieService movieService;
    
    public ReactiveMovieController(ReactiveMovieService movieService) {
        this.movieService = movieService;
    }
    
    @GetMapping("/{title}")
    public Mono<MovieDTO> getMovie(@PathVariable String title) {
        return movieService.getMovieByTitle(title);
    }
    
    @GetMapping("/search")
    public Flux<MovieDTO> searchMovies(@RequestParam String keyword) {
        return movieService.searchMovies(keyword);
    }
    
    @PostMapping
    public Mono<MovieDTO> createMovie(@RequestBody CreateMovieRequest request) {
        return movieService.createMovie(request);
    }
}
```

## Testing Examples

### Integration Test with Neo4j Harness

```java
@DataNeo4jTest
class MovieRepositoryIntegrationTest {

    private static Neo4j embeddedNeo4j;

    @BeforeAll
    static void initializeNeo4j() {
        embeddedNeo4j = Neo4jBuilders.newInProcessBuilder()
            .withDisabledServer()
            .withFixture("""
                CREATE (m1:Movie {
                    imdbId: 'tt0120737',
                    title: 'The Lord of the Rings: The Fellowship of the Ring',
                    tagline: 'One Ring to rule them all',
                    releaseYear: 2001,
                    genres: ['Adventure', 'Drama', 'Fantasy']
                })
                CREATE (m2:Movie {
                    imdbId: 'tt0167261',
                    title: 'The Lord of the Rings: The Two Towers',
                    tagline: 'The journey continues',
                    releaseYear: 2002,
                    genres: ['Adventure', 'Drama', 'Fantasy']
                })
                CREATE (p:Person {
                    name: 'Peter Jackson',
                    birthYear: 1961
                })
                CREATE (p)-[:DIRECTED]->(m1)
                CREATE (p)-[:DIRECTED]->(m2)
                """)
            .build();
    }

    @AfterAll
    static void stopNeo4j() {
        embeddedNeo4j.close();
    }

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.neo4j.uri", embeddedNeo4j::boltURI);
        registry.add("spring.neo4j.authentication.username", () -> "neo4j");
        registry.add("spring.neo4j.authentication.password", () -> "null");
    }

    @Autowired
    private MovieRepository movieRepository;

    @Test
    void shouldFindMovieByTitle() {
        Optional<Movie> movie = movieRepository.findByTitle(
            "The Lord of the Rings: The Fellowship of the Ring");
        
        assertThat(movie).isPresent();
        assertThat(movie.get().getImdbId()).isEqualTo("tt0120737");
        assertThat(movie.get().getReleaseYear()).isEqualTo(2001);
    }

    @Test
    void shouldFindMoviesByYear() {
        List<Movie> movies = movieRepository.findByReleaseYear(2001);
        
        assertThat(movies).hasSize(1);
        assertThat(movies.get(0).getTitle())
            .contains("Fellowship of the Ring");
    }

    @Test
    void shouldFindMoviesByGenre() {
        List<Movie> movies = movieRepository.findByGenresContaining("Fantasy");
        
        assertThat(movies).hasSize(2);
    }

    @Test
    void shouldSearchMoviesByKeyword() {
        List<Movie> movies = movieRepository.searchByTitle("Rings");
        
        assertThat(movies).hasSize(2);
    }
}
```

### Service Layer Test with Mocks

```java
@ExtendWith(MockitoExtension.class)
class MovieServiceTest {

    @Mock
    private MovieRepository movieRepository;

    @Mock
    private PersonRepository personRepository;

    @InjectMocks
    private MovieService movieService;

    @Test
    void shouldGetMovieByTitle() {
        // Given
        String title = "The Matrix";
        Movie movie = new Movie(
            "tt0133093",
            title,
            "A computer hacker learns about the true nature of reality",
            1999,
            List.of("Action", "Sci-Fi")
        );
        
        when(movieRepository.findByTitle(title))
            .thenReturn(Optional.of(movie));

        // When
        MovieDTO result = movieService.getMovieByTitle(title);

        // Then
        assertThat(result.title()).isEqualTo(title);
        assertThat(result.releaseYear()).isEqualTo(1999);
        verify(movieRepository).findByTitle(title);
    }

    @Test
    void shouldThrowExceptionWhenMovieNotFound() {
        // Given
        String title = "Non-existent Movie";
        when(movieRepository.findByTitle(title))
            .thenReturn(Optional.empty());

        // When/Then
        assertThatThrownBy(() -> movieService.getMovieByTitle(title))
            .isInstanceOf(MovieNotFoundException.class)
            .hasMessageContaining(title);
    }

    @Test
    void shouldCreateMovie() {
        // Given
        CreateMovieRequest request = new CreateMovieRequest(
            "tt1234567",
            "New Movie",
            "A new movie description",
            2024,
            List.of("Action")
        );
        
        Movie movie = new Movie(
            request.imdbId(),
            request.title(),
            request.description(),
            request.releaseYear(),
            request.genres()
        );
        
        when(movieRepository.save(any(Movie.class)))
            .thenReturn(movie);

        // When
        MovieDTO result = movieService.createMovie(request);

        // Then
        assertThat(result.imdbId()).isEqualTo(request.imdbId());
        assertThat(result.title()).isEqualTo(request.title());
        verify(movieRepository).save(any(Movie.class));
    }
}
```

### Reactive Test Example

```java
@DataNeo4jTest
class ReactiveMovieRepositoryTest {

    private static Neo4j embeddedNeo4j;

    @BeforeAll
    static void initializeNeo4j() {
        embeddedNeo4j = Neo4jBuilders.newInProcessBuilder()
            .withDisabledServer()
            .withFixture("CREATE (m:Movie {imdbId: 'tt0133093', " +
                        "title: 'The Matrix', releaseYear: 1999})")
            .build();
    }

    @AfterAll
    static void stopNeo4j() {
        embeddedNeo4j.close();
    }

    @DynamicPropertySource
    static void neo4jProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.neo4j.uri", embeddedNeo4j::boltURI);
        registry.add("spring.neo4j.authentication.username", () -> "neo4j");
        registry.add("spring.neo4j.authentication.password", () -> "null");
    }

    @Autowired
    private ReactiveMovieRepository reactiveMovieRepository;

    @Test
    void shouldFindMovieByTitle() {
        StepVerifier.create(reactiveMovieRepository.findByTitle("The Matrix"))
            .assertNext(movie -> {
                assertThat(movie.getImdbId()).isEqualTo("tt0133093");
                assertThat(movie.getReleaseYear()).isEqualTo(1999);
            })
            .verifyComplete();
    }

    @Test
    void shouldReturnEmptyWhenMovieNotFound() {
        StepVerifier.create(reactiveMovieRepository.findByTitle("Non-existent"))
            .verifyComplete();
    }

    @Test
    void shouldFindMoviesByYear() {
        StepVerifier.create(reactiveMovieRepository.findByReleaseYear(1999))
            .expectNextCount(1)
            .verifyComplete();
    }
}
```

These examples demonstrate real-world patterns for using Spring Data Neo4j, including entity modeling, repository design, service layer implementation, and comprehensive testing strategies.
