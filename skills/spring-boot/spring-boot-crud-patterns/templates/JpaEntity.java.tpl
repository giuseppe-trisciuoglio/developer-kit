package $package.infrastructure.persistence;

import jakarta.persistence.*;
$extra_imports

@Entity
@Table(name = "$table_name")
public class ${entity}Entity {

$jpa_fields_decls

    protected ${entity}Entity() { /* for JPA */ }

    public ${entity}Entity($jpa_ctor_params) {
$jpa_assigns
    }

$jpa_getters_setters
}
