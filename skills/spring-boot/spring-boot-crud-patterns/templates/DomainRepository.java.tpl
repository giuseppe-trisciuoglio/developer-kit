package $package.domain.repository;

import java.util.Optional;
import java.util.List;
import $package.domain.model.$entity;

public interface ${entity}Repository {
    $entity save($entity aggregate);
    Optional<$entity> findById($id_type $id_name);
    List<$entity> findAll(int page, int size);
    void deleteById($id_type $id_name);
    boolean existsById($id_type $id_name);
    long count();
}
