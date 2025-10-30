package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.model.$entity;
import $package.domain.service.${entity}Service;
import $package.application.mapper.${entity}Mapper;
import $package.application.exception.${entity}ExistException;
import org.springframework.dao.DataIntegrityViolationException;
import $package.presentation.dto.$dto_request;
import $package.presentation.dto.$dto_response;

@Service$service_annotations_block
@Transactional
public class Create${entity}Service {

    private final ${entity}Service ${entity_lower}Service;
    private final ${entity}Mapper mapper;

    $create_constructor

    public $dto_response create($dto_request request) {
        try {
            $entity agg = mapper.toAggregate($create_id_arg, request);
            agg = ${entity_lower}Service.save(agg);
            return mapper.toResponse(agg);
        } catch (DataIntegrityViolationException ex) {
            throw new ${entity}ExistException("Duplicate $entity");
        }
    }
}
