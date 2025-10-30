package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.model.$entity;
import $package.domain.repository.${entity}Repository;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

@Service
$service_annotations
@Transactional
public class Update${entity}Service {

    private final ${entity}Repository repository;

    public Update${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public $dto_response update($id_type $id_name, $dto_request request) {
        $entity updated = $entity.create($update_create_args);
        updated = repository.save(updated);
        return new $dto_response($response_from_agg_args);
    }
}
