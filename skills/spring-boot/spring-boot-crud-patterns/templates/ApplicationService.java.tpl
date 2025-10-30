package $package.application.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.repository.${entity}Repository;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

@Service
@Transactional
public class ${entity}Service {

    private final ${entity}Repository repository;

    public ${entity}Service(${entity}Repository repository) {
        this.repository = repository;
    }

    public $dto_response create($dto_request request) {
        // TODO create domain aggregate and persist
        throw new UnsupportedOperationException("Implement create use case");
    }

    @Transactional(readOnly = true)
    public $dto_response get($id_type $id_name) {
        // TODO fetch and map
        throw new UnsupportedOperationException("Implement get use case");
    }
}
