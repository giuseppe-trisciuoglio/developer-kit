package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.model.$entity;
import $package.domain.repository.${entity}Repository;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

@Service$service_annotations_block
@Transactional
public class Create${entity}Service {

    private final ${entity}Repository repository;

    public Create${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public $dto_response create($dto_request request) {
        $entity agg = $entity.create($request_all_args);
        agg = repository.save(agg);
        return new $dto_response($response_from_agg_args);
    }
}
