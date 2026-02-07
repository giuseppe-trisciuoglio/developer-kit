package $package.domain.service;

import java.util.List;
import java.util.Optional;
$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.model.$entity;
import $package.domain.repository.${entity}Repository;

@Service$service_annotations_block
@Transactional
public class ${entity}Service {

    private final ${entity}Repository repository;

    $domain_service_constructor

    public $entity save($entity aggregate) {
        return repository.save(aggregate);
    }

    public Optional<$entity> findById($id_type $id_name) {
        return repository.findById($id_name);
    }

    public List<$entity> findAll(int page, int size) {
        return repository.findAll(page, size);
    }

    public void deleteById($id_type $id_name) {
        repository.deleteById($id_name);
    }

    public boolean existsById($id_type $id_name) {
        return repository.existsById($id_name);
    }

    public long count() {
        return repository.count();
    }
}
