package $package.infrastructure.persistence;

import jakarta.persistence.*;
$extra_imports
$entity_lombok_imports

@Entity
@Table(name = "$table_name")$entity_lombok_annotations_block
public class ${entity}Entity {

$jpa_fields_decls

    protected ${entity}Entity() { /* for JPA */ }

    public ${entity}Entity($jpa_ctor_params) {
$jpa_assigns
    }

$jpa_getters_setters
}
