package $package.infrastructure.persistence;

import jakarta.persistence.*;
$extra_imports
$lombok_model_imports
import lombok.NoArgsConstructor;

@Entity
@Table(name = "$table_name")
@Getter
@Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ${entity}Entity {

$jpa_fields_decls

    protected ${entity}Entity() { /* for JPA */ }

    // Full constructor (optional, can be removed if not needed)
    public ${entity}Entity($jpa_ctor_params) {
$jpa_assigns
    }

    // Lombok generates getters and setters automatically
}
