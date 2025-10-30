package $package.application.service;

$lombok_common_imports
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import $package.domain.service.${entity}Service;
import $package.application.mapper.${entity}Mapper;
import $package.application.exception.${entity}NotFoundException;
import $package.presentation.dto.$EntityResponse;

@Service$service_annotations_block
@Transactional(readOnly = true)
public class Get${entity}Service {

    private final ${entity}Service ${entity_lower}Service;
    private final ${entity}Mapper mapper;

    $get_constructor

    public $EntityResponse get($id_type $id_name) {
        return ${entity_lower}Service.findById($id_name)
            .map(mapper::toResponse)
            .orElseThrow(() -> new ${entity}NotFoundException($id_name));
    }
}
