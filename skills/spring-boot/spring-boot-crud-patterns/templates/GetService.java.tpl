package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.repository.${entity}Repository;
import $package.presentation.dto.$dto_response;

@Service
$service_annotations
@Transactional(readOnly = true)
public class Get${entity}Service {

    private final ${entity}Repository repository;

    public Get${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public $dto_response get($id_type $id_name) {
        return repository.findById($id_name)
            .map(a -> new $dto_response($list_map_response_args))
            .orElseThrow(() -> new org.springframework.web.server.ResponseStatusException(org.springframework.http.HttpStatus.NOT_FOUND));
    }
}
