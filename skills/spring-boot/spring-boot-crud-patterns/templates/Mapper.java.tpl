package $package.application.mapper;

import $package.domain.model.$entity;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

public class ${entity}Mapper {

    public $entity toAggregate($id_type id, $dto_request request) {
        return $entity.create($mapper_create_args);
    }

    public $dto_response toResponse($entity a) {
        return new $dto_response($list_map_response_args);
    }
}
