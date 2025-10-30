package $package.domain.model;

$lombok_model_imports
$extra_imports

$model_annotations
public class $entity {
$domain_fields_decls

    private $entity($domain_ctor_params) {
$domain_assigns
    }

    public static $entity create($domain_ctor_params) {
        // TODO: add invariant checks
        return new $entity($all_names_csv);
    }

$domain_getters
}
