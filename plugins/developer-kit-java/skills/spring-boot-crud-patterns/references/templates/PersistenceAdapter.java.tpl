package $package.infrastructure.persistence;

$lombok_common_imports
import java.util.Optional;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.data.domain.PageRequest;

import $package.domain.model.$entity;
import $package.domain.repository.${entity}Repository;
import org.springframework.stereotype.Component;

@Component$adapter_annotations_block
public class ${entity}RepositoryAdapter implements ${entity}Repository {

    private final ${entity}JpaRepository jpa;

    $adapter_constructor

    @Override
    public $entity save($entity a) {
        ${entity}Entity e = new ${entity}Entity($adapter_to_entity_args);
        e = jpa.save(e);
        return $entity.create($adapter_to_domain_args);
    }

    @Override
    public Optional<$entity> findById($id_type $id_name) {
        return jpa.findById($id_name).map(e -> $entity.create($adapter_to_domain_args));
    }

    @Override
    public List<$entity> findAll(int page, int size) {
        return jpa.findAll(PageRequest.of(page, size))
                  .stream()
                  .map(e -> $entity.create($adapter_to_domain_args))
                  .collect(Collectors.toList());
    }

    @Override
    public void deleteById($id_type $id_name) {
        jpa.deleteById($id_name);
    }

    @Override
    public boolean existsById($id_type $id_name) {
        return jpa.existsById($id_name);
    }

    @Override
    public long count() {
        return jpa.count();
    }
}
