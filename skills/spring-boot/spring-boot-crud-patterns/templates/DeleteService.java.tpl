package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.repository.${entity}Repository;

@Service
$service_annotations
@Transactional
public class Delete${entity}Service {

    private final ${entity}Repository repository;

    public Delete${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public void delete($id_type $id_name) {
        repository.deleteById($id_name);
    }
}
