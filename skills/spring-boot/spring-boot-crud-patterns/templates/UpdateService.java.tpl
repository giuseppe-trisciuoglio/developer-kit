package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.model.$entity;
import $package.domain.service.${entity}Service;
import $package.application.mapper.${entity}Mapper;
import $package.application.exception.${entity}ExistException;
import org.springframework.dao.DataIntegrityViolationException;
import $package.presentation.dto.$EntityRequest;
import $package.presentation.dto.$EntityResponse;

@Service$service_annotations_block
@Transactional
public class Update${entity}Service {

    private final ${entity}Service ${entity_lower}Service;
    private final ${entity}Mapper mapper;

    $update_constructor

    public $EntityResponse update($id_type $id_name, $EntityRequest request) {
        try {
            $entity agg = mapper.toAggregate($id_name, request);
            agg = ${entity_lower}Service.save(agg);
            return mapper.toResponse(agg);
        } catch (DataIntegrityViolationException ex) {
            throw new ${entity}ExistException("Duplicate $entity");
        }
    }
}
