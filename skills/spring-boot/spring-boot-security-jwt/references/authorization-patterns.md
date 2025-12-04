# Authorization Patterns and Strategies

## Role-Based Access Control (RBAC)

### Hierarchical Role Structure
```java
@Entity
@Table(name = "roles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Role {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

    private String description;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "role_hierarchy",
        joinColumns = @JoinColumn(name = "child_role_id"),
        inverseJoinColumns = @JoinColumn(name = "parent_role_id")
    )
    private Set<Role> parentRoles = new HashSet<>();

    @ManyToMany(mappedBy = "parentRoles")
    private Set<Role> childRoles = new HashSet<>();

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "role_permissions",
        joinColumns = @JoinColumn(name = "role_id"),
        inverseJoinColumns = @JoinColumn(name = "permission_id")
    )
    private Set<Permission> permissions = new HashSet<>();

    public Set<Permission> getAllPermissions() {
        Set<Permission> allPermissions = new HashSet<>(permissions);

        // Recursively collect permissions from parent roles
        for (Role parentRole : parentRoles) {
            allPermissions.addAll(parentRole.getAllPermissions());
        }

        return allPermissions;
    }

    public boolean hasPermission(String permissionName) {
        return getAllPermissions().stream()
            .anyMatch(permission -> permission.getName().equals(permissionName));
    }
}
```

### Custom Role Hierarchy Voter
```java
@Component
public class RoleHierarchyVoter implements AccessDecisionVoter<Object> {

    private final RoleHierarchy roleHierarchy;

    public RoleHierarchyVoter(RoleHierarchy roleHierarchy) {
        this.roleHierarchy = roleHierarchy;
    }

    @Override
    public boolean supports(ConfigAttribute attribute) {
        return attribute.getAttribute() != null &&
               attribute.getAttribute().startsWith("ROLE_");
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return true;
    }

    @Override
    public int vote(Authentication authentication, Object object,
                   Collection<ConfigAttribute> attributes) {

        Collection<? extends GrantedAuthority> authorities = roleHierarchy
            .getReachableGrantedAuthorities(authentication.getAuthorities());

        for (ConfigAttribute attribute : attributes) {
            if (authorities.contains(new SimpleGrantedAuthority(attribute.getAttribute()))) {
                return ACCESS_GRANTED;
            }
        }

        return ACCESS_ABSTAIN;
    }
}

@Configuration
public class RoleHierarchyConfig {

    @Bean
    public RoleHierarchy roleHierarchy() {
        RoleHierarchyImpl roleHierarchy = new RoleHierarchyImpl();
        String hierarchy =
            "ROLE_ADMIN > ROLE_MANAGER\n" +
            "ROLE_MANAGER > ROLE_USER\n" +
            "ROLE_MANAGER > ROLE_SUPPORT\n" +
            "ROLE_SUPPORT > ROLE_READONLY";
        roleHierarchy.setHierarchy(hierarchy);
        return roleHierarchy;
    }
}
```

### Method-Level Security with Roles
```java
@Service
@PreAuthorize("hasRole('USER')")
public class DocumentService {

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteAllDocuments() {
        // Only administrators can delete all documents
    }

    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public void approveDocument(Long documentId) {
        // Admins and managers can approve documents
    }

    @PreAuthorize("hasRole('USER')")
    public List<Document> getMyDocuments() {
        // Regular users can view their own documents
    }

    @PreAuthorize("hasRole('MANAGER')")
    @PostAuthorize("returnObject.owner.id == authentication.principal.id or hasRole('ADMIN')")
    public Document getDocumentForApproval(Long documentId) {
        // Managers can view documents for approval, admins can view any
        return documentRepository.findById(documentId)
            .orElseThrow(() -> new DocumentNotFoundException(documentId));
    }
}
```

## Permission-Based Access Control

### Permission Entity with Resource Types
```java
@Entity
@Table(name = "permissions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Permission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ResourceType resourceType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ActionType action;

    // Permission templates for dynamic permissions
    private String template;

    // Conditions for conditional permissions
    @Lob
    private String conditions;
}

public enum ResourceType {
    USER("user", "User Management"),
    DOCUMENT("document", "Document Management"),
    ORDER("order", "Order Processing"),
    PRODUCT("product", "Product Catalog"),
    INVOICE("invoice", "Invoice Management"),
    REPORT("report", "Reporting"),
    SYSTEM("system", "System Administration");

    private final String code;
    private final String description;

    ResourceType(String code, String description) {
        this.code = code;
        this.description = description;
    }
}

public enum ActionType {
    CREATE("create"),
    READ("read"),
    UPDATE("update"),
    DELETE("delete"),
    APPROVE("approve"),
    REJECT("reject"),
    EXPORT("export"),
    IMPORT("import");

    private final String code;

    ActionType(String code) {
        this.code = code;
    }
}
```

### Custom Permission Evaluator
```java
@Component("permissionEvaluator")
public class CustomPermissionEvaluator implements PermissionEvaluator {

    private final PermissionService permissionService;

    public boolean hasPermission(Authentication authentication,
            Object targetDomainObject, Object permission) {

        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        User user = (User) authentication.getPrincipal();
        String permissionName = permission.toString();

        // Check direct permissions
        if (user.hasPermission(permissionName)) {
            return true;
        }

        // Check resource-specific permissions
        if (targetDomainObject != null) {
            return checkResourcePermission(user, targetDomainObject, permissionName);
        }

        return false;
    }

    @Override
    public boolean hasPermission(Authentication authentication,
            Serializable targetId, String targetType, Object permission) {

        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        User user = (User) authentication.getPrincipal();
        String permissionName = permission.toString();

        return permissionService.hasResourcePermission(user, targetId, targetType, permissionName);
    }

    private boolean checkResourcePermission(User user, Object resource, String permission) {
        // Extract resource information
        String resourceType = extractResourceType(resource);
        Serializable resourceId = extractResourceId(resource);

        // Check ownership
        if (isOwner(user, resource) && hasOwnershipPermission(permission)) {
            return true;
        }

        // Check department/organizational permissions
        if (isInSameDepartment(user, resource) && hasDepartmentPermission(permission)) {
            return true;
        }

        // Check global permissions
        return permissionService.hasGlobalPermission(user, resourceType, permission);
    }

    private boolean hasOwnershipPermission(String permission) {
        return permission.endsWith("_OWN") || permission.endsWith("_MY");
    }

    private boolean hasDepartmentPermission(String permission) {
        return permission.endsWith("_DEPT") || permission.endsWith("_ORG");
    }
}
```

### Dynamic Permission Builder
```java
@Service
public class PermissionBuilderService {

    public Set<String> buildPermissions(User user) {
        Set<String> permissions = new HashSet<>();

        // Role-based permissions
        user.getRoles().forEach(role -> {
            permissions.add("ROLE_" + role.getName());
            role.getPermissions().forEach(permission -> {
                permissions.add(permission.getName());
            });
        });

        // User-specific permissions
        user.getUserPermissions().forEach(userPermission -> {
            if (isPermissionValid(userPermission)) {
                permissions.add(buildPermissionString(userPermission));
            }
        });

        // Dynamic permissions based on user attributes
        addDynamicPermissions(user, permissions);

        return permissions;
    }

    private void addDynamicPermissions(User user, Set<String> permissions) {
        // Department-based permissions
        if (user.getDepartment() != null) {
            permissions.add("DEPT_" + user.getDepartment().getCode() + "_READ");
        }

        // Location-based permissions
        if (user.getLocation() != null) {
            permissions.add("LOCATION_" + user.getLocation().getCode() + "_ACCESS");
        }

        // Project-based permissions
        user.getProjectMemberships().forEach(membership -> {
            permissions.add("PROJECT_" + membership.getProject().getId() + "_MEMBER");
            if (membership.getRole() == ProjectRole.MANAGER) {
                permissions.add("PROJECT_" + membership.getProject().getId() + "_MANAGER");
            }
        });
    }

    private String buildPermissionString(UserPermission userPermission) {
        return String.format("%s_%s_%s",
            userPermission.getResourceType(),
            userPermission.getAction(),
            userPermission.getScope());
    }
}
```

## Attribute-Based Access Control (ABAC)

### Policy-Based Authorization
```java
@Component
public class PolicyBasedAccessDecisionManager implements AccessDecisionManager {

    private final PolicyRepository policyRepository;
    private final PolicyEvaluationService evaluationService;

    @Override
    public void decide(Authentication authentication, Object object,
                       Collection<ConfigAttribute> configAttributes) throws AccessDeniedException {

        if (configAttributes.isEmpty()) {
            return;
        }

        for (ConfigAttribute attribute : configAttributes) {
            if (supports(attribute)) {
                String policyName = attribute.getAttribute();
                Policy policy = policyRepository.findByName(policyName)
                    .orElseThrow(() -> new PolicyNotFoundException(policyName));

                if (!evaluationService.evaluate(policy, authentication, object)) {
                    throw new AccessDeniedException(
                        "Access denied by policy: " + policyName);
                }
            }
        }
    }

    @Override
    public boolean supports(ConfigAttribute attribute) {
        return attribute.getAttribute() != null &&
               attribute.getAttribute().startsWith("POLICY_");
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return true;
    }
}

@Service
public class PolicyEvaluationService {

    public boolean evaluate(Policy policy, Authentication authentication, Object resource) {
        // Build evaluation context
        EvaluationContext context = EvaluationContext.builder()
            .subject(extractSubjectInfo(authentication))
            .resource(extractResourceInfo(resource))
            .environment(extractEnvironmentInfo())
            .build();

        // Evaluate policy rules
        return policy.getRules().stream()
            .allMatch(rule -> evaluateRule(rule, context));
    }

    private boolean evaluateRule(PolicyRule rule, EvaluationContext context) {
        // Implement rule evaluation logic using SPEL or custom evaluator
        StandardEvaluationContext spe1Context = new StandardEvaluationContext(context);
        ExpressionParser parser = new SpelExpressionParser();
        Expression expression = parser.parseExpression(rule.getCondition());

        return expression.getValue(spe1Context, Boolean.class);
    }
}
```

### ABAC Policy Definitions
```java
@Entity
@Table(name = "policies")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Policy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String name;

    private String description;

    @Enumerated(EnumType.STRING)
    private PolicyEffect effect; // PERMIT or DENY

    @OneToMany(mappedBy = "policy", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("priority ASC")
    private List<PolicyRule> rules = new ArrayList<>();

    @Column(columnDefinition = "TEXT")
    private String targetCondition; // SPEL expression for target matching

    public enum PolicyEffect {
        PERMIT, DENY
    }
}

@Entity
@Table(name = "policy_rules")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PolicyRule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "policy_id")
    private Policy policy;

    private String description;

    @Column(columnDefinition = "TEXT")
    private String condition; // SPEL expression

    private int priority;

    @Enumerated(EnumType.STRING)
    private RuleType type;

    public enum RuleType {
        SUBJECT, RESOURCE, ENVIRONMENT, COMPOSITE
    }
}
```

## Time-Based Access Control

### Time-Restricted Permissions
```java
@Component
public class TimeBasedPermissionEvaluator {

    public boolean hasTimeBasedPermission(Authentication authentication,
            Object permission, Instant accessTime) {

        User user = (User) authentication.getPrincipal();

        // Check business hours
        if (!isWithinBusinessHours(accessTime)) {
            return user.hasPermission("AFTER_HOURS_ACCESS");
        }

        // Check time-based restrictions
        return user.getTimeRestrictions().stream()
            .noneMatch(restriction -> isRestricted(restriction, accessTime));
    }

    private boolean isWithinBusinessHours(Instant accessTime) {
        ZonedDateTime zdt = accessTime.atZone(ZoneId.systemDefault());
        DayOfWeek dayOfWeek = zdt.getDayOfWeek();
        int hour = zdt.getHour();

        // Monday to Friday, 9 AM to 6 PM
        return dayOfWeek != DayOfWeek.SATURDAY &&
               dayOfWeek != DayOfWeek.SUNDAY &&
               hour >= 9 && hour < 18;
    }
}

@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@PreAuthorize("@timeBasedPermissionEvaluator.hasTimeBasedPermission(authentication, 'READ', T(java.time.Instant).now())")
public @interface TimeRestrictedAccess {
    String value() default "READ";
}
```

### Expiration-Based Access
```java
@Entity
@Table(name = "access_grants")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AccessGrant {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    private User user;

    @Column(nullable = false)
    private String resource;

    @Column(nullable = false)
    private String permission;

    @Column(nullable = false)
    private Instant grantedAt;

    @Column(nullable = false)
    private Instant expiresAt;

    private String grantedBy;

    @Column(columnDefinition = "TEXT")
    private String reason;

    public boolean isValid() {
        return Instant.now().isBefore(expiresAt);
    }
}

@Service
public class AccessGrantService {

    @Transactional
    public AccessGrant grantTemporaryAccess(User user, String resource,
            String permission, Duration duration, String grantedBy, String reason) {

        AccessGrant grant = AccessGrant.builder()
            .user(user)
            .resource(resource)
            .permission(permission)
            .grantedAt(Instant.now())
            .expiresAt(Instant.now().plus(duration))
            .grantedBy(grantedBy)
            .reason(reason)
            .build();

        return accessGrantRepository.save(grant);
    }

    public boolean hasTemporaryAccess(User user, String resource, String permission) {
        return accessGrantRepository
            .findByUserAndResourceAndPermissionAndExpiresAtAfter(
                user, resource, permission, Instant.now())
            .isPresent();
    }
}
```

## Location-Based Access Control

### IP Address Restrictions
```java
@Component
public class LocationBasedAccessControl {

    private final IpRangeRepository ipRangeRepository;

    public boolean isAccessAllowedFromIp(Authentication authentication, String ipAddress) {
        User user = (User) authentication.getPrincipal();

        // Check if user has location restrictions
        if (!user.hasLocationRestrictions()) {
            return true;
        }

        // Check IP against allowed ranges
        List<IpRange> allowedRanges = ipRangeRepository.findByUser(user);
        return allowedRanges.stream()
            .anyMatch(range -> isInRange(ipAddress, range));
    }

    private boolean isInRange(String ipAddress, IpRange ipRange) {
        try {
            InetAddress address = InetAddress.getByName(ipAddress);
            InetAddress networkAddress = InetAddress.getByName(ipRange.getNetworkAddress());
            int prefixLength = ipRange.getPrefixLength();

            byte[] addressBytes = address.getAddress();
            byte[] networkBytes = networkAddress.getAddress();

            int fullPrefix = prefixLength / 8;
            int partialPrefix = prefixLength % 8;

            for (int i = 0; i < fullPrefix; i++) {
                if (addressBytes[i] != networkBytes[i]) {
                    return false;
                }
            }

            if (partialPrefix > 0) {
                byte mask = (byte) (0xFF << (8 - partialPrefix));
                if ((addressBytes[fullPrefix] & mask) != (networkBytes[fullPrefix] & mask)) {
                    return false;
                }
            }

            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

## Organizational Access Control

### Department-Based Security
```java
@Entity
@Table(name = "departments")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Department {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String code;

    private String name;

    private String description;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_department_id")
    private Department parentDepartment;

    @OneToMany(mappedBy = "parentDepartment")
    private List<Department> childDepartments = new ArrayList<>();

    private int level;

    // Get all child departments recursively
    public List<Department> getAllChildDepartments() {
        List<Department> allChildren = new ArrayList<>();
        for (Department child : childDepartments) {
            allChildren.add(child);
            allChildren.addAll(child.getAllChildDepartments());
        }
        return allChildren;
    }
}

@Service
public class DepartmentSecurityService {

    public boolean canAccessDepartmentData(User user, Department targetDepartment) {
        // Users can access their own department
        if (user.getDepartment().equals(targetDepartment)) {
            return true;
        }

        // Check parent department access
        if (canAccessParentDepartment(user, targetDepartment)) {
            return true;
        }

        // Check child department access
        if (canAccessChildDepartments(user, targetDepartment)) {
            return true;
        }

        return false;
    }

    private boolean canAccessParentDepartment(User user, Department department) {
        Department current = department.getParentDepartment();
        while (current != null) {
            if (current.equals(user.getDepartment()) &&
                user.hasPermission("DEPT_CHILDREN_ACCESS")) {
                return true;
            }
            current = current.getParentDepartment();
        }
        return false;
    }

    private boolean canAccessChildDepartments(User user, Department department) {
        return user.getDepartment().getAllChildDepartments().contains(department) &&
               user.hasPermission("DEPT_PARENT_ACCESS");
    }
}
```